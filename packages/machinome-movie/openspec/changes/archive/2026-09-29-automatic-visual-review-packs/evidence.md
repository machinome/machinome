# Automatic visual review packs: red-phase evidence

## Origin and pre-change absence (task 1.1)

Leonardo's archived `demo-all-features` film is 46 seconds / 1,380 encoded
H.264 frames at 30 fps, 1920 × 1080, with AAC and external SRT. The archived
[`film-motion` report](../../../../workflow/archive/film-motion-2026-09-29/report.md)
and `workflow/archive/film-motion-2026-09-29/evidence.json` record a manual
review of 92 half-second indices (`0, 15, …, 1365`), exact spoken pairs
`479/480`, `509/510`, `558/559`, source-emphasis/clear pairs `693/694`,
`711/712`, `730/731`, `784/785`, and head/join/tail indices `0`, `129`,
`279`, `396`, `402`, `408`, `639`, `1239`, `1379`. Its four overview JPEGs
and three event PNG sheets were hand-made from decoded final-film frames;
they are **not** outputs of the proposed pack generator. Four blank cells
on its last overview sheet were padding, not black film frames. The archived
sampled inspection did not claim a complete watch or audio judgement.

Read-only pre-change SHA-256 of the preserved project MP4 was
`c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e`,
equal to its existing manifest's `outputSha256`. That manifest's bytes hash
`ebd88c977c39f19bdc62c1f4737f6d6f731a9192511a8fce1c02d1c8f1b5c75d`;
its top-level keys have `count`, `fps`, `output` and `outputSha256`, but no
`reviewSamples`, `reviewPlan` or pack index. Current `src/render.mjs` builds
and publishes the manifest without a review plan or post-publication pack
attempt. Current `bin/videomaker.mjs` accepts only check/speech/preview/render/build.
The direct pre-change command
`node bin/videomaker.mjs review <that manifest>` exited 1 with
`Unknown command: review`. These are observations of absent behavior, not
individual red executions of the later pure-plan and decoder assertions.

## Test chronology

Before any renderer, CLI, timeline or pack implementation edit, the first
pure run (`node --test --test-concurrency=1 test/review-samples.test.mjs`)
reported **1 pass / 4 fail**. The passing control pins exact pre-change
`frameAt` JSON and shot-cache-key digests for 0.2, 0.3, default model-only
0.4 and default split-source 0.4. All four failures stopped at the *same*
absent `src/review-samples.mjs` module/function check. Their detailed
fractional/identity/fade/end assertions were written before implementation
but **did not yet execute**; they are not four independent behavior failures.

The first focused render red produced a real four-frame, two-shot MP4 at
`/tmp/videomaker-review-pack-LaxrcK/_build/review.mp4` and a published
manifest but failed `cold.reviewSamples?.schema === 'review-samples-v1'`
with actual `undefined`. A separate warm run at
`/tmp/videomaker-review-pack-NJXSym/` captured four frames once, then reused
all four (`cache.reusedFrames === 4`, `framesChecked === 0`) and failed the
same plan assertion. These are direct behavioral reds, not missing-module
proxies. Both fixture roots were retained by `KEEP_VIDEOMAKER_TEST=1`.

A distinct render at `/tmp/videomaker-review-pack-74o9aU/` published a
hash-valid MP4/manifest while the would-be review-pack directory was
unwritable, but emitted no `review pack failed; film published` warning:
the current renderer never attempted a pack. Its standalone retry assertion
was not reached. A valid tiny manifest/MP4 fixture at
`/tmp/videomaker-review-pack-nrQrkl/` gave CLI status 1 and
`Unknown command: review` instead of generating a pack; a legacy-plan
fixture at `/tmp/videomaker-review-pack-cL364j/` gave that same unknown-command
error instead of a rerender instruction. These are independently executable
CLI/publication reds.

The first combined pre-code run of the two new test files was **1 pass /
17 fail** in 6.72 s. Beyond the direct reds above, pack decode, hash/race,
reuse, and page tests stopped on absent `src/review-pack.mjs` exports; no
individual decoder, tamper, pagination, or publication-order behavior is
claimed red from those blocked assertions. The test-owned FFmpeg fixture has
a genuinely nonzero first encoded video PTS, integer tick `32768` at time
base `1/16384`, independently probed before product changes. This prevents
an `n/fps` label from passing the later actual-PTS test by coincidence.

