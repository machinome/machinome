# Voron-2 mounting investigation — planning and implementation evidence

Status: implementation and viewer/document acceptance completed, with parent
adversarial-review task 4.3 accepted on 5 October 2026 in `parent-review.md`.
Earlier planning/red records below remain historical evidence. Final results
are recorded in the last replay section and retained under `acceptance/`.
ADR amendment text and Proposed ADR-078 are drafted for parent text review;
baseline sync, archive, implementation commit and integration remain on hold. A separate
project-owned intended CoreXY geometry mismatch remains unresolved; successful
document-language parity does not resolve it.

## Inputs and ownership

- Viewer source: clean main `5838b97e1e1c10bf468d2f3a40a0c86a0a4448b7`.
- Viewer worktree: `/home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export`, branch `mount-voron-export`, same base.
- Project root: `/mnt/data/machinome-projects/3D-Printers/Voron-2`, `Voron2.4`; pinned export content inspected while clean at `a67893b88cd05e58eaa88bbf381455144f65117f`. The historical proposal-time HEAD was `52a9ad17439556648f7a3ab638e065137ad6d37d`, changing authority documentation only; later project commits and unrelated proposal files belong to their separate cycles. The acceptance source is the frozen export's file hashes, not a claim that this remains the current project HEAD.
- Original portable export: `_build_resume_main_browser_export`, version 4; 232,347 bindings, 1,636 nodes, 1,565 model paths. Manifest approximately 26 MB.
- Manifest SHA256: `e9fee11746ff36a1f585f24a3db154b472a207bfc83db00e183ebdc96f2cb0c7`.
- Exported bundle SHA256: `a009e0ff0cbe320eb02869ef0553a19b4ad314e1acf608ae1edf76835aaea478`.

The original main-browser record in project `docs/evidence/resumed-main-validation.json`
receives HTTP 200 for page, bundle and manifest only, then its body-read observation
times out after the 30-second settle and 180-second DOM deadline. No model request,
mounted printer or screenshot was obtained. The record identifies source framework
`d22d0a1` and viewer `ccc05a6`; the later viewer base adds documentation only.
Existing document replay checks do not establish browser success.

Authority: the pilot approved propose/apply through parent review, then
local rebase/merge of verified fixes after actual Voron adversarial review and
spec sync/archive. No pushing, publication or issues are authorized. At the
proposal checkpoint, the proposer stopped at uncommitted planning for parent
review/commit before different-agent application. The current document handoff
stops before parent-owned baseline sync/archive/implementation commit.

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

## Final application — historical handoff before parent review

Application resumed only after the parent-reviewed geometry-loading amendment
commit `66984ab7de224c57b0555ff57e3ee21f9dd8a5f1`. Production code remains
uncommitted in the isolated worktree. The finite expression trigger is still
125,000; there is no asynchronous expression scope, persistent negative-profile
cache, new public loader option, retry, permanent STL cache or producer rewrite.

The private geometry admission module shares four FIFO distinct-URL groups
across the bundle/page. Models and markings reserve their mesh/material identity
before queuing. Overlapping subscribers retain independent STLLoader parses and
mutable geometry; groups stop accepting subscribers after any actual settlement.
Owners cancel their own queued work, retain active admission until real settlement,
and dispose late/prepared resources exactly once. Initial/reload failure and
targeted preparations clean up their candidate work without replacing last-good
geometry/driver state for an asset failure. Pending runtime readiness and pending
trees are covered by handle disposal.

### Additional controlled red/green ownership evidence

The deferred-loader fan-out regression first observed **18 initially started,
18 peak, 18 completed** jobs across two trees, models and markings. The admitted
implementation reports **4 initially started, 4 peak, all 18 completed**, with
reverse-order settlement. Queue tests cover cancellation without requests,
active capacity held through settlement, exact original errors, completed-group
closure, late-result disposal and failed prepare-before-mutation replacement.

The parent's independently added geometry regression was red: cancellation in
the microtask between the STL wrapper and admission continuation leaked the
returned geometry (**0 disposals, expected 1**). Admission now owns an explicit
abandoned-result disposer; the load consumer also cleans up a returned result if
cancellation lands after admission. The parent regression and cancellation after
0/1/2/3/4 microtasks pass with exactly one disposal and no late attachment.

A separate runtime-readiness diagnostic freezes a second real running-fixture
runtime's ready promise, disposes the handle, then releases readiness. A scratch
instrumentation build removing only the post-await guard is red with **61
post-disposal tree updates**. Current production source yields **0**, two runtime
starts, two disposals and zero remaining canvases. The scratch-only red build does
not edit production. Its raw results/scripts and owned-group cleanup are retained.

