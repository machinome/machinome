// The movie document, machinome-movie/0.1 (docs/movie-document.md): format,
// schema and static checks on the unresolved document, anchor resolution
// against cached takes (pure), and the loader that turns a document into the
// episode the rest of the tool consumes. Design: the movie-document change.
import {readFile,realpath} from 'node:fs/promises';
import {resolve,dirname,isAbsolute} from 'node:path';
import {execFileSync} from 'node:child_process';
import {MOVIE_SCHEMA,validateSchema} from './schema.mjs';
import {DEFAULT_SPEECH_OFFSET} from './chapters.mjs';
import {validateAlignment} from './words.mjs';
import {json} from './util.mjs';
import {cachedTake,generateTakes} from './speech.mjs';
import {validateEpisode,assemblyPaths,contained} from './episode.mjs';
import {loadSourceCode,validateCodeSource} from './code.mjs';
import {loadPictures} from './pictures.mjs';

export const MOVIE_FORMAT='machinome-movie/0.1';
const EPISODE_FORMAT='machinome-video-draft/0.4';
const SETS=['paper','paper-split','source-only'];
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const isAnchor=v=>v!==null&&typeof v==='object';
const phraseOf=a=>a.spoken??a.spokenEnd;
const sameTime=(a,b)=>isAnchor(a)&&isAnchor(b)?a.spoken===b.spoken&&a.spokenEnd===b.spokenEnd&&(a.plus??0)===(b.plus??0):a===b;
const codePointIndex=(text,index)=>Array.from(text.slice(0,index)).length;
const spokenForm=(text,replacements={})=>{
  let result=text;
  for(const [term,spoken] of Object.entries(replacements))result=result.replaceAll(term,spoken);
  return result;
};
// An anchor as refusals name it: spoken "In the model" plus 0.8, mark pull_start.
export function describeAnchor(a){
  if(!isAnchor(a))return String(a);
  const head=a.mark!==undefined?`mark ${a.mark}`:a.spoken!==undefined?`spoken "${a.spoken}"`:`spokenEnd "${a.spokenEnd}"`;
  return a.plus===undefined?head:`${head} plus ${a.plus}`;
}
export const missingTake=id=>`Chapter ${id} has spoken anchors and no cached narration take; run the speech command first (check, preview and render never generate speech)`;

// Every field of a shot that may carry an anchor, named by its path inside the
// shot (design D6): time anchors (spoken, spokenEnd) and model seconds (mark).
export function anchorSlots(shot){
  const slots=[];
  const add=(path,obj,key,kind)=>{if(obj&&typeof obj==='object'&&obj[key]!==undefined)slots.push({path,obj,key,kind});};
  add('until',shot,'until','time');
  shot.camera?.forEach((k,i)=>add(`camera[${i}].at`,k,'at','time'));
  const sim=shot.simulation;
  if(sim){
    add('simulation.from',sim,'from','model');add('simulation.to',sim,'to','model');
    sim.keyframes?.forEach((k,i)=>{add(`simulation.keyframes[${i}].at`,k,'at','time');add(`simulation.keyframes[${i}].seconds`,k,'seconds','model');});
  }
  for(const list of ['overlays','annotations','highlight','pictures'])shot[list]?.forEach((cue,i)=>{
    add(`${list}[${i}].from`,cue,'from','time');add(`${list}[${i}].to`,cue,'to','time');
    if(list==='pictures')cue?.view?.forEach((v,j)=>add(`pictures[${i}].view[${j}].at`,v,'at','time'));
  });
  shot.code?.typing?.forEach((cue,i)=>{add(`code.typing[${i}].from`,cue,'from','time');add(`code.typing[${i}].to`,cue,'to','time');});
  return slots;
}
const spokenIn=chapter=>chapter.shots.some(shot=>anchorSlots(shot).some(s=>s.kind==='time'&&isAnchor(s.obj[s.key])));
// The chapters whose anchors need their cached take to resolve.
export const chaptersNeedingTakes=doc=>doc.chapters.filter(spokenIn).map(c=>c.id);

