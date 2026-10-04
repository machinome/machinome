// The take transport bundled for a browser page, as the browser and viewer
// layers load it beside a viewer (the take-transport change; ADR-020):
// esbuild over transport/, the transports and the clocks with the pose rule
// they import, into one script that defines window.VideomakerTransport. Built
// once per worker. Not a test file: it registers no tests.
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as esbuild from 'esbuild';

export const TRANSPORT=join(dirname(fileURLToPath(import.meta.url)),'..','..','transport');
// The entry re-exports the transport's two modules. Written from their names,
// so the memo's reach (test/support/reach.mjs), which reads import lines, does
// not take it for an import of this file; transport/ is declared there.
const ENTRY=['take','clock'].map(name=>`export * from ${JSON.stringify(`./${name}`)};`).join('\n');
let bundled=null;
export function transportBundle(){
  return bundled??=esbuild.build({stdin:{contents:ENTRY,resolveDir:TRANSPORT,sourcefile:'transport-entry.ts',loader:'ts'},
    bundle:true,format:'iife',globalName:'VideomakerTransport',platform:'browser',target:'es2022',
    write:false,logLevel:'silent',legalComments:'none'}).then(result=>result.outputFiles[0].text);
}

// A page of the run's Chromium, `width` by `height`, holding one viewer host
// `#v` of the page's size, the viewer script and the transport, served with
// `files` (a path to {type, body} or to a file) by the run's one asset server.
export async function transportPage({browser,assets},{viewer,files={},width=640,height=360}){
  const served={
    '/':{type:'text/html',body:`<!doctype html><html><body style="margin:0"><div id="v" style="width:${width}px;height:${height}px"></div>`+
      '<script src="/viewer.js"></script><script src="/transport.js"></script></body></html>'},
    '/viewer.js':{type:'text/javascript',body:viewer},
    '/transport.js':{type:'text/javascript',body:await transportBundle()},
  };
  const release=assets.mount(async(req,res)=>{
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const entry=served[path]??files[path];
    if(!entry){res.writeHead(404);res.end();return;}
    try{
      res.setHeader('Content-Type',entry.type??'application/octet-stream');
      res.end(entry.body??await readFile(entry.file));
    }catch{res.writeHead(404);res.end();}
  });
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  try{await page.goto(`${assets.origin}/`);}catch(error){await page.close();release();throw error;}
  return {page,close:async()=>{await page.close();release();}};
}
