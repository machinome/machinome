# Independent consumer and film review — 29 September 2026

Codex acted as the pilot's delegated adversarial reviewer and video operator.
This is agent review, not pilot approval of taste or publication. The Leonardo
episode sources remain untracked; generated media stay in ignored `_build/`.
The model and export were not changed.

## Real consumer and narrated film

`videos/demo-text-animation/` contains two eight-second shots: a title and
even/spoken overlays, then typed source with three spoken identifiers. The
source excerpt is lines 413–415 of export-pinned revision
`28b43bce1b88446995f0ff231dd9075d1a839ab3`. The exact two cached takes, hashes
and measured onsets are recorded in `evidence.md`.

After reframing the first shot, root reran `check` and `preview` with the
API-28 viewer bundle at viewer commit `f040f45`, SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
Preview passed: 23 retained stills, 37 poses, two reveal checks, five
same-instant title comparisons, one five-sample emphasis check, and exact
pixel replay. Both reveals reported 1, 2, 3 visible words; source marks
accumulated and cleared as requested.

Root rendered with `render --width 960 --fps 30`, without `--silent`, reading
the existing cache and purchasing no further speech. Result:

- Video: `videos/demo-text-animation/_build/rehearsal.mp4` in Leonardo.
- H.264, 960 × 540, 30 fps, 480 frames, 16 seconds; one AAC audio stream,
  also 16 seconds.
- SHA-256: `74fc594461fed3ada615a0775b8fa98af4ecf7c9c643c89dac28564ef17fd58b`.
- Render identity: `1a7d134814ae9c7b1a4c2e416fe7d7688e6bab4572f58de2511ee74ca8b7ec21`.
- `releaseReady: false`; no publication or external release is implied.

Root decoded and visually inspected 32 overview frames at half-second cadence
(`review-sequence-01.jpg`, `review-sequence-02.jpg`) and exact before/after
frame pairs (`review-spoken-onsets.png`, `review-source-onsets.png`). Frame
numbers below are zero-based and refer to the actual encoded film:

| Event | Measured global onset | First drawn frame | Before/after inspected |
| --- | ---: | ---: | --- |
| Propose. | 3 s | 90 | 89 / 90 |
| Inspect. | 4 s | 120 | 119 / 120 |
| Correct. | 5.63 s | 169 | 168 / 169 |
| waterwheel | 10.133 s | 304 | 303 / 304 |
| drives | 10.72 s | 322 | 321 / 322 |
| crankshaft | 11.347 s | 341 | 340 / 341 |
| clear source emphasis | 13.14 s | 395 | 394 / 395 |

Each pair shows the expected one-word change; the final pair clears all three
marks. Timing is checked against the recorded take's alignment and the
manifest's unaltered audio offsets (3 s and 10 s), not estimated reading speed.
The spoken words keep their positions; the even lower line builds steadily.
The code stays readable on the light palette, and its teal tint/underline
distinguishes emphasis without replacing syntax colouring or source text.
The wheel and crank remain visible in the source view; other tall mechanism
members are deliberately cropped. No creator, copyright, licence or URL is
drawn on the film.

## Findings and resolutions

- The first title subtitle was lost over dark model geometry. Root changed
  only the authored camera, placing the whole model below the title. The
  retained `review-title-before.png` and fresh preview show the correction.
  The subtitle is now legible, with no covering card or new product interface.
- Exact one-frame-early onsets, decreasing alignment end times, pronunciation
  replacements before emphasized identifiers, and astral characters before
  source ranges gained regressions and fixes.
- The real source onset at global 10.133 s exposed subtraction rounding;
  scoped boundary settling preserves the exclusive clear boundary.
- Effective output fps is checked, including silent build. Several words
  may legitimately arrive together; only an unfilmed word is refused.
- Preview now counts actual computed-visible spans and retains successful
  text proof stills. Wrong counts, overflow and missing-cache commands are
  exercised, not inferred from timeline values alone.
- Caption files and cached takes survive a measured-phrase refusal.

The final implementation suite passes 98/98; later additional Node assertions
pass 18/18 without source changes. No tolerance was widened. The main browser
test was added after implementation rather than red-first. Root explicitly
accepts this recorded process exception under the pilot's delegation; it is
not presented as an executed red-first test sequence.

## Compatibility and closure

With the same API-28 bundle at width 960, fresh previews match detached
pre-overlay `6417f97` byte-for-byte: 3/3 format-0.2 `demo-legacy-02` images,
6/6 `demo-annotate-a-part` images and 26/26 `demo-feed-mechanism` images.
The root checked the latter 32 directly after this cycle's render. Earlier
keyframe, transition and graphic-overlay demos also pass `check` without
speech. The historic sawmill still refuses its 296-versus-1460 duration pin;
historic Revolutions still refuses its missing source revision. Neither was
changed to conceal those pre-existing failures.

The video, tests, compatibility evidence and explicit process exception meet
the delegated closure gate. Root syncs the new text-animation capability and
archives this cycle. Covering cards, pronunciation dictionaries, adoption by
Revolutions, publication, pushing and main-branch integration remain outside
this work.
