# Curta carry association changes with the carriage

**Status:** pre-spec requirement and implementation handoff, requested by the
pilot on 2026-09-15. This records a reproduced project limitation, not a
ratified API or permission to redesign the solver. The refused representation
is not evidence that every supported representation is impossible.

**Taken up** as OpenSpec change `select-the-source` (ADR-122, extracted after
review) on 2026-09-15: a cycle every selection breaks is a BLOCK, one entry of
the running program, ordered once per PIECE of a tick rather than once per
program. The selection is the comparison the model already writes; nothing new
is declared. The project-side migration (item 6) and the viewer's execution of
a version 7 document (item 7) remain open, each in its own repository, and
what the migration needs is listed in that change's design.md section 12.

This follows [retained-angle clearing](curta-retained-angle-clearing.md).
ADR-121 has resolved that declaration limitation in Python, and the project's
finite-band clearing prerequisite tests now pass. The finding below concerns
dependencies between different moving parts, not another own-angle read.
The viewer's retained-angle implementation remains separate ongoing work;
it does not block establishing and testing a Python-side representation.

## Required maker outcome

The maker lifts the Curta carriage, shifts it to another working position,
and seats it, each as an independent physical action. Subsequent crank motion
acts on the newly aligned digits. Returning the carriage does not restore an
old calculator result, reset a lever, or replay an earlier crank revolution.
Register angles and partial motion remain on the actual mechanical parts.

The carry levers and transmission shafts belong to the fixed frame, while
the number dials move with the carriage. The same fixed carry lever therefore
meets different dials at different carriage positions. A dial's passage trips
that lever; the engaged carry gear advances the next aligned shaft; the reset
mechanism returns the lever. The lever's position must participate in causing
the carry, not merely illustrate an independently computed arithmetic answer.

All six working carriage positions and both register banks belong to one
persistent run. The maker can attempt partial or blocked movements in any
order. Physical interlocks limit admitted movement; no controller completes a
crank turn, lifts the carriage, or seats it to prepare a shift. This remains
prescribed kinematics with declared constraints, not a force/contact solver.

## Originating project and measured identities

The independent repository is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, checkpoint `6a00abe950e9d9c1ecf8847935a8f47787d24f6c`.
Framework main tested is `8e15791e5fe66aecced30fc3c1735a62c71cad90`, including
the Python implementation of ADR-121 (`32cfc56`). Both checkouts were clean.
The probes below were rerun at those identities for this handoff.

Project-relative evidence:

- `simulation/docs/direct-operation-2026-09-15.md`: pilot-approved control
  inventory, retained operation and whole-machine acceptance obligations.
- `openspec/changes/simulate-the-curta/specs/curta-operation/spec.md`:
  independent carriage operation, mechanical retention and carry/reset needs.
- `simulation/docs/direct-operation-running-checkpoint-2026-09-15.md`:
  the clearing prerequisite's resolution and this follow-on finding.
- `simulation/tools/shifted_carry_probe.py`: geometry-free reduced failure
  and two fixed-position positive controls.
- `simulation/test_direct_operation_probe.py` and
  `simulation/tools/direct_operation_probe.py`: working fixed associations
  and own-angle clearing, including partial/repeated motion and replay.
- `simulation/transmission.py`, `shifted()` and `channel_values()`: the
  existing pose model's association of carriage dials with fixed channels.
  For fixed channel 1, its lever reads dial `shift`, while its output shaft
  engages dial `shift + 1`. These pose laws are evidence of association, not
  an implementation of retained mechanical operation.
- `simulation/standard/carry.py`, `simulation/standard/channels.py`,
  `simulation/registers.py`, `simulation/mechanism.py` and
  `simulation/carry_motion.py`: real lever, shaft and dial ownership,
  carriage placement, and existing engagement/reset geometry and timing.

The operating and geometry references remain the project's approved design,
its source measurements, and `Manual/Curta Build Manual.pdf`. The schematic
fixture below does not replace them.

## Reduced failure: active graphs versus their union

The fixture has two wheels, one fixed carry lever and a live carriage input:

| Carriage position | Fixed lever reads | Lever's output drives |
| --- | --- | --- |
| 0 | Lower wheel | Higher wheel |
| 1 | Higher wheel | Next wheel, outside this reduced fixture |

Ignoring each coordinate's supported own-read, either position's active graph
is acyclic. At position 0 the lower wheel drives the lever, which gates the
higher wheel's drive. At position 1 the higher wheel drives the lever and the
return connection to that wheel is inactive. The union nevertheless contains
`higher.turn -> carry.travel -> higher.turn`.

The public-API fixture expresses selection with mutually exclusive
`shift < .5` and `shift >= .5` factors. Its wheel relation names
`carry.travel`; its lever relation names both wheel angles. The compiled run
rejects the union before an operation can begin:

```text
UnsupportedLaw: the relations
(crank, shift, clearing, carry.travel, higher.turn) drives higher.turn,
(lower.turn, higher.turn, shift, carry.travel) drives carry.travel
form a cycle the run cannot order: each waits on a coordinate another determines.
A running program is acyclic, because the rest render solved every relation
in one direction.
```

