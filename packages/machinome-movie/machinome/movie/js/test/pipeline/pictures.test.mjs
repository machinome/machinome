import {slowTest as test,artefact} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,mkdir,symlink,copyFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {base02} from '../frame-fixtures.mjs';
import {validateEpisode,requiredViewerApi,episodeFilm} from '../../src/episode.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {STAGE_AREAS,pictureRect,viewAt,clipFrameAt,loadPictures,validatePictureSizing,
  pictureAt,extractClips,pictureReports,inspectClipProbe,clipCadence,clipCadenceForCue} from '../../src/pictures.mjs';

const manifest={animation:{loop:296}};
// A validated YAML episode's frame through the loader's conversion; a YAML
// shot is one chapter, so its picture cue #i is the element `<shot>.picture-<i>`.
const frameOf=(e,t)=>frameAt(episodeFilm(e),t);
const pictureIn=(frame,i=0)=>frame.elements[`${frame.chapterId}.picture-${i}`];
const episode=()=>{const e=base02();e.format='machinome-video-draft/0.4';e.output.width=1920;e.output.height=1080;
  e.stills={image:{file:'image.png',credit:'Own render',rights:'Own work',upscale:2}};
  e.clips={movie:{file:'movie.mp4',credit:null,rights:null,upscale:2}};
  e.shots[0].pictures=[{from:0,to:1.8,still:'image',area:'frame',fit:'contain'}];
  return e;};
async function mediaFixture(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-picture-matrix-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  execFileSync('git',['init','-q'],{cwd:dir});
  // The encoded stills and clips are an input product, memoized; the test
  // works on its own copies.
  const media=await artefact('pictures-media-matrix',{},async out=>{
    const still=(name,codec)=>execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=red:s=120x80',
      '-frames:v','1','-c:v',codec,join(out,name)]);
    still('image.png','png');still('photo.jpg','mjpeg');still('web.webp','webp');
    execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=blue:s=120x80:r=3',
      '-t','2','-c:v','libx264','-pix_fmt','yuv420p',join(out,'movie.mp4')]);
    execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=green:s=120x80:r=3',
      '-t','2','-c:v','libvpx-vp9',join(out,'movie.webm')]);
  });
  for(const name of ['image.png','photo.jpg','web.webp','movie.mp4','movie.webm'])await copyFile(join(media,name),join(dir,name));
  await writeFile(join(dir,'drawing.svg'),'<svg width="420" height="240" viewBox="0 0 420 240"><path d="M0 0L10 10"/></svg>');
  await writeFile(join(dir,'missing-viewbox.svg'),'<svg width="420" height="240"><path d="M0 0L10 10"/></svg>');
  await copyFile(join(dir,'photo.jpg'),join(dir,'wrong.png'));
  execFileSync('git',['add','.'],{cwd:dir});
  execFileSync('git',['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','media'],{cwd:dir});
  const e=episode();e.paths={repository:dir,production:join(dir,'production.yaml'),build:join(dir,'_build')};
  e.stills.image.upscale=20;e.clips.movie.upscale=20;
  return {dir,e};
}

test('picture geometry fits, covers, holds and keeps zoom fixed point',()=>{
  assert.deepEqual(STAGE_AREAS.plain,[.05,.16,.90,.63]);
  assert.deepEqual(STAGE_AREAS.code,[.56,.20,.42,.65]);
  assert.deepEqual(pictureRect({width:1000,height:500},[0,0,1920,1080],'contain',{center:[.5,.5],zoom:1}),
    [0,.05555555555555558,1,.8888888888888888]);
  assert.deepEqual(pictureRect({width:1000,height:500},[0,0,1920,1080],'cover',{center:[.5,.5],zoom:1}),
    [-.0625,0,1.125,1]);
  const keys=[{at:1,center:[.5,.5],zoom:1},{at:8,center:[.5,.27],zoom:1.9,ease:'linear'}];
  assert.deepEqual(viewAt(keys,0),{center:[.5,.5],zoom:1});
  assert.deepEqual(viewAt(keys,8),{center:[.5,.27],zoom:1.9});
  assert.deepEqual(viewAt(keys,9),{center:[.5,.27],zoom:1.9});
  const mid=viewAt(keys,4.5),fixed=(.27*1.9-.5)/(1.9-1);
  assert.ok(Math.abs((fixed-mid.center[1])*mid.zoom-(fixed-.5))<1e-12);
  const pan=viewAt([{at:0,center:[.2,.3],zoom:2},{at:2,center:[.8,.7],zoom:2,ease:'linear'}],1);
  assert.deepEqual(pan,{center:[.5,.5],zoom:2});
  for(const [name,fit,expected] of [
    ['plain','contain',[.10625,0,.7875,1]],
    ['plain','cover',[0,-.134920634920635,1,1.26984126984127]],
    ['code','contain',[0,.21282051282051284,1,.5743589743589743]],
    ['code','cover',[-.3705357142857143,0,1.7410714285714286,1]]]){
    const area=STAGE_AREAS[name].map((v,i)=>v*(i%2?1080:1920));
    const actual=pictureRect({width:1000,height:500},area,fit,{center:[.5,.5],zoom:1});
    assert.ok(actual.every((v,i)=>Math.abs(v-expected[i])<1e-12),`${name} ${fit}: ${actual}`);
  }
});

