# Pre-implementation evidence — 2026-09-15

Origin: the pilot approved direct mechanical operation of
`projects/Calculators/Curta-Type-I-3x`, including individual selectors,
crank lift/rotation and carriage lift/rotation, without automatic sequencing.

At framework base `3519c61bf6d79e2be5df7a5972411358c9ae2371`, run from
this cycle worktree with the workspace environment:

```sh
PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_controls.py::RefusalTest::test_a_turn_on_a_coordinate_that_does_not_turn_is_refused tests/test_controls.py::RefusalTest::test_a_node_declaring_two_joints_is_refused -q
```

Result: **2 passed in 1.14 s**. These tests prove the current intentional
refusals, not the proposed features. The fixtures `Sliding` and `TwoJoints`
exercise the public Sim path and assert the named translational-domain and
multiple-joint errors. The new positive feature tests must still run red
after ratification and before implementation.

At viewer base `33ac0ad934ee5011f2085365134a640bd4544ee8`, the source
`solid_node_viewer/widget/src/partControls.ts` lists only button/turn and
unconditionally validates a leading rotation. This also rejects a prismatic
button, even though a press does not need angular gesture math. No viewer
behavioral test for the new feature has yet been run.

The project currently declares one operand Driver and derives all eight
selector settings from it. Its crank and register carriage each already own
both turn and lift joints. Its custom calculator page keeps register history
outside the run and performs operation preparation. The approved migration
removes those interaction abstractions; existing source-fit findings remain
separate work, not evidence for this prerequisite.

No production source has been changed and no prerequisite implementation is
claimed complete. Ratification, new feature red tests and paired browser
verification are outstanding.

# Implementation evidence — 2026-09-15

Planning committed alone, one commit above the base. Everything below
was run from this cycle worktree with the workspace environment,
`PYTHONPATH="$PWD"` and
`/home/asa/devel/libresolid-studio/.venv/bin/python`.