// Format, schema, then the rules that need no take (design D6-D8).
export function checkMovie(doc){
  need(doc!==null&&typeof doc==='object'&&!Array.isArray(doc),'A movie document must be a JSON object');
  need(doc.format===MOVIE_FORMAT,`Unsupported movie format: ${doc.format}; this Videomaker reads ${MOVIE_FORMAT}`);
  validateSchema(MOVIE_SCHEMA,doc);
  const chapterIds=new Set(),shotIds=new Set(),all=doc.chapters.flatMap(c=>c.shots.map(shot=>({chapter:c,shot})));
  for(const chapter of doc.chapters){
    need(!chapterIds.has(chapter.id),`Duplicate chapter id: ${chapter.id}`);chapterIds.add(chapter.id);
  }
  for(const [index,{chapter,shot}] of all.entries()){
    const c=chapter.id,s=shot.id;
    need(!shotIds.has(s),`Duplicate shot id: ${s} (chapter ${c})`);shotIds.add(s);
    const set=shot.set??(shot.code?'paper-split':'paper');
    need(SETS.includes(set),`Unknown set: ${set} (shot ${s} in chapter ${c}); a set is paper, paper-split or source-only`);
    if(set==='paper')need(!shot.code,`Set paper has no source panel: shot ${s} (chapter ${c}) has code; use paper-split or source-only`);
    else need(shot.code,`Set ${set} needs code: shot ${s} (chapter ${c})`);
    if(shot.fadeIn!==undefined)need(index===0,`fadeIn is accepted only on the film's first shot: shot ${s} (chapter ${c})`);
    if(shot.fadeOut!==undefined)need(index===all.length-1,`fadeOut is accepted only on the film's last shot: shot ${s} (chapter ${c})`);
    if(!isAnchor(shot.until))need(shot.until>0,`Shot ${s} ends at or before its start: until ${shot.until} (chapter ${c})`);
    shot.camera.forEach((key,i)=>need(Object.hasOwn(doc.cameras,key.preset),`Unknown camera preset: ${key.preset} (camera[${i}] of shot ${s} in chapter ${c})`));
    // The last model keyframe is at the shot's end whatever the take: the same
    // literal or the same anchor as until (design D15).
    const last=shot.simulation.keyframes?.at(-1);
    if(last)need(sameTime(last.at,shot.until),`Model keyframes must end at the shot's until: shot ${s} (chapter ${c}) has its last keyframe at ${describeAnchor(last.at)} and until ${describeAnchor(shot.until)}`);
    for(const {path,obj,key,kind} of anchorSlots(shot)){
      const v=obj[key];if(!isAnchor(v))continue;
      if(kind==='model'){need(Object.hasOwn(doc.marks??{},v.mark),`Unknown mark: ${v.mark} (${path} of shot ${s} in chapter ${c})`);continue;}
      const phrase=phraseOf(v),first=chapter.narration.indexOf(phrase);
      need(first>=0,`Spoken phrase is absent from the narration of chapter ${c}: ${phrase} (${path} of shot ${s})`);
      need(chapter.narration.indexOf(phrase,first+1)<0,`Spoken phrase is ambiguous in the narration of chapter ${c}: ${phrase} (${path} of shot ${s})`);
    }
  }
}

