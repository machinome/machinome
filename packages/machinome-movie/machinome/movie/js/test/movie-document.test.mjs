// Layer 2 (pure): the document contract over the shared fixtures/. Every
// registered document validates, passes the static checks with its export and
// its excerpts read through its root, and resolves against its takes to exactly
// its pinned resolution, twice identically, on the frame grid; every invalid
// fixture is refused naming its must_mention words. Then the refusals that need
// resolved times, by name, and the three readings the design records (D2.3).
// No browser, no FFmpeg, no provider.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile,readdir,access} from 'node:fs/promises';
import {join,dirname,resolve,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkMovie,resolveMovie,chaptersNeedingTakes,excerptSources,movieViewerApi,shotTimes,describeAnchor,MOVIE_FORMAT} from '../src/movie.mjs';
import {SCHEMA_KEYWORDS,schemaKeywords,MOVIE_SCHEMA} from '../src/schema.mjs';
import {frameAt} from '../src/timeline.mjs';
import {chapterOf,narrationOf,takeOffset,chapterTakeLines} from '../src/chapters.mjs';
import {validateEpisode,episodeFilm} from '../src/episode.mjs';
import {outputShotUnits} from '../src/shot-cache.mjs';
import {evenAlignment} from './project-fixture.mjs';

const fixtures=join(dirname(fileURLToPath(import.meta.url)),'..','fixtures');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const exists=file=>access(file).then(()=>true,()=>false);
const isAnchor=v=>v!==null&&typeof v==='object';
// A fixture's export manifest and excerpt texts, read through its root as the
// Python side reads them; absent files are left out.
async function projectOf(doc,dir){
  const base=resolve(dir,doc.root??'.');
  const file=resolve(base,doc.model?.manifest??'');
  const manifest=await exists(file)?await json(file).catch(()=>null):null;
  return {manifest,sources:await excerptSources(doc,base)};
}
// Takes of a fixture document, by chapter; a chapter whose anchors need a take
// the fixtures lack fails naming the file to add.
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
const documentOf=name=>json(join(fixtures,'documents',`${name}.json`));
const refusal=fn=>{try{fn();}catch(error){return error.message;}assert.fail('was not refused');};
// Asserts a refusal names every word.
const refusedNaming=(fn,words)=>{
  const message=refusal(fn);
  for(const word of words)assert.ok(message.includes(word),`refusal "${message}" does not name "${word}"`);
  return message;
};
const onGrid=(t,fps)=>Math.abs(t*fps-Math.round(t*fps))<1e-6;

test('the schema uses only keywords the validator implements',()=>{
  for(const keyword of schemaKeywords(MOVIE_SCHEMA))
    assert.ok(SCHEMA_KEYWORDS.has(keyword),`schema keyword ${keyword} is not implemented by src/schema.mjs`);
  assert.equal(MOVIE_SCHEMA.$schema,'https://json-schema.org/draft/2020-12/schema');
});

test('every registered document validates, passes its checks and resolves to its pin, twice identically, on the frame grid',async()=>{
  const {documents}=await json(join(fixtures,'manifest.json'));
  assert.ok(documents.includes('minimal')&&documents.includes('tour'));
  for(const name of documents){
    const doc=await documentOf(name),{manifest,sources}=await projectOf(doc,join(fixtures,'documents'));
    assert.equal(doc.format,MOVIE_FORMAT,name);
    assert.ok(manifest,`${name}: its export manifest is read through its root`);
    assert.deepEqual(Object.keys(sources).sort(),Object.keys(doc.sourceCode).sort(),`${name}: every excerpt is read through its root`);
    checkMovie(doc,{manifest,sources});
    const takes=await fixtureTakes(name,doc);
    const pinned=join(fixtures,'resolved',`${name}.json`);
    assert.ok(await exists(pinned),`fixture ${name} has no pinned resolution fixtures/resolved/${name}.json`);
    const once=resolveMovie(structuredClone(doc),takes),twice=resolveMovie(structuredClone(doc),takes);
    assert.equal(JSON.stringify(once),JSON.stringify(twice),`${name} resolves twice identically`);
    assert.deepEqual(once,await json(pinned),`${name} resolution differs from fixtures/resolved/${name}.json`);
    const fps=doc.output.fps,shots=once.chapters.flatMap(c=>c.shots);
    let clock=0;
    for(const shot of shots){
      assert.equal(shot.start,clock,`${name} shot ${shot.id} starts where the one before ended`);
      assert.ok(onGrid(shot.start,fps)&&onGrid(shot.end,fps),`${name} shot ${shot.id} [${shot.start}, ${shot.end}] is off the ${fps} fps grid`);
      clock=shot.end;
    }
    assert.equal(once.output.durationSeconds,clock);
    // Every time written as an anchor lands on the grid (emphasis onsets and
    // reveal onsets stay unsnapped by design and are not anchors).
    const original=new Map(doc.chapters.flatMap(c=>c.shots.map(s=>[s.id,s])));
    for(const shot of shots){
      const resolved=new Map(shotTimes(shot).map(t=>[t.field,t.obj[t.key]]));
      for(const {field,obj,key} of shotTimes(original.get(shot.id)))if(isAnchor(obj[key])&&field!=='until')
        assert.ok(onGrid(shot.start+resolved.get(field),fps),`${name} shot ${shot.id} ${field} is off the grid`);
    }
    // The document itself is untouched by resolving.
    assert.deepEqual(doc,await documentOf(name));
  }
});

