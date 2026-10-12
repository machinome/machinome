# OperatingCurta path-piece cache: bounded browser and engine evidence

Viewer base `fcecb1a`; document `Calculators/Curta-Type-I-3x/_build_source_timing_2026_09_22/operating_curta/viewer.json`, SHA256 `cdbb284e56672aa905e38a25c7efd1f3169fc8f128cd3195f27baf7745a9c28b`. This is the unchanged v11, 213-coordinate performance fixture, not the project's later collar/bound work. Browser bundle after the cache: SHA256 `0c26af11ae389da99706704190989637b2cb6ed26e8bad186dea3c217d680e86`.

## Same export, no WebGL

Node v24.11.1, in-thread `Engine`, `dt=1/240`, selector 1 to 1 over 0.2 s, then `Turn crank` for exactly the first 48 of its 480 ticks. Both runs loaded the same document and reported identity `0aac38742fcad90b0818ed07bd2bd4e239873169ffa9d207b3a18f869a732ca3`, selector completed and crank 36° after 48 ticks. The first 48 ticks are not the whole revolution, and the selector time is separate.

| Viewer source | Selector completion | First 48 crank ticks | Mean per crank tick |
| --- | ---: | ---: | ---: |
| base `fcecb1a` | 11.553 s | 32.605 s | 679 ms |
| incremental bind | 7.004 s | 27.838 s | 580 ms |

The 14.6% crank-window improvement is real but inadequate. Multiplying 27.838 s by ten gives 278.4 s (4.64 min) for 480 ticks **only if later ticks cost the same**; no full-turn engine time is claimed. A second base/cache pair serialized all 213 bank entries after the same 48 ticks (sorted `[key, value]` pairs) and produced identical SHA256 `3d63c86327099f82643b75ebe7f865d40177588ca1d77ee6b820c4a8b474696f`; that pair took base 29.178 s and cache 26.525 s for those ticks, with both at 36° and selector completed. The committed Curta v6/v7/v11/constrained corpus independently passes full-bank, command, record and restored replay equivalence; it does not contain this project-specific 213-coordinate export.

The post-cache CPU profile (`/tmp/curta-cached.cpuprofile`, not committed) still places repeated path binding, path point evaluation, `nest`, whole-expression `compute` and name resolution high. `ExpressionPath.bind` also copies the entire flat bank on every piece, including when only a few names matter. Those are next-cycle candidates, not evidence of a completed interactive turn.

## Standalone Chromium

Headless Chromium with SwiftShader served the actual export locally and loaded the rebuilt worktree bundle. It reported API 24, a real worker, 25 controls and 213 bank keys with no page errors. A real pointer drag of selector 1 produced digits `[1,0,0,0,0,0,0,0]`, shaft 36°, crank 0. A real pointer click on the crank handle's `one revolution` control submitted `Turn crank`; the panel showed `running…`. After the bounded 45-second wait (plus earlier setup and scheduling), the worker's retained bank had reached 108°, but the [captured canvas/readout](operating-cache-partial-browser-2026-09-22.png) visibly showed 60°. This is render/update lag in addition to slow execution. The command had not completed, so neither a final readout nor restored replay is claimed.

## Suite interpretation

All semantic widget suites passed, including the complete source-timing Curta corpus. The two existing wall-time floors in `src/run/cost.test.ts` failed both on this cache branch (719 vs required >900; 2453 vs >3000 ticks/s) and on unchanged base `fcecb1a` (704 and 2392 ticks/s) in the same host conditions; they are not cache regressions. Exact resolution-count tests were updated to account for avoided work: the curved-search fixture 278→274, Clearing 471.1→459.1 per tick, Curta carriage 6277.4→4301.9 per tick. Search samples and bank behavior remained pinned by separate tests.
