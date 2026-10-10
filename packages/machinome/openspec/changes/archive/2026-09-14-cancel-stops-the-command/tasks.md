## 1. Red first: what cancellation must do

- [x] 1.1 Record the baseline in `evidence.md`: run
      `tests/test_running_simulation.py tests/test_running_stops.py
      tests/test_running_jumps.py tests/test_running_document.py
      tests/test_running_corpus.py` against this worktree and paste the
      counts, so the "green unchanged" of 2.5 has something to mean.
- [x] 1.2 In `tests/test_running_simulation.py`, a `CancelTest` beside
      `CommandTest`, over the existing `Train` fixture (`crank`, `lever`,
      the two-input `Wind` instruction) and `Ranged` for the blocked
      case — no new machine. One test per spec scenario:
      - a `move('crank', by=10, duration=1.0)` cancelled at the tick it
        was issued on, then one tick stepped: `cancelled`, `0` admitted,
        `sim.state` equal to the pre-move bank, `sim.commands == ()`;
      - a ten-tick move stepped three ticks, cancelled, stepped seven
        more: `cancelled`, the three ticks' travel admitted, the bank
        unchanged from the cancel onwards, `sim.commands == ()`;
      - `rate('crank', 90.0)` stepped, cancelled, stepped again: same
        shape, and `remaining` still `None` for a rate;
      - a replacement `move` on the same input issued immediately after
        the cancel with no tick between: accepted, the only entry in
        `sim.commands`, and running from the bank the cancelled command
        left — assert the resulting bank, not just that no exception was
        raised;
      - `cancel()` twice with a replacement issued in between: the first
        handle still `cancelled` with its own travel, the replacement
        still `active`, still owning `crank`, and still admitting travel
        on the next tick (the identity test of design decision 4);
      - `cancel()` on a `completed` handle (`Train`), on a `blocked` one
        (`Ranged`, driven into its bound) and on a `refused` one
        (`Differential`, the conflict `ConflictTest` already provokes):
        each keeps its status and its admitted travel, and
        `sim.commands` is unchanged;
      - `trigger('Wind')` — two handles, `crank` and `lever` — one
        cancelled: that input stands, the other reaches `completed` with
        all its travel;
      - the same script twice (issue, step, cancel, step): equal bank,
        equal tick, equal status and admitted travel at every step.
- [x] 1.3 In `SnapshotTest` of the same file, the two snapshot
      scenarios: a snapshot taken AFTER a cancel carries no command
      (`snapshot.commands == ()`), restores to an empty `sim.commands`
      and moves that input on no later tick; a snapshot taken BEFORE a
      cancel, restored after it, leaves the cancelled handle reporting
      `cancelled` with what it had admitted while `sim.commands` holds a
      fresh `active` command for that input that continues from the
      recorded progress on the next tick.
- [x] 1.4 Run the new tests and record them RED in `evidence.md` with
      the actual failures — the first one failing with travel admitted
      after a cancel and the replacement raising `'crank' is already
      owned by <move crank cancelled: ...>`, which is the wart's own
      symptom inside the suite.

## 2. The retirement

- [x] 2.1 `solid_node/simulation/run.py`: `Command.__slots__` gains the
      slot holding its run, set to `None` in `__init__` (a command not
      yet in `active` owns nothing), and `Command.record()` is left
      exactly as it is — eight fields, no run — so `RunSnapshot`
      equality and `restore` are untouched.
- [x] 2.2 `solid_node/simulation/run.py`: `Run._retire(command, status)`
      — set the status, remove the entry from `active` only when it IS
      this command (`self.active.get(command.input) is command`), and
      drop the command's reference to the run. Every existing retirement
      goes through it with its own word: `_block` with `'blocked'`,
      `_refuse` with `'refused'`, the completion loop at the end of
      `integrate` and `rate(input, 0)` with `'completed'`, and
      `restore` with `'cancelled'` over a LIST of the active commands,
      since it retires while emptying the dict. No status word changes,
      and no retirement changes when it happens.
- [x] 2.3 `solid_node/simulation/run.py`: `move`, `rate` and the
      reconstruction loop in `restore` set the new command's run as they
      put it into `active`, so a restored command is cancellable through
      `sim.commands` exactly as an issued one is through its handle.
- [x] 2.4 `solid_node/simulation/run.py`: `Command.cancel()` retires
      itself through its run when its status is `active` and its run is
      set, and returns the handle in every case. It does NOT call
      `Run._owns()` (design decision 5) and it touches no coordinate.
      Its docstring keeps its promise and now states the release and the
      idempotence.
- [x] 2.5 Section 1 green, and `tests/test_running_simulation.py`,
      `tests/test_running_stops.py`, `tests/test_running_jumps.py`,
      `tests/test_running_document.py` and
      `tests/test_running_corpus.py` green UNCHANGED against the counts
      of 1.1 — the corpus fixture and `tools/generate_running_corpus.py`
      are not touched by this change, and the corpus replay passing is
      the evidence that the other five retirements still retire where
      they did.

## 3. Records

- [x] 3.1 `docs/architecture.md`, the running-simulation synthesis: the
      sentence listing what retires a command from `sim.commands` ("the
      tick it completes, blocks or is refused") names cancellation too,
      and says the input is free at once.
- [x] 3.2 `docs/scenarios.rst`: the running-commands passage, which
      lists the five statuses and says a completed command leaves
      `sim.commands`, states what `cancel()` does and shows the
      replacement.
- [x] 3.3 `docs/changelog.rst`, Unreleased: what changed, in the
      pilot's register — a cancelled command stops, frees its input and
      keeps its travel; nothing else moves.
- [x] 3.4 `evidence.md`: the green runs, the reproduction from
      `workflow/warts.md` re-run against the fixed worktree (it must now
      print no travel, no owner and accept the replacement), and the
      probe of `evidence/probe_scenarios.py` re-run so the before and
      after stand side by side.
- [x] 3.5 `workflow/warts.md`: the "Pin tumbler lock (2026-09-14,
      running-command cancellation)" entry's status line records the
      fix and names this change, in the form the log's other fixed
      entries use.
- [x] 3.6 ADR disposition: confirm after implementation that no new ADR
      is owed — ADR-105 already states the handle contract and names
      `cancelled` — and add the sentence to ADR-105's consequences if
      the implemented shape warrants it. Do not write an ADR for a
      defect fix that decides nothing new.