After root's pre-code review, I strengthened (not yet executed behind the
missing pack module) exact display-order `frame=pts` assertions and an
independent eight-frame raw RGB byte count, one-frame null-PTS refusal,
all-frame count/dimension refusal, same-description authored-identity and
same-frame word-ordinal cases, a long cue with a distinctive unsafe visible
text marker, and an actual hash-matching `../../outside.png` bait file for
the reuse path. The decode-replacement test now registers child completion
immediately, limits the wrapper's wait, and releases/reaps only its owned
detached process group in `finally`. On the old CLI, both replacement
branches exited promptly at `Unknown command: review`; the decode gate was
never reached, so no mid-decode refusal is claimed red.

The first CLI film-success attempt used a test fixture with uppercase shot
IDs, and the second had a sub-two-frame transition. Those two failures were
**fixture setup errors**, not product reds. Once made valid, the focused
`render --silent` CLI run exited 0, printed its good MP4 path, and published
`/tmp/videomaker-review-pack-48be3L/_build/silent-preview.mp4` (SHA-256
`3df78fe6a258e80b3d0d2d8ea3697d93daaa52cc9c0c6be3c49e73de68a70d1b`)
and `silent-preview-manifest.json` (bytes SHA-256
`08f2692855e7d1e3be8baffce36846ac3e5cd81d3ed0780c8debcd268aa64942`).
The test then failed specifically because stderr lacked `review pack failed;
film published`. The standalone retry assertion was not reached. This is a
second direct failure-path red, at the actual command exit boundary.

The final pre-code combined run after these test corrections was **24 total,
1 pass / 23 fail** in 9.51 s (`KEEP_VIDEOMAKER_TEST=1 node --test
--test-concurrency=1 test/review-samples.test.mjs test/review-pack.test.mjs`).
The lone pass remains the unchanged request/key compatibility control.
Directly exercised reds are the absent `review` command, absent cold/warm
manifest plan, and absent pack-failure warning after direct and CLI film
success. The other failures are shared missing-module/CLI blockers, not
individual behavioral proofs. Every fixture from this run was retained
under its unique `/tmp/videomaker-review-pack-*` root; no product module,
renderer, CLI, or encoded-film tolerance had been edited.

## Proposed implementation seams at red handoff

The pure `buildReviewSamplePlan(e, units, fps)` seam consumes the existing
global output-shot units, returns `review-samples-v1` with `frameCount`,
`fps`, and deduplicated `{indices, labels}` samples, and must leave unit
frame JSON and shot keys untouched. Labels retain `shotId`, authored cue
`authoredIndex`, `wordOrdinal` where applicable, `side`/`sides`, full
description, and the explicit `resolved candidate, not reviewed` qualifier;
kind values exercised by tests are join, word-onset,
source-emphasis-onset/clear, picture-entry, shot-end, film-end,
transition-midpoint and transition-last-active. The incoming join keeps its
logical outgoing shot ID even when a fade selects only one picture side.

The standalone `reviewManifest(manifestPath, {beforeReuse?,beforePublish?})`
seam owns a manifest-relative generation. The two optional hooks are
test-only race injections, not author/CLI/manifest options. Tests also use
internal `validateDecodedFrames` and `planReviewPages` seams. The proposed
`review-pack-v1` index has explicit `generated, not reviewed` status,
manifest/MP4 SHA-256 inputs, film count/dimensions/fps, exact selected
`{index,ptsTicks,timeBase,file,sha256}` entries, and page entries with
bounded cells, full labels, padding and artifact SHA-256. The index is
published after images; exact fields may be refined during implementation
only if these tested provenance and page contracts remain true.

## Implementation and green chronology

