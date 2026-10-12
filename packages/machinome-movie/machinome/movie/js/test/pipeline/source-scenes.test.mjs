import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {loadSourceCode,validateCode} from '../../src/code.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {yamlProject} from '../support/yaml-project.mjs';
import {speechRequest,pcmWav,mixSpeech} from '../../src/speech.mjs';

async function temp(t){const dir=await mkdtemp(join(tmpdir(),'videomaker-source-test-'));t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));return dir;}
test('source excerpts match pinned Git bytes, with validated bounds and containment',async t=>{
  const dir=await temp(t),git=(...args)=>execFileSync('git',args,{cwd:dir,encoding:'utf8'}).trim();
  git('init','-q');await writeFile(join(dir,'machine.py'),'class Mill:\n    wheel = Wheel()\n    wheel.drives(saw)\n');
  git('add','machine.py');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture');
  const e={paths:{repository:dir,production:join(dir,'production.yaml')},model:{sourceRevision:git('rev-parse','HEAD')},sourceCode:{drive:{file:'machine.py',lines:[2,3]}}};
  const loaded=await loadSourceCode(e);assert.equal(loaded.drive.text,'wheel = Wheel()\nwheel.drives(saw)');assert.equal(loaded.drive.lines[0],2);assert.equal(loaded.drive.file,'machine.py');
  e.sourceCode.drive.lines=[2,9];await assert.rejects(loadSourceCode(e),/line range/);e.sourceCode.drive.lines=[2,3];
  e.sourceCode.drive.file='../outside.py';await assert.rejects(loadSourceCode(e),/outside|ENOENT/);e.sourceCode.drive.file='machine.py';
  await writeFile(join(dir,'machine.py'),'made_up = True\n');await assert.rejects(loadSourceCode(e),/pinned/);
});
test('typing follows local time, holds between cues, restores and escapes markup',async t=>{
  const lines=[...Array.from({length:9},(_,i)=>`# line ${i+1}`),'x = "<script>"','wheel.drives(saw)'];
  const project=await yamlProject(t,{manifest:{root:{name:'test'},animation:{loop:8}},files:{'machine.py':lines.join('\n')+'\n'}});
  const code={snippet:'drive',typing:[{from:1,to:3,throughLine:10},{from:5,to:7,throughLine:11}]};
  const e={format:'machinome-video-draft/0.4',title:'Typing',output:{width:320,height:180,fps:10,durationSeconds:8},
    model:{expectedDurationSeconds:8},cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},
    sourceCode:{drive:{file:'machine.py',lines:[10,11]}},
    shots:[{id:'test',start:0,end:8,narration:'Type.',direction:'Type.',simulation:{from:0,to:8},camera:[{at:0,preset:'a'}],
      hiddenLayers:[],overlays:[],evidence:[],code}]};
  const film=await project.film(e),codeAt=time=>frameAt(film,time).elements['test.code'];
  assert.equal(codeAt(0).text,'');assert.equal(codeAt(4).text,'x = "<script>"');
  const before=codeAt(2);codeAt(7);assert.deepEqual(codeAt(2),before);
  const full=codeAt(7);assert.equal(full.text,'x = "<script>"\nwheel.drives(saw)');assert.match(full.html,/hljs-string/);assert.ok(!full.html.includes('<script>'));
  assert.match(full.html,/hljs-title function_/);
  // The same rules as the YAML validation states them.
  const snippet={file:'machine.py',lines:[10,11],text:full.text},shot={id:'test',start:0,end:8,code:structuredClone(code)};
  assert.doesNotThrow(()=>validateCode({sourceCode:{drive:snippet}},shot));
  shot.code.typing[1].from=2;assert.throws(()=>validateCode({sourceCode:{drive:snippet}},shot),/typing/);
  shot.code.typing=[{from:0,to:3,throughLine:10}];assert.throws(()=>validateCode({sourceCode:{drive:snippet}},shot),/complete/);
  code.typing[1].from=2;await assert.rejects(project.film(e),/typing/);
});
test('v3 omits continuity fields and uses valid defaults without changing legacy requests',()=>{
  const request=speechRequest({audio:{model:'eleven_v3'}},['First.','Second.'],1);
  assert.equal(request.voice_settings.stability,.5);assert.equal(request.previous_text,undefined);assert.equal(request.next_text,undefined);
  const legacy=speechRequest({audio:{model:'eleven_multilingual_v2'}},['First.','Second.'],1);
  assert.equal(legacy.previous_text,'First.');assert.equal(legacy.voice_settings.stability,.65);
});
test('lossless wrapping preserves every sample and mixing retains sound from clip start',async t=>{
  const dir=await temp(t);const pcm=Buffer.alloc(24000*2);
  for(let i=0;i<24000;i++)pcm.writeInt16LE(Math.round(9000*Math.cos(2*Math.PI*700*i/24000)),i*2);
  const wav=pcmWav(pcm,24000);assert.deepEqual(wav.subarray(44),pcm);assert.equal(wav.readUInt32LE(24),24000);
  assert.throws(()=>pcmWav(Buffer.alloc(3),24000),/PCM/);
  const file=join(dir,'onset.wav');await writeFile(file,wav);const mix=join(dir,'mix.wav');
  await mixSpeech([{file,offset:.5}],2,mix);
  const bytes=execFileSync('ffmpeg',['-v','error','-i',mix,'-f','f32le','-ac','1','-ar','24000','pipe:1']);
  const signal=new Float32Array(bytes.buffer,bytes.byteOffset,bytes.length/4);
  let xx=0,yy=0,xy=0;for(let i=0;i<2400;i++){const x=pcm.readInt16LE(i*2),y=signal[12000+i];xx+=x*x;yy+=y*y;xy+=x*y;}
  assert.ok(xy/Math.sqrt(xx*yy)>.995,'first 100ms must survive');
  assert.ok(Math.abs(signal[12000])>.05,'first sample is not gated');
});
test('film stage has no narration caption element',async()=>{
  const html=await readFile(new URL('../../src/film.html',import.meta.url),'utf8');
  assert.doesNotMatch(html,/id="caption"/);
});
