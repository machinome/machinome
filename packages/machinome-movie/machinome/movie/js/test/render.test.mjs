import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {preview,render} from '../src/render.mjs';
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