// The parts a document names, against the export's assembly (design D15):
// every layer path, and every part a highlight or an annotation targets. It
// needs the export's manifest and no take, so it refuses before speech.
export function checkMovieExport(doc,manifest){
  const known=new Set(),path=p=>p.join('/');
  (function walk(n,at=[]){known.add(JSON.stringify(at));for(const child of n?.children??[])walk(child,[...at,child.name]);})(manifest.root);
  for(const [name,paths] of Object.entries(doc.layers))for(const p of paths)
    need(known.has(JSON.stringify(p)),`Missing assembly path: ${path(p)} (layer ${name})`);
  for(const chapter of doc.chapters)for(const shot of chapter.shots){
    const where=field=>`${field} of shot ${shot.id} in chapter ${chapter.id}`;
    shot.hiddenLayers.forEach((name,i)=>need(Object.hasOwn(doc.layers,name),`Unknown layer: ${name} (${where(`hiddenLayers[${i}]`)})`));
    const target=(part,field)=>{
      if(typeof part==='string')need(Object.hasOwn(doc.layers,part),`Unknown layer: ${part} (${where(field)})`);
      else need(known.has(JSON.stringify(part)),`Missing assembly path: ${path(part)} (${where(field)})`);
    };
    shot.highlight?.forEach((cue,i)=>cue.parts?.forEach(part=>target(part,`highlight[${i}]`)));
    shot.annotations?.forEach((cue,i)=>{if(cue.part!==undefined)target(cue.part,`annotations[${i}]`);});
  }
}

// The numeric format 0.4 episode with chapters (design D6, D7, D10). Pure:
// `takes` maps a chapter id to its cached take ({alignment}); only chapters
// with spoken anchors need one.
export function resolveMovie(doc,takes={}){
  checkMovie(doc);
  const fps=doc.output.fps,snap=t=>Math.round(t*fps)/fps,replacements=doc.audio.replacements??{};
  const chapters=[],shots=[];
  let clock=0;
  for(const chapter of doc.chapters){
    let alignment=null;
    if(spokenIn(chapter)){
      need(takes[chapter.id],missingTake(chapter.id));
      alignment=validateAlignment(takes[chapter.id].alignment,`chapter ${chapter.id}`);
    }
    const start=clock,offset=chapter.speechOffset??DEFAULT_SPEECH_OFFSET;
    // Film seconds of an anchor, snapped to the nearest output frame.
    const instant=(anchor,path,shot)=>{
      const phrase=phraseOf(anchor),spoken=spokenForm(phrase,replacements),where=`${path} of shot ${shot.id}`;
      const at=alignment.text.indexOf(spoken);
      need(at>=0,`Spoken phrase is absent from the recorded narration of chapter ${chapter.id}: ${phrase} (${where})`);
      need(alignment.text.indexOf(spoken,at+1)<0,`Spoken phrase is ambiguous in the recorded narration of chapter ${chapter.id}: ${phrase} (${where})`);
      let t;
      if(anchor.spoken!==undefined){
        // The onset of the first letter or digit of the phrase's first word.
        const word=/\S+/u.exec(spoken),letter=word&&/[\p{L}\p{N}]/u.exec(word[0]);
        need(letter,`No spoken letter or digit begins ${phrase} (${where} in chapter ${chapter.id})`);
        t=alignment.starts[codePointIndex(alignment.text,at+word.index+letter.index)];
      }else t=alignment.ends[codePointIndex(alignment.text,at+spoken.length)-1];
      return snap(start+offset+t+(anchor.plus??0));
    };
    const ids=[];
    for(const shot of chapter.shots){
      const shotStart=clock;
      let end;
      if(isAnchor(shot.until)){
        end=instant(shot.until,'until',shot);
        need(end>shotStart+1e-9,`Shot ${shot.id} ends at or before its start: until ${describeAnchor(shot.until)} (chapter ${chapter.id}) resolves at ${end} s, where the shot starts at ${shotStart} s`);
      }else end=shotStart+shot.until;
      const duration=end-shotStart,copy=structuredClone(shot);
      for(const {path,obj,key,kind} of anchorSlots(copy)){
        const v=obj[key];
        if(path==='until'||!isAnchor(v))continue;
        if(kind==='model'){obj[key]=doc.marks[v.mark]+(v.plus??0);continue;}
        let local=instant(v,path,shot)-shotStart;
        if(Math.abs(local)<1e-9)local=0;else if(Math.abs(local-duration)<1e-9)local=duration;
        need(local>=0&&local<=duration,`Anchor ${describeAnchor(v)} of ${path} in shot ${shot.id} (chapter ${chapter.id}) falls outside the shot`);
        obj[key]=local;
      }
      const {id,set,until,direction,...rest}=copy,resolved={id,start:shotStart,end,direction:direction??''};
      if((set??(shot.code?'paper-split':'paper'))==='source-only')resolved.layout='source-only';
      shots.push(Object.assign(resolved,rest));ids.push(id);clock=end;
    }
    chapters.push({id:chapter.id,narration:chapter.narration,speechOffset:offset,start,end:clock,shots:ids,
      ...(chapter.direction!==undefined?{direction:chapter.direction}:{})});
  }
  const {format,root,marks,output,chapters:_,...rest}=doc;
  return {format:EPISODE_FORMAT,movie:MOVIE_FORMAT,...rest,style:rest.style??{},
    output:{...output,durationSeconds:clock},chapters,shots};
}

