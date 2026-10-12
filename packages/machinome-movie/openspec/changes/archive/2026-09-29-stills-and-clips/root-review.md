# Independent consumer and film review — 29 September 2026

Status: accepted for sync and archival after consumer checks, fresh browser
preview, encoded-film visual review, complete tests and legacy comparison.
Codex is the pilot's delegated reviewer and video
operator. This records agent review, not rights clearance or publication.

## Real consumer and media

Leonardo `videos/demo-stills-and-clips/` is an untracked, four-shot, sixteen-second
episode using only the project's own reconstruction media. It pins the existing
1460-second export at `28b43bce1b88446995f0ff231dd9075d1a839ab3` and changes no
mechanics. Generated output belongs to the episode's ignored `_build/`.

The episode pans/zooms an own render in the stage; holds another render across
the frame then returns to the still-running model; displays a copied carpentry
SVG with a viewBox and film-readable line weights/dashes added to the copy;
and inserts a model-stage crop of the graphic-overlay
demonstration from a half-second in-point. The final view key is at 3.2 seconds,
leaving a brief held destination before the fade/cut. Narration fields describe
the shots, but this feature demo buys no speech and will be rendered silently.

| Media | SHA-256 |
| --- | --- |
| `mates-isometric.png`, 1200×900 | `42be08dab08feca8037428a7d44136b913bcd9888725d864e8b85c09a48ee386` |
| `repair-isometric.png`, 1200×900 | `33d7decead124dfdee84820f4a1381474eb5929c3293412810ca25cd812a97b8` |
| copied `beam-drawing.svg`, viewBox 0 0 420 240 | `a50d3774c639f678c8ca3ed3a97823199e58916af5afebe660f2af4404677911` |
| `overlay-detail.mp4`, 864×340, H.264, 30 fps, 15 seconds | `8f9d91654f4cd304e4323aded85f4170fb65113f4d2ef85cf5838d931cab843d` |

The SVG is a copy of `export/hydraulic_sawmill-frame/carpentry/B1-iso.svg`.
The clip is an H.264 crop (`crop=864:340:48:86`, CRF 18, yuv420p) of the completed
15-second graphic-overlays demonstration; its source SHA is recorded in that
cycle's root review. Cropping removes the baked-in film masthead and titles,
so the containing episode owns those elements. None of these media is tracked
at project HEAD. Credits and rights are written in production and description,
not drawn over the film.

## Root data-level checks

The real episode passes `check` with the pinned API-28 source-worktree bundle.
Root then cloned its loaded production data in memory, leaving the authored
files untouched, and called the same loading/sizing validation for three
negative cases. All refused as expected:

- Without the `isometric` allowance: `Still isometric would be enlarged
  1.13× in shot still-view (1200×900 source pixels in the 1728×680.4 stage
  area); its upscale allowance is 1.`
- Substituting the tracked, ffprobe-confirmed 640×360
  `screenshots/hydraulic_sawmill.png`, without keyed zoom or allowance:
  `Still isometric would be enlarged 1.89× in shot still-view (640×360 source
  pixels in the 1728×680.4 stage area); its upscale allowance is 1.`
- Checking the original episode at render width 3840:
  `Still isometric would be enlarged 2.27× in shot still-view (1200×900 source
  pixels in the 3456×1360.8 stage area); its upscale allowance is 1.25.`

Each refusal also explains how to allow enlargement, choose the stage area or
use a larger source. The explicit production allowances are author choices,
not claims that scaling adds detail.

## Early adversarial findings

Root identified these cases in the initial media implementation and sent them
for regressions before fixes: quoted/whitespace internal SVG `url(#...)`
references were incorrectly treated as external by regex backtracking; CSS
`animation-name` and `transition-property` escaped the shorthand-only scan;
nonzero initial clip timestamps were refused instead of normalized to the
first frame; and the extraction-end epsilon cancelled the frame-selection
epsilon, including a frame at an exclusive cue end. The implementation
agent reports all four fixed with the expanded Node matrix; final full-suite
and real-film evidence remain the closure gate.

## Combined-film diagnostic findings

The first real clip preview exposed a timestamp precision error: reading
FFprobe's six-decimal timestamp strings made the 30 fps source in a 30 fps
film skip and repeat 40 frames over the 120-frame cue, ending at frame 133
instead of 134. Integer presentation ticks with the rational stream time
base select frames 15 through 134 with zero drops/repeats. A separate
fractional-cue regression ensures cadence reports use the actual global
film-frame grid, not a grid starting at the cue's in-point.

Root also found that a still and clip with the same legal name received the
still's credit twice. The regression failed before credits were resolved by
kind. These are reporting/correctness fixes, not new authoring fields.

