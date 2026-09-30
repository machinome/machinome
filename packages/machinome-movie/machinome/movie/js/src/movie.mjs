// The movie document, machinome-movie/0.2 (docs/movie-document.md): format,
// schema and static checks on the unresolved document (a port of the Python
// side's check_document, so both runtimes refuse the shared invalid fixtures
// naming the same things), resolution against cached takes to the resolved
// document (pure), and the loader. Design: the react-stage change, D1 and D2.
import {readFile,realpath,stat} from 'node:fs/promises';
import {resolve,dirname,isAbsolute,relative,extname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {MOVIE_SCHEMA,validateSchema} from './schema.mjs';
import {DEFAULT_SPEECH_OFFSET} from './chapters.mjs';
import {validateAlignment,spokenOnsets,emphasisTiming} from './words.mjs';
import {json} from './util.mjs';
import {cachedTake,generateTakes} from './speech.mjs';
import {assemblyPaths,contained} from './episode.mjs';
import {loadSourceCode} from './code.mjs';
import {loadPictures} from './pictures.mjs';
import {EASINGS,endSlope,ease} from './easing.mjs';
import {TOKEN,countPhrase,countWords,countToken,excerptLine,propKind,spokenForm} from './text.mjs';
import {effectiveStyle,COLOR} from './style.mjs';

export const MOVIE_FORMAT='machinome-movie/0.2';
// The sets the tool ships for movies, with their slots; the ones it keeps for
// YAML episodes only; the element kinds it ships, with the fields a
// declaration requires and takes (`kind` aside); each shipped element's
// actions with their required and accepted fields.
export const SHIPPED_SETS={frame:['stage'],split:['left','right']};
export const EPISODE_SETS=['paper','paper-split','source-only'];
export const SHIPPED_ELEMENTS={view:[['camera'],['camera','hide']],source:[['source'],['source']],
  title:[['text'],['text','subtitle']],picture:[[],['still','clip','fit','inPoint']]};
export const ACTIONS={
  view:{move:[['camera','until'],['camera','until','ease']],highlight:[['parts'],['parts','others','color']],
    ring:[['part'],['part','padding','enter','leave']],label:[['part','text'],['part','text','offset','enter','leave']],
    arrow:[['place'],['part','point','text','place','enter','leave']]},
  source:{type:[['throughLine','over'],['throughLine','over']],emphasize:[['words'],['words','hold','line']]},
  title:{show:[[],['enter','leave','reveal']]},
  picture:{show:[[],['enter','leave','view']]},
};
// Actions that end on their own; every other action spans its cue.
export const UNSPANNED=['move','type','emphasize'];
const DRAWN=['ring','arrow'],TRANSITIONS=['dissolve','fade','wipe','slide'],MODULE=/\.(ts|tsx|js|jsx)$/;
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const isAnchor=v=>v!==null&&typeof v==='object';
const phraseOf=a=>a.spoken??a.spokenEnd;
const codePointIndex=(text,index)=>Array.from(text.slice(0,index)).length;
const list=items=>items.length?items.join(', '):'none';
const sorted=items=>[...items].sort();

// An anchor as refusals name it: spoken "In the model" plus 0.8, mark
// pull_start, narrationEnd plus 0.9.
export function describeAnchor(a){
  if(!isAnchor(a))return String(a);
  const head=a.mark!==undefined?`mark ${a.mark}`:a.spoken!==undefined?`spoken "${a.spoken}"`:
    a.narrationEnd!==undefined?'narrationEnd':`spokenEnd "${a.spokenEnd}"`;
  return a.plus===undefined?head:`${head} plus ${a.plus}`;
}
export const missingTake=id=>`Chapter ${id} has spoken anchors and no cached narration take; run the speech command first (check, preview and render never generate speech)`;

// Every time of a shot that may be an anchor, by its field, with where it is
// written, so resolution can replace it.
export function shotTimes(shot){
  const out=[{field:'until',obj:shot,key:'until'}];
  shot.model?.keys?.forEach((k,i)=>out.push({field:`model.keys[${i}].at`,obj:k,key:'at'}));
  shot.cues?.forEach((cue,i)=>{
    out.push({field:`cues[${i}].at`,obj:cue,key:'at'});
    if(cue.until!==undefined)out.push({field:`cues[${i}].until`,obj:cue,key:'until'});
    cue.actions.forEach((action,j)=>{
      if(action.until!==undefined)out.push({field:`cues[${i}].actions[${j}].until`,obj:action,key:'until'});
      action.view?.forEach((key,k)=>out.push({field:`cues[${i}].actions[${j}].view[${k}].at`,obj:key,key:'at'}));
    });
  });
  return out;
}
function modelTimes(model){
  if(model.keys)return model.keys.map((k,i)=>({field:`model.keys[${i}].seconds`,obj:k,key:'seconds'}));
  return [{field:'model.from',obj:model,key:'from'},{field:'model.to',obj:model,key:'to'}];
}
// A chapter needs its take when a time is anchored to its narration, or when
// words light or appear as they are spoken.
const needsTake=chapter=>chapter.shots.some(shot=>shotTimes(shot).some(t=>isAnchor(t.obj[t.key]))||
  shot.cues.some(cue=>cue.actions.some(a=>a.action==='emphasize'||a.reveal?.timing==='spoken')));
export const chaptersNeedingTakes=doc=>doc.chapters.filter(needsTake).map(c=>c.id);

// Format, schema, then every refusal that needs no take (design D1). With the
// export's manifest, part paths are checked; with `sources` (excerpt name ->
// the text of its lines), emphasised tokens are.
export function checkMovie(doc,{manifest=null,sources={}}={}){
  need(doc!==null&&typeof doc==='object'&&!Array.isArray(doc),'A movie document must be a JSON object');
  need(doc.format===MOVIE_FORMAT,`Unsupported movie format: ${doc.format}; this Videomaker reads ${MOVIE_FORMAT}`);
  validateSchema(MOVIE_SCHEMA,doc);
  new Semantics(doc,manifest,sources).check();
}

class Semantics{
  constructor(doc,manifest,sources){
    this.doc=doc;this.sources=sources;this.stage=doc.stage;
    this.paths=manifest?assemblyPaths(manifest.root??{}):null;
  }
  check(){
    const doc=this.doc;
    this.checkStage();
    const chapters=new Set(),shots=new Map(),film=doc.chapters.flatMap(c=>c.shots.map(s=>[c,s]));
    for(const chapter of doc.chapters){
      need(!chapters.has(chapter.id),`Chapter ${chapter.id} appears twice; chapter ids are unique`);chapters.add(chapter.id);
    }
    for(const [chapter,shot] of film){
      need(!shots.has(shot.id),`Shot ${shot.id} appears in chapters ${shots.get(shot.id)} and ${chapter.id}; shot ids are unique across a movie`);
      shots.set(shot.id,chapter.id);
    }
    for(const [name,layer] of Object.entries(doc.layers))for(const path of layer)this.path(path,`layer ${name}`);
    let index=0;
    for(const chapter of doc.chapters){
      for(const [key,element] of Object.entries(chapter.elements))this.element(chapter,key,element);
      const completed=new Set();
      for(const shot of chapter.shots){this.shot(chapter,shot,completed,index===0,index===film.length-1);index++;}
    }
  }
  checkStage(){
    const stage=this.stage,seen=new Set();
    for(const module of stage.modules){
      need(!seen.has(module),`stage.modules lists ${module} twice`);seen.add(module);
      need(!module.startsWith('/')&&MODULE.test(module),`stage.modules: ${module} is not a stage module; a module is a TypeScript or JavaScript file (.ts, .tsx, .js or .jsx) relative to root`);
    }
    for(const [kind,entry] of Object.entries(stage.sets)){
      const where=`stage.sets.${kind}`;
      need(new Set(entry.slots).size===entry.slots.length,`${where}: slots lists a slot twice`);
      if(entry.module===undefined){
        need(Object.hasOwn(SHIPPED_SETS,kind),`${where}: ${kind} has no module and is not a set the tool ships for movies (frame, split)`);
        need(JSON.stringify(entry.slots)===JSON.stringify(SHIPPED_SETS[kind]),
          `${where}: the shipped set ${kind} has the slots ${SHIPPED_SETS[kind].join(', ')}, not ${list(entry.slots)}`);
        need(entry.base===undefined,`${where}: a set the tool ships has no base`);
        continue;
      }
      need(!Object.hasOwn(SHIPPED_SETS,kind)&&!EPISODE_SETS.includes(kind),`${where}: ${kind} is a set the tool ships; a project set takes another kind`);
      this.module(entry.module,where);
      let base=entry.base;const chain=[kind];
      while(base!==undefined){
        need(!chain.includes(base),`${where}: its base ${base} derives from it (${[...chain,base].join(' -> ')})`);
        if(Object.hasOwn(SHIPPED_SETS,base)&&!Object.hasOwn(stage.sets,base))break;
        need(Object.hasOwn(stage.sets,base),`${where}: its base ${base} is neither a set of stage.sets nor one the tool ships`);
        chain.push(base);base=stage.sets[base].base;
      }
    }
    for(const [kind,entry] of Object.entries(stage.elements)){
      const where=`stage.elements.${kind}`;
      need(!Object.hasOwn(SHIPPED_ELEMENTS,kind),`${where}: ${kind} is an element the tool ships; a project element takes another kind`);
      this.module(entry.module,where);
    }
  }
  module(module,where){need(this.stage.modules.includes(module),`${where}: its module ${module} is not listed in stage.modules`);}
  element(chapter,key,element){
    const where=`chapter ${chapter.id}, elements.${key}`,kind=element.kind;
    const fields=Object.keys(element).filter(f=>f!=='kind');
    let required,accepted;
    if(Object.hasOwn(SHIPPED_ELEMENTS,kind))[required,accepted]=SHIPPED_ELEMENTS[kind];
    else if(Object.hasOwn(this.stage.elements,kind))[required,accepted]=[['props'],['props']];
    else throw new Error(`${where}: unknown element kind '${kind}'; a kind is view, source, title, picture or one of stage.elements`);
    this.fields(where,`a ${kind} element`,fields,required,accepted);
    if(kind==='view'){
      this.known(element.camera,'cameras',where,'camera');
      for(const layer of element.hide??[])this.known(layer,'layers',where,'layer');
    }else if(kind==='source')this.known(element.source,'sourceCode',where,'source excerpt');
    else if(kind==='picture'){
      need((element.still!==undefined)!==(element.clip!==undefined),`${where}: a picture shows one still or one clip`);
      if(element.still!==undefined){
        this.known(element.still,'stills',where,'still');
        need(element.inPoint===undefined,`${where}: inPoint belongs to a clip, not a still`);
      }else this.known(element.clip,'clips',where,'clip');
      need(['contain','cover'].includes(element.fit??'contain'),`${where}: fit '${element.fit}' must be contain or cover`);
    }else if(!Object.hasOwn(SHIPPED_ELEMENTS,kind)){
      const declared=this.stage.elements[kind].props,given=element.props;
      for(const name of sorted(new Set([...Object.keys(declared),...Object.keys(given)]))){
        need(Object.hasOwn(given,name),`${where}: props: the ${kind} element declares the prop ${name}, and it is missing`);
        need(Object.hasOwn(declared,name),`${where}: props: ${name} is not a prop the ${kind} element declares (${list(Object.keys(declared))})`);
        need(propKind(given[name])===declared[name],`${where}: props: ${name} is a ${propKind(given[name])}, and the ${kind} element declares it a ${declared[name]}`);
      }
    }
  }
  fields(where,what,fields,required,accepted){
    for(const field of sorted(fields))need(accepted.includes(field),`${where}: ${what} takes ${sorted(accepted).join(', ')||'nothing'}, not ${field}`);
    for(const field of sorted(required))need(fields.includes(field),`${where}: ${what} needs ${field}`);
  }
  known(name,table,where,what){need(Object.hasOwn(this.doc[table]??{},name),`${where}: unknown ${what} '${name}'`);}
  shot(chapter,shot,completed,first,last){
    const where=`chapter ${chapter.id}, shot ${shot.id}`,sets=this.stage.sets;
    need(Object.hasOwn(sets,shot.set),`${where}: unknown set '${shot.set}'; the stage block declares the sets ${list(Object.keys(sets))}`);
    const slots=sets[shot.set].slots,placed=new Map();
    for(const [slot,key] of Object.entries(shot.places)){
      need(slots.includes(slot),`${where}, places.${slot}: the set ${shot.set} has no slot ${slot}; its slots are ${slots.join(', ')}`);
      need(Object.hasOwn(chapter.elements,key),`${where}, places.${slot}: the chapter does not declare the element ${key}`);
      const other=[...placed].find(([,k])=>k===key)?.[0];
      need(other===undefined,`${where}: the element ${key} is placed in two slots, ${other} and ${slot}; an element is in one place at a time`);
      placed.set(slot,key);
    }
    need(isAnchor(shot.until)||shot.until>0,`${where}, until: the shot ends at or before its start (until ${shot.until})`);
    need(shot.fadeIn===undefined||first,`${where}: fadeIn is accepted only on the film's first shot`);
    need(shot.fadeOut===undefined||last,`${where}: fadeOut is accepted only on the film's last shot`);
    this.joins(shot,where);
    for(const {field,obj,key} of shotTimes(shot)){
      const value=obj[key];
      // The end of the narration names no phrase to look for.
      if(isAnchor(value)&&value.narrationEnd===undefined)this.phrase(chapter.narration,phraseOf(value),where,field);
    }
    this.model(shot,where);
    const typed=new Map();
    shot.cues.forEach((cue,i)=>this.cue(chapter,placed,cue,`${where}, cues[${i}]`,typed,completed));
    for(const [slot,key] of placed){
      const element=chapter.elements[key];
      if(element.kind==='source'&&!completed.has(key)){
        const lastLine=this.doc.sourceCode[element.source].lines[1];
        throw new Error(`${where}, places.${slot}: the source panel ${key} is placed and not complete: no typing of this shot or an earlier one of the chapter reaches its last line, ${lastLine}`);
      }
    }
  }
  joins(shot,where){
    for(const field of ['transition','fadeIn','fadeOut']){
      const join=shot[field];if(join===undefined)continue;
      const kind=join.kind;
      if(field==='transition')need(TRANSITIONS.includes(kind),`${where}, transition.kind: '${kind}' is not a transition; use dissolve, fade, wipe or slide`);
      else need(kind===undefined||kind==='fade',`${where}, ${field}.kind: '${kind}' is not a fade`);
      if(join.direction!==undefined)need(['wipe','slide'].includes(kind)&&['left','right'].includes(join.direction),
        `${where}, ${field}.direction: a direction is left or right, on a wipe or a slide`);
      if(join.color!==undefined)need(kind===undefined||kind==='fade',`${where}, ${field}.color: a colour belongs to a fade`);
      this.ease(join.ease,where,`${field}.ease`);
    }
  }
  model(shot,where){
    const model=shot.model,marks=this.doc.marks??{};
    for(const {field,obj,key} of modelTimes(model)){
      const value=obj[key];
      if(isAnchor(value))need(Object.hasOwn(marks,value.mark),`${where}, ${field}: unknown mark '${value.mark}'; the document's marks are ${list(Object.keys(marks))}`);
    }
    const keys=model.keys;if(!keys)return;
    need(keys[0].at===0,`${where}, model.keys[0].at: model keys must start at the shot's start, with a first key at 0`);
    need(JSON.stringify(keys.at(-1).at)===JSON.stringify(shot.until),
      `${where}, model.keys[${keys.length-1}].at: model keys must end at the shot's until, with a last key at the same time`);
    keys.forEach((key,i)=>this.ease(key.ease,where,`model.keys[${i}].ease`));
  }
  cue(chapter,placed,cue,where,typed,completed){
    cue.actions.forEach((action,number)=>{
      const here=`${where}.actions[${number}]`,key=action.element,name=action.action;
      need([...placed.values()].includes(key),`${here}: ${name} acts on ${key}, which the shot does not place`);
      const element=chapter.elements[key],kind=element.kind;
      const fields=Object.keys(action).filter(f=>f!=='element'&&f!=='action');
      if(Object.hasOwn(ACTIONS,kind)){
        need(Object.hasOwn(ACTIONS[kind],name),`${here}: the ${kind} element has no action ${name}; it has ${Object.keys(ACTIONS[kind]).join(', ')}`);
        const [required,accepted]=ACTIONS[kind][name];
        this.fields(here,`the action ${name}`,fields,required,accepted);
      }else{
        const declared=this.stage.elements[kind].actions;
        need(Object.hasOwn(declared,name),`${here}: the ${kind} element has no action ${name}; it declares ${list(Object.keys(declared))}`);
        this.fields(here,`the action ${name}`,fields,['params'],['params']);
        this.params(here,kind,name,declared[name],action.params);
      }
      need(UNSPANNED.includes(name)||cue.until!==undefined,`${where}: ${name} shows something for a span and needs the cue's until`);
      if(kind==='view')this.viewAction(action,here);
      else if(kind==='source'&&name==='type')this.typing(element,key,action,here,typed,completed);
      else if(kind==='source'&&name==='emphasize')this.emphasis(element,cue,action,where,here,chapter.narration);
      else if(kind==='title'){this.entrances(action,here,name);this.reveal(chapter.narration,element,action.reveal,here);}
      else if(kind==='picture'){
        this.entrances(action,here,name);
        action.view?.forEach((view,i)=>this.ease(view.ease,here,`view[${i}].ease`));
      }
    });
  }
  params(where,kind,name,declared,given){
    for(const param of sorted(new Set([...Object.keys(declared),...Object.keys(given)]))){
      need(Object.hasOwn(given,param),`${where}: params: the ${kind} action ${name} declares the parameter ${param}, and it is missing`);
      need(Object.hasOwn(declared,param),`${where}: params: ${param} is not a parameter the ${kind} action ${name} declares (${list(Object.keys(declared))})`);
      const actual=propKind(given[param]);
      need(actual===declared[param],`${where}: params: ${param} is a ${actual}, and the ${kind} action ${name} declares it a ${declared[param]}`);
    }
  }
  viewAction(action,where){
    const name=action.action;
    if(name==='move'){this.known(action.camera,'cameras',where,'camera');this.ease(action.ease,where,'ease');return;}
    if(name==='highlight'){
      for(const part of action.parts)this.part(part,where,'parts');
      need(['keep','dim','ghost'].includes(action.others??'keep'),`${where}: others '${action.others}' must be keep, dim or ghost`);
      if(action.color!==undefined)need(COLOR.test(action.color),`${where}, color: '${action.color}' must be a quoted #rrggbb`);
      return;
    }
    if(name==='arrow')need((action.part!==undefined)!==(action.point!==undefined),`${where}: an arrow points at one part or one point`);
    if(action.part!==undefined)this.part(action.part,where,'part');
    this.entrances(action,where,name);
  }
  entrances(action,where,name){
    for(const field of ['enter','leave']){
      const entrance=action[field];if(entrance===undefined)continue;
      const kinds=DRAWN.includes(name)&&field==='enter'?['fade','draw']:['fade'];
      need(kinds.includes(entrance.kind),`${where}, ${field}.kind: '${entrance.kind}' is not an ${field==='enter'?'entrance':'exit'} of a ${name}; use ${kinds.join(' or ')} (draw only on the entrance of a ring or an arrow)`);
      this.ease(entrance.ease,where,`${field}.ease`);
    }
  }
  typing(element,key,action,where,typed,completed){
    const [first,last]=this.doc.sourceCode[element.source].lines,through=action.throughLine;
    need(!completed.has(key)||typed.has(key),`${where}: type: the source panel ${key} was completed by an earlier shot of the chapter and is already typed; it keeps its text`);
    need(first<=through&&through<=last,`${where}: throughLine ${through} is outside the excerpt ${element.source}, lines ${first} to ${last}`);
    need(!typed.has(key)||through>typed.get(key),`${where}: throughLine ${through}: the panel ${key} is already typed through line ${typed.get(key)}; typing runs forward`);
    typed.set(key,through);
    if(through===last)completed.add(key);
  }
  emphasis(element,cue,action,cueWhere,where){
    const at=cue.at;
    need(isAnchor(at)&&at.spoken!==undefined&&at.plus===undefined,`${cueWhere}.at: emphasize lights words where they are spoken, so the cue's at is a spoken phrase with no plus`);
    const phrase=at.spoken,excerpt=element.source,[first,last]=this.doc.sourceCode[excerpt].lines,line=action.line;
    need(line===undefined||(first<=line&&line<=last),`${where}, line: line ${line} is outside the excerpt ${excerpt}, lines ${first} to ${last}`);
    action.words.forEach((word,index)=>{
      const found=countWords(phrase,word.spoken);
      need(found===1,`${where}, words[${index}].spoken: the spoken words '${word.spoken}' are ${found===0?'absent from':'ambiguous in'} the cue's phrase '${phrase}' (found ${found} times as whole words)`);
      const token=word.token;
      need(TOKEN.test(token),`${where}, words[${index}].token: '${token}' is not a source token; a token is an identifier or a dotted path`);
      if(Object.hasOwn(this.sources,excerpt)){
        const text=line===undefined?this.sources[excerpt]:excerptLine(this.sources[excerpt],first,line);
        const count=countToken(text,token);
        const place=line===undefined?`the excerpt ${excerpt}`:`line ${line} of the excerpt ${excerpt}`;
        need(count===1,`${where}, words[${index}].token: the token '${token}' is ${count===0?'absent from':'ambiguous in'} ${place} (found ${count} times, bounded by anything but a letter, a digit or an underscore)`);
      }
    });
  }
  reveal(narration,element,reveal,where){
    if(reveal===undefined)return;
    if(reveal.timing==='spoken'){
      const phrase=reveal.phrase??element.text,words=s=>s.split(/\s+/u).filter(Boolean);
      need(JSON.stringify(words(phrase))===JSON.stringify(words(element.text)),`${where}, reveal.phrase: '${phrase}' does not match the title's text '${element.text}' word for word`);
      this.phrase(narration,phrase,where,'reveal.phrase');
      need(reveal.duration===undefined&&reveal.ease===undefined,`${where}, reveal: a spoken reveal takes no duration or ease`);
    }else if(reveal.timing==='even'){
      need(reveal.duration>0,`${where}, reveal.duration: an even reveal needs a duration`);
      need(reveal.phrase===undefined,`${where}, reveal.phrase: an even reveal is not spoken`);
      this.ease(reveal.ease,where,'reveal.ease');
    }else throw new Error(`${where}, reveal.timing: '${reveal.timing}' must be spoken or even`);
  }
  ease(name,where,field){
    need(name===undefined||EASINGS.includes(name),`${where}, ${field}: unknown easing '${name}'; use linear, smooth, in, out or in-out`);
  }
  phrase(narration,phrase,where,field){
    const found=countPhrase(narration,phrase);
    need(found>0,`${where}, ${field}: the phrase '${phrase}' is absent from the chapter's narration`);
    need(found<2,`${where}, ${field}: the phrase '${phrase}' is ambiguous in the chapter's narration (it occurs ${found} times)`);
  }
  part(part,where,field){
    if(typeof part==='string')need(Object.hasOwn(this.doc.layers,part),`${where}, ${field}: unknown layer '${part}'`);
    else this.path(part,`${where}, ${field}`);
  }
  path(path,where){need(!this.paths||this.paths.has(JSON.stringify(path)),`${where}: the export does not contain ${path.join('/')}`);}
}

// Resolution (design D2): the resolved document, pure. `takes` maps a chapter
// id to its cached take ({alignment}); only chapters that need one must have it.
export function resolveMovie(doc,takes={}){
  checkMovie(doc);
  const fps=doc.output.fps,snap=t=>Math.round(t*fps)/fps,replacements=doc.audio.replacements??{};
  const chapters=[];let clock=0;
  for(const chapter of doc.chapters){
    let alignment=null;
    if(needsTake(chapter)){
      need(takes[chapter.id],missingTake(chapter.id));
      alignment=validateAlignment(takes[chapter.id].alignment,`chapter ${chapter.id}`);
    }
    const start=clock,offset=chapter.speechOffset??DEFAULT_SPEECH_OFFSET,shots=[];
    // The phrase's place in the recorded narration, once.
    const recorded=(phrase,field,where)=>{
      const spoken=spokenForm(phrase,replacements),at=alignment.text.indexOf(spoken);
      need(at>=0,`${where}, ${field}: the phrase '${phrase}' is absent from the recorded narration of chapter ${chapter.id}`);
      need(alignment.text.indexOf(spoken,at+1)<0,`${where}, ${field}: the phrase '${phrase}' is ambiguous in the recorded narration of chapter ${chapter.id}`);
      return {spoken,at};
    };
    // Film seconds of a time anchor, snapped to the nearest output frame.
    const instant=(anchor,field,where)=>{
      if(anchor.narrationEnd!==undefined){
        // The end of the take's last letter or digit: the mirror of a spoken
        // anchor's first letter or digit; punctuation carries no sound.
        const last=Array.from(alignment.text).findLastIndex(c=>/[\p{L}\p{N}]/u.test(c));
        need(last>=0,`${where}, ${field}: narrationEnd: no spoken letter or digit ends the recorded narration of chapter ${chapter.id}`);
        return snap(start+offset+alignment.ends[last]+(anchor.plus??0));
      }
      const phrase=phraseOf(anchor),{spoken,at}=recorded(phrase,field,where);
      let t;
      if(anchor.spoken!==undefined){
        const word=/\S+/u.exec(spoken),letter=word&&/[\p{L}\p{N}]/u.exec(word[0]);
        need(letter,`${where}, ${field}: no spoken letter or digit begins '${phrase}'`);
        t=alignment.starts[codePointIndex(alignment.text,at+word.index+letter.index)];
      }else t=alignment.ends[codePointIndex(alignment.text,at+spoken.length)-1];
      return snap(start+offset+t+(anchor.plus??0));
    };
    for(const shot of chapter.shots){
      const shotStart=clock,where=`chapter ${chapter.id}, shot ${shot.id}`;
      const end=isAnchor(shot.until)?instant(shot.until,'until',where):shotStart+shot.until;
      need(end>shotStart+1e-9,`${where}, until: the shot ends at or before its start: until ${describeAnchor(shot.until)} resolves at ${end} s, where the shot starts at ${shotStart} s`);
      const duration=end-shotStart,copy=structuredClone(shot);
      for(const {field,obj,key} of shotTimes(copy)){
        if(field==='until')continue;
        const value=obj[key];
        let local=isAnchor(value)?instant(value,field,where)-shotStart:value;
        if(Math.abs(local)<1e-9)local=0;else if(Math.abs(local-duration)<1e-9)local=duration;
        need(local>=0&&local<=duration,`${where}, ${field}: ${describeAnchor(value)} falls outside the shot (at ${local.toFixed(3)} s of its ${duration.toFixed(3)} s)`);
        obj[key]=local;
      }
      if(copy.model.keys)copy.model.keys.at(-1).at=duration;
      for(const {obj,key} of modelTimes(copy.model)){const v=obj[key];if(isAnchor(v))obj[key]=doc.marks[v.mark]+(v.plus??0);}
      // Words that light or appear as they are spoken, from the chapter's take.
      const takeStart=start+offset-shotStart;
      copy.cues.forEach((cue,i)=>cue.actions.forEach((action,j)=>{
        const field=`cues[${i}].actions[${j}]`;
        if(action.action==='emphasize'){
          const timing=emphasisTiming({phrase:shot.cues[i].at.spoken,words:action.words.map(w=>w.spoken),alignment,
            replacements,offset:takeStart,hold:action.hold??0,where:`${where}, ${field}`});
          timing.onsets.forEach((at,k)=>{action.words[k].at=at;});
          // A hold that runs past the cut ends with the shot (finding: the
          // contract does not say; the Python side accepts it).
          action.until=Math.min(timing.clear,duration);
        }else if(action.reveal?.timing==='spoken'){
          const element=chapter.elements[action.element];
          action.reveal.onsets=spokenOnsets({text:element.text,phrase:action.reveal.phrase??element.text,narration:chapter.narration,
            alignment:takes[chapter.id].alignment,replacements,offset:takeStart,from:cue.at,to:cue.until,shotStart,fps,
            where:`${where}, ${field}, reveal`});
        }
      }));
      const {id,...rest}=copy;
      shots.push({id,start:shotStart,end,...rest,until:duration});
      clock=end;
    }
    const {id,narration,speechOffset,direction,elements,shots:_,...other}=chapter;
    chapters.push({id,narration,speechOffset:offset,...(direction!==undefined?{direction}:{}),...other,
      start,end:clock,elements,shots});
  }
  const {format,output,chapters:_,...rest}=doc;
  const resolved={format,resolved:true,...rest,output:{...output,durationSeconds:clock},chapters};
  checkResolved(resolved);
  return resolved;
}

// The rules that need resolved times (design D2.3).
function checkResolved(film){
  const fps=film.output.fps,frames=d=>d*fps>=2-1e-9,shots=film.chapters.flatMap(c=>c.shots.map(s=>[c,s]));
  const style=effectiveStyle(film.style);
  for(const [index,[chapter,shot]] of shots.entries()){
    const where=`chapter ${chapter.id}, shot ${shot.id}`,duration=shot.end-shot.start;
    if(shot.model.keys){
      shot.model.keys.forEach((key,i)=>{
        if(i)need(key.at>shot.model.keys[i-1].at,`${where}, model.keys[${i}].at: model keys must follow one another in time`);
        if(i)need(key.seconds>=shot.model.keys[i-1].seconds,`${where}, model.keys[${i}].seconds: model time never runs back (${key.seconds} after ${shot.model.keys[i-1].seconds})`);
      });
    }
    for(const s of modelSeconds(shot.model))
      need(s>=0&&s<=film.model.expectedDurationSeconds,`${where}: model time ${s} s is outside the export's ${film.model.expectedDurationSeconds} s`);
    const spans=new Map();
    shot.cues.forEach((cue,i)=>cue.actions.forEach((action,j)=>{
      const field=`cues[${i}].actions[${j}]`,name=action.action;
      if(name==='move')need(action.until>cue.at+1e-9,`${where}, ${field}.until: the move ends at or before it starts`);
      if(!UNSPANNED.includes(name))need(cue.until>cue.at+1e-9,`${where}, cues[${i}].until: the cue ends at or before it starts`);
      const from=cue.at,to=name==='move'?action.until:name==='emphasize'?action.until:name==='type'?cue.at+action.over:cue.until;
      if(['move','highlight','show'].includes(name)){
        const key=`${action.element}/${name}`,prior=spans.get(key)??[];
        for(const p of prior)need(from>=p.to-1e-9||to<=p.from+1e-9,`${where}, ${field}: ${name} on ${action.element} overlaps ${p.field}; one ${name} of an element at a time`);
        prior.push({from,to,field});spans.set(key,prior);
      }
      if(name==='type')need(cue.at+action.over<=duration+1e-9,`${where}, ${field}: typing ends after the shot does`);
      const span=to-from;
      for(const side of ['enter','leave']){
        const x=action[side];if(!x)continue;
        need(frames(x.duration),`${where}, ${field}.${side}.duration: at least two frames (${(2/fps).toFixed(3)} s at ${fps} fps)`);
        need(x.duration<=span+1e-9,`${where}, ${field}.${side}.duration: ${x.duration} s is longer than the cue's ${span.toFixed(3)} s`);
      }
      if(name==='show'&&action.view){
        action.view.forEach((key,k)=>{
          need(key.at>=from-1e-9&&key.at<=to+1e-9&&(k===0||key.at>action.view[k-1].at),`${where}, ${field}.view[${k}].at: view keys follow one another inside the cue`);
          need(key.center.every(v=>v>=0&&v<=1)&&key.zoom>=1,`${where}, ${field}.view[${k}]: a view key's center is inside the picture and its zoom at least 1`);
        });
      }
      if(action.reveal?.timing==='even')need(from+action.reveal.duration<=to+1e-9,`${where}, ${field}.reveal.duration: longer than the cue`);
    }));
    for(const field of ['transition','fadeIn','fadeOut']){
      const x=shot[field];if(!x)continue;
      need(frames(x.duration),`${where}, ${field}.duration: at least two frames (${(2/fps).toFixed(3)} s at ${fps} fps)`);
      need(x.duration<=duration+1e-9,`${where}, ${field}: ${x.duration} s is longer than shot ${shot.id} (${duration} s)`);
      if(field!=='transition'||x.kind==='fade')need(COLOR.test(x.color??style.background),`${where}, ${field}.color: a colour is a quoted #rrggbb`);
      if(field==='transition'){
        need(index>0,`${where}, transition: the first shot comes in from nothing; use fadeIn`);
        // The outgoing shot continues past its end for as long as it is seen,
        // however short it was (finding: the tour fixture joins a 0.5 s shot
        // by a 0.6 s dissolve; a YAML episode keeps its refusal).
        const [,prior]=shots[index-1];
        const shown=x.kind==='fade'?x.duration/2:x.duration,reach=lastSeconds(prior.model)+endRate(prior)*shown;
        need(reach<=film.model.expectedDurationSeconds+1e-9,`Shot ${prior.id} cannot continue ${shown} s into the ${x.kind} to shot ${shot.id}: its model would reach ${reach.toFixed(2)} s, past the export's ${film.model.expectedDurationSeconds} s; end its model earlier or shorten the transition`);
      }
    }
    // An incoming join and a fade-out may overlap (the tour fixture's last
    // shot does): the join is drawn until it ends, then the fade-out.
  }
}
const modelSeconds=model=>model.keys?model.keys.map(k=>k.seconds):[model.from,model.to];
const lastSeconds=model=>model.keys?model.keys.at(-1).seconds:model.to;
// Model seconds per video second at a shot's end: the last segment's average
// rate times its curve's end slope, so a segment easing to rest, or a hold, holds.
export function endRate(shot){
  const duration=shot.end-shot.start,m=shot.model;
  const keys=m.keys??[{at:0,seconds:m.from},{at:duration,seconds:m.to}];
  const a=keys.at(-2),b=keys.at(-1);
  return (b.seconds-a.seconds)/(b.at-a.at)*endSlope(b.ease??'linear');
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
// What speech needs before anything is resolved: the narration, the audio
// settings and the build directory.
export async function pendingMovie(file){
  const {doc,documentPath,base,build}=await readMovie(file);
  return {movie:MOVIE_FORMAT,audio:doc.audio,paths:{episode:documentPath,base,build},
    chapters:doc.chapters.map(c=>({id:c.id,narration:c.narration}))};
}
// The speech command's first step on a document: generate each missing take.
export async function generateMovieTakes(file){return generateTakes(await pendingMovie(file));}

// The text of each source excerpt's lines, read through the root, for the
// token checks (the Python side reads the same).
export async function excerptSources(doc,base){
  const sources={};
  for(const [name,excerpt] of Object.entries(doc.sourceCode??{})){
    const text=await readFile(resolve(base,excerpt.file),'utf8').catch(()=>null);
    if(text===null)continue;
    const lines=text.replace(/\r\n/g,'\n').split('\n'),[first,last]=excerpt.lines;
    sources[name]=lines.slice(first-1,last).join('\n');
  }
  return sources;
}

// The view elements' cameras that need Viewer API 28: a mark or a highlight,
// or a lens or up other than the one the view mounts with.
export function movieViewerApi(film){
  const reasons=[],unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
  const differs=(c,d)=>c.fov!==d.fov||unit(c.up).some((v,i)=>Math.abs(v-unit(d.up)[i])>1e-12);
  for(const chapter of film.chapters)for(const shot of chapter.shots){
    for(const cue of shot.cues)for(const action of cue.actions){
      const element=chapter.elements[action.element];if(element?.kind!=='view')continue;
      if(['ring','label','arrow'].includes(action.action))reasons.push(`marks (shot ${shot.id})`);
      if(action.action==='highlight')reasons.push(`highlight (shot ${shot.id})`);
      if(action.action==='move'&&differs(film.cameras[action.camera],film.cameras[element.camera]))reasons.push(`camera up/field of view (shot ${shot.id})`);
    }
  }
  const unique=[...new Set(reasons)];
  return {api:unique.length?28:21,reasons:unique};
}

// Load, check, resolve against the cached takes, write the resolved document,
// then check it against the project (design D1.4).
export async function loadMovie(file){
  const {doc,documentPath,base,build}=await readMovie(file);
  const manifestPath=await realpath(resolve(base,doc.model.manifest));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  checkMovie(doc,{manifest,sources:await excerptSources(doc,base)});
  const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
  need(contained(repository,base),'Movie root must live inside its project repository');
  for(const module of doc.stage.modules){
    const path=resolve(base,module);
    const found=await stat(path).then(s=>s.isFile(),()=>false);
    need(found,`stage.modules: ${module} does not exist (${path})`);
    need(contained(repository,await realpath(path)),`stage.modules: ${module} is outside the project repository`);
  }
  const pending={audio:doc.audio,paths:{build},chapters:doc.chapters.map(c=>({id:c.id,narration:c.narration}))};
  const needed=chaptersNeedingTakes(doc),takes={},wordTiming={};
  for(const [i,chapter] of doc.chapters.entries()){
    if(!needed.includes(chapter.id))continue;
    const take=await cachedTake(pending,i);
    need(take,missingTake(chapter.id));
    takes[chapter.id]={alignment:take.alignment};
    for(const shot of chapter.shots)wordTiming[shot.id]={sha256:take.sha256};
  }
  const resolved=resolveMovie(doc,takes);
  await json(resolve(build,'movie-resolved.json'),resolved);
  const film=structuredClone(resolved);
  checkProject(film,manifest);
  for(const path of Object.values(film.evidence))await readFile(resolve(base,path));
  const sourceRevision=(await readFile(resolve(dirname(manifestPath),'source-revision.txt'),'utf8')).trim();
  need(film.model.sourceRevision===sourceRevision,'Pin model.sourceRevision to the export source-revision.txt before rendering');
  film.paths={episode:documentPath,production:documentPath,base,manifest:manifestPath,repository,build};
  film.source='movie';
  film.wordTiming=wordTiming;
  film.excerpts=await loadSourceCode({sourceCode:film.sourceCode,model:film.model,paths:film.paths});
  await loadPictures(film);
  const {checkFilm}=await import('./timeline.mjs');
  checkFilm(film);
  film.viewerApi=movieViewerApi(film);
  return film;
}

// What validateEpisode checks of the model and output, for a document.
function checkProject(film,manifest){
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  need(manifest.animation?.loop===film.model.expectedDurationSeconds,'Model duration differs from production settings; recheck the exported simulation');
  need(film.model.timeMode==='normalized-loop'&&!manifest.program&&!manifest.clocked,'Only posed normalized-loop models are supported');
  need(finite(film.model.expectedDurationSeconds)&&film.model.expectedDurationSeconds>0,'Invalid model duration');
  for(const k of ['width','height','fps'])need(Number.isInteger(film.output[k])&&film.output[k]>0,`Invalid output ${k}`);
  need(film.output.width%2===0&&film.output.height%2===0,'Video dimensions must be even');
  const frames=film.output.durationSeconds*film.output.fps;
  need(Math.abs(frames-Math.round(frames))<1e-6,'Video duration must be a whole number of frames');
  for(const [name,c] of Object.entries(film.cameras)){
    need(c.position.length===3&&c.target.length===3&&c.up.length===3,`Invalid camera ${name}`);
    need(c.position.some((v,i)=>v!==c.target[i]),`Camera ${name} coincides with target`);
    need(c.up.some(v=>v!==0)&&c.fov>0&&c.fov<180,`Invalid camera ${name}`);
  }
}