The source-only planner first reached **4/7** pure tests: the pinned old
request/key control, fade-side selection and filmed ends passed. Two
prewritten test fixtures were then corrected, without backdating their red
history: a continuity case had expected a B onset during an outgoing-only
fade, so its identity case now uses a dissolve; a “two words on one frame”
case had written onsets `.3,.31` though the sampled local time was `.3`, so
the valid increasing onsets now lie at `.26,.27`. Two simultaneously cleared
source words are represented by one authored-cue clear label with both
word ordinals/descriptors in its `words` list. After those corrections the
initial seven pure tests passed.

Root's subsequent adversarial checks found five genuine planner defects.
Focused assertions ran red before each correction: back-to-back dissolves
were merged into one transition run; fadeIn/fadeOut interiors were missing;
an emphasis clear after a cut carried its old incoming rather than selected
outgoing side; a frame-zero reveal omitted its valid single-frame onset;
and a coarse FPS override let a fade-delayed first incoming picture appear
as two new word onsets instead of picture-entry state. The focused pure
planner ended **12/12 green** while retaining exact old request/key pins.

The first encoded-film implementation passed its initial four focused
standalone/decode/metadata/page checks and then **17/17** pack tests. Root's
review found an internally contradictory but hash-matching complete index
could be reused, and a malformed v1 plan with no film end could publish an
overview-only pack. New targeted tests ran red before the reuse/plan
validators were strengthened. They now reject empty/missing/duplicate
selected frames, omitted event pages, wrong film dimensions, altered full
cell labels, unsafe/null PTS, missing film end, unknown event kind and missing
candidate qualifier. Reuse compares the exact selected set and deterministic
page/cell/label layout against the stored plan, checks image dimensions and
hashes, and checks live manifest/MP4 bytes again before reporting success.
The final live rehash on a new generation is immediately after artifact
verification and before the atomic complete index.

This implementation uses its own deterministic RGB PNG encoder and small
fixed bitmap glyphs for sheets, not an FFmpeg filter with authored text.
Full selected PNGs are exact RGB values from the MP4 decoder; the sheets are
bounded navigation thumbnails, with complete labels in JSON. Root viewed a
retained tiny sheet at
`/tmp/videomaker-review-pack-b7RmAW/review-packs/a98828b389f4-cea3b70fb457-e5f5d048-e6a5-4f58-bb94-35bb786c5cbc/events-001.png`
and found the fixed labels, adjacency and explicit padding inspectable; that
tiny synthetic sheet is not the required real Leonardo film review. The
decoder identity records actual `ffmpeg` and `ffprobe` version lines. The
pack probes every display-frame PTS and dimensions, then streams all RGB
frames from a stable MP4 snapshot while retaining only selected images:
these are **two decoder operations**, not a claim of a literal one-pass
decoder. Attempt snapshots are removed before index publication (and on
failure); incomplete image generations have no complete index.

The combined focused new-test run finished **30/30 green** in 26.47 s. The
full scoped `npm test` finished **188/188 green**, 0 failures, in 328.84 s,
with serial browser execution. After that full run, root identified a test
fidelity issue: the 9-frame manifest count case still held the old 8-frame
film-end pair and failed plan validation before decoding. The test now uses
a valid 9-frame plan ending at index 8, resets to a valid 8-frame plan for
the dimension case, and requires the exact decoder count/dimension refusal
messages. Its focused rerun passed **1/1**; no runtime code changed after
the full scoped run. Root separately ran the new `review` command against
the original archived 46-second Leonardo legacy manifest: it refused with
the compatible-plan/rerender message, and the original MP4 SHA-256
`c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e`
and manifest SHA-256
`ebd88c977c39f19bdc62c1f4737f6d6f731a9192511a8fce1c02d1c8f1b5c75d`
remained unchanged. This green legacy refusal is later than, and does not
replace, the pre-implementation `Unknown command: review` red.

The real Leonardo consumer's encoded-frame, sheet and root visual-inspection
gate in task 3.1 is root/empirical-owned; synthetic tests and sheets are not
human review or visual approval of that film.

## Post-empirical catalogue-symlink correction

