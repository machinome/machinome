# Implementation evidence

## Authority and scope

The first cycle of the React stage step of the declarative-python campaign,
on branch `one-runner` (worktree `WTs/one-runner`), cut from `react-stage` at
`5dae43f`. Planning commit `82ba537`, made for the orchestrator's review
(task 0.2, not claimed here). Nothing was pushed or published; no network
request or paid request was made; no `.env` was read and the runs had no
speech key in their environment. `node_modules` is the campaign worktree's
install, reached through the worktree's symlink; nothing was installed.
Integration into `react-stage` is the pilot's.

Environment of every run: Linux, Node v24.11.1, vitest 5.0.3, Playwright's
Chromium 151.0.7922.34, `ffmpeg version 6.1.1-3ubuntu5`, `git version 2.43.0`,
DejaVu fonts from `/usr/share/fonts/truetype/dejavu/`.

## Base

`npm test` on the base source (`5dae43f`, `node --test --test-concurrency=1
test/*.test.mjs experiments/dark-source/emphasis.test.mjs`), before any
change: **209 tests, 208 pass, 1 fail, 348.5 s** (5 min 49 s).

The failure was not the known intermittent one: it was
`a movie document is refused before its takes, then checks, speaks, previews
and renders from them` (`test/movie-pipeline.test.mjs`), refused by preview's
picture proof with `Partial picture replay is not deterministic: wheel #0 at
1.00 s`. Run alone right after (`node --test test/movie-pipeline.test.mjs`),
the file passed, 3 of 3, 30.5 s. The known intermittent `every incremental
PNG equals a separately cold film across the first reused-shot gap` passed in
this run and in every run of this cycle. Both are recorded, not fixed; the
finding is in `workflow/warts.md` under "The test suite".

## Red

- `test/memo.test.mjs` before `test/support/memo.mjs` existed
  (`npx vitest run --project pure test/memo.test.mjs`): the file fails to
  load, `Cannot find module './support/memo.mjs'`, no tests.
- `test/browser-seam.test.mjs` before the seam (with `CHROMIUM_ARGS` already
  exported, a refactor the global setup needed, and the harness in place):
  3 of 3 fail. The shared stage could not be made
  (`renderer.assetServer is not a function` in `test/support/stage.mjs`), and
  `assetServer is not a function` in the asset server test. The second test,
  a session given no browser, failed on a defect of the test itself (the
  field `browser` it returned collided with the session's own `info.browser`,
  the version string); renamed `owner` before the seam was written. That test
  characterizes the command line's unchanged path and is green by design on
  the base code.
- The first run of the memo's tests after writing the module: 11 of 12 pass.
  The failure was the test's: removing the file it had just added restored a
  state already recorded, which the memo rightly reused. The test now removes
  a different file.

Each honesty test's specific failure, shown by a targeted mutation of
`test/support/memo.mjs`, each reverted at once (`--project pure`):

| mutation | failing tests |
|---|---|
| fingerprint hashes names and mtime, not bytes | `a modification time is not an input`; `an input changed while the step runs records nothing`; `a fingerprint is the content and names of files, never their times` |
| the verdict entry's check hash not verified | `a corrupted, truncated or forged entry is regenerated` |
| a failure is recorded | `a failure is never recorded, and fails again on the next run` |
| inputs not fingerprinted again after the body | `an input changed while the step runs records nothing` |
| the cold switch ignored | `the cold switch runs the step and leaves the memo untouched` |
| a memoized pass not labelled | `a pass is recorded once, then passed from the memo without running, with the same verdict twice` |
| artefact parts not hash-checked on reuse | `a damaged, partial or extended entry is regenerated whole` |
| an artefact entry without index accepted | `a damaged, partial or extended entry is regenerated whole` |
| the toolchain left out of the verdict key | `a changed input, a new or removed file, another toolchain or another test misses` |

