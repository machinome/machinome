# OperatingCurta minimal path-input retention

This viewer-only cycle follows ADR-074. The existing `ExpressionPath.bind` copied every key of the run's bank into its generation-reset snapshot. A red test instrumented 213 unrelated enumerable getters beside the two names an expression reads; the old path touched all 213, the new one touches none. A separate test resets the shared expression store between bind and `at` and checks bound, present and absent names against an uninterrupted path. No expression semantics or runtime dt changed.

Pinned document: `Calculators/Curta-Type-I-3x/_build_source_timing_2026_09_22/operating_curta/viewer.json`, SHA256 `cdbb284e56672aa905e38a25c7efd1f3169fc8f128cd3195f27baf7745a9c28b`, version 11, 213 coordinates, identity `0aac38742fcad90b0818ed07bd2bd4e239873169ffa9d207b3a18f869a732ca3`. Node v24.11.1, no WebGL, `dt=1/240`, selector 1 to 1 over 0.2 s, then exactly 48 of the 480 crank ticks. The paired builds were run consecutively in a reserved CPU window:

| Viewer source | Selector completion | First 48 crank ticks | Mean per crank tick | Crank after 48 |
| --- | ---: | ---: | ---: | ---: |
| `f748463` (ADR-074 cache) | 7.021 s | 24.420 s | 509 ms | 36° |
| minimal-input branch | 4.127 s | 22.075 s | 460 ms | 36° |

The latter saved 9.6% of the bounded crank window and 41% of selector setup in this pair. Its SHA256 over sorted `[key,value]` entries of the complete committed bank is `3d63c86327099f82643b75ebe7f865d40177588ca1d77ee6b820c4a8b474696f`, exactly the base build's. The v11 source-timing corpus passes full banks, commands, records and restored replay. No full 360° browser turn or visible final readout is claimed: multiplying 22.075 s by ten would give 220.7 s only if later ticks cost the same, still vastly slower than the two-second declaration. The prior [browser screenshot](operating-cache-partial-browser-2026-09-22.png) remains the latest bounded visual evidence, not acceptance of this new build.

`PathValue.at`, `nest` and whole-expression evaluation remain significant CPU costs; this cycle did not touch them. The two wall-speed floors that fail on this host were already shown to fail at the unchanged base in the previous cycle. Semantic tests and typecheck pass; their exact commands and status accompany the cycle commit.
