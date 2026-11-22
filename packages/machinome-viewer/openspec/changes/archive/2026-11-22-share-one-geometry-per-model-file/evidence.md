# Evidence: share-one-geometry-per-model-file

Applier's record of tasks 1.2 to 5.2 and 7.1, 22 November 2026, on the
bench `machinome/WTs/share-one-geometry-per-model-file` (branch of the same
name, base `4b456edffcdcf34e24b521f45657cdf4fdd42e0a`, planning commit
`3cdeb1fe`). Task 6.2 (the Enigma page) and 7.2 (the decision record) are
the reviewer's. Commands ran from the widget directory unless stated, one
at a time.

## 1.2 The bench

`git log`: `3cdeb1fe plan: share one geometry per model file` above
`4b456edf viewer: follow the slider as it is dragged`; `git status --short`
empty; `openspec validate share-one-geometry-per-model-file --strict`:
"Change 'share-one-geometry-per-model-file' is valid".

## Facts of the base checked before relying on them

- three.js is 0.156.1 (`node_modules/three/package.json`). `FileLoader.js`
  keeps the module-level `loading` table: a `load` of a URL already in it
  pushes its callbacks and returns (lines 53-64); the response's callbacks
  are taken and the entry deleted when the data arrives (220-221).
  `STLLoader.load` parses inside that callback, once per caller.
- `BufferGeometry.clone` is `new this.constructor().copy(this)`; `copy`
  clones every attribute and the index (`BufferAttribute.copy` makes a new
  array, `BufferAttribute.js` 56), the groups and the bounds if present.
  STLLoader's `hasColors` and `alpha` are not copied; nothing reads them.
- `WebGLRenderer.dispose` (655-685) disposes render lists, states,
  properties, cube maps, objects, binding states, uniform groups and the
  program cache; nothing that holds a geometry's attributes. `WebGLGeometries`
  adds a `dispose` listener per geometry (`get`, line 68).
- The suite's test environment is Node 24 (vitest's default environment
  for a file without a docblock is node); `Request`, `Headers` and
  `ReadableStream` are Node's.
- The base bundle built from the base source is
  `67c7794777ea6d40b888a638781ce4df1077c4141b20da14daec1cf6e8843e28`, the
  SHA256 the design names.
- On the base, exactly the four tests of `src/geometry-admission.test.ts`
  that design Decision 11 names fail against the implementation (4.1), and
  the thirteen files of task 4.2 pass unmodified (4.2).

No fact the design states about the base, three.js or Chromium was found
false.

## 2.3 The new widget tests on the base

Both files ran on the base source (the worktree's source before task 3,
and again, after the last change to either test file, with
`src/geometry-admission.ts` and `src/tree.ts` restored from `HEAD` and then
put back byte-equal). The outputs below are from that second run; the first
run, before S10's batch was corrected (below), was red for the same
reasons.

`vitest run src/share-one-geometry.test.ts` on the base: 19 failed, 2
passed (21).

| Test | Base | Reason shown (the first assertion that failed) |
|---|---|---|
| S1 | red | `parsesOf(at)` length 15, expected 7 (line 324: a parse per part); the request per file (one each) and the four requests sent during construction passed |
| S2 | red | three distinct geometries, expected 1 (line 349) |
| S3 | red | two parses of `m.stl`, expected 1 (line 391); one request each passed |
| S4 | red | four parses, expected 1 (line 435); before it, one request in all and the parts' bytes `[2, 2]` (the first request's) passed |
| S5 (a, b) | red | two parses, expected 1 (line 458); one request passed |
| S6 | red | six parses, expected 2 (line 492); the new tree's requests (`g.stl` only) passed |
| S7 | red | two parses of one response, expected 1 (line 523); one request passed |
| S8 | red | four parses, expected 1 (line 540); one request passed |
| S9 | red | three parses, expected 1 (line 569); one request passed |
| S10 (0 to 6) | red | two parses, expected 1 (line 600) |
| S11 | green | a guard |
| S12 | green | a guard |
| S13 | red | `census()` undefined (line 761); before it, every parse freed exactly once and no live mesh on a file's geometry passed |
| G1 | red | "seed 1 step 0 (mount): D3 the census: expected undefined to be defined" (line 884); D1 and D2 passed before it |

`vitest run src/share-one-geometry-viewer.test.ts` on the base: 4 failed,
1 passed (5).

