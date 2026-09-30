// Layer 5 (serial; Chromium, the viewer double): YAML episodes, loaded as the
// command line loads them, posed on the stage in the shipped paper sets.
// Element keys are `<shot id>.<element>`: `view`, `code`, `overlay-<i>`,
// `picture-<i>` (a YAML shot is one chapter).
import {slowTest as test,artefact} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {writeFile,readFile,stat,copyFile,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {preview,render,browserSession} from '../support/stage.mjs';
import {yamlProject,PAWL_MANIFEST} from '../support/yaml-project.mjs';
import {pcmWav} from '../../src/speech.mjs';
import {frameAt,filmShots,shotActions} from '../../src/timeline.mjs';
import {decodePng,hexColor} from '../../src/pixels.mjs';
import {resolveWordTiming} from '../../src/words.mjs';
import {viewerDouble} from '../viewer-double.mjs';

const stateAt=(film,t,key)=>frameAt(film,t).elements[key];
// The element state drawn as absent.
const absent=state=>state.kind==='view'?state:{...state,shown:false,opacity:0};
// The mark id (cues[i].actions[j]) of a YAML shot's annotation #index.
const markId=(film,shotId,index)=>shotActions(filmShots(film).find(s=>s.shot.id===shotId).shot)
  .find(x=>x.action.annotation===index).id;

// A minimal viewer double exercises film composition/encoding only.
test('short mixed-layout film renders with a same-basename sidecar, not embedded subtitles',async t=>{
  const project=await yamlProject(t,{manifest:{root:{name:'test'},animation:{loop:2}},files:{'machine.py':'x = 1\n'}});
  const {dir}=project,viewer=join(dir,'viewer.js');
  await writeFile(viewer,`window.MachinomeViewer={async mount(selector,url,options){
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';document.querySelector(selector).append(canvas);
    let view=options.view;return {apiVersion:27,setTime(){},setVisible(){},navigation(){return {}},
      setView(v){if(!v.camera.every(Number.isFinite))throw new Error('invalid camera');view=v;},
      view(){return {camera:{toArray:()=>view.camera},target:{toArray:()=>view.target}}}};
  }};`);
  const mix=join(dir,'voice.wav');await writeFile(mix,pcmWav(Buffer.alloc(24000*2*2),24000));
  const shot={narration:'Separate subtitles.',direction:'Show source.',camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]};
  const e=await project.film({title:'Test',series:'',output:{width:640,height:360,fps:2,durationSeconds:2},
    model:{expectedDurationSeconds:2},style:{background:'#f5f1e8',foreground:'#222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
    sourceCode:{test:{file:'machine.py',lines:[1,1]}},
    cameras:{a:{position:[1,1,1],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    release:{descriptionTemplate:'description.md'},
    shots:[{...shot,id:'code',start:0,end:1,simulation:{from:0,to:1},code:{snippet:'test',typing:[{from:0,to:.5,throughLine:1}]}},
      {...shot,id:'whole',start:1,end:2,simulation:{from:1,to:2}}]});
  assert.deepEqual(filmShots(e).map(s=>s.shot.set),['paper-split','paper'],'a code shot is the split set, the other the plain one');
  const p=await preview(e,{viewer,width:640});assert.equal(p.pixelReplay,true);assert.equal(p.samples.length,7);
  const captions=[{text:'Separate subtitles.',start:.2,end:.8}];
  const output=await render(e,{viewer,audio:{mix,records:[],captions}});
  assert.equal(output,join(dir,'_build/rehearsal.mp4'));
  assert.match(await readFile(join(dir,'_build/rehearsal.srt'),'utf8'),/00:00:00,200 --> 00:00:00,800\nSeparate subtitles\./);
  const report=JSON.parse(await readFile(join(dir,'_build/rehearsal-manifest.json'),'utf8'));
  assert.deepEqual(report.probe.streams.map(s=>s.codec_type).sort(),['audio','video']);
  assert.equal(report.count,4);assert.equal(report.subtitles.burnedIn,false);
  assert.ok((await readFile(join(dir,'_build/thumbnail.png'))).length>0);
});

async function pixel(file,x,y){
  const bytes=execFileSync('ffmpeg',['-v','error','-i',file,'-f','rawvideo','-pix_fmt','rgb24','pipe:1']);
  const width=Number(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width','-of','csv=p=0',file],{encoding:'utf8'}).trim());
  const i=(Math.round(y)*width+Math.round(x))*3;return [bytes[i],bytes[i+1],bytes[i+2]];
}
// One shot, `pawls`, over the two-second pawl model; `extra` replaces episode fields.
function filmEpisode(shotExtra={},extra={}){
  return {format:'machinome-video-draft/0.3',title:'Test',series:'',output:{width:640,height:360,fps:2,durationSeconds:2},
    model:{expectedDurationSeconds:2},
    style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{pawl:[['Feed','Pawl']]},
    release:{descriptionTemplate:'description.md'},
    shots:[{id:'pawls',start:0,end:2,narration:'Look.',direction:'Look.',simulation:{from:0,to:2},camera:[{at:0,preset:'a'}],
      hiddenLayers:[],overlays:[],evidence:[],...shotExtra}],...extra};
}
async function filmFixture(t,options){
  const project=await yamlProject(t,options);
  const viewer=async(name,options)=>{const file=join(project.dir,name);await writeFile(file,viewerDouble(options));return file;};
  return {project,dir:project.dir,viewer};
}

test('text animation preview proves measured/even words, title fade and source emphasis on a moving model',async t=>{
  const {project,viewer}=await filmFixture(t,{files:{'machine.py':'"<&"; wheel\n'}}),speech='One Two Three wheel';
  const alignment={characters:Array.from(speech),character_start_times_seconds:Array.from(speech,(_,i)=>i*.05),
    character_end_times_seconds:Array.from(speech,(_,i)=>(i+1)*.05)};
  const source=filmEpisode({narration:speech,speechOffset:.2,
    overlays:[
      {from:0,to:1.8,text:'One Two Three',position:'top',reveal:{timing:'spoken'}},
      {from:0,to:1.8,text:'A B C',position:'lower-third',reveal:{timing:'even',duration:1.2}},
      {from:0,to:1.8,text:'Moving model',subtitle:'Still visible',position:'title',
        enter:{kind:'fade',duration:.4},leave:{kind:'fade',duration:.4}}],
    code:{snippet:'test',typing:[{from:0,to:.1,throughLine:1}],
      emphasis:[{line:1,phrase:'wheel',words:['wheel'],hold:.2}]}},
  {format:'machinome-video-draft/0.4',output:{width:640,height:360,fps:30,durationSeconds:2},audio:{replacements:{}},
    sourceCode:{test:{file:'machine.py',lines:[1,1]}}});
  const e=await project.film(source);
  await assert.rejects(preview(e,{viewer:'unused',width:640}),/Word timing needs cached speech.*run the speech command first/);
  await assert.rejects(render(e,{viewer:'unused',width:640,audio:null}),/Word timing needs cached speech.*run the speech command first/);
  await resolveWordTiming(e,async()=>({sha256:'fixture',alignment}));
  const moving=await viewer('moving.js',{timeColor:true});
  const report=await preview(e,{viewer:moving,width:640});
  assert.equal(report.pixelReplay,true);
  assert.equal(report.revealChecks.length,2);
  assert.deepEqual(report.revealChecks[0].samples.map(s=>s.shown),[1,2,3]);
  assert.equal(report.fadeChecks.length,5);
  assert.ok(report.emphasisChecks[0].samples.some(s=>s.phase==='word-0'&&s.words[0]==='wheel'));
  assert.equal(report.samples.filter(s=>s.reveal!==undefined||s.title!==undefined||s.emphasis!==undefined).length,14);
  // The check reads the words the stage shows, not the count it was asked for.
  await assert.rejects(browserSession(e,moving,640,[],async({page,pose})=>{
    await page.addStyleTag({content:'.vm-reveal-word{visibility:hidden !important}'});
    await pose(.4);
  }),/Overlay word count differs from timeline: pawls\.overlay-0 in pawls at 0\.40 s/);
  const overflow=structuredClone(source);
  overflow.shots[0].overlays[2].text=Array(30).fill('TOO TALL').join('\n');
  const tall=await project.film(overflow);
  await resolveWordTiming(tall,async()=>({sha256:'fixture',alignment}));
  await assert.rejects(browserSession(tall,moving,640,[],async({pose})=>{await pose(.5);}),/Title leaves the frame/);
});

test('a still and clip reach real browser pixels at their authored geometry and timestamps',async t=>{
  // The still, the clip frames and the two lossless encodes are an input
  // product, memoized; the test works on its own copy.
  const media=await artefact('render-picture-media',{},async out=>{
    execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','nullsrc=s=256x256',
      '-vf','geq=r=X:g=Y:b=0','-frames:v','1',join(out,'ramp.png')]);
    await mkdir(join(out,'clip-frames'));
    for(let n=0;n<9;n++){
      const c=(16*n).toString(16).padStart(2,'0');
      execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i',`color=c=0x${c}${c}${c}:s=160x120`,
        '-frames:v','1',join(out,'clip-frames',`frame${String(n).padStart(3,'0')}.png`)]);
    }
    const pictures=join(out,'clip-frames','frame%03d.png');
    execFileSync('ffmpeg',['-y','-v','error','-framerate','3','-i',pictures,'-f','lavfi','-i','sine=frequency=440:duration=3',
      '-shortest','-c:v','libx264','-qp','0','-pix_fmt','yuv444p','-c:a','aac',join(out,'clip.mp4')]);
    execFileSync('ffmpeg',['-y','-v','error','-framerate','3','-i',pictures,'-c:v','libvpx-vp9','-lossless','1',join(out,'clip.webm')]);
  });
  const files={'description.md':'Credits: {{pictureCredits}}'};
  for(const name of ['ramp.png','clip.mp4','clip.webm'])files[name]=await readFile(join(media,name));
  const {project,dir,viewer}=await filmFixture(t,{files});
  const source=filmEpisode({narration:'Pictures.',pictures:[
    {from:0,to:1,still:'ramp',area:'frame',fit:'contain',
      view:[{at:0,center:[.5,.5],zoom:1},{at:.8,center:[.5,.6],zoom:2,ease:'linear'}]},
    {from:1,to:2,clip:'clip',inPoint:1,area:'stage',enter:{kind:'fade',duration:.5}}],
    overlays:[{from:0,to:2,position:'top',text:'Above picture'}]},
  {format:'machinome-video-draft/0.4',output:{width:640,height:360,fps:4,durationSeconds:2},
    stills:{ramp:{file:'ramp.png',credit:'Test gradient',rights:'Own work',upscale:3}},
    clips:{clip:{file:'clip.mp4',credit:null,rights:null,upscale:3}}});
  const e=await project.film(source);
  const p=await preview(e,{viewer:await viewer('pictures.js',{timeColor:true}),width:640});
  assert.equal(p.pictureChecks.length,2);
  assert.ok(p.pictureChecks.every(c=>c.replay));
  const first=p.pictureChecks[0].samples[0],ramp=decodePng(await readFile(first.file));
  const i=(Math.round(180)*ramp.width+Math.round(320))*3;
  assert.ok(Math.abs(ramp.rgb[i]-128)<=1&&Math.abs(ramp.rgb[i+1]-128)<=1);
  assert.equal(p.pictureChecks[1].samples[0].frame,e.pictureMedia.clips.clip.timestamps.findIndex(t=>t>=1));
  assert.ok(p.pictureChecks[1].replayOpacity>.01);
  assert.deepEqual(p.pictureChecks[1].samples.map(s=>s.frame),[3,3,4,5]);
  for(const sample of p.pictureChecks[1].samples.filter(s=>s.time>=1.5)){
    const screen=decodePng(await readFile(sample.file));
    const clipFrame=decodePng(await readFile(join(e.pictureMedia.clips.clip.extraction.dir,
      `${String(sample.frame).padStart(6,'0')}.png`)));
    const screenAt=(180*screen.width+320)*3,sourceAt=(60*clipFrame.width+80)*3;
    for(let k=0;k<3;k++)assert.ok(Math.abs(screen.rgb[screenAt+k]-clipFrame.rgb[sourceAt+k])<=1);
  }
  const key=e.pictureMedia.clips.clip.extraction.key,indexPath=join(e.pictureMedia.clips.clip.extraction.dir,'index.json');
  const written=(await stat(indexPath)).mtimeMs;
  const extractedPng=join(e.pictureMedia.clips.clip.extraction.dir,'000005.png');
  const decodedWritten=(await stat(extractedPng)).mtimeMs;
  const priorPicture=await readFile(p.pictureChecks[1].samples.at(-1).file);
  const originalFull=decodePng(await readFile(p.pictureChecks[1].samples.find(s=>s.time>=1.5).file));
  const originalFullColor=[0,1,2].map(k=>originalFull.rgb[(180*originalFull.width+320)*3+k]);
  const repeated=await preview(e,{viewer:await viewer('pictures-reuse.js',{timeColor:true}),width:640});
  assert.equal(e.pictureMedia.clips.clip.extraction.key,key);
  assert.equal((await stat(indexPath)).mtimeMs,written);
  assert.equal((await stat(extractedPng)).mtimeMs,decodedWritten);
  assert.ok(priorPicture.equals(await readFile(repeated.pictureChecks[1].samples.at(-1).file)));
  const still='pawls.picture-0',clip='pawls.picture-1',top='pawls.overlay-0';
  await browserSession(e,await viewer('picture-pixels.js',{timeColor:true}),640,[],async({page,pose})=>{
    const at=async t=>{await pose(t);return decodePng(await page.screenshot());};
    const rgb=(picture,x,y)=>[0,1,2].map(k=>picture.rgb[(y*picture.width+x)*3+k]);
    const start=await at(0),middle=await at(.4),end=await at(.8);
    assert.deepEqual(rgb(start,10,180),[245,241,232]);
    assert.ok(Math.abs(rgb(start,320,180)[0]-128)<=1);
    assert.ok(Math.abs(rgb(start,360,180)[0]-(128+40/(360/256)))<=1);
    assert.ok(Math.abs(rgb(end,320,180)[1]-153)<=1);
    assert.ok(Math.abs(rgb(end,360,180)[0]-(128+40/(720/256)))<=1);
    assert.ok(Math.abs(rgb(middle,320,252)[1]-179)<=1);
    // The masthead (the paper set's chrome: its brand and series, and no
    // rule) stays above the full-frame picture, unchanged by it.
    const startPose=await pose(0),withStartPicture=decodePng(await page.screenshot());
    assert.equal(startPose.observed.chrome.length,2,'the brand and the series, and no rule');
    await pose(0,{elements:{[still]:absent(stateAt(e,0,still))}});const withoutStartPicture=decodePng(await page.screenshot());
    let unchangedMastheadPixels=0;
    for(const box of startPose.observed.chrome){
      for(let y=Math.floor(box.y);y<Math.ceil(box.y+box.height);y++)
        for(let x=Math.floor(box.x);x<Math.ceil(box.x+box.width);x++){
          const i=(y*withStartPicture.width+x)*3;
          for(let k=0;k<3;k++)assert.equal(withStartPicture.rgb[i+k],withoutStartPicture.rgb[i+k],`masthead at ${x},${y}`);
          unchangedMastheadPixels++;
        }
    }
    assert.ok(unchangedMastheadPixels>100);
    await pose(.4);const withPicture=decodePng(await page.screenshot());
    await pose(.4,{elements:{[still]:absent(stateAt(e,.4,still))}});const withoutPicture=decodePng(await page.screenshot());
    assert.ok(!withPicture.rgb.equals(withoutPicture.rgb),'the picture changes non-chrome pixels');
    await pose(.4,{elements:{[top]:absent(stateAt(e,.4,top))}});const withoutText=decodePng(await page.screenshot());
    await pose(.4);const withText=decodePng(await page.screenshot());
    const box=await page.locator('.vm-slot[data-slot="top"]').boundingBox();let textPixels=0;
    for(let y=Math.floor(box.y);y<Math.ceil(box.y+box.height);y++)
      for(let x=Math.floor(box.x);x<Math.ceil(box.x+box.width);x++){
        const i=(y*withText.width+x)*3;
        if([0,1,2].some(k=>withText.rgb[i+k]!==withoutText.rgb[i+k]))textPixels++;
      }
    assert.ok(textPixels>50,'the top overlay reaches pixels above the full-frame picture');
  });
  const low=structuredClone(source);low.output.fps=2;delete low.shots[0].pictures[1].enter;
  const lowFilm=await project.film(low);
  const lowReport=await preview(lowFilm,{viewer:await viewer('pictures-3-into-2.js',{timeColor:true}),width:640});
  assert.deepEqual(lowReport.pictureChecks[1].samples.map(s=>s.frame),[3,4]);
  for(const sample of lowReport.pictureChecks[1].samples){
    const screen=decodePng(await readFile(sample.file));
    const clipFrame=decodePng(await readFile(join(lowFilm.pictureMedia.clips.clip.extraction.dir,
      `${String(sample.frame).padStart(6,'0')}.png`)));
    const screenAt=(180*screen.width+320)*3,sourceAt=(60*clipFrame.width+80)*3;
    for(let k=0;k<3;k++)assert.ok(Math.abs(screen.rgb[screenAt+k]-clipFrame.rgb[sourceAt+k])<=1);
  }
  const cutSource=structuredClone(source);cutSource.shots[0].pictures[0].to=.75;
  cutSource.shots[0].pictures[0].view=[{at:0,center:[.5,.5],zoom:1}];
  const cut=await project.film(cutSource);
  await browserSession(cut,await viewer('picture-cut.js',{timeColor:true}),640,[],async({page,pose})=>{
    const forced=stateAt(cut,.74,still);
    await pose(.75,{elements:{[still]:forced}});const full=await page.screenshot();
    await pose(.75);const gone=await page.screenshot();
    await pose(.75,{elements:{[still]:absent(forced)}});const plain=await page.screenshot();
    assert.ok(!full.equals(gone),'the picture is nonvacuous immediately before its exclusive end');
    assert.ok(gone.equals(plain),'at cue.to the continuing model is exactly the plain frame');
  });
  await assert.rejects(browserSession(e,await viewer('picture-layout.js',{timeColor:true}),640,[],async({page,pose})=>{
    await page.addStyleTag({content:'.vm-slot[data-slot="stage"]{left:6% !important}'});
    await pose(1.2);
  }),/Film stage layout differs from the picture geometry/);
  const webmSource=structuredClone(source);webmSource.clips.clip.file='clip.webm';
  const webm=await project.film(webmSource);
  const alternate=await preview(webm,{viewer:await viewer('pictures-webm.js',{timeColor:true}),width:640});
  assert.deepEqual(alternate.pictureChecks[1].samples.map(s=>s.frame),[3,3,4,5]);
  const colours=[];
  for(const sample of alternate.pictureChecks[1].samples.filter(s=>s.time>=1.5)){
    const screen=decodePng(await readFile(sample.file));
    const clipFrame=decodePng(await readFile(join(webm.pictureMedia.clips.clip.extraction.dir,
      `${String(sample.frame).padStart(6,'0')}.png`)));
    const screenAt=(180*screen.width+320)*3,sourceAt=(60*clipFrame.width+80)*3;
    for(let k=0;k<3;k++)assert.ok(Math.abs(screen.rgb[screenAt+k]-clipFrame.rgb[sourceAt+k])<=1);
    colours.push(screen.rgb[screenAt]);
  }
  assert.ok(colours[1]>colours[0]);
  const narration=join(dir,'narration.wav');await writeFile(narration,pcmWav(Buffer.alloc(24000*2*2),24000));
  const out=await render(await project.film(source),{viewer:await viewer('pictures.js',{timeColor:true}),width:640,fps:4,
    audio:{mix:narration,records:[],captions:[]},label:'pictures'});
  const record=JSON.parse(await readFile(join(dir,'_build','pictures-manifest.json'),'utf8'));
  assert.equal(record.releaseReady,false);
  assert.ok(record.pictureReleaseIssues.some(s=>/clip.*credit/.test(s)));
  assert.equal(record.pictures.stills.ramp.sha256,e.pictureMedia.stills.ramp.sha256);
  assert.equal(record.pictures.stills.ramp.committed,true);
  assert.equal(record.pictures.clips.clip.audio,'not played');
  assert.equal(record.pictures.clips.clip.extraction.key,e.pictureMedia.clips.clip.extraction.key);
  assert.ok(record.pictures.clips.clip.extraction.ffmpegVersion.startsWith('ffmpeg version'));
  assert.match(await readFile(join(dir,'_build','description.md'),'utf8'),/ramp: Test gradient/);
  const streams=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-of','json',out],{encoding:'utf8'})).streams;
  assert.deepEqual(streams.map(s=>s.codec_type),['video','audio']);
  const clipStreams=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-of','json',join(dir,'clip.mp4')],{encoding:'utf8'})).streams;
  assert.deepEqual(clipStreams.map(s=>s.codec_type),['video','audio']);
  // A still and a clip of one name are credited separately.
  const collisionSource=structuredClone(source);
  collisionSource.clips={ramp:{...collisionSource.clips.clip,credit:'Distinct clip credit'}};collisionSource.shots[0].pictures[1].clip='ramp';
  await render(await project.film(collisionSource),{viewer:await viewer('pictures-collision.js',{timeColor:true}),width:640,fps:4,
    audio:null,label:'collision'});
  assert.match(await readFile(join(dir,'_build','description.md'),'utf8'),/ramp: Test gradient\nramp: Distinct clip credit/);
  // A clip with unresolved rights, not committed, and a template without the credits placeholder.
  await copyFile(join(dir,'clip.mp4'),join(dir,'uncommitted.mp4'));
  const unreadySource=structuredClone(collisionSource);
  unreadySource.clips.ramp={...unreadySource.clips.ramp,file:'uncommitted.mp4',rights:null};
  await writeFile(join(dir,'description.md'),'No picture-credit placeholder.');
  await render(await project.film(unreadySource),{viewer:await viewer('pictures-unready.js',{timeColor:true}),width:640,fps:4,
    audio:null,label:'unready'});
  const unreadyReport=JSON.parse(await readFile(join(dir,'_build','unready-manifest.json'),'utf8'));
  assert.ok(unreadyReport.pictureReleaseIssues.some(s=>/unresolved rights/.test(s)));
  assert.ok(unreadyReport.pictureReleaseIssues.some(s=>/not committed/.test(s)));
  assert.ok(unreadyReport.pictureReleaseIssues.some(s=>/lacks \{\{pictureCredits\}\}/.test(s)));
  // The render width rechecks the enlargement, on the first frame that draws the still.
  await assert.rejects(render(e,{viewer:await viewer('pictures-wide.js',{timeColor:true}),width:3840,fps:4,audio:null}),
    /Still ramp would be enlarged/);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=blue:s=160x120:r=3',
    '-t','3','-c:v','libx264','-pix_fmt','yuv420p',join(dir,'clip.mp4')]);
  const blue=await project.film(source);
  const replaced=await preview(blue,{viewer:await viewer('pictures-replaced.js',{timeColor:true}),width:640});
  assert.notEqual(blue.pictureMedia.clips.clip.extraction.key,key);
  const replacement=replaced.pictureChecks[1].samples.find(s=>s.time>=1.5);
  const changed=decodePng(await readFile(replacement.file));
  const color=[0,1,2].map(k=>changed.rgb[(180*changed.width+320)*3+k]);
  assert.notDeepEqual(color,originalFullColor);
  assert.ok(color[2]>color[0],'replacement frame is blue, unlike the original luma frame');
  const changedSource=decodePng(await readFile(join(blue.pictureMedia.clips.clip.extraction.dir,
    `${String(replacement.frame).padStart(6,'0')}.png`)));
  for(let k=0;k<3;k++)assert.ok(Math.abs(color[k]-changedSource.rgb[(60*changedSource.width+80)*3+k])<=1);
});

