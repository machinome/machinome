// Layer 8 (serial; Chromium, FFmpeg, the viewer double, no speech): what
// check, preview and render say of the Git work trees whose heads they
// record (the honest-provenance change, ADR-015), and of the revision the
// model's export records it was made from (the read-the-exports-source
// change, ADR-019). The project's tree is the test's own copy, committed
// with its export and build directories ignored; the export's manifest
// records the copy's commit as its `source`, as the framework writes it.
// Videomaker's tree is the checkout the suite runs in, whose state is read
// outside the memo's key, so it is asserted only by the shape of its words.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {writeFile,readFile,appendFile,rm,realpath} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {yamlProject} from '../support/yaml-project.mjs';
import {viewerDouble} from '../viewer-double.mjs';

const here=dirname(fileURLToPath(import.meta.url));
// The command line in a child process with no key and a fetch that throws.
const NO_FETCH='data:text/javascript,globalThis.fetch=()=>{throw new Error("A test attempted a network request")}';
const cli=(...args)=>{
  try{return {code:0,out:execFileSync(process.execPath,['--import',NO_FETCH,join(here,'..','..','bin','videomaker.mjs'),...args],
    {encoding:'utf8',stdio:['ignore','pipe','pipe'],env:{...process.env,ELEVENLABS_API_KEY:''}})};}
  catch(error){return {code:error.status,out:String(error.stdout)+String(error.stderr)};}
};
const readJson=async file=>JSON.parse(await readFile(file,'utf8'));

// One two-second shot at two frames a second, with every release field set,
// so that nothing but a tree can keep it from being release-ready.
const EPISODE={format:'machinome-video-draft/0.4',title:'Provenance test',series:'PROVENANCE TEST',
  output:{width:320,height:180,fps:2,durationSeconds:2},model:{expectedDurationSeconds:2},
  audio:{provider:'elevenlabs',model:'test-model',voice:'test-voice',outputFormat:'pcm_24000',replacements:{}},
  style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
  cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
  release:{descriptionTemplate:'description.md',simulationUrl:'https://simulation.example.invalid/',
    sourceUrl:'https://source.example.invalid/'},
  stills:{},clips:{},shots:[{id:'a',start:0,end:2,narration:'Look.',direction:'Test.',camera:[{at:0,preset:'a'}],
    hiddenLayers:[],overlays:[],evidence:[],simulation:{from:0,to:2}}]};

// The project committed whole: the episode, its production settings and the
// description; the export (where the viewer double is written) and _build/
// are ignored by the project's .gitignore, so the tree is clean. The export
// records the commit the episode pins, clean, as `machinome export` run at
// that commit records it.
const MODEL={root:{name:'test'},animation:{loop:2}};
async function cleanProject(t){
  const project=await yamlProject(t,{manifest:MODEL});
  const file=await project.write(EPISODE);
  const pinned=project.revision;
  project.git('add','-A');
  project.git('commit','-q','-m','the episode');
  await project.setManifest({...MODEL,source:{revision:pinned,dirty:false}});
  const viewer=join(project.dir,'export','viewer.js');
  await writeFile(viewer,'// machinome-viewer double, viewer API 28\n'+viewerDouble({}));
  assert.equal(project.git('status','--porcelain'),'','the fixture project starts clean');
  return {...project,file,viewer,pinned,head:project.git('rev-parse','HEAD')};
}
// Videomaker's line, whichever state the checkout is in.
const toolLine=(command,consequence)=>new RegExp(`^Videomaker tree: (clean at [0-9a-f]{12}|dirty at ${command}, \\d+ paths? differs? from its head [0-9a-f]{12} \\(.+\\); ${consequence})$`,'m');

