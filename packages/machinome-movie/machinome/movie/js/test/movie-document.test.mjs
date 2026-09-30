// Timeline layer (pure): the movie document's schema, static checks and
// anchor resolution against take doubles, over the shared fixtures and inline
// cases. No browser, no FFmpeg, no provider.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir,access} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkMovie,checkMovieExport,resolveMovie,chaptersNeedingTakes,MOVIE_FORMAT} from '../src/movie.mjs';
import {SCHEMA_KEYWORDS,schemaKeywords,loadMovieSchema} from '../src/schema.mjs';
import {chaptersOf,chapterOf,narrationOf,takeOffset} from '../src/chapters.mjs';
import {validateEpisode} from '../src/episode.mjs';
import {outputShotUnits} from '../src/shot-cache.mjs';
import {resolveWordTiming} from '../src/words.mjs';
import {evenAlignment} from './project-fixture.mjs';

const fixtures=join(dirname(fileURLToPath(import.meta.url)),'..','fixtures');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const exists=file=>access(file).then(()=>true,()=>false);
// Takes of a fixture document, by chapter; a chapter whose anchors need a take
// that the fixtures lack fails naming the file to add.
async function fixtureTakes(name,doc){
  const takes={};
  for(const chapter of doc.chapters){
    const file=join(fixtures,'takes',name,`${chapter.id}.json`);
    if(await exists(file))takes[chapter.id]=await json(file);
    else assert.ok(!chaptersNeedingTakes(doc).includes(chapter.id),
      `fixture ${name} needs fixtures/takes/${name}/${chapter.id}.json for the spoken anchors of chapter ${chapter.id}`);
  }
  return takes;
}
const minimal=async()=>json(join(fixtures,'documents','bare.json'));
// Instants every resolved anchor of a document lands on, in film seconds.
function anchoredInstants(doc,resolved){
  const out=[],isAnchor=v=>v&&typeof v==='object'&&(v.spoken!==undefined||v.spokenEnd!==undefined);
  const shots=new Map(resolved.shots.map(s=>[s.id,s]));
  for(const chapter of doc.chapters)for(const shot of chapter.shots){
    const r=shots.get(shot.id);
    if(isAnchor(shot.until))out.push({where:`${shot.id} until`,t:r.end});
    (function walk(value,resolvedValue,path){
      if(Array.isArray(value))value.forEach((v,i)=>walk(v,resolvedValue?.[i],`${path}[${i}]`));
      else if(value&&typeof value==='object'){
        for(const [key,v] of Object.entries(value)){
          if(isAnchor(v))out.push({where:`${shot.id} ${path}.${key}`,t:r.start+resolvedValue[key]});
          else walk(v,resolvedValue?.[key],`${path}.${key}`);
        }
      }
    })(Object.fromEntries(Object.entries(shot).filter(([k])=>k!=='until')),r,'');
  }
  return out;
}

test('the schema uses only keywords the validator implements',async()=>{
  const schema=await loadMovieSchema();
  const used=schemaKeywords(schema);
  for(const keyword of used)assert.ok(SCHEMA_KEYWORDS.has(keyword),`schema keyword ${keyword} is not implemented by src/schema.mjs`);
  assert.equal(schema.$schema,'https://json-schema.org/draft/2020-12/schema');
});

test('every registered document validates and resolves to its pinned resolution, twice identically, on the frame grid',async()=>{
  const {documents}=await json(join(fixtures,'manifest.json'));
  assert.ok(documents.length>=2);
  for(const name of documents){
    const doc=await json(join(fixtures,'documents',`${name}.json`));
    assert.equal(doc.format,MOVIE_FORMAT,name);
    checkMovie(doc);
    const takes=await fixtureTakes(name,doc);
    const pinned=join(fixtures,'resolved',`${name}.json`);
    assert.ok(await exists(pinned),`fixture ${name} has no pinned resolution fixtures/resolved/${name}.json`);
    const once=resolveMovie(structuredClone(doc),takes),twice=resolveMovie(structuredClone(doc),takes);
    assert.equal(JSON.stringify(once),JSON.stringify(twice),`${name} resolves twice identically`);
    assert.deepEqual(once,await json(pinned),`${name} resolution differs from fixtures/resolved/${name}.json`);
    const fps=doc.output.fps;
    for(const {where,t} of anchoredInstants(doc,once))
      assert.ok(Math.abs(t*fps-Math.round(t*fps))<1e-6,`${name} ${where} at ${t} is not on the ${fps} fps grid`);
    assert.equal(once.output.durationSeconds,once.shots.at(-1).end);
  }
});

