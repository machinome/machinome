// Global setup of the slow project (vitest.config.mjs; ADR-003). Runs once per
// run, in the main process:
// - launches the one Chromium every browser test of the run shares
//   (test/support/stage.mjs connects to it), with the command line's flags;
// - records the toolchain the memo keys on, each obtained by running it once:
//   Node, Chromium, FFmpeg, ffprobe, Git, and the file and SHA-256 of every
//   face render binds (DejaVu Sans and DejaVu Sans Mono, regular and bold);
// - carries the cold switch (VIDEOMAKER_TEST_COLD=1, set by `npm test -- --cold`).
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {chromium} from 'playwright';
import {CHROMIUM_ARGS} from '../../src/render.mjs';

const FACES=[['DejaVu Sans','Regular'],['DejaVu Sans','Bold'],['DejaVu Sans Mono','Regular'],['DejaVu Sans Mono','Bold']];
const firstLine=(command,args)=>{
  try{return execFileSync(command,args,{encoding:'utf8',stdio:['ignore','pipe','ignore']}).split('\n')[0].trim();}
  catch{return null;}
};

let server=null;
export async function setup(project){
  server=await chromium.launchServer({headless:true,args:CHROMIUM_ARGS});
  const probe=await chromium.connect(server.wsEndpoint());
  const browserVersion=probe.version();await probe.close();
  const fonts=FACES.map(([family,style])=>{
    const path=firstLine('fc-match',['-f','%{file}',`${family}:style=${style}`]);
    return {family,style,path,sha256:path?createHash('sha256').update(readFileSync(path)).digest('hex'):null};
  });
  const toolchain={node:process.version,chromium:browserVersion,
    ffmpeg:firstLine('ffmpeg',['-version']),ffprobe:firstLine('ffprobe',['-version']),
    git:firstLine('git',['--version']),fonts};
  project.provide('toolchain',toolchain);
  project.provide('browserEndpoint',server.wsEndpoint());
  project.provide('cold',process.env.VIDEOMAKER_TEST_COLD==='1');
}
export async function teardown(){await server?.close();server=null;}
