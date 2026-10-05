# Voron-2 mounting investigation — planning evidence

Status: parent-reviewed planning, 5 October 2026, under the pilot's advance
authorization. This file records pre-implementation diagnostics, not a product
fix or browser acceptance. Baseline sync, archive and integration remain gated
on implementation and actual Voron adversarial review.

## Inputs and ownership

- Viewer source: clean main `5838b97e1e1c10bf468d2f3a40a0c86a0a4448b7`.
- Viewer worktree: `/home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export`, branch `mount-voron-export`, same base.
- Project root: `/mnt/data/machinome-projects/3D-Printers/Voron-2`, `Voron2.4`; pinned export content inspected while clean at `a67893b88cd05e58eaa88bbf381455144f65117f`. Current HEAD is `52a9ad17439556648f7a3ab638e065137ad6d37d`, changing authority documentation only; subsequent unrelated project proposal files are owned by their separate cycle.
- Original portable export: `_build_resume_main_browser_export`, version 4; 232,347 bindings, 1,636 nodes, 1,565 model paths. Manifest approximately 26 MB.
- Manifest SHA256: `e9fee11746ff36a1f585f24a3db154b472a207bfc83db00e183ebdc96f2cb0c7`.
- Exported bundle SHA256: `a009e0ff0cbe320eb02869ef0553a19b4ad314e1acf608ae1edf76835aaea478`.

The original main-browser record in project `docs/evidence/resumed-main-validation.json`
receives HTTP 200 for page, bundle and manifest only, then its body-read observation
times out after the 30-second settle and 180-second DOM deadline. No model request,
mounted printer or screenshot was obtained. The record identifies source framework
`d22d0a1` and viewer `ccc05a6`; the later viewer base adds documentation only.
Existing document replay checks do not establish browser success.

Current authority: the pilot approved propose/apply through parent review, then
local rebase/merge of verified fixes after actual Voron adversarial review and
spec sync/archive. No pushing, publication or issues are authorized. This proposer
stops at uncommitted planning; the parent reviews and commits it before a different
agent applies.

## Bounded scratch experiments

The experiment file is `/tmp/voron-viewer-propose-SqxQpq/diagnose.mjs`, outside
tracked repositories. It bundles original viewer TypeScript with esbuild into
separately named scratch executables using source-loading instrumentation; no
tracked source or original export is edited. The entry reads the original manifest
and calls `assertRenderable`. The output labels validation/replay only, never mount.

Preparation commands are `node <scratch>/diagnose.mjs baseline`, `scoped`, `memo`
or `memo-evaluate`; execution is `timeout --signal=TERM --kill-after=5s <bound>s node
<scratch>/<mode>.cjs`. All launched diagnostic processes terminated. No browser,
model fetch, project shared cache or project log write occurs in these runs.

### Observed full-table rebuilding in the baseline

Instrumentation adds logging at `resetStore` and binding root-map preparation,
then stops at a later root-map rebuild after generation 3. It changes no calculation
before that deliberate diagnostic stop. The observed sequence was:

```text
parsed: 232347 bindings, version 4
reset: 125001 nodes, generation 0
reset: 125000 nodes, generation 1
reset: 125001 nodes, generation 2
table-prepare: generation 3
reset: 483728 nodes, generation 3
table-prepare: generation 4
stopped: diagnostic stop after three resets
elapsed: 4196.361556 ms; peakNodes: 483728
```

This establishes that the table exceeds the trigger by distinct node count,
and that validation rebuilds it again immediately. It does not assert that
every binding is a unique expression or that this is the only browser cost.

### Full scoping alone retains repeated profile reachability

The `scoped` entry encloses the unchanged validation in `withExpressions` and
counts `inspectProfileExpression`'s actually visited distinct IDs per call.
A bounded 12-second run reports one table preparation, then:

```text
500 inspection calls: 671993 visited-node occurrences
1000 inspection calls: 1487870 visited-node occurrences
timeout exit 124; validation did not complete
```

An earlier separately fenced scoped run logged individual walks above 300,000
distinct nodes per call and timed out at 30 seconds. Its logging adds overhead;
neither elapsed timeout is a browser benchmark. Together these establish the
second repeated traversal mechanism after removing table rebuilds.

### Reusing completed negative walks within this single operation

The `memo` scratch experiment retains IDs from a traversal only after it
successfully returns false, and skips those IDs on later inspections in the same
protected operation. It does not bypass parsing, binding ordering/closure checks,
reserved-call structural checks or undeclared-name checks. The memo is valid
only for this stable single-document, single-generation experiment; production
ownership and adversarial guard tests are still required.

```text
one table preparation: generation 0
500 inspection calls: 20493 visited IDs
1000 inspection calls: 36791 visited IDs
1500 inspection calls: 485689 visited IDs
28500 inspection calls: 610091 visited IDs
validated: 4231.932248 ms; nodes/peakNodes 610546; generation 0
```

The `memo-evaluate` experiment independently repeated validation in 4312.595046 ms,
then evaluated all 1,053 rigid operation scalars at driver defaults through the
original evaluator in one protected operation. The expected between-operation
reset happened, the table was prepared at generation 1, and every operation
scalar was finite; total elapsed 6307.410938 ms. It did not evaluate flexible
meshes, compare world matrices, load assets or render any pixels.

## Conclusion and limits