// A fixture document's root resolves from its own file, as a document's does;
// when its export is there (the Python side's fixture project), the parts it
// names are checked against it too, as loading does before any take is read.
test('every invalid fixture is refused naming what it must',async()=>{
  const names=(await readdir(join(fixtures,'invalid'))).filter(n=>n.endsWith('.json')).sort();
  assert.ok(names.length>=9);
  for(const file of names){
    const fixture=await json(join(fixtures,'invalid',file));
    assert.ok(fixture.name&&fixture.document&&Array.isArray(fixture.must_mention)&&fixture.must_mention.length,`${file} shape`);
    let message=null;
    try{
      checkMovie(fixture.document);
      const manifest=resolve(fixtures,'invalid',fixture.document.root,fixture.document.model.manifest);
      if(await exists(manifest))checkMovieExport(fixture.document,await json(manifest));
    }catch(error){message=error.message;}
    assert.ok(message!==null,`${file} was not refused`);
    for(const word of fixture.must_mention)assert.ok(message.includes(word),`${file}: refusal "${message}" does not mention "${word}"`);
  }
});

// A one-chapter, two-shot document whose take is inline and exact.
function inline({narration='The wheel turns. Then the saw cuts.',fps=10,shots,marks,audio,step=.1}={}){
  const doc={format:MOVIE_FORMAT,id:'inline',title:'Inline',root:'..',output:{width:320,height:180,fps},
    model:{manifest:'m.json',expectedDurationSeconds:20,timeMode:'normalized-loop',sourceRevision:null},
    audio:{provider:'elevenlabs',model:'test-model',voice:'v',...audio},cameras:{a:{position:[0,-1,0],target:[0,0,0],up:[0,0,1],fov:37}},
    layers:{},evidence:{},...(marks?{marks}:{}),
    chapters:[{id:'opening',narration,shots:shots??[
      {id:'wheel',until:{spoken:'Then'},simulation:{from:0,to:4},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]},
      {id:'saw',until:{spokenEnd:'the saw cuts.',plus:.5},simulation:{from:4,to:8},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]}]}]};
  let spoken=narration;for(const [k,v] of Object.entries(doc.audio.replacements??{}))spoken=spoken.replaceAll(k,v);
  return {doc,takes:{opening:{alignment:evenAlignment(spoken,step),duration:Array.from(spoken).length*step}}};
}
const plainShot=(id,until,extra={})=>({id,until,simulation:{from:0,to:4},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});

