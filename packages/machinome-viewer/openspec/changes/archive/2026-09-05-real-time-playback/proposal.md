## Why

The viewer plays every animation loop in `frames / fps` seconds — twelve
seconds for every document the framework publishes — because nothing in the
document says how long a turn of `$t` is. A clock modelled in real seconds
(3DPrintedClocks `wall_clock_01`: one turn is twelve hours, a 1.5 s
pendulum) plays at 3600× with 80 beats of the pendulum per frame; a maker
cannot watch the escapement work, and cannot slow it down.

The framework's paired change (`declared-time-base` in solid-node) lets a
root declare `time = Time(loop=<seconds>)` and publishes that loop as an
additive `animation.loop` key in every document it produces. The published
expressions already carry `$t * loop`, so the pose at every slider position
is right today; what the viewer cannot do is play the loop at a rate that
means something, or tell the maker what machine time the slider is at.

## What Changes

- The document type gains an optional `animation.loop` (seconds of machine
  time per turn of `$t`). A document without it is played exactly as today.
- When `loop` is present, playback runs at **real time by default**: one
  turn of `$t` takes `loop / speed` wall-clock seconds, with `speed`
  defaulting to 1. The maker chooses the speed from a control in the
  animation bar over a fixed ladder (slow motion through thousands of
  times real time), and the bar shows the machine time at the slider
  position (`h:mm:ss` for long loops, seconds for short ones).
- The host may set the initial speed through a new mount option and read or
  change it through the handle (`speed()`, `setSpeed(value)`), the way it
  sets and drives time. A document without `loop` ignores speed.
- `frames` keeps its role as the slider's step; `fps` is used only when
  `loop` is absent.
- The viewer API version rises, because a host may now require the speed
  capability.
- The capture's `--time` keeps its 0.0–1.0 meaning; nothing changes there.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: "The host chooses how animation is presented" — playback
  period, speed control, machine-time readout, host speed option and handle
  methods, all conditional on `animation.loop`.

## Impact

- `solid_node_viewer/widget/src/types.ts` — `animation.loop?`.
- `solid_node_viewer/widget/src/viewer.ts` — cycle computation, bar
  controls, handle methods; `options.ts` — `speed` option; a small pure
  module for the speed ladder and the time readout so both are tested in
  plain node.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi` bump.
- `README.md`, `CHANGELOG.md` — document the behaviour.
- No change to the Python package, the development server, the capture or
  the development app shell; the shell mounts with inline animation and
  gets the control through the bar.
- Consumers: the framework's `solid viewer` report carries the new API
  version; the shop floor's bundle check accepts a newer one.
