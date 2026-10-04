// The player page's build (the player-page change, design D2; ADR-022): the
// page `live` serves at /, its script and its stylesheet, bundled by the
// esbuild the stage build uses from player/ and the take transport it poses
// takes through, into <build>/player/. It is tool content: the same for every
// film, built once per session, reused while what it reads is unchanged.
//
//   buildPlayer(build)
//     build   the film's build directory; everything is written under
//             <build>/player/
//   -> {html, js, css (absolute paths of index.html, player.js, player.css),
//       htmlSha256, sha256 (of player.js), cssSha256, reused}
//
// Written under <build>/player/: index.html (the bytes of player/index.html),
// player.js (IIFE, no source maps, no legal comments), player.css (what
// player/index.ts imports), inputs.json ({key, inputs: [{path (a name),
// sha256}], htmlSha256, jsSha256, cssSha256, versions}).
//
// Names, not paths (ADR-013's rule): every file the bundle names is named by
// the tool, `videomaker/player/<file>`, `videomaker/transport/<file>` or
// `videomaker/src/<file>`, through the stage build's own rewriting of
// esbuild's names, so the bytes never depend on where the tool or the build
// directory lies. The key is the SHA-256 of every file under player/ and
// transport/ but their tests and of the pose rule src/take.mjs, each under its
// name, and esbuild's version: the player's imports are held to those files
// by a repository test (test/transport-boundary.test.mjs), so the key covers
// every input. An equal key whose files still hash as recorded is reused;
// never an mtime.
import {mkdir,readFile,readdir,realpath,rm,writeFile} from 'node:fs/promises';
import {dirname,extname,isAbsolute,join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as esbuild from 'esbuild';
import {renameOutput} from './stage-build.mjs';
import {hash,json} from './util.mjs';

const TOOL=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const PLAYER=join(TOOL,'player'),TRANSPORT=join(TOOL,'transport'),SOURCE=join(TOOL,'src');
const POSE_RULE=join(SOURCE,'take.mjs');
const ROOTS=[[PLAYER,'videomaker/player'],[TRANSPORT,'videomaker/transport'],[SOURCE,'videomaker/src']];
const TEST_FILE=/\.test\.[cm]?[jt]sx?$/;

const inside=(base,path)=>{const rel=relative(base,path);return rel===''||(!isAbsolute(rel)&&rel!=='..'&&!rel.startsWith('../'));};
const readOrNull=async path=>{try{return await readFile(path);}catch(error){if(error.code==='ENOENT')return null;throw error;}};
const sha=async path=>{const bytes=await readOrNull(path);return bytes===null?null:hash(bytes);};

// Every file the player can read, but tests, each with its name by the tool.
async function playerSources(){
  const files=[];
  async function walk(dir,prefix){
    for(const entry of await readdir(dir,{withFileTypes:true})){
      const path=join(dir,entry.name);
      if(entry.isDirectory())await walk(path,`${prefix}/${entry.name}`);
      else if(!TEST_FILE.test(entry.name))files.push({file:path,name:`${prefix}/${entry.name}`});
    }
  }
  await walk(PLAYER,'videomaker/player');
  await walk(TRANSPORT,'videomaker/transport');
  files.push({file:POSE_RULE,name:'videomaker/src/take.mjs'});
  return files.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
}

async function key(){
  const inputs=[];
  for(const {file,name} of await playerSources())inputs.push({path:name,sha256:await sha(file)});
  const versions={esbuild:esbuild.version};
  return {key:hash(JSON.stringify({inputs,versions})),inputs,versions};
}

export async function buildPlayer(build){
  if(!build)throw new Error('buildPlayer needs a build directory');
  const out=resolve(build,'player'),files={html:join(out,'index.html'),js:join(out,'player.js'),css:join(out,'player.css'),
    record:join(out,'inputs.json')};
  const {key:wanted,inputs,versions}=await key();
  const result=(record,reused)=>({html:files.html,js:files.js,css:files.css,htmlSha256:record.htmlSha256,sha256:record.jsSha256,
    cssSha256:record.cssSha256,reused});
  const recorded=await readOrNull(files.record).then(b=>b&&JSON.parse(String(b))).catch(()=>null);
  if(recorded?.key===wanted&&await sha(files.html)===recorded.htmlSha256&&await sha(files.js)===recorded.jsSha256&&
    await sha(files.css)===recorded.cssSha256)
    return result(recorded,true);

  await mkdir(out,{recursive:true});
  await rm(files.record,{force:true});
  let built;
  try{
    built=await esbuild.build({entryPoints:[join(PLAYER,'index.ts')],bundle:true,format:'iife',outfile:files.js,write:false,
      platform:'browser',target:'es2022',sourcemap:false,legalComments:'none',metafile:true,absWorkingDir:out,logLevel:'silent'});
  }catch(error){
    const messages=(error.errors??[]).map(e=>`${e.location?`${e.location.file}:${e.location.line}:${e.location.column}: `:''}${e.text}`);
    throw new Error(`The player does not build:\n${messages.join('\n')||error.message}`);
  }
  // esbuild's names, relative to the output directory through this machine's
  // directories, replaced by the tool's before anything is written.
  const outReal=await realpath(out),roots=await Promise.all(ROOTS.map(async([dir,prefix])=>[await realpath(dir),prefix]));
  const renames=new Map();
  for(const name of Object.keys(built.metafile.inputs)){
    const file=resolve(outReal,name),root=roots.find(([dir])=>inside(dir,file));
    if(!root)throw new Error(`The player read ${name}, which is neither the player's, the take transport's nor the pose rule`);
    renames.set(name,`${root[1]}/${relative(root[0],file)}`);
  }
  for(const output of built.outputFiles){
    const kind=extname(output.path)==='.css'?'css':'js';
    await writeFile(output.path,renameOutput(output.text,kind,renames));
  }
  if(await readOrNull(files.css)===null)await writeFile(files.css,'');
  await writeFile(files.html,await readFile(join(PLAYER,'index.html')));
  const record={key:wanted,inputs,htmlSha256:await sha(files.html),jsSha256:await sha(files.js),cssSha256:await sha(files.css),versions};
  await json(files.record,record);
  return result(record,false);
}