test('every invalid fixture is refused by the static checks, naming every word it must',async()=>{
  const dir=join(fixtures,'invalid');
  const files=(await readdir(dir)).filter(n=>n.endsWith('.json')).sort();
  assert.ok(files.length>=60,`${files.length} invalid fixtures`);
  for(const file of files){
    const fixture=await json(join(dir,file));
    assert.equal(fixture.name,basename(file,'.json'),`${file} is named after its file`);
    assert.ok(fixture.document&&Array.isArray(fixture.must_mention)&&fixture.must_mention.length,`${file} shape`);
    const {manifest,sources}=await projectOf(fixture.document,dir);
    let message=null;
    try{checkMovie(fixture.document,{manifest,sources});}catch(error){message=error.message;}
    assert.ok(message!==null,`${file} was not refused`);
    for(const word of fixture.must_mention)
      assert.ok(message.includes(word),`${file}: refused for another reason: "${message}" does not name "${word}"`);
  }
});

test('a 0.1 document is refused naming the format this build reads',async()=>{
  const doc=await documentOf('minimal');doc.format='machinome-movie/0.1';
  refusedNaming(()=>checkMovie(doc),['machinome-movie/0.1','machinome-movie/0.2']);
  refusedNaming(()=>resolveMovie(doc,{}),['machinome-movie/0.2']);
});

// Resolution refusals, on documents mutated from the fixtures.
const tour=async()=>{const doc=await documentOf('tour');return {doc,takes:await fixtureTakes('tour',doc)};};
const minimal=async()=>{const doc=await documentOf('minimal');return {doc,takes:await fixtureTakes('minimal',doc)};};
const shotOf=(doc,id)=>doc.chapters.flatMap(c=>c.shots).find(s=>s.id===id);

test('a chapter that needs a take and has none is refused naming the chapter and the speech command',async()=>{
  const {doc,takes}=await tour();
  assert.deepEqual(chaptersNeedingTakes(doc),['opening','balance','tip']);
  delete takes.balance;
  refusedNaming(()=>resolveMovie(doc,takes),['Chapter balance','speech']);
  const m=await minimal();
  refusedNaming(()=>resolveMovie(m.doc,{}),['Chapter only','speech']);
  // A chapter without spoken anchors needs no take.
  m.doc.chapters[0].shots[0].until=2.5;
  assert.deepEqual(chaptersNeedingTakes(m.doc),[]);
  assert.equal(resolveMovie(m.doc,{}).output.durationSeconds,2.5);
});

test('a phrase absent from or repeated in the take is refused naming the chapter, the shot, the field and the phrase',async()=>{
  const {doc,takes}=await tour();
  const narration=doc.chapters[1].narration;
  takes.balance={alignment:evenAlignment(narration.replace('In the source','In the code'),.06)};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter balance','shot holds','until',"'In the source'",'absent']);
  takes.balance={alignment:evenAlignment(narration.replace('In the source','In the source, In the source'),.06)};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter balance','shot holds','until',"'In the source'",'ambiguous']);
});