The first 46-second combined-film preview reached its closing dissolve and
failed its existing two-level pixel proof at 41.30 seconds. Its retained
`transition-closing-{outgoing,incoming,composed}.png` captures isolate the
problem: body pixels (y=40 through 519) differ by at most 0.5, the progress
rule by zero, but 1726 header channels differ by more than two, with a maximum
44.5. At (120,24), red is 173 in the picture-bearing outgoing capture and 84
in both incoming and composed captures. The clip itself continued and blended
correctly; picture-active chrome had a compositor/stacking mismatch. The
implementation agent is fixing both leaving-picture and entering-picture
transitions; the tolerance is not being widened. A targeted real rerun now
reports a maximum 0.5 for the body and whole image, and zero for chrome.
The viewer keeps posing beneath an opaque picture, but its covered viewport
is hidden to avoid changing text rasterization. An entering-picture synthetic
join separately failed at 201 because the transition's z-index covered the
chrome; the scoped stacking correction makes both directions pass. The
complete independent preview and encoded-film review remain pending.

Root inspected the initial combined preview's actual stills: both moving
rings/labels stayed on their parts; the title remained separate from the
model; full-frame imagery left the masthead legible. The copied SVG's original
0.35-unit lines were too faint at film size. Its geometry was preserved while
the copy gained 1.2-unit visible strokes and 0.8-unit hidden strokes with
3/2 dashes; the next preview is clear. Both descriptions disclose this
presentation edit and the original project export remains unchanged.

## Independent feature film and pixels

Root's fresh final-media preview at width 960 passes: 31 samples, 94 poses,
four picture checks and thirteen same-instant fade comparisons. Visible
replay is exact in all four shots, and partial-opacity replay is exact at
0.2, 8.2 and 12.2 seconds. The clip samples select source frames 15, 21, 27
and 134. Its extraction span is 15–134, key
`3f223d847e3309bf829c24f3828a328a11041599be7ad9100eb02f6fe6f046bc`.

Root rendered `videos/demo-stills-and-clips/_build/silent-preview.mp4`:
16.000 seconds, 960×540, 30 fps, 480 H.264 frames and no audio stream.
SHA-256: `6312b7750f3a74047c118c8112c1627ee57d074d76a8ff8d7203a2f850bf43f1`.
Frame identity: `89da2e21500629f1fef38258f35736bb242c4d992460bbbe1b07ee56163e231c`.
The manifest records source revision `28b43bc`, parent workflow HEAD
`9aea9f2` plus the actual worktree renderer hashes, and the pinned API-28
bundle named in the campaign. The implementation was not committed during
this render; the workflow HEAD alone is not its content identity.

Vision review used decoded MP4 frames, not only preview PNGs: 32 exact
half-second frames (indices 0,15,…,465) in two `review-sequence-*.jpg`
sheets; before/at-cut pairs 179/180, 239/240 and 359/360 in
`review-boundaries.png`; and frames 6,112,246,353,366,479 in
`review-fades-and-last.png`. The approach grows steadily and holds before
leaving; the full-frame still cuts back to the continuing live model at
6.0 seconds; the SVG linework is readable; the inserted mechanism moves with
its ring cues and finishes on the expected source view. Fade midpoints show
both same-instant images. Masthead and progress remain visible; no credits
are drawn. This is a silent feature demonstration, not an audio review.

At this rehearsal width the raster peaks are 0.567× (stage still), 0.6×
(frame still) and 1× (clip), under the recorded 1.25/1.25/2 allowances.
The SVG has no raster allowance. Cadence is 30→30 fps, zero dropped and zero
repeated. `releaseReady` is false: public URLs remain null and all four
shown media files are uncommitted at project HEAD. The four corresponding
`pictureReleaseIssues` are expected, not silently cleared by this review.

Root also independently rechecked the formerly failing combined-film
dissolve at native 1920×1080: at 41.30 s its unmasked maximum difference
is 0.5, and seeking to 29.5 s and back reproduces the image exactly (six
poses, API 28). This proves the real regression at final output size before
the combined film is mastered; it does not substitute for its final review.

## Compatibility and closure

The final serial suite passes 116/116 tests, with the added browser assertions
passing separately before that run: gradient decoding within one source
pixel, 3 fps into 2 fps clip sampling, exact return at an exclusive mid-shot
end, chrome above frame pictures, overlay layering, extraction-file reuse
and replacement identity. The original full-matrix-before-code task order
was not wholly followed; root explicitly accepts the honestly recorded
sequencing exception in `evidence.md`, not a retroactive all-red-first claim.

Root freshly regenerated all three compatibility previews with the same
API-28 bundle: `demo-legacy-02` has 3/3 matching PNGs,
`demo-annotate-a-part` 6/6 and `demo-feed-mechanism` 26/26. All 35 hashes
match the detached `6417f97` baseline byte for byte. The 0.2 and feed demos
also pass `check`. Unchanged historic `hydraulic-sawmill` still refuses
`Model duration differs from production settings; recheck the exported
simulation`, and `machinome-revolutions` still refuses `Pin
model.sourceRevision to the export source-revision.txt before rendering`.
Neither historic episode was repaired or treated as a compatibility fixture.

The ten added requirements are supported by the implementation, tests and
this real film. Sync and archive are accepted under the pilot's delegation.
This is local completion on `film-motion`, not integration into `main`,
pilot visual approval, rights clearance, a release, or publication.
