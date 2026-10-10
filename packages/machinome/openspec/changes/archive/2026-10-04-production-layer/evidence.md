# Production-layer implementation evidence

## Bench and authority

Implementation follows the pilot's explicit end-to-end authorization, without
an additional ratification pause. The planning-only bench was rebased onto
completed source commit `e570068287c56e84f6ccb4ed73f0bae7bed5a07c`, validated
with `openspec validate production-layer --strict --no-interactive`, and was
clean exactly one commit beyond that base before apply. Parent amendments keep
planning coherent; frozen validation HEAD is
`41d24cef37817f2a8c0c79ea9014eb93b77a0261`. At that checkpoint implementation
was uncommitted pending parent review; the completion commit containing this
record is separate from planning. No integration or publication.

## Red-first implementation

The focused commands use the workspace venv Python, `PYTHONPATH=.` and the
production framework WT as cwd. Tests were run against actual implementation
paths, not mocks substituting production outputs.

- `pytest tests/test_model_consumption.py -q`: initial collection failed with
  missing `machinome.model`. Subsequent regressions prove actual inherited and
  constructor-created child identity, omitted/empty repetitions, fusion/flexible
  boundaries, malformed rest render refusal, runtime-read refusal, running bank
  preservation and source/artifact invalidation.
- `pytest tests/test_production.py -q`: initial collection failed with missing
  `machinome.components`. Later red assertions exposed wrong constructor inputs,
  mutable captured declarations, raw HTML/FTP Markdown acceptance, reserved
  output-field shadowing and imported Step attribution to the consuming rather
  than defining module. Each failure was corrected and rerun green.
- `pytest tests/test_vet_universe.py tests/test_vet_assertions.py -q`: the valid
  production-writer fixture initially returned no denied-import findings instead
  of the two expected effectful imports. Narrow universe classification fixes
  this without denying pure Reference/component/recipe declarations.
- `pytest tests/test_production_documentation.py -q`: initially failed because
  defining-module production documentation was absent, then passed.

Final pre-lint frozen focused command:

```sh
PYTHONPATH=. /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_production.py tests/test_model_consumption.py tests/test_vet_universe.py tests/test_vet_assertions.py -q
```

Result: **89 passed, 62 subtests, 4 warnings, 6.72s**. The warnings are existing
build123d deprecations. Documentation/structure/class-name scan command with
`tests/test_production_documentation.py tests/test_docs_structure.py
tests/test_no_class_name_recognition.py`: **15 passed, 218 subtests, 4 warnings,
4.80s**. `git diff --check` passed. Parent's final full suite and requested lint
cleanup remain separate checkpoints; these counts do not claim their result.

The unchanged rebased baseline command covered state_binding, builder_lifecycle,
pieces, sheet_leaf, source_generation and scad_presentation before product edits:
**152 passed, 30 subtests, 9 warnings, 120.40s**. This is baseline evidence, not
final implementation proof.

## Empirical consumers

Independent Curta implementation commit:
`bab7c156b50bf672f54021479f3caf500ecf11ae`, base
`fb4708e98463b3cb4c0130cc3e92514c2a31155b`. Its project-owned
`production/evidence.md` records primary author spreadsheet/manual URLs,
2026-10-04 retrieval, exact mounted paths, supplier DIN934 M4x0.7 dimensional
evidence, unknown polymer, fifteen made-wire springs (not purchased parts), the
one author retaining spring represented by five mixed patches, and open
simulation-fit/mounting/whole-model geometry acceptance.

The actual public-only profile supplies four printed crank units and seven
nuts, with fifteen wire occurrences deliberately unassigned. Two crank units
are SeatedMainCrank/SeatedCrankGrip simulation-fit replacements, not original
author STL geometry. No simulation source changed. The final paired production
and narrow remaining/transmission-mate run passed **12 tests, 6 subtests,
100.25s**. Framework package SHA-256 was equal before/after:
`43628972f1a4458c5938f673c341fc9c0caadfe42397b8f1b8e61e6badab9738`.
Tested project tree `bcb6da65a05a446bf46d5473af6875cfb45b9f99`; committed tree
`e17dfd7d58f50c72b9989e41808614f0d49d03de` adds final evidence only.