Parent review identified an abandoned queued group's FIFO-position reuse. The
deterministic red occupies four slots, queues X then Y, cancels X's owner, queues
new X, and releases a slot: it observed **new X before Y**. Closing the emptied
group's URL-map eligibility immediately turns this green (**Y before new X**);
the queue may retain an inert tombstone, and identity-safe close cannot delete a
newer group for the same URL. Geometry tests now pass **11**, plus the parent's
one race regression. No speculative sequential-batch refactor was made: the
owner-cancellation loop is synchronous, whereas active-slot release occurs in a
promise-finally microtask and cannot interleave that supported failure path.

### FIFO-corrected test and build gates (before final artifact guard)

From the worktree widget directory, `npm test -- --maxWorkers=1` passed **1,700
tests, 2 existing skips**, across **65 passing files, 1 skipped file** in 106.73
seconds. The skips remain `profile-contact`'s missing actual Curta document and
the missing installed Curta profile benchmark input.
`npm run typecheck` and `npm run build` passed. An earlier concurrent full-suite
attempt had **1 timing-only Pascaline throughput failure** (2,209 ticks/s versus
the unchanged >2,400 requirement), **1,688 passes and 2 skips**; its focused
14-test rerun passed at 2,593 ticks/s, and the subsequent isolated full suites
passed. No timing requirement was weakened.

With `PYTHONPATH` exactly the candidate worktree and the existing workspace
`.venv/bin/python`, the final command
`python -B -m pytest -q tests/test_asset_load_order.py tests/test_profile_document.py tests/test_bundle.py tests/test_widget_e2e.py`
passed **81 tests, no skips, 33 existing Pillow deprecation warnings**, in 97.52
seconds. The larger-than-budget pixel regression compares two simultaneous
viewers, eight coincident model parts and two markings under reversed real server
completion delays; disposing one owner leaves the other's PNG unchanged, and
completion-order PNGs are equal.

That extra small stress test initially reported Chromium `ERR_ABORTED` despite
both parsed mounts completing and no fetch rejection. Paired base/candidate CDP
diagnostics showed `canceled:true` Fetch events immediately **after** the same
STL body was completely read, **before** any dispose/page close. Example candidate
request `221660.11`, `plate3.stl`: body done at 1791222153.165, cancellation at
1791222153.167927, both mounts ready at 1791222153.348. Base `221526.10`,
`plate2.stl`: done at 1791222151.744, cancellation at 1791222151.745397, mounts
ready at 1791222151.919. The parent approved only this bounded test-observer
qualification: every expected unique STL must finish with HTTP 200 and the exact
expected byte count; each canceled ERR_ABORTED consumes a distinct same-URL
completed-body fact preceding that event. Pre-completion/other request failures,
fetch/parse/page errors still fail. This is not product error suppression or a
retry. Raw IDs/times and base comparison are retained. **The actual full portable
page keeps the strict zero-request-errors gate unchanged.**

### FIFO-corrected portable page and host acceptance (before final artifact guard)

Final candidate production bundle SHA256:
`0b48ad5bb9ceaa60dc7614ade946e557fc225d75a32e0ca51318903068e52894`.
Final source-only host diagnostic SHA256:
`8d6eb82cb995ffa4a661822e6e3d8a8d8473104f89e4f9731e43c6370a086e27`.
Neither bundle was written into the original export.

The production bundle route alone was substituted in the original complete
portable page. Chromium 151.0.7922.34/ANGLE SwiftShader at 1400×1100 received
**1,568 HTTP-200 responses, all 1,565 model paths, zero failed requests, zero
page/HTTP errors**, with observed pending-model peak **4**. Complete mount/rest
screenshot gate elapsed **59.328 seconds**. Raw JSON
`acceptance/queued-public-fifo-final.json` SHA256:
`f0e98ae5793670cb7901f3c6b448e028ebfc1465afe7c744664d6e520513abfe`.
The screenshot was inspected and shows the assembled enclosure plus correct
default readouts; SHA256
`3c774d0b038c2dbae5a61a4d528049e7bc557e94e147d1a5fe42d39f7f9bdece`.
Browser graceful close exceeded its five-second allowance, explicitly recorded
as cleanup timeout, not render/request failure. The owned supervisor terminated
the complete group and confirmed **zero survivors**.