test('an arrow follows a moving part and a label rides a world point, reproducibly',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({annotations:[
    {from:.5,to:2,kind:'arrow',part:['Feed','Pawl'],place:[.1,.47],text:'Pulls'},
    {from:0,to:2,kind:'label',point:[0,0,0],offset:[0,-.2],text:'Origin'}]}));
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  const arrowId=markId(e,'pawls',0),labelId=markId(e,'pawls',1);
  const arrows=p.samples.filter(s=>s.marks?.['pawls.view']?.some(m=>m.id===arrowId))
    .map(s=>({...s,arrow:s.marks['pawls.view'].find(m=>m.id===arrowId)}));
  assert.ok(arrows.length>=4,'preview samples the cue at its start, quarters and end');
  const [first,last]=[arrows[1],arrows.at(-2)];
  assert.notDeepEqual(first.arrow.anchor,last.arrow.anchor);
  for(const {arrow} of [first,last]){
    const {anchor,rect}=arrow;
    assert.ok(anchor.x>=rect.x&&anchor.x<=rect.x+rect.width&&anchor.y>=rect.y&&anchor.y<=rect.y+rect.height,'the tip lies on the part');
  }
  const {anchor,tail}=first.arrow,l=Math.hypot(anchor.x-tail.x,anchor.y-tail.y);
  const colour=await pixel(first.file,anchor.x-2*(anchor.x-tail.x)/l,anchor.y-2*(anchor.y-tail.y)/l);
  for(const [i,v] of [0xbf,0x53,0x1f].entries())assert.ok(Math.abs(colour[i]-v)<=24,`accent at the tip: ${colour}`);
  const label=p.samples[0].marks['pawls.view'].find(m=>m.id===labelId);
  assert.ok(label.text.y+label.text.height<label.anchor.y,'the label sits above its point');
  await assert.rejects(preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640}),/Viewer API 28.*annotations \(shot pawls\).*declares API 27/);
  await assert.rejects(preview(e,{viewer:await viewer('vanishing.js',{vanishAfter:.5}),width:640}),/not on screen: pawls #0 'Pulls'/);
});

