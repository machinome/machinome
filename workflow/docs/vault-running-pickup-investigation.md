# Resolution tracking

The investigation below is a historical record at framework `b9b64dd`.
On 2026-09-19 the pilot ratified `unilateral-running-pickup`, companion
viewer support, adversarial review, and integration to main. The active
OpenSpec change is now the design authority; its implementation and caller
verification supersede the historical statements of pending authority below.
GitHub posting remains unperformed because the CLI is unauthenticated.

# Vault running pickup investigation

Status: investigation complete; capability/semantics wart drafted, awaiting
pilot review and GitHub authentication. No interface ratified, implementation
started, baseline spec changed, or external issue opened.
Date: 2026-09-19.

## Scope and identity

The pilot requested a framework investigation and, if warranted, a wart after
the complex Vault's running pickup prototype failed. The project must keep
`Time.running()`; replacing it with a clocked or duplicated host controller is
not the requested outcome.

- Origin: `projects/Locks/Vault_with_combination_lock`, checkpoint `78d4ceb`.
- Framework base: `main`, clean HEAD
  `b9b64ddaf0bc1d51d715d3d971b77b6ee58880bf`.
- Isolated branch/worktree: `vault-running-pickup-investigation`,
  `machinome-framework/WTs/vault-running-pickup-investigation`.
- Prospective integration target: framework `main`; no integration authorized.
- Scope is standalone, not a sprint. These are pre-spec working records,
  not an implementation cycle or accepted design.
- Environment: Python 3.12.3, Linux 6.8.0-139-generic x86_64, glibc 2.39.

## Finding: positional engagement is not unilateral pickup

The admitted experimental law is:

```python
lambda dial, held: dial * ((dial - held >= 3) + (dial - held <= -329))
```

It has a genuine 332-degree disengaged interval, a banked revolute coordinate,
a self-read only inside comparisons, and a guarded rest default. It is not a
zero-width gate, an unbound rest pose, a repeated-child qualification problem,
or a failure to retain wheel history in the bank.

However, it is not a complete statement of a peg contact. At `dial = 1590`,
`wheel = 1587`, the upper comparison is true. Under that branch, the skeleton
is `dial`, so reversing the dial by 10 degrees also moves the wheel by -10.
The relative level remains exactly 3. The physical peg should instead leave
the wheel where it stood: it can push at this flank, not pull.

This behavior follows the accepted ADR-121 rule, rather than proving a
regression against it. `machinome/simulation/program.py::_Walk._decide`
(base lines 1254–1298) starts from the comparison operator's branch and flips
only when the candidate path leaves the surface. `_probe` (1315–1327)
evaluates that path including the driven wheel's own motion. When dial and
wheel move together, the level is constant; `_probe` returns `None` and
`_decide` retains the engaged branch. `_solved` (1381 onward) similarly finds
no crossing of a level that does not move.

The mechanism needs a **direction-sensitive unilateral contact decision** at
this boundary. Position alone, with the current on-surface branch rule, does
not state it. It would be misleading to file the entire result as an
unconditional bug in ADR-121's existing missing-tooth clearing behavior.
No documented, validated alternative running formulation was found in the
public motion/mechanism API or scenarios. That is a capability finding, not
a proof that every possible expression has been exhausted.

## Reproduction and controls

The unchanged project supplies:

- `spikes/running_pickup.py`: one driver, one empty assembly carrying one
  revolute coordinate; no imported geometry.
- `simulation/test_running.py`: four contracts, including that mesh-free
  short reversal and an independent play-operator oracle for the three-wheel
  chain. The oracle is not a replacement runtime controller.

From the investigation bench, the following ran the existing project probe
against this worktree's framework code. Resolving the project path is
important because the catalogue is symlinked to another filesystem path.