Cut evidence uses `tests/sheet_project/frame_panel.py`, the historical exact
6mm authored-profile sheet fixture retained from ADR-053/metamaquina-rebuild.
The new production test proves four nominal-DXF quantities and lazy stock.
It does not claim the live Metamaquina2 ScadPart provides DXF, and migrates no
project geometry or model source.

## Distribution and documentation

`python -m build --wheel --sdist --no-isolation` failed because installed
setuptools84 violates the declared build requirement `<77`; no requirement was
weakened. The supported isolated build passed with setuptools76.1.0 and produced
both wheel and sdist under `/tmp/machinome-production-dist-isolated`.

A throwaway Python venv outside the checkout installed the wheel with
`pip install --no-deps`. Defining-module Standard/Production/Printed/Material
imports and `Printed(None)` passed without importing numpy, OCP, cadquery,
build123d or molejo. The same venv then installed only declared default wheel
dependencies, without extras. Simulation-only Sim/Driver imports passed;
OCP/cadquery/build123d/molejo were absent and no production module was imported.
These are installed-wheel import smokes, not manufactured geometry claims.

Strict Sphinx `-b html -n -W --keep-going` generated HTML but exited 1 on five
existing cross-reference warnings: AssemblyNode.simulate/time, old `name
keyword` prose, and Sim.initial/state prose interpreted as types. No warning
originated in the new production section. This environmental/baseline limitation
is reported rather than represented as a successful strict manual build.

Baseline confirmed independently: `git archive
e570068287c56e84f6ccb4ed73f0bae7bed5a07c` was extracted into
`/tmp/machinome-production-docbaseline.VZ041Z`; the same venv and
`PYTHONPATH=. python -m sphinx -b html -n -W --keep-going docs
/tmp/machinome-production-docbaseline.VZ041Z/html` also exited 1 with exactly
the same five warning targets. Baseline api.rst lines23/35/76 shifted with the
new section, and the Sim docstring warnings were unchanged. No baseline
checkout was modified and no unrelated warning was suppressed or repaired.

Framework manual records defining-module imports, lazy costs, partial draft
coverage, unknown mass/material, restricted attributed Markdown, direct-binding
provenance and immutable result contracts. Finding.check_status describes only
the represented structural check; export explicitly requests geometry/mass.
ADRs174/175 capture the confirmed architecture. Studio follow-through and final
archive/commit/full-regression results are recorded by their owners before close.

## Final source checkpoint after review cleanup

The first full regression run reported **2 failed, 4433 passed, 4 skipped,
3672 subtests, 55 warnings, 670.42s**. Both failures correctly rejected the new
paragraph in the released status page (`test_profile_documentation` and
`test_release_records`). That paragraph was removed by restoring the exact old
hunk; released status remains unchanged, while development capability stays in
the API and Unreleased changelog. No test was weakened.

Scoped flake8 initially reported119 issues. Black's scoped79-column formatting
was proved AST-identical across all16 selected files before/after. Explicit
cleanup removed unused imports/locals and an unused pure reference-path
computation, moved one test import, and used a named remaining slice to avoid
Black's E203 conflict. Wrapped strings retain content; four docstrings were
shortened. No model/production semantic redesign occurred. Final scoped
`flake8 machinome/model.py machinome/components.py machinome/production
tests/test_production.py tests/test_model_consumption.py
tests/test_production_documentation.py --count --statistics` returned **0**.

The final focused command adds profile-documentation and release-record tests
to the contract/vet/docs/class-name suite: **115 passed, 337 subtests,
4 warnings, 9.32s**. `git diff --check` passed. Python was frozen again for
parent's final full regression and the independent final-generation Curta rerun.

Studio API follow-through is committed independently as
`4f161c89929a057ea7557676ef21d8f8c2c0129e`; skill validation,17tests and
diff checks passed. Its isolated branch is clean, not integrated or pushed.