The separate source-instrumented host uses the **same full untouched document and
all assets**, not reduced/fake geometry. It verified **1,636 nodes/1,565 model
paths**, published defaults, Home **250/250/10/e0**, Center **125/125/20/e0**,
Present **125/30/180/e20**, and restored defaults. It advances the actual public
instruction handle using a controlled monotonic clock, not direct target posing.
Nine representative world matrices (bed, gantry/crossbeam/head, chain endpoints
and three belts) matched independent NumPy operation replay with maximum error
**2.842170943040401e-14**. Three full flexible meshes matched independent Python
molejo vertex arrays with maximum difference **0**, and their complete face/index
arrays were exactly equal at all five poses: front-left belt **11,526 vertices /
23,048 faces**, each CoreXY belt **37,126 / 74,248**.

All whole-assembly bounds were finite. Rest/restored/reloaded bounds were
min `[-90,-51,-143.0100235595703]`, max
`[340,483.77757709704366,378.98999169921876]`. After reload, the harness explicitly
rechecked the full 1,636/1,565 counts, default readbacks and finite bounds before
disposal. It received **3,134 HTTP-200 responses** across mount and reload, with
zero browser errors. Host gate elapsed **100.847 seconds**; JSON
`acceptance/host-fifo-acceptance.json` SHA256:
`f3bfd2e666ee2091d542ec88bdea33eae86e8cbc72f0ab0a5f7efa4e301f3167`.
Rest, Present and supplemental Present-interior PNGs were inspected. The
enclosure naturally hides the gantry; the supplemental image uses only the
existing public `setVisible(['enclosure'],false)` control, then restores it.
No resource/document pruning occurs. Present interior shows the raised gantry,
toolhead and bed. PNG SHA256 values are respectively
`cc0c1d5072efe044b2cebd969bec1f7a2ec961a1ffce6a761f4eace2f8c81363`,
`2a57addd4a93e5d50030b67354dff775081b79c65627d50eb08baa30555f42c7`,
`4b815208c1ba92c99c29f84a7383cee6ec3ef2a75a1e69786cf64941df3ed468`.

Final supervised groups all returned zero with **survivors []**: widget 231798
(107.44 seconds, peak aggregate sampled RSS 709,464 KiB); portable 234726
(59.59 seconds, 232,688 KiB); host 234832 (101.66 seconds, 2,105,416 KiB); Python
234957 (98.01 seconds, 667,964 KiB); runtime lifecycle 235075 (1.60 seconds,
165,092 KiB). These are diagnostic process-group RSS samples, not a universal
memory/performance guarantee. Each supervisor has a 225-second deadline plus
bounded five-second TERM/KILL waits, below 240 seconds total.

### Separate unresolved project geometry finding and stopping point

The first independent physical-reference comparison genuinely failed: CoreXY
`gantry/belt_a/strap` and `gantry/belt_b/strap` differ approximately **16.06 mm**
from the unchanged Python floor-modulo prototype. The project's original helper
uses Python `%`; the published document contract uses truncated remainder
(`math.fmod` / OpenSCAD). A native OpenSCAD echo and parent contract review confirm
the viewer's existing semantics. Only the scratch document-parity oracle was
adapted to that contract. **This does not prove intended/native belt correctness.**

Retained `project-sweep-divergence.json` SHA256
`f6b2346e89a3311f23569ad0d335bc7e834f6887c8f13c5ecd3fb6daa0050155`
records all five poses. Belt A parameters **a11/a17**, belt B **a3/a17** differ by
2π; both CoreXY mesh differences are 16.05999755859375 mm at rest/Home/Center/
restored and 16.059978485107422 mm at Present. The front-left drive belt agrees
at all poses. Original expression-helper source SHA256 is
`96c8fc39abc97e1ed8ca40e3173a6d6e6f30e1774337f56e0003a7c0bcd827ea`.
The project proposer owns the separate `publish-voron-corexy-signed-wraps` cycle;
this viewer change makes no numeric or frozen-input edits.

All **1,568 original export file hashes / 127,961,024 bytes** were independently
rechecked unchanged against `input-pins.json`; viewer primary `git status --short`
is empty. No shared-venv installation, project input/cache/log write, push,
publication, issue, baseline sync, ADR promotion, archive or implementation commit
occurred. Reproduction scripts, raw red/green logs/JSON, cleanup records, hashes
and inspected PNGs are retained under `acceptance/`, with explicit scratch-copy
execution instructions. Implementation stops here for the parent's **task 4.3**
adversarial acceptance review; downstream repository completion remains gated.

### Final post-review artifact-disposal correction and current-bundle replay