// The document, checked but unresolved, and where it lives.
export async function readMovie(file){
  const documentPath=await realpath(file);
  let doc;
  try{doc=JSON.parse(await readFile(documentPath,'utf8'));}
  catch(error){if(error instanceof SyntaxError)throw new Error(`Movie document is not valid JSON: ${error.message}`);throw error;}
  checkMovie(doc);
  const base=await realpath(isAbsolute(doc.root)?doc.root:resolve(dirname(documentPath),doc.root));
  return {doc,documentPath,base,build:resolve(base,'_build')};
}
// What speech needs before anything is resolved (design D4): the narration,
// the audio settings and the build directory.
export async function pendingMovie(file){
  const {doc,documentPath,base,build}=await readMovie(file);
  return {movie:MOVIE_FORMAT,audio:doc.audio,paths:{episode:documentPath,base,build},
    chapters:doc.chapters.map(c=>({id:c.id,narration:c.narration}))};
}
// The speech command's first step on a document: generate each missing take.
export async function generateMovieTakes(file){return generateTakes(await pendingMovie(file));}

// Load, resolve against the cached takes, write the resolved document, then
// check it against the export and the project exactly as a YAML episode is.
export async function loadMovie(file){
  const {doc,documentPath,base,build}=await readMovie(file);
  const manifestPath=await realpath(resolve(base,doc.model.manifest));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  checkMovieExport(doc,manifest);
  const pending={audio:doc.audio,paths:{build},chapters:doc.chapters.map(c=>({id:c.id,narration:c.narration}))};
  const needed=chaptersNeedingTakes(doc),takes={};
  for(const [i,chapter] of doc.chapters.entries()){
    if(!needed.includes(chapter.id))continue;
    const take=await cachedTake(pending,i);
    need(take,missingTake(chapter.id));
    takes[chapter.id]={alignment:take.alignment};
  }
  const resolved=resolveMovie(doc,takes);
  await json(resolve(build,'movie-resolved.json'),resolved);
  const e=structuredClone(resolved);
  validateEpisode(e,manifest);
  const paths=assemblyPaths(manifest.root);
  for(const layer of Object.values(e.layers))for(const path of layer)need(paths.has(JSON.stringify(path)),`Missing assembly path: ${path.join('/')}`);
  for(const path of Object.values(e.evidence))await readFile(resolve(base,path));
  const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
  need(contained(repository,base),'Movie root must live inside its project repository');
  const sourceRevision=(await readFile(resolve(dirname(manifestPath),'source-revision.txt'),'utf8')).trim();
  need(e.model.sourceRevision===sourceRevision,'Pin model.sourceRevision to the export source-revision.txt before rendering');
  e.paths={episode:documentPath,production:documentPath,base,manifest:manifestPath,repository,build};
  e.sourceCode=await loadSourceCode(e);
  for(const shot of e.shots)validateCodeSource(e,shot);
  await loadPictures(e);
  return e;
}
