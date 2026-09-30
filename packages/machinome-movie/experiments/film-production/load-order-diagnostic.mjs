// Evidence-only viewer load-order diagnostic. No product source or model changes.
// Usage: node experiments/film-production/load-order-diagnostic.mjs VIEWER_BUNDLE OUTPUT_DIR
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {chromium} from 'playwright';
import {decodePng} from '../../src/pixels.mjs';

const [bundlePath,outputPath]=process.argv.slice(2);
if(!bundlePath||!outputPath)throw new Error('Usage: node load-order-diagnostic.mjs VIEWER_BUNDLE OUTPUT_DIR');
const output=resolve(outputPath);
await mkdir(output,{recursive:true});
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const bundle=await readFile(resolve(bundlePath));

// Two separate URLs and identical, coincident closed solids. Only colour and
// asynchronous completion order differ; neither is a Leonardo project part.
const lo=-1,hi=1,z0=-0.02,z1=0.02;
const faces=[
  [[lo,lo,z1],[hi,lo,z1],[hi,hi,z1]],[[lo,lo,z1],[hi,hi,z1],[lo,hi,z1]],
  [[hi,lo,z0],[lo,lo,z0],[lo,hi,z0]],[[hi,lo,z0],[lo,hi,z0],[hi,hi,z0]],
  [[lo,lo,z0],[lo,lo,z1],[lo,hi,z1]],[[lo,lo,z0],[lo,hi,z1],[lo,hi,z0]],
  [[hi,lo,z1],[hi,lo,z0],[hi,hi,z0]],[[hi,lo,z1],[hi,hi,z0],[hi,hi,z1]],
  [[lo,hi,z1],[hi,hi,z1],[hi,hi,z0]],[[lo,hi,z1],[hi,hi,z0],[lo,hi,z0]],
  [[lo,lo,z0],[hi,lo,z0],[hi,lo,z1]],[[lo,lo,z0],[hi,lo,z1],[lo,lo,z1]],
];
const stl=Buffer.from('solid coincident_plate\n'+faces.map(points=>
  'facet normal 0 0 0\n outer loop\n'+points.map(p=>`  vertex ${p.join(' ')}`).join('\n')+
  '\n endloop\nendfacet\n').join('')+'endsolid coincident_plate\n');
const part=(name,color)=>({name,type:'LeafNode',color,mtime:0,operations:[],model:`${name}.stl`,piece:name});
const manifest={
  format:'machinome-export',version:2,animation:{fps:30,frames:30},drivers:{},instructions:{},
  root:{name:'Load order plates',type:'AssemblyNode',color:null,mtime:0,operations:[],children:[
    part('red','#ff0000'),part('blue','#0000ff')
  ]},
  pieces:['red','blue'].map(name=>({id:name,name,sources:[],models:[`${name}.stl`],count:1,
    size:[2,2,0.04],volume:0.16,watertight:true})),
};
const manifestBytes=Buffer.from(JSON.stringify(manifest,null,2)+'\n');
const html=Buffer.from('<!doctype html><html><head><meta charset="utf-8"><style>html,body,#host{margin:0;width:100%;height:100%;overflow:hidden}canvas{display:block}</style></head><body><div id="host"></div><script src="/viewer.js"></script></body></html>');
await Promise.all([
  writeFile(join(output,'manifest.json'),manifestBytes),
  writeFile(join(output,'red.stl'),stl),writeFile(join(output,'blue.stl'),stl),
  writeFile(join(output,'index.html'),html),
]);

let mode=null;
let completions=[];
const server=createServer(async(req,res)=>{
  const path=new URL(req.url,'http://127.0.0.1').pathname;
  const assets={'/': [html,'text/html'], '/viewer.js':[bundle,'text/javascript'],
    '/manifest.json':[manifestBytes,'application/json'],
    '/red.stl':[stl,'model/stl'], '/blue.stl':[stl,'model/stl']};
  const asset=assets[path];
  if(!asset){res.writeHead(404,{'Cache-Control':'no-store'});res.end();return;}
  if(path.endsWith('.stl')){
    const name=path.slice(1,-4);
    res.on('finish',()=>completions.push({name,finishedNs:process.hrtime.bigint().toString()}));
    if(name===mode.delay)await new Promise(done=>setTimeout(done,200));
  }
  res.writeHead(200,{'Content-Type':asset[1],'Cache-Control':'no-store','Content-Length':asset[0].length});
  res.end(asset[0]);
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const address=server.address();
const report={
  protocol:'fresh Chromium browser per mount; A delays blue 200 ms, B delays red 200 ms; ABBA',
  bundle:{path:resolve(bundlePath),sha256:sha(bundle)},
  manifest:{path:join(output,'manifest.json'),sha256:sha(manifestBytes)},
  stl:{red:join(output,'red.stl'),blue:join(output,'blue.stl'),sha256:sha(stl)},
  viewport:{width:640,height:480},camera:[0,0,5],target:[0,0,0],up:[0,1,0],fov:50,time:0.25,
  mounts:[],
};
try{
  for(const [index,label] of ['A','B','B','A'].entries()){
    mode={label,delay:label==='A'?'blue':'red'};
    completions=[];
    const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
    const context=await browser.newContext({viewport:report.viewport,deviceScaleFactor:1});
    const page=await context.newPage();
    const mount={index,label,delayed:mode.delay,browserVersion:browser.version(),captures:[],responseCompletions:[],pageErrors:[],consoleErrors:[]};
    report.mounts.push(mount);
    try{
      page.on('pageerror',error=>mount.pageErrors.push({name:error.name,message:error.message}));
      page.on('console',message=>{if(message.type()==='error')mount.consoleErrors.push(message.text());});
      await page.goto(`http://127.0.0.1:${address.port}/`,{waitUntil:'load'});
      const mounted=await page.evaluate(async()=>{
        if(MachinomeViewer.apiVersion!==28)throw Error(`Expected API 28, got ${MachinomeViewer.apiVersion}`);
        window.viewer=await MachinomeViewer.mount('#host','/manifest.json',{
          renderMode:'on-demand',animation:'external',autoplay:false,
          driverControls:'none',partControls:'none',time:0.25,
          up:[0,1,0],fov:50,view:{camera:[0,0,5],target:[0,0,0]},
        });
        window.viewer.setView({camera:[0,0,5],target:[0,0,0]});
        window.viewer.setTime(0.25);
        return {apiVersion:MachinomeViewer.apiVersion,view:window.viewer.view()};
      });
      mount.mounted=mounted;
      mount.responseCompletions=[...completions];
      mount.actualOrder=mount.responseCompletions.map(x=>x.name);
      for(let repeat=0;repeat<5;repeat++){
        await page.evaluate(()=>window.viewer.setTime(0.25));
        const bytes=await page.screenshot();
        const file=join(output,`mount-${index}-${label}-${repeat}.png`);
        await writeFile(file,bytes);
        const image=decodePng(bytes),offset=(240*image.width+320)*3;
        mount.captures.push({repeat,file,sha256:sha(bytes),width:image.width,height:image.height,
          centerPixel:[...image.rgb.subarray(offset,offset+3)]});
      }
    }catch(error){mount.error={name:error.name,message:error.message,stack:error.stack};}
    finally{await browser.close();}
    await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    if(mount.error)break;
  }
}finally{
  await new Promise(done=>server.close(done));
  await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
}
console.log(JSON.stringify(report,null,2));
if(report.mounts.length!==4||report.mounts.some(m=>m.error))process.exitCode=1;
