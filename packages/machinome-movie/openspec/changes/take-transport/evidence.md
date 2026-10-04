# Evidence — `take-transport`

Worktree `WTs/take-transport`, branch `take-transport`, cut from the
`player` head b86f88b (the campaign's plan and contract). Planning commit
1ff9174, after the orchestrator's ratification by message. The viewer
bundle for layer 6 is selected by path in the environment
(`VIDEOMAKER_VIEWER_BUNDLE`, the API 29 bundle, sha256
`b5fcdb8613aceb3936c09d755af41f1ceb9ad1125e4f5bc4e671a568a0920107`), never
written into the repository.

## The base

`VIDEOMAKER_VIEWER_BUNDLE=… npm test` on b86f88b with this change's
planning artifacts untracked (memo on):

```
 Test Files  40 passed (40)
      Tests  408 passed (408)
Test memo: 2 passed from the memo, 406 run
exit 0 elapsed 910 s
```

## Red first

### Layer 4: the transport absent

`vitest.config.mjs` gives the `stage` project `transport/**/*.test.ts`;
`transport/take.test.ts` and `transport/clock.test.ts` written, with the
`tsc --noEmit -p transport/tsconfig.json` test beside the stage's in
`test/stage-types.test.mjs`; no source of `transport/` exists.

`npm test -- --project stage transport/`:

```
 FAIL  |stage| transport/clock.test.ts [ transport/clock.test.ts ]
Error: Failed to resolve import "./clock" from "transport/clock.test.ts". Does the file exist?
 FAIL  |stage| transport/take.test.ts [ transport/take.test.ts ]
Error: Failed to resolve import "./take" from "transport/take.test.ts". Does the file exist?
 Test Files  2 failed (2)
      Tests  no tests
```

`npm test -- --project pure test/stage-types.test.mjs -t "take transport compiles"`:

```
 FAIL  |pure| test/stage-types.test.mjs > types > the take transport compiles strictly, its tests included: tsc --noEmit -p transport/tsconfig.json
AssertionError: expected 'error TS5058: The specified path does…' to be '' // Object.is equality
+ error TS5058: The specified path does not exist: '/home/asa/devel/machinome/videomaker/WTs/take-transport/transport/tsconfig.json'.
 Test Files  1 failed (1)
      Tests  1 failed | 11 skipped (12)
```

### Layer 4: green, and the identity check's mutation

`transport/viewer-handle.ts`, `transport/take.ts`, `transport/clock.ts`,
`transport/tsconfig.json` and `src/take.d.mts` written.

`npm test -- --project stage transport/`:

```
 ✓ |stage| transport/clock.test.ts (13 tests) 9ms
 ✓ |stage| transport/take.test.ts (15 tests) 12ms
 Test Files  2 passed (2)
      Tests  28 passed (28)
```

`tsc --noEmit --pretty false -p transport/tsconfig.json`: no output, exit 0.

Mutation: `attachMachine`'s identity check made `if(false)`, then
`npm test -- --project stage transport/take.test.ts`:

```
     × refuses another machine, naming both identities and take.identity, before touching it 6ms
     × refuses a viewer whose machine is not the take's 1ms
AssertionError: expected [Function] to throw an error
 Test Files  1 failed (1)
      Tests  2 failed | 13 passed (15)
```

The file was restored byte for byte (`cmp`).

### Layer 9: the boundary, the memo's keys, the bundle's names, the records

`test/transport-boundary.test.mjs` written. With `transport/` moved aside
(the transport absent), `npm test -- --project pure test/transport-boundary.test.mjs`:

```
   × every file of the take transport imports only its own files and the pose rule, and its tests also the runner and the fixtures 8ms
   × the handle's types are declared, not imported, and the stage takes them from there 10ms
   ✓ the boundary check refuses a package, the stage and the rest of src/, by file and specifier, and admits the transport's own and the pose rule 2ms
   ✓ src/take.d.mts declares exactly the functions src/take.mjs exports 2ms
Error: ENOENT: no such file or directory, scandir '…/WTs/take-transport/transport'
Error: ENOENT: no such file or directory, open '…/WTs/take-transport/transport/viewer-handle.ts'
      Tests  2 failed | 2 passed (4)
```

With `transport/` back and the stage not yet changed:

```
   ✓ every file of the take transport imports only its own files and the pose rule, and its tests also the runner and the fixtures 10ms
   × the handle's types are declared, not imported, and the stage takes them from there 14ms
AssertionError: stage/runtime.tsx declares no MachineHandle of its own
      Tests  1 failed | 3 passed (4)
```

Mutations: `transport/clock.ts` given `import {useState} from 'react';` and
`import type {Rect} from '../stage/types';`, and `export function takeLine`
deleted from `src/take.d.mts`:

```
AssertionError: the take transport imports across its boundary
+   'transport/clock.ts imports "react": a package',
+   'transport/clock.ts imports "../stage/types": the stage'
AssertionError: the declaration and the module disagree on their functions
-   'takeLine',
```

Both files restored byte for byte (`cmp`).

`test/memo.test.mjs` (every browser test's key reads `transport/take.ts`,
`transport/viewer-handle.ts` and `src/take.mjs`), `test/stage-types.test.mjs`
(the second checkout copies `transport/`; the bundle names
`videomaker/transport/take.ts` and `videomaker/src/take.mjs`) and the
records pin of `test/repository.test.mjs`, before the stage, the build or
the records changed:

```
   × the manual and the records say a view on a take is posed through the take transport (take-transport) 7ms
     × in this repository, every read of every slow test is declared and the stage is keyed for the browser tests 235ms
     × two checkouts bundle two copies of a project, at different places, to the same bytes 725ms
AssertionError: transport/take.ts is an input of …/test/browser/browser-seam.test.mjs
AssertionError: stage.md: the bundle names the transport by the tool
AssertionError: expected '"use strict";\n(() => {\n  var __crea…' to match /^ {2}\/\/ videomaker\/transport\/tak…/
      Tests  3 failed | 48 passed (51)
```

### The stage through the transport, and the bundle's names

`stage/types.ts` takes `Vec3`, `Rect` and `Bank` from
`transport/viewer-handle.ts` and re-exports them; `stage/runtime.tsx`
imports the handle's types from there, attaches the machine transport at
mount, poses through it, reports its bank and gains `transport(key)`;
`stage/take.test.tsx` poses through a machine transport. The `stage`
project and both type checks are green (`tsc -p stage/tsconfig.json` and
`tsc -p transport/tsconfig.json`: no output, exit 0):

```
 ✓ |stage| transport/clock.test.ts (13 tests) 11ms
 ✓ |stage| transport/take.test.ts (15 tests) 14ms
 ✓ |stage| stage/take.test.tsx (5 tests) 5ms
 ✓ |stage| stage/stage.test.tsx (20 tests) 383ms
 Test Files  4 passed (4)
      Tests  53 passed (53)
```

With the runtime importing the transport and `src/stage-build.mjs` not yet
changed, the two checkouts no longer bundle the same bytes
(`npm test -- --project pure test/stage-types.test.mjs`):

```
     × two checkouts bundle two copies of a project, at different places, to the same bytes 812ms
AssertionError: stage.js differs between the checkouts: expected [ Array(1) ] to deeply equal []
+   "14961:   // ../../../../../../home/asa/devel/machinome/videomaker/WTs/take-transport/transport/take.ts  |    // ../../../../../../other-checkout/transport/take.ts",
      Tests  1 failed | 11 passed (12)
```

A runtime-only bundle built then (a scratch script calling `buildStage`)
showed what the key's record (`inputs.json`) named: the stage's files by
the tool, and the transport and the pose rule by the machine:

```
'../../../../../../../../home/asa/devel/machinome/videomaker/WTs/take-transport/src/take.mjs',
'../../../../../../../../home/asa/devel/machinome/videomaker/WTs/take-transport/transport/take.ts'
```

It also showed (finding 1 below) that the script embeds `transport/take.ts`
and not `src/take.mjs`: the stage calls only `attachMachine`, so esbuild
drops the pose rule from the script, while reading it, so it is an input of
the key. The two-checkouts test was corrected to pin the transport's name in
the script and both names in the key's record, and the scenario of the
`react-stage` delta and design D8 were worded to match.

`src/stage-build.mjs` (the two roots, the runtime's sources over `stage/`
and `transport/`) and `test/support/reach.mjs` (what `src/render.mjs` and
`src/stage-build.mjs` read; `transport` among the paths a module may
locate) changed:

```
 ✓ |pure| test/transport-boundary.test.mjs (4 tests) 55ms
 ✓ |pure| test/memo.test.mjs (26 tests) 1977ms
 ✓ |pure| test/stage-types.test.mjs (12 tests) 5423ms
 Test Files  3 passed (3)
      Tests  42 passed (42)
```

### Layer 5: `window.film.transport`, and the transport beside the double

The new test of `test/browser/take.test.mjs` was written after the stage
gained `transport(key)` (the stage was changed with layer 4), so its red is
shown by running it with that one line of `stage/runtime.tsx` removed
(`npm test -- --project slow test/browser/take.test.mjs -t "window.film.transport"`):

```
   × window.film.transport reports the bank and the identity each frame on the take posed, the recorded bank at a mark, and null on a loop (take-transport) 870ms
Error: page.evaluate: TypeError: window.film.transport is not a function
 Test Files  1 failed (1)
      Tests  1 failed | 7 skipped (8)
```

`test/browser/transport.test.mjs` with `test/support/transport-bundle.mjs`
(the transport bundled by esbuild and served beside the double). Its first
run failed in the memo's reach, which read the helper's generated entry text
(`export {…} from './take'`) as an import of the helper and could not resolve
it; the entry is now written from the modules' names, and `transport/` is
declared in the reads table for the helper. Then, with the redraw of a pose
without a camera removed from `transport/take.ts` (a mutation):

```
   × a take transport beside the double seeks every mark of the counter's take to its recorded bank, by a restore and a redraw 301ms
   ✓ a take transport beside the double poses one time, another and the first again: one bank and identical pixels, the pose rule's 416ms
   ✓ a take transport refuses a viewer whose machine is not the take's, in the stage's words, before touching it 302ms
AssertionError: the mark nine is posed by a restore and a redraw, and no loop time is set
-   'setView'
      Tests  1 failed | 2 passed (3)
```

(The double paints a restored bank at once, so only the call order catches
it here; layer 6 asks the real viewer.) Restored byte for byte, both files
(`npm test -- --project slow test/browser/take.test.mjs test/browser/transport.test.mjs`, 10 s):

```
 ✓ |slow| test/browser/transport.test.mjs (3 tests) 1003ms
 ✓ |slow| test/browser/take.test.mjs (8 tests) 6829ms
 Test Files  2 passed (2)
      Tests  11 passed (11)
Test memo: 0 passed from the memo, 11 run
```

The seven existing take proofs of `test/browser/take.test.mjs` pass through
the transport: the pose by bank with no loop time, one restore and then the
camera per pose; A-B-A; the mark following the bank; the mount refusals in
the same words (`View counting.view in shot once: the viewer gives no
machine for this clocked document`, `…: the viewer's machine is
another-machine, and the take was recorded on … (take.identity)`); the
replay; the bank checks.

### Layer 6: the transport on the API 29 bundle

`test/viewer/transport.test.mjs`: the bundle mounted directly on the fixture
project's committed exports (`counter`, `seesaw`) under on-demand rendering,
the transport bundled beside it. Written after the transport, it passed on
its first run
(`VIDEOMAKER_VIEWER_BUNDLE=… npm test -- --project viewer test/viewer/transport.test.mjs`, 4 s):

```
 ✓ |viewer| test/viewer/transport.test.mjs (2 tests) 1543ms
   ✓ the take transport seeks the counter's take on the real viewer: the bank at every mark is the recorded one; one time, another and the first again hold one bank and draw identical pixels 996ms
   ✓ the loop transport seeks the seesaw's loop on the real viewer: one time, another and the first again draw identical pixels, and a time past the loop is its end 545ms
      Tests  2 passed (2)
Test memo: 0 passed from the memo, 2 run
```

So its red is shown by mutations of `transport/take.ts`, each restored byte
for byte afterwards:

- `seek` posing `bankAt(doc, at - .5)`:
  ```
     × the take transport seeks the counter's take on the real viewer: … 886ms
  AssertionError: the viewer holds the bank the take records at the mark nine
  ```
- the loop's `seek` not calling `setTime`:
  ```
     × the loop transport seeks the seesaw's loop on the real viewer: … 769ms
  AssertionError: two loop times are two pictures: setTime drew before it returned
  ```

The loop proof is the one design D5 asked for: on this bundle `setTime`
draws before it returns under on-demand rendering, as the contract states,
so `attachLoop.seek` is `setTime` alone.

A probe, not a mutation the suite must catch: with the redraw of a pose
without a camera removed, the take test **still passed** on the real viewer
(`Tests  1 passed | 1 skipped`): on this bundle `restore` draws the bank
before it returns (finding 2).

## The final runs

On the final content (the evidence file excepted), the Node suite cold
with the API 29 bundle selected
(`VIDEOMAKER_VIEWER_BUNDLE=… npm test -- --cold`):

```
 ✓ |stage| transport/take.test.ts (15 tests)
 ✓ |stage| transport/clock.test.ts (13 tests)
 ✓ |stage| stage/take.test.tsx (5 tests)
 ✓ |pure| test/transport-boundary.test.mjs (4 tests)
 ✓ |slow| test/browser/take.test.mjs (8 tests)
 ✓ |slow| test/browser/transport.test.mjs (3 tests)
 ✓ |viewer| test/viewer/transport.test.mjs (2 tests)
 ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests)
 ✓ |viewer| test/viewer/take.test.mjs (6 tests)
 Test Files  45 passed (45)
      Tests  446 passed (446)
Test memo: 0 passed from the memo, 446 run
exit 0 elapsed 885 s
```

(408 on the base. Five new files hold 37 tests; `test/stage-types.test.mjs`,
`test/repository.test.mjs` and `test/browser/take.test.mjs` gained one
each and `test/memo.test.mjs` one assertion; `stage/take.test.tsx` went
from seven to five: its three `viewMachine` proofs are now
`attachMachine`'s in `transport/take.test.ts`, and one proof of a bank
without a transport was added.)
Layer 6 ran on the bundle, none skipped.

The Python suite (`env -C python PYTHONPATH=python …/.venv/bin/python -m pytest -q`;
nothing in `python/` changed):

```
291 passed in 28.04s
```

## Records

ADR-020 (STAGE), Proposed, written and indexed; `docs/stage.md` (the view
row; the bundle's names and key), `docs/movie-document.md` ("The stage":
the pose through the transport, `transport(key)`),
`docs/architecture-overview.md` (the pipeline, the stage paragraph, the
bundle's names, "What is changing"), `AGENTS.md` (layer 4), `CHANGELOG.md`
(one bullet under `Unreleased`). The records pin of
`test/repository.test.mjs`, red above, then green
(`npm test -- --project pure test/repository.test.mjs test/transport-boundary.test.mjs`):

```
 ✓ |pure| test/transport-boundary.test.mjs (4 tests) 17ms
 ✓ |pure| test/repository.test.mjs (13 tests) 130ms
 Test Files  2 passed (2)
      Tests  17 passed (17)
```

## Edits to the planning artifacts after the planning commit

- `specs/react-stage/spec.md`: the two-checkouts scenario names the
  transport in the script and both the transport and the pose rule in the
  key's record (finding 1); "one render" per frame became "one restore and
  one camera call per frame, as before" (finding 2).
- `design.md` D7 and D8, `proposal.md`: the same two precisions.
- `tasks.md`: ticked.

## Findings

1. **The stage bundle reads the pose rule and does not embed it.** The
   stage calls only `attachMachine`, which does not use `bankAt`, so
   esbuild reads `src/take.mjs` through `transport/take.ts` and drops it from
   the script. It is still an input of the bundle's key (the metafile lists
   it), which is where its name mattered: without the `videomaker/src` root
   the record named it, and the transport, by a path of the machine. Not a
   defect; the scenario and the design say so now.
2. **On the API 29 bundle `restore` draws before it returns.** With the
   redraw of a pose without a camera removed, the layer 6 take test still
   passed (A-B-A distinct and identical): the restore alone changed the
   picture under on-demand rendering. This agrees with the pose-a-take
   design (the viewer cycle `on-demand-clocked`: "`restore`, `reset` and
   `move` pose and draw before they return") and not with ADR-012's
   sentence that the viewer "draws a restored bank on the next `setView`".
   The contract's redraw (`setView(viewer.view())`) is kept, by the
   orchestrator's ruling at the review of this cycle (4 October 2026): it is
   the viewer's documented rule, not a cost to trim. As the orchestrator
   reported it, the viewer's own reference says that a capture after the
   pose alone keeps the last framing's clipping planes, and that a capture
   after `setView` depends only on the bank and the view. So a picture that
   only `restore` drew can carry clipping planes fitted to an earlier pose,
   which the fixture counter's A-B-A did not show; the redraw is what makes
   a seek's picture a function of the bank and the view alone. (Quoted from
   the orchestrator's message; this cycle did not read the viewer's
   repository, which a Videomaker change does not inspect.)
3. **The memo's reach reads import lines inside strings.** The helper that
   bundles the transport for the browser tests first wrote its esbuild entry
   as a string literal holding `export {…} from './take'`; `reach.mjs`'s
   pattern took it for an import of the helper and refused the run (`imports
   ./take, which does not resolve`). The entry is now written from the
   modules' names. A pattern over text cannot tell code from a string; the
   failure is loud, so this is a note, not a defect to fix here.
4. **A process slip of this cycle.** To restart the final run after a
   comment edit, the first final run was stopped with
   `pkill -f "[v]itest.mjs run"`, a pattern that would also have matched a
   suite running in another worktree at that instant. The process list
   right after showed one remaining vitest worker, which exited; whether a
   suite of the parallel `live-server` cycle was running then is not known
   from here. The second final run below was started and left to finish.
   Recorded by the orchestrator as a process finding of the campaign: no
   `pkill` with a pattern, in any worktree.

## What was not done

- No spec synced, no change archived, ADR-020 left Proposed: the pilot
  ordered the campaign to stop before sync.
- No browser test drives a clock (design D6); the clocks are proved at
  layer 4 only.
- No real film was rendered or proved; fixtures only. No speech was bought.
