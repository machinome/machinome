## Why

Cycle 5 (`execute-the-commit`, ADR-062) made this viewer read and execute a
version 8 clocked machine: the bank, the request, the event solve, the
commit, the clip at a declared stop, the pose. It left exactly one thing
behind, and said so in ADR-062's own last line — **the CLOCK**.

solid-node's ADR-127 gives a clocked root a third time base. Under
`Time.elapsed()` the machine banks `time`: seconds, a float, starting at
`0.0`, published as `clocked.clock: "time"` (ADR-128 §10). A request may
MOVE it — `move('time', by=)` or `to=` — and every event whose level is a
function of elapsed seconds is located on that path by the same solver, the
same landing rule and the same ordering a driver's events use. **Events on
time and events on inputs are the same kind of event.** Nothing stops a
clock: a declared range is a MECHANICAL stop (ADR-108) and nothing is in the
way of the next second, so no compiled constraint ever clips a time request.
Time never runs backwards: a request that would is REFUSED by name, because
no bound was met and the request is meaningless rather than obstructed.

This build banks the clock, poses from it and refuses the one gesture:

```text
move('time', …) asks this machine's clock to advance, which this build
does not yet do. The bank stands at 0 seconds and the model is posed
there; a later build moves the clock and fires the events on it.
```
(`src/clocked/machine.ts:281-292`)

Three consequences follow, and this cycle closes all three.