test('check, render and preview say whether the project tree was dirty, and a dirty render is not release-ready',async t=>{
  const {dir,file,viewer,head,pinned}=await cleanProject(t);
  const short=head.slice(0,12),manifestPath=join(dir,'_build','silent-preview-manifest.json');
  const exportClean=new RegExp(`^Export: made from ${pinned.slice(0,12)}, clean$`,'m');

  // Clean: the lines say so, the records say so, and no project reason
  // keeps the film from being release-ready.
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.out);
  assert.match(checked.out,new RegExp(`^Project tree: clean at ${short}$`,'m'));
  assert.match(checked.out,toolLine('check','a render now records a head that is not the tool that rendered and is not release-ready'));
  assert.match(checked.out,exportClean);
  const clean=cli('render',file,'--viewer',viewer,'--silent');
  assert.equal(clean.code,0,clean.out);
  assert.match(clean.out,new RegExp(`^Project tree: clean at ${short}$`,'m'));
  assert.match(clean.out,toolLine('render','the manifest\'s workflowHead is not the tool that rendered, and the film is not release-ready'));
  assert.match(clean.out,exportClean);
  const first=await readJson(manifestPath);
  assert.equal(first.provenance.projectHead,head);
  assert.equal(first.provenance.projectDirty,false);
  assert.deepEqual([first.provenance.exportRevision,first.provenance.exportDirty],[pinned,false]);
  assert.equal(typeof first.provenance.workflowDirty,'boolean');
  assert.match(first.provenance.workflowHead,/^[0-9a-f]{40}$/);
  assert.deepEqual(first.releaseIssues.filter(issue=>!issue.startsWith('Videomaker tree dirty at render')),[],
    'nothing of the project keeps a clean render from being release-ready');
  assert.equal(first.releaseReady,first.releaseIssues.length===0);
  assert.equal(first.releaseIssues.length,first.provenance.workflowDirty?1:0);
  assert.equal(first.cache.capturedFrames,4);
  for(const shot of first.cache.shots)assert.deepEqual([shot.origin.projectHead,shot.origin.projectDirty,
    shot.origin.exportRevision,shot.origin.exportDirty],[head,false,pinned,false],shot.shotId);

  // An untracked file the project does not ignore: dirty, named, not
  // release-ready; the frames are reused, since the dirt is no picture input.
  await writeFile(join(dir,'notes.txt'),'An untracked note.\n');
  const dirty=cli('render',file,'--viewer',viewer,'--silent');
  assert.equal(dirty.code,0,dirty.out);
  assert.match(dirty.out,new RegExp(`^Project tree: dirty at render, 1 path differs from its head ${short} \\(notes\\.txt\\); the manifest's projectHead is not the content rendered, and the film is not release-ready$`,'m'));
  const second=await readJson(manifestPath);
  assert.equal(second.provenance.projectHead,head);
  assert.equal(second.provenance.projectDirty,true);
  assert.equal(second.releaseReady,false);
  assert.ok(second.releaseIssues.includes(`project tree dirty at render: 1 path differs from projectHead ${short} (notes.txt)`),
    JSON.stringify(second.releaseIssues));
  assert.equal(second.cache.commonKey,first.cache.commonKey,'the dirt does not enter the common key');
  assert.deepEqual([second.cache.capturedFrames,second.cache.reusedFrames],[0,4],'a dirty tree reuses the clean capture');
  for(const shot of second.cache.shots)assert.equal(shot.origin.projectDirty,false,'a reused shot keeps the tree it was captured from');

  // A tracked file changed: check and preview say so, naming it.
  await rm(join(dir,'notes.txt'));
  await appendFile(join(dir,'description.md'),'A changed line.\n');
  const rechecked=cli('check',file,'--viewer',viewer);
  assert.equal(rechecked.code,0,rechecked.out);
  assert.match(rechecked.out,new RegExp(`^Project tree: dirty at check, 1 path differs from its head ${short} \\(description\\.md\\); a render now records a head that is not the content rendered and is not release-ready$`,'m'));
  const previewed=cli('preview',file,'--viewer',viewer,'--width','320');
  assert.equal(previewed.code,0,previewed.out);
  assert.match(previewed.out,new RegExp(`^Project tree: dirty at preview, 1 path differs from its head ${short} \\(description\\.md\\); the preview's projectHead is not the content previewed$`,'m'));
  assert.match(previewed.out,toolLine('preview','the preview\'s workflowHead is not the tool that previewed'));
  const report=await readJson(join(dir,'_build','preview','report.json'));
  assert.deepEqual([report.provenance.projectHead,report.provenance.projectDirty],[head,true]);
  assert.equal(typeof report.provenance.workflowDirty,'boolean');
});