After the first real-film empirical run passed and released its lease, root
identified a standalone deployment-path bug: the normal project catalogue
can be a directory symlink, while pack artifact verification compared a
resolved artifact path against a lexical generation path. An owned eight-frame
manifest/MP4 regression accessed through a directory symlink ran **0/1 red**
before this correction, failing `Generated review artifact hash differs:
frames/000000.png` at `src/review-pack.mjs:397`. Its later reuse and
escape-symlink assertions did not execute in that red run.

The narrow correction resolves the manifest, MP4 and pack directory to real
paths before binding input provenance or checking artifact containment. The
same test then passed **1/1**: alias generation, direct-path, alias-path and
standalone CLI reuse all point to one complete generation with canonical
manifest provenance. It also placed a hash-matching
PNG outside that generation and replaced an indexed frame with a symlink to
it; this was refused as a reuse hit and caused a fresh generation. Both
review-pack test files then passed **31/31** in 30.49 s after the CLI
assertion was added. This targeted
post-full-suite correction does not rewrite the prior **188/188** full-suite
result or the first empirical proof. Root will pin the changed source and
rerun the exact real-film proof before final closure.

## Leonardo encoded-film proof and root review (task 3.1)

The real consumer was the existing root-authored Leonardo
`videos/demo-source-only/episode.yaml`, project HEAD
`28b43bce1b88446995f0ff231dd9075d1a839ab3`. Its episode SHA-256 was
`37989962da303a91b72c0ae9590edb2964ea87762b37bdd3235d6181ccf28766`,
production SHA-256
`fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3`,
export manifest SHA-256
`92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9`,
and Viewer API 28 bundle SHA-256
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.
The verified source-shot take and alignment were copied into each fresh ignored
build to resolve word timing; the two films were rendered **silent**. No paid
speech, episode/model/export rewrite, old film overwrite or 46-second-film
rerender occurred.

Two separate empirical generations remain preserved. The first, before the
catalogue-symlink correction, passed all actual-path encoded-frame and sheet
checks at
`/mnt/data/machinome-projects/Leonardo/videos/demo-source-only/_build/evidence/review-pack-2026-09-29T19-48-10-006Z-d381d8ba-8ded-4d85-a58e-c295909ac257/report.json`
(report SHA-256
`7e3fac2e71e43b39e37628a9ddc614a81b8e375498f6fecb0be271e7f3be813d`).
It was **not** retroactively called an alias-path pass. The second, after the
narrow symlink fix and focused **31/31** tests, repeated the full proof in a
new root and additionally invoked the actual standalone CLI through the
workspace catalogue alias. Final report:
`/mnt/data/machinome-projects/Leonardo/videos/demo-source-only/_build/evidence/review-pack-2026-09-29T19-55-57-828Z-0542d869-2bad-40fc-ac3c-1a73d684d106/report.json`,
SHA-256
`a4210851ee87a6c82d9bf3002327aef12db8ef8c02588de202388bc182f81fc9`.
The final harness SHA-256 was
`efcffc49a83923e933beca480a58837a751893134b0524143a5cddf4d5b6373b`;
it pinned Videomaker HEAD `9dbdded50d701d6e73e8ed636beddabcf1d49846`,
the complete 16-file `src/` tree SHA-256
`217b6099c2d9ae3091d577db6809c74caaffdd07d2b80f93cee10accc0e7a527`
(sorted paths relative to `src/`, path NUL bytes NUL), CLI SHA-256
`18513454760f8ce4f5b42a399b7cae5a1d133f12cd1f16676d224f60fa69aaa1`,
and lockfile SHA-256
`c83093ba053bf5e92d480b4e3c947fb83e3a9c54904f88a81a21a7c22da59d15`.

In that final single supervised run, the cold film captured **70/70** frames
in 19.841 s and the warm film reused **70/70** frames in 3.360 s. Both
encoded MP4s matched each other and the already accepted source-only film
byte-for-byte at SHA-256
`7e2585c3a4d5dcda9014f7bb1fdfee8fe787c64b244319c885fe795cf7dddd7d`.
Those times are render-wall observations for these two arms; they are **not**
an isolated speedup or standalone-review/decode runtime claim. The final
manifest / pack-index SHA-256 pairs were:

| Arm | Manifest | Pack index |
| --- | --- | --- |
| Cold automatic | `e67b58c543553ed23da309d7a0e591908911992e922523f14ef8580520a00385` | `b1ba794e1ac9d63147a78fa687f1af25c46ef55a003f5ca6986c3821011e1267` |
| Warm automatic | `5937eb72be58b2a474f0984e1a39e13e160e25dd094e1fceca3b659f57a4aff5` | `36ee1e8e9a5273948977efbb62368d786d5420d0ae22e72ce4e5ca30e8226eb6` |
| Fresh owned standalone copy | `5984fd0db268c383776d0a1cca247b669b48c0bc8ac1d3d16a8e0392fdb3cd98` | `727e294c289403f1c77f95783cf580412d42a751c7737ca2b60d5f244ec6197e` |

Each manifest contained the same **20-sample** resolved `review-samples-v1`
plan. The empirical harness asserted Leonardo's independently measured global
frame pairs: joins `11/12`, `46/47`, `56/57`; source picture-entry `13/14`,
word/emphasis edges `14/15`, `20/21`, `25/26`, `26/27`, source clear `40/41`;
continuation picture-entry `48/49` and word edges `49/50`, `51/52`; transition
midpoint/last-active singles `13`/`15` and `48`/`50`; four shot ends and film
end `68/69`. It also refused a false first-word onset while a fade selected
the other picture and a false cue event from active-to-outgoing role transfer.
These are **resolved candidate** labels; a coloured plate or wipe may still
hide content perceptually.

The harness independently decoded each complete 70-frame H.264 MP4 in
display order, probed actual frame PTS ticks/time base and dimensions, and
compared all **32 selected full-resolution RGB PNGs per pack** against the
published MP4. It checked every page rectangle, short visible/full JSON
label, actual-PTS text, pair adjacency, event retention, end sample,
artifact hash and explicit padding. Each pack had one overview sheet with
15 actual cells and 9 padding cells plus two event sheets with 24 and 12
actual cells. Independent nearest-neighbour reconstruction of each sheet's
480×270 thumbnail area matched the decoded MP4 exactly, not merely the
standalone extracted PNG. The three final cold sheets live beside its index
under the final root at
`fresh-cold-and-warm/review-packs/e67b58c54355-7e2585c3a4d5-509b7e84-b2d9-48d2-ac13-d13be930aca5/`
as `overview-000.png`, `events-001.png`, `events-002.png`; native selected
frames such as `frames/000027.png` and `frames/000041.png` sit there too.
Every index says `generated, not reviewed`.

The owned standalone copy deliberately replaced embedded episode, source,
export and build paths with absent locations; the CLI succeeded from its
stored plan and bound MP4. Invoking that **same** manifest via
`/home/asa/devel/machinome/projects/Leonardo/` returned `verified reuse` of
the exact same complete generation and created no additional pack. Its
36-file generation-tree SHA-256
`0ca0cf4b5dc9ab97873ab58a678080678d1d7081fb5cc461c6b69a58c2bf5860`
was unchanged; the final cold pack's 36-file tree SHA-256
`44fb0423d54fcd245c565141f8f9ad7b27d975819c5889ad9c8cf882e78546cd`
also survived warm and standalone review unchanged. Earlier source-only
films, the original 46-second MP4 and the first successful report were
preserved. Replacement/tamper and mid-attempt drift refusals are covered by
the focused tests above; this real-film proof did not mutate a published
input merely to repeat that fault matrix.

Root independently rehashed all three final MP4/manifest/index bindings,
**96 selected PNGs** and **9 sheets**, independently decoded and probed the
published 70-frame film, and compared all **153 sheet thumbnail cells**
(19,828,800 pixels) by direct indexing. Root viewed all three cold sheets
and native frames 27 and 41, checking source highlights/clear, joins, model
return and padding; the cold sheet and selected-frame hashes matched the
first, already visually inspected actual-path pack. Root also independently
reran the catalogue-alias standalone CLI: exit 0, same verified-reuse
generation, no new render or decode. This is root's sampled AI **visual** inspection
of a silent film, not human review, an audio watch, rights decision, aesthetic/pilot
approval, or release authorization. Root owns final spec sync, archive and
commit.