test('clips choose the frame on screen from irregular presentation timestamps',()=>{
  assert.deepEqual([0,.2,1/3,.5,.999,1].map(t=>clipFrameAt([0,1/3,2/3,1],t)),[0,0,1,1,2,3]);
  assert.deepEqual([0,.19,.2,.65,.66].map(t=>clipFrameAt([0,.2,.65],t)),[0,0,1,2,2]);
});

test('picture cue structure is closed and format-gated without changing old frames',()=>{
  const bad=(edit,pattern)=>{const e=episode();edit(e);assert.throws(()=>validateEpisode(e,manifest),pattern);};
  bad(e=>{e.format='machinome-video-draft/0.3';},/Pictures need format machinome-video-draft\/0.4: shot first/);
  bad(e=>{e.format='machinome-video-draft/0.2';},/Pictures need format machinome-video-draft\/0.4: shot first/);
  bad(e=>{e.shots[0].pictures[0].clip='movie';},/exactly one|still or clip/i);
  bad(e=>{delete e.shots[0].pictures[0].still;},/exactly one|still or clip/i);
  bad(e=>{e.shots[0].pictures[0].fit='stretch';},/fit/i);
  bad(e=>{e.shots[0].pictures[0].area='corner';},/area/i);
  bad(e=>{e.shots[0].pictures[0].caption='No';},/Unknown picture field: caption/);
  bad(e=>{e.shots[0].pictures[0].fadeIn={duration:.2};},/Unknown picture field: fadeIn/);
  bad(e=>{e.shots[0].pictures[0].fadeOut={duration:.2};},/Unknown picture field: fadeOut/);
  bad(e=>{e.shots[0].pictures[0].still='missing';},/Unknown still: missing/);
  bad(e=>{delete e.shots[0].pictures[0].still;e.shots[0].pictures[0].clip='missing';},/Unknown clip: missing/);
  bad(e=>{e.shots[0].pictures[0].from=-1;},/picture times/i);
  bad(e=>{e.shots[0].pictures[0].to=3;},/picture times/i);
  bad(e=>{e.shots[0].pictures.push({from:1,to:2,still:'image'});},/overlap/i);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1,ease:'in'}];},/Nothing to ease before the first view key/);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1,centerX:.5}];},/Unknown view key field: centerX/);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[1.1,.5],zoom:1}];},/view center/i);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:.9}];},/view zoom/i);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1},{at:0,center:[.5,.5],zoom:2}];},/View keys must increase/i);
  bad(e=>{e.shots[0].pictures[0].view=[{at:1.81,center:[.5,.5],zoom:1}];},/view keys.*inside/i);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1},{at:1,center:[.5,.5],zoom:2,ease:'nope'}];},/Unknown easing/);
  bad(e=>{e.shots[0].pictures[0].enter={kind:'draw',duration:.2};},/fade/i);
  bad(e=>{e.shots[0].pictures[0].leave={kind:'fade',duration:.01};},/two frames|duration/i);
  bad(e=>{e.shots[0].pictures[0].enter={kind:'fade',duration:1};e.shots[0].pictures[0].leave={kind:'fade',duration:1};},/overlap/i);
  bad(e=>{e.shots[0].pictures[0].enter={kind:'fade',duration:.2,curve:'in'};},/Unknown entrance field: curve/);
  bad(e=>{e.shots[0].pictures[0].leave={kind:'fade',duration:.2,curve:'in'};},/Unknown exit field: curve/);
  bad(e=>{e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1}];e.shots[0].pictures[0].clip='movie';delete e.shots[0].pictures[0].still;},/view belongs to a still/i);
  bad(e=>{e.shots[0].pictures[0].inPoint=1;},/inPoint belongs to a clip/i);
  bad(e=>{e.shots[0].pictures[0].clip='movie';delete e.shots[0].pictures[0].still;e.shots[0].pictures[0].inPoint=-1;},/inPoint/i);
  bad(e=>{e.style={safeInsetFraction:.08,accent:'#bf531f'};e.shots[0].annotations=[{from:0,to:1,kind:'arrow',point:[0,0,0],place:[.1,.1]}];},/Annotation #0 overlaps picture #0/);
  bad(e=>{e.style={safeInsetFraction:.08,accent:'#bf531f'};e.shots[0].hiddenLayers=[];e.shots[0].highlight=[{from:0,to:1,parts:['frame']}];},/Highlight #0 overlaps picture #0/);
  const e=episode();validateEpisode(e,manifest);
  e.pictureMedia={stills:{image:{format:'png',width:1920,height:1080,upscale:2}},clips:{}};
  assert.equal(pictureIn(frameOf(e,1.9)).shown,false);
  assert.equal(pictureIn(frameOf(e,.5)).shown,true);assert.equal(pictureIn(frameOf(e,.5)).media,'still');
  const old=base02();old.stills=e.stills;old.clips=e.clips;
  assert.ok(Object.values(frameOf(old,.5).elements).every(state=>state.kind!=='picture'),'an older episode has no picture element');
  validateEpisode(old,manifest);
  assert.deepEqual(requiredViewerApi(e),requiredViewerApi(old));
});