test('a highlight is applied and restored by requested state, and preview proves both in pixels',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({highlight:[{from:.5,to:1.5,parts:['pawl'],others:'ghost'}]}));
  const good=await viewer('viewer28.js');
  const p=await preview(e,{viewer:good,width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.highlightChecks.map(c=>[c.shotId,c.index,c.changed,c.restored,c.reapplied]),[['pawls',0,true,true,true]]);
  const calls=await browserSession(e,good,640,[],async({page,pose})=>{
    for(const time of [0,.6,1,1.6,.6,0])await pose(time);
    return {result:await page.evaluate(()=>window.viewerCalls.filter(c=>c[0]!=='setView'))};
  });
  assert.deepEqual(calls.result.map(c=>c[0]),['highlight','restore','highlight','restore'],'one highlight and one restore per entry and exit');
  for(const call of calls.result.filter(c=>c[0]==='highlight'))
    assert.deepEqual(call.slice(1),[[['Feed','Pawl']],{color:'#bf531f',others:'ghost'}]);
  await assert.rejects(preview(e,{viewer:await viewer('broken.js',{brokenRestore:true}),width:640}),/Highlight did not restore exactly: pawls #0/);
  await assert.rejects(preview(e,{viewer:await viewer('inert.js',{inertHighlight:true}),width:640}),/Highlight did not reach the pixels: pawls #0/);
  await assert.rejects(preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640}),/Viewer API 28 for highlight \(shot pawls\).*declares API 27/);
});

