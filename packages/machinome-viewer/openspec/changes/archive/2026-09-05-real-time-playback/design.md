## Context

`viewer.ts` keeps one `time` in 0..1, advances it in the animation loop by
`elapsed / cycleSeconds` while playing, and sets `cycleSeconds =
frames / fps` whenever a document is loaded or republished. The bar
(`buildControls`) is play/pause plus a range slider stepping by
`1 / frames`. `resolveOptions` clamps a host-set initial `time`. Expressions
are evaluated with `$t` bound to that fraction; a framework document with a
declared time base already multiplies `$t` by the loop inside its
expressions, so nothing about evaluation changes.

The paired framework change publishes an optional `animation.loop`. Speed is
the viewer's decision: the framework declares what a turn is, the maker
decides how fast to watch it.

## Goals / Non-Goals

**Goals:**

- Real time by default when the document says what a turn is.
- A speed the maker can change without leaving the viewer, and a readout so
  the slider position means something (a clock at 6:00:00, not at 0.5).
- The same door for the host: an option and two handle methods, as for time.
- Byte-for-byte the old behaviour for a document without `loop`.

**Non-Goals:**

- Changing the slider's domain: it stays 0..1 of the turn, which is what
  `$t`, the capture's `--time` and every expression already share.
- A free-text speed field. A ladder is accessible, predictable and enough;
  the host option covers any exact value.
- Frame-stepping or scrubbing precision beyond `1 / frames`.
- Anything in the Python package or the capture.

## Decisions

### D1. `loop` decides the cycle; `speed` divides it

`cycleSeconds = loop / speed` when `loop` is present, `frames / fps`
otherwise, recomputed in `refreshControls` (document load and republish)
and whenever speed changes. `speed` is widget state beside `time`, initial
value from the resolved option, surviving `update()` and republish exactly
as `time` does. Positive finite numbers only; anything else throws naming
the value from both the option resolver and `setSpeed`.

### D2. A pure playback module

`playback.ts` holds what can be decided without a DOM: the speed ladder
(`[0.1, 0.25, 0.5, 1, 2, 5, 10, 60, 360, 3600]`), `ladderFor(speed)`
(the ladder with a host-set value inserted in order when absent), and
`formatMachineTime(seconds, loop)` (`h:mm:ss` when `loop >= 3600`, `m:ss.s`
when `loop >= 60`, else `s.ss s`). Both are unit-tested in vitest the way
`controls.ts` is; `viewer.ts` renders exactly what they return.

### D3. The bar grows two elements, only under `loop`

A `<select>` for speed (`aria-label="Playback speed"`, options labelled
`×0.1` … `×3600`) and a `<span>` readout, appended after the slider.
Choosing a speed does not pause playback; scrubbing still does. The readout
updates from `setTime`, so it follows both playback and scrubbing. A
document without `loop` builds the bar it built before, so the existing
control tests keep passing untouched.

### D4. Handle and option

`ViewerOptions.speed?: number`; `ViewerHandle.speed(): number` and
`setSpeed(value: number): void`. `setSpeed` on a document without `loop` is
accepted and stored — the host may set it before the document it applies to
is republished — but has no effect on playback until a loop is present.
API version rises from 5 to 6: a host may require the speed capability.

### D5. The mount page and the capture are untouched

The capture mounts with `animation: 'none'`-style host-driven time at the
requested fraction; playback speed never enters a still photograph.

## Risks / Trade-offs

- [A twelve-hour loop at ×1 barely moves the slider] → That is the truthful
  picture; the readout ticks and the maker picks ×720 to see a turn in a
  minute. The ladder tops at ×3600 so a day-long loop can be watched in
  under a minute.
- [Two bars to maintain (with and without loop)] → One builder with one
  conditional append; the difference is two elements.
- [An API bump forces the shop floor to accept 6] → Its check is "too old",
  not "exactly"; the framework's `solid viewer` report carries whatever the
  installed package declares.

## Migration Plan

Additive. Documents without `loop` play as before; hosts that pass no
`speed` see no change. Framework side lands independently; a new viewer over
an old document, or an old viewer over a new document, both behave as they
did today.

## Open Questions

None.