```sh
PYTHONPATH="$PWD" /home/asa/devel/machinome-studio/.venv/bin/python - <<'PY'
import sys
from pathlib import Path
sys.path.append(str(Path('/home/asa/devel/machinome-studio/projects/Locks/Vault_with_combination_lock').resolve()))
import machinome
from spikes import running_pickup as probe
print(machinome.__file__)
for strict in (False, True):
    probe.STRICT = strict
    for dt in (0.02, 0.01, 0.001, 0.0001):
        print(probe.probe(dt))
PY
```

The imported `machinome.__file__` was inside this investigation worktree.
Probe destinations are `2, 360, 1590, 1580, 672, 720, 1182, 1140`, each over
one second. Expected wheel motion is the geometric play operator over each
monotonic segment: `max(x - high, min(previous, x - low))`.

| Comparison | dt (s) | First failure |
| --- | --- | --- |
| Inclusive `>=` / `<=` | 0.02, 0.01, 0.001, 0.0001 | At dial 1580, wheel 1577 instead of held 1587 |
| Strict `>` / `<` | 0.02 | At destination 672, tick 230: `UnsupportedLaw` |
| Strict `>` / `<` | 0.01 | At destination 720, wheel 1049.0000000000032 instead of held 1001 |
| Strict `>` / `<` | 0.001 | At destination 672, tick 4613: `UnsupportedLaw` |
| Strict `>` / `<` | 0.0001 | At destination 672, tick 46124: `UnsupportedLaw` |

The strict cases report a sliding mode. In the full three-wheel prototype,
non-integer measured pickup offsets additionally produce `TooManyCrossings`.
These outcomes show that strict comparisons or an arbitrarily small `dt`
are not validated workarounds. They do **not** establish that all refusals
are one implementation defect; numerical near-tangency and the semantics of
surface-following contact need separate analysis in any eventual fix.

Controls run on the same unmodified framework worktree:

```sh
PYTHONPATH="$PWD" /home/asa/devel/machinome-studio/.venv/bin/python -m pytest tests/test_running_reads.py -q
```

Result: **42 passed, 62 subtests passed** in 6.17 s. The existing source
contains an intentional sliding-mode refusal test, and its reversal tests
exercise missing-tooth clearing, not the Vault's unilateral contact.

The project suite was also rerun from the bench by adding the resolved project
path to `sys.path` and loading `simulation.test_running` with `unittest`.
Result: **1 passed, 1 assertion failure, 2 errors**. Snapshot/replay passes;
pickup motion, reversal, and cadence/segmentation remain red. A replay of an
incorrect path is not physical correctness.

## Relationship to earlier findings and possible follow-on

`workflow/warts.md`, "Locks (2026-09-13, Combination safe lock)", already
records the cost of retaining pickup in separate Python and browser
controllers for a different source model. The present finding is narrower:
running state retention exists, but the attempted declarative positional
gate does not express unilateral release at contact. It is not evidence
that the author's Vault geometry or published combination is wrong.

A future ratified change would need to establish, not assume:

1. How a maker states the two contact flanks and direction-sensitive release
   without a second history controller or hidden per-tick project mutation.
2. Which behavior is existing-law conformance and which needs a new contract.
3. Correct collection, immediate release on reversal, opposite-flank pickup,
   arbitrary partial moves, cadence/command splitting, snapshot and reset.
4. Behavior at exact and non-integer contact surfaces without an unexplained
   epsilon, while preserving the genuine sliding-mode refusal control.
5. Independent viewer parity if the running program's semantics change;
   the viewer is a separate repository, not framework implementation scope.

No particular API, integrator repair, document version, or viewer change is
proposed or authorized by this investigation.

## Filing disposition

The proposed body is [vault-running-pickup-wart.md](vault-running-pickup-wart.md).
Target confirmed from the framework remote and public issue page:
`machinome/machinome-framework`. The public open-issue page shows no matching
pickup issue; authenticated/all-state duplicate and label checks remain open.

`gh repo view` failed before any write because GitHub CLI is unauthenticated.
The shop's `file-a-wart` skill also requires review of the body and target
before posting. No issue URL exists, labels have not been assumed present,
and no external issue, PR, push or release occurred. Local investigation and
wart records are uncommitted in the isolated bench pending that review.