test('field of view and up reach the viewer at API 28 and the picture proves the lens',async t=>{
  const {project,viewer}=await filmFixture(t);
  const cameras={a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},tight:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:20},
    rolled:{position:[0,-10,0],target:[0,0,0],up:[1,0,1],fov:37}};
  const e=await project.film(filmEpisode({camera:[{at:0,preset:'a'},{at:1.5,preset:'tight'}]},{cameras}));
  const good=await viewer('viewer28.js');
  const p=await preview(e,{viewer:good,width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.cameraChecks.map(c=>[c.shotId,c.time,c.fov]),[['pawls',0,37],['pawls',1.5,20]]);
  for(const c of p.cameraChecks)assert.ok(Math.abs(c.measured/c.expected-1)<=.02);
  const calls=await browserSession(e,good,640,[],async({page,pose})=>{await pose(.75);return {result:await page.evaluate(()=>window.viewerCalls.at(-1)[1])};});
  assert.deepEqual(calls.result,{camera:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:28.5});
  const rolled=await project.film(filmEpisode({camera:[{at:0,preset:'a'},{at:1.5,preset:'rolled'}]},{cameras}),{at:'rolled'});
  const r=await preview(rolled,{viewer:good,width:640});
  assert.ok(r.cameraChecks.length===2&&r.cameraChecks.every(c=>c.upAbove===true));
  await assert.rejects(preview(e,{viewer:await viewer('ignores.js',{ignoreFov:true}),width:640}),/Viewer did not adopt the requested field of view/);
  await assert.rejects(preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640}),/Viewer API 28 for camera up\/field of view \(shot pawls\).*declares API 27/);
});

