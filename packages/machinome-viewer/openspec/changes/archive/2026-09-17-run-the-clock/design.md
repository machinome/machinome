## Context

**The base.** Viewer worktree `solid-node-viewer/WTs/clocked-machine`, branch
`clocked-machine`, head `ee9bb6c` — cycle 5's two commits over main `4a63aaa`.
Package `0.2.0` unreleased, `solidNodeViewerApi: 17`,
`solidNodeDocumentVersions: [1,2,3,4,5,6,7,8]`, highest EXPORT ADR **062**.
`npx tsc --noEmit` clean; `npx vitest run` → **44 files, 1139 tests, 31.5 s,
all green** (measured at proposal time).

**The producer.** solid-node branch `clocked-machine`, head `1a959d3`, nine
commits ahead of main `81c5364`, UNINTEGRATED, checked out READ-ONLY at
`solid-node/WTs/clocked-machine`. ADR-125 (the state), ADR-126 (the bound),
**ADR-127 (the clock)** and ADR-128 (the document) accepted 2026-09-17.
`tests/clocked-corpus.json` — 139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`, `"tolerance": {"float": 0.0}`, 30
machines, 76 steps, 722 recorded numbers — is committed here verbatim as
`src/clocked-corpus.json` and is the contract.

**What ADR-127 decided, and this cycle mirrors.** Under `Time.elapsed()` on a
root whose tree declares a `State`:

- the clock is a BANKED value, id `time`, in SECONDS, initial `0.0`, carried
  by `snapshot`/`restore` and returned to `0.0` by `reset`;
- ONE verb moves it — `move('time', by=)` / `to=` — under the same
  one-moving-input rule, with seconds as both design and native unit, so no
  conversion happens anywhere (`clocked.py:1617-1644`, `_ClockInput`);
- **time never reverses**: a negative travel, or a `to=` behind the banked
  instant, is REFUSED BY NAME naming both instants — a refusal and not a
  stop, because no bound was met (`clocked.py:2068-2082`). **Zero is
  admitted**, fires nothing and poses what already stands;
- an event on the clock IS an event: one solver, one landing rule, one
  ordering, one conflict rule, no new tolerance. `_CROSSING_TOLERANCE`
  appears nowhere in `clocked.py`;
- **nothing stops a clock.** Constraint plans are compiled per DECLARED
  DRIVER (`clocked.py:1422`, `for input_id in sorted(drivers)`), so the clip
  finds nothing for the clock — and ADR-127 states that as a PROMISE rather
  than leaving it an accident, because a declared range is a MECHANICAL stop
  (ADR-108) and nothing is in the way of the next second. ADR-126's
  END-OF-REQUEST judgement is untouched;
- **a compiled chain may not follow the clock**: any free name surviving a
  composed chain that is not a bank id (`$own` aside) is refused at
  simulation construction (`clocked.py:1448-1487`), and the clocked bank is
  the drivers and the states and NOT the clock (`compile_bounds`,
  `clocked.py:1368-1377`);
- ADR-128 §10 publishes it: `clocked.clock` is `"time"` under the elapsed
  base and `null` otherwise, and the document carries the free name `time`
  wherever the model reads the clock — `$t` is a separate 0..1 animation
  variable and is not seconds (`solid_node/core/serializer.py:240-290`).

**Where the viewer stands.** Cycle 5 banks the clock at zero
(`document.ts:288-302`), poses from it, admits a commit `shapes` entry naming
it (`document.ts:562-566`), shows it as a follow-only readout
(`clockedControls.ts:228, 236-240`) — and refuses the one gesture
(`machine.ts:281-292`). The corpus's three clock machines are a stated
DEPARTURE and five downstream steps are deferred, pinned as `76 = 68 + 3 + 5`
(`clocked-corpus.test.ts:110-134, 183-247, 365-405`). ADR-062's closing line:
"**What is left to the next cycle**: the CLOCK — a request that advances
elapsed seconds, the events on it, and the playback of an elapsed base."

**The three corpus machines that declare a clock**, read off the file:

| machine | steps | what it pins |
| --- | --- | --- |
| `Regulator` | 5 | `move('time', by=5)` → five events, first landing `0.49999999999999994`; `snapshot`; `move('time', by=-1)` → `ValueError` naming `time`; `move('time', by=0)` → admitted `0.0`, no commits; `restore` |
| `ClockAlone` | 1 | a relation NO driver can move — `(time, count) commits count` — three events on `by=3` |
| `Lift` | 2 | a time request of `4.0` on a machine with TWO compiled bounds, admitted WHOLE with no stop; then an ordinary CLIPPED driver move (`lift` by 12 → admitted 9, high stop at fraction 0.75) |

`Lift` is the machine that proves "nothing stops a clock" against a machine
that really does declare stops, and it proves it in the same script as an
ordinary clip. Nothing else in the corpus moves a clock.

## Goals / Non-Goals

**Goals:**

1. Execute a request that moves the clock, bit-for-bit as `clocked.py` does.
2. Close the census: **76 of 76 steps, 722 of 722 numbers**, replayed with
   `toBe` and the file's own `tolerance.float`, with no departure and no
   deferral left.
3. Give a maker a way to RUN an elapsed clocked machine in the page, at a
   cost the frame budget can afford, with the numbers printed.
4. Mirror the producer's guard against a stop that follows the clock, so a
   document the producer could not have written is refused rather than
   executed.
5. Leave versions 1–7, the run, the worker, the capture and the framework
   exactly as they are.

**Non-Goals:**

- **An instruction with meaning.** ADR-128 §14 publishes the table and gives
  it none; it stays listed and disabled.
- **A cadence for the drivers.** `step()` and `rate()` stay refused by name:
  a clocked driver request is one gesture, one solve, one pose. The clock's
  transport is a clock, not a tick.
- **A time request that is CLIPPED.** ADR-127 decided against it explicitly,
  and ADR-127's own consequences record the later cycle that would take it
  (its first task being to settle ADR-126's contested direction test for a
  level PERIODIC in time). Nothing here anticipates that.
- **A multi-input request** moving a driver and the clock together
  (ADR-125's narrowing).
- **The Curta project migration**, and any change to the framework, to
  another checkout or to the document's shape.
- **The shop's floor and hub.** How the studio presents a clocked machine's
  transport is the shop's own follow-up; this cycle changes the widget and
  the handle it hands a host.
- **The PRIMARY checkout's bundle.** The tasks rebuild the WORKTREE's bundle
  only; the primary's rebuild belongs to integration and is the
  orchestrator's.

## Decisions

### 1. The clock is the moving input, and the request path is the one that exists

`machine.ts`'s `move` already builds a straight path from `bank[inputId]`,
clips it, locates events on it, commits and poses. The clock joins it as one
more `inputId`:

- `declarationOf` already answers for the clock with a driver-shaped
  declaration — `{default: 0, range: null, unit: 's', dtype: null, scale:
  null}` (`machine.ts:136-140`) — which is `_ClockInput` field for field
  (`clocked.py:1629-1636`). `native()` is therefore the identity and `scale`
  is `null`, so `by`, `to` and `admitted` are all plain seconds. **No
  conversion is added anywhere**, and that is a decision: a clock with a
  `scale` would make `admitted` and `by` speak different units in the one
  place a maker reads them side by side.
- `eventOn` already selects relations by `relation.jumps.has(inputId)`
  (`machine.ts:172`), and a commit's published `shapes` may name the clock
  (`document.ts:562-566`), so `Regulator`'s single relation is examined for
  `time` and `Lift`'s is too. Nothing in the solve is clock-aware.
- The eleven lines of `machine.ts:281-292` are DELETED and replaced by the
  backwards check.

**Rejected: a separate `advance(seconds)` verb on the handle.** ADR-127
rejected `sim.advance(seconds)` on the producer side for reasons that apply
here unchanged — it would carry its own return type, ordering rules and
documentation, all copies of `move`'s, and it could not say "advance to
exactly `t = 10`" without a second argument that is `to=` under another name.
The corpus scripts `{"move": {"input": "time", ...}}`, so a second verb would
also make the replay translate.

### 2. Time never reverses, and the check goes exactly where the producer's is

Mirrored from `clocked.py:2064-2082`, in its position: AFTER the by/to
exclusivity refusal and after `target` is computed, BEFORE the clip. The
order is observable — a request stating both `by` and `to` on a backwards
clock must get the exclusivity message, not the reversal one — so it is
mirrored rather than re-derived.

```
move('time', by=-1.0) asks this machine's clock to run BACKWARDS: it
stands at 5.0 seconds and the request ends at 4.0. Elapsed seconds never
wrap and never reverse -- no bound was met and nothing stopped, the
request has no meaning. Restore a snapshot taken at the earlier instant,
or reset the machine, to stand before it again.
```

Kind `ValueError` (`ClockedRequestError`, `document.ts:86-90`), which is what
the corpus records for `Regulator` step 2: `{"kind": "ValueError", "names":
["time"]}`. The replay asserts the kind and that the message CONTAINS each
listed name, never the prose (`clocked-corpus.test.ts:307-313`), so the
wording above is this repository's and the contract is the kind and the name.

**Zero is admitted** and needs no code: `target === origin` makes `clipped`
return immediately, the event loop breaks on `delta === 0`, and `admitted` is
`(target - origin) * 1 === 0`. `Regulator` step 3 records exactly that —
`admitted: 0.0`, no commits, no stops, the bank unchanged — and it is what
keeps `move('time', {to: t})` idempotent.

**Rejected: clamping a backwards request to zero travel.** It reads as
forgiving and it is a lie: a stop reports a bound the machine MET, and no
bound was met. ADR-127 draws that line and the corpus pins it as a refusal.

### 3. Nothing stops a clock — stated, asserted, and guarded at the load

It already falls out: `clip` returns `null` when the constraint publishes no
plan for the moving input (`bounds.ts:207-208`), and a published `bounds`
entry's `shapes` can only name declared drivers because the producer compiles
plans only for them (`clocked.py:1422`). So this cycle writes **no clip code
at all** — and does three things so the behaviour is a promise rather than a
coincidence:

1. **States it** in the spec, with its reason: a declared range is a
   mechanical stop, and nothing is in the way of the next second.
2. **Asserts it on `Lift`**, which declares a clock and two compiled bounds:
   `move('time', by=4)` is admitted WHOLE (4.0, four events, no stops) where
   the very next step's `move('lift', by=12)` is clipped to 9.0 with a high
   stop at fraction 0.75. One script, both behaviours, from the corpus.
3. **Refuses at load** any document that would make it false (§4).

**The END-OF-REQUEST judgement is unchanged and still runs on a time
request.** `judged` (`machine.ts:338-341`) is called for every request and
re-evaluates every constraint over the FINAL bank, so a commit fired by a
time request that carries a bounded coordinate out of its range refuses the
whole request by name with kind `JointRangeError`. **No corpus machine
exercises that on a time request** — the corpus's one `JointRangeError` is
`Shut` step 0, a driver request on a machine with no clock — so it is pinned
by a hand-written document in `machine.test.ts` (a `Regulator`-shaped machine
whose counted dial carries a declared range the count drives past), in the
style cycle 5 already uses there. Said plainly because the alternative is a
spec sentence nothing checks.

### 4. A constraint that follows the clock is refused at load, by name

The producer cannot write one. `compile_bounds` builds its chains over
`set(drivers) | set(states)` and NOT the clock (`clocked.py:1368-1377`), and
`_over_the_bank` refuses any free name that survives a composed chain and is
not a bank id, naming the clock case specifically (`clocked.py:1448-1487`).
That refusal is ADR-127's tightening of a hole ADR-126's implementation left
open, and it was EXECUTED, not merely read: the fixture's first request died
with the bare `KeyError` exactly where it was predicted.

The viewer mirrors half of it today. `readBound` refuses a `shapes` key that
is not a declared driver (`document.ts:753-757`), which already covers the
clock — the message is widened to SAY the clock, since that is the one case a
reader will meet. But a bound's `value`, its `bound` and the level built from
them are checked against `declaredNames` (`document.ts:674-677`), and
`declaredNames` INCLUDES the clock (`document.ts:288-302`). A hand-written or
corrupted document could therefore carry a stop whose chain reads `time`,
load cleanly, and be clipped against a clock-driven coordinate — the exact
shape the producer refuses.

So `readBound` refuses a chain, a bound or a level naming the machine's clock,
by name and with the producer's own reason. This is the `mirror-the-gate-guard`
shape (archived 2026-09-16): a guard the producer states and the consumer
must not be silently wider than. It costs one `Set` difference per compiled
constraint at load and nothing per request.

**Rejected: narrowing `declaredNames` itself.** The clock is a legal name in
a commit's level, in a commit's law and in the tree's own pose expressions —
it is a bank id. The refusal belongs where the fact is: a CONSTRAINT's chain.

### 5. The transport: one request per rendered frame, and no scrub

**How a maker advances an elapsed clocked machine.** A PLAY/PAUSE toggle
beside the clock readout, which — while playing — issues exactly ONE
`move('time', {by})` per rendered frame, for the wall seconds elapsed since
the previous frame times the playback speed. This is the shape the run's
real-time playback already has (`viewer.ts:1352-1377`, `runtime.frame`
at `src/run/runtime.ts:270-296`, ADR-046/048), with the run's own reason: the
render loop drives the CADENCE.

It is the right shape here for a reason of its own. **Each frame is ONE
request, so every event inside that frame is located exactly and in order**,
by the same solver, against the same landings — a long frame is simply a long
request. Sampling instead (posing at `t = k·Δ` without a request) would skip
every event between samples; issuing one request per EVENT would need the
events located first, which is the request. So the frame-sized request is not
a convenience, it is the only shape that keeps the exactness claim while the
clock runs.

Three consequences are decided here rather than discovered later:

- **`max_crossings` applies to a frame.** A long frame is a long request, and
  a request crossing more than `limits.max_crossings` surfaces of one
  relation is refused whole (ADR-125, unchanged). At `Regulator`'s one event
  per second and the ladder's ×3600, a 16 ms frame carries ~58 events and a
  1 s stall would carry 3600 — past the corpus's own limit of 1000. So the
  per-frame advance is **CAPPED**, at four frames' worth of the current speed
  exactly as the run caps its debt (`runtime.ts:286-295`, design D9): wall
  time beyond the cap is LOST, visibly, because the seconds readout falls
  behind the clock on the wall — and losing it is honest where firing a burst
  of 3600 events, or refusing the frame, is not.
- **The fractional remainder is NOT carried.** The run carries a debt because
  its `dt` quantizes what a frame can earn; a clock request has no
  quantization — `by` may be any float — so the frame's own elapsed seconds
  are requested as they are. One fewer piece of state, and `move('time',
  {by})` ten times equals `move('time', {by: 10×})` once, instant for
  instant, which is the property ADR-127 says a tolerance would have cost.
- **A refused frame PAUSES.** Any refusal — `max_crossings`, a two-writer
  conflict, an out-of-range commit — pauses the transport and shows the
  message across the panel, rather than repeating a refused request sixty
  times a second. This is the run's own rule (`viewer.ts:975-981`).

**No scrub, and no reverse.** A timeline slider implies both directions, and
the clock refuses one of them by decision: dragging left would raise a
refusal on every pointer move. A one-way slider that silently ignores half
its travel is worse than no slider. What replaces it is a **STEP**: advance
by a stated number of seconds, one request, with an editable amount — the
shape the driver handles' nudge already has (`clockedControls.ts:169-194`),
minus the minus. A maker who wants to look at an instant steps to it and
snapshots; a maker who wants an earlier instant restores a snapshot, which is
exactly what ADR-127's refusal message tells them.

**Speed** is the existing ladder — `SPEED_LADDER` at `playback.ts:25-26`,
`0.1 … 3600`, whose 360 and 3600 exist for watching a clock — reached through
`ViewerHandle.setSpeed` (`viewer.ts:461-470`), which already refuses a
non-positive or non-finite multiplier and already feeds the run. One meaning
of speed in the widget, for all three kinds of document.

**Pause holds the bank** — no request is issued, so nothing moves. **Reset**
is the one the chrome already offers (`viewer.ts:1074-1081`), which calls
`machine.reset()`: the whole bank to its published defaults, the clock to `0`
(`machine.ts:370-372`, `document.ts:297-299`). It also stops the transport,
because a machine that reset itself while running would be a machine nobody
could read.

**Rejected: a `duration=` on the request**, the shape ADR-127 records as an
open narrowing. It would put the cadence inside the machine, where the whole
clocked discipline's point is that there is none; the cadence belongs to the
page, which is where the frames are.

### 6. `$t` and the clock are two controls, and usually only one of them exists

ADR-128 §10: under the elapsed base the document carries the free name
`time` wherever the model reads the clock, and `$t` is a 0..1 animation
variable that is not seconds. The producer binds `time` symbolically for
every assembly that holds a snapshot (`serializer.py:282-290`), so an elapsed
clocked document's expressions read `time` — and `tree.animated` is true only
where something reads `$t` (`tree.ts:553-561`). **For the ordinary elapsed
clocked document `animated` is false, `controlPlan` returns no bar
(`options.ts:217-224`) and no timeline chrome is built at all
(`viewer.ts:1126-1152`)**: the clock transport is the only transport such a
document has, and there is nothing for a maker to confuse it with.

Where a document does carry both — a `$t` operation somewhere alongside a
clocked machine with a clock — the two controls are independent and each says
what it advances: the timeline plays `$t` over its `frames`, the transport
advances the machine's seconds, and neither touches the other's value. The
pose reads both through one scope (`clockedScope`, `run/pose.ts:48-55`), so a
frame in which both moved re-evaluates once. Under `clocked.clock: null` this
cycle changes nothing at all: the timeline is presented exactly as cycle 5
ships it and the transport is absent.

### 7. The handle grows two verbs, and `step()` stays refused

`MachineHandle` is `ClockedMachine` today (`viewer.ts:166`), which is the pure
library — no DOM, no frames. The transport is a page concern, so `machine()`
returns the library WRAPPED:

```ts
export interface MachineHandle extends ClockedMachine {
  clockPlaying(): boolean;
  setClockPlaying(playing: boolean): void;
}
```

Two verbs and no more. A host that wants a single frame's worth calls
`move(machine.clock()!, {by})`, which it already can. **They are NOT named
`play`/`step`**: `step()` is an existing member of `ClockedMachine` that
refuses by name — a clocked machine has no tick — and reusing the word for
the clock would make one handle answer two meanings for it.

`setClockPlaying(true)` on a machine whose `clock()` is `null` is refused by
name: there is nothing to run. `clockPlaying()` is `false` for such a machine
and needs no guard.

**The pure/impure line is kept.** The per-frame arithmetic — elapsed × speed,
the cap — goes in a new pure module `src/clocked/clock.ts`, decided and
tested in node exactly as `playback.ts` and `clockedControls.ts` are, and
`viewer.ts` renders and calls. Nothing about the frame loop is decided inside
`machine.ts`, which stays the corpus's own library.

### 8. The API version rises to 18; `documentVersions` does not move

The rule: the declared version rises "whenever the mount interface or handle
changes incompatibly, and when a capability a host may require is added"
(`viewer-package`, "The viewer declares its API version").

Both halves apply. The handle gains two members, and — more to the point — a
host that means to present an elapsed clocked machine that RUNS cannot tell a
build that runs it from one that refuses every clock request: both mount the
same version 8 document, both render it truthfully at its initial bank, and
only a request distinguishes them. That is precisely the case the version
exists to answer without trying. The precedent is cycle 5's own 16 → 17 (a
new executing capability with a new control surface) and ADR-057's 14 → 15.

`solidNodeDocumentVersions` stays `[1 … 8]`: no new document shape is read,
and `RELEASED_DOCUMENT_VERSIONS` (`bundle.py:56-62`) does not move. The two
declarations are independent by design and this cycle is the clean case that
shows it — a capability gate moving while the schema list stands still.

### 9. What is measured, against what

The claim to falsify is that **a played frame fits in the frame budget**.
Printed by the tests themselves, three runs each, as cycle 5 printed its own:

- **In thread** (`src/clocked/cost.test.ts`): one frame-sized request on
  `Regulator` at ×1 (one event per second, so a 16 ms frame carries none or
  one), at ×60 and at ×3600 — the last being the many-events-per-second case,
  ~58 events in one 16 ms frame. **No corpus machine has a faster release
  than `Regulator`'s, and none is added**: the corpus is the framework's, and
  the speed ladder supplies the event rate without inventing a machine the
  producer never generated. Also the per-EVENT cost, which is the number that
  scales.
- **In a real page** (`tests/test_regulator_document.py`, Chromium): a played
  second at ×1 and at ×60 on the exported fixture, SOLVE AND POSE, asserted
  under one 16 ms budget — the same falsifiable form cycle 5 used
  (`tests/test_calculator_document.py:390-399`).
- **The whole-corpus replay**, against cycle 5's recorded **13.6 ms for 68
  steps**; this cycle replays 76.

The cap of §5 is what keeps the first claim true under a stall, and the test
asserts the cap rather than hoping: a frame reporting 10 s of wall time
advances the clock by the cap, not by 10 s × speed.

**What the comparison is NOT**, printed in the test as cycle 5 prints its
own: nothing here is compared to the running Curta. A clock request is not a
tick and `Regulator` is not the Curta, which has no clock at all (ADR-127's
own note: "the Curta does not owe this cycle and this cycle costs it
nothing").

### 10. The acceptance fixture is `Regulator`, exported verbatim

The corpus's documents carry no `root` and no `animation`: they are machines,
not pages. So the page evidence needs an export, exactly as cycle 5's
`tests/fixtures/calculator/` is one.

`tests/clocked_project/pendulum.py:Regulator` is the right one and it already
exists: `time = Time.elapsed()`, one driver `engaged`, one state `count`, one
committing relation on the clock, and GEOMETRY — a `Bob` on a revolute joint
posed by `self.bob.swing = A·sin(360·self.time/T)` with `T = 2.0 s` and
`A = 12°`. Under the elapsed base that `self.time` publishes as the free name
`time`, so the bob's placement is an expression over the BANK: playing the
clock swings it, which is a thing a person can see.

Produced the way cycle 5 produced its fixture — `solid export … --no-widget`
from a THROWAWAY COPY of solid-node at branch `clocked-machine` head
`1a959d3`, never writing the read-only worktree and never touching the
pilot's primary checkout — with the file renamed to `viewer.json` and nothing
else done to it. Its `clocked.identity` will differ from the corpus's for
ADR-062's finding F2 (the identity opens with the class's MODULE PATH); the
fixture's README records both strings, as the calculator's does, and the
fixture is never replayed against corpus numbers.

In Chromium: it opens at `t = 0` with `count = 0`; play for one wall second
at ×1 advances the readout by ≈1 s and the count by ≈1 (a release every
`T/2 = 1 s`); pause holds both; a 2 s STEP advances the count by exactly 2;
reset returns the bob to rest, the clock to `0` and the count to `0`; and the
bob's transform differs between two instants, so the pose is really following
the bank. Two screenshots kept as evidence.

### 11. The corpus closes, and the census must stay derived

Deleted: the departure branch and the deferral branch of the replay
(`clocked-corpus.test.ts:365-405`), and the `departureAt`/`clockMoves`
helpers they exist for. Every machine replays step by step through
`replayStep`, `Regulator`'s recorded `ValueError` matched by the ordinary
refusal path that already exists (`:298-314`).

The census stays and stays DERIVED — it is what makes a regenerated corpus
loud. It becomes: 30 machines, **76 steps, 76 replayed, 0 departed, 0
deferred**, **722 of 722 numbers**, and the three clock machines still named
OFF THE FILE (a `move` whose input is that machine's own `clocked.clock`) —
now as the machines this build must EXECUTE rather than depart from. The two
"derived from the file" tests (`:263-289`) are kept as they are: they prove
the census reads the file, and they are the guard against a later cycle
quietly narrowing the suite.

The exactness tests (`:406-448`) are untouched, and one is ADDED in their
shape: `Regulator`'s first landing `0.49999999999999994` moved by ONE
representable value must turn the replay red. That value is the strangest
number in the file and the one a reader is most tempted to "fix" to `0.5`.

### 12. `solid develop`, the studio and the capture need nothing

- **The develop page** reloads a version 8 document as any other (cycle 5);
  the transport is inside the widget and needs no hook. One behaviour is
  stated rather than left to be discovered: a republish rebuilds the machine
  at its INITIAL bank (`viewer.ts:1089-1099`, `startMachine`) and therefore
  stops the clock and returns it to `0`, exactly as it restarts a run. A
  maker watching a pendulum while editing its model sees it go back to
  `t = 0` on every rebuild, which is the truth about what was rebuilt.
- **The capture** photographs a staged document at an instant and never
  plays: cycle 5's split of `carries_clocked` / `carries_program` /
  `animates_time` (`capture.py:59-90`) is exactly right for an elapsed
  document too — it is photographed at its INITIAL bank, and `--time` still
  addresses `$t`. **No `snapshot-capture` delta.**
- **The shop** is not touched. How the floor presents the transport is its
  own follow-up.

### 13. What is asserted UNCHANGED

- Versions 1–7 load, pose, animate, drive and run exactly as they do;
  `run()` stays `null` for a version 8 document and `machine()` stays `null`
  for every other.
- The run's worker, its protocol, its playback and `running-corpus.json` —
  not one line of `src/run/run.ts`, `worker.ts`, `runtime.ts` or `jumps.ts`
  changes, asserted by diff.
- `RELEASED_DOCUMENT_VERSIONS`, `solidNodeDocumentVersions`, the published
  names (`solid-widget.js`, `data-solid-widget`, `SolidNodeWidget`,
  `/_viewer`, `/build/`), and the framework contract
  (`solid-node-viewer describe|serve|capture`).
- A machine with `clock: null` behaves in every respect as it does today,
  including `move('time', …)` meeting the ordinary undeclared-input refusal
  (`machine.ts:151-156`) — ADR-062's finding F7, deliberately kept.

## Risks / Trade-offs

- **A corpus landing disagrees.** → It is a bug at the operation, never a
  tolerance to widen, a fixture to edit or a scenario to skip. The three
  clock machines' levels are `floor((time + 0.5) / 1.0)` — affine, solved by
  one division — so a disagreement is in `farSideOf`'s ordinal walk or in the
  division, both of which already replay 68 steps of driver requests. If an
  operation genuinely cannot agree: STOP and report, per the campaign's rule.
- **A stall fires a burst of events.** → The per-frame cap (§5), asserted by
  a test that hands the frame hook 10 s of wall time. The trade-off is
  visible lost time, chosen over a burst or a refusal.
- **`max_crossings` refuses a played frame at a high speed on a machine with
  a fast release.** → It is the machine's own published limit and the refusal
  pauses with its message, which names the split. Recorded as a limit rather
  than worked around; a maker's remedy is a lower speed.
- **The cost floors are load-sensitive**, as ADR-062 records for cycle 5's
  (one transient failure in six runs, unreproduced). → The numbers stay at
  the design's own ratified floors rather than being quietly widened, and the
  evidence says which assertions can be made to fail by load alone.
- **The export of `Regulator` might refuse or warn.** → A warning is
  expected and is ADR-128 §15 working (cycle 5's fixture carries one). A
  REFUSAL is a finding to report, not a fixture to hand-edit: nothing in
  `tests/fixtures/` is ever written by hand.
- **One host process at a time on this box** (virtiofs; EMFILE means wait).
  The Chromium acceptance and a full vitest run are not started together.

## Migration Plan

No migration. A host at API 17 keeps working against every document it
already reads; a host that requires the clock reads `18` from the same one
declaration it already reads 17 from (`package.json`,
`bundle.describe`). Rollback is the branch.

## Open Questions

1. **Does the transport belong in the studio's own chrome?** The widget's
   transport is the viewer's; whether the shop's floor presents its own is
   the shop's follow-up and is deliberately not decided here.
2. **Should a played frame at a refusing speed suggest the speed to drop
   to?** The refusal names the split; computing the largest admissible speed
   would need the event rate, which the machine does not publish. Left as it
   is, recorded.
