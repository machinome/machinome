// Historical Leonardo render evidence only; this script reads completed media.
// Wall seconds below are transcribed observations from the original CLI runs,
// not timings measured by this recorder. Never use it to attribute later runs.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {decodePng} from '../../src/pixels.mjs';

const [project,kind]=process.argv.slice(2);
if(!project||!['80','70'].includes(kind))throw new Error('Usage: node record-matrix.mjs LEONARDO_ROOT 80|70');
const tool=resolve(import.meta.dirname,'../..');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const fileSha=async path=>sha(await readFile(path));
const base=resolve(project,'videos');
const measuredHashes={
  renderSha256:'c34f3423c7130f37965f34534b9fb7eac797774e58f3d3a8ba46b4bc52c50312',
  shotCacheSha256:'9dbab4bdfbff39bb4e0ff66def627e6c0bcdda09f05f7e68ca199bebf1b991ed',
  timelineSha256:'af93900b72ccc9b4429ce3df1bde62824988354e439d38d9e6fabeed9703648b',
  filmSha256:'74a4ecb314aca8a5e1bfc6cbbd479632584e27b7b57e775e4f5b8093cf18024f',
  viewerSha256:'a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c',
  modelManifestSha256:'92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9',
  cachedSpeechSha256:'fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8',
};
const measuredProvenance={
  '80':{
    baseline:['bd3e4433c76107149238c3179ea4e469d8eb6f0eafb37a26fc8a3163603451e2','995f449451796520a6fd4ba8bfb5d3cce8f142f19b057d7f5a8ac1465afff85d'],
    warm:['bd3e4433c76107149238c3179ea4e469d8eb6f0eafb37a26fc8a3163603451e2','995f449451796520a6fd4ba8bfb5d3cce8f142f19b057d7f5a8ac1465afff85d'],
    variant:['f75acd21e85958dd31aa08964553d7e0b1ee65695a5fc9656f555a78be38df8b','995f449451796520a6fd4ba8bfb5d3cce8f142f19b057d7f5a8ac1465afff85d'],
    cold:['f75acd21e85958dd31aa08964553d7e0b1ee65695a5fc9656f555a78be38df8b','995f449451796520a6fd4ba8bfb5d3cce8f142f19b057d7f5a8ac1465afff85d'],
  },
  '70':{
    baseline:['9e1ad0a730c47c4ff17e898ca44f37f006fdf0d5141553d807571d20d6d82d09','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
    warm:['9e1ad0a730c47c4ff17e898ca44f37f006fdf0d5141553d807571d20d6d82d09','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
    variant:['a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
    cold:['a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
    coldRepeat1:['a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
    coldRepeat2:['a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96','fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3'],
  },
};
const specs=kind==='80'?
  {episode:'demo-incremental-rendering',count:80,comparedTo:'variant',runs:[
    ['baseline','demo-incremental-rendering/_build/evidence/new-baseline/silent-preview-manifest.json',31.57],
    ['warm','demo-incremental-rendering/_build/evidence/new-warm/silent-preview-manifest.json',1.99],
    ['variant','demo-incremental-rendering/_build/evidence/new-variant/silent-preview-manifest.json',20.22],
    ['cold','demo-incremental-rendering-cold/_build/silent-preview-manifest.json',31.34]]}:
  {episode:'demo-incremental-source-grid',count:70,comparedTo:'variant',runs:[
    ['baseline','demo-incremental-source-grid/_build/evidence/new-baseline/silent-preview-manifest.json',22.75],
    ['warm','demo-incremental-source-grid/_build/evidence/new-warm/silent-preview-manifest.json',2.00],
    ['variant','demo-incremental-source-grid/_build/evidence/new-variant/silent-preview-manifest.json',15.62],
    ['cold','demo-incremental-source-grid-cold/_build/evidence/original-cold/silent-preview-manifest.json',22.74],
    ['coldRepeat1','demo-incremental-source-grid-cold-repeat-1/_build/silent-preview-manifest.json',23.12],
    ['coldRepeat2','demo-incremental-source-grid-cold-repeat-2/_build/silent-preview-manifest.json',22.64]]};

const inputHashes={
  renderSha256:await fileSha(resolve(tool,'src/render.mjs')),
  shotCacheSha256:await fileSha(resolve(tool,'src/shot-cache.mjs')),
  timelineSha256:await fileSha(resolve(tool,'src/timeline.mjs')),
  filmSha256:await fileSha(resolve(tool,'src/film.js')),
  viewerSha256:await fileSha('/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js'),
  modelManifestSha256:await fileSha(resolve(project,'export/hydraulic_sawmill/manifest.json')),
};
if(kind==='70')inputHashes.cachedSpeechSha256=await fileSha(resolve(base,'demo-incremental-source-grid/_build/audio/source-72b6eea39321423a.wav'));
for(const [name,actual] of Object.entries(inputHashes)){
  if(actual!==measuredHashes[name])throw new Error(`Historical evidence input changed: ${name}; refusing to write a new record`);
}
const runs={};
for(const [name,relativeManifest,wallSeconds] of specs.runs){
  const manifestPath=resolve(base,relativeManifest),manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  if(manifest.count!==specs.count)throw new Error(`${name} has ${manifest.count} frames, expected ${specs.count}`);
  const [episodeSha256,productionSha256]=measuredProvenance[kind][name];
  if(manifest.provenance.episodeSha256!==episodeSha256||manifest.provenance.productionSha256!==productionSha256)
    throw new Error(`Historical evidence source changed: ${name}; refusing to write a new record`);
  const preservedOutput=resolve(dirname(manifestPath),'silent-preview.mp4');
  if(manifest.outputSha256!==await fileSha(preservedOutput))throw new Error(`${name} MP4 hash mismatch`);
  const frames=[];
  for(let i=0;i<specs.count;i++){
    const filename=`${String(i).padStart(6,'0')}.png`,path=resolve(manifest.dir,filename);
    frames.push({index:i,path,sha256:await fileSha(path)});
  }
  runs[name]={manifestPath,manifestSha256:await fileSha(manifestPath),outputPath:preservedOutput,
    outputSha256:manifest.outputSha256,assemblyDir:manifest.dir,wallSeconds,
    episodeSha256:manifest.provenance.episodeSha256,productionSha256:manifest.provenance.productionSha256,
    browser:manifest.browser,cache:manifest.cache??null,frames};
}
const pixelDiff=async(a,b)=>{
  const A=decodePng(await readFile(a)),B=decodePng(await readFile(b));
  if(A.width!==B.width||A.height!==B.height)throw new Error('PNG dimensions differ');
  let pixelCount=0,channelCount=0,maxChannelDelta=0,x0=A.width,y0=A.height,x1=-1,y1=-1;
  for(let y=0;y<A.height;y++)for(let x=0;x<A.width;x++){
    const at=(y*A.width+x)*3;let changed=false;
    for(let k=0;k<3;k++){
      const delta=Math.abs(A.rgb[at+k]-B.rgb[at+k]);
      if(delta){changed=true;channelCount++;maxChannelDelta=Math.max(maxChannelDelta,delta);}
    }
    if(changed){pixelCount++;x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
  }
  return {pixelCount,channelCount,maxChannelDelta,bounds:pixelCount?{x0,y0,x1,y1}:null};
};
const pairs={};
for(const name of Object.keys(runs)){
  if(name===specs.comparedTo)continue;
  const differences=[];
  for(let i=0;i<specs.count;i++){
    const a=runs[specs.comparedTo].frames[i],b=runs[name].frames[i];
    if(a.sha256!==b.sha256)differences.push({index:i,variantSha256:a.sha256,otherSha256:b.sha256,pixels:await pixelDiff(a.path,b.path)});
  }
  pairs[`${specs.comparedTo}_vs_${name}`]={equal:differences.length===0,differences};
}
const report={schema:'leonardo-render-matrix/1',fixture:specs.episode,frameCount:specs.count,
  inputHashes,runs,pairs};
const output=resolve(base,specs.episode,'_build/evidence',`postimplementation-${kind}.json`);
await mkdir(dirname(output),{recursive:true});
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output,summary:Object.fromEntries(Object.entries(runs).map(([n,r])=>[n,{wallSeconds:r.wallSeconds,captured:r.cache?.capturedFrames,reused:r.cache?.reusedFrames,outputSha256:r.outputSha256}])),pairs:Object.fromEntries(Object.entries(pairs).map(([n,p])=>[n,p.differences.map(d=>d.index)]))},null,2));
