// Layer 3 (pure): what a live session answers of a generation (the
// live-server change, design D5 and D11). The frame route is the renderer's
// frame at the nearest output instant, clamped to the film; the outline is
// the film's shape as the player reads it; the take document is what the
// pose rule reads. The shared fixtures `count` (a clocked take) and `tour`
// (a posed loop with a reframe and a wipe), resolved; no DOM, no browser, no
// server.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {frameFor,outline,takeDocument,markInstants} from '../src/live.mjs';
import {resolveMovie,excerptSources,movieViewerApi} from '../src/movie.mjs';
import {frameAt,filmShots,modelSecondsAt} from '../src/timeline.mjs';
import {bankAt} from '../src/take.mjs';

const fixtures=join(dirname(fileURLToPath(import.meta.url)),'..','fixtures');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const refusal=fn=>{try{fn();}catch(error){return error;}assert.fail('was not refused');};
const FACTS={number:1,loadedAt:'2026-10-04T12:00:00.000Z',stageSha256:'a'.repeat(64),
  speech:{mix:false,captions:false},refusal:null};

// The counter resolved against its take, with its excerpt attached as a load
// attaches it (the source panel in carry reads it) and the API it requires.
async function count(){
  const doc=await json(join(fixtures,'documents','count.json'));
  const film=resolveMovie(doc,{counting:await json(join(fixtures,'takes','count','counting.json'))});
  const text=(await excerptSources(doc,resolve(fixtures,'documents',doc.root))).relations;
  film.excerpts={relations:{file:'models/counter.py',lines:doc.sourceCode.relations.lines,text}};
  film.viewerApi=movieViewerApi(film);
  return film;
}
async function tour(){
  const film=await json(join(fixtures,'resolved','tour.json'));
  film.viewerApi=movieViewerApi(film);
  return film;
}

test('the frame route gives the renderer\'s frame at the nearest output instant',async()=>{
  const film=await count(),fps=film.output.fps;
  assert.equal(fps,10);
  // round(t·fps)/fps: the renderer's grid (outputShotUnits).
  for(const [t,index] of [[0,0],[0.04,0],[0.06,1],[3.24,32],[6.04,60],[6.06,61],[11.31,113]])
    assert.deepEqual(frameFor(film,t),frameAt(film,index/fps),`t = ${t}`);
  assert.deepEqual(frameFor(film,6.04),frameFor(film,6.04),'the same instant twice');
});

test('the frame route clamps to the film\'s first and last frames',async()=>{
  const film=await count(),fps=film.output.fps,last=Math.round(film.output.durationSeconds*fps)-1;
  assert.equal(last,113);
  for(const t of [-1,-0.04,-1e9])assert.deepEqual(frameFor(film,t),frameAt(film,0),`t = ${t}`);
  // The film's end is not a frame: its last frame is.
  for(const t of [film.output.durationSeconds,11.38,99,1e9])assert.deepEqual(frameFor(film,t),frameAt(film,last/fps),`t = ${t}`);
});

test('the frame route refuses a time that is not a finite number, naming t',async()=>{
  const film=await count();
  for(const t of [Number.NaN,Infinity,-Infinity,undefined,null,'1']){
    const error=refusal(()=>frameFor(film,t));
    assert.ok(error instanceof RangeError,`${String(t)}: ${error}`);
    assert.match(error.message,/\bt\b/,`${String(t)}: ${error.message}`);
  }
});

test('the outline of the counter: output at the session\'s width, chapters, shots with their resolved model, cues in video time, the take',async()=>{
  const film=await count(),o=outline(film,{width:640,...FACTS});
  assert.deepEqual([o.id,o.title],['count','Count']);
  assert.deepEqual(o.output,{width:640,height:360,fps:10,duration:11.4});
  assert.deepEqual(o.chapters,[{id:'counting',start:0,end:11.4}]);
  const shots=filmShots(film);
  assert.deepEqual(o.shots,shots.map(({chapter,shot})=>({id:shot.id,chapter:chapter.id,start:shot.start,end:shot.end,set:shot.set,
    join:shot.transition?{kind:shot.transition.kind,duration:shot.transition.duration}:null,model:shot.model})));
  assert.deepEqual(o.shots.map(s=>[s.id,s.set,s.join]),[['once','frame',null],['nine','frame',null],['carry','split',{kind:'dissolve',duration:0.5}]]);
  // The model as the resolved document records it, the crossing included.
  const pinned=(await json(join(fixtures,'resolved','count.json'))).chapters[0].shots;
  assert.deepEqual(o.shots.map(s=>s.model),pinned.map(s=>s.model));
  assert.equal(o.shots[1].model.crossing.mark,'nine');
  // Cues by their index in their shot, in video time.
  const carry=shots[2].shot;
  assert.deepEqual(o.cues,carry.cues.map((cue,i)=>({shot:'carry',id:`cues[${i}]`,at:carry.start+cue.at,
    until:cue.until===undefined?null:carry.start+cue.until})));
  assert.deepEqual(o.cues.map(c=>[c.id,c.until===null]),[['cues[0]',true],['cues[1]',true],['cues[2]',false]]);
  // The clocked take under `take`, its marks sorted by time, and where its
  // document is served.
  assert.deepEqual(o.takes,{take:{kind:'clocked',duration:8,
    marks:[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}],url:'/take.json'}});
  assert.deepEqual(o.speech,{mix:false,captions:false});
  assert.deepEqual(o.stage,{sha256:'a'.repeat(64)});
  assert.deepEqual(o.viewer,{api:29});
  assert.deepEqual(o.generation,{number:1,loadedAt:'2026-10-04T12:00:00.000Z'});
  assert.equal(o.refusal,null);
  assert.deepEqual(JSON.parse(JSON.stringify(o)),o,'the outline is JSON');
  assert.deepEqual(outline(film,{width:640,...FACTS}),o,'the same outline twice');
});