test('below API 28 the page calls setView exactly as before, with camera and target only',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({camera:[{at:0,preset:'a'},{at:2,preset:'b'}]},{format:'machinome-video-draft/0.2',
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},b:{position:[5,-10,0],target:[0,0,0],up:[0,0,1],fov:37}}}));
  const calls=await browserSession(e,await viewer('viewer27.js',{api:27}),640,[],async({page,pose})=>{
    await page.evaluate(()=>{window.viewerCalls.length=0;});
    for(const time of [0,.5,1.5])await pose(time);
    return {result:await page.evaluate(()=>window.viewerCalls.map(c=>Object.keys(c[1]).sort()))};
  });
  assert.equal(calls.result.length,3);
  for(const keys of calls.result)assert.deepEqual(keys,['camera','target']);
});

test('eased camera moves and model time reach the viewer as frameAt poses them, on API 28 and API 27',async t=>{
  const {project,viewer}=await filmFixture(t);
  const cameras={a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},b:{position:[4,-10,2],target:[0,0,0],up:[0,0,1],fov:37}};
  const e=await project.film(filmEpisode({camera:[{at:0,preset:'a'},{at:1.5,preset:'b',ease:'out'}],
    simulation:{from:0,to:2,keyframes:[{at:0,seconds:0},{at:.5,seconds:0},{at:2,seconds:2,ease:'in'}]}},
  {format:'machinome-video-draft/0.4',cameras}));
  const good=await viewer('viewer28.js',{recordTime:true});
  const p=await preview(e,{viewer:good,width:640});
  assert.equal(p.pixelReplay,true);
  const instants=[.25,.75,1.25,1.5,1.75];
  const calls=await browserSession(e,good,640,[],async({page,pose})=>{
    await page.evaluate(()=>{window.viewerCalls.length=0;});
    for(const time of instants)await pose(time);
    return {result:await page.evaluate(()=>window.viewerCalls)};
  });
  const views=calls.result.filter(c=>c[0]==='setView').map(c=>c[1]),times=calls.result.filter(c=>c[0]==='setTime').map(c=>c[1]);
  assert.equal(views.length,instants.length);assert.equal(times.length,instants.length);
  instants.forEach((time,i)=>{
    const f=stateAt(e,time,'pawls.view');
    assert.deepEqual(views[i],{camera:f.view.camera,target:f.view.target,up:f.up,fov:f.fov},`setView at ${time}`);
    assert.equal(times[i],f.time,`setTime at ${time}`);
  });
  // Eased, not the default curves: out at half the move, in at half the segment.
  assert.deepEqual(views[1].camera,[3.5,-10,1.75]);
  assert.equal(times[2],.125);
  assert.equal(times[0],0,'the held pose before the eased segment');
  const old=await preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640});
  assert.equal(old.pixelReplay,true,'easing needs no newer viewer');
});