Parent review subsequently found a second bounded disposal race: after
`artifactChanged`'s aggregate preparation promise resolved, disposal could occur
before replacement attachment. The parent's parameterized 0–10 microtask test
was independently reproduced red: **3 failed / 9 passed**, with late attachment
at steps 3/4/5. A disposed check immediately after aggregate model/decal
preparation now rejects before **either** commit route. Parent tests pass **12**;
the geometry regression file now passes **15**, including four additional
shared-path model-and-marking disposal timings. Red/green logs and cleanup
records are retained as `artifact-disposal-*` and `artifact-marking-green-*`.

All following results use the final guarded source, not the earlier FIFO-only
bundle. Current production bundle SHA256:
`02bde914f9d30f4d5866d2eb64cdb76abb73be1aac77a949ca3475ccc7a132b4`.
Current separately instrumented host bundle SHA256:
`f3c1cac84be8d2ef1fbea1f511a9f3a0e0903feabbd416eeb1c0fa8926f04cb4`.
`npm run build`, `npm run typecheck` and `git diff --check` pass.

The fresh complete `npm test -- --maxWorkers=1` result is **1,715 passed / the
same 2 existing skips**, 65 passing files and one skipped file, **110.81 seconds**.
The same candidate-PYTHONPATH relevant Python/browser command above passes
**81 / no skips / 33 unchanged Pillow warnings**, **109.88 seconds**. The fresh
runtime-ready disposal diagnostic still reports two starts, two disposals,
**zero post-disposal updates and zero canvases**.

Fresh unchanged portable-page acceptance: **1,568 HTTP 200, every 1,565 model
path, zero HTTP/request/page errors, pending-model peak 4**. Probe elapsed
**69.677 seconds**; the separate five-second graceful-close timeout remains
truthfully recorded and the owned group has no survivors. Result
`acceptance/queued-public-artifact-final.json` SHA256:
`96fca8c188aace48cdf25c0bcba5fa04334c771cb166a7c7dc0fd9e779c98a94`.
The current rest screenshot was inspected again and has the same assembled
printer/default-control pixels (SHA256 `3c774d0b038c2dbae5a61a4d528049e7bc557e94e147d1a5fe42d39f7f9bdece`).

Fresh full host acceptance repeats **rest/Home/Center/Present/restored**, all
1,636 nodes/1,565 models and declared readbacks. All three flexible vertex
arrays remain exact (**maximum delta 0**) with exactly equal face/index arrays;
maximum representative matrix difference remains **2.842170943040401e-14**.
Reload explicitly restores full counts/defaults and the same finite rest bounds.
All **3,134 responses are HTTP 200**, with no browser errors; elapsed
**114.810 seconds**. `acceptance/host-acceptance.json` SHA256:
`c124c714bcf7a3561be57482620c5ba478e6252aac535bad3454b6928a946a9b`.
Current rest, Present and interior PNG hashes match those above; rest and
interior were visually inspected again. This remains document-language parity,
**not** resolution of the preserved project physical-oracle mismatch.

Final owned groups all exit **0, survivors []**: widget **253483** (111.62
seconds, peak sampled aggregate RSS **676,764 KiB**), portable **257906**
(70.14 seconds, **235,480 KiB**), host **258031** (115.54 seconds,
**2,099,136 KiB**), Python **258175** (110.50 seconds, **653,360 KiB**), and
runtime-ready **258303** (1.62 seconds, **168,952 KiB**). The same bounded
225-second supervisors and termination fences apply. All 1,568 original input
hashes were rechecked unchanged again. No additional production edits remain
planned. At this replay handoff, tasks were **18/23 complete** and parent task
4.3 was still pending. That historical stop is superseded by the accepted parent
review and document-phase disposition below; the raw replay results are unchanged.

### Accepted review and document-phase disposition — 5 October 2026

The parent accepted task **4.3** in [parent-review.md](parent-review.md), after
independent source/adversarial/full-manifest checks, all 1,568 original input
hashes, final bundle/result hashes and current rest/Present-interior images.
Acceptance remains viewer/document scoped; the graceful-close timeout and
separate physical CoreXY finding retain the qualifications recorded above.

ADR-043/044 now contain accepted dated implementation clarifications, and
ADR-078 is **Accepted**, following parent text review. The portable-export
portion of [the Voron wart](../../../../workflow/warts.md) is resolved by this
reviewed worktree result, not described as integrated or published. The separate
capture-fetch finding remains unresolved, as does the project-owned signed-wrap
physical finding. No production code changed during this documentation phase.
The parent completed tasks 4.4/4.5 and synchronized the two modified
viewer-package requirements. An independent block comparison confirms exact
agreement with both delta requirements and byte-for-byte preservation of every
other baseline section. Task 5.2 is completed by the enclosing archive and
implementation commit, after strict validation. Local integration is authorized
as a separate next step; this record does not claim a push or publication.