1. **The conformance corpus is not whole.** `src/clocked-corpus.json`
   carries 30 machines and 76 steps; cycle 5 replays 68 of them and 652 of
   the 722 recorded numbers. The remaining 8 are the clock's: three
   requests this build refuses where the producer admitted them
   (`Regulator` 0, `ClockAlone` 0, `Lift` 0) and five steps standing
   downstream of them, against a bank this build cannot reach. The census
   test pins `76 = 68 + 3 + 5` precisely so that partition cannot be
   forgotten (`src/clocked/clocked-corpus.test.ts:183-213`). The exactness
   claim — bit for bit, `tolerance.float` read from the file — is untested
   on the one machine shape whose landings are the strangest the corpus
   holds: `Regulator`'s first release lands on `0.49999999999999994`, one
   representable value below the ideal instant, which is the landing rule
   working rather than a rounding error (ADR-127, "An event on the clock is
   an event").
2. **A maker cannot RUN an elapsed clocked machine.** The chrome shows the
   clock as a follow-only readout and offers no transport at all
   (`src/clockedControls.ts:236-240`; the spec says "SHALL NOT offer a
   transport"). A pendulum whose bob is a formula of elapsed seconds and a
   counter beside it stands at `t = 0` forever. That is a truthful render
   of an instant, and it is not a machine anyone can watch.
3. **A published guard is missing.** The producer compiles a constraint
   plan per DECLARED DRIVER only (`solid_node/simulation/clocked.py:1422`)
   and refuses any composed chain carrying a name the bank has not got
   (`clocked.py:1448-1487`), so no document it writes can carry a stop that
   follows the clock. The viewer's loader mirrors the first of those
   (`src/clocked/document.ts:753-757`) and not the second: a bound's chain
   is checked against `declaredNames`, which INCLUDES the clock
   (`document.ts:288-302`, `:674-677`). A hand-written or corrupted
   document could therefore be clipped against a clock-driven coordinate
   the producer would have refused.

## What Changes

- **A request may move the CLOCK.** `machine().move('time', {by})` and
  `{to}` execute on the same path as a driver request: the clock is the
  moving input, every `commits` entry whose published `shapes` names it is
  examined and no others, crossings are solved and landed by the same
  far-side walk, relations landing on one float are one event with
  synchronous pre-event reads, commits are in path order, and the tree is
  posed ONCE from the resulting bank. `by=0` and `to=` the banked instant
  are ADMITTED and move nothing.
- **Nothing stops a clock, as a PROMISE.** No declared stop ever clips a
  request that moves the clock. It already falls out of the compile —
  `bounds.ts:207-208` finds no plan for an input no constraint names — and
  this cycle states it, asserts it on `Lift` (a machine with a clock AND
  two compiled bounds) and refuses at LOAD any document that would make it
  false. The END-OF-REQUEST judgement is unchanged: a commit inside a time
  request that carries a bounded coordinate out of range still refuses the
  whole request by name.
- **Time never reverses.** A request whose travel is negative, or whose
  `to=` lies behind the banked seconds, is refused by name — kind
  `ValueError`, naming the clock and both instants — mirroring
  `clocked.py:2068-2082`. It is a refusal, not a stop.
- **The census closes: 76 of 76, 722 of 722.** All three clock machines
  replay bit for bit, `Regulator`'s recorded `ValueError` becomes an
  ordinary matched refusal, and its snapshot/restore steps replay. The
  deferred list and the departure assertions are DELETED and the census
  asserts `76 = 76`, so the file — not a list — still decides.
- **A maker runs an elapsed clocked machine on screen.** A transport beside
  the clock readout: PLAY/PAUSE, which issues exactly ONE
  `move('time', {by})` per rendered frame for the wall seconds elapsed
  since the last frame times the playback speed; a STEP, which advances the
  clock by a stated number of seconds; and the existing speed ladder, whose
  ×3600 exists for exactly this. There is NO scrub and NO reverse: the
  clock is one-way by decision, and a control that could not honour a drag
  backwards must not offer one. Pause holds the bank; RESET returns the
  whole bank to its published defaults with the clock at `0`. A refused
  frame PAUSES the transport and reports the message, rather than repeating
  a refused request sixty times a second. A machine that declares no clock
  gets no transport, exactly as today.
- **A `bounds` entry that follows the clock is refused at load**, by name,
  mirroring the producer's own general refusal: a constraint's chain, its
  bound or its level naming the machine's clock, and its `shapes` naming
  the clock, are each malformed — a clocked stop is compiled over the bank,
  and a clock-driven coordinate is not something a stop can hold.
- **The declared API version rises 17 → 18.** `documentVersions` does NOT
  move: it stays `[1 … 8]`, because no new document shape is read. What
  moves is a CAPABILITY a host may require — a build at 17 mounts an
  elapsed clocked document and refuses every request that would make it
  run, with no way for the host to know beforehand except by trying.
- **Measured and printed**: the per-frame cost of the play control on
  `Regulator` in thread and in a real page, against the 16 ms frame budget,
  at ×1 and at the speeds where one frame carries tens of events; and the
  whole-corpus replay, against cycle 5's 13.6 ms for 68 steps.
- **A version 8 ELAPSED document with geometry runs in a real page**: the
  framework's own `tests/clocked_project/pendulum.py:Regulator` — a bob
  posed by `A·sin(360·time/T)` and a count the machine writes twice a
  period — exported verbatim and committed as `tests/fixtures/regulator/`,
  mounted in Chromium, played, paused, stepped and reset.
- **NOT** a change to the document's shape, to the framework, or to the
  contract between the two packages; not an instruction with meaning; not a
  cadence for the drivers (`step()` and `rate()` stay refused); not a
  clipped time request; and nothing of the viewer's code moves into
  solid-node.

## Capabilities

### New Capabilities

None. This cycle widens capabilities the viewer already has.

### Modified Capabilities

- `viewer-package`:
  - **ADDED** — "A request may advance a clocked machine's clock" (the time
    request, its events, the promise that nothing clips it, the backwards
    refusal, zero admitted, and the session verbs carrying it).
  - **ADDED** — "A maker runs an elapsed clocked machine on screen" (the
    transport: play/pause, step, speed, the seconds readout, pause holding
    the bank, reset, and a refusal pausing rather than repeating).
  - **MODIFIED** — "The viewer executes a clocked machine's requests" (the
    one input a request may move is a declared driver OR the machine's
    clock).
  - **MODIFIED** — "A declared stop stops a clocked request on its path"
    (no stop ever clips a time request; the end-of-request judgement is
    unchanged).
  - **MODIFIED** — "A clocked machine the viewer cannot execute is refused
    by name" (the clock-request refusal is withdrawn; a request naming a
    clock a document does not declare, and a constraint that follows the
    clock, are refused).
  - **MODIFIED** — "The two runtimes agree on the clocked corpus" (every
    step is replayed; the census asserts the whole file).
  - **MODIFIED** — "A maker operates a clocked machine on screen" (the
    clock readout is joined by the transport of the new requirement; a
    machine with no clock still has none).
  - **MODIFIED** — "One loader reads either published document" (what a
    version 8 document's clock means to a consumer).
  - **MODIFIED** — "The viewer declares its API version" (18).
  - **MODIFIED** — "The host chooses how driver controls are presented"
    (the sentence names the third kind of document the switch gates, which
    cycle 5's implementation already did and its spec did not say).

## Impact

- `solid_node_viewer/widget/src/clocked/machine.ts` — the clock as a moving
  input, the backwards refusal, the promise that no constraint is consulted
  for it.
- `solid_node_viewer/widget/src/clocked/document.ts` — the mirrored guard on
  a constraint that names the clock.
- `solid_node_viewer/widget/src/clocked/clock.ts` (new) — the pure per-frame
  advance: wall seconds × speed, capped, with the remainder carried, on
  `src/run/runtime.ts:270-296`'s own shape.
- `solid_node_viewer/widget/src/clockedControls.ts` — the transport beside
  the readout; `src/viewer.ts` — the frame hook, the two new handle verbs,
  and the chrome that renders them.
- `solid_node_viewer/widget/src/clocked/clocked-corpus.test.ts` — the
  departure and deferral deleted, the census closed; `src/clocked/cost.test.ts`
  — the per-frame numbers.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi: 18`;
  `src/version.test.ts`.
- `tests/fixtures/regulator/` (new), `tests/support.py`, and a new Playwright
  acceptance beside `tests/test_calculator_document.py`.
- `CHANGELOG.md` under `0.2.0 — unreleased`, `README.md`'s version table; ONE
  new decision record, `docs/adrs/EXPORT/ADR-063`, extracted after
  implementation and consuming solid-node's ADR-127 and ADR-128 §10, and
  `docs/adrs/README.md`.
- Nothing in the framework, nothing in another checkout, nothing of the
  document's shape, and nothing of the run.