// Shot transitions (format 0.4). The double paints its canvas a colour computed
// from model time, so the continued outgoing shot and the incoming one differ.
const timeColor=time=>[Math.round(255*time),96,160];
const transitionFixture=t=>filmFixture(t,{manifest:{...PAWL_MANIFEST,animation:{loop:20}},files:{'machine.py':'x = 1\n'}});
// Code and model shots alternate, each joined to the next by another kind;
// model seconds jump between shots so every pair of pictures differs.
function joinedFilm(){
  const e=filmEpisode({},{format:'machinome-video-draft/0.4',output:{width:640,height:360,fps:4,durationSeconds:10},
    model:{expectedDurationSeconds:20},
    sourceCode:{test:{file:'machine.py',lines:[1,1]}}});
  const base=e.shots[0],code={snippet:'test',typing:[{from:0,to:.5,throughLine:1}]};
  const shot=(i,id,extra)=>({...base,id,start:2*i,end:2*i+2,simulation:{from:3*i,to:3*i+2},...extra});
  e.shots=[shot(0,'code0',{code,fadeIn:{duration:.5}}),
    shot(1,'model1',{transition:{kind:'dissolve',duration:1}}),
    shot(2,'code2',{code,transition:{kind:'wipe',duration:1,direction:'right'}}),
    shot(3,'model3',{transition:{kind:'slide',duration:1}}),
    shot(4,'code4',{code,transition:{kind:'fade',duration:1},fadeOut:{duration:.5,color:'#000000'}})];
  return e;
}

test('a dissolve from a continued clip into a fading title keeps film chrome unblended',async t=>{
  const {project,dir,viewer}=await transitionFixture(t);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=blue:s=160x120:r=4',
    '-t','3','-c:v','libx264','-pix_fmt','yuv420p',join(dir,'joined.mp4')]);
  const source=filmEpisode({pictures:[{from:0,to:2,clip:'joined',area:'stage'}],
    overlays:[{from:0,to:2,text:'Outgoing clip',position:'top'}]},
  {format:'machinome-video-draft/0.4',output:{width:640,height:360,fps:4,durationSeconds:4},
    model:{expectedDurationSeconds:20},
    clips:{joined:{file:'joined.mp4',credit:'Own',rights:'Own',upscale:2}}});
  source.shots.push({...structuredClone(source.shots[0]),id:'closing',start:2,end:4,
    simulation:{from:2,to:4},pictures:[],transition:{kind:'dissolve',duration:1},
    overlays:[{from:.2,to:2,text:'CLOSING',position:'title',enter:{kind:'fade',duration:.6}}]});
  const p=await preview(await project.film(source),{viewer:await viewer('joined-picture.js',{timeColor:true}),width:640});
  assert.ok(p.transitionChecks[0].largestDifference<=2);
  const incoming=structuredClone(source);
  incoming.shots[0].pictures=[];
  incoming.shots[1].pictures=[{from:0,to:2,clip:'joined',area:'stage'}];
  const q=await preview(await project.film(incoming),{viewer:await viewer('incoming-picture.js',{timeColor:true}),width:640});
  assert.ok(q.transitionChecks[0].largestDifference<=2);
});

