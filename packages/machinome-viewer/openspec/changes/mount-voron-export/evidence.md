# Voron-2 mounting investigation — planning evidence

Status: parent-reviewed planning, 5 October 2026, under the pilot's advance
authorization. This file records pre-implementation diagnostics and partial
application with a new red browser gate, not browser acceptance. Baseline sync, archive and integration remain gated
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

## Application progress — stopped at a new full-browser blocker

The different apply agent worked from planning commit
`0ca25281b4905b5072b2809feb1a0e31e0ac250b` over base `5838b97`.
Strict planning validation passed. Project HEAD was now `1d51587`, from
other authorized project work; the frozen acceptance export hashes still
match the pins above. A read-only inventory records 1,568 files,
127,961,024 bytes, 1,636 nodes, 1,565 distinct model paths and 232,347
bindings. All file hashes are in
`/tmp/voron-viewer-apply-Yi3m3o/input-pins.json` (SHA256
`eb99436946f39cd264b31d84fab8404f7cac9ed5cb6253649863da6a633a6925`).
The viewer primary remains clean. A worktree-only `node_modules` symlink
reuses installed dependencies; no install or shared-venv mutation occurred.

### Counted red and green

`npm test --prefix machinome_viewer/widget -- src/validation-pressure.test.ts`
first ran against base implementation plus source-only counters and the two
new regressions: **2 failed**. With the threshold lowered to 5, one valid
80-binding document with 30 operation readers and a flexible parameter
prepared its binding map **91** times and changed generation **171** times.
Shared-prefix profile inspection visited **7,562** nodes against **303**
distinct nodes. These are actual preparation/structural-visit counters,
not timing assertions.

The bounded production correction wraps all synchronous `assertRenderable`
work in `withExpressions` and owns negative structural facts in a local
inspector tied to one binding map and expression generation. Reserved-name
direct-callee checks precede shortcuts; positive/failed walks publish no
negative facts. Running Bounds retain the original inspector. The trigger
remains 125,000. The same command then passed **2/2**, with **1** map
preparation, **0** generation changes and **303** structural visits. A later
operation reclaimed the graph and reconstructed the exact expected value,
with the map preparation count rising to 2 as expected.

The regression file was expanded to **11 passing tests**, including alias,
bare/indirect profile-name, arity/index, dead-branch/flexible-parameter,
positive/failed traversal, document-meaning and late-unreferenced malformed
entry cases. Focused evaluator/expression/binding/document/lifetime/profile
suites passed **233 tests, 1 skipped** before this expansion (the existing
profile installed-export test skip remains). `npm run typecheck --prefix
machinome_viewer/widget` passed; `npm run build --prefix
machinome_viewer/widget` built the candidate. Full widget/Python/browser
acceptance and parent adversarial review remain outstanding.

### Fresh actual portable-page red and candidate failure

The read-only harness is
`/tmp/voron-viewer-apply-Yi3m3o/browser_probe.py`. Commands used the existing
workspace `.venv/bin/python`:

```text
python /tmp/voron-viewer-apply-Yi3m3o/browser_probe.py base
python /tmp/voron-viewer-apply-Yi3m3o/browser_probe.py candidate --bundle /home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export/machinome_viewer/widget/dist/machinome-viewer.js
```

Both serve the original page/manifest/assets unchanged from the frozen
directory on loopback. The candidate alone substitutes the bundle route via
Playwright `route.fulfill(path=...)`. Chromium **151.0.7922.34** runs headless
with ANGLE/SwiftShader at 1400×1100. The unchanged page SHA256 is
`5a9b57d06fc62ff8acf1d4d3e7c51a7a9b1ee0a01415684a17aecbd3c1fa4605`.
The tested candidate bundle SHA256 is
`085c8a3038ee677d95123b4c31f5ebca953011a16dcc348c9ff10e4829ea3f82`.

Base: **31.406 seconds**, only **3 requests/3 HTTP-200 responses** (page,
bundle, manifest), then the body-read deadline expired. No model request
occurred. Evidence: `base.json`, `base.log`, `base-cleanup.json` in that
scratch directory. `base.json` SHA256:
`69e616a5893a306c1ec58582aefac1ab8aeb79331b08cc2e3b6cff41249477b8`.

Candidate: **15.851 seconds**; all **1,568 unique URLs** requested (the
same three plus all **1,565 model paths**), **1,278 HTTP-200 responses**
including **1,275 models**, and **290 failed model requests**, all named
`net::ERR_INSUFFICIENT_RESOURCES`. There were no HTTP errors or page-error
events, but the portable page read **`machinome-viewer: Failed to fetch`**
and contained **zero canvases**. An 8.756-second response checkpoint already
contained the resource errors; exact per-request timestamps and maximum
simultaneously pending request count were not instrumented in this first
gate and are **not claimed**. Source inspection confirms `WidgetTree`
constructs all descendants and starts their `loadModel` work immediately.