test('the outline scales the output to the session\'s width by the renderer\'s rule, and carries the facts it is given',async()=>{
  const film=await count();
  assert.deepEqual(outline(film,{width:960,...FACTS}).output,{width:960,height:540,fps:10,duration:11.4});
  assert.deepEqual(outline(film,{width:322,...FACTS}).output,{width:322,height:182,fps:10,duration:11.4});
  const refused={message:'Movie document is not valid JSON: …',at:'2026-10-04T12:01:00.000Z'};
  const o=outline(film,{width:640,...FACTS,number:4,speech:{mix:true,captions:true},refusal:refused});
  assert.deepEqual([o.generation.number,o.speech,o.refusal],[4,{mix:true,captions:true},refused]);
});

test('the outline of the tour: a posed loop under `loop`, its period and marks in model seconds, and its joins',async()=>{
  const film=await tour(),o=outline(film,{width:960,...FACTS});
  assert.deepEqual(o.output,{width:960,height:540,fps:30,duration:18.9});
  assert.deepEqual(o.takes,{loop:{kind:'loop',duration:20,marks:[{name:'rise',time:5},{name:'top',time:10},{name:'fall',time:15}]}});
  assert.deepEqual(o.chapters.map(c=>c.id),['opening','balance','tip']);
  const joins=Object.fromEntries(o.shots.filter(s=>s.join).map(s=>[s.id,s.join.kind]));
  assert.deepEqual(joins,{question:'reframe',source:'dissolve',push:'wipe',rhythm:'dissolve',invitation:'dissolve'});
  assert.deepEqual(o.viewer,{api:28});
});

test('the take document is the length, the marks and the take block the pose rule reads; a loop has none',async()=>{
  const film=await count(),doc=takeDocument(film);
  assert.deepEqual(doc,{model:{expectedDurationSeconds:8},marks:film.marks,take:film.take});
  assert.equal(JSON.stringify(doc),JSON.stringify({model:{expectedDurationSeconds:film.model.expectedDurationSeconds},marks:film.marks,take:film.take}),'verbatim');
  for(const t of [0,1,2,4.5,6,7.25,8])assert.deepEqual(bankAt(doc,t),bankAt(film,t),`bankAt at ${t}`);
  assert.equal(takeDocument(await tour()),null);
});

// The player-page change, design D3: the marks in video time, at the frames
// where a shot's model time reaches them on the renderer's grid.
test('the marks in video time: the first frame of a shot that reaches each mark, and none for a mark no frame reaches',async()=>{
  const film=await count();
  // nine begins at the mark one; carry begins at the mark nine; ten (8 s) is
  // past carry's last frame, which poses 7.97 s.
  assert.deepEqual(markInstants(film),[{name:'one',shot:'nine',at:3.2},{name:'nine',shot:'carry',at:5.3}]);
  const carry=filmShots(film).find(({shot})=>shot.id==='carry').shot;
  assert.ok(modelSecondsAt(carry,11.3-carry.start)<8,'the last frame does not reach ten');
  assert.deepEqual(markInstants(film),markInstants(film),'twice the same');
  // A loop's marks are model seconds, read against each shot's model time:
  // question starts past 4 s and crosses rise (5 s), source starts at top
  // (10 s), push crosses fall (15 s); the keyed shot rise starts at 5 s and
  // eases through 10 s.
  const loop=await tour(),fps=loop.output.fps;
  assert.deepEqual(markInstants(loop).map(m=>[m.name,m.shot,Math.round(m.at*fps)]),
    [['rise','question',91],['top','source',198],['fall','push',325],['rise','rise',343],['top','rise',405]]);
  for(const {at} of markInstants(loop))assert.equal(at,Math.round(at*fps)/fps,'on the grid');
  // The outline carries them.
  assert.deepEqual(outline(film,{width:640,...FACTS}).marks,markInstants(film));
  assert.deepEqual(outline(loop,{width:640,...FACTS}).marks,markInstants(loop));
});

test('a mark is flagged once where a shot holds at it, and where a shot crosses it backwards',()=>{
  const shot=(id,start,end,model)=>({id,start,end,set:'frame',places:{},cues:[],model});
  const film={output:{fps:10,durationSeconds:3,width:640,height:360},marks:{m:1},model:{timeMode:'take',expectedDurationSeconds:2},
    chapters:[{id:'c',start:0,end:3,elements:{},shots:[shot('held',0,1,{from:1,to:1}),shot('back',1,2,{from:2,to:0}),shot('past',2,3,{from:1.5,to:2})]}]};
  assert.deepEqual(markInstants(film),[{name:'m',shot:'held',at:0},{name:'m',shot:'back',at:1.5}]);
});
