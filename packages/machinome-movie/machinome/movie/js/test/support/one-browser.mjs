// Setup file of the slow project: a browser test never launches its own
// Chromium. Counts chromium.launch in the worker and fails the file when it
// launched more than its tests declared (allowLaunches in stage.mjs). Command
// line runs in child processes launch their own, as the command line must.
import {afterAll} from 'vitest';
import {chromium} from 'playwright';

const counts=globalThis.videomakerChromiumLaunches??={launched:0,allowed:0};
if(!chromium.launch.videomakerCounted){
  const launch=chromium.launch;
  const counted=async function(...args){counts.launched++;return launch.apply(this,args);};
  counted.videomakerCounted=true;
  chromium.launch=counted;
}
afterAll(()=>{
  if(counts.launched>counts.allowed)
    throw new Error(`A browser test launched its own Chromium (${counts.launched-counts.allowed} undeclared); `+
      'take preview, render and browserSession from test/support/stage.mjs');
});