The cycle was worked on the recorded base `3519c61` and, on the pilot's
instruction, REBASED onto framework `main` when it was finished. Main
had moved six commits since planning (`d3dfba7`, `5fcada6`, `b8409cc`,
`94ede81`, `55d16e7`, `31c12a6`) and one more while the cycle was being
completed (`33f9df7`). Three conflicts, each resolved by keeping both
sides: the ADR index (115 then 117), the changelog (this entry above
`a-read-is-not-a-binding`'s) and one test import list. One real
breakage the auto-merge could not see: `StatedPlug`, a fixture main
added, holds `key = Slide()` — the leaf this cycle renamed `Carriage`
so the name could belong to the control. Renamed there too. Every
number below is from the REBASED tree.

## Red before green

The public name did not exist. With the fixtures and tests written and
no production source changed:

```
ImportError: cannot import name 'Slide' from 'solid_node.simulation'
```

`tests/test_controls.py` and `tests/test_running_document.py` both failed
to collect on it — the honest red for "prove Slide and explicit
coordinate selection fail through the public declaration/Sim path",
since a declaration the package cannot name fails at the import.

## What the fixtures are

`tests/running_project/machine.py` gained the DIRECT MOTION machines:
`Selector` (one prismatic joint, a `Slide` and a `Button` on the same
sliding part), `Crank`/`CrankBare` (one body, an off-centre revolute and
a prismatic, three selected controls and the control-free twin),
`AmbiguousCrank` (the same body with no selection), `Tilted`
(non-parallel inner revolute and outer prismatic, under a placing
ancestor, the slide at a NEGATIVE ratio), `Register` (a knob under a
jointed child of a carriage, whose `Slide` selects the carriage),
`Sideways`, `FreeSelected`, `SlidingTurn` and `GateTouched` (the pin
tumbler gate with its key and plug declared as controls). The leaf
`parts.Slide` is renamed `parts.Carriage`, because `Slide` is now a
public control; no other module named it.

## Green

```sh
python -m pytest tests/test_controls.py tests/test_running_document.py \
    tests/test_lazy_test_framework.py tests/test_browser_renderer.py -q
```
**233 passed, 1 skipped, 194 subtests passed.**

```sh
python -m pytest tests/ -q
```
**2743 passed, 4 skipped, 1521 subtests passed in 320.37 s, 0 failed**
— the whole suite on the rebased tree, main's own new tests included.
(On the pre-rebase base the same suite read 2709 passed, 4 skipped,
1513 subtests, 0 failed.)

## What did not move

- `tests/base_documents/touched_columns.json` is `Columns`' whole
  document, captured from the producer at the base commit BEFORE any
  source was changed (generated from `git archive HEAD tests` so the
  capture could not see the new fixtures). `document(bound(Columns()))`
  still equals it byte for byte: the four inferred rotational entries
  gain no field, and neither does the program.
- The five no-control base documents are byte-identical, as before.
- `PYTHONPATH="$PWD" python tools/generate_running_corpus.py` rewrites
  `tests/running-corpus.json` byte-identically (185,444 bytes, 14
  scenarios over 12 machines), confirmed with `cmp` against the copy
  taken first.

## Consumer fixtures for `slide-and-turn-parts`

`tools/generate_control_fixtures.py` exports the five documents the
paired viewer change reads. Reproducible command, from this worktree:

```sh
PYTHONPATH="$PWD" python tools/generate_control_fixtures.py \
    --output <directory>
```

Producer content: framework worktree `direct-part-motion`, this cycle's
implementation commit (recorded in the completion report), base
`3519c61`. Paired viewer base `33ac0ad`. Running it twice into two
directories and `diff -r`-ing them shows no difference; 144 KB in total.
What it publishes:

| fixture | machine | controls | with a span |
| --- | --- | --- | --- |
| `columns` | `Columns` | 4 | 0 |
| `selector` | `Selector` | 2 | 2 |
| `crank` | `Crank` | 3 | 3 |
| `tilted` | `Tilted` | 2 | 2 |
| `register` | `Register` | 2 | 2 |

sha256 of the five manifests as generated here:

```
ceb797f5806fcd8783c009ee8ae51657d3b0aa4d5198129acabb97cf3ed50dd5  columns/manifest.json
1a11d61e13b08436c65f362acab7c82df879520cdb160d6c79afdb65eb576abd  crank/manifest.json
56b8c8d7de85e3c80326577af873819ecf360f28b47c0f21de45c6ff0a70ef9b  register/manifest.json
349656ff281fde54d4bf6c600454f42ab4e9c37a34f61e51a081c02973a11a38  selector/manifest.json
bcab72e78acd12655fe1d57e7452f539bc7939eb57348a7e5c0d847c3f7171b9  tilted/manifest.json
```

The entries they carry, read back out of the manifests:

```
selector  press selector  button  selector.travel       axis [0,1,0]  origin [0,0,0]  span [0,1]
selector  slide selector  slide   selector.travel       axis [0,1,0]  origin [0,0,0]  span [0,1]  per_unit 6.0
crank     lift crank      slide   crank.lift            axis [0,0,1]  origin [0,0,0]  span [3,4]  per_unit 8.0
crank     rotate crank    turn    crank.turn            axis [0,0,1]  origin [0,12,0] span [0,3]  per_unit 360.0
crank     turn crank      button  crank.turn            axis [0,0,1]  origin [0,12,0] span [0,3]
tilted    shift stack     slide   stack.shift           axis [0,1,0]  origin [0,0,0]  span [1,2]  per_unit -2.5
tilted    swing stack     turn    stack.swing           axis [1,0,0]  origin [0,0,0]  span [0,1]  per_unit 1.0
register  shift register  slide   register.travel       axis [1,0,0]  origin [0,0,0]  span [0,1]  per_unit 1.0
register  turn marker     turn    register.marker.turn  axis [0,0,1]  origin [0,0,0]  span [0,1]  per_unit 1.0
columns   (four entries)  turn/button                   no span anywhere
```

## What is NOT claimed

- **No paired viewer evidence.** `slide-and-turn-parts` is proposed, not
  ratified and not implemented, and it owns every gesture, handle and
  browser assertion. Nothing here has been operated by a pointer. Task
  3.1's paired browser evidence is the consumer cycle's to produce, and
  the originating need is not satisfied until it exists.
- **No Curta work.** The pilot assigned `Curta-Type-I-3x` to another
  agent; nothing in that project was read for state or changed here, and
  its migration, its mechanical laws and its acceptance run are that
  agent's. The prerequisite this cycle owed the project is the framework
  surface, and it is what the fixtures above demonstrate.
- **Not integrated.** The branch is rebased onto `main` and is exactly
  two commits above it, fast-forwardable, but integration itself is the
  pilot's to direct. Nothing is pushed, tagged or published.
