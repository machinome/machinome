## Context

Under a running root (`Time.running()`, ADR-104…111) every movement of a
declared input goes through a COMMAND. `Run.move`, `Run.rate` and
`Run.trigger` claim the input through `Run._claim`, construct a
`Command`, put it in `Run.active` under the input's qualified id, and
return it as the caller's handle. Each tick, `Run.integrate` asks every
command in `active` for its admission — `Command.admits(tick, dt)`, a
pure function of the tick count since the command started — integrates
them over the compiled program, commits, and then RETIRES whatever
finished.

Retirement already exists in four shapes, and every one of them is the
same two steps — set the status, remove the command from `active`:

| where | word | trigger |
| --- | --- | --- |
| `Run.integrate` end | `completed` | `Command.finished(tick)` |
| `Run.rate(input, 0)` | `completed` | the caller releases a rate |
| `Run._block` | `blocked` | the input was stopped at a bound |
| `Run._refuse` | `refused` | the tick failed and committed nothing |
| `Run.restore` | `cancelled` | a snapshot replaces the command set |

Those five sites give the run its invariant: a command's status is
`active` exactly while it is the entry in `Run.active` for its input.
`_claim` depends on it — it refuses any entry in `active`, whatever its
status — and so does `sim.commands`, which is `active`'s values, and so
does `snapshot()`, which records them.

`Command.cancel()` is the sixth site and the only one that breaks the
invariant. It sets `self.status = 'cancelled'` and stops: the command
stays in `active`, keeps admitting travel every tick (`admits` knows
nothing about the status), keeps owning its input, and is recorded by
`snapshot()` as an active command — so a restore constructs it again and
it goes on moving (`evidence.md`, probe 10). A cancelled command is not
even reported as active by its own handle, so `sim.commands` disagrees
with every handle in it.

`Command` cannot fix this alone: it is a value-like handle with
`__slots__` and no way back to the run that holds it. That is the whole
of the mechanism this change has to choose.

The originating project is `projects/Locks/Pin_tumbler_lock`; the
reproduction is `workflow/warts.md`'s and is run against this worktree in
`evidence.md`.

## Goals / Non-Goals

**Goals:**

- `handle.cancel()` stops the command where it stands, keeping its
  signature, its return and its status word.
- The input is free the moment `cancel()` returns, so a replacement is
  issued at the same tick.
- The handle goes on reporting `cancelled` with the travel it did admit;
  the travel it did not make is remembered nowhere.
- The run's invariant — `active` status exactly while in `Run.active` —
  holds through cancellation, so `sim.commands`, `_claim` and
  `snapshot()` agree again.
- Replay stays deterministic: cancelling is an action at a tick, not a
  wall-clock event.

**Non-Goals:**

- No new public name. No `sim.cancel(input)`, no `cancel_all()`, no
  `Command.active` predicate, no change to `move`, `rate`, `trigger`,
  `snapshot`, `restore` or `reset` signatures.
- No change to what `completed`, `blocked` or `refused` mean, and none to
  `rate(input, 0)`, which keeps completing a rate rather than cancelling
  it.
- No change to admission arithmetic, to stop localization, to the
  compiled program, to the published document or its version, or to
  `program.identity`.
- No new script action in `tests/running-corpus.json` and no new entry in
  `tools/generate_running_corpus.py`'s `REQUIRED` (decision 6).
- No partial-tick cancellation: there is no point inside a tick at which
  a caller can run, and none is invented.

## Decisions

### 1. Cancellation is a retirement, not a flag

A cancelled command is retired exactly as a blocked one is: status set,
entry removed from `Run.active`. Everything the proposal promises follows
from that one act — `sim.commands` drops it, `_claim` accepts a
replacement, `integrate` never asks it for an admission again because it
only iterates `active`, and `snapshot()` stops recording it.

*Alternative rejected — a cancelled flag consulted by `admits` and
`_claim`:* leave the command in `active`, teach `Command.admits` to
return `0` when cancelled, and teach `_claim` to treat a cancelled owner
as no owner. It needs three edits instead of one, leaves `sim.commands`
reporting a command that is not active (which is what it means), leaves
`snapshot()` recording a dead command, and leaves the run with two
distinct notions of "owns this input". The status word would be doing
control-flow work that the `active` dict already does for every other
outcome.

