// The browser entry points of src/render.mjs for the slow tests, on the run's
// one Chromium (launched by test/support/toolchain.mjs) and one asset server.
// The slow project runs in one worker with a shared module graph, so the first
// call connects and makes the asset server, and every later call of the run
// reuses both. A test whose pass is memoized never calls them, and a run
// whose every browser test is memoized connects to nothing. (ADR-003)
import {inject} from 'vitest';
import {chromium} from 'playwright';
import * as renderer from '../../src/render.mjs';

let shared=null;
export function sharedStage(){
  return shared??=(async()=>{
    const endpoint=inject('browserEndpoint');
    if(!endpoint)throw new Error('No shared Chromium: the slow project\'s global setup (test/support/toolchain.mjs) did not run');
    return {browser:await chromium.connect(endpoint),assets:await renderer.assetServer()};
  })();
}
export async function preview(e,options){return renderer.preview(e,{...options,...await sharedStage()});}
export async function render(e,options){return renderer.render(e,{...options,...await sharedStage()});}
export async function browserSession(e,viewer,width,captions,action){
  return renderer.browserSession(e,viewer,width,captions,action,await sharedStage());
}

// Chromium launches in this worker, counted by test/support/one-browser.mjs.
export const launches=()=>globalThis.videomakerChromiumLaunches?.launched??0;
// A test that launches on purpose (the command line's path) declares it.
export function allowLaunches(count){globalThis.videomakerChromiumLaunches.allowed+=count;}