The final frozen source was rebuilt with the isolated wheel+sdist command into
`/tmp/machinome-production-dist-final`, successfully. Wheel SHA-256:
`2f4fafdd522124fa47a5081d87a0d8bc29e0be2b2c52eaff17845e256325fd90`;
sdist SHA-256:
`b71d888e38f660b0720aa7a3d45149b83b9999c90473949eaa494c8b233064e0`.
The final wheel passed both installed smokes again, outside every checkout:
dependency-empty defining-module authoring in a fresh venv, and simulation-only
Sim/Driver import in the default-dependency venv with OCP/cadquery/build123d/
molejo absent and no production imports. These results supersede the pre-lint
distribution checkpoint above. No distribution was uploaded.

Final Python-package fingerprint (`rg --files machinome -g '*.py' | sort |
xargs sha256sum | sha256sum`):
`4c60b1115f303d30a6a5cfcc00376cf9292a5be7a4a70932244c0609e76153d5`.
Parent owns the final full-suite result, independent rerun linkage, task6.3,
supported archive and second implementation commit.

## Numeric conformance correction after full-suite checkpoint

Parent's full suite on package `4c60b111...` passed **4435 tests,4 skipped,
3672 subtests,55 warnings,668.37s**. That complete regression checkpoint
precedes the final narrowly scoped numeric correction; no third whole-suite
run is claimed.

Public-path real native24mm³ geometry reproduced three red failures: finite
density1e308 incorrectly yielded infinite grams instead of2.4e303; positive
density1e-320 yielded known zero after underflow; two explicit measured1e308g
occurrences published an infinite subtotal without refusal. Exponent-scaled
frexp/ldexp multiplication avoids intermediate overflow and divide-first
underflow. Unrepresentable positive mass retains an unknown basis; nonfinite
subtotals raise contextual OverflowError. No density/volume physical limit or
new API was introduced. A real1000³mm box checks truly unrepresentable output.

Final tests also retain export's existing ProductionExportError wrapper, assert
its contextual message and OverflowError cause, and prove neither destination
nor temporary stage remains. The first assertion expected an unwrapped error;
review corrected that test to the existing export contract without changing
production's exception handling.

Final whole focused group: **119 passed,337 subtests,4 warnings,10.51s**;
the last added no-stage assertion also passed independently. Scoped flake8
returned0 and diff checks passed. Parent reviewed exact pre/post source: only
the mass arithmetic block changed. Final package fingerprint:
`cba98e7237076f001503e3e0f5aff55ff35cbaa18476de18feff85a534924ffa`.
Distribution hashes and final Curta validation follow this frozen generation.

After the final export assertion, isolated wheel and sdist were rebuilt into
`/tmp/machinome-production-dist-approved`. Final wheel SHA-256:
`c299ffcd84cbcb9cc52663c0ecec3d16fa40726e07f0e95c438f6ba3657c3e8b`;
final sdist SHA-256:
`4e2a75b753dd1ab5c66dc574038a356790271aa65c6715808655dd1c261b031b`.
The rebuilt wheel passed dependency-empty production authoring and default-only
simulation imports again in the outside-checkout environments described above.
These final artifact hashes supersede earlier distribution checkpoints.

## Final independent acceptance

The parent independently reran the final focused suite including the complete
export-cleanup assertion: **119 passed, 337 subtests, 4 warnings, 9.90s**.
The independent Curta consumer then reran production plus remaining/transmission
mate tests: **12 passed, 6 subtests, 97.55s**. Its verified imported framework
paths belong to this worktree, and package SHA-256 `cba98e723...924ffa` matched
before and after. Curta implementation remains `bab7c156b50bf672f54021479f3caf500ecf11ae`;
later project changes are evidence-only. No simulation or Curta2x changes.

All 46 active OpenSpec/spec items passed strict validation before archival.
The parent compared every new baseline requirement to both deltas. The separate
implementation-review.md records review disposition, full-suite versus final
focused evidence, accepted ADRs, independent repository commits and the absence
of integration/publication authority.