| Test | Base | Reason shown |
|---|---|---|
| V1 | red | three parses for the reload, expected 2 (line 420); before it, both files requested again and the old meshes still in the scene with undisposed geometry passed |
| V2 | red | six parses, expected 2 (line 444) |
| V3 | green | a guard |
| V4 | red | two parses, expected 1 (line 504); before it, one request and the old meshes standing while it was held passed |
| G2 | red | "seed 1 step 0 (mount): D3 the census: expected undefined to be defined" (line 673) |

### What the base showed for the assertions of today's behaviour

- S4: the parts end on the first request's bytes, version 2 (the file was
  version 3 when the second notice was sent): `expect(shown.map(versionOf)).toEqual([2, 2])`
  passed on the base before the parse count failed, and passes on the
  implementation.
- S11 and S12 passed on the base and pass on the implementation.
- V3 passed on the base (the file requested and parsed again for the new
  part, the part on screen keeping its geometry) and passes on the
  implementation.
- B2 and B3 passed on the base bundle and pass on the implementation's.
- Not regenerated: no expected value in these tests was changed after the
  base runs.

### G1 on the base without the census

To know whether D1, D2 and D4 hold on the base, a scratch copy of the tree
file whose D3 and D5 skip the census (not kept) ran G1's 300 sequences on
the base source: D1, D2 and D4 held at every step of every sequence; D5's
"every parse freed exactly once" failed at seeds 109 and 164, a parse never
disposed. The tally of the identical sequences: requests 3,830, parses
12,651, meshes 13,968 (the implementation: requests 3,830, parses 3,434,
copies 421, meshes 13,968). Seeds 109 and 164 are the base's leak of an
artifact update applied to a part a republish removed meanwhile; see
"Deviations", 1.

## 2.4 The browser tests on the base bundle

`npm run build` from the base source:
`67c7794777ea6d40b888a638781ce4df1077c4141b20da14daec1cf6e8843e28`, copied
to `.scratch/` (deleted before the report). `pytest
tests/test_share_one_geometry.py tests/test_asset_load_order.py -rs -s`: 1
failed, 6 passed.

- B1 red, for its stated reason: `AssertionError: 8 != 4`; the counts
  printed were mount `{created: 8, deleted: 0, bytes: 1152}`,
  `artifactChanged` `{created: 14, deleted: 6, bytes: 2016}`, dispose
  `{created: 14, deleted: 14}`: 8 at mount, 6 created and 6 deleted by the
  update, all 14 deleted, the design's figures.
- B2 green (pixels of the shared and copied documents equal in all six
  states).
- B3 green: the disposed viewer `{created: 8, deleted: 8}`, the other
  `{created: 8, deleted: 0}`, its pixels unchanged.
- `tests/test_asset_load_order.py`: 4 passed.

## 3.3 The implementation, the two files

`tsc --noEmit`: no output, exit 0. `vitest run src/share-one-geometry.test.ts`:
21 passed (21); G1 "300 sequences of 40 steps in 5725 ms".
`vitest run src/share-one-geometry-viewer.test.ts`: 5 passed (5); G2 "40
sequences of 25 steps in 594 ms".

## 4.1 The four tests of `src/geometry-admission.test.ts`

