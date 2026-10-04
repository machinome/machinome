// Layer 9: the take transport's boundary (the take-transport change;
// ADR-020). The transport is written to be moved to the viewer package at
// the migration, with its tests and nothing else, so its sources (every file
// under transport/ but its tests) import only files of the directory and the
// pose rule src/take.mjs: no package, nothing from the stage, nothing else
// from src/. Its tests may also import the test runner and the shared
// fixtures. And the pose rule's declaration, src/take.d.mts, declares
// exactly the functions src/take.mjs exports. Pure: it reads files.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {dirname,isAbsolute,join,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as poseRule from '../src/take.mjs';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const TRANSPORT=join(root,'transport'),POSE_RULE=join(root,'src','take.mjs'),FIXTURES=join(root,'fixtures');
const TEST_FILE=/\.test\.[cm]?[jt]sx?$/;
const inside=(base,path)=>{const rel=relative(base,path);return rel===''||(!isAbsolute(rel)&&rel!=='..'&&!rel.startsWith(`..${sep}`));};

// Every module specifier a source names: static imports and re-exports
// (`import … from`, `import '…'`, `export … from`, across lines), import()
// and require() of a literal; and `null` for an import() or require() of
// anything but a literal, which no reader can check.
export function specifiers(text){
  const out=[];
  for(const m of text.matchAll(/\b(?:import|export)\b[^'";]*?\bfrom\s*['"]([^'"]+)['"]|\bimport\s*['"]([^'"]+)['"]|\b(?:import|require)\s*\(\s*(?:['"]([^'"]+)['"]\s*\)|([^)\s]))/g))
    out.push(m[4]!==undefined?null:m[1]??m[2]??m[3]);
  return out;
}
// Why `file` (absolute, under transport/) may not name `spec`, or null.
export function refusal(file,spec){
  if(spec===null)return 'a module computed at run time, which the boundary cannot check';
  const test=TEST_FILE.test(file);
  if(test&&spec==='vitest')return null;
  if(!spec.startsWith('./')&&!spec.startsWith('../'))return test?'a package other than vitest':'a package';
  const target=resolve(dirname(file),spec);
  if(inside(TRANSPORT,target)||target===POSE_RULE)return null;
  if(test&&inside(FIXTURES,target))return null;
  if(inside(join(root,'stage'),target))return 'the stage';
  return `${relative(root,target).split(sep).join('/')}, which is neither the transport's nor the pose rule`;
}
async function files(dir,out=[]){
  for(const entry of (await readdir(dir,{withFileTypes:true})).sort((a,b)=>a.name<b.name?-1:1)){
    const path=join(dir,entry.name);
    if(entry.isDirectory())await files(path,out);else out.push(path);
  }
  return out;
}

test('every file of the take transport imports only its own files and the pose rule, and its tests also the runner and the fixtures',async()=>{
  const all=await files(TRANSPORT),names=all.map(f=>relative(TRANSPORT,f));
  for(const needed of ['viewer-handle.ts','take.ts','clock.ts','tsconfig.json'])assert.ok(names.includes(needed),`transport/${needed}`);
  const refused=[];
  for(const file of all)
    for(const spec of specifiers(await readFile(file,'utf8'))){
      const why=refusal(file,spec);
      if(why)refused.push(`transport/${relative(TRANSPORT,file)} imports ${spec===null?'import(<computed>)':JSON.stringify(spec)}: ${why}`);
    }
  assert.deepEqual(refused,[],'the take transport imports across its boundary');
});

test('the handle\'s types are declared, not imported, and the stage takes them from there',async()=>{
  const handle=await readFile(join(TRANSPORT,'viewer-handle.ts'),'utf8');
  assert.deepEqual(specifiers(handle),[],'viewer-handle.ts imports nothing');
  for(const name of ['Vec3','Rect','Bank','Vector','CameraView','MachineHandle','ViewerInstance','ViewerFactory'])
    assert.match(handle,new RegExp(`^export (?:type|interface) ${name}\\b`,'m'),`viewer-handle.ts declares ${name}`);
  assert.doesNotMatch(handle,/^export (?:const|let|var|function|class|default|enum)\b/m,'viewer-handle.ts holds no value');
  const runtime=await readFile(join(root,'stage','runtime.tsx'),'utf8');
  for(const name of ['MachineHandle','ViewerInstance','ViewerFactory'])
    assert.doesNotMatch(runtime,new RegExp(`^(?:export )?interface ${name}\\b`,'m'),`stage/runtime.tsx declares no ${name} of its own`);
  assert.match(runtime,/from '\.\.\/transport\/viewer-handle';/,'the runtime imports the handle from the transport');
  assert.match(await readFile(join(root,'stage','types.ts'),'utf8'),/from '\.\.\/transport\/viewer-handle';/,'the stage\'s types take Vec3, Rect and Bank from the transport');
});

test('the boundary check refuses a package, the stage and the rest of src/, by file and specifier, and admits the transport\'s own and the pose rule',()=>{
  const source=join(TRANSPORT,'take.ts'),unit=join(TRANSPORT,'take.test.ts');
  const check=(file,text)=>specifiers(text).map(spec=>[spec,refusal(file,spec)]);
  assert.deepEqual(check(source,"import {useState} from 'react';\nimport type {Rect} from '../stage/types';\nexport * from '../src/movie.mjs';\n"),
    [['react','a package'],['../stage/types','the stage'],['../src/movie.mjs','src/movie.mjs, which is neither the transport\'s nor the pose rule']]);
  assert.deepEqual(check(source,"import {\n  a,\n  b,\n} from 'react-dom';\nimport 'three';\nconst m=import('react');\nconst n=import(name);\nconst o=require('fs');\n"),
    [['react-dom','a package'],['three','a package'],['react','a package'],[null,'a module computed at run time, which the boundary cannot check'],['fs','a package']]);
  assert.deepEqual(check(source,"import {bankAt,type TakeDocument} from '../src/take.mjs';\nimport type {Bank} from './viewer-handle';\nexport {timerClock} from './clock';\n"),
    [['../src/take.mjs',null],['./viewer-handle',null],['./clock',null]]);
  assert.deepEqual(check(source,"import {test} from 'vitest';\nimport count from '../fixtures/documents/count.json';\n"),
    [['vitest','a package'],['../fixtures/documents/count.json','fixtures/documents/count.json, which is neither the transport\'s nor the pose rule']]);
  assert.deepEqual(check(unit,"import {test} from 'vitest';\nimport count from '../fixtures/documents/count.json';\nimport {render} from '../stage/runtime';\nimport {x} from 'jsdom';\n"),
    [['vitest',null],['../fixtures/documents/count.json',null],['../stage/runtime','the stage'],['jsdom','a package other than vitest']]);
});

test('src/take.d.mts declares exactly the functions src/take.mjs exports',async()=>{
  const declared=[...(await readFile(join(root,'src','take.d.mts'),'utf8')).matchAll(/^export function (\w+)\(/gm)].map(m=>m[1]).sort();
  const exported=Object.keys(poseRule).filter(name=>typeof poseRule[name]==='function').sort();
  assert.ok(exported.includes('bankAt'));
  assert.deepEqual(declared,exported,'the declaration and the module disagree on their functions');
  assert.deepEqual(Object.keys(poseRule).sort(),exported,'src/take.mjs exports functions only');
});
