// Layer 4 (pure, Node): the stage runtime and the take transport compile under
// `tsc --noEmit` (strict), and a movie's
// generated types check its stage modules: the fixture tour's template
// compiles against the types generated from its document's stage block, and a
// module whose slot, prop or action parameter differs is refused naming it.
// Also the bundle's reuse and its refusals (src/stage-build.mjs), in a
// temporary directory outside the repository.
import {execFile} from 'node:child_process';
import {cp,mkdtemp,readFile,realpath,rm,symlink,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {afterAll,beforeAll,describe,expect,test} from 'vitest';
import {buildStage,movieTypes,renameOutput} from '../src/stage-build.mjs';

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
  test('the take transport compiles strictly, its tests included: tsc --noEmit -p transport/tsconfig.json',async()=>{
    const {code,output}=await run(['--noEmit','--pretty','false','-p','transport/tsconfig.json'],TOOL);
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
  // The stable-stage-bundle change (ADR-013): the bundle names what it read by
  // the tool and the project, never by the machine's directories, so two
  // checkouts of the same tool building two copies of the same project write
  // the same bytes, and a second checkout reuses what the first one built.
  // The second checkout is a copy of the tool's src/, stage/, transport/ and
  // package.json elsewhere, with its node_modules a link to this checkout's,
  // as a worktree's is.
  let otherCheckout=null;
  const elsewhere=()=>otherCheckout??=(async()=>{
    const other=join(work,'other-checkout');
    // package.json too: its "type" decides how esbuild imports the runtime.
    for(const entry of ['src','stage','transport','package.json'])await cp(join(TOOL,entry),join(other,entry),{recursive:true});
    await symlink(await realpath(join(TOOL,'node_modules')),join(other,'node_modules'));
    return import(pathToFileURL(join(other,'src','stage-build.mjs')).href);
  })();
  const copyOfTour=async(...at)=>{const dir=join(work,...at,'project');await cp(TOUR,dir,{recursive:true});return dir;};
  test('two checkouts bundle two copies of a project, at different places, to the same bytes',async()=>{
    const near=await copyOfTour('near'),far=await copyOfTour('far','deeper','still');
    const first=await buildStage({root:near,modules:stageBlock.modules,stageBlock,build:join(near,'_build')});
    const second=await (await elsewhere()).buildStage({root:far,modules:stageBlock.modules,stageBlock,build:join(far,'_build')});
    expect(first).toMatchObject({reused:false,typechecked:true});
    expect(second).toMatchObject({reused:false,typechecked:true});
    const lines=async file=>(await readFile(file,'utf8')).split('\n');
    const differing=async(a,b)=>{const [x,y]=[await lines(a),await lines(b)];
      return x.flatMap((line,i)=>line===y[i]?[]:[`${i+1}: ${line}  |  ${y[i]}`]).concat(y.length===x.length?[]:[`${x.length} lines | ${y.length} lines`]);};
    expect(await differing(first.js,second.js),'stage.js differs between the checkouts').toEqual([]);
    expect(await differing(first.css,second.css),'stage.css differs between the checkouts').toEqual([]);
    expect([second.sha256,second.cssSha256]).toEqual([first.sha256,first.cssSha256]);
    // Every name is the tool's or the project's: no path through the machine.
    const js=await readFile(first.js,'utf8'),css=await readFile(first.css,'utf8');
    for(const text of [js,css]){
      for(const machine of [TOOL,await realpath(TOOL),await realpath(join(TOOL,'node_modules')),work,await realpath(work)])
        expect(text).not.toContain(machine.slice(1));
      expect(text).not.toMatch(/^\s*(\/\/|\/\*|["']) ?\.\.\//m);
    }
    expect(js).toMatch(/^ {2}\/\/ videomaker\/stage\/runtime\.tsx$/m);
    expect(js).toMatch(/^ {2}\/\/ project\/stage\.tsx$/m);
    // The take transport the runtime bundles (ADR-020). It imports the pose
    // rule, which esbuild reads and drops from the script, since the stage
    // poses banks the frame gives it; the record the key is computed over
    // names both by the tool, and nothing by the machine.
    expect(js).toMatch(/^ {2}\/\/ videomaker\/transport\/take\.ts$/m);
    for(const build of [first,second]){
      const names=JSON.parse(await readFile(join(dirname(build.js),'inputs.json'),'utf8')).inputs.map(i=>i.path);
      for(const name of ['videomaker/transport/take.ts','videomaker/transport/viewer-handle.ts','videomaker/src/take.mjs','videomaker/stage/runtime.tsx'])
        expect(names).toContain(name);
      expect(names.filter(name=>name.startsWith('../'))).toEqual([]);
    }
    expect(js).toMatch(/^ {4}"videomaker\/node_modules\/react\/index\.js"\(exports, module\) \{$/m);
    expect(css).toMatch(/^\/\* videomaker\/stage\/stage\.css \*\/$/m);
    expect(css).toMatch(/^\/\* project\/stage\.css \*\/$/m);
  },120_000);
  test('the bundle\'s key is the same from another checkout, which reuses the bundle this one built',async()=>{
    const root=await copyOfTour('shared'),build=join(root,'_build');
    const first=await buildStage({root,modules:stageBlock.modules,stageBlock,build});
    expect(first.reused).toBe(false);
    const reused=await (await elsewhere()).buildStage({root,modules:stageBlock.modules,stageBlock,build});
    expect(reused).toMatchObject({reused:true,typechecked:true,sha256:first.sha256,cssSha256:first.cssSha256});
    // And back: this checkout reuses it too.
    expect(await buildStage({root,modules:stageBlock.modules,stageBlock,build})).toMatchObject({reused:true,sha256:first.sha256});
  },120_000);
  test('a name esbuild escaped or quoted singly is found and renamed; nothing else is touched',()=>{
    // The forms esbuild 0.28 prints for a directory with a non-ASCII
    // character or a double quote in it (seen in the change's evidence).
    const renames=new Map([['../a\u00e7a\u00ed dir/c.cjs','videomaker/node_modules/c/c.cjs'],
      ['../q"d x/y \u{1F600} \u0142/c.cjs','project/\u00e9/c.cjs'],['../../stage.css','project/stage.css']]);
    const js=['  // ../a\u00e7a\u00ed dir/c.cjs','  var require_c = __commonJS({','    "../a\\xE7a\\xED dir/c.cjs"(exports, module) {',
      '      module.exports = "../a\\xE7a\\xED dir/c.cjs";','    }','  });',
      '    \'../q"d x/y \\u{1F600} \\u0142/c.cjs\'(exports) {','  // ../elsewhere/c.cjs',''].join('\n');
    expect(renameOutput(js,'js',renames).split('\n')).toEqual(['  // videomaker/node_modules/c/c.cjs','  var require_c = __commonJS({',
      '    "videomaker/node_modules/c/c.cjs"(exports, module) {','      module.exports = "../a\\xE7a\\xED dir/c.cjs";','    }','  });',
      '    "project/\\u00e9/c.cjs"(exports) {','  // ../elsewhere/c.cjs','']);
    expect(renameOutput('/* ../../stage.css */\n.a {\n  content: "/* ../../stage.css */";\n}\n','css',renames))
      .toBe('/* project/stage.css */\n.a {\n  content: "/* ../../stage.css */";\n}\n');
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
