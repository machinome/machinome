// What the renderer serves from a model's export (the
// serve-what-the-viewer-reads change, design D1 and D2): exactly the files
// the viewer reads, as the framework's export document defines them. A rigid
// node of the manifest's `root` tree names its model, `model`, and each of
// its markings names its artifact, `markings[].model`, both beneath the
// export's `models/`; a node's `children` are nodes. Nothing else of the
// manifest is a file the viewer reads: the printed-piece inventory
// (`pieces[].models` names the same files again, `pieces[].sources` the files
// a piece was built from, relative to the project) and every other string are
// provenance or data, never served and never opened.
import {readFile,stat} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {contained} from './episode.mjs';

// The files the viewer reads from an export whose manifest is `manifest`:
// one entry per distinct path, `{path, field, node}`, with the field path in
// the manifest that first names it and the node it belongs to. Depth first,
// in each node's own key order, which is the order the renderer served them
// in before this module, so an export's URLs and their order are unchanged.
export function viewerFiles(manifest){
  const files=new Map();
  const take=(path,field,node)=>{if(typeof path==='string'&&!files.has(path))files.set(path,{path,field,node});};
  function visit(node,field){
    if(!node||typeof node!=='object')return;
    const name=typeof node.name==='string'?node.name:'unnamed';
    for(const [key,value] of Object.entries(node)){
      if(key==='model')take(value,`${field}.model`,name);
      else if(key==='markings'&&Array.isArray(value))value.forEach((marking,i)=>
        take(marking?.model,`${field}.markings[${i}].model`,`marking ${marking?.name??i} of ${name}`));
      else if(key==='children'&&Array.isArray(value))value.forEach((child,i)=>visit(child,`${field}.children[${i}]`));
    }
  }
  visit(manifest?.root,'root');
  return [...files.values()];
}

const isFile=file=>stat(file).then(s=>s.isFile(),()=>false);

// The URL of each file the viewer reads, `/model/<path>`, and the file it
// serves. Refuses, naming the field, the node and the path, a file outside
// the export directory or one the export does not hold.
export async function exportFiles(manifestPath){
  const root=dirname(resolve(manifestPath));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  const served=new Map();
  for(const {path,field,node} of viewerFiles(manifest)){
    const file=resolve(root,path),named=`${field} (${node}) names ${path}`;
    if(!contained(root,file))throw new Error(`Export file outside the export: ${named}, which lies outside the export ${root}; export the model again so its manifest names only files inside it`);
    if(!await isFile(file))throw new Error(`Export file missing: ${named}, which the export ${root} does not hold; export the model again so the export holds every file its manifest names`);
    served.set('/model/'+path,file);
  }
  return served;
}
