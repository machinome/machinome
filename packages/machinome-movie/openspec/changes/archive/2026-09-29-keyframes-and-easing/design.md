## Context

A frame is a pure function of video time. `frameAt(e, t)` in `src/timeline.mjs`
finds the shot and its local time, then:

- `cameraAt` picks the camera keys around the local time (the last key with
  `at <= local`, and the next one; after the last key it holds), computes
  `u = min(1, (local - a.at) / (b.at - a.at))` (0 on a hold), eases it with
  `u*u*(3-2*u)`, and mixes position and target as `v + (w - v) * ease`, the field
  of view the same way (exactly the key's value when both keys share it), and, in
  a shot whose up changes, the two unit up directions, normalized again.
- Model time comes from `simulation.keyframes` (or the two implied keys
  `{0, from}` and `{duration, to}`): in the segment `[k_i.at, k_{i+1}.at)` it is
  `L + (R - L) * (local - A) / (B - A)`, evaluated left to right, multiplication
  before division.

`validateEpisode` accepts `machinome-video-draft/0.2` and `/0.3`; five places
compare the format with 0.3 (`episode.mjs`: annotations, highlight,
the 0.2 lens refusal, the up-along-view sweep; `timeline.mjs`: which frames
carry annotations and highlight). Camera keys, `simulation` and model keyframes
refuse nothing they do not know: an extra field is ignored today. A survey of
every Leonardo episode (four `demo-*` in 0.3, five in 0.2) found no field
outside the documented ones on shots, `simulation`, model keyframes or camera
keys.

The render's frame-cache identity hashes the served page files, `render.mjs`,
`timeline.mjs`, `code.mjs` and the lock file.

## Goals / Non-Goals

Give every keyed value in an episode one small, named easing vocabulary; let a
camera move and a mechanism's model time choose from it per segment; keep every
0.2 and 0.3 frame bit-exact; open format 0.4 for this campaign. Not goals:
overshooting or elastic curves, per-key tangents, easing anything that is on/off
today (transitions and entrances are later cycles), any viewer change.

## Decisions

### D1. Five curves, defined exactly

For `u` in `[0, 1]` (clamped: `ease` first sets `u = min(1, max(0, u))`, the
identity inside the interval):

| name     | value                                                  | speed at start / end |
|----------|--------------------------------------------------------|----------------------|
| `linear` | `u`                                                    | 1 / 1                |
| `smooth` | `u*u*(3-2*u)`, today's expression, same operation order | 0 / 0, peak 1.5      |
| `in`     | `u*u*u`                                                | 0 / 3                |
| `out`    | `v = 1-u`; `1 - v*v*v`                                 | 3 / 0                |
| `in-out` | `u < 0.5 ? 4*u*u*u : 1 - 4*v*v*v`, with `v = 1-u`      | 0 / 0, peak 3        |

Every curve gives exactly 0 at `u = 0` and exactly 1 at `u = 1`, is
non-decreasing, and stays within `[0, 1]`: none overshoots or reverses. `in-out`
is `in` on the first half and `out` on the second, meeting at exactly 0.5;
`out(u) = 1 - in(1 - u)`; `smooth` and `in-out` are symmetric about the midpoint.

Why cubic for `in`, `out` and `in-out`, not quadratic:

- `in-out` must be a choice an author can see next to `smooth`, which is already
  the default S-curve. The quadratic `in-out` never departs from smoothstep by
  more than 3.7 % of the move, which no viewer can tell apart; the cubic one
  departs by up to 11.1 % (it lingers longer at each end and crosses the middle
  faster).
- At a quarter of its segment the cubic `in` has covered 1.6 % of the move
  (quadratic: 6.25 %): a start that reads as gentle, which is what the
  `machinome` shot's "resume motion" asks of a machine leaving rest.
- One family: all three share the degree of `smooth`.

The cost is speed: the cubic curves peak at three times the segment's average
speed (quadratic: two). Where that is too brisk the author adds a key and
shortens the eased segment (Risks).

### D2. The shared module `src/easing.mjs`

```js
export const EASINGS = ['linear', 'smooth', 'in', 'out', 'in-out'];
export function ease(name, u)              // D1; throws for any other name
export function keyedValue(keys, t, fallback)
  // keys: [{at, value, ease?}], `at` strictly increasing, values all finite
  // numbers or all finite vectors of one length; fallback: the field's default name
```

`ease` refuses any name outside `EASINGS`, including a non-string, `null`,
another capitalization and `ease-in`:
`Unknown easing: bounce; use linear, smooth, in, out or in-out`.

`keyedValue(keys, t, fallback)`:

- Before the first key it returns the first value; at or after the last key, the
  last value, as given (a hold).
- Otherwise it takes the segment `a = keys[i]`, `b = keys[i+1]` with
  `a.at <= t < b.at`, and the name `b.ease ?? fallback` (the segment ending at
  `b`, D3). For `linear` it returns `a.value + (b.value - a.value) * (t - a.at) / (b.at - a.at)`,
  evaluated left to right: today's model-time expression and operation order.
  For any other name it returns `a.value + (b.value - a.value) * ease(name, (t - a.at) / (b.at - a.at))`,
  today's camera expression, clamped into the closed interval between
  `a.value` and `b.value`. Vectors are interpolated component by component with
  the same formulas.
- At `t = b.at` it is already in the next segment and returns `b.value` exactly.

The two linear spellings are the same number up to the last bit, and differ
there on about 2 % of instants (for keys `{0, 158.7}` and `{8.6, 180.1}` at
`t = 8` the multiply-first order gives 178.60697674418606 and the divide-first
order 178.60697674418603). The order is therefore part of the contract, so that
every existing model time keeps its bits. The clamp on the eased branch makes
"an eased segment never leaves the interval between its keys" exact in floating
point: `out` rounds to exactly 1 slightly before its key, and `a + (b - a) * 1`
can land one unit in the last place beyond `b`. The clamp is new behaviour
only; no 0.2 or 0.3 frame reaches that branch through model time.

Later cycles call `ease(name, u)` for a progress curve (a transition, an
entrance, a word reveal) and `keyedValue` for a keyed number or vector (an
opacity, a pan-and-zoom `[x, y, scale]`). They validate their own keys and state
their own default name; the campaign's rule is `smooth` wherever a smoothstep
exists today.

### D3. One convention: `ease` on a key shapes the segment that ends there

Wherever keys carry `ease`, the value on a key names the curve of the segment
from the previous key to that key. It reads the way an author speaks: "arrive at
the linkage settling", "reach 461 gently". The first key ends no segment; `ease`
on it is refused, not ignored:
`Nothing to ease before the first camera key: shot genome` (and likewise
`... before the first model keyframe: shot genome`). A key without `ease` takes
the field's default. A hold (two keys with the same preset or the same seconds)
accepts any name and looks the same with all of them.

### D4. Camera keys

```yaml
# format machinome-video-draft/0.4 — the Revolutions genome shot, restaged
    camera:
      - {at: 0, preset: mechanism}
      - {at: 9.615, preset: linkage, ease: out}   # already travelling at the cut; settles on the linkage
```

Keys become `{at, preset, ease?}`, default `smooth`. `cameraAt` keeps its key
selection and its `u`, and replaces the fixed smoothstep with
`w = ease(b.ease ?? 'smooth', u)`. Position, target and field of view are mixed
with `w` by today's expressions (not through `keyedValue`), and in a shot whose
up changes, the two up directions are mixed with `w` and normalized, exactly as
today. With no `ease` anywhere, `w` is today's smoothstep by the same operation
order, so every 0.2 and 0.3 camera, field of view and up is unchanged to the bit.

The up-along-view sweep (`validateUpAlongShot`) already evaluates `cameraAt` at
every output frame, so it follows the eased path without change; the reversal
check between adjacent keys is unaffected (easing changes speed, not the
directions visited). The preview's lens proof poses the keys themselves, where
every curve gives exactly the key's value.

### D5. Model keyframes and "model time never decreases"

```yaml
# format machinome-video-draft/0.4 — the Revolutions machinome and genome shots, restaged
  - id: machinome
    simulation:
      from: 453
      to: 461
      keyframes:
        - {at: 0, seconds: 453}
        - {at: 3.733, seconds: 453}              # held pose while the assembly is restored
        - {at: 14, seconds: 461, ease: in}       # the machine starts gently
  - id: genome
    simulation:
      from: 461
      to: 466.8
      keyframes:
        - {at: 0, seconds: 461}
        - {at: 6.899, seconds: 466.8, ease: out} # settles into the pause on "pause"
        - {at: 12.5, seconds: 466.8}
```

Keys become `{at, seconds, ease?}`, default `linear`. Model time is
`keyedValue(keys as {at, value: seconds, ease}, local, 'linear')`; the implied
two keys of a shot without `keyframes` go through the same call.

What easing model time means: it is the speed of playback within a segment,
like slow motion, never the mechanism's own dynamics. Every frame still shows a
real pose of the simulation at some model second.

- Keys stay exact. At every key's `at` the model is at that key's `seconds`
  whatever the curves, so a mechanical beat aligned to a measured word by a key
  (the sawmill's cut/advance beats, the *Revolutions* half-cycle boundary) stays
  aligned. An event inside a segment moves in video time when the segment's
  curve changes; an author who needs it on a word puts a key there.
- Model time never decreases. `validateEpisode` still refuses keys whose seconds
  decrease. Each of the five curves is non-decreasing with values in `[0, 1]`,
  so between keys `L <= R` the eased value never decreases and, with D2's clamp,
  never leaves `[L, R]`. A curve that overshoots (a spring, a bounce) would run
  the machine backwards past a key; none of the five does, which is one reason
  the vocabulary stops at five.
- Easing does not smooth a speed change across a key. Each segment is eased on
  its own: `in` after a moving segment first returns the machine to rest, and
  `out` into a moving segment arrives at rest. A hold on each side, as in both
  *Revolutions* shots, is where these curves read best.

### D6. Nothing else in the format gets a curve now

- Typing cues reveal characters at a steady rate between measured narration
  instants; a varying typing speed has no craft reason and no episode asks.
- Overlays, annotations and highlights are on or off within their intervals.
  Their entrances are campaign item 7 (graphic overlays with entrances) and item
  5 (transitions); those proposals name an easing from D1 and use D2.
- Speech offsets, the progress rule (linear in video time by definition) and the
  code cursor stay as they are.
- A plain `simulation: {from, to}` span takes no `ease`: two keys with `ease` on
  the second already say it, and a second spelling would be one more thing to
  keep consistent.

### D7. Format 0.4

The first cycle of the film motion campaign applied implements the shared
decision, on the pattern of `annotate-a-part` D5:

- `FORMATS` gains `machinome-video-draft/0.4`; `loadEpisode` and
  `validateEpisode` accept it. 0.4 accepts everything 0.3 does with the same
  meaning. The five comparisons with 0.3 (Context) become "0.3 or later"
  (and the 0.2 lens refusal "is 0.2"), through one ordered comparison, so a 0.4
  episode may annotate, highlight and change lens. Their messages are unchanged
  ("Annotations need format machinome-video-draft/0.3", read as "0.3 or later").
- `frameAt` gives 0.4 frames exactly the shape of 0.3 frames (always
  `annotations` and `highlight`). A 0.4 episode without `ease` therefore produces
  frames deep-equal to the same episode declared 0.3.
- `ease` on a camera key or a model keyframe is accepted only in 0.4. In 0.2 or
  0.3 it is refused, naming the shot:
  `Easing needs format machinome-video-draft/0.4: shot genome`. The bump is
  needed: today's validator ignores unknown key fields, so without it a 0.3
  episode with `ease` would render with every curve silently replaced by the
  default.
- Closed field lists in 0.4. A shot accepts `id, start, end, speechOffset,
  narration, direction, simulation, camera, hiddenLayers, overlays, evidence,
  code, annotations, highlight`; `simulation` accepts `from, to, keyframes`; a
  model keyframe `at, seconds, ease`; a camera key `at, preset, ease`. Anything
  else is refused, naming the shot:
  `Unknown camera key field: eas (key #1 in shot genome)`,
  `Unknown model keyframe field: ...`, `Unknown simulation field: ...`,
  `Unknown shot field: transiton (shot genome)`. This is the house rule ("a
  misspelled field is refused"), and it matters more in 0.4 than before: 0.4
  grows over five campaign cycles, and without the closed list a 0.4 episode
  using a later cycle's field would render silently without it on a build that
  predates that cycle. Each later cycle adds its fields to the list. 0.2 and 0.3
  keep ignoring unknown fields, as today, so no existing episode can break.
- No viewer requirement is added. `requiredViewerApi` stays reason-based: a 0.4
  episode that only eases needs Viewer API 21, and its page calls are the same
  calls with different numbers. The campaign as a whole runs on Viewer API 28
  because of the 0.3 cues it uses, not because of the format.

### D8. Frame cache and provenance

The render identity adds the hash of `src/easing.mjs`, the new module on the
frame path, so a change to a curve starts a new frame cache. (The identity of
every existing episode changes once with this change, since `timeline.mjs`
changes too; the frames it re-renders are identical.) The build manifest already
records the resolved episode, including every `ease`.

## Risks / Trade-offs

- Cubic curves peak at three times a segment's average speed. Restaged, the
  `machinome` segment (8 model seconds over 10.267 s) ends at about 2.3 times
  real speed and `genome`'s `out` starts at about 2.5 times, just after the cut.
  Whether that reads as a gentle start and a settle, or as a rush, is for the
  pilot's motion review; a key that shortens the eased part tempers it. A switch
  to quadratic curves would change 0.4 frames only, which no released episode
  uses yet (Open Questions).
- Easing model time can be mistaken for the machine's physics (a waterwheel does
  not brake). It is the same editorial time as the freeze *Revolutions* already
  uses on "pause"; narration and directions must not present it as dynamics.
- A speed jump at a key between two moving segments is not smoothed (D5). The
  *Revolutions v2* draft's `ratchet-is-a-spool` ("first show winding motion,
  then clearly accelerate model time") cannot be spelled without a visible dip
  to rest, because `in` starts from zero speed. That shot is an unrendered
  editorial draft; speed-matched curves would need per-key speeds, which no
  rendered episode asks for, and are left out.
- Closed field lists in 0.4 make a later cycle's field a refusal on an older
  build, by design; an author must use a build that knows the field.
- The arithmetic order of D2 is load-bearing for bit-exact frames and easy to
  "tidy" away; the pin in tasks 1.2 includes an instant where the two orders
  differ, so a reordering fails a test.

## Migration Plan

Additive. 0.2 and 0.3 episodes, including every Leonardo episode, parse and
render with identical frames (pinned by test, and by byte-identical preview
stills before and after with one bundle). Authors opt in by changing `format`
to 0.4 and adding `ease` where wanted. Reverting the tool commit makes a 0.4
episode "Unsupported episode format", never rendered with its curves missing.

## Open Questions

- Cubic or quadratic `in`/`out`/`in-out` (D1): cubic is chosen so that `in-out`
  is visibly distinct from `smooth`; the pilot may prefer quadratic's gentler
  peak after seeing the demo clip. Deciding before the first 0.4 episode is
  released keeps the change free.
- Whether *Revolutions* itself moves its `machinome` and `genome` shots to 0.4
  is the pilot's editorial decision; this change only makes it possible.
- The closed shot-field list (D7) is campaign-wide in effect: every later cycle
  must add its fields. The orchestrator confirms that at ratification.

## Ratification (29 September 2026)

Ratified by the orchestrating agent as the campaign's review gate, under the
pilot's delegation, with these resolutions:

- **D1 stands as cubic.** The pilot judges the peak speed in the demo clip;
  a switch to quadratic would change 0.4 frames only.
- **D7's closed field lists are campaign-wide.** Every later cycle of the film
  motion campaign (`shot-transitions`, `graphic-overlays`, `text-animation`,
  `stills-and-clips`) adds its fields to the 0.4 lists it touches, and the
  cycle that first touches overlay cues closes their field list too. Recorded
  in `workflow/ongoing/film-motion-campaign.md`.
- **Task 3.4's clip is implementation evidence** (small, silent); the
  campaign's demo video for the pilot is produced separately, at output size,
  after this change is archived.
- **Task 3.1 is authored in the Leonardo project as an untracked demo episode**
  (`videos/demo-keyframes-and-easing/`), as the earlier demos were; nothing is
  committed to Leonardo.
