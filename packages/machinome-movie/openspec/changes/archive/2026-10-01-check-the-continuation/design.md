## Context

A join between two shots is drawn from same-instant captures (the
shot-transitions change, the react-stage change's D4): while a dissolve, a
wipe or a slide lasts, and through the first half of a fade, the frame
carries the outgoing shot's frame under `transition.outgoing`, posed at its
own local time past its end. Its model time there is
`modelSecondsAt(shot, local)` in `src/timeline.mjs`: past the shot's end,
the last key's take time plus the shot's end rate (`endRate`: the last
segment's average rate times its easing's end slope, so a hold, or a
segment eased to rest, stands still) times the seconds past the end. On a
take document that take time is posed as a bank by the pose rule
(`bankAt`, ADR-012), so a shot that ends still moving shows the machine
running on into whatever the take does next.

`checkResolved` in `src/movie.mjs` refuses one case: a continuation whose
reach (`last + endRate × joinShows(join)`) passes the export's length. A
continuation that stays inside the take and runs past a mark, into the
next step, is drawn and not mentioned. The Curta film's `read_23` did
that; the fixture counter's `nine` does it today (ends on the mark `nine`
at 6 s, `endRate` 4/2.1 take seconds per second, a 0.5 s dissolve into
`carry` at 10 fps: its last frame in the dissolve poses 6.76 s, inside
`step-3`, the second turn of the crank).

The marks are the author's named instants (`Mark(name)`), each the exact
end of a step (ADR-016). The shot cache's common key hashes
`src/timeline.mjs` and `src/take.mjs` among the renderer's modules, and not
`src/movie.mjs`: a change to either recaptures every shot of every film.

## Goals / Non-Goals

Goals: `check` names every shot on a take whose continuation through its
outgoing join crosses a mark, with the join, the mark, how far past it, and
the step it runs into, in a sentence that says what to do; the resolved
document records the same fact on the shot's model time. Non-goals: those
of the proposal.

## Decisions

### D1. A report, not a refusal

A crossing is printed by `check` and recorded in the resolved document;
`check`, `preview` and `render` still pass. An author may want the machine
to keep moving under a dissolve (the campaign's cut of finding 3). The
refusal of a continuation past the take's end keeps its words, its
abstract reach and its place: it runs first, in `checkResolved`, so a
document it refuses reports nothing.

Rejected: **refuse a crossing.** It would forbid a legitimate film, and an
author's only way out would be a hold the film does not want.

### D2. Measured on the frames the join poses

The take time a continuation reaches is the one posed on the last output
frame the join shows the outgoing shot: for the frames `n / fps` of the
film from the incoming shot's start (the frames the renderer and the shot
cache pose, `index / fps`), while a dissolve, wipe or slide lasts
(`t < start + duration`) or a fade is in its first half (`2u / duration <
1`, settled as `transitionAt` settles it), the outgoing shot's
`modelSecondsAt(shot, (end − start) + u)`, `u = t − start`; a reframe shows
no outgoing shot. These are `transitionAt`'s own conditions and
`modelSecondsAt` is the frame's own rule; a layer-3 test holds them
together by reading the outgoing view's bank from `frameAt` on every frame
of the counter's join.

