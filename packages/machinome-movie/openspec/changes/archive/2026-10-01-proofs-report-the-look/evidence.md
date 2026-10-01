# Implementation evidence

## Authority and scope

Cycle 6 of Videomaker's addition-warts campaign, warts 2 and 4 of
*Addition*, on branch `proofs-report-the-look` (worktree
`WTs/proofs-report-the-look`), cut from `addition-warts` at `500ebca`. The
planning commit is `db96d98`. Nothing was pushed or published; no network
or paid request was made; nothing was installed. No schema, contract page,
Python source or viewer source was changed. The viewer was reached only
through the API 29 bundle selected by path
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` of the
workspace), never written into the repository. Nothing was written in the
Curta project or its shared `_build/` (see "The film"). Integration into
`addition-warts` is the orchestrator's.

Environment: Linux, Node v24, vitest 5, Playwright's Chromium (SwiftShader),
Python 3.12 from the workspace venv. Other agents ran suites in other
worktrees at the same time; durations are not comparable across runs.

## Red

Each red was run cold (`VIDEOMAKER_TEST_COLD=1`) before the code it proves.

### The highlight's images (layer 5, `test/browser/render.test.mjs`)

     × a highlight is applied and restored by requested state, and preview proves both in pixels 1451ms
     FAIL  |slow| test/browser/render.test.mjs > a highlight is applied and restored by requested state, and preview proves both in pixels
    AssertionError: Expected values to be strictly deep-equal:
    + actual - expected

      [
    +   undefined,
    +   undefined,
    +   undefined
    -   [
    -     'pawl'
    -   ],
    -   [
    -     [
    -       'Feed',
    -       'Pawl'
    -     ]
    -   ],
    -   {
    -     "difference": "highlights/pawls-highlight-0-pawl-difference.png",
    -     "lit": "highlights/pawls-highlight-0-pawl-lit.png",
    -     "unlit": "highlights/pawls-highlight-0-pawl-unlit.png",
    -   },

The highlight check carried no parts, paths or images; the captures were
dropped.

### The text the probe measures (layer 5, `test/browser/layout.test.mjs`)

     × the probe measures each shot's code size and title lines, and a narrowed headline wraps 1226ms
     FAIL  |slow| test/browser/layout.test.mjs > the probe measures each shot's code size and title lines, and a narrowed headline wraps
    TypeError: Cannot read properties of undefined (reading 'map')
     ❯ shape test/browser/layout.test.mjs:65:26

`measureLayouts` returned no `text`.

### `check`'s lines (layer 8, `test/pipeline/movie-pipeline.test.mjs`)

Run with `src/`, `stage/` and `bin/` stashed back to the planning commit
(the tests at their new content; restored afterwards, byte for byte), the
narrowed headline:

     × check reports a headline that wraps in its lines, measured in its one Chromium, and refuses nothing 2085ms
    AssertionError: The input did not match the regular expression /^Shot question: title opening\.title in headline on 1 line, its subtitle on 4 lines$/m. Input:

    'Tour: 3 chapters, 9 shots, 18.9s; model 20s\n' +
      …
      'Layout playbill at 1280×720: stage 870.4×576 at 64,86.4; plate 870.4×576 at 64,86.4; aside 243.2×288 at 972.8,216; headline sized by what it holds\n' +
      …
      'Reframe into question: opening.wide from playbill stage 870.4×576 at 64,86.4 to playbill-split right 563.2×489.6 at 652.8,158.4\n' +

`check` said the headline was sized by what it holds, and nothing of the
four lines the subtitle wrapped to. With the layer 5 code in place and the
command not yet changed, the tour's two tests failed at
`Source excerpt is not loaded: declaration` (the command passed no
excerpts), and the clocked fixture's:

    AssertionError: The input did not match the regular expression /^Text not measured: check measures a movie's stage only when it shows a picture or comes in by a reframe; read the sizes and the lines on preview's stills$/m. Input:

    'Count: 1 chapters, 3 shots, 11.4s; model 8s\n' +

### The manual pins (layer 9, `test/repository.test.mjs`)

Written after the pages; shown red with `README.md`, `docs/FORMAT.md`,
`docs/stage.md`, `docs/adrs/README.md` and `CHANGELOG.md` stashed back to
the planning commit, then restored:

     × the manual and the records say where a highlight landed and what check measured of the text (proofs-report-the-look) 19ms
    AssertionError: README: the highlight images
          Tests  1 failed | 8 passed (9)

### Layer 6

`test/viewer/real-viewer.test.mjs` gained its assertions after the code; it
was not run red. It was run green with the bundle (`✓ the tour is checked,
previewed and rendered with the real viewer 137197ms`, then again in the
whole suite).

## Green

The changed files cold, after the change: `layout.test.mjs` 2 passed;
`render.test.mjs` the highlight test passed; `movie-pipeline.test.mjs`
the three changed tests passed (178 s); the real-viewer tour test passed.

### The Node suite, whole, cold, with the bundle

`VIDEOMAKER_VIEWER_BUNDLE=<the API 29 bundle> VIDEOMAKER_TEST_COLD=1 npm test`
on the final content (after D4a and the archive):

     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 146683ms
     ✓ |viewer| test/viewer/take.test.mjs (5 tests) 18576ms
     Test Files  40 passed (40)
          Tests  390 passed (390)
       Duration  864.89s (tests 98%, import 1%)
    Test memo: 0 passed from the memo, 390 run

### The Python suite

    286 passed in 18.33s

`openspec validate --specs --strict`: 16 passed, 0 failed.

## The film

The Curta project's head moved while this cycle ran: at 09:22:35 the
pilot's commit `f2ad951` ("Rename Curta models to posed, mechanistic and
event-driven") rewrote `simulation/clocked.py`, which the film's
`_build/movie.json` (evaluated at 03:15) pins at `c214704` for its three
excerpts. `check` of the film in place, at 09:25:06, refused before
anything this change touches, in the words `loadMovie` would use too:

    Source differs from pinned model revision: simulation/clocked.py

Re-evaluating and re-exporting the film is project work and would write in
the shared `_build/` and `export/`. So the proofs ran on a copy: the
project cloned into the scratchpad at the film's commit `23c9e6f` (where
`simulation/clocked.py` equals `c214704`'s), with copies of the untracked
`export/clocked_curta/` and of `_build/movie.json`, `_build/audio/` and
`_build/audio-manifest.json`. Nothing in the project or its `_build/` was
written, restored or deleted.

### `check`, 09:26:04 to 09:26:06, exit 0

    Layout curta at 1920×1080: stage 1766.4×928.8 at 76.8,97.2; headline sized by what it holds; aside 345.6×324 at 1420.8,626.4
    Layout curta-split at 1920×1080: left 902.4×648 at 96,302.4; right 825.6×928.8 at 1017.6,97.2
    Reframe into inputs: machinome.curta from curta stage 1766.4×928.8 at 76.8,97.2 to curta-split right 825.6×928.8 at 1017.6,97.2
    Shot question: title question.problem in headline on 1 line, its subtitle on 1 line
    Shot inputs: source machinome.drivers in left at 17.3 px (0.90 vw)
    Shot turn: source machinome.instruction in left at 17.3 px (0.90 vw)
    Shot commit: source machinome.relation in left at 17.3 px (0.90 vw)
    Shot result: title closing.answer in headline on 1 line

At `23c9e6f` the film had already been tuned by looking ("the code
legible", 0.90 vw where the wart saw 0.82 vw, the headline on one line);
the lines now say so without a render.

### `preview`, first run, 09:26:13 to 09:35:32, exit 0 (as planned, D4)

Every ghosted or dimmed highlight's difference marked the whole machine:

    Highlight add-23 cues[0].actions[0] lights main_drive/stepped_drum: 59865 pixels changed within 232×417 at 372,50; see preview/highlights/add-23-cue0-action0-stepped_drum-difference.png
    Highlight add-23 cues[1].actions[0] lights main_drive/stepped_drum, transmission/result/ones/p_10219_410002_1, transmission/result/tens/p_10230_410008_1_419229: 58795 pixels changed within 232×416 at 372,51; see preview/highlights/add-23-cue1-action0-stepped_drum+p_10219_410002_1+p_10230_410008_1_419229-difference.png

The drum alone and the drum with the pinions were indistinguishable, which
is the finding the change exists for. This is the implementation evidence
for design D4a.

### `preview`, after D4a, 09:37:04 to 09:45:48, exit 0

    Highlight set-23 cues[0].actions[0] lights input_selectors/selectors: 19917 pixels changed within 278×297 at 271,171; see preview/highlights/set-23-cue0-action0-selectors-difference.png
    Highlight set-23 cues[1].actions[0] lights input_selectors/selectors/digit_selector_axle_1/selector_knob_1_419057: 2240 pixels changed within 31×87 at 512,262; see preview/highlights/set-23-cue1-action0-selector_knob_1_419057-difference.png
    Highlight add-23 cues[0].actions[0] lights main_drive/stepped_drum: 1167 pixels changed within 94×277 at 434,137; see preview/highlights/add-23-cue0-action0-stepped_drum-difference.png
    Highlight add-23 cues[1].actions[0] lights main_drive/stepped_drum, transmission/result/ones/p_10219_410002_1, transmission/result/tens/p_10230_410008_1_419229: 1490 pixels changed within 94×125 at 434,293; see preview/highlights/add-23-cue1-action0-stepped_drum+p_10219_410002_1+p_10230_410008_1_419229-difference.png
    Highlight add-145 cues[1].actions[0] lights carry_mechanism/result_carries/results_tens_lever_assembly_1, carry_mechanism/result_carries/results_tens_lever_assembly_2: 1952 pixels changed within 50×89 at 485,218; see preview/highlights/add-145-cue1-action0-results_tens_lever_assembly_1+results_tens_lever_assembly_2-difference.png

(eleven lines; the `keep` highlights' figures are unchanged between the two
runs, e.g. `set-23 cues[1]` 2240 pixels within 31×87 both times). The
pinion highlight's entry in `preview/report.json`, listed under
`main_drive/stepped_drum`, `transmission/result/ones/p_10219_410002_1` and
`transmission/result/tens/p_10230_410008_1_419229`:

    {"shotId": "add-23", "cue": "cues[1].actions[0]", "element": "first.inside", "time": 31.849999999999998,
     "paths": [["main_drive","stepped_drum"], ["transmission","result","ones","p_10219_410002_1"],
               ["transmission","result","tens","p_10230_410008_1_419229"]],
     "lit": "highlights/add-23-cue1-action0-stepped_drum+p_10219_410002_1+p_10230_410008_1_419229-lit.png",
     "unlit": "highlights/…-unlit.png", "partsLit": "highlights/…-parts-lit.png", "difference": "highlights/…-difference.png",
     "changedPixels": 1490, "changedBox": [434, 293, 94, 125]}

`preview/highlights/` holds 39 images (eleven highlights, six of them
ghosted or dimmed). Looked at: the pinion difference marks, in red, the
visible pixels of the drum and the input pinions in the lower middle of the
machine, below the result register; the lit frame shows them tinted through
the ghosted case. The index has fifteen part names.

## Findings

1. **The difference of a dimmed or ghosted highlight marks the whole
   model** (the first film run above). Resolved in this change by D4a: one
   more review pose with the rest kept. Recorded here because it changed the
   planned design during implementation; the orchestrator may overturn it.
2. **With the rest kept, the named parts are partly hidden by the parts in
   front of them**, so the difference marks only their visible pixels (the
   drum's 1167 pixels of a much larger part). It says where the parts are on
   screen, not their whole extent; the film's ghosted lit frame shows them
   whole. Recorded, no fix.
3. **`check` measures text only when it measures the layout** (a picture or
   a reframe). A movie document without either, such as the clocked fixture
   `count`, gets `Text not measured`. The contract says such a document
   opens no browser (`docs/movie-document.md`, "The stage": "A document
   that shows no picture opens no browser at `check`"; `movie-document`
   spec, "No picture, no browser"). Smallest correction, if a film needs
   it: let the probe run when a document shows a source panel or a title,
   and amend that sentence and scenario.
4. **The contract page lists what the shipped elements report** ("a source
   panel its displayed text, its lit tokens, its cursor and whether the
   excerpt fits its box; a title the box of its text and its revealed
   count", "The stage"). Smallest correction, not made since the page is
   the orchestrator's: "a source panel its displayed text, its lit tokens,
   its cursor, whether the excerpt fits its box and the font size of its
   code (`fontSize`); a title the box of
   its text, its revealed count and the lines its text and subtitle wrap
   to (`lines`, `subtitleLines`)". `docs/stage.md` says it.
5. **The Curta film cannot be checked at the project's head**: `f2ad951`
   rewrote `simulation/clocked.py`, the film pins `c214704`, and its
   README's export directory (`export/event_driven_curta`) is not the one
   the document reads (`export/clocked_curta`). The film needs evaluating
   and exporting again; project work, the pilot's.
6. **The probe measures a shot's text without its other elements.** A
   template whose title slot takes its width from a sibling (a flex row
   beside a view) would be measured in a width the film does not give it.
   Neither fixture nor film does that; design D6 states the premise.

## What was not done, and why

- No refusal, threshold or expected region, by the brief and the
  orchestrator's cut (design, "Alternatives rejected").
- The encoded film's review pack is unchanged: its images come from the
  MP4, which has no unlit frame.
- No text measurement for YAML episodes or for movie documents `check`
  opens no browser for (finding 3).
- `docs/movie-document.md` and the schema were not touched (finding 4).
- The film was not re-rendered, re-evaluated or re-exported, and nothing in
  the project was written (finding 5); the proofs ran on a scratch copy at
  the film's commit. The copy's preview was run twice, the second after
  D4a; the shared `_build/` was never touched.
- Layer 6 was not shown red (its assertions were written after the code).
