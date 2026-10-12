// Writes render.instrumented.mjs beside this script: src/render.mjs of this
// worktree with its imports pointed back at src/, and timers around the
// page calls a frame makes (the stage's setFrame, the renderer's checks, the
// screenshots and compositions inside a transition). Every edit must match
// the original exactly once, so a changed renderer fails here instead of
// being measured with a stale patch. The original's sha256 is recorded.
//   node instrument.mjs
import {readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

const here=dirname(fileURLToPath(import.meta.url));
const original=resolve(here,'../../../../src/render.mjs');
let text=await readFile(original,'utf8');
const sha256=createHash('sha256').update(text).digest('hex');
const edits=[
  // Imports and the renderer's own directory point back at src/.
  [/from '\.\//g,"from '../../../../src/",'imports'],
  ["const here=dirname(fileURLToPath(import.meta.url));",
   "const here=resolve(dirname(fileURLToPath(import.meta.url)),'../../../../src');"],
  // Wart 1's ground, sidestepped: a manifest string naming a file the export
  // does not hold (the framework's pieces[].sources) is not served, instead
  // of failing the session. The Curta export's workaround link was moved
  // aside during this investigation; the viewer never reads those files.
  ["import {chromium} from 'playwright';",
   "import {chromium} from 'playwright';\nimport {existsSync} from 'node:fs';"],
  ["    const file=resolve(dirname(film.paths.manifest),asset);\n",
   "    const file=resolve(dirname(film.paths.manifest),asset);\n    if(!existsSync(file))continue;\n"],
  // The session takes a trace, launch flags and an init script.
  ["{browser:givenBrowser,assets:givenAssets,outputWidth=film.output.width}={}) {",
   "{browser:givenBrowser,assets:givenAssets,outputWidth=film.output.width,trace=null,launchArgs=CHROMIUM_ARGS,initScript=null}={}) {"],
  ["browser??=await chromium.launch({headless:true,args:CHROMIUM_ARGS});",
   "browser??=await chromium.launch({headless:true,args:launchArgs});"],
  ["page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});",
   "page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});\n    if(initScript)await page.addInitScript(initScript);"],
  // The stage's setFrame round trip, and the renderer's checks after it.
  ["const observed=await page.evaluate(f=>window.film.setFrame(f),{...request,...live,pictureOnly,fresh});\n      viewerApi??=await page.evaluate(()=>window.film.apiVersion);",
   "let __t=performance.now();\n      const observed=await page.evaluate(f=>window.film.setFrame(f),{...request,...live,pictureOnly,fresh});\n      trace?.add('setFrame',performance.now()-__t);\n      viewerApi??=await page.evaluate(()=>window.film.apiVersion);\n      __t=performance.now();"],
  ["        }else if(!(Math.abs(seen.opacity-reframe.progress)<=1e-3))\n          throw new Error(`Reframe fade differs from the timeline: ${name} (opacity ${seen.opacity} instead of ${reframe.progress})`);\n      }\n      return observed;",
   "        }else if(!(Math.abs(seen.opacity-reframe.progress)<=1e-3))\n          throw new Error(`Reframe fade differs from the timeline: ${name} (opacity ${seen.opacity} instead of ${reframe.progress})`);\n      }\n      trace?.add('checks',performance.now()-__t);\n      return observed;"],
  // Captures inside a frame: a fading mark's or picture's variants, and a
  // transition's same-instant pictures.
  ["pictures.push({src:png(await page.screenshot()),weight});",
   "{const __s=performance.now();const __b=await page.screenshot();trace?.add('innerScreenshot',performance.now()-__s);pictures.push({src:png(__b),weight});}"],
  ["return {src:png(await page.screenshot()),observed};",
   "const __s=performance.now();const __b=await page.screenshot();trace?.add('innerScreenshot',performance.now()-__s);\n      return {src:png(__b),observed};"],
  ["Object.assign(observed,await page.evaluate(r=>window.film.compose(r),{...request,pictureOnly}));",
   "{const __s=performance.now();Object.assign(observed,await page.evaluate(r=>window.film.compose(r),{...request,pictureOnly}));trace?.add('compose',performance.now()-__s);}"],
  ["Object.assign(observed,await page.evaluate(r=>window.film.composeMarkBlend(r),{pictures,pictureOnly:Boolean(options.pictureOnly)}));",
   "{const __s=performance.now();Object.assign(observed,await page.evaluate(r=>window.film.composeMarkBlend(r),{pictures,pictureOnly:Boolean(options.pictureOnly)}));trace?.add('compose',performance.now()-__s);}"],
];
for(const [from,to,label] of edits){
  if(from instanceof RegExp){
    const n=(text.match(from)??[]).length;
    if(!n)throw new Error(`No match for ${label}`);
    text=text.replace(from,to);continue;
  }
  const n=text.split(from).length-1;
  if(n!==1)throw new Error(`Expected one match, found ${n}: ${from.slice(0,80)}`);
  text=text.replace(from,()=>to);
}
const header=`// GENERATED by instrument.mjs from src/render.mjs sha256 ${sha256}.\n// An instrumented copy for the render-cost investigation; never imported by the tool.\n`;
await writeFile(resolve(here,'render.instrumented.mjs'),header+text);
console.log(`render.instrumented.mjs from src/render.mjs ${sha256}`);
