# Source-only shots: implementation evidence

## Pre-change compatibility capture (task 1.1)

Before any runtime edit, `node experiments/film-production/source-only-baseline.mjs`
captured 13 sampled poses at width 960 with Viewer API 28 bundle SHA-256
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`
and Chromium `151.0.7922.34`. Full request JSON, each numbered PNG, exact
timestamps and output settings are retained in ignored
`_build/source-only-prechange-p18Xnz/report.json` (report SHA-256
`4b7d4198b3b4eb73eb95ec8e40a50ce01fc3a76f4335f00fc6962d451a08d305`).
These are **13 sampled poses**, not a claim to have compared every frame of
four films.

| Existing consumer | Episode SHA-256 | Sample times (s) | PNG SHA-256, in time order |
| --- | --- | --- | --- |
| `demo-legacy-02` / 0.2 model | `658dc7d3ef08f43757e00296d02a28be739b0e610931c7acdd7c31d3c3fd06f2` | 0, 1, 3 | `c23c566ff1aca1ccffb7fcc717679e1d425d82d2dc5964a6a05b39deda7984bc`, `6314b4c8c899c10df721002c0db7dfead4b97c6b9b15efd00b4c7dd8305bdb5d`, `cd8a6197f11b52d93a3cb6a997ac320a69282afc7f259e03082ee39cc5eb5ea4` |
| `demo-annotate-a-part` / 0.3 annotated | `360e8f738eff01a78fc37d832be9271b4b93a56aed557a17c5f79f0558a80de3` | 0, 1, 4.5 | `6acbf4aef4451e51f9b0a0aa866647a34324ffb38891c9d5a78e392a90d12836`, `cc36f1556ddf0f6c5146c3c579d372b37620669c7827d675c1063008a67d8ca0`, `73189340626a181351b73df37414c02d4886e2d40b414821fefee28e039d1474` |
| `demo-keyframes-and-easing-2` / 0.4 model | `2718b6e49326856075929db522796137960dfcef0ea27d260b18b0711e1bc447` | 0, 1, 4.5 | `8ce692cccece6e70476261d71d46a42e9d630d248a6a1f2351e53ccf2f7d9d3d`, `4ab79fe4bce3a7d2d9e01e807941a112cde1722035876c91b0389acf13d36eb6`, `bad90cf5fe989551070fb9f94495b86629499143a5eef904a24578ebb8e5a0ba` |
| `demo-incremental-source-grid-fixed` / 0.4 split | `a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96` | 1.2, 2.5, 4.7, 5 | `f320aaeca52650e87c006272ae530175452e9e41b342ff698e193adcf3e3d75c`, `e5edbaa9aa29c37136999ff2b16c4b889bff4920a54010fba54f58bdae45e454`, `53175267a1f8378f8d8f4ece4283625120744912d0e4b5214eccfeb1819b9252`, `bcfa9249b993f53d3f54efb85f1568514b67e0ae7089329bc069000f1aac5911` |

All four episodes used the same model manifest SHA-256
`92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9`.
Their production YAML SHA-256 values, in table order, were
`7bd0b1fd474462329c80e3cc8d4e8e1ddc5396abbf9518d85d0b7a7f98451cb3`,
`95bd905cab668baa9d82914ac13df2efb4663516995188c16fff1fa362c97c23`,
`6ce70fb6d1c05d8e64744df72f15cdf70c7c8b4b3ba570707ac76573a4972280`,
`fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3`.
The split case's verified cached take SHA-256 was
`fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8`.
Later exact comparisons must retain these episode, production, model, viewer,
output and take inputs; this is a bounded consumer pin, not a broad
reproducibility audit.

Every sampled old request omits `layout`. Its 4.7-second transition has
outgoing shot `source`, the complete pinned text
`water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)`, and
`cursor: false`; the pre-change renderer's outgoing continuation is therefore
measured, not inferred.

## Actual red-test chronology, before runtime edits (tasks 1.2–1.5)

The first `node --test --test-concurrency=1 test/source-only-shots.test.mjs`
run was 0/3: the valid opt-in was refused as `Unknown shot field: layout
(shot second)`; the missing-code named refusal was masked by that same old
unknown-field error; the timeline returned `layout: undefined` at the 1.15 s
fractional incoming boundary. After splitting the cases into independent
subtests, the expanded pure suite was 0/12: 0.2 and 0.3 silently accepted
the unsupported field, all named 0.4 refusals remained masked by the unknown
field, and opted source and dependent join keys remained equal to their split
counterparts. The key-specific failure reported identical B keys
`49f52b966cb3a23d3767f081d7be0d445b0a369020b9b3f8c4dc6cf7c389461a`.
These failures prove parser/request/cache absence independently.

For browser-level red, the old parser cannot load the authored opt-in.
`experiments/film-production/source-only-real-browser.test.mjs` loads the
otherwise identical valid Leonardo `episode-baseline.yaml`, then injects only
`layout: source-only` into in-memory shot/frame requests. It does not modify
project source. The initial browser run found the old panel at
`x=48,y=135,w=470.39,h=307.81` on a 960×540 frame, not the proposed
plain-stage `x=48,y=86.4,w=864,h=340.2`. The first waterwheel emphasis onset
occurs while typing is still incomplete; an initial assertion incorrectly
expected the whole line. That test was corrected to compare the exact
`frameAt(e,onset).code.text` **before** a focused rerun, which then failed on
the intended panel geometry. This fixture/test correction is not counted as
a product red. The old long-excerpt overflow guard already refused, but its
message omitted the output frame time; a separate tightened opt-in assertion
then failed because it expected `source at 3.60 s` and got only `source`.

The private real-viewer join run covered both directions of fade, dissolve,
wipe and slide. In all eight cases the opted picture was byte-identical to
the split control (red). At the same time, independent same-instant pixel
math passed the pre-existing limits: fade/dissolve at most approximately
0.5 channel level (allowed 2), wipe/slide exactly 0. The real hidden-lens
preview returned source-shot `measured`/`expected` projection distances at
both lens keys (about 5.245/8.257 pixels) despite the requested picture
having no visible model; that is a false visible-lens claim, not a crash.
The initially saved images used ignored `_build/source-only-red-browser/`;
their later overwrite is disclosed below, so they are not claimed as an
immutable original-red image set.

The tracked portable synthetic suite `test/source-only-browser.test.mjs`
uses a generated Viewer API 28 double and no private project path. Its first
pre-change run was 1/4: the page still used a 313.59-pixel split source at
640×360 instead of 576 pixels, and all eight joins again matched their split
controls while preserving the same-instant pixel tolerances. The existing
long-excerpt overflow refusal passed. The lens test initially stopped on a
*test-double defect* (its `setView` did not reject NaN); after correcting the
double, the focused lens rerun failed on the intended false visible-projection
report (`measured` about 3.497 and 5.504 pixels). The added first-shot and
missing-panel tests then both failed as intended: first-shot source was still
split-sized, and `display:none` on the source was not refused. The full
post-expansion portable browser run was **1/6** (the old overflow refusal
passed; all five behavior/geometry groups failed). After tightening the
overflow's time-context promise and panel-refusal patterns, a focused 0/2 run
confirmed the old overflow error lacks `at 3.60 s` and a hidden source panel
is still not refused. A separate visible
split control passed with two positive projected lens measurements before any
runtime edit. A separate pure C-key control failed: its model requests were
identical but its dependent join key remained the old
`323a54f2da84d3a700a8829d9e00f7d101a7d8e1f5e21a16071e269319397e5c`.
No runtime source was edited during any of these red runs.

The final pre-change portable browser rerun after all test corrections was
**1/7 in 19.19 s**: only the unchanged visible split-lens control passed.
The six failures were the source-only appearance, named overflow time,
first-shot source mount, absent-panel refusal, hidden-lens evidence, and the
eight-case join matrix. The independent pure dependent-join check also
failed as above. The browser/test lease was released after these runs; no
renderer, page, parser or timeline file had been edited.

Root independently reproduced the red C-key equality above and the portable
first-source bound failure (old source width 313.59 px versus intended 576 px
at 640×360) before approving implementation. These are independent checks of
the recorded gate, not retroactively added tests.

## Implementation diagnostics and exact compatibility

After root accepted the red gate, the opt-in validation/request changes made
`test/source-only-shots.test.mjs` **13/13**. The first portable page/proof run
was **20/20**, but the pinned real-viewer run found two further defects:
exact replay differed at seven pixels, all on the first glyph edge at x=48
(filename rows 101–104 and code rows 127–129, maximum channel delta 56), and
the preview fade into `source` failed at 1.25 s (maximum 115 versus existing
limit 2). These were not written off as font tolerance or accepted imagery.
The preview's saved outgoing proof showed a blank model because its
same-instant override accidentally inherited the *incoming* source-only
layout. The composed frame itself showed the outgoing sawmill. A new portable
cross-shot override assertion failed `block !== none` before correction. A
new shared-shift assertion also failed: both `#source` and the hidden
`#viewport` could move together and fool a relative-only bounds check.

