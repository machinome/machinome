# Evidence: vet-the-project

Every command ran from `/home/asa/devel/machinome/machinome/WTs/vet-the-project`
with `PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`,
one suite at a time.

## 0. Opening evidence

### 0.1 The interpreter imports this worktree

    python -c "import machinome; print(machinome.__file__, machinome.__version__)"
    /home/asa/devel/machinome/machinome/WTs/vet-the-project/machinome/__init__.py 0.7.0

Base commit: `d791eaa` (Implement place-parts-by-mate), with the planning
commit `71e3e6b` on branch `vet-the-project` above it.

### 0.2 The full suite at the base

    python -m pytest tests -q -p no:cacheprovider
    3816 passed, 4 skipped, 53 warnings, 2487 subtests passed in 405.93s

### 0.3 The catalogue survey of 2026-09-26

The proposal's table comes from the survey recorded in
`workflow/ongoing/vet.md`. Method: every `*.py` under a project's
`simulation/` directory in the catalogue, excluding paths containing
`/.git/`, `/_build`, `/WTs/`, `/tests/`, `/tools/`, `/scripts/` or
`/.venv/`, and files named `test_*.py` or `conftest.py`: 1,131 files
(an earlier 1,892 counted the copies under `.git/licensing-worktrees/`).
Counts are of files, not of model closures.

| What the code does | Files |
| --- | --- |
| Runs a process through `subprocess` | 4 |
| Fetches over the network (`urllib`) | 1 |
| Writes a file | 7 |
| Lists a directory through `os` | 6 |
| Mutates `sys.path` | 2 |
| Other stdlib outside the pure tier | 8 |
| Third-party outside the kernels | 1 |
| Uses shapely | 2 |
| Reads a project file by hand | 9 |
| Imports `os` or `pathlib` | 31 |
| Adapter sources computed rather than literal | 14 (122 assignments) |

The 625 literal source declarations resolve under their project roots.
The pilot's decisions of 2026-09-26 are recorded in `design.md`'s last
section; none is open.

## 1. Planning record

### 1.1 Validation

    openspec validate vet-the-project --strict
    Change 'vet-the-project' is valid

The planning commit `71e3e6b` holds the change folder and
`workflow/ongoing/vet.md` and nothing else (`git show --stat 71e3e6b`:
12 files, all under `openspec/changes/vet-the-project/` plus the note).

## 2. The manifest module (`tests/test_manifest_module.py`)

### Red

    python -m pytest tests/test_manifest_module.py -q
    14 failed in 0.34s

Every test failed for the reason 2.1-2.3 name: `ModuleNotFoundError: No
module named 'machinome.manifest'` (the probe of 2.1 exits nonzero on the
same import).

### Green (2.4)

`machinome/manifest.py` holds `ProjectManifestError`, `MODEL_NAME`,
`_find_manifest`, `project_root` and the new `read_declaration` /
`Declaration`; `machinome/core/loader.py` imports and re-exports them and
builds `read_project` from the declaration plus build directories.

    python -m pytest tests/test_manifest_module.py -q
    14 passed, 10 subtests passed in 0.29s
    python -m pytest tests/test_named_models.py tests/test_loader_references.py \
        tests/test_lazy_test_framework.py tests/test_cli.py -q
    95 passed, 92 subtests passed in 43.89s

The four loader suites are unchanged (`git diff --stat` on them is empty).
The refusal tests pin each message `read_project` gave before the move,
literally, and assert both `read_declaration` and `read_project` give it.

## 3. Fixtures, the universe and its packaging

### 3.1-3.2 Fixtures

`tests/conftest.py`'s `collect_ignore` gains `vet_projects`. The fixture
projects under `tests/vet_projects/` are one pure project and one per
finding kind or rule (34 in all, named as in tasks.md 3.2), each with its
own `pyproject.toml`. Two deviations of spelling, recorded here: the
`tests_tier` fixture's "second model module that imports `unittest`" is a
second declared model (`bad = "sim.bad:Bad"`) beside the pure `gear`, so
the pure model's verdict stays readable; the `side_effect` fixture's
package is named `side_effect_fixture` rather than `sim`, so its absence
from `sys.modules` is unambiguous. The symlinks of `escaped_module` and
`source_escapes` are created by the tests in temporary copies.