A mark `m` is crossed when `e ≤ m < r`, `e` the shot's take time at its end
(its `to`, or its last key's `seconds`, with marks resolved) and `r` the
take time on that last frame. A shot that ends on the mark still moving
crosses it (`read_23`, `nine`); a shot that ends before a mark and runs
past it crosses it too; a shot held at its end, or eased to rest, has
`r = e` and crosses nothing; a continuation that only reaches a mark, on
its last frame, does not cross it, since that frame poses the mark's
recorded bank exactly.

Rejected: **the abstract reach** (`e + endRate × joinShows`), the
refusal's measure. A mark inside the last frame's interval would be
reported though no frame shows the machine past it; the report is about
what is drawn. The refusal keeps the abstract reach: it guards what the
viewer may be asked, conservatively.

### D3. Marks only; the first crossed; the step that starts there

Only the document's `marks` are reported: a step boundary that is not a
mark is not an instant the author named, and running through one is what a
continuation does. When a continuation crosses several marks, the first,
the smallest `m`, is reported: holding there holds them all. The step it
runs into is the step whose `at` is that mark, exactly (a mark is the
written end of the step before it, and the next step's `at`, ADR-016); it
is named by its `id`, its `input` and its `to` or `by` as the document
records them: `step-3, which moves crank by 360`. The document does not
record a trigger's instruction by name (the take block carries what the
framework returned for the request, `input` and `to` or `by`), so a
trigger's step is named the same way; the finding is recorded in the
evidence, and the contract is not forked for it.

A crossing is looked for only on a take document: a posed loop's marks are
instants of a loop, with no step after them, and no film has asked.

### D4. Recorded on the shot's model time in the resolved document

Resolution adds to the outgoing shot's resolved `model`, and only to a shot
that crosses a mark:

```json
"crossing": {"join": "dissolve", "duration": 0.5, "into": "carry",
             "mark": "nine", "step": "step-3",
             "reaches": 6.761904761904763, "past": 0.7619047619047628,
             "report": "Continuation: shot nine runs on through …"}
```

`join` and `duration` are the incoming shot's `transition`, `into` its id;
`reaches` is `r` and `past` is `r − m`, unrounded; `report` is the sentence
`check` prints. A shot that crosses nothing is resolved exactly as before,
so the pins of `minimal` and `tour` (loops) do not change and `count`'s
gains this one field on `nine`. `check`, `preview` and `render` write the
same `movie-resolved.json`, so the stage, the proofs and a reader of the
build read the same fact `check` printed. `check` prints each `report`
after the `Take:` line, in film order.

Rejected: **a list on the take block**, or a top-level `crossings`: the
fact belongs to the shot whose model time runs on, where its model time is
recorded. **Recording every continuation**, crossing or not: it would
change every pin with a join for a fact nobody reads.

### D5. In resolution, outside the shot cache's key

The rule is written in `src/movie.mjs`, beside `checkResolved`'s refusal of
the same continuation, reading `modelSecondsAt` from `src/timeline.mjs`;
`src/timeline.mjs` and `src/take.mjs` are not edited. Both are in the shot
cache's common key, and a report changes no picture: the Curta film's 3 787
captured frames stay valid. The shot cache does not hash the resolved
document; it hashes each frame's request, which `crossing` does not enter.

Rejected: **a helper in `src/timeline.mjs`** shared with `transitionAt`.
It would state the join's extent once, at the price of recapturing every
film for a sentence; the layer-3 test that compares the two on real frames
keeps them from drifting.

### D6. No Python change

Evaluation writes the unresolved document: a shot's length comes from the
narration's measured speech, which only resolution knows, so the take time
a continuation reaches cannot be known before it. The shared documents do
not change; both suites still check every fixture as before, and the
crossing is a fact of the Node resolver's pin.

### D7. The words

    Continuation: shot <id> runs on through the <duration> s <join> into
    shot <into> and crosses the mark <mark>: its last frame there poses
    take time <r> s, <past> s past the mark, inside <step>, which moves
    <input> to|by <value>; hold the shot at the mark before it ends, or
    ease its model to rest there

Seconds in the sentence are written to two decimals, as the refusal beside
it writes its reach; the record keeps them unrounded. The remedy names the
two ways a shot stops moving at its end: a last key at the mark held to
the shot's end, or a segment ending at the mark with an easing whose end
slope is 0 (`smooth`, `out`, `in-out`).

## Risks / Trade-offs

- The resolved document gains a field. Readers of it (the stage, the
  review packs, the shot cache) ignore fields they do not know; the stage
  reads frames, not shots' model blocks. The pin of `count` changes by one
  field, reviewed by hand.
- The Curta film's current document is reported with two crossings
  (`set-23` into `step-3`, `set-145` into `step-7`): `check` stays green and
  the film is not changed by this change.
- A shot whose model runs backward is not reported; the take's model time
  in a film runs forward, and no declaration of a backward continuation
  exists.

## Migration Plan

None: a report on documents that load today.

## Open Questions

None.
