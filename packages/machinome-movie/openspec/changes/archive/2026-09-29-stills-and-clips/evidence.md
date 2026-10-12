# Stills-and-clips implementation evidence

## Preconditions

The 29 September 2026 delegated ratification in `design.md` still covers the
D1–D13 field shapes, full-area covering and stacking, fixed-point view mix,
enlargement allowances, sample-and-hold clip choice, media refusals and release
gate. Implementation begins on `film-motion` at
`9aea9f2` after the four prerequisite cycles were applied; text animation is
synced and archived. No project or production media are edited by the
implementation agent. The root owns the real demo, video, vision and archive.

The pre-change DOM order was annotations, overlays, source, transition. The
picture layer was placed after source. Conditional stacking puts pictures
below text overlays and transitions and keeps the masthead/progress above
both. The page still poses the model under the picture; while a picture is
fully opaque, it hides the covered viewport to prevent Chromium changing
the masthead's antialiasing. Pictures with partial opacity use same-instant
opaque/absent raster captures, preserving exact replay and fade boundaries.

## Red tests

The test order was not wholly the task list's ideal “all red before any
implementation”. The first `test/pictures.test.mjs` skeleton failed with
`ERR_MODULE_NOT_FOUND` before `src/pictures.mjs` existed. The pure module was
then started before the whole refusal/geometry matrix was added. Its expanded
matrix first failed for a missing `clipCadence` export; after the module was
filled in, a 10/12 run still failed the unwired episode validation and a test
fixture extraction setup. Three fixture corrections were made (allowance
metadata, SVG fixture inheritance, and a clip use); episode/timeline wiring
then made the matrix 12/12. Those later assertions were not retroactively
pre-implementation reds. The root accepts this sequencing exception for the
cycle, subject to complete final coverage.

The real-browser test was authored before `film.html`/`film.js` picture
implementation. Its first run was invalid because a 0.5 s fade at 2 fps is
only one frame; after correcting the fixture to 4 fps, the run failed at
`p.pictureChecks` undefined. The page/render implementation then made this
test green. Later browser assertions for pixel colours, extraction reuse,
manifest, credits and release issues were added after the first page work;
their actual red/green outcomes are recorded below, not claimed as an
initial browser red.

Specific regressions found and proved red before their fixes:

- SVG `href=https://…` without quotes escaped the conservative external
  reference scan. The refusal test failed, then the scanner accepted quoted
  or bare values for inspection; internal `url( #paint)` and
  `url("#paint")` remain accepted.
- The real 30 fps clip's six-decimal timestamp strings gave a 120-frame cue
  source span 15–133 with 40 dropped and 40 repeated frames. The new
  independent FFmpeg regression failed with exactly those numbers; using
  integer presentation ticks and rational `time_base` gives 15–134, 0/0.
- A fractional cue beginning at global 10.1 s in a 2 fps film reported source
  frames `[0,2]`, 2 dropped, instead of the actual global-grid sample `[2]`,
  3 dropped. The test failed, then cadence was moved to the film-frame grid.
- Two shown media entries both named `ramp`, one still and one clip, produced
  `ramp: Test gradient` twice in the description. The browser/render test
  failed, then credit lookup became kind-qualified.
- A synthetic entering-picture dissolve failed with largest channel
  difference 201 because the transition layer covered the masthead. A scoped
  z-index correction made the entering and leaving picture joins pass.

Two real-consumer diagnostic reds were also preserved in Leonardo's ignored
`_build/preview/` during implementation. The 16 s still demo's partial
picture at 0.2 s replayed with two channel values one level apart, and its
zero-opacity entrance screenshot differed from the absent picture. After
same-instant opaque/absent composition, that demo preview passed exact
partial-opacity replay at 0.2 s, 8.2 s and 12.2 s and all fade boundaries.
The 46 s combined demo failed the dissolve into `closing` at 41.30 s with
largest difference 44.5. Root's and the implementation agent's independent
pixel audit located all >2 differences in masthead rasterization; the body
blend was within 0.5 level. Hiding only the fully covered WebGL viewport
made an unmasked focused real-browser check at 41.30 s pass with largest
difference 0.5 and chrome difference 0. Root owns the fresh final preview.

## Green tests and consumer diagnostics

`node --test --test-concurrency=1 --test-reporter=spec`: **116 tests passed,
0 failed**, 105.2 s, after the final browser coverage additions. The focused
expanded browser case separately passed 1/1 in 27.5 s. This includes the
unchanged literal 0.2 and 0.3 frame
pins; the 0.4 comparisons were amended to include `picture: null` alongside
their existing `transition: null`. A synthetic H.264 clip with its own audio
and a VP9 WebM used distinguishable 16·n-luma frames: browser-selected
indices and fully opaque centre pixels matched extracted source PNGs at
3→4 and 3→2 frame-rate ratios. Extraction reuse kept the index and extracted
PNG modification times; replacing the clip changed its key and decoded pixel
identity. A short render encoded narration audio but no clip audio. Manifest
tests cover media hashes, extraction key/version, committed status, null
credit, same-named still/clip credits, missing description placeholder,
unresolved rights and uncommitted media. Width override refused enlargement
before opening a browser.

The gradient still's keyed centre, right-offset texel and interpolated fixed
point were checked within one source-colour unit. At the first contained view,
the masthead's pixels were exactly unchanged by the picture; at a zoomed view
the opaque progress rule was exactly unchanged. A top text overlay produced
visible pixels above the picture. A separate mid-shot picture cue ended at
`to` on a moving model: that frame equalled the same-instant plain model
exactly and differed from the forced full picture. The browser rejected a
shifted `#viewport` with the stage-geometry error. The preview's fade samples
and exact seek-away/back replay passed; the focused real closing transition
proof also passed unmasked at 1920×1080 with maximum difference 0.5.

The early real still-demo preview (before root's final SVG contrast edit)
passed with 4 picture checks, 26 sample stills, 80 poses and exact replay;
after the integer-PTS fix its clip sample ended at source frame 134 and
`check` printed 30→30 fps, 0 dropped/0 repeated. The SVG source then changed
under root ownership, so root will make the final feature preview and render.

The first broad browser chrome assertion, added after implementation, failed
because it compared antialiased glyph backgrounds even where the full-frame
image legitimately changed the background. It was narrowed to the contained
view's unchanged masthead background and the opaque progress rule, then the
focused test and full suite passed. This was a test correction, not a runtime
change. Runtime and test files are frozen for root consumer review.