### 3.3-3.4 Red

    python -m pytest tests/test_vet_universe.py -q
    13 failed in 0.12s

Ten fail with `ModuleNotFoundError: No module named 'machinome.vet'`, the
packaging test with `ImportError: cannot import name 'vet'`, the
bumpversion test with the section missing from `setup.cfg`, and the
dependency test with `shapely==2.1.*` missing from `[project]
dependencies`.

### 3.5 Green

`machinome/vet/universe.toml` (D3, verbatim lists), `load_universe` and
`Universe.member` in `machinome/vet/__init__.py`, the
`[bumpversion:file:machinome/vet/universe.toml]` section in `setup.cfg`,
`"shapely==2.1.*"` in `pyproject.toml` (installed: 2.1.2), and
`include machinome/vet/universe.toml` in `MANIFEST.in`.
`requirements.txt`, which says it mirrors `pyproject.toml`'s runtime
dependencies, gains the same line.

    python -m pytest tests/test_vet_universe.py -q
    13 passed in 0.08s

## 4. The resolver (`tests/test_vet_closure.py`)

### Red

    python -m pytest tests/test_vet_closure.py -q
    15 failed in 0.14s

All fifteen fail with `ImportError: cannot import name 'vet' from
'machinome.vet'`: there is no resolver and no `vet()` to run it.

### Green (4.4)

`machinome/vet/resolve.py` (D4: entry, dotted and relative resolution,
`from p import n`, star imports, every scope, escape, shadowing, parsing
from bytes, a worklist over real paths with each file parsed once and
judged once per mode), and `vet()` with the `Report`, `ModelReport` and
`Finding` records in `machinome/vet/__init__.py`, so the closure can be
asked for. At this step `assertions.py` held only what the closure needs
(the import statements of a file and universe membership); its rules are
section 5's, written red first there.

    python -m pytest tests/test_vet_closure.py -q
    15 passed in 0.14s

## 5. The static assertions (`tests/test_vet_assertions.py`)

### Red

Run against the closure-only `assertions.py` of step 4.4:

    python -m pytest tests/test_vet_assertions.py -q
    74 failed, 7 passed, 2 subtests passed in 0.54s

The eighteen tests of 5.1-5.9 and 5.11 that expect a finding fail because
no rule raises one (each fixture's findings are the empty set, or, for
`sys_path` and `sys_modules`, only `outside-universe` `sys`), and 5.11
fails because the module declares no `KINDS`. Seven pass at this step,
and are reported rather than hidden:

- the four that assert the *absence* of a finding (the pure APIs,
  `pathlib` whole, a computed source, a literal under the root without
  its file) cannot be red while no rule exists; they are the guards
  against a rule that fires too widely, and they stay green after 5.12;
- the two of 5.10 (the tests tier) were already green, because the tests
  tier is membership, which the universe (3.5) and the resolver's
  per-mode judging (4.4) implement; the red-first gap is that 5.10 was
  not written before 4.4;
- `test_every_fixture_raises_only_declared_kinds` is a guard of the same
  kind.

### Green (5.12)

`machinome/vet/assertions.py` (D5, D7): the sixteen kind constants and
`KINDS`, `judge_import`/`judge_reach` against the contract and kernel
denylists, the restriction and the import-system names, and the per-file
scanner (import bindings, attribute chains on import-bound names, the
method denylist on unbound receivers, dynamic and denied built-ins,
dunders as names, attributes and string literals, the `open` mode rule,
the pathlib write methods, and the source attributes). One resolver fix
went with it: a `from p import n` judges `p.n` as a reach even when `p`
itself is outside the universe, so `from sys import path` raises both
`outside-universe` `sys` and `import-system` `sys.path` (spec scenario
"sys.path mutation", tasks 5.6).

    python -m pytest tests/test_vet_assertions.py -q
    25 passed, 58 subtests passed in 0.36s
    python -m pytest tests/test_vet_closure.py tests/test_vet_universe.py -q
    28 passed in 0.19s