test('older production media maps are ignored without probing or changing old frames',async()=>{
  for(const format of ['machinome-video-draft/0.2','machinome-video-draft/0.3']){
    const e=base02();e.format=format;e.stills={unused:{file:'no-file.gif'}};e.clips={unused:{file:'no-file.avi'}};
    e.paths={repository:'/not-a-repository',production:'/not-a-production'};
    const before=frameOf(e,.5);validateEpisode(e,manifest);await loadPictures(e);
    assert.deepEqual(e.pictureMedia,{stills:{},clips:{}});
    assert.deepEqual(frameOf(e,.5),before);
  }
});

test('loading project media probes real files, hashes and committed status; sizing refuses unallowed enlargement',async t=>{
  const dir=await mkdtemp(join(tmpdir(),'videomaker-pictures-test-'));
  t.onTestFinished(async()=>{const {rm}=await import('node:fs/promises');await rm(dir,{recursive:true,force:true});});
  execFileSync('git',['init','-q'],{cwd:dir});
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=red:s=100x80','-frames:v','1',join(dir,'image.png')]);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=blue:s=100x80:r=3','-t','2','-c:v','libx264','-pix_fmt','yuv420p',join(dir,'movie.mp4')]);
  await writeFile(join(dir,'drawing.svg'),'<svg viewBox="0 0 420 240"><path d="M0 0L10 10"/></svg>');
  execFileSync('git',['add','.'],{cwd:dir});
  execFileSync('git',['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','media'],{cwd:dir});
  const e=episode();e.paths={repository:dir,production:join(dir,'production.yaml'),build:join(dir,'_build')};
  e.stills.image.upscale=20;
  e.stills.drawing={file:'drawing.svg',credit:'Own',rights:'Own'};
  await loadPictures(e);
  assert.deepEqual([e.pictureMedia.stills.image.width,e.pictureMedia.stills.image.height],[100,80]);
  assert.equal(e.pictureMedia.stills.image.committed,true);
  assert.equal(e.pictureMedia.stills.drawing.format,'svg');
  assert.equal(e.pictureMedia.clips.movie.timestamps[0],0);
  assert.ok(e.pictureMedia.clips.movie.timestamps.length>=5);
  const enlarged=episode();enlarged.pictureMedia=structuredClone(e.pictureMedia);
  enlarged.stills.image.upscale=1;
  enlarged.pictureMedia.stills.image.upscale=1;
  assert.throws(()=>validatePictureSizing(enlarged),/Still image would be enlarged/);
  enlarged.stills.image.upscale=20;enlarged.pictureMedia.stills.image.upscale=20;validatePictureSizing(enlarged);
  e.shots[0].pictures=[{from:0,to:1.8,clip:'movie',area:'stage'}];
  e.clips.movie.upscale=20;
  await loadPictures(e);
  await extractClips(e);
  assert.ok(e.pictureMedia.clips.movie.extraction.key);
  const index=JSON.parse(await readFile(join(e.pictureMedia.clips.movie.extraction.dir,'index.json'),'utf8'));
  assert.ok(index.frames.length>=5);
});

