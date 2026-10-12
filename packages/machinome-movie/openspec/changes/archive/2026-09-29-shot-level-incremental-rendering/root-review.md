# Root review

## Planning gate — 29 September 2026

Approved for implementation under the pilot's delegated film-production
commission, after Sol's proposal and root's adversarial review. This is not
a claim that the pilot individually reviewed these interface details.

The originating Leonardo finding is measured, not inferred from the roadmap:
`videos/demo-incremental-rendering/evidence.md` records 80 captures in 31.67 s,
an identical rerun with zero captures in 1.70 s, and a one-line interior-title
edit causing 80 captures in 32.11 s. Root independently hashed all 80 baseline
and edited PNG pairs: only frames 21–42 changed. Root also verified both MP4
hashes and inspected a contact sheet decoded from the edited MP4. The fixture
shows the actual sawmill and readable overlays, not a substituted model.

The baseline and edited MP4 hashes are respectively
`997b94bd98e54c02a6eb2c6e4e8c31d5a8d25a10728d5423504938ebd2ea3525` and
`50c674071bf64c84856f6978b38bca1eb0f80ab46822d1f4f36bf510fe0b2025`.
Their paths and complete source/viewer/export hashes are in the project
record; preserved artifacts remain in its ignored `_build/evidence/`.

Review refinements incorporated before this planning commit:

- Whole-shot granularity includes the incoming join. The measured fixture
  should reuse A+D (40 frames) and recapture B+C (40), not promise prefix-only
  reuse or the 22-frame observed pixel minimum.
- Global output instants and progress, outgoing continuation, actual reached
  media and measured word inputs determine validity. Nonvisual preload lists
  and unrelated clip extraction ranges are not common dependencies.
- The initial mount is conservatively common. First-shot edits can invalidate
  all shots; no universally minimal cache claim is made.
- Complete generations are attested atomically; failed captures/encodes must
  not masquerade as complete films or destroy a prior good output.
- Skipping cached poses can alter browser raster history. Every incremental
  PNG must equal a separately cold result exactly, including source/text and
  a fractional-grid case; tolerance relaxation is not an acceptable fix.
- Implementation starts with a behavioral failing test against the existing
  renderer. A missing helper import alone does not prove the originating bug.

No implementation or performance benefit has been approved as proven yet.
The apply agent owns focused red/green tests; the evidence agent then renders
real consumers under a separate browser lease; root verifies before closure.

## Implementation review and independent checks

Root read the complete new shot-cache module, renderer changes, documentation
and focused test file. Review found and Sol proved red before correcting:
nonvisual Viewer API refusal reasons entering the common key; measured onset
changes smaller than one output frame not entering the key; and contradictory
generation metadata being accepted despite intact PNG bytes. Sol additionally
proved and fixed a reused in-memory episode hiding a now-missing measured take.
The output probe now names the published film, and only the newly created
recovery link is removed after successful publication. Prior failed-run
recovery links and legacy caches are preserved.

After Sol's serial 133-test pass and two late media-assertion reruns, root
independently ran five critical browser/refusal tests: B-only lens locality,
all-PNG cold equivalence across the same-layout source gap, missing measured
take, contradictory generation index, and interrupted publication. All five
passed in 17.58 s. Root separately ran the three disposable dark-source
emphasis tests; all passed. Strict change validation and diff checks passed.
No browser raster tolerance was changed, and no forced repaint was needed
for the exact comparisons exercised so far.

The original relevant capture failure was genuinely red before implementation;
the remaining matrix was mostly added green. The evidence record distinguishes
these chronologies. Root accepts the bounded page/font test-method gap:
`stage()` hashes the actual film page/scripts; those hashes and the four known
regular/bold film/mono font hashes directly enter `commonKey`, which enters
every unit key. Root inspected that data path and the tested font records,
but did not mutate shared source or installed font files in a browser test.
This is structural verification, not a claimed font/page mutation red or a
cross-machine reproducibility audit. The behavioral requirement is unchanged.

The browser lease has passed to the empirical agent for the 80-frame consumer
and 70-frame source/fractional-grid consumer. Completion is still gated on
their real-frame equality and root's independent verification.

## Real-consumer gate: first pass and a held failure

Root independently hashed all 80 PNG pairs from the new incremental title
variant and its separately cold counterpart: zero differences, with 40
captures (B+C) and 40 verified reuses (A+D), versus 80 cold captures. Both
actual encoded MP4s match their recorded SHA-256
`50c674071bf64c84856f6978b38bca1eb0f80ab46822d1f4f36bf510fe0b2025`.
The original 46-second `demo-all-features` MP4 remains unchanged at
`c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e`.

