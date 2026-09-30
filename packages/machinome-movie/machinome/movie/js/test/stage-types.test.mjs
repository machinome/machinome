// Layer 4 (pure, Node): the stage runtime compiles under `tsc --noEmit` (strict), and a movie's
// generated types check its stage modules: the fixture tour's template
// compiles against the types generated from its document's stage block, and a
// module whose slot, prop or action parameter differs is refused naming it.
// Also the bundle's reuse and its refusals (src/stage-build.mjs), in a
// temporary directory outside the repository.
import {execFile} from 'node:child_process';
import {cp,mkdtemp,readFile,rm,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {afterAll,beforeAll,describe,expect,test} from 'vitest';
import {buildStage,movieTypes} from '../src/stage-build.mjs';

const TOOL=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const TOUR=join(TOOL,'python/tests/fixtures/project/videos/tour');
let work='';
let stageBlock;

beforeAll(async()=>{
  work=await mkdtemp(join(tmpdir(),'videomaker-stage-'));
  stageBlock=JSON.parse(await readFile(join(TOOL,'fixtures/documents/tour.json'),'utf8')).stage;
  await cp(TOUR,join(work,'project'),{recursive:true});
});
afterAll(async()=>{if(work)await rm(work,{recursive:true,force:true});});

const run=(args,cwd)=>new Promise(done=>
  execFile(join(TOOL,'node_modules/.bin/tsc'),args,{cwd},(error,stdout,stderr)=>done({code:error?1:0,output:stdout+stderr})));

describe('types',()=>{
  test('the runtime compiles strictly: tsc --noEmit -p stage/tsconfig.json',async()=>{
    const {code,output}=await run(['--noEmit','--pretty','false','-p','stage/tsconfig.json'],TOOL);
    expect(output).toBe('');
    expect(code).toBe(0);
  });
  test('the tour template compiles against the types generated from its stage block, and the bundle is then reused',async()=>{
    const root=join(work,'project');
    const first=await buildStage({root,modules:stageBlock.modules,stageBlock,build:join(work,'build')});
    expect(first).toMatchObject({reused:false,typechecked:true});
    const dts=await readFile(first.dts,'utf8');
    expect(dts).toBe(movieTypes(stageBlock));
    expect(dts).toContain('export type PlaybillSlot = "stage" | "plate" | "headline" | "aside";');
    expect(dts).toContain('export type TallyActions = {action: "light"; params: {"item": string}};');
    expect(dts).toContain('"playbill-split": {slot: PlaybillSplitSlot; props: PlaybillSplitProps};');
    const again=await buildStage({root,modules:stageBlock.modules,stageBlock,build:join(work,'build')});
    expect(again).toMatchObject({reused:true,typechecked:true,sha256:first.sha256,cssSha256:first.cssSha256});
    // A module's own import is an input: a changed stylesheet rebuilds.
    await writeFile(join(root,'stage.css'),(await readFile(join(root,'stage.css'),'utf8'))+'\n.tally{outline:0}\n');
    const rebuilt=await buildStage({root,modules:stageBlock.modules,stageBlock,build:join(work,'build')});
    expect(rebuilt.reused).toBe(false);
    expect(rebuilt.cssSha256).not.toBe(first.cssSha256);
    expect(await readFile(rebuilt.css,'utf8')).toContain('outline: 0');
    // A damaged output is rebuilt, not reused.
    await writeFile(rebuilt.js,'damaged');
    expect((await buildStage({root,modules:stageBlock.modules,stageBlock,build:join(work,'build')})).reused).toBe(false);
  });
  test.each([
    ['a missing slot','slot.tsx',[/slots: \['stage', 'plate', 'headline', 'aside'\]/,"slots: ['stage', 'plate', 'headline']"],/slotsDifferFromTheDocument/],
    ['an extra slot','extra.tsx',[/slots: \['left', 'right', 'headline'\]/,"slots: ['left', 'right', 'headline', 'extra']"],/"extra"/],
    ['an action parameter','param.tsx',[/params\.item/,'params.job'],/Property 'job' does not exist/],
    ['a prop','prop.tsx',[/props\.series/g,'props.brand'],/Property 'brand' does not exist/],
  ])('a module whose %s differs from the document is refused naming it',async(_,name,[pattern,replacement],diagnostic)=>{
    const root=join(work,'project'),source=await readFile(join(TOUR,'stage.tsx'),'utf8');
    const changed=source.replace(pattern,replacement);
    expect(changed).not.toBe(source);
    await writeFile(join(root,name),changed);
    const refusal=buildStage({root,modules:[name],stageBlock,build:join(work,`build-${name}`)});
    await expect(refusal).rejects.toThrow(new RegExp(`Stage module ${name.replace('.','\\.')} does not type-check`));
    await expect(refusal).rejects.toThrow(diagnostic);
  });
});

describe('bundle',()=>{
  test('a JavaScript module is bundled without the type check; no module bundles the runtime alone',async()=>{
    const root=join(work,'project');
    await writeFile(join(root,'plain.jsx'),
      "import {defineElement} from 'videomaker/stage';\ndefineElement({kind: 'tally', component: ({state}) => <b>{state.props.items.length}</b>});\n");
    const js=await buildStage({root,modules:['plain.jsx'],stageBlock,build:join(work,'build-jsx')});
    expect(js).toMatchObject({reused:false,typechecked:false});
    const alone=await buildStage({root,modules:[],stageBlock:null,build:join(work,'build-alone')});
    expect(alone).toMatchObject({reused:false,typechecked:false,modules:[]});
    expect((await readFile(alone.js,'utf8')).length).toBeGreaterThan(10_000);
  });
  test('a module that is missing or outside the project is refused by name',async()=>{
    const root=join(work,'project');
    await expect(buildStage({root,modules:['nowhere.tsx'],stageBlock,build:join(work,'build-x')}))
      .rejects.toThrow(/Stage module nowhere\.tsx does not exist/);
    await writeFile(join(work,'outside.tsx'),'export {};\n');
    await expect(buildStage({root,modules:['../outside.tsx'],stageBlock,build:join(work,'build-x')}))
      .rejects.toThrow(/Stage module \.\.\/outside\.tsx is outside the project/);
    await expect(buildStage({root,modules:['stage.css'],stageBlock,build:join(work,'build-x')}))
      .rejects.toThrow(/Stage module stage\.css is not TypeScript or JavaScript/);
  });
});
