## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, `23 + 145`), the first film on
a clocked take. Finding 3 of `workflow/warts.md` ("Addition (Curta,
1 October 2026)"): **a shot's continuation through a join is refused only
when it leaves the take.** While a dissolve, a wipe, a slide or the first
half of a fade still shows the outgoing shot, that shot keeps moving: its
model time runs on past its end at the rate it ended with
(`modelSecondsAt` in `src/timeline.mjs`; the shot-transitions requirement
"The outgoing shot keeps moving while it is still seen"). `check` refuses a
continuation that would pass the take's last second and says nothing else.

The film's `read_23` was declared `Take.run(5.2, "added_23")`: it ended on
the mark `added_23`, the instant the crank finished its turn and the dials
read 23, still moving, and the 0.6 s dissolve into `set_145` ran its take
time on into the next step, the units slide moving to 5. Nothing said so;
the author found it by looking at the preview and fixed it with a hold at
the mark (the Curta project's commit `23c9e6f`, `Take.keys({0: 5.2,
lines.end(plus=0.6): "added_23", lines.end(plus=1.2): "added_23"})`). The
same rule runs the film's `set_23` and `set_145` into the crank strokes
after their marks today, unremarked, and the fixture counter's own `nine`
dissolves past the mark `nine` into the next turn of the crank.

## What the film does with the result

The next take a film declares, and the Curta film's next `check`, is told
by `check` which shot runs past which mark into which step during which
join, and by how much, before anything is rendered: the author holds the
shot at the mark or lets the machine run on under the dissolve, knowingly.
The Curta film's current document is reported with its two crossings,
`set-23` into the first stroke and `set-145` into the second, for its
author to decide; `read-23` as it was before the hold is reported naming
`added_23` and the units slide's move.

## What Changes

- **Resolution finds every continuation that crosses a mark.** For a take
  document, after the shots are timed, each shot that a join shows past its
  end is followed through the output frames on which the join shows it, by
  the timeline's own model-time rule; when its take time on the last such
  frame lies past a mark the shot ended on or before, the continuation
  crosses that mark. The step it runs into is the step that starts at the
  mark. A step boundary that is not a mark is not reported, and a shot held
  at its end (a model that stops moving) crosses nothing.
- **The resolved document records it.** The outgoing shot's `model` gains
  `crossing`: the join, the incoming shot, the mark, the step, the take
  time reached, how far past the mark, and the sentence `check` prints. A
  shot that crosses no mark is resolved exactly as before.
- **`check` reports it.** After the `Take:` line, one line per crossing, in
  film order, a sentence a reader can act on: `Continuation: shot nine
  runs on through the 0.5 s dissolve into shot carry and crosses the mark
  nine: its last frame there poses take time 6.76 s, 0.76 s past the mark,
  inside step-3, which moves crank by 360; hold the shot at the mark before
  it ends, or ease its model to rest there`. It is a report, not a
  refusal: `check` still passes.
- **The refusal stays.** A continuation that would run past the take's
  last second is refused with its words, before anything is reported.
- **Records**: ADR-014 (TIMELINE), the contract's "Resolution" in
  `docs/movie-document.md` (the resolved shot's `model.crossing`, as the
  brief allows), `README.md` (the `check` line),
  `docs/declaring-a-movie.md` (what a join does to a moving shot's take
  time), `fixtures/README.md`, `CHANGELOG.md`, a clause in
  `docs/architecture-overview.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `movie-document`: resolution records, and `check` reports, a shot on a
  take whose continuation through its outgoing join crosses a mark.

## Impact

Code: `src/movie.mjs` (resolution: the continuation's frames, the mark and
the step, `model.crossing` and its sentence), `bin/videomaker.mjs` (the
`check` lines). `src/timeline.mjs` and `src/take.mjs` are read, not
changed: both are in the shot cache's common key, and a report changes no
picture, so no film's shots are recaptured for it. Tests at layer 3
(`test/take.test.mjs`), layer 2 (the resolved pin `resolved/count.json`
gains `crossing` on its shot `nine`, the only change to any pin) and layer
8 (`check` of the fixture movie `count` prints the line); layer 9 for the
manual's words. No schema change (the schema is the unresolved document's),
no Python change (evaluation never knows a shot's length, which comes from
speech), no stage, viewer or encoding change.

## Non-goals

Changing how a join carries model time, or what a join shows; new joins; a
refusal of a crossing; anything in the stage. A crossing on a posed loop's
marks, which name instants of a loop no step follows (no film has asked).
A shot whose model time runs backward through its join (no film writes
one; nothing is reported for it). Naming a trigger's instruction, which the
document does not record (a finding, below in `design.md`). No publication,
push or paid request.
