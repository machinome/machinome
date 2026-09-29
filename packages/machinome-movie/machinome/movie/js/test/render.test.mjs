import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {preview,render,browserSession} from '../src/render.mjs';
import {pcmWav} from '../src/speech.mjs';

// A minimal viewer double exercises film composition/encoding only. The real
// sawmill preview separately proves the public viewer and mechanical pixels.
test('short mixed-layout film renders with a same-basename sidecar, not embedded subtitles',async t=>{
  const dir=await mkdtemp(join(tmpdir(),'videomaker-render-test-'));
  t.after(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  const git=(...args)=>execFileSync('git',args,{cwd:dir,encoding:'utf8'}).trim();
  git('init','-q');
  await writeFile(join(dir,'episode.yaml'),'test: film composition\n');
  await writeFile(join(dir,'production.yaml'),'test: short render\n');
  await writeFile(join(dir,'description.md'),'Test description.');
  git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture');
  await writeFile(join(dir,'manifest.json'),JSON.stringify({root:{name:'test'},animation:{loop:2}}));
  const viewer=join(dir,'viewer.js');
  await writeFile(viewer,`window.MachinomeViewer={async mount(selector,url,options){
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';document.querySelector(selector).append(canvas);
    let view=options.view;return {apiVersion:27,setTime(){},setVisible(){},navigation(){return {}},
      setView(v){if(!v.camera.every(Number.isFinite))throw new Error('invalid camera');view=v;},
      view(){return {camera:{toArray:()=>view.camera},target:{toArray:()=>view.target}}}};
  }};`);
  const mix=join(dir,'voice.wav');await writeFile(mix,pcmWav(Buffer.alloc(24000*2*2),24000));
  const shot={narration:'Separate subtitles.',direction:'Show source.',camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]};
  const e={title:'Test',series:'',output:{width:640,height:360,fps:2,durationSeconds:2},
    model:{expectedDurationSeconds:2},style:{background:'#f5f1e8',foreground:'#222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
    sourceCode:{test:{file:'machine.py',lines:[1,1],text:'x = 1'}},
    paths:{repository:dir,episode:join(dir,'episode.yaml'),production:join(dir,'production.yaml'),manifest:join(dir,'manifest.json'),build:join(dir,'_build')},
    cameras:{a:{position:[1,1,1],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    release:{descriptionTemplate:'description.md'},
    shots:[{...shot,id:'code',start:0,end:1,simulation:{from:0,to:1},code:{snippet:'test',typing:[{from:0,to:.5,throughLine:1}]}},
      {...shot,id:'whole',start:1,end:2,simulation:{from:1,to:2}}]};
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

// A configurable API 28 viewer double. Its canvas is one flat colour; a part's
// on-screen rect moves with model time; project() is a pinhole camera.
function viewerDouble(options={}){
  const o={api:28,color:'#6f8fa8',...options};
  return `window.MachinomeViewer={async mount(selector,url,options){
    const o=${JSON.stringify(o)};
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';canvas.style.background=o.color;
    document.querySelector(selector).append(canvas);
    let view={camera:options.view.camera,target:options.view.target,up:options.up,fov:options.fov},time=options.time??0,lit=null;
    const calls=window.viewerCalls=[];
    const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
    const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
    const norm=a=>{const l=Math.hypot(...a);return a.map(v=>v/l);};
    const vec=a=>({toArray:()=>[...a]});
    return {apiVersion:o.api,setVisible(){},navigation(){return {};},
      setTime(t){time=t;},
      setView(v){calls.push(['setView',v]);if(!v.camera.every(Number.isFinite))throw new Error('invalid camera');
        view={...view,camera:v.camera,target:v.target};
        if(!o.ignoreFov){if(v.up)view.up=v.up;if(v.fov!==undefined)view.fov=v.fov;}},
      view(){return {camera:vec(view.camera),target:vec(view.target),up:vec(view.up),fov:view.fov};},
      partOnScreen(path){
        if(path.join('/')!=='Feed/Pawl')throw new Error('Unknown assembly path: '+path.join('/'));
        if(o.vanishAfter!==undefined&&time>o.vanishAfter)return null;
        const b=canvas.getBoundingClientRect();
        return {rect:{x:b.left+b.width*(.35+.3*time),y:b.top+b.height*.5-10,width:24,height:20},point:null};
      },
      project(p){
        const f=norm(sub(view.target,view.camera)),r=norm(cross(f,view.up)),u=cross(r,f),d=sub(p,view.camera),z=dot(d,f);
        if(z<=0)return null;const b=canvas.getBoundingClientRect(),k=(b.height/2)/Math.tan(view.fov*Math.PI/360);
        return {x:b.left+b.width/2+dot(d,r)/z*k,y:b.top+b.height/2-dot(d,u)/z*k};
      },
      highlight(paths,settings){
        if(lit)throw new Error('A highlight is already standing');
        calls.push(['highlight',paths,settings]);if(!o.inertHighlight)canvas.style.background=settings.color;
        const token=lit={};
        return ()=>{if(lit!==token)throw new Error('restore called twice');calls.push(['restore']);lit=null;if(!o.brokenRestore)canvas.style.background=o.color;};
      }};
  }};`;
}
async function pixel(file,x,y){
  const bytes=execFileSync('ffmpeg',['-v','error','-i',file,'-f','rawvideo','-pix_fmt','rgb24','pipe:1']);
  const width=Number(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width','-of','csv=p=0',file],{encoding:'utf8'}).trim());
  const i=(Math.round(y)*width+Math.round(x))*3;return [bytes[i],bytes[i+1],bytes[i+2]];
}
function filmEpisode(dir,shotExtra={},extra={}){
  return {format:'machinome-video-draft/0.3',title:'Test',series:'',output:{width:640,height:360,fps:2,durationSeconds:2},
    model:{expectedDurationSeconds:2},
    style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
    paths:{repository:dir,episode:join(dir,'episode.yaml'),production:join(dir,'production.yaml'),manifest:join(dir,'manifest.json'),build:join(dir,'_build')},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{pawl:[['Feed','Pawl']]},
    release:{descriptionTemplate:'description.md'},
    shots:[{id:'pawls',start:0,end:2,narration:'Look.',direction:'Look.',simulation:{from:0,to:2},camera:[{at:0,preset:'a'}],
      hiddenLayers:[],overlays:[],evidence:[],...shotExtra}],...extra};
}
async function filmFixture(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-film-test-'));
  t.after(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  await writeFile(join(dir,'manifest.json'),JSON.stringify({root:{name:'test',children:[{name:'Feed',children:[{name:'Pawl'}]}]},animation:{loop:2}}));
  const viewer=async(name,options)=>{const file=join(dir,name);await writeFile(file,viewerDouble(options));return file;};
  return {dir,viewer};
}

test('an arrow follows a moving part and a label rides a world point, reproducibly',async t=>{
  const {dir,viewer}=await filmFixture(t);
  const e=filmEpisode(dir,{annotations:[
    {from:.5,to:2,kind:'arrow',part:['Feed','Pawl'],place:[.1,.47],text:'Pulls'},
    {from:0,to:2,kind:'label',point:[0,0,0],offset:[0,-.2],text:'Origin'}]});
  const p=await preview(e,{viewer:await viewer('viewer28.js'),width:640});
  assert.equal(p.pixelReplay,true);
  const arrows=p.samples.filter(s=>s.annotations?.some(a=>a.index===0)).map(s=>({...s,arrow:s.annotations.find(a=>a.index===0)}));
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
  const label=p.samples[0].annotations.find(a=>a.index===1);
  assert.ok(label.text.y+label.text.height<label.anchor.y,'the label sits above its point');
  await assert.rejects(preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640}),/Viewer API 28.*annotations \(shot pawls\).*declares API 27/);
  await assert.rejects(preview(e,{viewer:await viewer('vanishing.js',{vanishAfter:.5}),width:640}),/not on screen: pawls #0 'Pulls'/);
});

test('a highlight is applied and restored by requested state, and preview proves both in pixels',async t=>{
  const {dir,viewer}=await filmFixture(t);
  const e=filmEpisode(dir,{highlight:[{from:.5,to:1.5,parts:['pawl'],others:'ghost'}]});
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
  const {dir,viewer}=await filmFixture(t);
  const cameras={a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},tight:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:20},
    rolled:{position:[0,-10,0],target:[0,0,0],up:[1,0,1],fov:37}};
  const e=filmEpisode(dir,{camera:[{at:0,preset:'a'},{at:1.5,preset:'tight'}]},{cameras});
  const good=await viewer('viewer28.js');
  const p=await preview(e,{viewer:good,width:640});
  assert.equal(p.pixelReplay,true);
  assert.deepEqual(p.cameraChecks.map(c=>[c.shotId,c.time,c.fov]),[['pawls',0,37],['pawls',1.5,20]]);
  for(const c of p.cameraChecks)assert.ok(Math.abs(c.measured/c.expected-1)<=.02);
  const calls=await browserSession(e,good,640,[],async({page,pose})=>{await pose(.75);return {result:await page.evaluate(()=>window.viewerCalls.at(-1)[1])};});
  assert.deepEqual(calls.result,{camera:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:28.5});
  const rolled=filmEpisode(dir,{camera:[{at:0,preset:'a'},{at:1.5,preset:'rolled'}]},{cameras});
  const r=await preview(rolled,{viewer:good,width:640});
  assert.ok(r.cameraChecks.length===2&&r.cameraChecks.every(c=>c.upAbove===true));
  await assert.rejects(preview(e,{viewer:await viewer('ignores.js',{ignoreFov:true}),width:640}),/Viewer did not adopt the requested field of view/);
  await assert.rejects(preview(e,{viewer:await viewer('viewer27.js',{api:27}),width:640}),/Viewer API 28 for camera up\/field of view \(shot pawls\).*declares API 27/);
});

test('below API 28 the page calls setView exactly as before, with camera and target only',async t=>{
  const {dir,viewer}=await filmFixture(t);
  const e=filmEpisode(dir,{camera:[{at:0,preset:'a'},{at:2,preset:'b'}]},{format:'machinome-video-draft/0.2',
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},b:{position:[5,-10,0],target:[0,0,0],up:[0,0,1],fov:37}}});
  const calls=await browserSession(e,await viewer('viewer27.js',{api:27}),640,[],async({page,pose})=>{
    for(const time of [0,.5,1.5])await pose(time);
    return {result:await page.evaluate(()=>window.viewerCalls.map(c=>Object.keys(c[1]).sort()))};
  });
  assert.equal(calls.result.length,3);
  for(const keys of calls.result)assert.deepEqual(keys,['camera','target']);
});