The seam's, by targeted mutations of `src/render.mjs` (`--cold --project slow
test/browser-seam.test.mjs`), each reverted at once:

| mutation | result |
|---|---|
| the given browser ignored (a launch per session) | `two sessions on the shared browser ...`: `no Chromium launched` fails; and the file's launch guard fails: `A browser test launched its own Chromium (2 undeclared)` |
| the given browser closed after the session | `two sessions on the shared browser ...` fails |
| the given asset server ignored | `two sessions on the shared browser ...` fails (origin differs) |
| a second mount not refused | `the asset server serves one session at a time ...`: `Missing expected exception` |

The launch guard on a real file: `test/source-only-browser.test.mjs` with its
browser entry points taken from `src/render.mjs` instead of
`test/support/stage.mjs` (cold, reverted after): its 9 tests pass and the file
fails, `A browser test launched its own Chromium (11 undeclared)`. That is
what every browser test did under `node --test`: one Chromium per session.

## Green

The whole suite, cold, after the conversion (`npm test -- --cold`, memo
absent before and after): **23 files, 218 tests, 218 pass, 342.9 s**
(344 s wall). 218 = 203 converted tests (209, less the three
`node --test` parents that are now groups, less the three experiment tests)
+ 12 memo honesty tests + 3 seam tests. The pure project alone
(`npx vitest run --project pure`): 14 files, 122 tests, 1.0 s.

A run filling the memo (`npm test`): 218 pass, 357.3 s, 0 passed from the
memo, 218 run; 96 verdicts recorded (one per slow test) and three artefacts
(`review-fixture-film`, `render-picture-media`, `pictures-media-matrix`).

The artefact memo across a verdict miss: a comment appended to
`test/review-pack.test.mjs` (reverted after) made its 18 tests run again (0
from the memo) while the `review-fixture-film` entry was reused: no artefact
entry's inode change time moved and no new entry appeared.

Final, on the final content (after archive; only records changed since, none
of them an input):

- **Cold**: `npm test -- --cold`: 23 files, **218 pass, 340.3 s** (341 s wall),
  "0 passed from the memo, 218 run", no line "passed from the memo", and every
  file under `.test-memo/` byte-identical before and after (SHA-256 of all).
  The slow files: incremental-rendering 140.9 s, render 103.5 s,
  movie-pipeline 31.0 s, review-pack 28.6 s, source-only-browser 26.0 s,
  pictures 6.6 s, browser-seam 0.7 s, source-scenes 0.3 s, speech 0.02 s.
- **Warm**: `npm test`: 23 files, **218 pass, 4.85 s** (6 s wall),
  "Test memo: 96 passed from the memo, 122 run". Each memoized test printed
  `passed from the memo: <file> > <test>` in its stdout and carried the label
  in its task meta; the reporter listed them:

  - test/incremental-rendering.test.mjs > a local title edit recaptures its shot and incoming join, but reuses distant shots
  - test/incremental-rendering.test.mjs > a B-only lens edit does not turn a viewer refusal reason into a global pixel dependency
  - test/incremental-rendering.test.mjs > every incremental PNG equals a separately cold film across the first reused-shot gap
  - test/incremental-rendering.test.mjs > each join depends on its outgoing shot, while an ordinary cut does not > cut
  - test/incremental-rendering.test.mjs > each join depends on its outgoing shot, while an ordinary cut does not > fade
  - test/incremental-rendering.test.mjs > each join depends on its outgoing shot, while an ordinary cut does not > dissolve
  - test/incremental-rendering.test.mjs > each join depends on its outgoing shot, while an ordinary cut does not > wipe
  - test/incremental-rendering.test.mjs > each join depends on its outgoing shot, while an ordinary cut does not > slide
  - test/incremental-rendering.test.mjs > release-only and unused media changes keep PNGs; only a reached still recaptures
  - test/incremental-rendering.test.mjs > a shared clip extraction range can broaden without invalidating unchanged selected frames
  - test/incremental-rendering.test.mjs > fractional shot boundaries use the global output grid and invalidate shifted requests
  - test/incremental-rendering.test.mjs > common style, chrome, viewer, model, geometry, FPS and duration invalidate all units
  - test/incremental-rendering.test.mjs > a pre-resolved measured cue cannot hide its now-missing cached speech take
  - test/incremental-rendering.test.mjs > a verified measured take and alignment bind only the shots whose words can show
  - test/incremental-rendering.test.mjs > audio and external captions change the output but never buy speech or recapture plain PNGs
  - test/incremental-rendering.test.mjs > an index contradicting its bound media or measured inputs is not reused
  - test/incremental-rendering.test.mjs > only complete, dimensioned and byte-attested shot generations survive interruption or damage
  - test/incremental-rendering.test.mjs > assembly refuses duplicate or missing global output frames before encoding
  - test/incremental-rendering.test.mjs > a failed encode preserves the previous MP4 and manifest while completed shots remain reusable
  - test/incremental-rendering.test.mjs > an interrupted publication leaves a stale-hash manifest and a recoverable prior film
  - test/render.test.mjs > short mixed-layout film renders with a same-basename sidecar, not embedded subtitles
  - test/render.test.mjs > text animation preview proves measured/even words, title fade and source emphasis on a moving model
  - test/render.test.mjs > a still and clip reach real browser pixels at their authored geometry and timestamps
  - test/render.test.mjs > an arrow follows a moving part and a label rides a world point, reproducibly
  - test/render.test.mjs > a highlight is applied and restored by requested state, and preview proves both in pixels
  - test/render.test.mjs > field of view and up reach the viewer at API 28 and the picture proves the lens
  - test/render.test.mjs > below API 28 the page calls setView exactly as before, with camera and target only
  - test/render.test.mjs > eased camera moves and model time reach the viewer as frameAt poses them, on API 28 and API 27
  - test/render.test.mjs > a dissolve from a continued clip into a fading title keeps film chrome unblended
  - test/render.test.mjs > shots joined by every kind pass preview with each transition proved in pixels, and render reproducibly
  - test/render.test.mjs > an arrow that runs to the cut follows its part into the transition and is refused when it leaves
  - test/render.test.mjs > a ring encloses its moving part in the accent, and draws itself on clockwise from the top
  - test/render.test.mjs > an arrow fading in and a label fading out are proved as the blends their easing predicts
  - test/render.test.mjs > a drawn arrow keeps its words visible and reveals only the shaft toward its part
  - test/render.test.mjs > a ring whose part is not wholly on the stage, or that leaves the frame, is refused
  - test/render.test.mjs > an entrance lasting the whole cue ends at its exclusive boundary without a false full-mark proof
  - test/render.test.mjs > a fractional cue at a nonzero shot start is active at its authored start and absent at its end
  - test/movie-pipeline.test.mjs > a YAML episode keeps its take keys, captions, word timing and every frame
  - test/movie-pipeline.test.mjs > a movie document is refused before its takes, then checks, speaks, previews and renders from them
  - test/movie-pipeline.test.mjs > speech generates one take per chapter from the unresolved document, and only once
  - test/review-pack.test.mjs > standalone review is a manifest route, before episode/source/viewer resolution
  - test/review-pack.test.mjs > symlinked catalogue manifest owns and reuses a canonical pack without following escaping artifacts
  - test/review-pack.test.mjs > standalone legacy manifest refusal asks for rerender, not an episode or unknown command
  - test/review-pack.test.mjs > matching film yields exact decoded selected PNGs and actual display-order PTS
  - test/review-pack.test.mjs > tampered MP4, legacy plan and malformed plan refuse without loading frameAt
  - test/review-pack.test.mjs > internally incomplete or contradictory complete indexes regenerate instead of verifying reuse
  - test/review-pack.test.mjs > a real decode refuses manifest frame-count and dimension disagreement
  - test/review-pack.test.mjs > decoded metadata rejects missing/nonincreasing PTS, frame count or dimensions
  - test/review-pack.test.mjs > overview and event pages keep 93/96 bound, 24 cells, adjacent pairs, padding and long full labels
  - test/review-pack.test.mjs > a live MP4 or manifest replaced during decode refuses despite a stable snapshot > mp4
  - test/review-pack.test.mjs > a live MP4 or manifest replaced during decode refuses despite a stable snapshot > manifest
  - test/review-pack.test.mjs > verified reuse rechecks live inputs and every artifact path/hash; prior generations stay immutable
  - test/review-pack.test.mjs > a new manifest hash publishes a new generation without overwriting an old complete pack
  - test/review-pack.test.mjs > interruption and mid-attempt input drift never publish a complete new index; retry succeeds
  - test/review-pack.test.mjs > render writes a review-samples-v1 plan on a cold capture and on a full shot-cache hit
  - test/review-pack.test.mjs > a warm full shot-cache hit still records the resolved review plan
  - test/review-pack.test.mjs > automatic pack failure warns after a good film and standalone retry succeeds
  - test/review-pack.test.mjs > render CLI exits zero with a published film even when its automatic pack fails
  - test/source-only-browser.test.mjs > portable source-only page proves literal typing, measured mark, chrome and exact seek replay
  - test/source-only-browser.test.mjs > portable source-only overflow refuses with shot and exact frame time
  - test/source-only-browser.test.mjs > a first-shot source picture mounts at useful size and the next model returns visibly
  - test/source-only-browser.test.mjs > source-only browser check refuses an absent or displaced panel, not just overflowing text
  - test/source-only-browser.test.mjs > matching shifted source and hidden viewport do not launder the wrong picture rectangle
  - test/source-only-browser.test.mjs > a preview proof override to an outgoing model does not inherit incoming source layout
  - test/source-only-browser.test.mjs > portable preview separates hidden source lens pose from visible split projection
  - test/source-only-browser.test.mjs > the unchanged visible split still proves changed FOV/up by positive projection
  - test/source-only-browser.test.mjs > portable source/model joins in both directions obey the old four same-instant pixel rules
  - test/pictures.test.mjs > picture geometry fits, covers, holds and keeps zoom fixed point
  - test/pictures.test.mjs > clips choose the frame on screen from irregular presentation timestamps
  - test/pictures.test.mjs > picture cue structure is closed and format-gated without changing old frames
  - test/pictures.test.mjs > older production media maps are ignored without probing or changing old frames
  - test/pictures.test.mjs > loading project media probes real files, hashes and committed status; sizing refuses unallowed enlargement
  - test/pictures.test.mjs > media loader accepts three raster formats and an internal SVG paint reference
  - test/pictures.test.mjs > media loader refuses escape, wrong bytes, animated and scripted stills, and incomplete provenance
  - test/pictures.test.mjs > museum enlargement is explicit, stage is smaller, and render width rechecks it
  - test/pictures.test.mjs > a moving view is checked between valid keys, not only at its endpoints
  - test/pictures.test.mjs > a zoom that exposes a plate at its ending key is refused
  - test/pictures.test.mjs > clip probe normalizes first PTS, refuses undefined instants, interlace, pixels and rotation
  - test/pictures.test.mjs > real 30 fps PTS ticks give every frame of a four-second span once, including frame 134
  - test/pictures.test.mjs > sample-and-hold cadence counts dropped/repeated frames without including exclusive endpoint
  - test/pictures.test.mjs > a clip must cover the cue and outgoing transition continuation, even if it leaves
  - test/pictures.test.mjs > fractional picture boundaries and outgoing continuation preserve a still or advance a clip
  - test/pictures.test.mjs > extraction uses only source frames whose presentation instants precede the exclusive cue end
  - test/browser-seam.test.mjs > two sessions on the shared browser launch nothing, share one asset server and leave the browser open
  - test/browser-seam.test.mjs > a session given no browser launches exactly one Chromium and closes it, as the command line does
  - test/browser-seam.test.mjs > the asset server serves one session at a time and refuses a second by name
  - test/source-scenes.test.mjs > source excerpts match pinned Git bytes, with validated bounds and containment
  - test/source-scenes.test.mjs > typing follows local time, holds between cues, restores and escapes markup
  - test/source-scenes.test.mjs > v3 omits continuity fields and uses valid defaults without changing legacy requests
  - test/source-scenes.test.mjs > lossless wrapping preserves every sample and mixing retains sound from clip start
  - test/source-scenes.test.mjs > film stage has no narration caption element
  - test/speech.test.mjs > cached speech overflow is refused without deleting the generated segment
  - test/speech.test.mjs > cache-only rendering refuses missing speech instead of generating it
  - test/speech.test.mjs > corrupt cached speech is refused instead of silently regenerated
  - test/speech.test.mjs > word timing reads only the exact cached take and verifies its checksum without a key or network
  - test/speech.test.mjs > speech leaves its cached take and written captions when measured text differs from the take

Compared with the base: 348.5 s cold under `node --test` (one Chromium per
session) against 340.3 s cold under vitest (one Chromium per run); the slow
layers dominate both, and the launches saved (one per session, eleven in
`source-only-browser` alone; not counted for the whole suite) are a small
part of it. The gain is the warm run: 4.85 s while nothing a slow test reads changes.

## What was not done, and why

- The slow files stay at the top of `test/`; the move to `test/browser/` and
  `test/pipeline/` is a later cycle (design D1).
- The command-line tests (`movie-pipeline`'s `check`, `review-pack`'s
  `render`) spawn `bin/videomaker.mjs`, which launches its own Chromium, as
  the command line must; the launch guard counts only the test worker.
- No slow test renders a film only to use it as an input, so no rendered
  fixture film is in the artefact memo yet; the fixture export is a JSON file
  written per test in milliseconds, so "built once" costs nothing to leave.
- The architecture overview does not describe the test runner; unchanged.
- Baseline specs: no existing spec named `node --test` or the test command,
  so none was modified; the new `test-suite` spec was created by the archive.