test('spoken, spokenEnd and plus resolve from the chapter take and snap to the frame grid',()=>{
  const {doc,takes}=inline();
  const r=resolveMovie(doc,takes);
  // "Then" is character 17: 0.2 offset + 1.7 s = 1.9 s; "cuts." ends at character 34: 0.2 + 3.5 + 0.5 = 4.2 s.
  assert.deepEqual(r.shots.map(s=>[s.id,s.start,s.end]),[['wheel',0,1.9],['saw',1.9,4.2]]);
  assert.deepEqual(r.chapters,[{id:'opening',narration:doc.chapters[0].narration,speechOffset:.2,start:0,end:4.2,shots:['wheel','saw']}]);
  assert.equal(r.output.durationSeconds,4.2);
  assert.equal(r.format,'machinome-video-draft/0.4');
  assert.equal(r.movie,MOVIE_FORMAT);
  assert.equal(r.shots[0].direction,'');
  // Off the grid: 0.23 + 1.7 - 0.34 = 1.59 s, snapped to 1.6 s.
  const off=inline();off.doc.chapters[0].speechOffset=.23;off.doc.chapters[0].shots[0].until={spoken:'Then',plus:-.34};
  const s=resolveMovie(off.doc,off.takes);
  assert.equal(s.shots[0].end,1.6);assert.equal(s.chapters[0].speechOffset,.23);
  // A pronunciation alias: the phrase is found in the spoken form of the take.
  const alias=inline({narration:'Machinome turns. Then it stops.',audio:{replacements:{Machinome:'mah-SHEEN-ohm'}}});
  alias.doc.chapters[0].shots[1].until={spokenEnd:'it stops.'};
  // Spoken: "mah-SHEEN-ohm turns. Then it stops." "Then" at 21, "." ends at 35.
  const a=resolveMovie(alias.doc,alias.takes);
  assert.deepEqual(a.shots.map(s=>[s.start,s.end]),[[0,2.3],[2.3,3.7]]);
  // Onset is the first letter or digit of the phrase's first word.
  const quoted=inline({narration:'He said "Cut" then left.'});
  quoted.doc.chapters[0].shots[0].until={spoken:'"Cut"'};quoted.doc.chapters[0].shots[1].until={spokenEnd:'left.'};
  assert.equal(resolveMovie(quoted.doc,quoted.takes).shots[0].end,1.1);
});

test('cue, key, typing and picture view anchors become shot-local; literal numbers are kept',()=>{
  const {doc,takes}=inline({marks:{rest:2,go:3}});
  const [wheel,saw]=doc.chapters[0].shots;
  wheel.camera.push({at:{spoken:'wheel'},preset:'a',ease:'out'});
  wheel.overlays=[{from:.25,to:{spoken:'Then'},text:'Wheel',position:'top'}];
  saw.set='paper-split';
  saw.simulation={from:{mark:'rest'},to:{mark:'go',plus:1.5},
    keyframes:[{at:0,seconds:{mark:'rest'}},{at:{spoken:'saw'},seconds:{mark:'go',plus:-.5},ease:'in'},{at:{spokenEnd:'the saw cuts.',plus:.5},seconds:{mark:'go',plus:1.5}}]};
  saw.code={snippet:'x',typing:[{from:{spoken:'Then'},to:{spokenEnd:'saw'},throughLine:1}]};
  saw.highlight=[{from:{spoken:'saw',plus:-.2},to:{spokenEnd:'cuts'},parts:['p']}];
  saw.pictures=[{from:0,to:{spoken:'cuts'},still:'s',view:[{at:0,center:[.5,.5],zoom:1},{at:{spoken:'saw'},center:[.5,.5],zoom:1.2}]}];
  const r=resolveMovie(doc,takes);
  const [w,s]=r.shots;
  // "wheel" at character 4: 0.2 + 0.4 = 0.6 s.
  assert.deepEqual(w.camera,[{at:0,preset:'a'},{at:.6,preset:'a',ease:'out'}]);
  assert.deepEqual(w.overlays,[{from:.25,to:1.9,text:'Wheel',position:'top'}]);
  const local=t=>t-1.9;
  // "saw" at character 26: 0.2 + 2.6 = 2.8 s; "saw" ends at character 28 (2.9 + 0.2 = 3.1 s); "cuts" starts at 30 (3.2 s), ends 33 (3.6 s).
  assert.equal(s.layout,undefined);assert.equal(s.set,undefined);assert.equal(s.until,undefined);
  assert.deepEqual(s.simulation,{from:2,to:4.5,keyframes:[{at:0,seconds:2},{at:local(2.8),seconds:2.5,ease:'in'},{at:s.end-s.start,seconds:4.5}]});
  assert.equal(s.simulation.keyframes.at(-1).at,s.end-s.start);
  assert.deepEqual(s.code.typing,[{from:0,to:local(3.1),throughLine:1}]);
  assert.deepEqual(s.highlight,[{from:local(2.6),to:local(3.6),parts:['p']}]);
  assert.deepEqual(s.pictures[0].view.map(v=>v.at),[0,local(2.8)]);
  assert.equal(s.pictures[0].to,local(3.2));
});

