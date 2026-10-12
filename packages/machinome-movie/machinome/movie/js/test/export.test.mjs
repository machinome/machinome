// What the renderer serves from a model's export (the serve-what-the-viewer-reads
// change, wart 1 of the Curta film Addition): the files the viewer reads, the
// `root` tree's model references and its markings', as the framework's export
// document defines them, and nothing else; a missing or escaping one refused
// by its field in the manifest. Over the fixture project's real exports and
// edited copies of them in a temporary directory; no browser.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {cp,mkdtemp,readFile,writeFile,rm,unlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {viewerFiles,exportFiles} from '../src/export.mjs';

const EXPORTS=join(dirname(fileURLToPath(import.meta.url)),'..','python','tests','fixtures','project','export');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
// The URLs the extension walk of `stage()` served for the two fixture
// exports, computed on the base c8c6309 before this change. Literal; never
// regenerate from the code under test: an export with no provenance file
// string serves these, in this order, so its films keep their cache key.
const BASE={
  seesaw:['/model/models/models/seesaw-Block-211d0bb8cf4f.stl'],
  counter:['/model/models/models/counter-Base,bore=8.2,post_height=36.0,post_offset=28.0-8ba03b76c773.stl',
    '/model/models/models/counter-Crank,arm_height=40.0,arm_length=40.0,diameter=8.0-3f5fc2f38c14.stl',
    '/model/models/models/counter-Drum,bore=8.2-ed1a79eec5ec.stl',
    '/model/models/models/counter-Drum,bore=8.2-ed1a79eec5ec.marking-digits.stl']};

// A copy of a fixture export, its manifest edited before it is read.
async function exportCopy(t,name,edit=()=>{}){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-export-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  await cp(join(EXPORTS,name),dir,{recursive:true});
  const manifest=join(dir,'manifest.json'),doc=await json(manifest);
  edit(doc);await writeFile(manifest,JSON.stringify(doc,null,2)+'\n');
  return {dir:resolve(dir),manifest};
}
const refusal=async promise=>{try{await promise;}catch(error){return error.message;}assert.fail('was not refused');};

test('the files of the fixture exports are their root models and markings, served as before',async()=>{
  const seesaw=await json(join(EXPORTS,'seesaw','manifest.json'));
  assert.deepEqual(viewerFiles(seesaw),[{path:'models/models/seesaw-Block-211d0bb8cf4f.stl',field:'root.children[0].model',node:'Base'}],
    'one file, named first by the base; the other four nodes name it again');
  const counter=await json(join(EXPORTS,'counter','manifest.json'));
  assert.deepEqual(viewerFiles(counter).map(f=>[f.field,f.node]),
    [['root.children[0].model','base'],['root.children[1].model','handle'],['root.children[2].model','units_drum'],
      ['root.children[2].markings[0].model','marking digits of units_drum']]);
  for(const name of ['seesaw','counter']){
    const files=await exportFiles(join(EXPORTS,name,'manifest.json'));
    assert.deepEqual([...files.keys()],BASE[name],`${name}: the URLs and their order`);
    for(const [url,file] of files)assert.equal(file,resolve(EXPORTS,name,url.slice('/model/'.length)));
  }
});

test('a provenance source the export does not hold is neither served nor opened',async t=>{
  const {manifest}=await exportCopy(t,'seesaw',doc=>{
    doc.pieces[0].sources=['STLs/absent.stl','media/absent.png'];
    doc.readme='docs/absent.svg';
  });
  const files=await exportFiles(manifest);
  assert.deepEqual([...files.keys()],BASE.seesaw);
  assert.deepEqual(viewerFiles(await json(manifest)).map(f=>f.path),['models/models/seesaw-Block-211d0bb8cf4f.stl']);
});

test('a model file lost from the export is refused by its field, its node and its path',async t=>{
  const {dir,manifest}=await exportCopy(t,'seesaw',doc=>{
    doc.root.children[2].children[0].model='models/models/lost.stl';
  });
  assert.equal(await refusal(exportFiles(manifest)),
    `Export file missing: root.children[2].children[0].model (Plank) names models/models/lost.stl, which the export ${dir} does not hold; export the model again so the export holds every file its manifest names`);
});

test('a marking artifact lost from the export is refused by the marking\'s field',async t=>{
  const {dir,manifest}=await exportCopy(t,'counter');
  await unlink(join(dir,'models','models','counter-Drum,bore=8.2-ed1a79eec5ec.marking-digits.stl'));
  const message=await refusal(exportFiles(manifest));
  assert.match(message,/^Export file missing: root\.children\[2\]\.markings\[0\]\.model \(marking digits of units_drum\) names models\/models\/counter-Drum,bore=8\.2-ed1a79eec5ec\.marking-digits\.stl, /);
  assert.match(message,/export the model again/);
});

test('a model outside the export is refused by its field',async t=>{
  const {dir,manifest}=await exportCopy(t,'seesaw',doc=>{doc.root.children[0].model='../outside.stl';});
  assert.equal(await refusal(exportFiles(manifest)),
    `Export file outside the export: root.children[0].model (Base) names ../outside.stl, which lies outside the export ${dir}; export the model again so its manifest names only files inside it`);
});
