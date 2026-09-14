## Why

`Command.cancel()` does not stop the command. It sets the handle's
status to `cancelled` and nothing else: the command stays in
`Run.active`, `Run.integrate` goes on asking it for admissions,
`Command.admits` does not know it was cancelled, and `Run._claim`
refuses a replacement because the input is still owned. So a cancelled
move keeps moving the machine, and the refusal the caller gets when it
tries to issue a replacement advises it to cancel the command it has
already cancelled:

    ValueError: 'feed' is already owned by <move feed cancelled: 0.5
    admitted>. An input has one owner at a time: cancel that command, or
    release the rate with rate(input, 0), before asking for another.

The originating project is `projects/Locks/Pin_tumbler_lock`, where the
defect was found in a minimal API probe while preparing the lock for
`Time.running()` (`workflow/warts.md`, "Pin tumbler lock (2026-09-14,
running-command cancellation)"). The reproduction is that entry's, run
against this worktree in `evidence.md`: with `dt=0.02`, a 5 mm move over
0.2 s, cancelled before the first tick, still moves the input and its
carriage 0.5 mm on the next tick, still reads as the one entry in
`sim.commands`, and still owns `feed`.

This contradicts what the framework says about itself in three places:
`Command.cancel`'s own docstring ("Stop this command where it stands"),
the requirement "Commands have one owner per input and report their
outcome", which offers `cancel()` as part of the handle and names
`cancelled` as an outcome beside `blocked` and `refused` — both of which
free the input at once — and `_claim`'s refusal message, which tells the
caller to cancel. It is also load-bearing downstream: the shop's public
API skill carries a warning telling projects not to rely on
cancellation, and `sim.snapshot()` records a cancelled command as an
active one, so a restore resurrects it and it goes on moving.

## What Changes

- **A cancelled command is RETIRED, exactly as a blocked or a refused
  one is.** `handle.cancel()` keeps its signature and its return; what
  it now does is retire the command with the status `cancelled`: the
  command leaves `sim.commands`, its input is free the moment `cancel()`
  returns, and it admits nothing from the next tick on. The handle goes
  on reporting `cancelled` with the travel it had actually admitted, and
  nothing anywhere remembers the travel it did not make — the rule
  `blocked` already states.
- **A replacement is accepted immediately.** `move` or `rate` on the
  cancelled command's input, issued at the same tick, is claimed and
  starts from the bank as it stands. No tick has to pass first.
- **Cancelling a retired command does nothing.** A handle that reports
  `completed`, `blocked`, `refused` or `cancelled` keeps what it
  reported; `cancel()` is idempotent and never reclaims an input a newer
  command now owns.
- **Cancelling one command cancels nothing else.** Commands on other
  inputs run on, including the sibling commands an instruction issued in
  the same call.
- **A cancelled command is not in a snapshot.** Because it is no longer
  active, `sim.snapshot()` does not record it and a restore cannot bring
  it back. A snapshot taken BEFORE the cancel still carries the command
  and restoring it re-issues it as a fresh active handle from the
  recorded progress, which is what restore already means; the cancelled
  handle the caller holds is unaffected and keeps reporting `cancelled`.
- **Cancellation is a caller action at a tick, not a wall-clock event.**
  Per-tick admission stays a pure function of the tick count since the
  command started, so a script that issues, steps and cancels in the
  same order admits exactly the same travel every time it is replayed.
- **Nothing else moves.** `rate(input, 0)` still retires a rate
  `completed`; `blocked`, `refused` and `completed` keep their words and
  their meanings; the compiled program, the published document, its
  version, `program.identity` and the conformance corpus are untouched,
  and no new public name is added.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: "Commands have one owner per input and report their
  outcome" states what `cancel()` does — retirement with the status
  `cancelled`, the input released at once, no admission from the next
  tick, idempotent on a retired handle, and no effect on any other
  command; "Snapshot, restore and reset act on the run's bank" gains the
  scenario that a cancelled command is not among the active commands a
  snapshot carries.

## Impact

- `solid_node/simulation/run.py`: `Command` learns the run that holds
  it, so `cancel()` can retire itself through it; the run gains one
  retirement path — status set, command removed from `active`, the
  handle's grip on the run dropped — which `cancel`, `_block`,
  `_refuse`, `rate(input, 0)`, the completion at the end of `integrate`
  and `restore` all use, each keeping its own word.
- `tests/test_running_simulation.py`: the cancellation scenarios, red
  first.
- `docs/architecture.md` (the running-simulation synthesis names the
  three outcomes that retire a command and must name the fourth),
  `docs/scenarios.rst` and `docs/changelog.rst`.
- No change to `solid_node/simulation/program.py`, the serializer, the
  document schema, `tests/running-corpus.json` or
  `tools/generate_running_corpus.py`.
- Outside this repository, and therefore outside this change: the shop's
  `shop-skills/solid-node-api/SKILL.md` carries a warning not to rely on
  `cancel()` which this change makes false, and the browser viewer's
  corpus worker replays the fixture this change leaves alone.
