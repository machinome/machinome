# Implementation evidence

## Authority and scope

Cycle 5 of Videomaker's addition-warts campaign
(`workflow/ongoing/addition-warts-campaign/plan.md`), finding 3 of
`workflow/warts.md`, "Addition (Curta, 1 October 2026)", cut by the
orchestrator as a `check` report line, not a refusal. Branch
`check-the-continuation` (worktree `WTs/check-the-continuation`), cut from
`addition-warts` at `500ebca`. The planning commit is `e1e2574`. Nothing
was pushed or published; no network or paid request was made; nothing was
installed. The schema is unchanged; `docs/movie-document.md` gained the
resolved shot's `model.crossing` in "Resolution", rule 7, as the brief
allowed ("the sentence appears … in the resolved document where the
shot's model time is recorded"). The viewer was reached only through the
bundle selected by path in the environment
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` of the
workspace, Viewer API 29), never written into the repository. The Curta
project was read (its `_build/movie.json`, its cached narration, its Git
history) and nothing was written in it. Integration into `addition-warts`
is the orchestrator's.

Environment: Linux, Node v24, vitest, Playwright's Chromium, Python 3.12
from the workspace venv. Other agents ran their cycles' suites in other
worktrees at the same time; durations are not comparable across runs.

## Red

Every red below was run before the code it proves was written.

### Layer 3 (`test/take.test.mjs`), before `src/movie.mjs` changed

    × the counter's nine runs past the mark nine into step-3 during its dissolve, and its resolved model records it
    × the take time a crossing records is the one the join's last frame poses for the outgoing view
    ✓ a shot held at the mark, or eased to rest on it, crosses nothing
    ✓ a step boundary that is not a mark is not reported
    × a shot that ends before a mark and runs past it crosses it; a fade follows only its first half
    × a step is named by its input and where it moves it; crossings are reported in film order
    ✓ a continuation that would leave the take is still refused with its words, and reports nothing
     Test Files  1 failed (1)
          Tests  4 failed | 20 passed (24)
    Test memo: 0 passed from the memo, 24 run

The assertions, verbatim:

    AssertionError: Expected values to be strictly deep-equal:
    + actual - expected
    + undefined
    - {
    -   duration: 0.5,
    -   into: 'carry',
    -   join: 'dissolve',
    -   mark: 'nine',
    -   past: 0.7619047619047628,
    -   reaches: 6.761904761904763,
    -   report: 'Continuation: shot nine runs on through the 0.5 s dissolve into shot carry and crosses the mark nine: its last frame there poses take time 6.76 s, 0.76 s past the mark, inside step-3, which moves crank by 360; hold the shot at the mark before it ends, or ease its model to rest there',
    -   step: 'step-3'
    - }

    TypeError: Cannot read properties of undefined (reading 'reaches')
     ❯ test/take.test.mjs:265:56

    AssertionError: Expected values to be strictly deep-equal:   (nine ending at 5.5 s)
    -   mark: 'nine',
    -   past: 0.16666666666666785,
    -   reaches: 6.166666666666668,
        report: undefined,
    -   step: 'step-3'

    AssertionError: Expected values to be strictly deep-equal:
    + []
    - [
    -   'once',
    -   'nine'
    - ]

The three that passed before the change are its guards: a hold, a step
boundary that is not a mark, and the refusal past the take's end, which
must stay as they are. After the red, the second test was strengthened to
compare the outgoing view's bank with the rule on every frame of the join
(five at 10 fps), not only the last.

### Layer 2 (`test/movie-document.test.mjs`), the pin written by hand first

`fixtures/resolved/count.json` gained, by hand, `crossing` on `nine`'s
`model`; on the old resolver:

    × every registered document validates, passes its checks and resolves to its pin, twice identically, on the frame grid
    AssertionError: count resolution differs from fixtures/resolved/count.json
            model: {
    -             crossing: {
    -               duration: 0.5,
    -               into: 'carry',
    -               join: 'dissolve',
    -               mark: 'nine',
    …
     Test Files  1 failed (1)
          Tests  1 failed | 21 passed (22)

After the resolver changed, `node scripts/pin-resolved.mjs count minimal
tour` wrote `count.json` byte-identical to the hand-written pin (`cmp`
silent) and left `minimal.json` and `tour.json` unchanged (`git status`
lists only `count.json`). The pin's diff is one field on one shot:

    "model": {
      "from": 2,
      "to": 6,
    + "crossing": {
    +   "join": "dissolve", "duration": 0.5, "into": "carry", "mark": "nine",
    +   "step": "step-3", "reaches": 6.761904761904763, "past": 0.7619047619047628,
    +   "report": "Continuation: shot nine runs on through …"
    + }
    },

### Layer 8 (`test/pipeline/movie-pipeline.test.mjs`), cold, before the command printed it

`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow test/pipeline/movie-pipeline.test.mjs -t "clocked take count"`,
with the resolver already recording the crossing and `bin/videomaker.mjs`
unchanged:

    × the clocked take count is checked, previewed and rendered twice from the command line 982ms
    AssertionError: The input did not match the regular expression /^Take: .*\nContinuation: shot nine runs on through the 0\.5 s dissolve into shot carry and crosses the mark nine: its last frame there poses take time 6\.76 s, 0\.76 s past the mark, inside step-3, which moves crank by 360; hold the shot at the mark before it ends, or ease its model to rest there$/m. Input:
    'Count: 1 chapters, 3 shots, 11.4s; model 8s\n' +
      '  counting: take 10.84 s, chapter 11.40 s, tail 0.36 s\n' +
      'Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark\n' +
      'Viewer API 29 required for clocked take, highlight (shot carry); /tmp/videomaker-movie-ONLwyP/viewer-double.js declares API 29\n' +
      …
     Test Files  1 failed (1)
          Tests  1 failed | 13 skipped (14)
    Test memo: 0 passed from the memo, 1 run

Green after `bin/videomaker.mjs` printed each crossing's report, cold:

    ✓ the clocked take count is checked, previewed and rendered twice from the command line 28058ms
     Test Files  1 passed (1)
          Tests  1 passed | 13 skipped (14)
    Test memo: 0 passed from the memo, 1 run

## Suites on the final content

The Node suite whole, `npm test` with `VIDEOMAKER_VIEWER_BUNDLE` naming the
workspace's Viewer API 29 bundle, on the final content (the records aside),
every slow test cold since `src/movie.mjs` reaches them all:

     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 151084ms
     ✓ |viewer| test/viewer/take.test.mjs (5 tests) 22090ms
     Test Files  40 passed (40)
          Tests  395 passed (395)
       Duration  904.56s (tests 98%, import 1%, transform 1%)
    Test memo: 0 passed from the memo, 395 run

The Python suite whole, from the worktree's `python/`:

    286 passed in 14.87s

## The Curta case

The film's evaluated document, `videos/addition/_build/movie.json` of the
Curta project (written 03:15 on 1 October, the document the film was
rendered from, with `read-23` and `read-168` held at their marks), read by
a scratch script (`scratchpad/…/curta.mjs`, outside both repositories)
that resolves it with this worktree's `resolveMovie` against the film's
cached narration (`cachedTake`, read only) and prints what `check` prints
after its chapter lines. `read-23`'s model was then set, in memory, to what
the project's commit `1567439` declared before the hold,
`Take.run(5.2, "added_23")`, which evaluates to `{"from": 5.2, "to":
{"mark": "added_23"}}` (the diff of `23c9e6f` shows the hold replacing
exactly that). Nothing was written in the project: `git status` of its
`videos/` was the same before and after, and `_build/movie-resolved.json`
kept its 08:47 time.

`read-23` as it was before the hold:

    Continuation: shot read-23 runs on through the 0.6 s dissolve into shot set-145 and crosses the mark added_23: its last frame there poses take time 9.74 s, 0.74 s past the mark, inside step-4, which moves digit_1 to 5; hold the shot at the mark before it ends, or ease its model to rest there

`digit_1` is the units slide (the take's own comment); the line names the
shot, the join, the mark, how far past it, and the step into which the
dissolve ran it: the units slide moving to 5. With `read-168` reverted too,
the existing refusal speaks first, unchanged:

    refused: Shot read-168 cannot continue 0.8 s into the dissolve to shot whole: its model would reach 19.15 s, past the export's 18.75 s; end its model earlier or shorten the transition

The film as rendered, with its holds, is reported with two crossings
nobody had seen:

    Take: 7 steps, marks rest 0 s, units_3 1.5 s, set_23 3 s, added_23 9 s, units_5 10.25 s, tens_4 11.5 s, set_145 12.75 s, added_145 18.75 s, 18.75 s long; the replay of its steps gives the recorded bank at every mark
    Continuation: shot set-23 runs on through the 0.5 s dissolve into shot add-23 and crosses the mark set_23: its last frame there poses take time 3.35 s, 0.35 s past the mark, inside step-3, which moves crank_rotation by 360; hold the shot at the mark before it ends, or ease its model to rest there
    Continuation: shot set-145 runs on through the 0.5 s dissolve into shot add-145 and crosses the mark set_145: its last frame there poses take time 12.98 s, 0.23 s past the mark, inside step-7, which moves crank_rotation by 360; hold the shot at the mark before it ends, or ease its model to rest there

## The manual's two spellings

The two `Turns.keys` spellings `docs/declaring-a-movie.md` gives for
stopping `nine` at its mark were declared on the fixture project and
evaluated by a scratch script (nothing written), giving:

    held {"keys": [{"at": 0, "seconds": {"mark": "one"}}, {"at": {"spoken": "bring it"}, "seconds": {"mark": "nine"}}, {"at": {"spoken": "On the tenth turn"}, "seconds": {"mark": "nine"}}]}
    eased {"keys": [{"at": 0, "seconds": {"mark": "one"}}, {"at": {"spoken": "On the tenth turn"}, "seconds": {"mark": "nine"}, "ease": "out"}]}

Their resolved shapes are the ones layer 3's "held at the mark, or eased to
rest on it" resolves, crossing nothing.

## Findings

1. **The Curta film still runs two shots past their marks.** `set-23`
   ends on `set_23` still moving (its last key segment 1.5 → 3 s) and its
   0.5 s dissolve into `add-23` turns the crank 0.35 s into the first
   stroke (about 21° of 360°); `set-145` ends on `set_145` and runs 0.23 s
   into the second stroke (about 14°). The incoming shots start on the
   same marks and move slowly, so during each dissolve two crank angles are
   blended. Whether that reads as a fault is the film's author's to judge;
   `check` now says it. Film work, not this change's.
2. **The take block does not name a trigger's instruction.** A step made
   by `Trigger("Turn crank")` is recorded with what the framework returned,
   `input` and `by`, so the report names it `step-3, which moves
   crank_rotation by 360`, not "Turn crank". The contract ("The take")
   lists the step's fields and has no instruction field; the smallest
   correction, if a film wants the name, is an optional `instruction` on a
   trigger's step, written by evaluation. Not forked here.
3. **"Its dissolve" is the next shot's.** The finding says `read_23` ran
   on "during its dissolve"; `read_23`'s own `Dissolve(0.5)` is how it
   comes in, and the join it ran past `added_23` in is `set_145`'s
   incoming 0.6 s dissolve (a join belongs to the incoming shot). The
   report names the join it measured and the shot it leads into.
4. **A shot's take time may run backward.** Neither runtime refuses
   `from > to` on a take's shot (only model keys must not run back); a
   continuation of such a shot runs back through the marks behind it and
   is not reported. No film writes one; recorded, not built.
5. **The past-the-end refusal and the report measure differently**, by
   decision (D2): the refusal keeps the abstract reach `end + endRate ×
   joinShows(join)`, conservative for what the viewer is asked; the report
   takes the take time posed on the join's last frame, what is drawn. A
   continuation can be refused for an instant no frame poses; that was so
   before this change and is unchanged.

## What was not done, and why

- **No refusal**, by the campaign's cut: a crossing is reported and
  `check` passes.
- **No Python change.** Evaluation does not know a shot's length (it comes
  from measured speech), so it cannot know where a continuation runs; the
  shared documents and both suites' fixture checks are unchanged.
- **`src/timeline.mjs` and `src/take.mjs` unchanged**, though the brief
  named them as where the rules live: both are in the shot cache's common
  key, and editing either would recapture every shot of every film (the
  Curta's 3 787 frames, about an hour) for a report that changes no
  picture (D5). The join's extent is restated in `src/movie.mjs`, held to
  `frameAt` by layer 3.
- **Loops' marks are not followed** and **backward continuations are not
  reported** (finding 4): no film has asked.
- **The Curta film was not changed**, its `check` not run in place (it
  writes the film's `_build/`, shared with other agents, finding 16 of the
  campaign), and nothing re-rendered: the reproduction resolved the film's
  own document in memory.
- **`workflow/warts.md` untouched**; the findings above are for the
  orchestrator's triage.