Removing an entry from `active` is safe from every place a caller can
run. `Sim.run` fires an `at()` action and an `every()` slot AFTER
`Run.advance()` has returned, never inside it, so no callback can cancel
while `integrate` is iterating `self.active` — which is also why there is
no partial-tick cancellation to define.

*Alternative rejected — sweeping cancelled commands at the start of the
next tick:* the input would stay owned until a tick passed, so the
replacement the wart asks for would still be refused; the whole point of
the finding is the immediate replacement.

### 2. The handle retires itself through a reference to its run

`Command` gains one slot holding the `Run` that issued it, set wherever a
command ENTERS `active` — `Run.move`, `Run.rate` and the reconstruction
in `Run.restore` — and never carried in `Command.record()`, which stays
the eight-field tuple a `RunSnapshot` compares by value.
`Command.cancel()` asks that run to retire it, and the run — the only
object that knows `active` — does the work.

The reference is DROPPED when the command is retired, by whatever word.
So a handle a caller keeps for its numbers after the run is finished
holds nothing but its own numbers, and `cancel()` on a retired handle has
nothing to call, which is the same no-op as its status test. While a
command IS active, the reference is a cycle with `Run.active`, which
already holds the command; it therefore adds no lifetime that
`Run.active` did not already create, and Python's collector handles
cycles.

*Alternative rejected — a weak reference:* it would make `cancel()`'s
behaviour depend on whether the garbage collector had run, which is not a
contract anybody can state.

*Alternative rejected — `sim.cancel(handle)` or `sim.cancel(input)`:* a
new public name for something the ratified interface already offers on
the handle, and the spec's sentence "offering `cancel()`" would still be
unmet.

*Alternative rejected — a callback stored on the command
(`self._retire = run._retire`):* a bound method is the same reference
with a name that hides what it points at, and it cannot be cleared
without the same bookkeeping.

### 3. One retirement path, six callers

The five existing retirement sites and `cancel()` all do the same two
steps, and one of them (`restore`) already uses the very word this change
is about. They become one small `Run` method — set the status, pop the
entry from `active`, drop the command's reference to the run — called by
`_block` with `blocked`, `_refuse` with `refused`, the end of `integrate`
and `rate(input, 0)` with `completed`, `restore` with `cancelled`, and
`cancel()` with `cancelled`. Each keeps its own word and its own reason;
what they stop doing is each spelling the invariant out again.

This is the smallest change that makes the invariant enforceable in one
place rather than asserted in six, and it is what lets the reference of
decision 2 be dropped everywhere without adding a line to each site.

*Alternative rejected — touch only `cancel()`:* it would leave five
copies of the two steps and one new copy, and the reference of decision 2
would leak on every other retirement.

### 4. Cancelling is idempotent and never reaches past its own command

`cancel()` tests the status first, as it does today: only an `active`
command is retired. A handle reporting `completed`, `blocked`, `refused`
or `cancelled` keeps exactly what it reported.

This matters beyond tidiness. Between a cancel and a second cancel a
caller may have issued a REPLACEMENT on the same input, and that
replacement is now the entry in `active`. A `cancel()` that popped by
input id rather than by identity would retire the innocent replacement.
So the retirement removes the entry only when it IS this command —
`active.get(input) is self` — and the status test makes that test
redundant rather than load-bearing. Both are cheap; both are kept,
because the invariant is what the rest of the run trusts.

### 5. `cancel()` does not consult `_owns()`

`Run._owns()` refuses to act when another `Sim` has taken the tree over.
`cancel()` binds nothing, moves nothing and reads no coordinate: it edits
the run's own bookkeeping. Refusing it on a released run would leave a
caller no way to tidy up a run it can no longer step, and `move` and
`rate` do not consult `_owns()` either — the check belongs to `bind` and
to the tick.

### 6. The conformance corpus is left alone