test('sets map to the three layouts, with today\'s defaults',()=>{
  const {doc,takes}=inline();
  const [wheel,saw]=doc.chapters[0].shots,code={snippet:'x',typing:[{from:0,to:.5,throughLine:1}]};
  wheel.set='source-only';wheel.code=code;saw.code=code;
  const r=resolveMovie(doc,takes);
  assert.equal(r.shots[0].layout,'source-only');
  assert.equal(r.shots[1].layout,undefined);
  for(const set of ['paper-split','source-only']){
    const bad=inline();bad.doc.chapters[0].shots[0].set=set;
    assert.throws(()=>checkMovie(bad.doc),new RegExp(`Set ${set} needs code: shot wheel \\(chapter opening\\)`));
  }
});

test('marks resolve with plus; an unknown mark is refused naming shot and mark',()=>{
  const {doc,takes}=inline({marks:{pull_start:436}});
  doc.chapters[0].shots[0].simulation={from:{mark:'pull_start'},to:{mark:'pull_start',plus:2}};
  const r=resolveMovie(doc,takes);
  assert.deepEqual(r.shots[0].simulation,{from:436,to:438});
  doc.chapters[0].shots[1].simulation.to={mark:'cycle_end'};
  assert.throws(()=>checkMovie(doc),/^Error: Unknown mark: cycle_end \(simulation\.to of shot saw in chapter opening\)$/);
});

test('a chapter with spoken anchors and no take is refused naming it; one without anchors needs none',async()=>{
  const {doc}=inline();
  assert.deepEqual(chaptersNeedingTakes(doc),['opening']);
  assert.throws(()=>resolveMovie(doc,{}),
    /^Error: Chapter opening has spoken anchors and no cached narration take; run the speech command first \(check, preview and render never generate speech\)$/);
  const m=await minimal();
  assert.deepEqual(chaptersNeedingTakes(m),[]);
  assert.equal(resolveMovie(m,{}).output.durationSeconds,2);
});

test('a phrase the take lacks or repeats is refused naming chapter, shot, field and phrase',()=>{
  const {doc,takes}=inline();
  takes.opening.alignment=evenAlignment('The wheel turns. Than the saw cuts.',.1);
  assert.throws(()=>resolveMovie(doc,takes),/Spoken phrase is absent from the recorded narration of chapter opening: Then \(until of shot wheel\)/);
  takes.opening.alignment=evenAlignment('The wheel turns. Then Then the saw cuts.',.1);
  assert.throws(()=>resolveMovie(doc,takes),/Spoken phrase is ambiguous in the recorded narration of chapter opening: Then \(until of shot wheel\)/);
});

test('an anchor outside its shot and an anchored until at or before the start are refused',()=>{
  const {doc,takes}=inline();
  doc.chapters[0].shots[1].overlays=[{from:{spoken:'wheel'},to:{spoken:'cuts'},text:'x',position:'top'}];
  assert.throws(()=>resolveMovie(doc,takes),/Anchor spoken "wheel" of overlays\[0\]\.from in shot saw \(chapter opening\) falls outside the shot/);
  const late=inline();
  late.doc.chapters[0].shots[1].until={spoken:'wheel'};
  assert.throws(()=>resolveMovie(late.doc,late.takes),/Shot saw ends at or before its start: until spoken "wheel" \(chapter opening\)/);
  const minus=inline();
  minus.doc.chapters[0].shots[0].until={spoken:'wheel',plus:-1};
  assert.throws(()=>resolveMovie(minus.doc,minus.takes),/Shot wheel ends at or before its start: until spoken "wheel" plus -1 \(chapter opening\)/);
});

