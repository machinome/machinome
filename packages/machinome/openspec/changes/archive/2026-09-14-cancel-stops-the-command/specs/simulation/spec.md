## MODIFIED Requirements

### Requirement: Commands have one owner per input and report their outcome

Under a running root the system SHALL provide one path for every
movement request: `move(input, by=..., duration=...)`,
`move(input, to=..., duration=...)`, `rate(input, rate)` and
`trigger(name)`. `input` SHALL be the qualified id of a declared driver;
naming anything else — a joint coordinate, an unknown id — SHALL be
refused naming the id and the declared inputs. `by`, `to` and `rate` are
stated in the input's DESIGN units and converted through its declared
scale once; `rate` is design units per simulated second; `duration` is a
whole number of ticks, zero included. Exactly one of `by`/`to` SHALL be
given.

Each input SHALL have ONE OWNER at a time: a move or a rate on an input
that an active move or rate already owns SHALL be refused naming the
input and the owning command. `rate(input, 0)` SHALL release the active
rate, completing it, and SHALL be a no-op on an input no rate owns. A
REVERSE request — negative `by`, a `to` below the committed value, a
negative `rate` — SHALL be admitted and SHALL meet a declared range as
a physical stop exactly as a forward request does.

`move` and `rate` SHALL return a HANDLE reporting the input, the kind,
the status — `active`, `completed`, `blocked`, `refused` or `cancelled`
— the travel requested and the travel actually ADMITTED so far, in
design units, and offering `cancel()`. A request that fails validation SHALL
raise rather than return a handle; `refused` is the status of a command
whose tick failed, and `blocked` the status of one whose input was
stopped. Per-tick admission SHALL be a pure function of the
tick count since the command started: a move distributes its travel as
the ramp program does, integer-exact for an integer input and landing
exactly, in either direction; a rate admits the difference of its
cumulative travel at successive ticks, TRUNCATED TOWARD ZERO for an
integer input so that the two directions round alike. A zero-duration move
SHALL integrate at once at the current tick without advancing it.
A command whose input is STOPPED SHALL be retired reporting `blocked`,
with the travel it actually admitted — every completed tick's travel
plus the fraction of the stopping tick's travel it made before the
stop — and SHALL NOT resume: no travel it did not make is remembered
anywhere, and a later tick SHALL NOT continue it. A `rate` on a stopped
input SHALL be retired `blocked` in the same way. A new request on that
input SHALL be accepted at once, and SHALL be blocked again with `0`
admitted if it pushes into the same stop. A request that lands EXACTLY
on a bound SHALL report `completed`, the bounds being inclusive. Where
one instruction names several inputs, EACH command SHALL report for
itself and no instruction-level summary SHALL be owed: an instruction
one of whose inputs is stopped reports that handle `blocked` and the
others by their own outcome.

`cancel()` on a handle SHALL STOP that command where it stands. The
command SHALL be RETIRED at once, reporting `cancelled` with the travel
it had actually admitted; its input SHALL be free from the moment
`cancel()` returns, so a move or a rate on that input SHALL be accepted
at the same tick with no tick passing in between; and it SHALL admit
nothing further — every tick from the next one on admits nothing for it,
and no travel it did not make is remembered anywhere, the rule a
`blocked` command already states. This SHALL hold wherever the command
stands: before its first tick, part way through a move, and on a rate,
which has no end of its own. `cancel()` SHALL return the handle.
`cancel()` on a command ALREADY RETIRED — `completed`, `blocked`,
`refused` or `cancelled` — SHALL preserve what that handle reported and
SHALL NOT touch whatever command owns its input now, so cancelling twice
is cancelling once. Cancelling one command SHALL leave every other
command running, the sibling commands of one instruction included.
Cancellation is a caller's action AT A TICK and never a wall-clock
event: per-tick admission stays a pure function of the tick count since
the command started, so a script replayed with the same requests,
cancellations and steps in the same order SHALL admit exactly the same
travel.

`sim.commands` SHALL be the active handles; a command SHALL be RETIRED
from them the tick it completes, blocks or is refused, and the moment it
is cancelled, so a long run
accumulates no finished
commands, while the handle the caller holds keeps reporting.

#### Scenario: A rate and a move on one input are an ownership conflict

- **WHEN** `rate('crank', 90.0)` is active and `move('crank', by=10, duration=1.0)`
  is requested, or two moves are requested on `crank`
- **THEN** the second request is refused naming `crank` and the owning
  command, and the first command keeps running

#### Scenario: A rate accumulates until released

- **WHEN** `rate('crank', 90.0)` runs for two seconds and `rate('crank', 0)`
  is then called
- **THEN** the crank has moved `180` and its joints followed, the handle
  reports `completed` with `180` admitted, and `sim.commands` is empty

#### Scenario: A reverse move runs

- **WHEN** `move('crank', by=-10, duration=1.0)`, `move('crank', to=5, duration=1.0)`
  from `20`, or `rate('crank', -90.0)` is requested on a crank meeting no
  stop
- **THEN** each runs, the bank and the driven coordinates follow
  backwards through the same laws, and each handle reports `completed`
  with its travel admitted

#### Scenario: A blocked command does not resume and reports its travel

- **WHEN** a move whose input is stopped part way through a tick is
  followed by ten more ticks with no new command
- **THEN** the handle reports `blocked` with the travel made up to the
  stop, `sim.commands` is empty, the coordinate stands at its bound
  through all ten ticks, and a new move on that input is accepted at once

#### Scenario: An instruction naming two inputs reports each for itself

- **WHEN** an instruction moves a stopped input and a free one over the
  same duration