`tests/running-corpus.json` is the cross-runtime contract: the framework
writes it from its own run and the browser viewer's worker replays the
same file (ADR-111). Its script vocabulary is `move`, `rate`, `trigger`,
`snapshot`, `restore` — there is no `cancel` action, and
`tools/generate_running_corpus.py`'s `REQUIRED` inventory does not name
cancellation, so the fixture as it stands stays valid and the generator
keeps refusing to narrow it.

Adding a `cancel` action would pin a behaviour on the viewer's worker
that no viewer cycle has been asked for, and would break the shipped
worker against a fixture it cannot script. The corpus is therefore
untouched, and determinism is proved where it belongs for a
Python-side caller action: by replaying the same script twice in the
framework's own tests (the spec's "A cancelled run replays identically").
Whether the viewer's own run implementation has the same defect is a
question for that repository; it is recorded as an open question below
rather than answered here.

### 7. What restore does is unchanged, and now consistent

`restore()` already retires every pre-restore active command reporting
`cancelled`, and empties `active` — the one place in the code that
cancels correctly. It keeps that behaviour, through the shared path of
decision 3.

Two consequences follow from decision 1 and are worth stating because
today's behaviour differs:

- a snapshot taken AFTER a cancel no longer carries the cancelled
  command, so restoring it cannot resurrect a command that goes on
  moving (today it does: `evidence.md`, probe 10);
- a snapshot taken BEFORE a cancel still carries the command, and
  restoring it re-issues it as a FRESH active handle continuing from the
  recorded progress. That is what restore already means for every
  command, and the cancelled handle the caller holds is a different
  object which keeps reporting `cancelled`. Restoring an earlier state is
  not undoing a cancel; it is putting the whole run back.

### 8. `rate(input, 0)` keeps saying `completed`

A released rate and a cancelled rate now do the same thing to the run,
and the two words stay different because they say different things to the
caller: `rate(input, 0)` is "that is far enough", `cancel()` is "stop,
never mind". Both are already ratified words with these meanings, and
nothing in the finding asks for them to merge.

## Risks / Trade-offs

- **A caller that today cancels a command and expects it to keep running
  gets different behaviour.** → That is the defect being fixed, and the
  old behaviour is unusable by construction: the input could never be
  re-commanded afterwards. No project in the workspace relies on it; the
  shop skill that documents it tells projects NOT to use `cancel()`.
- **The handle holds its run while it is active.** → It is a cycle with
  `Run.active`, which already holds the command, so no lifetime is added;
  the reference is dropped at retirement so a long-lived handle holds
  nothing.
- **A `cancel()` racing a replacement could retire the replacement.** →
  Retirement matches on command identity as well as status (decision 4),
  and a scenario pins it.
- **Six call sites move to one path.** → The other five statuses are
  covered by existing tests (`test_running_simulation.py`,
  `test_running_stops.py`, the corpus replay), which must stay green
  unchanged; the tasks require exactly that.
- **The viewer's own run may keep the defect.** → Out of this
  repository's scope; the corpus is untouched so nothing breaks, and the
  question is recorded below.

## Migration Plan

None. `cancel()` keeps its signature, its return and its status word; no
document, snapshot format, program identity or fixture changes, so a
project upgrades by upgrading. A project that worked around the defect
(by never cancelling, or by restoring a snapshot instead) keeps working;
it may drop the workaround.

## Open Questions

- **Does the browser viewer's run implementation cancel correctly?** The
  viewer repository owns that answer and its own corpus worker. This
  change leaves the fixture alone precisely so the question can be
  answered separately; if the answer is no, that is a viewer cycle.
- **Should `cancel()` on a retired handle be visible at all?** It is
  silent here (returns the handle, changes nothing). A caller that
  cancels something already blocked gets no signal that the cancel did
  nothing. Nothing in the finding asks for a signal, and raising would
  make the idempotent case an error, so silence is proposed — but a
  future `handle.active` predicate would settle it if the pilot wants
  one.
- **Is an ADR owed?** ADR-105 states the handle contract and names
  `cancelled` among the statuses; this change makes the implementation
  match it rather than deciding anything new, so the proposal plans no
  new ADR and a sentence in ADR-105's consequences instead. The
  ADR-extraction step after implementation is where that is confirmed.