test('media loader accepts three raster formats and an internal SVG paint reference',async t=>{
  const {dir,e}=await mediaFixture(t);
  await writeFile(join(dir,'paint.svg'),'<svg viewBox="0 0 12 8"><defs><linearGradient id="paint"/></defs><rect width="12" height="8" fill="url( #paint)"/><rect width="2" height="2" fill=\'url("#paint")\'/></svg>');
  e.stills.photo={file:'photo.jpg',credit:null,rights:null,upscale:20};
  e.stills.web={file:'web.webp',credit:'Own',rights:'Own',upscale:20};
  e.stills.paint={file:'paint.svg',credit:'Own',rights:'Own'};
  e.clips.webm={file:'movie.webm',credit:'Own',rights:'Own',upscale:20};
  const result=await loadPictures(e);
  assert.deepEqual([result.stills.image.format,result.stills.photo.format,result.stills.web.format],['png','jpg','webp']);
  assert.deepEqual([result.stills.paint.width,result.stills.paint.height],[12,8]);
  assert.equal(result.stills.paint.committed,false);
  assert.equal(result.clips.webm.codec,'vp9');
});

test('media loader refuses escape, wrong bytes, animated and scripted stills, and incomplete provenance',async t=>{
  const {dir,e}=await mediaFixture(t);
  const another=await mkdtemp(join(tmpdir(),'videomaker-picture-outside-'));
  t.onTestFinished(()=>rm(another,{recursive:true,force:true}));
  await copyFile(join(dir,'image.png'),join(another,'outside.png'));
  await symlink(join(another,'outside.png'),join(dir,'link.png'));
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','testsrc2=s=120x80:r=2',
    '-frames:v','2','-plays','0','-f','apng',join(dir,'animated.png')]);
  const invalids=[
    [{file:join(another,'outside.png')},/outside the project/],
    [{file:'link.png'},/outside the project/],
    [{file:'wrong.png'},/not a single PNG/],
    [{file:'animated.png'},/not a single PNG/],
    [{file:'image.gif'},/Unsupported still extension/],
    [{file:'missing-viewbox.svg'},/viewBox="0 0 420 240"/],
    [{file:'drawing.svg',upscale:1.5},/upscale is not allowed on SVG/],
    [{file:'image.png',upscale:.9},/Invalid upscale/],
    [{file:'image.png',credit:undefined},/credit/],
    [{file:'image.png',rights:undefined},/rights/],
    [{file:'image.png',upsacle:2},/Unknown still field: upsacle/],
  ];
  for(const [change,pattern] of invalids){const bad=structuredClone(e);Object.assign(bad.stills.image,change);
    if(change.file?.endsWith('.svg')&&change.upscale===undefined)delete bad.stills.image.upscale;
    if(change.credit===undefined&&Object.hasOwn(change,'credit'))delete bad.stills.image.credit;
    if(change.rights===undefined&&Object.hasOwn(change,'rights'))delete bad.stills.image.rights;
    await assert.rejects(loadPictures(bad),pattern);}
  for(const [name,svg,pattern] of [
    ['script','<svg viewBox="0 0 1 1"><script>bad()</script></svg>',/script/],
    ['animate','<svg viewBox="0 0 1 1"><animate attributeName="x"/></svg>',/animation/],
    ['external','<svg viewBox="0 0 1 1"><image href="https://x.invalid/a.png"/></svg>',/external href/],
    ['external-bare','<svg viewBox="0 0 1 1"><image href=https:\/\/x.invalid\/a.png\/></svg>',/external href/],
    ['external-url','<svg viewBox="0 0 1 1"><rect style="fill:url(https://x.invalid/a.png)"/></svg>',/external href/],
    ['foreign','<svg viewBox="0 0 1 1"><foreignObject/></svg>',/foreignObject/],
    ['css-animation','<svg viewBox="0 0 1 1"><style>.a{animation-name:move}</style></svg>',/animation/],
    ['css-transition','<svg viewBox="0 0 1 1"><style>.a{transition-property:opacity}</style></svg>',/animation/],
  ]){await writeFile(join(dir,`${name}.svg`),svg);const bad=structuredClone(e);
    bad.stills.image={file:`${name}.svg`,credit:'Own',rights:'Own'};
    await assert.rejects(loadPictures(bad),pattern);}
  const clip=structuredClone(e);clip.clips.movie.unknown=1;
  await assert.rejects(loadPictures(clip),/Unknown clip field: unknown/);
  const changed=structuredClone(e);changed.stills.image={file:'drawing.svg',credit:'Own',rights:'Own'};
  await writeFile(join(dir,'drawing.svg'),(await readFile(join(dir,'drawing.svg'),'utf8'))+'\n');
  await loadPictures(changed);assert.equal(changed.pictureMedia.stills.image.committed,false);
});