The narrow corrections were: clear inherited layout only when `pose` receives
a different shot's full request lacking `layout`; compare the source rectangle
against the fixed plain-stage fractions of the output dimensions rather than
only the hidden stage; and run the existing repaint flush for every source-only
frame so left-edge text antialiasing no longer depends on prior poses. The
two newly red portable tests became **2/2** green. A fresh pinned real-viewer
focused run at `_build/source-only-real-gEUlOU/` became **2/2** green for exact
seek replay and hidden-lens/fade preview. No fade, dissolve, wipe, slide or
glyph tolerance was widened.

Root's width-960 visual read found the old split-size source type too small
when carried into the 864-pixel source-only rectangle. The only fit change was
`.source-only #source pre {font-size:1.8vw}`: same family, syntax colours,
layout, chrome and default split CSS. A later fresh real-viewer run at
`_build/source-only-real-8KapLA/` was **4/4** green: visible literal/fitted
source, measured emphasis and exact replay; named overflow refusal; changed
hidden FOV/up without false visible projection and positive split control;
and eight fade/dissolve/wipe/slide directions with same-instant pixel bounds.
Its `appearance/full.png` is the larger-type review still; aesthetic approval
remains with root/pilot.

`npm test` (the repository's scoped `test/*.test.mjs` plus retained
`experiments/dark-source/emphasis.test.mjs`) passed **158/158** tests with no
failures or skips in 251.26 s. The preceding suite had 136 tests: 133
scoped tests, already including the two late media assertions from the prior
cycle, plus three dark-source tests. The two new portable source-only files
contribute 22 tests, verified independently by running just those two files
at **22/22** after the comment-only final source edit. The original parser,
request/cache, page and transition behavior assertions have the red outcomes
recorded above; later safety and compatibility controls were added as green
regressions, except the separately recorded shared-shift and cross-shot
override failures, which were red before their fixes. This is not a claim
that all 22 tests ran red before implementation.

