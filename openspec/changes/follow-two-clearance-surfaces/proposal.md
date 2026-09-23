## Why

The Curta Type I radial positioning-ball trial at project checkpoint `a2d0783` has two measured, independently moving clearance surfaces. Its ball must be pushed by either surface, remain where it was when contact retreats, and stop the connected request when the surfaces become incompatible. The existing ADR-121 self-read switch pulls the ball back on retreat; `Play` admits only one direct, monotonic source with fixed offsets. Neither can state this measured mechanism.

## What Changes

- Add an explicit running-only two-envelope retained `Follow` law for one banked scalar coordinate. It evaluates declared lower and upper numeric expressions over ordered source coordinates, sweeps certified piecewise-affine paths, and projects the retained coordinate at each path piece. It does not reinterpret ordinary self-read laws or `Play`.
- Refuse malformed relation shapes, non-finite or reversed rest envelopes, uncertified source or envelope paths, ambiguous writers, and unsupported branch/discontinuity shapes by relation identity or as an atomic tick refusal. No sampling resolution or physical-stop tolerance changes.
- Carry exact absolute follower landings through the existing dynamic `Bound` prefix replay, so the Curta's separately declared lower and upper Bounds localize the first incompatible contact, retain relief, and replay after restore.
- Publish a distinct `follow` running edge only in documents that use it; raise their document version so an older viewer refuses the capability by name. A companion change in `machinome-viewer` will consume the same edge and prove parity before Curta adoption.

The Curta-backed scope is terminal follower output with matched dynamic Bounds, producer-published lower/upper jump plans, and exact linear sources from inputs, held bank coordinates or unbranched ordinary affine-law chains. Wiring/formula ancestry and downstream edge reads are refused rather than approximated from endpoint chords.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `couplings`: accept only the explicit ordered retained `Follow` relation shape.
- `simulation`: sweep certified two-envelope contact, preserve retained history, and use existing dynamic Bounds for incompatible-surface admission.
- `export`: publish and version the new running edge without altering older documents.

## Impact

Framework coupling resolution, running program compilation/propagation, source-path certification, dynamic-bound prefix replay, and document serialization change. The originating Curta trial has affine bell-turn and carriage-lift source laws, symbolic piecewise-linear bell/collar envelopes, two dynamic Bounds, and red tests for retreat hold, first-contact stop, relief, and snapshot replay. The trial remains unadopted until its independent geometry and paired browser gates pass. No project files, timestep, law sampling budget, or viewer source are changed by this framework cycle.