test('an until at or before its start is refused naming the shot and the anchor',async()=>{
  const {doc,takes}=await minimal();
  doc.chapters[0].shots[0].until={spokenEnd:'seesaw',plus:-5};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter only','shot whole','until','at or before its start','spokenEnd "seesaw" plus -5']);
});

// The end of the narration (wart 2 of Cut and Advance): its own anchor form.
test('a narrationEnd anchor resolves to the end of the take\'s last letter or digit plus its plus, on the grid',async()=>{
  const {doc,takes}=await tour(),fps=doc.output.fps;
  const question=shotOf(doc,'question');
  assert.deepEqual(question.until,{narrationEnd:true,plus:0.8});
  const film=resolveMovie(structuredClone(doc),takes),opening=film.chapters[0];
  // "…How does the weight tip it?": the last letter is the t of "it", before the "?".
  const {characters,character_end_times_seconds:ends}=takes.opening.alignment;
  const last=characters.findLastIndex(c=>/[\p{L}\p{N}]/u.test(c));
  assert.equal(characters[last],'t');assert.equal(characters.at(-1),'?');
  const expected=Math.round((opening.start+opening.speechOffset+ends[last]+0.8)*fps)/fps;
  assert.equal(shotOf(film,'question').end,expected);
  assert.ok(onGrid(expected,fps));
  // The same instant as the end of the last word, which the document wrote before.
  const spelled=structuredClone(doc);
  for(const {obj,key} of shotTimes(shotOf(spelled,'question')))if(obj[key]?.narrationEnd)
    obj[key]={spokenEnd:'it',...(obj[key].plus!==undefined?{plus:obj[key].plus}:{})};
  assert.deepEqual(resolveMovie(spelled,takes),film);
  // Not the last character's end, which the "?" would push one or two frames later.
  assert.notEqual(Math.round((opening.start+opening.speechOffset+ends.at(-1)+0.8)*fps)/fps,expected);
});

test('a narrationEnd anchor needs its chapter\'s take, and a take with no letter or digit is refused naming it',async()=>{
  const {doc,takes}=await minimal();
  assert.deepEqual(doc.chapters[0].shots[0].until,{narrationEnd:true,plus:0.5});
  assert.deepEqual(chaptersNeedingTakes(doc),['only']);
  refusedNaming(()=>resolveMovie(doc,{}),['Chapter only','speech']);
  takes.only={alignment:evenAlignment('...',.06)};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter only','shot whole','until','narrationEnd','letter or digit']);
});

test('check\'s line for each chapter gives its take, its length and its tail, or says it has no take',async()=>{
  const {doc,takes}=await tour(),film=resolveMovie(doc,takes);
  const records=await Promise.all(film.chapters.map(c=>json(join(fixtures,'takes','tour',`${c.id}.json`))));
  assert.deepEqual(chapterTakeLines(film,records),[
    '  opening: take 3.94 s, chapter 4.77 s, tail 0.63 s',
    '  balance: take 6.04 s, chapter 6.67 s, tail 0.43 s',
    '  tip: take 6.22 s, chapter 7.47 s, tail 1.05 s']);
  const m=await minimal();m.doc.chapters[0].shots[0].until=2.5;
  assert.deepEqual(chapterTakeLines(resolveMovie(m.doc,{}),[null]),['  only: no cached take, chapter 2.50 s']);
});

test('a narrationEnd anchor is named in refusals, and one carrying another field is refused by the schema naming it',async()=>{
  assert.equal(describeAnchor({narrationEnd:true}),'narrationEnd');
  assert.equal(describeAnchor({narrationEnd:true,plus:0.8}),'narrationEnd plus 0.8');
  const {doc,takes}=await minimal();
  doc.chapters[0].shots[0].until={narrationEnd:true,plus:-5};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter only','shot whole','until','at or before its start','narrationEnd plus -5']);
  const t=await tour();
  shotOf(t.doc,'question').until={narrationEnd:true,phrase:'it'};
  refusedNaming(()=>checkMovie(t.doc),['shot question','until','phrase','narrationEnd anchor']);
  shotOf(t.doc,'question').until={narrationEnd:'it'};
  refusedNaming(()=>checkMovie(t.doc),['shot question','until.narrationEnd','narrationEnd anchor']);
});

