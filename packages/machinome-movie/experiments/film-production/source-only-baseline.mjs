// Pre-change, exact-pixel compatibility baseline for source-only-shots.
// Four existing Leonardo episodes are loaded unchanged. Each browser is closed
// before the next opens. Generated PNGs and the report stay in ignored _build/.
import {mkdtemp,mkdir,writeFile,readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadEpisode} from '../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {browserSession} from '../../src/render.mjs';
import {fileHash,hash,json} from '../../src/util.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const buildRoot=resolve(here,'../../_build');
const project='/home/asa/devel/machinome/projects/Leonardo/videos';
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
const expectedViewerSha='5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413';
const oldReportPath=process.argv[2]==='--compare'?process.argv[3]:null;
if(process.argv.length>2&&!oldReportPath)throw new Error('Usage: node source-only-baseline.mjs [--compare PRECHANGE_REPORT]');
const oldReport=oldReportPath?JSON.parse(await readFile(resolve(oldReportPath),'utf8')):null;
const cases=[
  {name:'format-02-model',episode:'demo-legacy-02',times:[0,1,3]},
  {name:'format-03-annotated',episode:'demo-annotate-a-part',times:[0,1,4.5]},
  {name:'format-04-model',episode:'demo-keyframes-and-easing-2',times:[0,1,4.5]},
  {name:'format-04-split',episode:'demo-incremental-source-grid-fixed',times:[1.2,2.5,4.7,5]},
];
if(await fileHash(viewer)!==expectedViewerSha)throw new Error('Repaired Viewer API 28 bundle hash changed');
await mkdir(buildRoot,{recursive:true});
const output=await mkdtemp(resolve(buildRoot,oldReport?'source-only-postchange-':'source-only-prechange-'));
const report={kind:oldReport?'source-only-shots/post-change':'source-only-shots/compatibility-capture',viewer,viewerSha256:expectedViewerSha,
  output,width:960,cases:[]};
for(const sample of cases){
  const source=resolve(project,sample.episode,'episode.yaml');
  const e=await loadEpisode(source);
  if(sample.name==='format-04-split')
    await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:e.output.fps});
  const dir=resolve(output,sample.name);await mkdir(dir);
  e.paths.build=dir;
  const records=[];
  const result=await browserSession(e,viewer,960,[],async({page,pose})=>{
    for(const time of sample.times){
      const request=frameAt(e,time,[]);
      await pose(time);
      const bytes=await page.screenshot();
      const file=resolve(dir,`${String(records.length).padStart(2,'0')}-${time.toFixed(2)}.png`);
      await writeFile(file,bytes);
      records.push({time,file,sha256:hash(bytes),request});
    }
    return {records};
  });
  report.cases.push({name:sample.name,source,episodeSha256:await fileHash(source),
    format:e.format,outputSettings:e.output,browser:result.browser,viewerApi:result.viewerApi,
    framesChecked:result.framesChecked,records});
  await json(resolve(output,'report.json'),report);
}
const split=report.cases.find(c=>c.name==='format-04-split');
const outgoing=split.records.find(r=>r.time===4.7)?.request.transition?.outgoing;
if(!outgoing?.code)throw new Error('Expected outgoing source continuation at 4.7 s is absent');
report.outgoingContinuation={time:4.7,shotId:outgoing.shotId,code:outgoing.code,
  request:split.records.find(r=>r.time===4.7).request};
if(oldReport){
  assert.equal(report.viewerSha256,oldReport.viewerSha256);
  assert.equal(report.width,oldReport.width);
  const comparisons=[];
  for(const sample of report.cases){
    const old=oldReport.cases.find(c=>c.name===sample.name);
    assert.ok(old,`Pre-change case missing: ${sample.name}`);
    assert.equal(sample.episodeSha256,old.episodeSha256,`episode changed: ${sample.name}`);
    assert.deepEqual(sample.outputSettings,old.outputSettings,`output changed: ${sample.name}`);
    assert.equal(sample.browser,old.browser,`Chromium changed: ${sample.name}`);
    assert.equal(sample.viewerApi,old.viewerApi,`viewer API changed: ${sample.name}`);
    assert.equal(sample.records.length,old.records.length);
    for(const [i,record] of sample.records.entries()){
      const prior=old.records[i];
      assert.equal(record.time,prior.time);
      assert.deepEqual(JSON.parse(JSON.stringify(record.request)),prior.request,
        `frameAt request changed: ${sample.name} ${record.time}`);
      const exact=(await readFile(record.file)).equals(await readFile(prior.file));
      comparisons.push({case:sample.name,time:record.time,exact,sha256:record.sha256});
      assert.ok(exact,`PNG differs from pre-change: ${sample.name} ${record.time}`);
    }
  }
  report.comparison={baseline:resolve(oldReportPath),exactPairs:comparisons.length,comparisons};
}
await json(resolve(output,'report.json'),report);
console.log(resolve(output,'report.json'));