## 6. The adapters contain their sources (`tests/test_missing_source_file.py`)

### 6.1 Fixtures

`EscapingBracket`/`EscapingAbsentBracket`/`LinkedBracket` in
`tests/stl_project/parts.py` and `EscapingPart`/`EscapingAbsentPart`/
`LinkedPart` in `tests/step_project/parts.py`. The escaping ones declare
`'../../pyproject.toml'` (the repository's own manifest, a regular file
above `tests/`, which is the fixtures' project root) or an absent file
beside it; the linked ones go through `linked_outside.stl` /
`linked_outside.step`, symbolic links `setUpModule` creates into a
temporary directory and `tearDownModule` removes (both names fall under
the existing `.gitignore` patterns for generated fixtures). The OpenSCAD
and JSCAD cases write scratch projects `<base>/project/` beside
`<base>/outside.*`, through `../` and through a symlink. The marking case
declares `Svg('../pyproject.toml')` from `tests/`.

### Red

    python -m pytest tests/test_missing_source_file.py -q
    11 failed, 13 passed in 3.09s

Each containment test fails for the reason 6.2 names. Construction does
not refuse: the artwork class is created (`ValueError not raised`); an
absent escaping source raises `MissingSourceFile`, a `FileNotFoundError`,
not the containment `ValueError`; an existing one gets past admission and
fails later, in `AbstractBaseNode.__init__`, with `ProjectManifestError:
No pyproject.toml with [tool.machinome] found above <the source>`, and the
OpenSCAD one has already called `coherent_read` by then. The 6.3 tests
(a computed STL source and an absolute STEP source under the root) pass
before and after, as they must.

6.4's first draft placed the source beside the manifest-less module; it
failed today for a reason that is not the change: `AbstractBaseNode`
finds the project root of the *source* for its build directory, so a
source in no project has never constructed. The test was corrected
before the implementation to a module in no project whose source lies in
another project, which is the case the scenario means ("constructs as
before"), and it passes before and after.

### Green (6.5)

`require_source_file` (`machinome/node/sources.py`) calls
`_require_inside_project` first: the declaring module's real path, its
root through `machinome.manifest.project_root` (memoized per module real
path in `_declaring_roots`; a `ProjectManifestError` means no project and
no judgement), and `os.path.commonpath` on the real paths. The four
adapters and `Svg.resolve` are not edited.

    python -m pytest tests/test_missing_source_file.py -q
    24 passed in 2.55s

### 6.6 The suites that construct source-bound leaves

    python -m pytest tests/test_missing_source_file.py tests/test_stl_node.py \
        tests/test_step_node.py tests/test_meta.py \
        tests/test_builder_reload_resilience.py tests/test_markings.py \
        tests/test_build_lock.py -q
    311 passed, 24 warnings, 56 subtests passed in 108.21s

None of those files except `test_missing_source_file.py` changed. No
existing test declares a source outside its root.

## 7. The command and the report (`tests/test_vet_command.py`)

### Red

    python -m pytest tests/test_vet_command.py -q
    15 failed in 1.99s

Every test fails on `argument command: invalid choice: 'vet'` (exit 2,
usage on standard error): the command is not registered. The deliberate
update of `tests/test_cli_lazy_imports.py` (7.6: `machinome.manager.vet`
in `COMMAND_MODULES`, `vet` last in `COMMAND_ORDER`, `Vet` in the eager
reference parser) was then run red too:

    python -m pytest tests/test_cli_lazy_imports.py -q
    8 failed, 6 passed, 9 subtests passed in 1.51s

(`ModuleNotFoundError: No module named 'machinome.manager.vet'` in the
oracle, and `vet` missing from the registry order.)

A harness finding on the way: the import probe runs `python -c`, which
puts the working directory first on `sys.path`, and inside the
`shadowing` fixture that made the fixture's own `json.py` stand in for
the standard library's in the vetting process itself (`AttributeError:
module 'json' has no attribute 'dump'` in the probe). The installed
`machinome` script does not put the working directory on the path, so
the command tests run the probe with `PYTHONSAFEPATH=1`, as the script
effectively does. This is a property of `python -c` in any directory,
not of vet.

### Green (7.7)

`machinome/manager/vet.py` (`Vet`, `needs_node = False`, its own
`reference`, `--tests`, `--json`; manifest errors and a directory
reference exit 2 with the reason on standard error), `render_text`,
`report_object` and `render_json` in `machinome/vet/__init__.py`, and
`'vet': ('machinome.manager.vet', 'Vet')` last in `COMMANDS`.

    python -m pytest tests/test_cli_lazy_imports.py tests/test_vet_command.py -q
    29 passed, 20 subtests passed in 3.69s

The top-level help changed by exactly one entry. `diff` of `machinome -h`
before and after:

    2c2
    <                  {build,develop,test,snapshot,new,export,viewer,models,import-step}
    >                  {build,develop,test,snapshot,new,export,viewer,models,import-step,vet}
    13c13
    <   {build,develop,test,snapshot,new,export,viewer,models,import-step}
    >   {build,develop,test,snapshot,new,export,viewer,models,import-step,vet}
    41a42,43
    >     vet                 Checks, statically, that the project stays inside the
    >                         machinome universe.

The two choice lines are argparse's rendering of the same one new name.

## 8. Cost and isolation (`tests/test_vet_isolation.py`)

These properties have no implementation step of their own: they hold, or
not, of the code sections 4 and 7 wrote. Written after 7.7, the tests
were green on their first run:

    python -m pytest tests/test_vet_isolation.py -q
    4 passed, 17 subtests passed in 0.50s

So each was proved able to fail by a mutation of that code, run, seen
red for the reason its task names, and reverted (the files restored from
copies; `grep -c MUTATION machinome/vet/*.py` is 0 afterwards):

- 8.1, `import numpy` added to `machinome/vet/__init__.py`:
  `AssertionError: True is not false : numpy` (1 failed).
- 8.2, `runpy.run_path(path)` added to the resolver's `_parse`: the
  fixture's marker file exists after the vet (`True is not false`,
  1 failed); the test's cleanup removed the marker.
- 8.3, the JSON `root` taken from `SOLID_BUILD_DIR` when set: both
  environment tests fail, the `.env` one because `machinome`'s own
  `load_dotenv` put `SOLID_BUILD_DIR=/nowhere` into the environment
  (2 failed).

After the reverts:

    python -m pytest tests/test_vet_isolation.py -q
    4 passed, 17 subtests passed in 0.51s

The ordering gap is reported: tasks.md places section 8 after 7.7, so
these are mutation-proved rather than red before their code.

## 9. Documentation, records and completion

### 9.1 Architecture

`docs/architecture.md`, CLI section: one synthesis sentence naming `vet`,
its declaration `machinome/vet/universe.toml`, the kernel-free
`machinome.manifest`, and its limit (static, not a sandbox; reads bounded
by the runtime, declared sources by the adapters), citing the vet ADR (written as ADR-148, renumbered ADR-149 at the rebase below). The
Map's CLI row gains `machinome/manifest.py`, `machinome/vet/`, the spec
`vet` and ADR 148.

### 9.2 The manual

`docs/reference/cli.rst` gains a `machinome vet` section after
`machinome import-step`: synopsis, what pure means, the tiers described
without their member lists (pointing at the shipped declaration), what is
judged, the scopes, the text report (a `parsed-literal` example on the
public command, its version through `|release|`), the JSON shape, the
sixteen kinds, the exit statuses, and the limit, stated once. The pages
that document the sources say a source outside the project is refused at
construction: `reference/api.rst` (`scad_source`, `jscad_source`,
`stl_source`), `howto/imported-parts.rst` (STL, and STEP relative or
absolute), `howto/backends.rst` (OpenSCAD, JSCAD) and
`howto/markings.rst` (`Svg`). No release fact beyond `|release|`, no
publication caveat.

    python -m pytest tests/test_docs_structure.py -q
    7 passed, 110 subtests passed in 0.14s
    python -m sphinx -b html -n -W --keep-going -q -E docs <scratch>/html
    5 warnings, exit 1

The five warnings are the nitpicky `-n` warnings the base already has
(`reference/api.rst` lines 23, 35, 76 and two `Sim` docstrings), none on a
page this change touched: the same command over `git archive 71e3e6b`
gives the same five, and a `diff` of the two logs is empty. The built
`reference/cli.html` shows `universe machinome 0.7.0` in the example.

### 9.3 Warts

`workflow/warts.md` gains "OpenSCAD parameter values are echoed by hand
(2026-09-26, the vet survey)": Metamaquina2 and snappy-reprap
`simulation/params.py` and hangprinter `simulation/csg.py` run
`openscad -o <file>.echo` in a temporary directory to read values, with
line references; the gap the SCAD import could close. The fetch tooling
and fender-bender's `sys.path` are not filed.

### 9.4 ADR

`docs/adrs/BUILD/ADR-149-vet-checks-a-project-against-a-versioned-universe.md`
(written as ADR-148, the next free number after 147 at the base; renumbered 149 at the rebase, see below; at the base `grep -rn ADR-148` found no other
claim), indexed under BUILD in `docs/adrs/README.md`.

### 9.5 The full suite at the end

    python -m pytest tests -q -p no:cacheprovider
    4 failed, 3912 passed, 4 skipped, 53 warnings, 2574 subtests passed in 404.16s

Base (0.2): 3816 passed, 4 skipped, 2487 subtests. The change adds 100
tests. The four failures are all
`tests/test_import_step.py::GeneratedModelFaithfulnessTest` (single part,
nested, repeated, duplicate-named), and they are this change's
containment refusal, not a flake:

    ValueError: FixedRing declares step_source = '../../../home/asa/devel/
    machinome/machinome/WTs/vet-the-project/tests/step_project/
    import_simple.step', resolved against /tmp/tmp…/import_step_fixture_3/
    parts.py, but …/tests/step_project/import_simple.step lies outside the
    project at /tmp/tmp…

The test writes `generate_parts` output into a scratch project under
`/tmp` (with its own `[tool.machinome]` manifest) while the STEP document
stays in the framework's `tests/step_project/`, and `generate_parts`
writes `step_source` as the path from the package to the document
(`os.path.relpath`), so the generated leaf points outside its project.
Per task 6.6 the test is reported, not rewritten. See "Needs the
reviewer".

### 9.6 The catalogue

`machinome vet --json` (default scope), run from each project root the
survey names, read only, `PYTHONPATH` at this worktree and
`SOLID_BUILD_DIR` unset. No project refused (no exit 2).

| Project | Exit | Models (impure) | Files vetted | Findings by kind |
| --- | --- | --- | --- | --- |
| 3D-Printers/Metamaquina2 | 1 | 1 (1) | 167 | outside-universe 2 (`subprocess`, `tempfile`), file-write 1 |
| 3D-Printers/snappy-reprap | 1 | 1 (1) | 29 | outside-universe 2 (`subprocess`, `tempfile`), file-write 1 |
| 3D-Printers/hangprinter | 0 | 1 (0) | 12 | none (`csg.py` is not in the model closure) |
| 3DPrintedClocks | 1 | 49 (49) | 2306 | kernel-io 4367 (`cadquery.exporters` 4116, `export` 147, `cadquery.occ_impl.exporters` 49), outside-universe 462 (`sys`, `git`, `io`, `warnings`, `datetime`, `shutil`, `os.system`, …), file-write 441 (`mkdir` 294, `open` 147) — the shared `clocks/` library imports `cadquery.exporters` in most modules, so every model reaches it |
| Robots/openvmp | 1 | 1 (1) | 8 | outside-universe 6 (`jinja2`, `yaml`, `sys`, `urllib.request`, `os.makedirs`, `os.replace`), file-write 1, kernel-io 1 (`cadquery.importers`) |
| Actuators/Internal-Cycloidal-Actuator | 1 | 1 (1) | 6 | outside-universe 4 (`sys`, `zipfile`, `os.makedirs`, `os.replace`), file-write 2 |
| Calculators/Curta-Type-I-3x | 1 | 4 (4) | 228 | file-write 8 (`mkdir` 4, `write_text` 4), kernel-io 3 (`trimesh.load_mesh`) |
| 3D-Printers/kossel | 0 | 1 (0) | 24 | none (its `os.listdir` passes) |
| 3D-Printers/Prusa3-vanilla | 0 | 1 (0) | 25 | none |
| 3D-Printers/fender-bender | 1 | 1 (1) | 20 | import-system 2 (`sys.path`), outside-universe 15 (`sys`, and the upstream modules it reaches through `sys.path`: `bender_config`, `filament_bracket`, …) |
| Lab-Equipment/openflexure-microscope | 0 | 1 (0) | 41 | none (the archived `sys.path` script is not reached) |
| 3D-Printers/Voron-2 | 0 | 1 (0) | 43 | none (`ast` admitted) |
| Calculators/Poleni-1709 | 0 | 1 (0) | 9 | none — after the review closure's bound-name rule; before it, denied-builtin 11 (`input`) |
| Calculators/calculators-reconstruction/poleni-1709 | 0 | 1 (0) | 9 | none — same; before it, denied-builtin 11 (`input`) |
| Robotic-Hands/orcahand_hardware | 0 | 1 (0) | 4 | none |
| Robotic-Arms/Thor | 0 | 1 (0) | 16 | none |
| Robots/YouCanBuildDog | 1 | 1 (1) | 10 | kernel-io 2 (`OCP.STEPCAFControl`, `OCP.IFSelect`), outside-universe 2 (`sys`, `os.makedirs`) |
| Calculators/Pascaline-module | 0 | 1 (0) | 9 | none — same; before it, denied-builtin 2 (`input`) |
| Actuators/open_robot_actuator_hardware | 0 | 1 (0) | 3 | none |
| Actuators/OpenCycloid | 1 | 1 (1) | 7 | outside-universe 9 (`argparse`, `sys`, `tempfile`, `urllib.request`, `urllib.error`, `os.environ`, `os.fspath`, `os.close`), file-write 7 (`unlink`, `rmdir`, `mkdir`, `open`) |
| Robotic-Arms/open_manipulator | 0 | 1 (0) | 4 | none |
| Robotic-Arms/openarm | 0 | 1 (0) | 6 | none |
| Robots/AlbertPro | 0 | 1 (0) | 12 | none |
| Calculators/mechanical-multiplier | 0 | 1 (0) | 5 | none |

Against the proposal's table: the printers' `subprocess` rows are
findings where the model reaches them (Metamaquina2, snappy-reprap; not
hangprinter, whose model does not import `csg.py`); openvmp's `urllib`,
`yaml`/`jinja2` and writes are findings; the writers
(Internal-Cycloidal-Actuator, Curta, openvmp, the clocks) are findings;
the `os` listing projects (kossel, Prusa3-vanilla) pass; fender-bender's
`sys.path` is a finding and openflexure's archived script is not reached;
Voron-2's `ast` passes; the eleven computed-source projects raise no
source finding. Two things the survey did not predict: the clocks'
shared library makes all 49 models impure through `cadquery.exporters`,
and the `input` rule flags class-body children named `input`.

## Needs the reviewer

1. **`import-step` generates sources the containment refuses.**
   `generate_parts` writes `step_source` as the relative path from the
   `--into` package to the document, so `machinome import-step
   /elsewhere/robot.step --into sim/` yields a leaf that now refuses to
   construct unless the document lies inside the project. Four existing
   tests do exactly that (the document in the framework's
   `tests/step_project/`, the package in a `/tmp` project) and now fail
   with the containment `ValueError`. Choices: move the test's document
   into the scratch project (a test change, since a generated project
   whose document lives elsewhere is what containment forbids by design),
   and/or have `import-step` refuse, or warn about, a document outside
   the `--into` project at generation time. The spec delta for
   `step-import` does not mention the generator. Not decided here.
2. **`input` as a class-body child name.** D5 flags a `Name` whose id is
   a denied built-in "in any context"; Poleni-1709 (both checkouts, 11
   each) and Pascaline-module (2) declare a child `input = InputSector()`
   / `InputArbor()` and write `input.turn.drives(...)`, which binds and
   reads a class-local name, never the built-in. The rule as specified
   reports them. A Store-context exemption plus names bound in the same
   file would clear them, but would change the ratified rule; left as
   specified.
3. **The preamble** gains one word over design.md's sample, "Vet
   *statically* checks what this project declares; …", because the
   spec requires the preamble to state that vet is a static check; the
   rest is the sample's text and wrapping.
4. **An import-bound name is not the built-in.** The dynamic and denied
   built-in rules, and the `open` rules, skip a name an import statement
   binds (`from re import compile` then `compile(p)`), since it is then
   not the built-in the spec names. Narrower than "any context" read
   literally; reviewer's call.
5. **ADR-148 status** is written `Accepted` with a ratification line
   citing the pilot's decisions of 2026-09-26; adjust if the review gate
   wants `Proposed` until integration.
6. **Red-first gaps**: 5.10's two tests were green before 5.12 (the
   tests tier is membership, implemented in 3.5/4.4), and section 8's
   tests were written after the code they test and proved by mutation
   (section 8 above).

## Review closure (2026-09-26)

The reviewer accepted the implementation with two decisions that change
the ratified planning wording. Both are applied here, red first.
"Needs the reviewer" items 1 and 2 are closed by them, item 3 (the
preamble's "statically") is now design.md's sample text, and item 4 (an
import-bound name is not the built-in) is subsumed by the bound-name
rule.

### Decision 1: a name the file binds is not the built-in (task 5.13)

Planning: `specs/vet/spec.md` states the bound-name rule once, under "A
dynamic route around the declaration is a finding", and "A file write is
a finding" refers to it; scenarios "A child named input" and "A locally
bound compile" are added, and "eval is a dynamic route" and "input is a
denied built-in" now say the module binds no such name. design.md D5
replaces "in any context" with the rule and records the residual (a file
that binds `eval` and also calls the built-in is not caught); the D8
sample preamble reads "Vet statically checks what this project
declares; …". Fixture `tests/vet_projects/bound_builtin/` (a class-body
`input = InputArbor()` then `input.turn.drives('output')`,
`from re import compile` then `compile(pattern)`, `def f(help): return
help`) is added to task 3.2.

Red:

    python -m pytest tests/test_vet_assertions.py -q -k binds
    AssertionError: Items in the first set but not the second:
    ('sim/model.py', 33, 'denied-builtin', 'input')
    ('sim/model.py', 32, 'denied-builtin', 'input')
    ('sim/model.py', 28, 'denied-builtin', 'help')
    1 failed, 25 deselected in 0.09s

(The imported `compile` was already clear: item 4's import-binding
exemption.) Code: `machinome/vet/assertions.py` gains `bound_names(tree)`,
one `ast.walk` pass beside `import_bindings`, collecting every name in
Store or Del context (assignment of every form, `for`, `with`,
comprehension and walrus targets), every `def`/`class` name, every
parameter, `except ... as` names, `match` captures and imported names.
`visit_Name` skips the built-in rules for a name in that set that no
import binds; `visit_Call` judges `open(...)` only when `open` is not in
it. `import_bindings` still drives the dotted-name reach. The dunder rule
is unchanged.

Green:

    python -m pytest tests/test_vet_assertions.py -q
    26 passed, 59 subtests passed in 0.35s
    python -m pytest tests/test_vet_command.py -q
    15 passed in 2.26s
    python -m pytest tests/test_vet_closure.py -q
    15 passed in 0.13s

### Decision 2: import-step refuses a document outside the target project (task 6.7)

Planning: the `cli` delta gains "Import-step command" as a MODIFIED
requirement (the full current text, plus the refusal paragraph) with
scenarios "A document outside the project is refused" and "A document
inside the project scaffolds"; design.md gains D11 (the generation-time
half of D10; warning and generating anyway rejected, because the
scaffold's first construction would fail with the adapters' message
instead of the command's).

Before the change the file had the four `GeneratedModelFaithfulnessTest`
failures of 9.5 (`4 failed, 24 passed`). Red, the new
`ImportStepContainmentTest`:

    python -m pytest tests/test_import_step.py -q -k Containment
    >  with self.assertRaises(SystemExit) as raised:
    E  AssertionError: SystemExit not raised
    FAILED ...ImportStepContainmentTest::test_a_document_outside_the_project_is_refused
    1 failed, 2 passed, 28 deselected in 2.80s

The other two (a document inside the project scaffolds; `--into` in no
project is not judged) are guards and pass before and after. Code:
`machinome/manager/import_step.py` gains `_outside_project(document,
into)`, called in `handle` after the overwrite refusal and before
`os.makedirs`: it resolves the `--into` directory's root with
`machinome.manifest.project_root` (imported inside the function;
`ProjectManifestError` means no project, nothing judged), compares real
paths with `os.path.commonpath`, and on refusal writes, e.g.:

    Error: …/tests/step_project/import_simple.step lies outside the project
    at /tmp/tmpazqb1kc4, and the adapters refuse a source outside its
    project, so the generated model could not construct. Copy the document
    under /tmp/tmpazqb1kc4 and run import-step on the copy. Nothing was
    written.

and exits 1. After the code, the four faithfulness tests and
`test_prints_manifest_lines_and_never_touches_pyproject` (whose scratch
directory holds a `[tool.machinome]` manifest) failed on that refusal as
expected; both now generate against a copy of the document under their
scratch project root (`shutil.copy`, commented: a generated project's
document belongs to the project).

    python -m pytest tests/test_import_step.py -q
    31 passed, 12 subtests passed in 3.20s

The vet ADR's adapters paragraph gains the sentence that `import-step`
refuses at generation a document outside the target project, and its
assertions paragraph notes the built-in rules are waived for a name the
file binds itself. `docs/reference/cli.rst`'s `machinome import-step`
section gains one sentence stating the refusal.

    python -m pytest tests/test_docs_structure.py -q
    7 passed, 110 subtests passed in 0.13s

### Validation and the full suite

    openspec validate vet-the-project --strict
    Change 'vet-the-project' is valid

    python -m pytest tests -q -p no:cacheprovider
    3920 passed, 4 skipped, 53 warnings, 2575 subtests passed in 430.63s (0:07:10)

Against 9.5 (4 failed, 3912 passed, 2574 subtests): the four failures are
gone, and the four new tests (one assertion test, three containment
tests) and one subtest (the new fixture in the every-fixture kinds check)
are added. Against the base (3816 passed): 104 tests added.

### The catalogue rows

`machinome vet --json` re-run read only from each root, as in 9.6:
Poleni-1709, calculators-reconstruction/poleni-1709 and Pascaline-module
now exit 0, one model each, pure, 9 files, no findings. The 9.6 table is
updated in place.


## Rebase onto main (2026-09-26)

Framework main moved from the cycle base d791eaa to 297ce54 while this
cycle ran: `state-the-mate-line` (which took ADR-148, NODE) and
`read-frames-and-mates`, with their Thor validation records. The pilot
chose a rebase. The two cycle commits were replayed onto 297ce54; the
one conflict, both sides appending to `workflow/warts.md`, was resolved
by keeping both entries in order; the vet ADR was renumbered from 148 to
149 with every reference (index, architecture synthesis and map row, the
`vet` spec purpose, the archived note and this record). No source file
overlapped. The full suite was re-run on the rebased state; its counts
are recorded below.

Rebased state, full suite, one run: 3957 passed, 4 skipped, 2681 subtests
(main 297ce54 alone carries the mates cycles; the vet cycle adds its 104).
`openspec validate --specs`: 37 passed.
