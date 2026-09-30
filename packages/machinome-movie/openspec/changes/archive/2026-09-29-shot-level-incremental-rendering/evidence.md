# Shot-level incremental rendering evidence

## Baseline and first behavioral red

Root's project-owned [`demo-incremental-rendering` baseline](/home/asa/devel/machinome/projects/Leonardo/videos/demo-incremental-rendering/evidence.md) records the real-sawmill 80-frame silent film at 960 × 540 / 10 fps: 31.67 s cold, 1.70 s unchanged with 80 old-cache hits, then 32.11 s and all 80 recaptured after only the `feed-pawls` title changed. Only frame pixels 21–42 changed. The project record pins the Videomaker/tool/project/viewer/export hashes and preserves both films and old frame directories; `demo-all-features` remained untouched. These are observations of the old renderer, not expected new timings.

Before editing renderer runtime, `test/incremental-rendering.test.mjs` rendered a four-shot synthetic film cold, unchanged, then with only B's title changed. The existing whole-episode cache used the same directory on the unchanged rerun, then a new directory containing **16 newly captured PNGs for all 16 output frames** after the B edit. The rerun of the red test deliberately asserted capture behavior first and failed `edited.framesChecked: 16 !== 8`: only B and the incoming-transition shot C should be captured; A and D are unrelated. This is a behavioral red, not a missing import or report field. Command: `node --test test/incremental-rendering.test.mjs`; exit 1, one failed test, 5.06 s. The old edited cache directories in the test run were `78717656b6de4211` (cold/warm) and `ff6940d2b72535eb` (edited) under its temporary fixture. The temporary fixture was removed by the test; its diagnostic and failure are retained in the run output.

An earlier draft of the same test also failed on absent `cache.reusedFrames` after logging the old 16-frame recapture. The stronger `framesChecked` assertion was moved before it and rerun, as requested by root; no runtime code changed between the two red runs.

## Focused defect reds and test chronology

The behavioral red above preceded runtime implementation. The broader matrix
was expanded while implementation progressed; those added assertions were
green on first execution unless a focused defect red is named below. The
following are actual subsequent red-to-green observations, not a claim that
every final assertion existed before implementation:

- A B-only field-of-view edit initially recaptured all 16 frames instead of
  B plus C's incoming wipe (8). `requiredViewerApi.reasons` and its minimum
  requirement were in the common key even though the mounted viewer remained
  API 28. Removing this refusal text from visual common inputs made the
  focused test pass at 8 captures, with A and D reused.
- A pre-resolved measured spoken cue with its take removed initially rendered
  successfully (`Missing expected rejection`). Re-reading the exact verified
  cached take at render entry restored the existing missing-take refusal;
  rendering never generated speech.
- Moving a verified word onset within one filmed frame (.50 to .55 seconds)
  initially left B's key unchanged, contrary to the alignment dependency.
  Binding the resolved per-shot word-timing digest as well as the WAV checksum
  changed B's key and recaptured its whole generation.
- Rewriting B's generation index with contradictory measured metadata initially
  still reused it (four B frames). Verification now compares index media and
  measured records, plus origin common/shot keys, with the freshly derived
  unit. The focused rerun recaptured B and reused A/C/D.

The matrix added green coverage for cut/fade/dissolve/wipe/slide dependency,
unused still and clip declarations/bytes, reached still and clip bytes,
shared-clip extraction-range independence, fractional global-grid assignment,
common-input invalidation, even reveal versus audio/SRT-only changes, complete
generation integrity, legacy-cache non-import, duplicate/hole refusal, encode
failure and interrupted publication. It also compares all 16 incremental PNG
SHA-256 values with a separate cold render across the first cached-to-captured
gap, using moving-model pixels, source typing in both A and B, animated title
and word overlays, and an incoming wipe; the MP4 checksums match. A second
fractional-grid 32-frame cold comparison also matches every PNG. The first
fractional test draft expected C to miss after moving A/B's boundary. Inspection
showed C's outgoing B payload sequence was identical, so the test expectation
was corrected to C reuse and now explicitly asserts C's unchanged key and
outgoing payload; this was test-design correction, not a product defect.

## Integrity, publication and final local validation

The new `shot-v1` namespace leaves legacy frames untouched. A completed
generation has an index published last, with exact global indices/times,
dimensions and per-PNG SHA-256. The focused matrix damaged a PNG, removed a
PNG, replaced the index with `null`, inserted a null frame row, removed
provenance, substituted a correctly re-hashed wrong-size PNG, and left a
partial generation without an index. Each bad B generation missed and was
recaptured whole while A/C/D reused; a stray regular file in the generation
parent did not hide a healthy candidate. A failed encode retained the old MP4
and manifest and its completed shots were reusable afterward. A deliberately
interrupted sidecar publication left the previous manifest's MP4 hash visibly
stale and the prior good MP4 at `<label>.mp4.previous-<id>`; a successful
publication removed its temporary recovery link. The public probe filename
names the published MP4, not its former pending path.

`node --test --test-concurrency=1 --test-reporter=spec test/*.test.mjs` passed
**133/133** with no failures in **217.12 s**. The test file was loaded before
two last media-locality assertions were added; a subsequent focused run of
`node --test --test-concurrency=1 --test-name-pattern='release-only and unused media|a shared clip extraction range' test/incremental-rendering.test.mjs`
passed **2/2** in **13.61 s**, specifically including unused clip bytes and
changed reached clip source bytes. No runtime code changed after the serial
suite. Exact cold/incremental equality and cache integrity checks remained
literal; no pixel tolerance or refusal was weakened.

Coverage limit: the common-key code binds `film.html`/`film.js` stage hashes
and the known regular/bold film and mono font files with SHA-256. The tests
assert those four font records and behaviorally change viewer/model/style,
series, width, FPS and duration, but do not mutate a repository film page or
a machine-installed font during a browser test. This is inspected key coverage,
not a claimed page/font mutation red. The conservative mounted-first-frame
dependency remains, so this change does not promise minimum invalidation for
edits to the initial request or universal font fallback coverage.

## Real-film integration proof

The initial 80-frame proof passed; the initial 70-frame proof exposed a
viewer fresh-load ordering defect and was held, never waived. After the
separate viewer correction, Sol's new matrices pass all 80 incremental/cold
PNG comparisons and all 70 against each of three cold mounts. Root independently
verified the files, generation origins and encoded review images. The exact
timings, artifact paths, hashes, viewer commit and bounded acceptance are in
`root-review.md`. The script `experiments/film-production/revalidate-fixed-viewer.mjs`
refuses changed pinned runtime/viewer/model inputs and pre-existing output
episode names, preserving both earlier failures and later successful evidence.
