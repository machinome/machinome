// One stage bundle per movie (design D7): the tool's React stage runtime
// (`stage/`) and the movie's stage modules, bundled by esbuild into one script
// and one stylesheet, with the movie's types generated from its stage block
// and TypeScript modules checked against them.
//
//   buildStage({root, modules, stageBlock, build, project?})
//     root        absolute directory the module paths are relative to (the
//                 document's `root`; a YAML episode passes any directory and
//                 no modules)
//     modules     the document's `stage.modules`: paths relative to `root`,
//                 .ts, .tsx, .js or .jsx; [] or undefined bundles the runtime
//                 alone
//     stageBlock  the document's `stage` block ({modules, sets, elements});
//                 the types are generated from it and it enters the key
//     build       the build directory; everything is written under
//                 `<build>/stage/`
//     project     the repository every module must lie inside (default: root)
//   -> {js, css, dts (absolute paths of stage.js, stage.css, movie.d.ts),
//       sha256 (of stage.js), cssSha256, reused, typechecked,
//       modules: [{path (as given), file (absolute), sha256}]}
//
// Written under <build>/stage/: entry.tsx (imports the runtime, each module in
// order, then boots), stage.js (IIFE, production React, no source maps),
// stage.css (every imported stylesheet; empty when none), movie.d.ts,
// tsconfig.json (for `tsc --noEmit`), metafile.json (esbuild's, with this
// machine's paths) and inputs.json ({key, inputs: [{path (a name), sha256}],
// bundleSha256, cssSha256, dtsSha256, typechecked, versions}).
//
// Names, not paths (ADR-013): every file the bundle names is named by the tool
// or the project repository, never by the machine's directories, so the same
// tool content and project content bundle to the same bytes from any checkout
// and any copy of the project. A file in the output directory keeps esbuild's
// name (`entry.tsx`); the runtime is `videomaker/stage/<file>`, the take
// transport the runtime poses a take through `videomaker/transport/<file>` and
// the pose rule it imports `videomaker/src/<file>` (ADR-020), the tool's
// packages `videomaker/node_modules/<file>`, a project file `project/<path in
// the repository>`; anything else keeps esbuild's name, relative to the output
// directory. esbuild prints its own names, relative to the output directory
// through the checkout, in three places, and the outputs are rewritten there
// before they are written: a `// <name>` line before each module, a wrapper's
// `"<name>"(…) {` line for each CommonJS or lazily initialised module, and a
// `/* <name> */` line before each stylesheet.
//
// The key is the SHA-256 of the runtime's sources (every file under stage/
// and transport/ but their tests: the take transport's types reach a
// project's type check through videomaker/stage even where esbuild drops
// them), each module's bytes, every input the previous build read (so a
// module's own imports count, the pose rule among them), each under its
// name, the stage block, and the versions of esbuild, TypeScript and React.
// An equal key whose outputs still hash as recorded is reused without
// building; never an mtime, never a path of the machine, so a second checkout
// reuses the first one's bundle.
import {execFile} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {mkdir,readFile,readdir,realpath,rm,stat,writeFile} from 'node:fs/promises';
import {dirname,extname,isAbsolute,join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as esbuild from 'esbuild';
import {hash,json} from './util.mjs';

const TOOL=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const STAGE=join(TOOL,'stage');
const TRANSPORT=join(TOOL,'transport');
const SOURCE=join(TOOL,'src');
const NODE_MODULES=join(TOOL,'node_modules');
// The tool's directories whose files the bundle names by the tool, and how.
const TOOL_ROOTS=[[STAGE,'videomaker/stage'],[TRANSPORT,'videomaker/transport'],[SOURCE,'videomaker/src']];
const EXTENSIONS=new Set(['.ts','.tsx','.js','.jsx']);
const TYPED=new Set(['.ts','.tsx']);

const inside=(base,path)=>{const rel=relative(base,path);return rel===''||(!isAbsolute(rel)&&rel!=='..'&&!rel.startsWith('../'));};
const readOrNull=async path=>{try{return await readFile(path);}catch(error){if(error.code==='ENOENT')return null;throw error;}};
const sha=async path=>{const bytes=await readOrNull(path);return bytes===null?null:hash(bytes);};

/**
 * Every source of the runtime (stage/ and the take transport it poses a take
 * through, transport/; tests excluded), sorted, each with its name by the
 * tool.
 */
export async function runtimeSources(){
  const files=[];
  async function walk(dir,prefix){
    for(const entry of await readdir(dir,{withFileTypes:true})){
      const path=join(dir,entry.name);
      if(entry.isDirectory())await walk(path,`${prefix}/${entry.name}`);
      else if(!/\.test\.[cm]?[jt]sx?$/.test(entry.name))files.push({file:path,name:`${prefix}/${entry.name}`});
    }
  }
  await walk(STAGE,'videomaker/stage');
  await walk(TRANSPORT,'videomaker/transport');
  return files.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
}

export function versions(){
  const version=name=>JSON.parse(readFileSync(join(NODE_MODULES,name,'package.json'),'utf8')).version;
  return {esbuild:esbuild.version,typescript:version('typescript'),react:version('react'),reactDom:version('react-dom')};
}

// ----- movie.d.ts -----

const pascal=kind=>kind.split(/[^A-Za-z0-9]+/).filter(Boolean).map(w=>w[0].toUpperCase()+w.slice(1)).join('');
const key=name=>JSON.stringify(name);
function valueType(value){
  if(typeof value==='string')return 'string';
  if(typeof value==='number')return 'number';
  if(typeof value==='boolean')return 'boolean';
  if(Array.isArray(value))return 'unknown[]';
  if(value===null)return 'null';
  return 'Record<string, unknown>';
}
const PROP_KINDS={string:'string',number:'number',boolean:'boolean',list:'unknown[]',object:'Record<string, unknown>'};
const PARAM_KINDS={string:'string',number:'number',boolean:'boolean'};

/** The TypeScript declarations of a stage block: `videomaker/movie`. */
export function movieTypes(stageBlock){
  const sets=stageBlock?.sets??{},elements=stageBlock?.elements??{},names=new Map(),lines=[];
  const claim=(name,subject)=>{
    if(names.has(name))throw new Error(`Stage types: ${subject} and ${names.get(name)} both generate the type ${name}`);
    names.set(name,subject);return name;
  };
  lines.push('// Generated by videomaker from the movie\'s stage block. Do not edit.',
    "import type {ProjectElementState} from 'videomaker/stage';",'');
  const setEntries=[],elementEntries=[];
  for(const [kind,set] of Object.entries(sets)){
    const base=pascal(kind),slot=claim(`${base}Slot`,`set ${kind}`),props=claim(`${base}Props`,`set ${kind}`);
    const slots=set.slots??[];
    if(!slots.length)throw new Error(`Stage types: set ${kind} declares no slots`);
    lines.push(`export type ${slot} = ${slots.map(key).join(' | ')};`);
    lines.push(`export interface ${props} {`,...Object.entries(set.props??{}).map(([name,value])=>`  ${key(name)}: ${valueType(value)};`),'}','');
    setEntries.push(`    ${key(kind)}: {slot: ${slot}; props: ${props}};`);
  }
  for(const [kind,element] of Object.entries(elements)){
    const base=pascal(kind),props=claim(`${base}Props`,`element ${kind}`),actions=claim(`${base}Actions`,`element ${kind}`),
      state=claim(`${base}State`,`element ${kind}`);
    lines.push(`export interface ${props} {`,...Object.entries(element.props??{}).map(([name,kindOf])=>{
      const type=PROP_KINDS[kindOf];
      if(!type)throw new Error(`Stage types: element ${kind} prop ${name} has unknown kind ${kindOf}`);
      return `  ${key(name)}: ${type};`;
    }),'}');
    const shapes=Object.entries(element.actions??{}).map(([action,params])=>`{action: ${key(action)}; params: {${
      Object.entries(params??{}).map(([name,kindOf])=>{
        const type=PARAM_KINDS[kindOf];
        if(!type)throw new Error(`Stage types: element ${kind} action ${action} parameter ${name} has unknown kind ${kindOf}`);
        return `${key(name)}: ${type}`;
      }).join('; ')}}}`);
    lines.push(`export type ${actions} = ${shapes.length?shapes.join(' | '):'never'};`);
    lines.push(`export type ${state} = ProjectElementState<${props}, ${actions}>;`,'');
    elementEntries.push(`    ${key(kind)}: {props: ${props}; actions: ${actions}};`);
  }
  lines.push("declare module 'videomaker/stage' {",'  interface MovieSets {',...setEntries,'  }',
    '  interface MovieElements {',...elementEntries,'  }','}','');
  return lines.join('\n');
}

/** The tsconfig under which `tsc --noEmit` checks the typed modules against movie.d.ts. */
export function stageTsconfig(typedModules){
  const types=(...p)=>join(NODE_MODULES,'@types',...p);
  return {
    compilerOptions:{
      strict:true,noEmit:true,target:'es2022',module:'esnext',moduleResolution:'bundler',jsx:'react-jsx',
      lib:['es2022','dom','dom.iterable'],types:[],skipLibCheck:true,isolatedModules:true,
      paths:{
        'videomaker/stage':[join(STAGE,'index.ts')],
        'videomaker/movie':['./movie.d.ts'],
        react:[types('react','index.d.ts')],
        'react/jsx-runtime':[types('react','jsx-runtime.d.ts')],
        'react-dom':[types('react-dom','index.d.ts')],
        'react-dom/client':[types('react-dom','client.d.ts')],
      },
    },
    files:['./movie.d.ts',join(STAGE,'css.d.ts'),...typedModules],
  };
}

function tsc(project,cwd){
  return new Promise(resolvePromise=>{
    execFile(join(NODE_MODULES,'.bin','tsc'),['--noEmit','--pretty','false','-p',project],{cwd,maxBuffer:16<<20},
      (error,stdout,stderr)=>resolvePromise({ok:!error,output:`${stdout}${stderr}`.trim()}));
  });
}

async function checkModules(root,project,modules){
  const base=await realpath(project).catch(()=>{throw new Error(`Stage project directory does not exist: ${project}`);});
  const checked=[];
  for(const path of modules){
    if(typeof path!=='string'||!path)throw new Error(`Stage module ${JSON.stringify(path)} is not a path`);
    const ext=extname(path).toLowerCase();
    if(!EXTENSIONS.has(ext))throw new Error(`Stage module ${path} is not TypeScript or JavaScript (.ts, .tsx, .js, .jsx)`);
    const absolute=resolve(root,path);
    let file;
    try{file=await realpath(absolute);if(!(await stat(file)).isFile())throw Object.assign(new Error(),{code:'ENOENT'});}
    catch(error){if(error.code==='ENOENT'||error.code==='ENOTDIR')throw new Error(`Stage module ${path} does not exist (${absolute})`);throw error;}
    if(!inside(base,file))throw new Error(`Stage module ${path} is outside the project (${project})`);
    checked.push({path,file,typed:TYPED.has(ext),sha256:hash(await readFile(file))});
  }
  return checked;
}

// ----- names (ADR-013) -----

const realOr=path=>realpath(path).catch(()=>resolve(path));

/** The names of one build: a bundled file by the root it lies in, and back. */
async function buildNames(out,project){
  // esbuild names files by their real paths relative to the real output
  // directory; a worktree's node_modules is a link to another checkout's.
  const outReal=await realOr(out);
  const roots=[...await Promise.all(TOOL_ROOTS.map(async([dir,prefix])=>[await realOr(dir),prefix])),
    [await realOr(NODE_MODULES),'videomaker/node_modules'],[await realOr(project),'project']];
  const nameOf=file=>{
    if(inside(outReal,file))return relative(outReal,file);
    for(const [root,prefix] of roots)if(inside(root,file))return `${prefix}/${relative(root,file)}`;
    return relative(outReal,file);
  };
  const fileOf=name=>{
    for(const [root,prefix] of roots)if(name.startsWith(`${prefix}/`))return join(root,name.slice(prefix.length+1));
    return resolve(outReal,name);
  };
  return {
    nameOf,fileOf,
    // A file of the output directory is generated from the inputs (the entry
    // holds this checkout's absolute paths): never a key input.
    generated:name=>inside(outReal,fileOf(name)),
    // esbuild's name for a file (relative to the output directory) -> ours.
    renamed:esbuildName=>nameOf(resolve(outReal,esbuildName)),
  };
}

// A JavaScript string literal as esbuild prints a name: either quote, and the
// escapes it writes for a character outside ASCII.
const ESCAPES={n:'\n',r:'\r',t:'\t',b:'\b',f:'\f',v:'\v',0:'\0'};
const unquote=literal=>literal.slice(1,-1).replace(/\\(?:u\{([0-9a-fA-F]+)\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2})|([^]))/g,
  (_,point,unit,byte,char)=>point?String.fromCodePoint(parseInt(point,16)):unit?String.fromCharCode(parseInt(unit,16)):
    byte?String.fromCharCode(parseInt(byte,16)):ESCAPES[char]??char);