- **THEN** its handle tuple holds one `blocked` handle with the fraction
  of its travel it made and one `completed` handle with all of its own,
  and the free input was not held back

#### Scenario: Only a declared input can be moved

- **WHEN** `move('first.turn', by=10, duration=1.0)` names a joint
  coordinate
- **THEN** it is refused naming `first.turn` and listing the declared
  inputs

#### Scenario: Completed commands are retired

- **WHEN** one hundred single-tick moves are issued one after another,
  each after the previous completed
- **THEN** `sim.commands` never holds more than one entry, every handle
  reports `completed`, and the crank has moved the sum of the travels

#### Scenario: A zero-duration move integrates now

- **WHEN** `move('crank', by=10, duration=0)` is requested at tick 20
- **THEN** the bank and the tree reflect the move at tick 20, the handle
  reports `completed`, and no tick was added

#### Scenario: A failed tick retires its commands as refused

- **WHEN** a move's tick is refused as a conflict
- **THEN** the handle reports `refused` with the travel admitted before
  that tick, `sim.commands` no longer holds it, and the run continues from
  the last committed bank once a consistent command is issued

#### Scenario: A move cancelled before its first tick moves nothing

- **WHEN** `move('feed', by=5, duration=0.2)` is cancelled at the tick it
  was issued on, at `dt=0.02`, and the simulation is then stepped one
  tick
- **THEN** the handle reports `cancelled` with `0` admitted, the input
  and every coordinate it drives stand where they stood, and
  `sim.commands` is empty

#### Scenario: A move cancelled part way keeps the travel it made

- **WHEN** a ten-tick `move('feed', by=5, duration=0.2)` is stepped three
  ticks, cancelled, and the simulation is stepped seven more
- **THEN** the handle reports `cancelled` with the travel of those three
  ticks, the bank stands at that travel through all seven remaining
  ticks, and `sim.commands` is empty

#### Scenario: A cancelled rate stops

- **WHEN** `rate('feed', 10)` is stepped three ticks, cancelled, and the
  simulation is stepped three more
- **THEN** the handle reports `cancelled` with the travel of those three
  ticks and the input does not move again

#### Scenario: A cancelled command's input takes a replacement at once

- **WHEN** a move is cancelled and a new `move` on the same input is
  requested before any tick is stepped
- **THEN** the request is accepted, the new handle is the input's only
  entry in `sim.commands`, and it runs from the bank as the cancelled
  command left it

#### Scenario: Cancelling twice is cancelling once

- **WHEN** a handle is cancelled, a replacement command is issued on the
  same input, and the first handle is cancelled again
- **THEN** the first handle still reports `cancelled` with what it had
  admitted, and the replacement is still active, still owns the input
  and goes on running

#### Scenario: A retired handle keeps what it reported

- **WHEN** `cancel()` is called on a handle that already reports
  `completed`, `blocked` or `refused`
- **THEN** the handle keeps that status and its admitted travel, and
  `sim.commands` is unchanged

#### Scenario: Cancelling one command leaves the others running

- **WHEN** an instruction issues commands on two inputs over the same
  duration and one of the two handles is cancelled
- **THEN** that input stops where it stands and the other command runs
  to `completed` with all of its own travel admitted

#### Scenario: A cancelled run replays identically

- **WHEN** the same machine is stepped twice with the same requests,
  cancellations and steps in the same order
- **THEN** the bank, the tick and every handle's status and admitted
  travel are equal at every step

### Requirement: Snapshot, restore and reset act on the run's bank

Under a running root `sim.snapshot()` SHALL return a VALUE OBJECT holding
the compiled program's identity, `dt`, the tick, the whole bank and the
active commands with their progress; two snapshots of one state SHALL
compare equal. `sim.restore(snapshot)` SHALL compare the program identity
and `dt` FIRST and refuse a mismatch naming both, touching nothing; it
SHALL then replace the bank, the tick and the active commands, clear the
recording, and bind the restored bank to the tree. Handles issued before a
restore SHALL report `cancelled` with what they had admitted; the restored
commands SHALL be reachable through `sim.commands` and continue from their
recorded progress. `sim.initial` SHALL be the snapshot taken at
construction and `sim.reset()` SHALL be `restore(sim.initial)`.

#### Scenario: A snapshot restores mid-run

- **WHEN** a simulation runs five ticks of a ten-tick move, takes a
  snapshot, runs the remaining five, restores the snapshot and runs five
  again
- **THEN** after the restore the bank, the tick and the tree equal the
  snapshot's, and after the second five ticks they equal what the first
  completion produced

#### Scenario: A mismatched program or dt is refused before anything changes

- **WHEN** a snapshot taken over a different root class, or over the same
  class at a different `dt`, is restored
- **THEN** the restore is refused naming the two identities or the two
  steps, and the bank, the tick and the commands are unchanged

#### Scenario: Reset returns to the initial snapshot

- **WHEN** a simulation has run and `reset()` is called
- **THEN** `sim.snapshot() == sim.initial`, the tick is zero, the bank is
  the rest pose, no command is active and the recording is empty

#### Scenario: A cancelled command is not in the snapshot

- **WHEN** a move is stepped two ticks, cancelled, and a snapshot is then
  taken and restored after further ticks
- **THEN** the snapshot carries no command, the restore leaves
  `sim.commands` empty, and no further tick moves that input

#### Scenario: A snapshot taken before a cancel re-issues the command

- **WHEN** a snapshot is taken part way through a move, the move is
  cancelled, and the snapshot is restored
- **THEN** the cancelled handle still reports `cancelled` with what it
  had admitted, `sim.commands` holds a fresh active command for that
  input continuing from the recorded progress, and stepping on moves the
  input again
