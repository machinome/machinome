// Global setup of the slow project and of the viewer layer (vitest.config.mjs;
// ADR-003, ADR-008). Runs in the main process, where vitest loads it once per
// project, each with its own module instance; what it makes is therefore kept
// on the main process's globalThis, made by the first setup of the run,
// provided to every project that sets up, and closed by the last teardown:
// - launches the one Chromium every browser test of the run shares
//   (test/support/stage.mjs connects to it), with the command line's flags,
//   and provides its endpoint and the PID of its browser process (the viewer
//   layer reads the memory of its process tree);
// - records the toolchain the memo keys on, each obtained by running it once:
//   Node, Chromium, FFmpeg, ffprobe, Git, and the file and SHA-256 of every
//   face render binds (DejaVu Sans and DejaVu Sans Mono, regular and bold);
// - carries the cold switch (VIDEOMAKER_TEST_COLD=1, set by `npm test -- --cold`);
// - finds the one memo store every worktree of the repository shares, and
//   removes what a killed run left in it and under the temporary directory;
// - on a cold run, opens the run's cold directory, which the teardown removes.
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {chromium} from 'playwright';
import {CHROMIUM_ARGS} from '../../src/render.mjs';
import {memoDirectory,sweep,openColdRun,closeColdRun} from './memo.mjs';

const FACES=[['DejaVu Sans','Regular'],['DejaVu Sans','Bold'],['DejaVu Sans Mono','Regular'],['DejaVu Sans Mono','Bold']];
const firstLine=(command,args)=>{
  try{return execFileSync(command,args,{encoding:'utf8',stdio:['ignore','pipe','ignore']}).split('\n')[0].trim();}
  catch{return null;}
};

const RUN=Symbol.for('videomaker.test-run');
export async function setup(project){
  const run=globalThis[RUN]??={users:0,ready:null};
  run.users++;
  run.ready??=open();
  const {server,toolchain,cold,memoDir,coldDir}=await run.ready;
  project.provide('toolchain',toolchain);
  project.provide('browserEndpoint',server.wsEndpoint());
  project.provide('browserPid',server.process().pid);
  project.provide('cold',cold);
  project.provide('memoDir',memoDir);
  project.provide('coldDir',coldDir);
}
export async function teardown(){
  const run=globalThis[RUN];
  if(!run||--run.users>0)return;
  delete globalThis[RUN];
  const {server,coldDir}=await run.ready;
  await server.close();
  if(coldDir)await closeColdRun(coldDir);
}
async function open(){
  const cold=process.env.VIDEOMAKER_TEST_COLD==='1',memoDir=memoDirectory();
  await sweep({dir:cold?null:memoDir});
  const coldDir=cold?await openColdRun():null;
  const server=await chromium.launchServer({headless:true,args:CHROMIUM_ARGS});
  const probe=await chromium.connect(server.wsEndpoint());
  const browserVersion=probe.version();await probe.close();
  const fonts=FACES.map(([family,style])=>{
    const path=firstLine('fc-match',['-f','%{file}',`${family}:style=${style}`]);
    return {family,style,path,sha256:path?createHash('sha256').update(readFileSync(path)).digest('hex'):null};
  });
  const toolchain={node:process.version,chromium:browserVersion,
    ffmpeg:firstLine('ffmpeg',['-version']),ffprobe:firstLine('ffprobe',['-version']),
    git:firstLine('git',['--version']),fonts};
  return {server,toolchain,cold,memoDir,coldDir};
}