test('an anchor outside its shot is refused naming the field and the anchor',async()=>{
  const {doc,takes}=await tour();
  // "balances" is spoken in the chapter's first shot, before the question starts.
  shotOf(doc,'question').cues[0].at={spoken:'balances'};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter opening','shot question','cues[0].at','spoken "balances"','outside the shot']);
});

test('a move whose until is at or before its at is refused naming the action',async()=>{
  const {doc,takes}=await tour();
  // The move to near now starts where it ends, at "How".
  shotOf(doc,'hook').cues[0].at={spoken:'How'};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter opening','shot hook','cues[0].actions[0].until','at or before']);
});

test('two highlights of one view overlapping in time are refused naming both',async()=>{
  const {doc,takes}=await tour();
  shotOf(doc,'source').cues[1].until={spoken:'The weight'};
  refusedNaming(()=>resolveMovie(doc,takes),['chapter balance','shot source','cues[2].actions[0]','highlight','mill','overlaps cues[1].actions[0]']);
});

// The three rules of the YAML formats a document does not follow (design D2.3,
// findings): pinned here as behaviour.
test('an emphasis hold running past its shot ends with the shot',async()=>{
  const {doc,takes}=await tour();
  const hold=shotOf(doc,'source').cues[3].actions[0];
  assert.equal(hold.action,'emphasize');
  for(const value of [.6,5]){
    hold.hold=value;
    const shot=shotOf(resolveMovie(structuredClone(doc),takes),'source');
    // The phrase's end plus the hold is past the cut; until is the shot's own end.
    assert.equal(shot.cues[3].actions[0].until,shot.until,`hold ${value}`);
    assert.equal(shot.until,shot.end-shot.start);
  }
});

test('a join longer than the shot it leaves is accepted, and the outgoing shot continues through it',async()=>{
  const {doc,takes}=await tour(),film=resolveMovie(doc,takes);
  const still=shotOf(film,'still'),invitation=shotOf(film,'invitation');
  assert.ok(invitation.transition.duration>still.end-still.start,'the fixture joins a 0.5 s shot by a 0.6 s dissolve');
  const late=frameAt(film,invitation.start+.55);
  assert.equal(late.transition.field,'transition');assert.equal(late.transition.outgoingShotId,'still');
  assert.equal(late.transition.outgoing.shotId,'still');
});

test('an incoming join overlapping a fade-out is accepted; the join is drawn until it ends, then the fade-out',async()=>{
  const {doc,takes}=await tour(),film=resolveMovie(doc,takes);
  const shot=shotOf(film,'invitation'),duration=shot.end-shot.start;
  assert.ok(shot.transition.duration+shot.fadeOut.duration>duration,'the join and the fade-out overlap');
  const overlap=shot.end-shot.fadeOut.duration+.05;
  assert.ok(overlap<shot.start+shot.transition.duration);
  assert.equal(frameAt(film,overlap).transition.field,'transition');
  assert.equal(frameAt(film,shot.start+shot.transition.duration+.05).transition.field,'fadeOut');
  assert.equal(frameAt(film,shot.end-1/film.output.fps).transition.plate,1,'the last frame is the colour');
});

test('movieViewerApi names every reason a movie needs Viewer API 28',async()=>{
  const {doc,takes}=await tour();
  assert.deepEqual(movieViewerApi(resolveMovie(doc,takes)),{api:28,reasons:[
    'highlight (shot source)','camera up/field of view (shot push)','marks (shot push)','marks (shot rise)','highlight (shot rise)',
    'camera up/field of view (shot rhythm)','highlight (shot invitation)']});
  const m=await minimal();
  assert.deepEqual(movieViewerApi(resolveMovie(m.doc,m.takes)),{api:21,reasons:[]});
  // A move to a camera with the mounted one's lens and up needs nothing.
  m.doc.chapters[0].shots[0].cues=[{at:0,actions:[{element:'view',action:'move',camera:'near',until:.5}]}];
  assert.deepEqual(movieViewerApi(resolveMovie(m.doc,m.takes)),{api:21,reasons:[]});
  m.doc.chapters[0].shots[0].cues[0].actions[0].camera='side';
  assert.deepEqual(movieViewerApi(resolveMovie(m.doc,m.takes)),{api:28,reasons:['camera up/field of view (shot whole)']});
});