Specializing the association to either fixed position constructs and admits
a crank request. This proves construction and command admission only, not
the fixture's numerical timing or real Curta arithmetic. Its latch threshold,
direct drive, carriage switch and clearing term are intentionally schematic.
In particular, this is not evidence about intermediate physical carriage
engagement or a validated bidirectional clearing law.

From the project root, using the workspace environment:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
  ../../../.venv/bin/python -m unittest simulation.test_direct_operation_probe
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
  ../../../.venv/bin/python -m simulation.tools.shifted_carry_probe
```

The first command passes both tests, including all ten starting clearing
digits in both directions. The second prints `completed` for fixed positions
0 and 1, then the live-selection refusal above, and deliberately exits 1.
Neither command needs a CAD build. No new CAD or browser validation is claimed
by this documentation handoff.

## Architectural question to resolve

First establish a supported public composition for changing the association
without losing real-part ownership or history. If one exists, return a small
executable example and evidence that it covers the live shift, not merely
each separately constructed position. If none fits the accepted contract,
propose the smallest coherent framework change under the shop workflow.

The current authorities remain `docs/architecture.md` (Kinematics and
Simulation), `openspec/specs/couplings/spec.md`,
`openspec/specs/simulation/spec.md`, and the accepted decisions:

- ADR-105: the run banks real driver/joint coordinates; plain ports are
  derived, inspection advances nothing, and the author declares no memory.
- ADR-106/107: the run compiles the relations' solved direction and integrates
  continuous contributions; branch jumps themselves move no part.
- ADR-108/113: physical stops and state-reading constraints determine admitted
  motion; an inactive engagement is not a stop on an otherwise free input.
- ADR-121: one driven coordinate may read itself through a switch. A read of
  another relation's driven coordinate remains an ordinary source. This does
  not establish arbitrary inter-relation cycles or a joint walk over several
  driven ends; grouping the wheels and lever is not an existing escape hatch.
- ADR-110/111: one published program and conformance evidence connect Python
  to the independent viewer runtime.

Any proposal must resolve how active dependencies are established, how a
selection or engagement change inside a tick affects their evaluation, and
what happens when dependencies really are simultaneously cyclic. Simply
removing cycle detection, freezing all reads for a tick, or accepting an
arbitrary evaluation order supplies no such semantics. This note selects
neither conditional ordering, a coupled solver, nor a new public API spelling.

The following do not meet the originating project's approved outcome:

- Making carriage position a construction parameter or reconstructing/resetting
  the run on every shift; neither demonstrates retained state and stable
  snapshot/program identity through an actual shift.
- Adding virtual per-dial carry-lever memories, duplicated coordinates solely
  to store history, page-owned registers, or per-tick project bookkeeping.
- Computing an independent calculator result and driving decorative carry
  parts from it, or clearing/resetting real latch state as a shift shortcut.

## Acceptance evidence owed

Start with a small geometry-free fixture with independent expected motion;
then return to the source-backed Curta mechanism. At minimum:

1. One run admits the two reduced associations and changes between them with
   distinct retained wheel and lever states. Shifting away and back preserves
   history except for motion actually caused by the modeled mechanism.
2. An inactive association neither moves its former wheel nor blocks an input
   that the mechanism permits. Selection alone creates no branch-jump motion.
3. Partial drive, lever engagement, carry completion and reset compose with
   release/resume and later shifts. A locked shift stops at its physical
   restraint; the controller does not discard a pending carry or finish it.
4. Selection/engagement changes within a command agree with finer partitions
   under a stated accuracy contract. Inspecting, recording, snapshot/restore
   and replay do not change the outcome or replace the program on a shift.
5. Genuinely unsupported active dependency cycles remain explicitly diagnosed,
   not silently evaluated in an arbitrary order. A runtime refusal, if the
   chosen design introduces one, is transactional. Existing single-command
   ownership, bounds, own-read clearing and ordinary acyclic laws regress green.
6. The real project exercises all six positions, carries/borrows through both
   banks, subtraction and counter reversal, partial crank motion, and clearing
   followed by another operation. Measured interlocks and carriage engagement
   determine legal motion, including intermediate positions. Preserve the
   approved page-53 calibration and existing contact/geometry obligations.
7. If the published program or its evaluation semantics change, document the
   producer/consumer compatibility requirement and validate actual exported
   fixtures through the viewer in its own repository. Python development may
   proceed first; paired replay and actual pointer validation remain owed,
   not waived. Record both tested content commits when that validation occurs.

Use the project's existing sequential, single-BLAS/OpenMP-thread, 8 GiB
address-space guard for heavy CAD validation, as documented in
`simulation/docs/pause-report-2026-09-11.md`. Existing whole-machine thread and
contact findings remain open independently of this requirement.

## Handoff and scope

The project remains at its pose-based production implementation with the
pilot-approved markings unchanged. Its direct-operation tasks 6.1–6.6 remain
open; passing prerequisites is not a completed interactive Curta.

This note was prepared on framework branch `curta-shifted-carry-requirement`
in `solid-node/WTs/curta-shifted-carry-requirement`, based on the clean main
commit named above. It is a documentation-only pre-spec record, not an
OpenSpec planning commit or ratification. No framework, viewer or project
implementation is included, and no integration or publication is implied.
The next deliverable is a supported example, or a separately proposed and
ratified framework contract, with evidence that unblocks the project migration.