// Wart 9 of the Curta film Addition and the pilot's ruling of 1 October 2026
// (read-the-exports-source, ADR-019): the export's manifest records the
// revision it was made from and whether the project was dirty then. The
// dirt is said, recorded and kept from release, never refused and never a
// key; an export that records no source is refused by name.
test('check, render and preview say whether the export was made from a dirty tree, which is not release-ready, never refused and no key',async t=>{
  const {dir,file,viewer,pinned,setManifest,manifest}=await cleanProject(t);
  const short=pinned.slice(0,12),manifestPath=join(dir,'_build','silent-preview-manifest.json');
  const dirtyLine=consequence=>new RegExp(`^Export: made from ${short}, dirty: Git listed changes in the project when the model was exported; ${consequence}$`,'m');
  const clean=cli('render',file,'--viewer',viewer,'--silent');
  assert.equal(clean.code,0,clean.out);
  const first=await readJson(manifestPath);
  assert.ok(!first.releaseIssues.some(issue=>issue.startsWith('export')),JSON.stringify(first.releaseIssues));

  // The same export as the framework records it when the project held a
  // change: said, recorded, not release-ready, the frames reused.
  await setManifest({...MODEL,source:{revision:pinned,dirty:true}});
  const dirty=cli('render',file,'--viewer',viewer,'--silent');
  assert.equal(dirty.code,0,dirty.out);
  assert.match(dirty.out,dirtyLine('the manifest\'s exportRevision is not the content exported, and the film is not release-ready'));
  const second=await readJson(manifestPath);
  assert.deepEqual([second.provenance.exportRevision,second.provenance.exportDirty],[pinned,true]);
  assert.equal(second.releaseReady,false);
  assert.ok(second.releaseIssues.includes(`export dirty when made: exportRevision ${short} is not the content exported; export the model again from a clean tree`),
    JSON.stringify(second.releaseIssues));
  assert.equal(second.cache.commonKey,first.cache.commonKey,'the export\'s source does not enter the common key');
  assert.deepEqual([second.cache.capturedFrames,second.cache.reusedFrames],[0,4],'a dirty export reuses the clean capture');
  assert.notEqual(second.hashes['/model/manifest.json'],first.hashes['/model/manifest.json'],
    'the manifest served, and hashed in the record, is the export as it is');
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.out);
  assert.match(checked.out,dirtyLine('a render now records an export that is not that revision and is not release-ready'));
  const previewed=cli('preview',file,'--viewer',viewer,'--width','320');
  assert.equal(previewed.code,0,previewed.out);
  assert.match(previewed.out,dirtyLine('the preview\'s exportRevision is not the content exported'));
  const report=await readJson(join(dir,'_build','preview','report.json'));
  assert.deepEqual([report.provenance.exportRevision,report.provenance.exportDirty],[pinned,true]);

  // No source: an export made before the framework recorded it, or outside
  // Git. Refused by name, whatever sidecar lies beside it.
  await writeFile(join(dirname(manifest),'source-revision.txt'),pinned+'\n');
  await setManifest({...MODEL,source:undefined});
  const refusal=`The export ${await realpath(manifest)} records no source, the revision it was made from (manifest field source.revision); export the model again with a machinome that records it, from the project's Git repository with a commit: a project outside Git cannot be filmed with a pinned revision`;
  for(const command of ['check','render']){
    const refused=cli(command,file,'--viewer',viewer,...(command==='render'?['--silent']:[]));
    assert.equal(refused.code,1,refused.out);
    assert.ok(refused.out.split('\n').includes(refusal),refused.out);
  }
});