const quote=name=>JSON.stringify(name).replace(/[^\x00-\x7e]/g,c=>`\\u${c.charCodeAt(0).toString(16).padStart(4,'0')}`);
const JS_COMMENT=/^(\s*)\/\/ (.+)$/,JS_WRAPPER=/^(\s*)("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')(\([^()]*\) \{)$/,CSS_COMMENT=/^\/\* (.+) \*\/$/;

/** An output of esbuild with each name it printed replaced by ours (design D2). */
export function renameOutput(text,kind,names){
  const ours=name=>names.has(name)?names.get(name):null;
  return text.split('\n').map(line=>{
    let m;
    if(kind==='css'){
      if((m=CSS_COMMENT.exec(line))&&ours(m[1])!==null)return `/* ${ours(m[1])} */`;
      return line;
    }
    if((m=JS_COMMENT.exec(line))&&ours(m[2])!==null)return `${m[1]}// ${ours(m[2])}`;
    if((m=JS_WRAPPER.exec(line))&&ours(unquote(m[2]))!==null)return `${m[1]}${quote(ours(unquote(m[2])))}${m[3]}`;
    return line;
  }).join('\n');
}

async function computeKey({names,runtime,modules,previous,stageBlock,versions:v}){
  const inputs=[],seen=new Set();
  const add=async(name,file,sha256)=>{
    if(seen.has(name)||names.generated(name))return;
    seen.add(name);inputs.push({path:name,sha256:sha256??await sha(file)});
  };
  for(const {file,name} of runtime)await add(name,file);
  for(const m of modules)await add(names.nameOf(m.file),m.file,m.sha256);
  for(const name of [...previous].sort())await add(name,names.fileOf(name));
  const key=hash(JSON.stringify({inputs,modules:modules.map(m=>m.path),stageBlock:stageBlock??null,versions:v}));
  return {key,inputs};
}

export async function buildStage({root,modules=[],stageBlock=null,build,project=root}){
  if(!root||!isAbsolute(root))throw new Error('buildStage needs an absolute root');
  if(!build)throw new Error('buildStage needs a build directory');
  const out=resolve(build,'stage'),files={
    entry:join(out,'entry.tsx'),js:join(out,'stage.js'),css:join(out,'stage.css'),dts:join(out,'movie.d.ts'),
    tsconfig:join(out,'tsconfig.json'),metafile:join(out,'metafile.json'),record:join(out,'inputs.json')};
  const checked=await checkModules(root,project,modules??[]);
  const typed=checked.filter(m=>m.typed);
  const runtime=await runtimeSources(),v=versions();
  const dts=movieTypes(stageBlock);
  const result=(record,reused)=>({js:files.js,css:files.css,dts:files.dts,sha256:record.bundleSha256,cssSha256:record.cssSha256,
    reused,typechecked:record.typechecked,modules:checked.map(({path,file,sha256})=>({path,file,sha256}))});

  // Reuse: the key over the previous build's inputs, by their names, read from
  // this checkout; and outputs as recorded.
  const recorded=await readOrNull(files.record).then(b=>b&&JSON.parse(String(b))).catch(()=>null);
  if(recorded&&Array.isArray(recorded.inputs)){
    const names=await buildNames(out,project);
    const {key}=await computeKey({names,runtime,modules:checked,previous:recorded.inputs.map(i=>i.path),stageBlock,versions:v});
    if(key===recorded.key&&(!typed.length||recorded.typechecked)&&
      await sha(files.js)===recorded.bundleSha256&&await sha(files.css)===recorded.cssSha256&&
      await sha(files.dts)===recorded.dtsSha256)
      return result(recorded,true);
  }

  await mkdir(out,{recursive:true});
  await rm(files.record,{force:true});
  const entry=['// Generated by videomaker: the movie\'s stage bundle entry. Do not edit.',
    `import {boot} from ${JSON.stringify(join(STAGE,'runtime.tsx'))};`,
    ...checked.map(m=>`import ${JSON.stringify(m.file)};`),
    'void boot();',''].join('\n');
  await writeFile(files.entry,entry);
  await writeFile(files.dts,dts);
  await writeFile(files.tsconfig,JSON.stringify(stageTsconfig(typed.map(m=>m.file)),null,2)+'\n');

  if(typed.length){
    const {ok,output}=await tsc(files.tsconfig,out);
    if(!ok){
      const named=typed.filter(m=>output.includes(m.file)||output.includes(relative(out,m.file)));
      const subjects=(named.length?named:typed).map(m=>m.path);
      throw new Error(`Stage module${subjects.length>1?'s':''} ${subjects.join(', ')} ${subjects.length>1?'do':'does'} not type-check against the movie's stage block:\n${output}`);
    }
  }

  await rm(files.css,{force:true});
  let built;
  try{
    built=await esbuild.build({
      entryPoints:[files.entry],bundle:true,format:'iife',outfile:files.js,write:false,platform:'browser',
      target:'es2022',define:{'process.env.NODE_ENV':'"production"'},sourcemap:false,legalComments:'none',
      jsx:'automatic',nodePaths:[NODE_MODULES],alias:{'videomaker/stage':join(STAGE,'index.ts')},
      metafile:true,absWorkingDir:out,logLevel:'silent',
    });
  }catch(error){
    const messages=(error.errors??[]).map(e=>`${e.location?`${e.location.file}:${e.location.line}:${e.location.column}: `:''}${e.text}`);
    const named=checked.filter(m=>messages.some(t=>t.includes(m.file)||t.includes(relative(out,m.file))));
    throw new Error(`The stage bundle does not build${named.length?` (stage module ${named.map(m=>m.path).join(', ')})`:''}:\n${messages.join('\n')||error.message}`);
  }
  // esbuild's names through this machine's directories, replaced by ours
  // before anything is written.
  const names=await buildNames(out,project),esbuildNames=Object.keys(built.metafile.inputs);
  const renames=new Map(esbuildNames.map(name=>[name,names.renamed(name)]).filter(([from,to])=>from!==to));
  for(const output of built.outputFiles){
    const kind=extname(output.path)==='.css'?'css':extname(output.path)==='.js'?'js':null;
    await writeFile(output.path,kind?renameOutput(output.text,kind,renames):output.contents);
  }
  if(await readOrNull(files.css)===null)await writeFile(files.css,'');
  await json(files.metafile,built.metafile);
  const {key,inputs}=await computeKey({names,runtime,modules:checked,previous:esbuildNames.map(names.renamed),stageBlock,versions:v});
  const record={key,inputs,bundleSha256:await sha(files.js),cssSha256:await sha(files.css),dtsSha256:await sha(files.dts),
    typechecked:typed.length>0,versions:v};
  await json(files.record,record);
  return result(record,false);
}

// The bundle of a loaded film: a movie's modules relative to its root and
// inside its project repository; a YAML episode's runtime alone.
export async function buildFilmStage(film){
  const root=film.paths.base??dirname(film.paths.production);
  return buildStage({root,modules:film.stage.modules??[],stageBlock:film.stage,build:film.paths.build,
    project:film.paths.repository??root});
}
