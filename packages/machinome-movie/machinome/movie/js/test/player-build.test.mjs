// Layer 9 (pure, Node; esbuild, no browser): the player's build (the
// player-page change, design D2). `live` builds the page once per session
// into the film's _build/player/, as tool content: every file it embeds is
// named by the tool, so two checkouts building into two build directories at
// different places write the same bytes; it is reused while what it reads is
// unchanged and its files hash as recorded, and rebuilt when one does not.
// In a temporary directory outside the repository.
import {cp,mkdtemp,readFile,realpath,rm,symlink,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {afterAll,beforeAll,expect,test} from 'vitest';
import {buildPlayer} from '../src/player-build.mjs';

const TOOL=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
let work='';
beforeAll(async()=>{work=await mkdtemp(join(tmpdir(),'videomaker-player-'));});
afterAll(async()=>{if(work)await rm(work,{recursive:true,force:true});});

// A second checkout: the tool's src/, player/, transport/ and package.json
// copied elsewhere, its node_modules a link to this checkout's, as a
// worktree's is.
let otherCheckout=null;
const elsewhere=()=>otherCheckout??=(async()=>{
  const other=join(work,'other-checkout');
  for(const entry of ['src','player','transport','package.json'])await cp(join(TOOL,entry),join(other,entry),{recursive:true});
  await symlink(await realpath(join(TOOL,'node_modules')),join(other,'node_modules'));
  return import(pathToFileURL(join(other,'src','player-build.mjs')).href);
})();

test('two checkouts build the player into build directories at different places to the same bytes, every file named by the tool',async()=>{
  const near=join(work,'near','_build'),far=join(work,'far','deeper','still','_build');
  const first=await buildPlayer(near),second=await (await elsewhere()).buildPlayer(far);
  expect([first.reused,second.reused]).toEqual([false,false]);
  for(const kind of ['html','js','css'])
    expect((await readFile(second[kind])).equals(await readFile(first[kind])),`${kind} differs`).toBe(true);
  expect([first.html,first.js,first.css]).toEqual(['index.html','player.js','player.css'].map(name=>join(near,'player',name)));
  expect(await readFile(first.html,'utf8')).toBe(await readFile(join(TOOL,'player','index.html'),'utf8'));
  const js=await readFile(first.js,'utf8'),css=await readFile(first.css,'utf8');
  for(const text of [js,css]){
    for(const machine of [TOOL,await realpath(TOOL),work,await realpath(work)])expect(text).not.toContain(machine.slice(1));
    expect(text).not.toMatch(/^\s*(\/\/|\/\*|["']) ?\.\.\//m);
  }
  // The page, the take transport, and the pose rule the take surface poses by.
  expect(js).toMatch(/^ {2}\/\/ videomaker\/player\/index\.ts$/m);
  expect(js).toMatch(/^ {2}\/\/ videomaker\/transport\/take\.ts$/m);
  expect(js).toMatch(/^ {2}\/\/ videomaker\/transport\/clock\.ts$/m);
  expect(js).toMatch(/^ {2}\/\/ videomaker\/src\/take\.mjs$/m);
  expect(css).toMatch(/^\/\* videomaker\/player\/player\.css \*\/$/m);
  expect([first.sha256,first.cssSha256,first.htmlSha256]).toEqual([sha(await readFile(first.js)),sha(await readFile(first.css)),sha(await readFile(first.html))]);
  // The record the key is computed over names its inputs by the tool, tests left out.
  const names=JSON.parse(await readFile(join(near,'player','inputs.json'),'utf8')).inputs.map(i=>i.path);
  for(const name of ['videomaker/player/index.ts','videomaker/player/index.html','videomaker/player/player.css','videomaker/player/model.ts',
    'videomaker/transport/take.ts','videomaker/src/take.mjs'])expect(names).toContain(name);
  expect(names.filter(name=>/\.test\./.test(name)||!name.startsWith('videomaker/'))).toEqual([]);
},120_000);

test('the player is reused while its inputs are unchanged, and rebuilt when one of its files does not hash as recorded',async()=>{
  const build=join(work,'reuse','_build');
  const first=await buildPlayer(build),again=await buildPlayer(build);
  expect([first.reused,again.reused]).toEqual([false,true]);
  expect([again.sha256,again.cssSha256,again.htmlSha256]).toEqual([first.sha256,first.cssSha256,first.htmlSha256]);
  // Another checkout's key is the same: it reuses this one's build.
  expect((await (await elsewhere()).buildPlayer(build)).reused).toBe(true);
  await writeFile(first.js,'// damaged\n');
  const rebuilt=await buildPlayer(build);
  expect(rebuilt.reused).toBe(false);
  expect(sha(await readFile(rebuilt.js))).toBe(first.sha256);
  await rm(first.css);
  expect((await buildPlayer(build)).reused).toBe(false);
},120_000);