`node experiments/film-production/source-only-baseline.mjs --compare
_build/source-only-prechange-p18Xnz/report.json` produced ignored
`_build/source-only-postchange-HSVe8d/report.json` (SHA-256
`6de1a9b0c76431223354163707100b1d7edcb282eb4c4bec1c2874d2c790cfb1`).
It verified **13/13 PNG pairs byte-for-byte**, all 13 serialized `frameAt`
requests, episode hashes, output settings, Viewer API and Chromium version
against the preserved pre-change report. The 0.2, 0.3, model-only 0.4 and
split 0.4 consumer images are therefore unchanged at these sampled instants.
After correcting only the explanatory repaint comment in `src/film.js`, the
same comparison was run again with the final source file and produced
`_build/source-only-postchange-ZK4xyR/report.json` (SHA-256
`369a26b4e525b6459e8e8ddc7ee1b46f78d576d77db6f6056047d1dfbd3ef712`):
again **13/13 PNG pairs** and all serialized requests matched. The earlier
post-change comparison remains a separate retained run, not overwritten.

Evidence hygiene: the first private browser test used fixed
`_build/source-only-red-browser/` filenames. The first post-code rerun
overwrote some original red screenshots there, and an earlier successful
preview `report.json` may coexist with a later failing preview. That directory
is **mixed and not an immutable original-red image set**. The original red
assertion outputs and saved baseline remain valid. The experiment was then
changed to allocate a fresh ignored `_build/source-only-real-*` root per run;
the two fresh roots named above must not be interpreted as pre-code captures.

## Leonardo real-film proof (tasks 3.1–3.3)