Against the implementation before the change, exactly these failed (7 of
15 cases): "cancels queued jobs…" (`expected +0 to be 4`: the old
signature's start never ran), "removes cancelled queued URL eligibility…"
(`settle.shift(...) is not a function`), "releases failures…" (`fail is
not a function`), and the four cases of "does not commit prepared
shared-path models or markings…" (`expected [ [Function] ] to have a
length of 2 but got 1` at microtask 3; the other three timed out behind
it). The others passed, among them ADR-078's counted test
(`{ initially: 4, peak: 4, total: 18 }`).

Changed, and nothing else in the file:

- "cancels queued jobs without requests and retains active capacity until
  real settlement": `admitGeometry(url, owner, viewer, reading(start))`
  where it was `admitGeometry(url, owner, start)`; the same counts
  (`started` 4, the survivor not started until a slot frees, every
  cancelled job rejected) and order; the survivor's share is released at
  the end.
- "removes cancelled queued URL eligibility so a later request cannot
  inherit abandoned FIFO priority": the same rewrite; `starts` is still
  `['Y', 'new X']`; the shares are released at the end.
- "releases failures, preserves their original error and closes duplicate
  groups after actual settlement": the second subscriber joins the one
  reading and has no read of its own, so its row is `{status: 'rejected',
  reason: error}` where it was `fulfilled`; the original error preserved
  and the later load being a fresh one (`fresh` 1, its value 3, now read
  as `share.value`) are asserted as they were. The `resolve()` of the
  second subscriber's own read is gone with that read.
- "does not commit prepared shared-path models or markings after disposal
  at microtask %i": `expect(pending).toHaveLength(1)` where it was 2; its
  assertions on attachment are as they were.

`vitest run src/geometry-admission.test.ts`: 15 passed (15).

## 4.2 Existing files, run singly and unmodified

| File | Result |
|---|---|
| `src/tree.test.ts` | 71 passed |
| `src/parent-adversarial-geometry.test.ts` | 12 passed |
| `src/shared-materials.test.ts` | 25 passed |
| `src/draw-on-change.test.ts` | 62 passed |
| `src/picture-revision.test.ts` | 22 passed |
| `src/assembly.test.ts` | 14 passed |
| `src/color.test.ts` | 22 passed |
| `src/flat-pass.test.ts` | 41 passed |
| `src/flat-pass-parity.test.ts` | 52 passed |
| `src/navtree.test.ts` | 40 passed |
| `src/follow-the-slider.test.ts` | 55 passed |
| `src/flexible.test.ts` | 32 passed |
| `src/flexible-rebuild.test.ts` | 18 passed |

No existing test the design said holds as written failed.

## 4.3 Mutations

Each applied alone to the implementation by a scratch script, both new
widget files run, the implementation restored and confirmed byte-equal to
a saved copy (SHA256 `24cd56c7…` for `geometry-admission.ts`, `3cd34962…`
for `tree.ts`) before the next.

| | Mutation as applied | Red |
|---|---|---|
| MU1 | every subscriber starts its own `kind.read` and holds its own parse (`start`) | S1 to S9, S10 (all seven), S11; V1, V2, V4. S1, S3, S7, S8 and V4 at their parse counts. B1 under the MU1 bundle (below) |
| MU2 | one holding per reading for every viewer (`take` keys by the reading) | S8 (`expected … not to be …`, the two viewers' geometries); V2 (`expected [] to have a length of 2`, no copies). B3 under the MU2 bundle |
| MU3 | `admitGeometry` never joins a reading whose request was sent | S1 (`f0.stl: expected … to have a length of 1 but got 2`: the first file's later parts read again), S2, S3, S4, S5 (a, b), S6, S7, S8, S9, S10 (all), S11; V1, V2, V4 |
| MU4 | `release()` without its flag | **nothing red**: 21 passed, 5 passed. `disposeMesh`'s `WeakSet` stops every second call before it reaches the share, and nothing else releases a share twice; the flag is a second guard no test can reach through the tree (S2 runs the cleanup more than once) |
| MU5 | `disposeMesh` disposes the shared geometry instead of releasing | S2, S4, S5 (a, b), S6, S8, S10 (3 to 6), S13, G1 ("seed 1 step 10 (answer 200): D1 a mesh in a live tree shows a disposed geometry"); V1, V2, V4, G2 ("seed 1 step 15 (dispose): geometry 41 disposed more than once") |
| MU6 | `loadDecal` disposes the file's geometry after the lift (today's line), then releases | S3 (`expected 1 to be +0`: the part's geometry disposed), S13, G1 (a geometry disposed twice); G2 |
| MU7 | normals computed by each subscriber, not by the reading | S1 (`expected 3 to be 1`, the normals count), S12 (the `normal` attribute's version 3 where the mount left 1) |
| MU8 | `loadMesh`'s failure path disposes the returned geometry instead of releasing | S10 at 2 microtasks (`expected 1 to be +0`) |
| MU9 | an untaken parse kept at retirement | S9 (`expected +0 to be 1`), S13, G1 ("seed 1 step 31: D2"); G2 ("seed 2: D5 freed once") |
| MU10 | a holding disposed at zero holders before its reading retires (`release` without the retirement condition; `retire` skips a holding already disposed) | **nothing red**, as the design expects: equivalent, every share being taken in the reaction round before any can be released |
| MU11 | a reading left open after its request settles (no close at arrival; retirement keeps the reading's request, value and holdings) | V3 (`expected [] to deeply equal [ 'http://view.test/v3/models/f.stl' ]`: no request for the new part), and S2, S4, S5 (a, b), S6, S7, S11, G1 (D4, "a reading closed before it asked"); V1, V4, G2 |
| MU12 | a disposed holding keeps its geometry and its reading keeps its holdings | **nothing red**, as the design records: unseen by the suite; the reviewer's memory measurement is the check |

Bundles: `npm run build` under MU1 (`a6da7879…`) then `pytest
tests/test_share_one_geometry.py`: B1 red (`8 != 4`; mount 8, update +6/+6),
B2 and B3 green. Under MU2 (`db73cdbb…`): B3 red (`0 != 4`: the disposed
viewer's 4 buffers never deleted), B1 and B2 green. The bundle rebuilt
from the implementation afterwards: `0ecadb1e8523bc46d9c289e17367a185d41261096be5fa86df200c7807c4caad`.

## 4.4 G1 and G2

- G1: seeds 1 to 300, 40 steps each, on documents of up to eight parts and
  markings on three files, two viewers' holders: 5,725 ms alone, 9,581 ms
  inside the whole suite. Over all sequences: 2,253 mounts, 588 reloads,
  694 republishes, 679 artifact updates, 3,072 rewrites, 2,901 answers and
  396 failures (HTTP 500), 1,417 disposals; 3,830 requests, 3,434 parses,
  421 copies, 13,968 meshes.
- G2: seeds 1 to 40, 25 steps each, two mounts: 594 ms alone, 787 ms in the
  suite. 165 mounts started (139 mounted), 83 reloads, 50
  `manifestChanged`, 44 `artifactChanged`, 280 rewrites, 243 answers and
  28 failures, 72 disposals; 350 requests, 322 parses, 116 copies.
- `G1_FROM`/`G1_TO` and `G2_FROM`/`G2_TO` replay a printed seed alone.

## 5.1 The gate

- `vitest run` (the whole widget suite): Test Files 76 passed, 1 skipped
  (77); Tests 2,079 passed, 2 skipped (2,081); 68.4 s. The skips:
  `src/run/profile-installed-benchmark.test.ts` (its one test runs only
  with `CURTA_INSTALLED_PROFILE_DOCUMENT` set) and one test of
  `src/run/profile-contact.test.ts` (runs only with
  `CURTA_PROFILE_V13_DOCUMENT` set): pinned Curta documents outside the
  bench, not set here. No failure.
- `tsc --noEmit`: exit 0, no output.

## 5.2 The bundle and the Python suite

`npm run build`: `dist/machinome-viewer.js`
`0ecadb1e8523bc46d9c289e17367a185d41261096be5fa86df200c7807c4caad`.

`pytest tests -rs` from `packages/machinome-viewer` on the bench's venv:
298 passed, 3 skipped, 71 warnings in 319.91 s; no failure. The skips, with
their stated reasons: `tests/test_curta_drawing.py:375` and `:469`, "the
Curta's own builds are not at
…/WTs/projects/Calculators/Curta-Type-I-3x/_build" (a project's build the
bench does not have); `tests/test_follow_the_slider.py:380`, "Playwright's
firefox is not installed at the revision it expects
(/home/asa/.cache/ms-playwright/firefox-1543/firefox/firefox is absent)".
Skipped, not passed. The warnings are Pillow's `getdata` deprecation and
the like in existing tests. `tests/test_asset_load_order.py` passed as
written (4 passed).

On that bundle, `tests/test_share_one_geometry.py` and
`tests/test_asset_load_order.py` alone: 7 passed. B1: mount `{created: 4,
deleted: 0, bytes: 576}`, after `artifactChanged('shared.stl')` and a draw
`{created: 6, deleted: 2}`, after `dispose()` `{created: 6, deleted: 6}`.
B3: the disposed viewer `{created: 4, deleted: 4}`, the other
`{created: 4, deleted: 0}`, its pixels unchanged. B2: equal pixels in all
six states.

## The implementation

- `src/geometry-admission.ts`. A *reading* is the admission group (`Group`):
  its URL, queued jobs, the slot, the count of subscribers not yet settled
  (`pending`), the kind of the load that opened it (`ReadingKind`: `read`,
  `copy`, `dispose`), its one `load` promise, the parse until it is taken
  (`value`, `parsed`, `taken`) and its per-viewer holdings (`Map` keyed by
  the viewer). `begin` calls `kind.read(url)` once, when the first job
  starts, and registers the close first, so the reading leaves the URL
  table in the first reaction to its settlement, before any subscriber's;
  each job's reaction takes its share then (`take`), or rejects with its
  owner's cancellation or the reading's error. `retire` runs when the last
  subscriber has settled (`pending` 0): it disposes a parse no one took,
  marks each holding retired and disposes those no one holds, then drops
  the reading's `load`, `value` and holdings. A *holding* is
  `{url, viewer, value, holders, retired, dispose}`: the first viewer's is
  the parse, each further viewer's `kind.copy` of it. It is disposed
  exactly once, when `holders` is 0 and it is retired (checked at release
  and at retirement); disposal drops `value` and `dispose` and removes it
  from the census set. A *share* (`HeldShare`) refers only to its holding
  and a `released` flag; `value` reads the holding's; `release()` acts
  once. Nothing on a load's path scans a structure that grows with the
  page: the census set is added to in `take` and deleted from in
  `disposeHolding`, and read only by `geometryCensus()`. The budget, FIFO,
  the cancellation of queued work (`GeometryOwner.cancel`, unchanged), the
  tombstone in `pump` and when a load may join (`groups.get(url)`, joined
  while queued or active) are the base's.
- What refers to what: the URL table and the queue refer to open readings;
  a reading refers to its holdings until it retires; a holding to its
  value until it is disposed; a share to its holding; a mesh's share is in
  `tree.ts`'s `meshShares` `WeakMap`; the census set to holdings alive.
  When a holding is disposed it drops its value and leaves the census set;
  when a reading retires it drops its parse, its promise and its holdings.
- `src/tree.ts`. `STL_READING` reads with `stlLoader.loadAsync(url)`,
  computes normals once and disposes the parse if that throws; copies with
  `clone`; disposes with `dispose`. `loadMesh` asks
  `admitGeometry(url, owner, presentation, STL_READING)`, sets the share's
  value on the mesh and records the share; on failure it releases a share
  not yet recorded, then `disposeMesh` (the placeholder), then `forget`.
  `disposeMesh` releases and forgets a recorded share, and disposes the
  mesh's geometry otherwise. `loadDecal` rejects with the owner's
  cancellation, making nothing, if the mesh was disposed before it
  continued; it lifts from the share's value, sets the decal's own
  geometry, forgets and releases the share.

## Deviations from the design, and decisions it left open

1. **An artifact update's replacement for a node removed meanwhile is
   disposed, not attached** (`tree.ts`, `artifactChanged`'s application,
   `if (tree.disposed) { disposeMesh(mesh); return; }`). Not in the
   design. G1 seeds 109 and 164 found it: an `artifactChanged` collects the
   nodes naming the path, a republish removes one of them (disposing it)
   while the update's request is held, and the update's application then
   calls `replaceMesh` on the disposed node, whose group is detached. On
   the base that mesh and its own parse are made and never disposed (the
   base probe above: D5 fails at the same two seeds); they are never
   drawn, and the viewer's material holder keeps the mesh until the viewer
   is disposed. With sharing, that mesh would hold a share for ever: its
   holding would never reach zero, so the file's geometry would outlive
   every part on screen that held it (its WebGL buffers too, when it was
   drawn) and outlive the viewer's disposal, against "a geometry SHALL be
   freed … once no part holds it" and "disposing a viewer SHALL free every
   geometry it held". Disposing the replacement there changes nothing
   drawn: the node is gone from the tree. Markings in the same race are
   left as the base has them: a decal holds no share after its lift. A
   reconcile overlapping a reconcile of the same tree has base behaviours
   of its own (a later application can re-add a child an earlier one
   disposed); G1 does not generate them (one republish at a time per tree,
   its `busy` flag), G2 does and found nothing.
2. **The census rows carry the holding's value** (`{url, viewer, holders,
   value}`), so D3 can match holdings to the meshes that show them. The
   census is a module-level set of the holdings alive.
3. **`admitGeometry`'s signature**: `admitGeometry(url, owner, viewer,
   kind): Promise<Share<T>>`; `ReadingKind<T> = {read(url), copy(value),
   dispose(value)}`, the opening load's kind used for the reading;
   `Share<T> = {value, release()}`. The viewer is the `MaterialPresentation`
   `loadMesh` already receives.
4. **S10** builds its two trees each with a `GeometryBatch` of its own,
   where the design says "in one batch". With one batch, the first tree's
   failure (its disposal rejects its `loaded`) cancels the batch, whose
   owners include the second tree's, and that disposes the second tree's
   meshes after they were attached: on the base as here, so the case would
   test the batch's coupling, not sharing. `replaceTree` builds every tree
   with a batch of its own. "After the response" is counted from
   `STLLoader.parse` of its bytes. MU8 bites at 2 microtasks.
5. **D2 and D3 count live meshes**, those made by the viewer's material
   holder and not yet released (`MaterialPresentation.prototype.mesh` and
   `release` spied), not only the meshes under a live or pending tree's
   group: at quiescence a pending republish's prepared replacements hold
   shares outside any group. D1 checks both. D4 learns the URL each mesh
   asked for and when from a pass-through wrapper of `admitGeometry` in a
   `vi.mock` of `./geometry-admission` (the test never calls it), and
   checks that the request whose bytes the mesh shows is of that URL and
   was answered after the mesh asked. A per-viewer copy is told from
   `liftDecal`'s temporary clone by the clone's `deleteAttribute('normal')`.
6. **S12**: `visibleBounds` is private to `viewer.ts`; S12 does to each
   visible mesh's geometry what it does (`computeBoundingBox` when null)
   and feeds the box to `frameBounds`. The mount's own decal lift from the
   shared file happens before the snapshot, so the snapshot is compared
   with three.js's own parse of the same bytes and one `computeVertexNormals`
   (attribute versions and arrays) before the battery; the battery's
   "decal lifted from a shared file" is a republish adding a marking on
   `f.stl`, which reads it again.
7. **S2**'s "owners' cleanups after the traversal": `WidgetTree.dispose`
   runs its owner's cleanups before its traversal; the test calls
   `dispose()` twice and then cancels the mount batch, so every mesh's
   `disposeMesh` is reached more than once (MU4 above).
8. **S11**: three.js 0.156.1's `HttpError` keeps `name` `'Error'`; the
   loader's error is asserted by its constructor's name, its message and
   identity across subscribers.
9. **The viewer bench** copies `draw-on-change.test.ts`'s counting renderer
   with its loop, its render count and the scene kept per renderer, records
   each `Scene` the viewer makes, mounts with `partControls` and
   `driverControls` `'none'`, and stubs a `ResizeObserver` that never
   fires.
10. **B1 to B3** count buffers per context on the context's canvas; B2's
    states are: mounted; highlight of `b` with others `keep`, `dim`,
    `ghost`; `c` hidden; after `artifactChanged('shared.stl')`.

## Sentences against "Corrected in review"

None found: proposal, design, delta and tasks were searched for a tick, a
displaced reading, a request that waits for another, and freshness by
operation; the only mentions are the ones that describe the struck rule
as struck (design Context, Decision 1's "stricter rule", "Alternatives
rejected", "Corrected in review").

## The reviewer's record (tasks 6.2, 7.2, 7.3)

Recorded by the reviewing agent on 22 November 2026, after the applying
agent stopped. Where a figure above counts the tests as they were handed
over (the two new widget files at 26 tests, the suite at 2079), this
section gives what was committed.

### What the review read, and what it changed

The diff of `src/geometry-admission.ts` and `src/tree.ts` was read against
design Decisions 1, 3, 4, 6 and 10 and the section "Corrected in review".
No source line was changed in review.

- **The deviation is accepted.** `artifactChanged`'s application lets go of
  a replacement prepared for a node a republish disposed meanwhile, where
  the base attached it to a group nothing shows. On the base that mesh
  kept a parse of its own for ever; with sharing it would keep a share,
  and through it the file's geometry and its buffers past every holder on
  screen. It is the smallest thing that keeps "freed once no part holds
  it" true, and it draws nothing differently. The review's fault that
  removes the line turns G1 red.
- **MU4 turning nothing red is a gap in the tests, not in the code.** A
  share's own flag is never reached twice through the tree, because
  `disposeMesh` stops a second call first. `R1` now asks the module
  itself.
- **Every place a geometry is disposed was read again in the result:**
  `disposeMesh` (a share let go, or the mesh's own geometry disposed),
  `FlexibleShape.dispose`, the reading's kind (`STL_READING.dispose`,
  reached only from a holding's or an untaken parse's disposal), and
  nothing else in the widget's sources.

### Tests added in review

In `src/share-one-geometry.test.ts`, each written for a fault that stood:

- `R1` a share let go twice counts once, the geometry is freed at the last
  release and not before, and a freed geometry is out of its shares'
  reach.
- `R2` a reading is closed when its request settles: a load asking the
  moment a share arrives makes a second reading.
- `R3` a second viewer mounting past the budget joins the first viewer's
  queued readings: one request and one parse a file, the first viewer
  holding the parse and the second a copy, each freed with its viewer.
- `R4` (31 cases) a marking whose tree is disposed 0 to 30 microtasks
  after its file arrives rejects with the cancellation and nothing else,
  and its one parse is freed exactly once.

The two new widget files are 60 tests. On the base source (put back for
the run and the final sources restored, byte-equal by digest): **27
failed, 33 passed.** Passing there: S11, S12 and V3, as the design says,
and thirty of `R4`'s cases. Failing: everything the applying agent lists,
`R1` and `R2` (they call the new signature), `R3` (a parse per part of
each viewer), and `R4` at eight microtasks, where the base disposes the
marking's parse twice: the fault of `loadDecal` the proposer found, closed
here by the check that the mesh was not disposed meanwhile.

### Faults planted in review

Twenty-five, each applied alone to the committed `geometry-admission.ts`
or `tree.ts` by exact text replacement, with five test files run
(`share-one-geometry`, `share-one-geometry-viewer`, `geometry-admission`,
`tree`, `parent-adversarial-geometry`) and the sources restored and checked
by digest. The verdict was first seen green on a replacement that changes
nothing and red on every part showing a copy of its own.

| Fault | Red |
|---|---|
| A holding nobody holds any more is not freed when its reading retires | `geometry-admission` (a returned result disposed once, an artifact replacement after disposal) |
| The first viewer is given a copy too, and the parse is left with no one | G1, G2, `geometry-admission` and `parent-adversarial-geometry` (21 tests) |
| A further viewer is given the first viewer's geometry | S8, S13, V2, G1, G2 |
| A reading is never closed | G1, G2, V3 and 14 more |
| A load whose owner was cancelled is given a share all the same | `geometry-admission` (queued jobs cancelled) |
| A share is handed out without being counted | 55 tests |
| A reading computes no normals | S1, S12, `tree` (normal preparation rejects) |
| A parse whose normals throw is not freed | `tree` (normal preparation rejects) |
| A load that fails after its share arrived never lets go of it | S10 at 2 microtasks, `geometry-admission` |
| A mesh does not record its share | 46 tests |
| A load whose owner was cancelled as its share arrived attaches it | S10 at 2 microtasks, `geometry-admission` |
| A marking never lets go of the file's geometry | S3, S13, G1, G2 |
| A marking lets go and keeps the record, so its own geometry is never freed | `tree` (a marking dropped from the list) |
| A replacement for a node disposed meanwhile is attached to it | G1 |
| The viewer taken to be the load's owner | S1, S2, S5 to S8, S11, S12, V1, V2 |
| A mesh lets go of its share and frees the geometry as well | 27 tests |
| A further viewer's copy is the same geometry | S8, S13, V2, G1, G2 |
| A reading stays joinable after its request settles, until it retires | `R2` |
| A share released twice counts twice | `R1` |
| A freed holding keeps its geometry reachable | `R1` |
| A second viewer does not join a queued reading of the first | `R3` |
| A decal is lifted for a mesh disposed meanwhile | `R4` at 8 microtasks |
| A holding freed at no holder while loads still wait on its reading | nothing: equivalent, every share of a reading is taken in the round its request settles, before any can be let go (the applying agent's MU10) |
| The slot given back at the first subscriber, not the last | nothing: equivalent now, every subscriber of a reading settles in that one round |
| A retired reading keeps its parse and its request | nothing: unreachable, nothing refers to a retired reading |

The last five of those that went red stood on the tests as handed over;
`R1` to `R4` were written for them.

### Gates on what is committed

- `tsc --noEmit`: no output, exit 0.
- The whole widget suite, once: **77 files, 76 passed and 1 skipped; 2115
  tests, 2113 passed and 2 skipped; no failure.** The skips are the two
  the applying agent names.
- The bundle built from the committed source: SHA256
  `0ecadb1e8523bc46d9c289e17367a185d41261096be5fa86df200c7807c4caad`
  (919.8 kB), the applying agent's: the review changed no source.
- The viewer's Python suite on that bundle, once: **298 passed, 3 skipped,
  no failure** (5 min 19 s); the skips are the two Curta builds that are
  not on this machine and the Firefox leg of another change's test.

### The Enigma I page (task 6.2)

`projects/enigma-i` at `081f4e6`, its built page served on this machine
only, by the method of `workflow/evidence/enigma-page-memory-2026-11-22.md`:
the suite's Chromium, headless, 1440 by 900, a probe build of the viewer
in place of the page's bundle (this bench's source, or framework `main` at
`4b456edf`, each with molejo's `main`, unminified, no source file edited).
One run of each build for the memory, draw calls counted and not executed;
three further loads of each for the time; two runs of each for the
pictures, really drawn in software.

| One open copy | Base | This change |
|---|---|---|
| All browser processes, settled | 4,217 MiB | 3,034 MiB |
| The tab | 2,167 | 1,578 |
| Its typed arrays | 1,612.6 | 1,039.1 |
| Its JavaScript heap in use | 205.8 | 202.6 |
| The graphics process | 1,931 | 1,334 |
| Meshes | 3,347 | 3,347 |
| Geometries | 3,347, none shared | 1,472, 184 of them shared |
| of the 2,868 parts read from files | 2,868 geometries, 1,110.2 MiB | 993 geometries, 536.7 MiB |
| of the 426 flexible parts | 426, 489.9 MiB | the same |
| of the 53 markings | 53, 3.2 MiB | the same |
| WebGL buffers alive | 6,747 of 1,603.4 MiB | 2,997 of 1,029.9 MiB |
| Draw calls asked in the same two frames | 6,694 | 6,694 |
| Peak while the page loads | 4,343 MiB | 3,265 MiB |
| From the click to a ready page, in that run and in three further loads | 13.3 s; 11.7, 11.7, 12.0 s | 11.0 s; 12.4, 10.7, 10.5 s |
| `reload()`: seconds, and the peak with both models held | 13.1 s, 6,286 MiB | 10.3 s, 4,581 MiB |
| After the reload, settled | 4,246 MiB; 6,747 buffers alive, 6,747 deleted | 3,057 MiB; 2,997 alive, 2,997 deleted |
| After `dispose()` | no buffer alive, 13,494 created and deleted | no buffer alive, 5,994 created and deleted |

The typed arrays and the buffers are each 573.5 MiB less, the figure the
files' census gave. After `dispose()` the tab's typed arrays stay on both
builds because the probe and the page still hold the scene; the buffers
are the measure there.

**Pictures.** Sixteen states on each build, each reached through the
mount's handle. In one run: the mount; the case at 0.4; the flap at 60
degrees; a wheel three teeth on; a key pressed; after `reload()`; the case
at 0.4 again; a key pressed again; the model seen from behind. In another:
the keyboard highlighted with the others kept; the electrical branch
highlighted with the others dimmed; the scrambler highlighted with the
others ghosted; the highlight put back; the enclosure hidden; the
enclosure and the electrical branch hidden (the 26 lamp caps, one geometry
now, among them); both shown again. In each, what is on screen equals a
forced draw on both builds, and the two builds' pictures are equal: **0 of
29,452,976 pixels differ over the thirty-four pictures** (the whole canvas,
998 by 868, panel included). The states differ from one another, by 128 to
167,987 pixels outside the panel, except those that return to an earlier
state (after the reload, the highlight put back, the parts shown again),
which equal it. The pictures are of the page's imported CAD and are not in
this repository.

**The design's expectations.** No pixel differs: yes. 3,347 meshes on
1,472 geometries: yes. About 2,997 WebGL buffers: 2,997. Typed arrays and
buffer bytes each about 573.5 MiB less: 573.5 and 573.5. One open copy
near 3,070 MiB: 3,034. The load shorter: not shown. Four loads of each
build took 11.7 to 13.3 s on the base and 10.5 to 12.4 s here, which
overlap.

**Limits.** One run of each build; the base's totals agree with the two
earlier runs within 1 %. A virtual machine with no graphics card: the
graphics process's share is ordinary memory here and lives with the card
elsewhere. The seconds are four loads of each build on that machine.
Chromium only. No
second viewer and no changing file were tried on this page; the suite's
browser tests hold those on small documents.

### The decision record (task 7.2) and the archive (task 7.3)

The measurement confirms the design. ADR-082, its line in
`workflow/adrs/README.md` and the dated amendment in ADR-078 were written
by the reviewing agent, the applying agent having stopped. The finding's
geometry is closed in `workflow/warts.md`. Integration into `main`,
pushing and publication are the pilot's.