test('shots joined by every kind pass preview with each transition proved in pixels, and render reproducibly',async t=>{
  const {project,dir,viewer}=await transitionFixture(t);
  const e=await project.film(joinedFilm());
  const colored=await viewer('colored.js',{timeColor:true,recordTime:true});
  const p=await preview(e,{viewer:colored,width:640});
  assert.equal(p.pixelReplay,true);
  const checks=Object.fromEntries(p.transitionChecks.map(c=>[`${c.shotId}:${c.field}`,c]));
  assert.deepEqual(Object.keys(checks).sort(),['code0:fadeIn','code2:transition','code4:fadeOut','code4:transition','model1:transition','model3:transition']);
  const dissolve=checks['model1:transition'];
  assert.equal(dissolve.kind,'dissolve');assert.ok(dissolve.largestDifference<=2);assert.equal(dissolve.picturesDiffer,true);
  for(const key of ['code2:transition','model3:transition']){
    assert.equal(checks[key].largestDifference,0,key);assert.equal(checks[key].picturesDiffer,true,key);
  }
  for(const key of ['code0:fadeIn','code4:fadeOut','code4:transition']){
    assert.equal(checks[key].exactColor,true,key);assert.ok(checks[key].largestDifference<=2,key);
  }
  for(const c of p.transitionChecks){assert.equal(c.replay,true);assert.equal(c.stills.length,c.instants.length);assert.ok(c.instants.length>=2);}
  assert.deepEqual(checks['model1:transition'].instants,[2,2.25,2.5,2.75],'first frame, quarters, midpoint and last frame, once each');
  // The outgoing code shot runs on into the dissolve: at its midpoint the viewer is
  // first posed at model second 2 + 0.5, and the composed canvas blends that colour.
  const middle=2.5,f=frameAt(e,middle),incoming=f.elements['model1.view'];
  assert.equal(f.transition.outgoing.elements['code0.view'].time,2.5/20);
  const seen=await browserSession(e,colored,640,[],async({page,pose})=>{
    await page.evaluate(()=>{window.viewerCalls.length=0;});
    await pose(middle);
    const file=join(dir,'middle.png');await page.screenshot({path:file});
    return {result:{calls:await page.evaluate(()=>window.viewerCalls.filter(c=>c[0]==='setTime').map(c=>c[1])),file}};
  });
  assert.deepEqual(seen.result.calls,[2.5/20,incoming.time]);
  const [pa,pb]=[timeColor(2.5/20),timeColor(incoming.time)],w=f.transition.progress;
  const got=await pixel(seen.result.file,640*.78,360*.5);
  for(let i=0;i<3;i++)assert.ok(Math.abs(got[i]-((1-w)*pa[i]+w*pb[i]))<=2,`blend of the continued outgoing colour: ${got} from ${pa} and ${pb}`);
  // The whole film renders, and a transition frame posed in a fresh session is byte-identical.
  const output=await render(e,{viewer:colored,label:'silent-preview'});
  const report=JSON.parse(await readFile(join(dir,'_build/silent-preview-manifest.json'),'utf8'));
  assert.equal(output,join(dir,'_build/silent-preview.mp4'));assert.equal(report.count,40);
  const fresh=await browserSession(e,colored,640,[],async({page,pose})=>{await pose(10/4);return {result:await page.screenshot()};});
  assert.ok(fresh.result.equals(await readFile(join(report.dir,'000010.png'))),'frame 10 (the dissolve midpoint) reproduces exactly');
});

test('an arrow that runs to the cut follows its part into the transition and is refused when it leaves',async t=>{
  const {project,viewer}=await transitionFixture(t);
  const source=filmEpisode({},{format:'machinome-video-draft/0.4',output:{width:640,height:360,fps:4,durationSeconds:4},
    model:{expectedDurationSeconds:20}});
  const base=source.shots[0];
  source.shots=[{...base,id:'model1',start:0,end:2,simulation:{from:0,to:2},
    annotations:[{from:.5,to:2,kind:'arrow',part:['Feed','Pawl'],place:[.1,.47],text:'Pulls'}]},
  {...base,id:'next',start:2,end:4,simulation:{from:5,to:7},transition:{kind:'dissolve',duration:1}}];
  const e=await project.film(source);
  const error=await preview(e,{viewer:await viewer('vanishing.js',{vanishAfter:2/20}),width:640}).then(()=>null,error=>error);
  assert.ok(error,'preview refuses');
  const match=/^Annotation target is not on screen: model1 #0 'Pulls' at (\d+\.\d+) s$/.exec(error.message);
  assert.ok(match,error.message);assert.ok(Number(match[1])>2,'a time past the outgoing shot\'s end');
  assert.equal((await preview(e,{viewer:await viewer('staying.js'),width:640})).pixelReplay,true);
});

// Rings, entrances and exits (graphic-overlays, format 0.4).
const V04={format:'machinome-video-draft/0.4'};
const ACCENT=hexColor('#bf531f'),CANVAS=hexColor('#6f8fa8');
// Every pixel of the 3×3 neighbourhood of p, as [r, g, b].
const around=(image,p)=>{const out=[];
  for(let y=Math.round(p.y)-1;y<=Math.round(p.y)+1;y++)for(let x=Math.round(p.x)-1;x<=Math.round(p.x)+1;x++)
    out.push([0,1,2].map(k=>image.rgb[(y*image.width+x)*3+k]));
  return out;};
const near=(c,d,levels)=>c.every((v,k)=>Math.abs(v-d[k])<=levels);

test('a ring encloses its moving part in the accent, and draws itself on clockwise from the top',async t=>{
  const {project,viewer}=await filmFixture(t);
  const good=await viewer('viewer28.js');
  const e=await project.film(filmEpisode({annotations:[{from:0,to:2,kind:'ring',part:'pawl'}]},V04));
  const p=await preview(e,{viewer:good,width:640});
  assert.equal(p.pixelReplay,true);
  const rings=p.samples.filter(s=>s.marks?.['pawls.view']?.length).map(s=>({file:s.file,...s.marks['pawls.view'][0]}));
  const [a,b]=[rings[0],rings.at(-1)];
  assert.notDeepEqual(a.ring,b.ring,'the ring follows the part');
  const P=.01*640*(1-2*.08);
  for(const {rect,ring,file} of [a,b]){
    const {cx,cy,rx,ry}=ring;
    assert.ok(Math.abs(cx-(rect.x+rect.width/2))<1e-9&&Math.abs(cy-(rect.y+rect.height/2))<1e-9,'centred on the rectangle');
    assert.ok(Math.abs(rx-Math.SQRT2*(rect.width/2+P))<1e-6&&Math.abs(ry-Math.SQRT2*(rect.height/2+P))<1e-6,'through the grown corners');
    for(const [x,y] of [[rect.x,rect.y],[rect.x+rect.width,rect.y],[rect.x,rect.y+rect.height],[rect.x+rect.width,rect.y+rect.height]])
      assert.ok(((x-cx)/rx)**2+((y-cy)/ry)**2<1,'every corner inside the ring');
    assert.ok(around(decodePng(await readFile(file)),{x:cx+rx,y:cy}).some(c=>near(c,ACCENT,24)),'accent at the rightmost point');
  }
  // Drawn on over its first second, linearly: half drawn at 0.5 s, from the top round the right.
  const drawn=await project.film(filmEpisode({annotations:[{from:0,to:2,kind:'ring',part:'pawl',enter:{kind:'draw',duration:1,ease:'linear'}}]},V04),{at:'drawn'});
  const seen=await browserSession(drawn,good,640,[],async({page,pose})=>{
    const f=await pose(.5);return {result:{ring:f.observed.elements['pawls.view'].marks[0],image:decodePng(await page.screenshot())}};
  });
  const {ring,image}=seen.result;
  assert.equal(ring.drawn,.5);assert.equal(ring.opacity,1);
  assert.ok(ring.inside.x>ring.ring.cx,'the drawn half is on the right (clockwise from the top)');
  assert.ok(ring.outside.x<ring.ring.cx,'the undrawn half is on the left');
  assert.ok(around(image,ring.inside).some(c=>near(c,ACCENT,24)),'part of the stroke is drawn');
  assert.ok(around(image,ring.outside).every(c=>near(c,CANVAS,2)),'the rest is not');
  const q=await preview(drawn,{viewer:good,width:640});
  assert.deepEqual(q.entranceChecks.map(c=>[c.shotId,c.index,c.phase,c.kind]),
    [['pawls',0,'enter-start','draw'],['pawls',0,'enter','draw'],['pawls',0,'enter-end','draw']]);
  assert.deepEqual(q.entranceChecks.map(c=>c.time),[0,.5,1]);
  assert.equal(q.entranceChecks[1].drawn,.5);assert.equal(q.entranceChecks[1].replay,true);
  for(const c of q.entranceChecks)assert.equal(c.vacuous,false);
});

