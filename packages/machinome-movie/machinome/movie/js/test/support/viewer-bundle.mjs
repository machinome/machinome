// The gate of the viewer layer (layer 6; ADR-008): the real viewer is proved
// through a bundle the maintainer selects by path in the environment,
// VIDEOMAKER_VIEWER_BUNDLE, never assumed. No path to a bundle is written in
// the repository.
//
// A test of test/viewer/ is declared with viewerTest(name, fn): unset (or
// empty), it is skipped with the note "no viewer bundle selected" before the
// memo is consulted, so a skip is never recorded nor reported as a pass; a
// path with no file fails, naming it; otherwise the memo decides (the bundle's
// bytes are in the key, test/support/reach.mjs), and a run first loads the
// bundle into a blank page and fails, naming the path, when it does not
// define MachinomeViewer. `fn(context, bundle)` receives the absolute path.
// Not a test file: it registers no tests.
import {readFile,stat} from 'node:fs/promises';
import {resolve} from 'node:path';
import {gatedSlowTest} from './memo.mjs';

export const BUNDLE_VARIABLE='VIDEOMAKER_VIEWER_BUNDLE';
export const NOT_SELECTED='no viewer bundle selected';

// The selected bundle's absolute path, or null when none is selected.
export async function selectedBundle(env=process.env){
  const value=env[BUNDLE_VARIABLE];
  if(!value)return null;
  const path=resolve(value);
  const file=await stat(path).then(s=>s.isFile(),()=>false);
  if(!file)throw new Error(`The selected viewer bundle ${path} does not exist (${BUNDLE_VARIABLE})`);
  return path;
}

// Loads the bundle into a blank page of the run's Chromium; refuses, naming
// the path, a script that does not define MachinomeViewer with a mount.
const verified=new Map();
export async function definesViewer(path){
  const text=await readFile(path,'utf8');
  if(verified.get(path)===text)return;
  const {sharedStage}=await import('./stage.mjs');
  const {browser}=await sharedStage();
  const page=await browser.newPage();
  let defined=false;
  try{
    await page.setContent('<!doctype html><html><body></body></html>');
    await page.addScriptTag({content:text}).catch(()=>{});
    defined=await page.evaluate(()=>typeof window.MachinomeViewer?.mount==='function');
  }finally{await page.close();}
  if(!defined)throw new Error(`The selected viewer bundle ${path} does not define MachinomeViewer (${BUNDLE_VARIABLE})`);
  verified.set(path,text);
}

// The API the movie needs, asserted from what a mounted instance declares.
export function assertViewerApi(path,declared,required){
  if(!(typeof declared==='number'&&declared>=required))
    throw new Error(`The selected viewer bundle ${path} declares Viewer API ${declared}; the fixture movie needs ${required} (${BUNDLE_VARIABLE})`);
}

// A slow test of the viewer layer.
const gated=gatedSlowTest(async context=>{
  const path=await selectedBundle();
  if(!path)context.skip(NOT_SELECTED);
  return path;
});
export function viewerTest(name,fn,options){
  return gated(name,async(context,path)=>{await definesViewer(path);return fn(context,path);},options);
}
