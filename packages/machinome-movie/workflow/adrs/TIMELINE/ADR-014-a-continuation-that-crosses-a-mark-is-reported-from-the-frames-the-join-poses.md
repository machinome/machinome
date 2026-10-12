# ADR-014: A continuation that crosses a mark is reported, from the frames the join poses

Status: Accepted (OpenSpec change `check-the-continuation`, 1 October 2026)

Numbered 014 by the addition-warts campaign's plan; ADR-013 and ADR-015
onward are other cycles' of the same campaign. A merge that reorders them
renumbers.

## Context

While a dissolve, a wipe, a slide or the first half of a fade still shows
the outgoing shot, that shot continues past its end (the shot-transitions
change; the react-stage change's D4): its model time runs on at the rate it
ended with, so a hold stays held and a moving shot keeps moving. On a
clocked take (ADR-011, ADR-012) the take time it reaches is posed as a
bank, and a shot that ends on a mark still moving shows the machine
running on into the next step. The only rule about it refused a
continuation that would pass the take's last second.

The Curta film *Addition* met the gap (finding 3 of its warts): `read_23`
ran its take time from 5.2 s to the mark `added_23`, the dials reading 23,
and its 0.6 s dissolve into `set_145` ran it on into the next step, the
units slide moving to 5. Nothing said so; the author found it by looking
and held the shot at the mark. The film's `set_23` and `set_145` still run
into the crank strokes after their marks, and the fixture counter's `nine`
into the next turn of the crank, unremarked.

## Decision

**A crossing is a report, recorded at resolution.** For a take document,
resolution follows each shot a join shows past its end through the output
frames `n / fps` on which the join shows it, by `transitionAt`'s own
conditions, and takes its take time on the last of them by the frame's own
rule (`modelSecondsAt`). A mark `m` with `end ≤ m < reached` is crossed,
`end` being the shot's take time at its end; the first is reported, with
the step whose `at` is the mark. The outgoing shot's resolved `model`
carries `crossing` (the join, its duration, the incoming shot, the mark,
the step, the take time reached, how far past, and the sentence), and
`check` prints the sentence after its `Take:` line. Nothing is refused for
it.

**Marks only.** A step boundary that is not a mark is not reported: a mark
is the instant the author named, and running through an unnamed boundary
is what a continuation is for.

**Outside the modules the shot cache hashes.** The rule is in
`src/movie.mjs`, beside the refusal of the same continuation, reading
`modelSecondsAt`; `src/timeline.mjs` and `src/take.mjs`, whose hashes key
every shot cache, are not changed, since a report changes no picture. A
layer-3 test holds the rule's frames to `frameAt`'s on the fixture
counter's join.

## Options considered

- **Refuse a crossing.** An author may want the machine to keep moving
  under a dissolve; a refusal would force a hold the film does not want.
- **The abstract reach** (`end + endRate × the join's shown seconds`), the
  refusal's measure. It would report a mark inside the last frame's
  interval, which no frame shows the machine past; the report is about
  what is drawn. The refusal keeps it, as a conservative bound on what the
  viewer is asked.
- **A helper in `src/timeline.mjs`** shared with `transitionAt`. One
  statement of the join's extent, at the price of recapturing every film's
  shots for a sentence.
- **Recording every continuation, crossing or not**, or a list on the take
  block. A fact nobody reads would change every pin with a join; the
  crossing belongs to the shot whose model time runs on.
- **Reporting from Python.** Evaluation never knows a shot's length, which
  comes from measured speech; only resolution can say how far a
  continuation runs.

## Consequences

- `check` names the shot, the join, the mark, the take time reached and
  how far past it, the step with its input and its `to` or `by`, and the
  two ways to stop: hold the shot at the mark before it ends, or ease its
  model to rest there. The resolved document every command writes carries
  the same fact.
- The fixture `count`'s resolved pin gains `crossing` on `nine`; no other
  pin changes. A film's shot cache is not invalidated by this change.
- A trigger's step is named by its input and its `by`, since the take block
  does not record the instruction's name.
- A posed loop's marks and a shot whose model runs backward are not
  followed.