The root-authored `videos/demo-source-only` fixture was run once by the
empirical worker under an exclusive browser lease. The complete project-owned
record is `videos/demo-source-only/source-only-evidence.md`; ignored raw
`videos/demo-source-only/_build/evidence/source-only-2026-09-29T18-49-57-465Z-38eb6fbe-072f-443f-bf3e-27a4fe8411f0/report.json`
retains every frame hash, manifest, cache origin, timing, preview and encoded
review still. Runner SHA-256 was
`2bb41ca6fdf224db1cc5a088e81ee3991f556203d7414a2cd99dcf878849d854`;
reviewed renderer source-tree SHA-256 was
`d095c77dc2622b43e964fa67e15b386bd50cd780f41be7d3ab154a965c1d42db`.
The fixed Viewer API 28 bundle and pre-change 13-pose report hashes remained
at the values above, and pre/post source, production, model, viewer and cached
take checks passed.

Cold split captured 70/70 frames (17.806 s); unchanged warm reused 70/70
(1.475 s). The one-line source-only edit captured 45 and reused 25 (10.797 s):
the changed source shot B captured 35, its dependent transition shot C 10;
unchanged A and D retained baseline generations and reused 12+13. Separate
source-only cold captured 70 (18.064 s). Warm versus baseline and incremental
versus cold matched **all 70 PNGs, all decoded-frame records and MP4 hashes**.
The edited and cold MP4 SHA-256 was
`7e2585c3a4d5dcda9014f7bb1fdfee8fe787c64b244319c885fe795cf7dddd7d`.
Each film probed as silent H.264 960×540, 10 fps, 70 frames, 7.000 s. The
same run rechecked 13/13 preserved pre-change legacy PNG/request samples,
matching root's independent post-change compatibility comparison; it does
not assert all-frame equality for those older films.

Real preview proved literal fitted source, no visible model on its own
source-only frames, visible model controls, measured two-word emphasis, exact
seek replay, both fade checks and outgoing/incoming source-to-model join
semantics. An in-memory first-shot source-only clone showed a nonzero 864×340
hidden mounted viewer canvas, later visible model and exact source replay.
The empirical worker inspected the encoded contact sheet and selected
individual stills; no audio was generated or listened to. Focused source-only
22/22 and `npm test` 158/158 are recorded above, as are the resolved-pose
hidden-lens and positive visible-lens controls. No pixel tolerance or
preview-proof limit was relaxed.

## Independent root acceptance (task 3.4)

On 29 September 2026 root reviewed the final runtime, tests and documentation,
then independently ran both portable source-only files: **22/22 passed in
26.89 s**. Root rehashed the preserved pre-change and final post-change reports
and all 26 compatibility PNGs, compared the 13 complete request objects and
episode/viewer/browser/output identities, and verified all 13 byte pairs.

Root independently checked the real-film report SHA-256
`d7ec36ca2c25bc8b9e79b35c5cd1d3eba6d92ccf77d068c8f9068bb04372cf8a`,
all 280 rendered PNG files, four MP4/manifest bindings, all 16 selected cache
index hashes, retained A/D generation origins and new B/C origins. All 70
warm/baseline pairs and 70 incremental/cold pairs match. Separate FFprobe and
full FFmpeg decodes confirmed both source-only films' 70-frame silent H.264
streams and all decoded-frame MD5 records. Direct independent MP4 extraction
of frames 15, 30, 47, 49 and 69 reproduced the saved review PNG hashes.

Root inspected the 22-sample encoded contact sheet (its two trailing black
cells are padding, not film), the native 960-pixel encoded source frame, and
the real-viewer source still. The literal drive line is readable, its two
measured identifiers are distinct, the source picture has no competing
model pane, the chrome remains, and both fade neighborhoods return to the
actual model without a source/layout discontinuity. This is a bounded visual
acceptance of the current-style source-only feature, not approval of a dark
theme, an audio review, a release decision or an all-frame legacy audit.

The original 46-second demonstration remains byte-identical at SHA-256
`c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e`.
The empirical run used workflow HEAD `a9b280e` with the explicitly pinned
uncommitted source tree above; the closure commit records that tested content.
Root accepts baseline promotion and archive on this branch. No main merge,
push, publication, new speech purchase or mechanical-source edit is implied.

The five source-only requirements were synced verbatim (with the main-spec
heading/Requirements form) and compared against their delta. All tasks were
complete, all nine baseline specs validated strictly, and the whole change
was archived as `2026-09-29-source-only-shots` without warnings.