test('an arrow fading in and a label fading out are proved as the blends their easing predicts',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({annotations:[
    {from:0,to:2,kind:'arrow',part:['Feed','Pawl'],place:[.1,.47],text:'Pulls',enter:{kind:'fade',duration:1,ease:'linear'}},
    {from:0,to:2,kind:'label',point:[0,0,0],offset:[0,-.2],text:'Origin',leave:{kind:'fade',duration:1}}]},V04));
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  const checks=Object.fromEntries(p.entranceChecks.map(c=>[`${c.index}:${c.phase}`,c]));
  assert.deepEqual(Object.keys(checks),['0:enter-start','0:enter','0:enter-end','1:leave-start','1:leave']);
  for(const key of ['0:enter','1:leave']){
    const c=checks[key];assert.equal(c.kind,'fade');assert.ok(c.largestDifference<=2,key);assert.equal(c.vacuous,false,key);
  }
  assert.equal(checks['0:enter'].opacity,.5);
  for(const key of ['0:enter-start','0:enter-end','1:leave-start'])assert.equal(checks[key].largestDifference,0,key);
  assert.equal(checks['0:enter-start'].opacity,0);assert.equal(checks['1:leave-start'].opacity,1);
});

test('a drawn arrow keeps its words visible and reveals only the shaft toward its part',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({annotations:[{from:0,to:2,kind:'arrow',part:'pawl',place:[.1,.47],text:'Pulls',
    enter:{kind:'draw',duration:1,ease:'linear'}}]},V04));
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.entranceChecks.map(c=>c.phase),['enter-start','enter','enter-end']);
  assert.equal(p.entranceChecks[1].drawn,.5);
  assert.equal(p.entranceChecks[1].replay,true);
  for(const c of p.entranceChecks)assert.equal(c.vacuous,false);
});

test('a ring whose part is not wholly on the stage, or that leaves the frame, is refused',async t=>{
  const {project,viewer}=await filmFixture(t);
  const ring=async(extra,at)=>project.film(filmEpisode({annotations:[{from:0,to:2,kind:'ring',part:'pawl',...extra}]},V04),{at});
  await assert.rejects(preview(await ring({},'plain'),{viewer:await viewer('wide.js',{rectSize:[600,20]}),width:640}),
    /^Error: Ring target is not wholly on screen: pawls #0 \(ring\) at 0\.00 s$/);
  await assert.rejects(preview(await ring({padding:.25},'padded'),{viewer:await viewer('viewer28.js'),width:640}),
    /^Error: Ring leaves the frame: pawls #0 \(ring\) at 0\.00 s$/);
  await assert.rejects(preview(await ring({},'vanishing'),{viewer:await viewer('vanishing.js',{vanishAfter:.5}),width:640}),
    /Annotation target is not on screen: pawls #0 \(ring\)/);
});

test('an entrance lasting the whole cue ends at its exclusive boundary without a false full-mark proof',async t=>{
  const {project,viewer}=await filmFixture(t);
  const e=await project.film(filmEpisode({annotations:[{from:0,to:2,kind:'ring',part:'pawl',enter:{kind:'fade',duration:2}}]},V04));
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.entranceChecks.map(c=>c.phase),['enter-start','enter','enter-end']);
  assert.deepEqual(p.entranceChecks[2],{shotId:'pawls',element:'pawls.view',mark:markId(e,'pawls',0),index:0,phase:'enter-end',kind:'fade',time:2,
    skipped:'cue ends at this exclusive boundary'});
});

test('a fractional cue at a nonzero shot start is active at its authored start and absent at its end',async t=>{
  const {project,viewer}=await filmFixture(t,{manifest:{...PAWL_MANIFEST,animation:{loop:20}}});
  const source=filmEpisode({},{...V04,model:{expectedDurationSeconds:20}});
  source.output.durationSeconds=12;source.output.fps=4;
  source.shots[0].id='lead';source.shots[0].end=10;source.shots[0].simulation.to=10;
  source.shots.push({...source.shots[0],id:'ropes',start:10,end:12,simulation:{from:10,to:12},
    annotations:[{from:.2,to:1.5,kind:'ring',part:'pawl',enter:{kind:'fade',duration:.5}}]});
  const e=await project.film(source);
  assert.deepEqual(stateAt(e,10.2,'ropes.view').marks.map(m=>m.id),[markId(e,'ropes',0)]);
  assert.deepEqual(stateAt(e,11.5,'ropes.view').marks,[]);
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.entranceChecks.map(c=>[c.phase,c.time]),[['enter-start',10.2],['enter',10.45],['enter-end',10.7]]);
});
