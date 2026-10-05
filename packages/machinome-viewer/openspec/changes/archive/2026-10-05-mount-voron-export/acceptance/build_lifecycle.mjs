import { build } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/node_modules/esbuild/lib/main.js';
import { readFileSync } from 'node:fs';
const red=process.argv.includes('--red');
await build({stdin:{contents:`
export { mount } from './src/viewer';
export { WidgetTree } from './src/tree';
export { RunRuntime } from './src/run/runtime';
`,resolveDir:'/home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export/machinome_viewer/widget',loader:'ts'},
 bundle:true,minify:true,format:'iife',globalName:'LifecycleProbe',
 outfile:`/tmp/voron-viewer-apply-Yi3m3o/lifecycle-${red?'red':'diagnostic'}.js`,
 plugins:red?[{name:'controlled-pre-guard',setup(build){build.onLoad({filter:/\/src\/viewer\.ts$/},args=>{
   const source=readFileSync(args.path,'utf8');
   const guard='if (disposed) { runtime?.dispose(); runtime = undefined; }\n        else next.update(scope());';
   if(!source.includes(guard))throw Error('Expected exact reviewed guard not found');
   return {contents:source.replace(guard,'next.update(scope());'),loader:'ts'};
 })}}]:[],
 define:{__VIEWER_API_VERSION__:'29',__DOCUMENT_VERSIONS__:'[1,2,3,4,5,6,7,8,9,10,11,12,13]',__WORKER_SOURCE__:'""'}});