All exact failed URLs and response URLs are retained in `candidate.json`
(SHA256 `968cc6bd54e8fef9435ac01b389f6296aecada90f7235ff59476106f608c5752`).
For example:
`/models/simulation/.cache/part-0606-__FittedSourceSolid_,_simulation_fits.py__,source_id=606-a9ac442904e5.stl`
and the following part 0607 failed with that same browser resource error.
`candidate.log` retains response progress. The inspected
`candidate-rest.png` shows only the named fetch failure, **not a printer**;
its SHA256 is `69875f446f261ce2ab72fa83367fa6e4cdf3c14c56f2fb40609a18ae5f14d0ae`.
No finite assembly bounds, poses, belts or mounted-printer screenshot were
accepted. Memory was not measured by this preliminary failure probe.

Each harness worker owns a separate process group, has a 115-second parent
fence plus bounded 5-second termination/kill paths, and bounded browser
close. Base group **140556** and candidate group **141532** both exited
with no surviving group members, recorded by their cleanup JSON files.
Logs/screenshots were written only in the unique scratch directory. No
project input, project cache/log or viewer-primary write occurred.

### Out of scope, found while applying

**Unresolved at the initial apply halt; the parent subsequently approved the revised scope:** the actual full printer exceeds Chromium's concurrent
resource-request headroom after validation succeeds. The parent directed
application to stop for a reviewed proposal revision before any production
loading change. No loader concurrency fix was attempted. The current
validation implementation and tests remain uncommitted for that review;
baseline sync, ADR amendment, archive, implementation commit and integration
have not occurred. This is a new actual-browser red gate, not a successful
mount and not resolution of the separate capture-fetch wart.

## Conclusion and limits

Two concrete validation costs are established on the original manifest:
reclamation between expression checks forces repeated full-table preparation,
and repeated negative profile checks expand shared aliases independently.
The scratch intervention removes both without changing document data and makes
validation terminate; the later partial application also makes its counted
regressions green, but exposes the resource-failure gate recorded above.
Actual browser mounting, full geometry, flexible shapes, instructed poses,
reload/disposal and malformed-input preservation remain mandatory apply/review
gates. The separate web-capture fetch failure remains undiagnosed by this record.

## Geometry-admission revision evidence

After the applier confirmed all writes stopped, the original proposer inspected
the actual `tree.ts` call sites and pinned dependency source. In three.js 0.156.1,
`FileLoader.load` starts fetch immediately for each distinct URL; only overlapping
same-URL callbacks are shared. `STLLoader.loadAsync` returns separately parsed
geometry per callback and does not provide the newer manager-abort API. Current
upstream API documentation was fetched through Context7 (`/mrdoob/three.js`),
but the installed release's source is the authority for this implementation.
The geometry admission/ownership correction is proposed only; no loader code
was edited by either the proposer or the paused applier at this checkpoint.

A separate bounded read-only network control on Chromium **151.0.7922.34**
retrieved every actual model path using four async workers, consuming each
entire response body before taking another path. It reported:

```json
{"phase":"network-only-not-mount","bound":4,"peak":4,"completed":1565,"bytes":59271584,"failures":[],"ms":1962.3999999761581}
```

This grounds the conservative private four-group proposal: resource reads remain
concurrent and every printer model is retrieved without the observed resource
failures. It does not measure STL parse/render cost, prove an optimum or browser
limit, or establish mounting. It creates no model cache and discards each response
buffer after counting bytes. Existing project/export files remain unchanged.

The control lived at `/tmp/voron-viewer-network-i7Zcdy/probe.py` and ran through
the ordinary native `.venv/bin/python`, with an outer 50-second timeout,
40-second browser operation timeout and 5-second bounded browser close. It
returned normally; its browser and loopback server closed in `finally`.
To reproduce without that temporary file, serve the original export read-only
on loopback, open a same-origin blank control page (not the original portable
page), collect its manifest's model paths in document order, and evaluate:

```js
async (paths) => {
  let cursor=0, active=0, peak=0, completed=0, bytes=0;
  const failures=[], start=performance.now();
  const work=async()=>{
    while(cursor<paths.length){
      const path=paths[cursor++]; active++; peak=Math.max(peak,active);
      try {
        const response=await fetch(path,{cache:'no-store'});
        if(!response.ok) throw Error(String(response.status));
        bytes+=(await response.arrayBuffer()).byteLength; completed++;
      } catch(e) { failures.push({path,error:String(e)}); }
      finally { active--; }
    }
  };
  await Promise.all(Array.from({length:4},work));
  return {phase:'network-only-not-mount',bound:4,peak,completed,bytes,
          failures,ms:performance.now()-start};
}
```

The preliminary candidate diagnostic's process exit zero and its status
“responsive portable page” describe observation completion only; with 290 failed
requests and zero canvases it is explicitly red. The revised true acceptance
harness must exit nonzero for request/HTTP/page errors or an absent complete
mount. No screenshot of its error page may be described as a mounted printer.

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
