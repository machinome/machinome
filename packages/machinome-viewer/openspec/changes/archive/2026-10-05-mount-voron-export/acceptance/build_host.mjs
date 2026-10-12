import { build } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/node_modules/esbuild/lib/main.js';
await build({stdin:{contents:`
export { mount } from './src/viewer';
export { WidgetTree } from './src/tree';
export * as THREE from 'three';
export { expressionMetrics } from './src/expressions';
export { withExpressions } from './src/expressions';
export { evalExpr } from './src/evaluator';
`,resolveDir:'/home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export/machinome_viewer/widget',loader:'ts'},
 bundle:true,minify:true,format:'iife',globalName:'HostProbe',
 outfile:'/tmp/voron-viewer-apply-Yi3m3o/host-diagnostic.js',
 define:{__VIEWER_API_VERSION__:'29',__DOCUMENT_VERSIONS__:'[1,2,3,4,5,6,7,8,9,10,11,12,13]',__WORKER_SOURCE__:'""'}});