test('museum enlargement is explicit, stage is smaller, and render width rechecks it',()=>{
  const e=episode();e.stills={museum:{file:'museum.jpg',credit:null,rights:null}};
  e.shots[0].pictures=[{from:0,to:1,still:'museum',area:'frame'}];
  e.pictureMedia={stills:{museum:{format:'jpg',width:1175,height:781,upscale:1}},clips:{}};
  assert.throws(()=>validatePictureSizing(e),/Still museum would be enlarged 1\.38×.*allowance is 1/);
  e.pictureMedia.stills.museum.upscale=1.4;
  validatePictureSizing(e);
  assert.ok(Math.abs(pictureReports(e)[0].peak-1.38)<.01);
  e.shots[0].pictures[0].area='stage';e.pictureMedia.stills.museum.upscale=1;
  validatePictureSizing(e);
  assert.ok(Math.abs(pictureReports(e)[0].peak-.87)<.01);
  e.pictureMedia.stills.museum.upscale=1.4;
  assert.throws(()=>validatePictureSizing(e,3840),/would be enlarged.*allowance is 1\.4/);
  e.shots[0].pictures[0].area='frame';
  e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1},{at:.8,center:[.5,.5],zoom:1.2}];
  assert.throws(()=>validatePictureSizing(e),/would be enlarged 1\.66×.*allowance is 1\.4/);
});

test('a moving view is checked between valid keys, not only at its endpoints',async t=>{
  const {e}=await mediaFixture(t);
  e.stills.image.upscale=30;
  e.shots[0].pictures[0].view=[
    {at:0,center:[.5,.5],zoom:1},
    {at:1.8,center:[.6,.5],zoom:2,ease:'linear'}];
  await assert.rejects(loadPictures(e),/Picture view leaves the picture.*shot first.*picture #0/);
});

test('a zoom that exposes a plate at its ending key is refused',async t=>{
  const {e}=await mediaFixture(t);e.stills.image.upscale=30;
  e.shots[0].pictures[0].area='frame';
  e.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1},
    {at:1,center:[.25,.75],zoom:2,ease:'linear'}];
  await assert.rejects(loadPictures(e),/Picture view leaves the picture.*shot first.*picture #0/);
});

test('clip probe normalizes first PTS, refuses undefined instants, interlace, pixels and rotation',()=>{
  const source={streams:[{codec_name:'h264',width:160,height:120,field_order:'progressive',sample_aspect_ratio:'1:1',avg_frame_rate:'2/1',time_base:'1/10000'}],
    frames:[0,5000,10000].map(t=>({best_effort_timestamp:50000+t,best_effort_timestamp_time:String(5+t/10000),
      pkt_duration:5000,interlaced_frame:0}))};
  const good=inspectClipProbe(source,'sample');
  assert.deepEqual(good.timestamps,[0,.5,1]);assert.equal(good.end,1.5);
  const bad=(edit,pattern)=>{const data=structuredClone(source);edit(data);assert.throws(()=>inspectClipProbe(data,'sample'),pattern);};
  bad(d=>{delete d.frames[1].best_effort_timestamp;},/no usable frame timestamps/);
  bad(d=>{d.frames[2].best_effort_timestamp=55000;},/no usable frame timestamps/);
  bad(d=>{d.streams[0].time_base='N/A';},/no usable frame timestamps/);
  bad(d=>{d.frames[1].interlaced_frame=1;},/interlaced/);
  bad(d=>{d.streams[0].sample_aspect_ratio='4:3';},/non-square pixels/);
  bad(d=>{d.streams[0].tags={rotate:'90'};},/rotation/);
});

test('real 30 fps PTS ticks give every frame of a four-second span once, including frame 134',async t=>{
  const {dir,e}=await mediaFixture(t);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=purple:s=160x120:r=30',
    '-t','5','-c:v','libx264','-pix_fmt','yuv420p',join(dir,'thirty.mp4')]);
  e.clips.movie.file='thirty.mp4';await loadPictures(e);
  const times=e.pictureMedia.clips.movie.timestamps,cadence=clipCadence(times,.5,4.5,30);
  assert.equal(times.length,150);
  assert.deepEqual([cadence.shown.length,cadence.shown[0],cadence.shown.at(-1),cadence.dropped,cadence.repeated],
    [120,15,134,0,0]);
});