test('the refusal the stage shows a movie on an older viewer calls it a movie',async()=>{
  const {stageConfig}=await import('../src/render.mjs');
  const {doc,takes}=await tour(),resolved=resolveMovie(doc,takes);
  const film={...resolved,source:'movie',viewerApi:movieViewerApi(resolved)};
  const {refusal}=stageConfig(film).viewer;
  assert.match(refusal,/^This movie needs Viewer API 28 for highlight \(shot source\), .*; the selected viewer declares API \{declared\}\./);
  assert.doesNotMatch(refusal,/episode/);
});

test('a shot reads its chapter\'s take at the chapter\'s offset from the shot',async()=>{
  const {doc,takes}=await tour(),film=resolveMovie(doc,takes);
  const source=shotOf(film,'source'),balance=film.chapters.find(c=>c.id==='balance');
  assert.equal(chapterOf(film,'source'),balance);
  assert.equal(narrationOf(film,'source'),balance.narration);
  assert.equal(takeOffset(film,source),balance.start+balance.speechOffset-source.start);
  // "stand" of "the stand holds the beam": its first letter's start in the take, from the shot.
  const at=balance.narration.indexOf('stand holds');
  const onset=takeOffset(film,source)+takes.balance.alignment.character_start_times_seconds[at];
  assert.ok(Math.abs(source.cues[3].actions[0].words[0].at-onset)<1e-9);
  // The first shot of a chapter reads it at exactly the chapter's offset.
  assert.ok(Object.is(takeOffset(film,shotOf(film,'holds')),balance.speechOffset));
});

test('an anchor on a cut made of literal durations lands exactly on it',async()=>{
  // 0.1 + 0.2 is 0.30000000000000004; "A" is spoken at 0.3 + 0 s, snapped to 0.3.
  const {doc,takes}=await minimal(),chapter=doc.chapters[0],whole=chapter.shots[0];
  chapter.speechOffset=.3;
  const literal=(id,until)=>({...structuredClone(whole),id,until,cues:[]});
  chapter.shots=[literal('one',.1),literal('two',.2),whole];
  whole.cues=[{at:{spoken:'A'},actions:[{element:'view',action:'move',camera:'near',until:{spokenEnd:'seesaw'}}]}];
  const shot=shotOf(resolveMovie(doc,takes),'whole');
  assert.equal(shot.start,.1+.2);
  assert.ok(Object.is(shot.cues[0].at,0));
});

test('a YAML episode is one chapter per shot, its offsets bit for bit, its duration a whole number of frames',()=>{
  // 31/30 × 30 is 31.000000000000004 in floating point.
  const d=31/30,shot=(id,start,end,more)=>({id,start,end,narration:`${id}.`,direction:'',simulation:{from:0,to:1},
    camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...more});
  const e={format:'machinome-video-draft/0.4',output:{width:320,height:180,fps:30,durationSeconds:d},
    model:{expectedDurationSeconds:20,timeMode:'normalized-loop'},cameras:{a:{position:[0,-1,0],target:[0,0,0],up:[0,0,1],fov:37}},
    layers:{},evidence:{},shots:[shot('a',0,.5,{speechOffset:.3}),shot('b',.5,d)]};
  validateEpisode(e,{animation:{loop:20}});
  const film=episodeFilm(e);
  assert.deepEqual(film.chapters.map(c=>[c.id,c.narration,c.speechOffset,c.start,c.end,c.shots.map(s=>s.id)]),
    [['a','a.',.3,0,.5,['a']],['b','b.',.2,.5,d,['b']]]);
  assert.ok(Object.is(takeOffset(film,film.chapters[1].shots[0]),.2));
  assert.equal(narrationOf(film,'b'),'b.');
  assert.equal(outputShotUnits(film,30).count,31);
  e.output.durationSeconds=e.shots[1].end=1.05;
  assert.throws(()=>validateEpisode(e,{animation:{loop:20}}),/Video duration must be a whole number of frames/);
});