Two concrete validation costs are established on the original manifest:
reclamation between expression checks forces repeated full-table preparation,
and repeated negative profile checks expand shared aliases independently.
The scratch intervention removes both without changing document data and makes
validation terminate; it is design evidence, not an implemented production fix.
Actual browser mounting, full geometry, flexible shapes, instructed poses,
reload/disposal and malformed-input preservation remain mandatory apply/review
gates. The separate web-capture fetch failure remains undiagnosed by this record.

## Reproduction annex independent of the temporary file

The instrumentation below reproduces the experiments without the original
temporary script. Create it only in a new scratch directory using `apply_patch`,
pass that directory as argument 3, and verify the source checkout is at the
recorded viewer base before bundling. The final version counts aggregate visits;
the earlier per-call observation preceded that logging refinement. Esbuild's
build/stdin/plugin API was checked through Context7 (`/evanw/esbuild`).

```js
import { build } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/node_modules/esbuild/lib/main.js';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const widget = '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget';
const mode = process.argv[2] ?? 'baseline';
const scratch = resolve(process.argv[3]);
const entry = `
import { readFileSync } from 'node:fs';
import { assertRenderable } from './src/viewer';
import { expressionMetrics, expressionGeneration, withExpressions } from './src/expressions';
import { evalExpr } from './src/evaluator';
const start = performance.now();
const doc = JSON.parse(readFileSync('/mnt/data/machinome-projects/3D-Printers/Voron-2/_build_resume_main_browser_export/manifest.json', 'utf8'));
console.log(JSON.stringify({phase:'parsed', ms: performance.now()-start, bindings: doc.bindings.length, version:doc.version}));
const load = () => assertRenderable(doc, '/original-voron/manifest.json');
try { const loaded = ${mode !== 'baseline' ? 'withExpressions(load)' : 'load()'};
console.log(JSON.stringify({phase:'validated', ms:performance.now()-start, metrics:expressionMetrics(), generation:expressionGeneration()}));
if (${mode === 'memo-evaluate'}) {
  let count=0;
  const scope = {time:0,drivers:Object.fromEntries(Object.entries(doc.drivers).map(([id,d])=>[id,d.default])),get bindings(){return loaded.table.roots()}};
  withExpressions(()=>{
    const visit=(node)=>{
      for(const op of node.operations) for(const ex of op[0]==='r'?[op[1]]:op[1]) {
        try { const v=evalExpr(ex,scope); if(!Number.isFinite(v)) throw Error('nonfinite'); count++; }
        catch(e) { console.log(JSON.stringify({phase:'pose-error',node:node.name,expression:ex,count,error:String(e)})); throw e; }
      }
      for(const ch of node.children??[]) visit(ch);
    }; visit(doc.root);
  });
  console.log(JSON.stringify({phase:'posed-operations-only', count, ms:performance.now()-start}));
}}
catch(e) { console.log(JSON.stringify({phase:'stopped', error:String(e), ms:performance.now()-start, metrics:expressionMetrics(), generation:expressionGeneration()})); }
`;
await build({
  stdin:{contents:entry, resolveDir:widget, loader:'ts'}, bundle:true,
  platform:'node', format:'cjs', outfile:`${scratch}/${mode}.cjs`,
  define:{__VIEWER_API_VERSION__:'29',__DOCUMENT_VERSIONS__:'[1,2,3,4,5,6,7,8,9,10,11,12,13]',__WORKER_SOURCE__:'""'},
  plugins:[{name:'observe',setup(build){
    build.onLoad({filter:/src\/expressions\.ts$/},args=>{
      let source = readFileSync(args.path,'utf8').replace('function resetStore(): void {', `function resetStore(): void { console.log(JSON.stringify({phase:'reset', nodes:nodes.length, generation:storeGeneration}));`);
      source = source.replace('export function inspectProfileExpression(', `let probeInspections = 0; let probeVisits = 0; let probeClear = new Set<NodeId>();\nexport function inspectProfileExpression(`);
      source = source.replace('  let found = false;\n  const seen', `  probeInspections += 1; let found = false;\n  const seen`);
      source = source.replace('    if (seen.has(id)) continue;', `    if (seen.has(id) ${mode.startsWith('memo') ? '|| probeClear.has(id)' : ''}) continue;`);
      source = source.replace('  return found;\n}', `  probeVisits += seen.size; ${mode.startsWith('memo') ? 'if (!found) for (const id of seen) probeClear.add(id);' : ''} if(probeInspections % 500 === 0) console.log(JSON.stringify({phase:'profile-inspections', calls:probeInspections, visits:probeVisits, memo:probeClear.size})); return found;\n}`);
      return {contents:source,loader:'ts'};
    });
    build.onLoad({filter:/src\/bindings\.ts$/},args=>({
      contents:readFileSync(args.path,'utf8').replace('const map = new Map<string, NodeId>();', `console.log(JSON.stringify({phase:'table-prepare', generation:expressionGeneration()})); if (expressionGeneration()>3) throw Error('diagnostic stop after three resets'); const map = new Map<string, NodeId>();`),loader:'ts',
    }));
  }}],
});
```

Run each mode separately, e.g. `node <scratch>/diagnose.mjs baseline <scratch>`,
then `timeout --signal=TERM --kill-after=5s 50s node <scratch>/baseline.cjs`;
use `scoped` with a 12-second bound and `memo`/`memo-evaluate` with 25-second
bounds. This scratch memo is confined to one protected validation. Its
module-level set has no cross-document/generation guard and must not be copied
into product code. No browser or model resources are involved in these experiments.