test('sample-and-hold cadence counts dropped/repeated frames without including exclusive endpoint',()=>{
  const three=[0,1/3,2/3,1,4/3,5/3,2];
  assert.deepEqual(clipCadence(three,0,2,2),{shown:[0,1,3,4],dropped:2,repeated:0});
  assert.deepEqual(clipCadence([0,1,2],0,2,2),{shown:[0,0,1,1],dropped:0,repeated:2});
  assert.deepEqual(clipCadence(Array.from({length:31},(_,i)=>i/30),0,1,30).shown.at(-1),29);
  // A cue beginning at film .1 s in a 2 fps output is sampled first at .5 s,
  // not at its authored onset. The clip instant is consequently .4 s.
  assert.deepEqual(clipCadence([0,.2,.4,.6,.8],0,.8,2,.4),
    {shown:[2],dropped:3,repeated:0});
  const shot={start:10,end:12},cue={from:.1,to:.9,clip:'c'},e={output:{fps:2},shots:[shot]};
  assert.deepEqual(clipCadenceForCue(e,shot,cue,{timestamps:[0,.2,.4,.6,.8]}),
    {shown:[2],dropped:3,repeated:0});
});

test('a clip must cover the cue and outgoing transition continuation, even if it leaves',async t=>{
  const {e}=await mediaFixture(t);
  e.shots[0].pictures=[{from:0,to:2,clip:'movie',inPoint:0,area:'stage'}];
  await loadPictures(e); // no continuation and exact 2-second clip
  for(const kind of ['fade','dissolve'])for(const leaving of [false,true]){
    const bad=structuredClone(e);bad.shots[1].transition={kind,duration:1};
    if(leaving)bad.shots[0].pictures[0].leave={kind:'fade',duration:.5};
    await assert.rejects(loadPictures(bad),/Clip movie ends.*needed by picture #0 in shot first/);
  }
  const short=structuredClone(e);short.shots[0].pictures[0].inPoint=1;
  await assert.rejects(loadPictures(short),/Clip movie ends.*needed by picture #0 in shot first/);
});

test('fractional picture boundaries and outgoing continuation preserve a still or advance a clip',()=>{
  const e=episode();e.stills.image.upscale=20;
  e.style={background:'#faf7ef'};
  e.shots[0].pictures=[{from:.1,to:2,still:'image',area:'frame',
    view:[{at:.1,center:[.5,.5],zoom:1},{at:1.5,center:[.5,.5],zoom:2}]}];
  e.shots[1].transition={kind:'dissolve',duration:.5};
  e.pictureMedia={stills:{image:{format:'png',width:1920,height:1080,upscale:20}},clips:{}};
  validateEpisode(e,manifest);
  assert.equal(pictureIn(frameOf(e,.1)).media,'still');assert.equal(pictureIn(frameOf(e,.1)).shown,true);
  assert.equal(pictureIn(frameOf(e,2.1).transition.outgoing).view.zoom,2);
  e.shots[0].pictures[0].leave={kind:'fade',duration:.5};
  assert.equal(pictureIn(frameOf(e,2.1).transition.outgoing).opacity,0);
  e.shots[0].pictures=[{from:.1,to:2,clip:'movie',inPoint:0}];
  e.pictureMedia.clips.movie={format:'mp4',width:1920,height:1080,upscale:20,
    timestamps:Array.from({length:12},(_,i)=>i*.25)};
  validateEpisode(e,manifest);
  assert.equal(pictureIn(frameOf(e,2.1).transition.outgoing).frame,8);
  assert.equal(pictureIn(frameOf(e,1.999)).media,'clip');assert.equal(pictureIn(frameOf(e,1.999)).shown,true);
});

test('extraction uses only source frames whose presentation instants precede the exclusive cue end',async t=>{
  const {dir,e}=await mediaFixture(t);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=purple:s=120x80:r=3',
    '-t','3','-c:v','libx264','-pix_fmt','yuv420p',join(dir,'long.mp4')]);
  e.clips.movie.file='long.mp4';e.shots[0].pictures=[{from:0,to:1,clip:'movie',inPoint:1,area:'stage'}];
  await loadPictures(e);await extractClips(e);
  assert.deepEqual(e.pictureMedia.clips.movie.extraction.frames,[3,4,5]);
});
