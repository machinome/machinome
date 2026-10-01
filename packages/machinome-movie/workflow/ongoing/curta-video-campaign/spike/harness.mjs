// The spike's browser harness: one Chromium launched as a server (so its
// process ID is known for /proc), an HTTP server that serves the viewer bundle
// the caller names and one or more export directories, and a page whose host
// box is laid out as the stage lays out a view (`.vm-view-host` absolutely
// inset, `.vm-viewer` 100 % of it). Mount options are the stage's
// (stage/runtime.tsx, mountView). Nothing here is product code; the scripts
// beside it import it.
import {chromium} from 'playwright';
import {createServer} from 'node:http';
import {readFile,readdir} from 'node:fs/promises';
import {join,extname,resolve,sep} from 'node:path';
import {CHROMIUM_ARGS} from '../../../../src/render.mjs';

export const STAGE_OPTIONS={renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none'};

const PAGE=`<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#faf7ef}
#box{position:absolute;left:0;top:0;width:100%;height:100%}
.vm-view-host{position:absolute;inset:0}.vm-viewer{width:100%;height:100%}
</style></head><body><div id="box"><div class="vm-view-host"><div class="vm-viewer" id="v"></div></div></div>
<script src="/viewer.js"></script></body></html>`;

const TYPES={'.js':'text/javascript','.json':'application/json','.html':'text/html'};

// exports: {name: directory}; served at /<name>/...
export async function serve(bundle,exports){
  const roots=Object.fromEntries(Object.entries(exports).map(([k,v])=>[k,resolve(v)]));
  const server=createServer(async(req,res)=>{
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    let file=null;
    if(path==='/'){res.setHeader('Content-Type','text/html');res.end(PAGE);return;}
    if(path==='/viewer.js')file=bundle;
    else{
      const [,name,...rest]=path.split('/');
      if(roots[name]){const f=resolve(roots[name],...rest);if(f.startsWith(roots[name]+sep))file=f;}
    }
    if(!file){res.writeHead(404);res.end();return;}
    try{res.setHeader('Content-Type',TYPES[extname(file)]??'application/octet-stream');res.end(await readFile(file));}
    catch{res.writeHead(404);res.end();}
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  return {origin:`http://127.0.0.1:${server.address().port}`,close:()=>new Promise(r=>server.close(r))};
}

export async function launch(){
  const server=await chromium.launchServer({headless:true,args:CHROMIUM_ARGS});
  const browser=await chromium.connect(server.wsEndpoint());
  return {browser,pid:server.process().pid,version:browser.version(),close:async()=>{await browser.close();await server.close();}};
}

// A page at `width`×`height` with the host box, errors collected.
export async function openPage(browser,origin,width,height){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.goto(`${origin}/`);
  return {page,errors};
}

// Mounts the viewer on `/<name>/manifest.json` with the stage's options and
// keeps it as window.viewer; returns the mount time in ms and the API.
export async function mount(page,name,extra){
  return page.evaluate(async([name,options])=>{
    const t0=performance.now();
    window.viewer=await window.MachinomeViewer.mount('#v',`/${name}/manifest.json`,options);
    return {ms:performance.now()-t0,api:window.viewer.apiVersion,renderMode:options.renderMode};
  },[name,{...STAGE_OPTIONS,...extra}]);
}

// The stage's options refuse a clocked document (question 1 of the note):
// try them, record the refusal, and mount with the one option the viewer
// admits for a clocked machine changed, `renderMode: 'continuous'`.
export async function mountClocked(page,name,extra){
  let refusal=null;
  try{await mount(page,name,extra);}
  catch(error){refusal=String(error.message).split('\n')[0].replace(/^page\.evaluate: Error: /,'');}
  if(refusal===null)return {refusal,...await page.evaluate(()=>({api:window.viewer.apiVersion,renderMode:'on-demand'}))};
  await page.evaluate(()=>{document.getElementById('v').replaceChildren();});
  return {refusal,...await mount(page,name,{...extra,renderMode:'continuous'})};
}

// The stage's frames(): two animation frames.
export const twoFrames='new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())))';

// The resident memory of a process and its descendants, in kB, from /proc
// (the layer-6 test's treeRss, copied).
export async function treeRss(root){
  const parents=new Map();
  for(const name of await readdir('/proc')){
    if(!/^\d+$/.test(name))continue;
    const stat=await readFile(`/proc/${name}/stat`,'utf8').catch(()=>null);
    if(!stat)continue;
    parents.set(Number(name),Number(stat.slice(stat.lastIndexOf(')')+2).split(' ')[1]));
  }
  const tree=new Set([root]);
  for(let grew=true;grew;){grew=false;for(const [pid,ppid] of parents)if(!tree.has(pid)&&tree.has(ppid)){tree.add(pid);grew=true;}}
  let kb=0;
  for(const pid of tree){
    const status=await readFile(`/proc/${pid}/status`,'utf8').catch(()=>'');
    const m=/^VmRSS:\s+(\d+) kB$/m.exec(status);if(m)kb+=Number(m[1]);
  }
  return {processes:tree.size,kb};
}

export const median=xs=>{const s=[...xs].sort((a,b)=>a-b),n=s.length;return n%2?s[(n-1)/2]:(s[n/2-1]+s[n/2])/2;};
export const sha=async buf=>(await import('node:crypto')).createHash('sha256').update(buf).digest('hex').slice(0,16);
export {join};