The second, 70-frame source/fractional-grid consumer is **not yet passing**.
It has the expected 25 reused / 45 captured frames, but empirical comparison
found one differing model pixel at global frame 10 (inside reused A),
coordinate (487,262), maximum channel difference 5. The prior cold A and
the reused A agree; the separate cold run differs despite identical common
and A keys and frame requests. Root inspected the full PNG. Cold-run and
within-mount repeat diagnostics are now required to distinguish load-order
or raster nondeterminism from incremental state. No tolerance is relaxed,
no matching run is substituted for the failure, and closure remains held.

Root then independently hashed all 70 frames against each of three cold
variants: the original cold and repeat 1 differ at frame 10 only; repeat 2
matches. All recorded MP4 hashes match their files. Five visits to film time
1.0 within a single mount, including after other poses, are byte-identical.
The model source, kinematics and export hashes remain unchanged.

Sol built a bounded diagnostic using two coincident, differently colored
STLs, a fixed manifest/view/bundle, and reversed HTTP asset completion order
in four fresh mounts (ABBA), with five captures per mount. Root caught its
initial browser-flag mismatch; that preliminary run is preserved separately.
With production SwiftShader flags, A (red then blue) always produces PNG
`069361614c03ad12e160cdf1e77fbd4ff1547d2ae7db1b3407b6403d8442a2eb`
and blue center RGB [30,30,204]; B (blue then red) always produces
`529fc85e7466dc46b25f5bc293303c8614b03a0fe3597f7348bc43a9908f31cb`
and red center RGB [201,30,30]. Root reran the full ABBA independently and
verified every PNG/hash/pixel record in both runs (40 captures total), with
no page or console errors. This proves load-order-sensitive pixels in the
controlled overlap; its responsibility for Leonardo's exact pixel remains
conditional until the real-film proof passes after a narrow correction.

Evidence is in Leonardo's `demo-incremental-source-grid/postimplementation-evidence.md`
and `_build/evidence/{postimplementation-70.json,within-mount/,
load-order-diagnostic-production-flags/,root-load-order-diagnostic/}`.
The diagnostic source is `experiments/film-production/load-order-diagnostic.mjs`.
A separate viewer-owned prerequisite is being proposed on
`machinome-viewer/WTs/film-production-order`, based on `f040f45`; it must
preserve geometry, materials, ordinary depth behavior and the current API.
No cache equality exception or broader reproducibility audit is authorized.

## Repaired-viewer acceptance and closure

The viewer prerequisite is implemented, independently verified, baseline-synced
and archived at viewer branch commit `94cfcc0`, with bundle SHA-256
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.
Root's repaired-bundle ABBA replay verified all 20 PNGs identical despite the
intended opposite response orders, with no browser errors. Root additionally
reran the viewer's 61 focused unit tests and two exact browser tests.

Sol then reran both real consumers from new project-owned directories, keeping
all prior failures. Root independently rehashed every assembled PNG, each
saved manifest and MP4, and each referenced generation index. At 960 × 540,
10 fps, silent, with the frozen runtime and repaired viewer:

| Consumer | Baseline | Warm | Local edit | Separate cold |
| --- | ---: | ---: | ---: | ---: |
| 80 frames / title edit | 34.66 s | 1.94 s, 80 reused | 21.84 s, 40 captured / 40 reused | 34.68 s, 80 captured |
| 70 frames / source camera edit | 25.09 s | 1.99 s, 70 reused | 16.95 s, 45 captured / 25 reused | 25.09 / 25.18 / 25.06 s, 70 captured each |

All 80 edited PNGs equal their cold counterparts. All 70 edited PNGs equal
each of three independently cold mounts (210 exact comparisons). The reused
A+D generations retain baseline episode provenance; captured B+C generations
name the edited episode. The 80-frame edited/cold MP4s share SHA-256
`152e2604b25459ede7627bea7357fe9d072f2dcebb4d0812af14269d9aee7d69`;
the 70-frame edited/three-cold MP4s share
`67d3c2f82975402eb7780d31949e3623074ecfedc8d61a618ccb8bf16f586d35`.
Frame 10 is now identical in all six 70-frame runs, with pixel (487,262)
RGB [25,33,37] and PNG SHA-256
`198ed28cbc3ff0238bb83cab729d88bec46ddbe886441fda00400470e665d8e2`.

The empirical script is `experiments/film-production/revalidate-fixed-viewer.mjs`.
Raw reports are under Leonardo's `videos/demo-incremental-rendering-fixed/`
and `videos/demo-incremental-source-grid-fixed/`, each at
`_build/evidence/fixed-viewer-revalidation.json`. Root inspected both encoded
contact sheets and the full-resolution source frame, and independently probed
the 70-frame MP4. Readable source, measured words, model, joins and endings
remain present. Model source, kinematics, export and original 46-second film
hashes are unchanged. No paid speech, source-model workaround, forced repaint
or tolerance relaxation was used.

Root accepts the paired implementation for closure in these branches. These
are measured local improvements, not a cross-hardware speed or universal
reproducibility promise. The conservative initial-mount dependency and the
explicit page/font mutation-test coverage limit remain. No main integration,
push, publication or human aesthetic/listening approval is implied.