test('fades are accepted only at the film\'s ends, across chapters',()=>{
  const {doc}=inline();
  doc.chapters.push({id:'closing',narration:'Again.',shots:[plainShot('again',2,{fadeIn:{duration:.5}})]});
  assert.throws(()=>checkMovie(doc),/fadeIn is accepted only on the film's first shot: shot again \(chapter closing\)/);
  delete doc.chapters[1].shots[0].fadeIn;doc.chapters[0].shots[1].fadeOut={duration:.5};
  assert.throws(()=>checkMovie(doc),/fadeOut is accepted only on the film's last shot: shot saw \(chapter opening\)/);
  doc.chapters[0].shots[1].fadeOut=undefined;delete doc.chapters[0].shots[1].fadeOut;
  doc.chapters[1].shots[0].fadeOut={duration:.5};doc.chapters[0].shots[0].fadeIn={duration:.5};
  checkMovie(doc);
});

test('the schema refuses unknown fields and wrong types, naming the field and where',async()=>{
  const m=await minimal();
  m.chapters[0].shots[0].camera[0].eas='out';
  assert.throws(()=>checkMovie(m),/Unknown field: eas \(chapters\/0\/shots\/0\/camera\/0\)/);
  const t=await minimal();t.chapters[0].shots[0].until='2';
  assert.throws(()=>checkMovie(t),/Invalid movie document: chapters\/0\/shots\/0\/until must be one of: seconds, spoken anchor, spokenEnd anchor/);
  const r=await minimal();delete r.chapters[0].narration;
  assert.throws(()=>checkMovie(r),/Missing field: narration \(chapters\/0\)/);
  const id=await minimal();id.chapters[0].id='Opening Chapter';
  assert.throws(()=>checkMovie(id),/Invalid movie document: chapters\/0\/id must match/);
});

test('word timing reads the shot\'s chapter take at its offset from the shot',async()=>{
  const doc=await json(join(fixtures,'documents','two-chapters.json'));
  const takes=await fixtureTakes('two-chapters',doc),e=resolveMovie(doc,takes);
  e.sourceCode={coupling:{file:'models/fixture.py',lines:[3,3],text:'waterwheel.drives(crankshaft)'}};
  const read=async shot=>({sha256:`take-${chapterOf(e,shot).id}`,alignment:takes[chapterOf(e,shot).id].alignment});
  await resolveWordTiming(e,read);
  const coupling=e.shots.find(s=>s.id==='coupling'),drive=e.chapters.find(c=>c.id==='drive');
  assert.equal(chapterOf(e,coupling),drive);
  assert.equal(narrationOf(e,coupling),drive.narration);
  assert.equal(takeOffset(e,coupling),drive.start+drive.speechOffset-coupling.start);
  // "waterwheel" is character 41 of the drive narration at 0.05 s a character.
  const onset=drive.start+drive.speechOffset+takes.drive.alignment.character_start_times_seconds[41];
  assert.ok(Math.abs(e.wordTiming.coupling.emphasis[0].cues[0].from-(onset-coupling.start))<1e-9);
  assert.equal(e.wordTiming.coupling.sha256,'take-drive');
  // The first shot of a chapter reads the take at exactly the chapter's offset.
  const wheel=e.shots.find(s=>s.id==='wheel');
  assert.equal(takeOffset(e,wheel),drive.speechOffset);
  assert.equal(e.wordTiming.wheel.overlays[0].onsets[0],drive.speechOffset);
});

test('a YAML-shaped episode is one chapter per shot, its offsets bit for bit',()=>{
  const e={shots:[{id:'a',start:0,end:5.366,narration:'One.',speechOffset:.3},{id:'b',start:5.366,end:9,narration:'Two.'}]};
  assert.deepEqual(chaptersOf(e),[
    {id:'a',narration:'One.',speechOffset:.3,start:0,end:5.366,shots:['a']},
    {id:'b',narration:'Two.',speechOffset:.2,start:5.366,end:9,shots:['b']}]);
  assert.ok(Object.is(takeOffset(e,e.shots[1]),.2));
  assert.equal(narrationOf(e,e.shots[1]),'Two.');
});

test('a duration on the frame grid is a whole number of frames despite floating point',()=>{
  // 31/30 × 30 is 31.000000000000004 in floating point.
  const d=31/30,e={format:'machinome-video-draft/0.4',output:{width:320,height:180,fps:30,durationSeconds:d},
    model:{expectedDurationSeconds:20,timeMode:'normalized-loop'},cameras:{a:{position:[0,-1,0],target:[0,0,0],up:[0,0,1],fov:37}},
    layers:{},evidence:{},shots:[{id:'only',start:0,end:d,narration:'x',direction:'',simulation:{from:0,to:1},
      camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]}]};
  validateEpisode(e,{animation:{loop:20}});
  assert.equal(outputShotUnits(e,30).count,31);
  e.output.durationSeconds=e.shots[0].end=1.05;
  assert.throws(()=>validateEpisode(e,{animation:{loop:20}}),/Video duration must be a whole number of frames/);
});

test('an anchor on a cut made of literal durations lands exactly on it',()=>{
  // 0.1 + 0.2 is 0.30000000000000004; "A" is spoken at 0.3 + 0 s, snapped to 0.3.
  const {doc,takes}=inline({narration:'A wheel turns. Then the saw cuts.',shots:[
    plainShot('one',.1),plainShot('two',.2),
    plainShot('three',{spokenEnd:'cuts.'},{overlays:[{from:{spoken:'A'},to:{spoken:'Then'},text:'x',position:'top'}]})]});
  doc.chapters[0].speechOffset=.3;
  const three=resolveMovie(doc,takes).shots[2];
  assert.equal(three.start,.1+.2);
  assert.ok(Object.is(three.overlays[0].from,0));
});

test('camera presets, the last model keyframe and named parts are checked before any take',()=>{
  const {doc}=inline();
  doc.chapters[0].shots[1].camera.push({at:1,preset:'b'});
  assert.throws(()=>checkMovie(doc),/Unknown camera preset: b \(camera\[1\] of shot saw in chapter opening\)/);
  const keys=inline();
  const saw=keys.doc.chapters[0].shots[1];
  saw.simulation.keyframes=[{at:0,seconds:4},{at:{spokenEnd:'the saw cuts.',plus:.5},seconds:8}];
  checkMovie(keys.doc);
  saw.simulation.keyframes[1].at={spokenEnd:'the saw cuts.'};
  assert.throws(()=>checkMovie(keys.doc),/Model keyframes must end at the shot's until: shot saw \(chapter opening\)/);
  const parts=inline(),manifest={root:{name:'m',children:[{name:'Feed',children:[{name:'Pawl'}]}]}};
  parts.doc.layers={pawl:[['Feed','Pawl']]};
  parts.doc.chapters[0].shots[1].highlight=[{from:0,to:1,parts:['pawl',['Feed','Pawl']]}];
  checkMovieExport(parts.doc,manifest);
  parts.doc.chapters[0].shots[1].annotations=[{from:0,to:1,kind:'ring',part:['Feed','Pawn']}];
  assert.throws(()=>checkMovieExport(parts.doc,manifest),/^Error: Missing assembly path: Feed\/Pawn \(annotations\[0\] of shot saw in chapter opening\)$/);
  parts.doc.chapters[0].shots[1].annotations=[{from:0,to:1,kind:'ring',part:'pawls'}];
  assert.throws(()=>checkMovieExport(parts.doc,manifest),/Unknown layer: pawls \(annotations\[0\] of shot saw in chapter opening\)/);
  parts.doc.layers.pawl=[['Feed','Pawn']];delete parts.doc.chapters[0].shots[1].annotations;
  assert.throws(()=>checkMovieExport(parts.doc,manifest),/Missing assembly path: Feed\/Pawn \(layer pawl\)/);
});
