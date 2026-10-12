# OperatingCurta expression capacity: measured before/after

This is a viewer-only local performance finding from a committed mechanical project. No framework or project source is copied into this repository. The project outputs below are ignored build artifacts, not committed viewer fixtures; the viewer-owned unit test reproduces the capacity boundary with a synthetic graph.

## Pinned inputs

- Committed `OperatingCurta` project `7586002`, public export `_build_current_operating_7586002/manifest.json`, SHA256 `c36432b1080387eeb40234532f516a9ae05f8a9822fd3f47f44ffbbb42f889d1`, program identity `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`, 213 coordinates. The published document is unchanged across all pairs.
- Current named `CounterTensOperatingTrial` candidate on project source `be890af`, public export `_build_counter_tens_trial_viewer_capacity_2026_09_22/manifest.json`, SHA256 `3ccbaf035afaa430c827576a21deb5c2098446e8ade6fe2c2effc0c2a96cfc10`, program identity `07d4f8d3341eded541ed5b6495fab160946bfe34e2912e9c73f2deb3328a5936`, 213 coordinates. It is a trial, not the default machine.
- Viewer source at `40659be` before this change; no source optimization was active during baseline or the temporary in-memory limit overrides. All CPU measurements used Node's in-thread viewer engine, `dt=1/240`, no WebGL, with the same bundled source and document.

## Cause

The 50,000-node expression trigger is below the committed machine's 97,474 prepared nodes. The direct generation probe showed generation 0 at load, 48 after the selector's 48 ticks, then 49–52 after crank ticks 1–4. Each crank tick re-created about 94,763 nodes. The candidate trial prepares 102,580 nodes. Two retained mounts containing both current machines share a 102,690-node union; releasing one leaves the table, and releasing the last clears it to zero and increments generation once. A temporary 125,000-node limit kept generation at 0 through the candidate's selector and first four crank ticks, without changing 3° admitted travel.

A V8 CPU profile of the committed machine's 48-tick segment at the original threshold (`/tmp/curta-current-7586002.cpuprofile`) attributed 13.1% of self samples to jokenizer's `binaryOperators` getter, 5.5% to DAG interning, further samples to tokenizer work and 5.8% to garbage collection. The evaluator itself remains a substantial cost; this cycle addresses repeated preparation, not arithmetic semantics.

## Paired 48-tick comparison

The same compiled temporary diagnostic ran on reserved CPU 15, with project work assigned CPUs 0–11 and framework profiling assigned CPU 14. Other host activity was not controlled. The selector advanced 48 ticks to digit 1, then `Turn crank` advanced **48 individual ticks** to 36°, with `record: null`. The only switch was the exported `EXPRESSION_LIMITS.nodes` value before `Engine.load`; no viewer source was changed for this pair.

| Limit | Crank 48-tick wall | Generation after selector + crank | Nodes at terminal | Terminal heap / RSS |
| ---: | ---: | ---: | ---: | ---: |
| 50,000 | 65.670 s | 96 | 94,763 | 77.5 / 398.0 MB |
| 125,000 in-memory override | 35.370 s | 0 | 97,474 | 139.2 / 573.1 MB |
| 125,000 source change | 37.440 s | 0 | 97,474 | 193.3 / 347.6 MB |

All three processes exited 0, admitted exactly 36°, ended at tick 96 with 213 coordinates, and produced the same sorted full-bank SHA256 `3d63c86327099f82643b75ebe7f865d40177588ca1d77ee6b820c4a8b474696f`. The in-memory override segment improved **46.1%**, and the built-from-changed-source segment improved **43.0%**, against the reserved-core baseline. The cache can retain about 2.5× as many nodes as before; terminal heap/RSS varied substantially between the two identically capped runs because of V8 collection state and other host activity, so these samples are not fixed per-document budgets. The 125,000-node trigger is finite and the last-mounted viewer still clears the table.

The earlier complete normal turn on the smaller `f7e4945` export took 197.923 seconds in Chromium. This newer expanded graph has **not** been run through a full browser revolution; even the optimized 48-tick segment projects a multi-minute turn, so this change does not claim the declared two-second drawing duration is achieved in wall time.

The viewer-owned red-first test `expression-lifetime.test.ts` prepares a 102,700-node graph, then asks three adjacent outer operations to retain its generation and value. Before the source change it failed in 394 ms (`expected generation 2 to be 1`); the existing 50,000-node threshold reclaimed it. The test is independent of the project's export.

## Browser and regression checks

The changed bundle (`2b23132094a25265db02f4be826b412c6418e96e3b17d5cd0bdc43843cf5e888`) mounted the pinned committed export in headless Chromium with API 24, 25 controls, 213 coordinate keys and no page errors. A 60-pixel pointer drag on the first selector yielded one terminal `digit_1` outcome `{status: completed, admitted: 1}`, digit 1 exactly 1 and crank 0. The export's embedded original bundle (`648da7dbfac1c802dfdb89fae7549a4c99a9dc194f1f67845313b0d9f94371c4`) gave the same terminal selector outcome and bank cardinality. An earlier progress screenshot showed digit 2 while a crank request was active; that mid-request image is not evidence of the selector's terminal result. The changed bundle subsequently accepted a real pointer crank request and reached at least 36° with correct opposite physical crank and 213 keys. Its progress image is in the originating project's ignored `_build_checks/operating-capacity-progress-browser-2026-09-22.png`; that partial browser check is **not** a completed revolution or bank-replay acceptance.

The current named CounterTensOperatingTrial public export was exercised by the same in-thread engine diagnostic: its 102,580 prepared nodes stayed in generation 0 through a 48-tick selector and the first four actual crank ticks at 125,000, admitting 3° with no exception. With the committed machine mounted beside it in the shared pool, 102,690 nodes stayed in generation 0. Releasing the first mount retained the pool; releasing the last emptied it and advanced one generation.

Focused expression-lifetime and running tests passed 123/123; an independent reviewer ran the expression and lifetime pair at 95/95 and found no lifetime blocker. Typecheck and widget build passed. The broader `npm test` process exited 1: 1,460 tests passed and the two wall-clock throughput gates in `src/run/cost.test.ts` failed under simultaneous host work; all four Curta source-timing replay fixtures passed. A paired cost-file rerun on reserved CPU 15 also exited 1 for both baseline viewer main `40659be` and the candidate, with the **same two** gates failing: Curta fixture 607 versus 877 ticks/s (required >900), ShiftedCarry quiet 2,301 versus 2,498 ticks/s (required >3,000). The candidate was faster in both paired measurements, but neither process was green, and concurrent host memory/CPU activity prevents treating those wall-clock numbers as an isolated throughput certification. No threshold was weakened or test skipped to present the broad run as green.
