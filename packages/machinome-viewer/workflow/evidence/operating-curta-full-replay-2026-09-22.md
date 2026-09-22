# OperatingCurta: complete no-WebGL turn and replay on the pinned v11 export

This records the historical pinned v11 run only, **not** a claim of an interactive or visibly accepted browser turn at that checkpoint. A later fresh-project export and actual browser turn are recorded in [the current-export evidence](operating-curta-current-export-2026-09-22.md).

The in-thread viewer engine was bundled from viewer `3ef7482` immediately before this run. Viewer main later moved to `e771a28`, a CI workflow/README-only merge with no widget source or package difference. The document was the unchanged `Calculators/Curta-Type-I-3x/_build_source_timing_2026_09_22/operating_curta/viewer.json`, SHA256 `cdbb284e56672aa905e38a25c7efd1f3169fc8f128cd3195f27baf7745a9c28b`, v11, identity `0aac38742fcad90b0818ed07bd2bd4e239873169ffa9d207b3a18f869a732ca3`, 213 bank coordinates. Node v24.11.1 ran with `dt=1/240` s and a 1024-entry recorder. No WebGL or browser process was involved.

Selector 1 moved to 1 over its declared 0.2 s in 48 individual ticks, completing in 4.119 s wall time. The pre-turn bank SHA256 (JSON of sorted `[key,value]` entries) was `34a629c55d4877f3d62a44ed8d80be27f9270d4a1ff293a853f8d747a776494e`. A `Turn crank` instruction then advanced one tick per call, all 480 ticks, with no sampling shortcut:

| Pass | Status | Admitted | Crank wall time | Terminal tick/clock | Full 213-key bank SHA256 |
| --- | --- | ---: | ---: | --- | --- |
| First | completed | 360° | 192.371 s | 528 / 2.2 s | `78196167897eae674cda4048269b6344a38282e8ecd45f4d3ba7f60de2b6253c` |
| Restored replay | completed | 360° | 181.700 s | 528 / 2.2 s | `78196167897eae674cda4048269b6344a38282e8ecd45f4d3ba7f60de2b6253c` |

After the first pass, restoring the exact pre-turn snapshot returned every bank value to its original value (`Object.is`), including crank 0. After the replay, all 213 terminal values again matched the first pass by `Object.is`, with no mismatches; both full terminal snapshot hashes were `727b80450ca63bddf4c524ecb0d7e860ab20794c973f78c62d0b4efd2b25949a`. Both had crank 360°, physical crank part −360°, selector 1, result ones 76° and tens −16°, and no stop records.

The original diagnostic process exited **1**, not 0, because its final assertion incorrectly compared the *cumulative* recorder-ring hashes. The first ring contained the selector's 48 trajectory entries and four crossings before the crank (528 trajectories, 507 crossings at terminal); `restore()` intentionally clears all three rings, so the replay ring contained only the crank (480 trajectories, 503 crossings). The bank and snapshot parity checks themselves passed. This recorder lifecycle is explicit in `Run.restore`; cumulative ring inequality is not a mechanical replay divergence. The harness has been corrected to compare turn-only suffixes, but that corrected version has **not yet been run through another full Curta revolution**.

The corrected accounting was exercised separately on the committed seven-coordinate `tests/fixtures/clearing/viewer.json`: a 24-tick preparatory command followed by a 24-tick command produced 48 retained trajectory entries on the first pass, then 24 after restore/replay; first-pass and replay *command-local* trajectories and the one crossing were byte-identical, as were all bank values. That small probe exited 0. It establishes the recorder comparison method, not this Curta's as-yet-unmeasured turn-local recorder hashes.

The observed 192–182 seconds per revolution is the actual in-thread cost, not the earlier 48-tick extrapolation. It remains roughly two orders of magnitude slower than the instruction's declared two-second drawing duration. The later fresh-export browser turn and corrected replay are recorded separately; this historical harness exit remains 1.
