# External wrapper cache identity — implementation evidence

## Tested content and scope

Standalone worktree `WTs/external-wrapper-cache-identity`, base
`928ac64c0968838ccedd84dc86336fac125c691b`, planning commit
`93ef04122e0437374d2399f010620083f53c4281`; clean and exactly one commit
above base before implementation. No caller, Studio, workspace, schema or
public API change belongs to this patch. Root cleared adversarial review and
authorized completion after the final expanded selected regression passed.
Integration remains root-owned.

The four actual source-bound adapters inherit one private identity mixin.
After existing source validation and artifact-project discovery, before
artifact paths are assigned, their canonical class component becomes a JSON
pair of qualname and defining real Python source relative to that project.
Constructor/resolved-declaration values retain their existing serialization.
Ordinary Python class components retain their exact historical bytes. No
backend import is required to detect participation. Layout, source tracking,
scoped digests, fingerprints, producer recipes and currency logic are unchanged.

## Red-first witnesses

Using workspace Python, cap 8 GiB, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`:

```sh
python -m pytest -q tests/test_external_wrapper_identity.py
```

Before source edits: **7 failed, 4 passed in 3.70 s** (six failing subcases
and one failing bounded STEP test). All four adapters shared
`Wrapper-6245d2f0ea7a` for different defining files. Real STEP/STL cached
meshes for the original wrapper had volume 192 rather than 24 after the
second wrapper materialized. Two real STEP wrappers did not reach simultaneous
STL/BREP currentness within four bounded passes.

Root review correctly identified that repeated `assemble()` on the same
instances was memoized. The durable bounded witness now constructs fresh
instances and calls both `assemble()` and `build_stls()` each pass; the
unchanged rebuild's producer-count check also uses fresh instances. Cached
BREP volumes are read as well as STL meshes. The strengthened witnesses were
rerun against unchanged primary/base by importing its node package before
pytest collected the absolute worktree test file:

```sh
python -c 'import machinome.node.base, pytest; raise SystemExit(pytest.main(["-q", "-p", "no:cacheprovider", "/home/asa/devel/machinome/machinome/WTs/external-wrapper-cache-identity/tests/test_external_wrapper_identity.py", "-k", "real_step_cache or same_named_native"]))'
```

**3 failed, 1 passed, 8 deselected in 2.99 s**: fresh bounded passes failed to
settle and both native cached originals still had the wrong volume. The
fixture subsequently makes its shared inherited adjustment explicit (scale
1.25), preserving this collision shape.

Root-owned independent `tests/test_external_wrapper_review.py` ran against
explicitly asserted primary node source through importlib/unittest:
**4 ran in 0.244 s, one expected failure**. Sources `a b.py` and `a+b.py`
incorrectly shared their old key. Other baseline invariants passed.

## Green checks so far

First patched focused witnesses: **5 passed, 6 subtests passed in 3.60 s**.

```sh
python -m pytest -q tests/test_external_wrapper_identity.py tests/test_step_node.py tests/test_stl_node.py tests/test_missing_source_file.py tests/test_node_scoped_currency.py tests/test_content_verified_currency.py tests/test_declarative_nodes.py tests/test_mates.py tests/test_mate_contracts.py tests/test_mate_existing_joint.py tests/test_backend_neutral_materialization.py
```

**424 passed, 494 subtests passed in 12.83 s**, four existing build123d
deprecation warnings. Includes real native meshes/BREPs, fresh cache bypass,
source-containment/refusal regressions, ordinary/declarative identity and mate
specializations. A prior smaller run caught an invalid axisless ordinary site
joint in the new fixture; corrected to an explicit z axis without a runtime
change.

```sh
python -m pytest -q tests/test_external_wrapper_identity.py tests/test_external_wrapper_review.py tests/test_cli_lazy_imports.py tests/test_mesh_import_deferred.py tests/test_scad_import_paths.py tests/test_source_set.py tests/test_source_generation.py tests/test_source_census.py
```

**75 passed, 28 subtests passed in 7.61 s**, two existing deprecated render-time
port-binding warnings. This run includes wrapper/helper edits that actually
double geometry, proving stable keys and invalidation followed by volume-192
cached geometry; restored sources rebuild independently. Root's four review
tests separately passed in 0.43 s: full hashes distinguish sanitized-prefix
collisions; realpath aliases share; coincidental ordinary source attributes
leave actual AssemblyNode identity unchanged; a fresh OpenSCAD-wrapper process
imports no OCCT, CadQuery or build123d.

## Expanded final selected regression

```sh
python -m pytest -q tests/test_external_wrapper_identity.py tests/test_external_wrapper_review.py tests/test_step_node.py tests/test_stl_node.py tests/test_missing_source_file.py tests/test_node_scoped_currency.py tests/test_content_verified_currency.py tests/test_declarative_nodes.py tests/test_mates.py tests/test_mate_contracts.py tests/test_mate_existing_joint.py tests/test_backend_neutral_materialization.py tests/test_cli_lazy_imports.py tests/test_mesh_import_deferred.py tests/test_scad_import_paths.py tests/test_source_set.py tests/test_source_generation.py tests/test_source_census.py
```

**489 passed, 518 subtests passed in 17.19 s**, six existing warnings. Includes
explicit inherited STEP scaling and both cached BREP volumes, plus site-joint
and fresh-mate author-key retention across all four adapters.

## Root-owned real Curta acceptance

Caller repository `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`,
HEAD `4aa04b51bf013aab01c43cec4ef4482e7f805c39`, with the following uncommitted
source blobs (freshly verified by root):

- `simulation/registers.py`: `1d4d1d4a0ad659dddf0ac6804597dcb36d30e1c4`
- `simulation/dial_frames.py`: `b97ebe7dc290d9fef636d074582ba1a5a3de68b9`
- `simulation/test_register_mates.py`: `f4be8c08af9b4779c8bfe466cc4820a71b490f50`

Framework content is planning commit plus this reviewed implementation patch.
Final production source blobs (the last base.py edit adds docstrings only):

- `machinome/node/base.py`: `76f808075ebc0221529883e63eedafcbe4ceb3ae`
- `machinome/node/sources.py`: `41bfd4c6f7ab9a5259600021cab297d0fe0cc660`
- `machinome/node/adapters/stl.py`: `baff117487779ac2e5fb58d890c1ddb50de92916`
- `machinome/node/adapters/step.py`: `e64a76a2d55242ad4e3352584bd7d2882e097893`
- `machinome/node/adapters/openscad.py`: `f7344613da22e47f15248443d47d59280557482c`
- `machinome/node/adapters/jscad.py`: `35cd6fa0933fc00dbc95644b7b8fef70d3f0df5b`

Root ran the real CLI sequentially, cap 8 GiB and threads 1, with
`PYTHONPATH=/home/asa/devel/machinome/machinome/WTs/external-wrapper-cache-identity`
and workspace venv `machinome`:

```sh
timeout 600 machinome test simulation/registers.py --faceted
timeout 600 machinome test simulation/registers.py
```

Faceted: **3 passed, 0 failed in 19.00 s**, exit 0. Exact: **3 passed, 0 failed
in 0.36 s**, exit 0. The previously nonterminating build now reaches and passes
its geometry assertions. No caller source was edited by this apply agent.

Root's fresh-process diagnostic instantiated original/framed wrappers,
assembled and called `build_stls()` with `exact._atomic_export` patched:
**zero native exports**, both independent STL/BREP pairs simultaneously current.
The two keys are
`__FittedDialType2_,_simulation_dial_fits.py__-8749d5c096ae` and
`__FittedDialType2_,_simulation_dial_frames.py__-1bf1f9e1e7f9`.
Both STL hashes are
`eeae4bfefeacd59482401adb59995c90fb21da08a120e2bdf16938b76e3a0e88`;
both BREP hashes are
`dfbad7f74cb64aeba321bc34f88bb674235fa025589f5cd9577590c880d7279d`;
volume is 3317.8854523044974. Their adjustments are identical, not a
different-geometry witness. BREP bytes match the prechange BREP. The STL hash
differs from the prechange `b689...` artifact, so no old byte-identical STL
claim is made; geometric acceptance is the CLI proof above.
Root additionally compared canonical oriented-triangle content of the retained
old STL and the new STL through `core.pieces._canonical_content`: they are
exactly equal, with full digest
`8768562b3d85c1d2b6d25409a43bac903d33b9232adec24d1e3842a6f4fee657`.
Thus raw STL bytes differ but canonical mesh/piece content does not.

## Full-suite result and baseline comparison

```sh
python -m pytest -q tests
```

Cap 8 GiB, threads 1, sequential native work: **14 failed, 4060 passed,
4 skipped, 2886 subtests passed in 399.95 s**, 53 existing warnings. This is
not a green full-suite claim. Eleven failures match the previously recorded
missing vet fixtures; three newly exposed markings assertions required a
reviewed semantic correction for the ratified identity change.

The three new failures were
`tests/test_markings.py::SolidIdentityTest::test_a_marking_does_not_key_the_artifact`,
`SolidIdentityTest::test_the_faceted_solid_is_byte_identical_too`, and
`OpenScadPathTest::test_the_scad_is_what_it_is_without_the_markings`.
The first two compared keys across different external-wrapper defining
modules, which now intentionally differ. The last refused any `marking`
substring, including the legitimate `markings_project` source origin in an
artifact filename. No solid-byte or piece-identity comparison failed.

Unchanged primary/base was tested with the exact three node ids and all four
vet files, using workspace Python and the same memory/thread limits:

```sh
python -m pytest -q -p no:cacheprovider tests/test_markings.py::SolidIdentityTest::test_a_marking_does_not_key_the_artifact tests/test_markings.py::SolidIdentityTest::test_the_faceted_solid_is_byte_identical_too tests/test_markings.py::OpenScadPathTest::test_the_scad_is_what_it_is_without_the_markings tests/test_vet_assertions.py tests/test_vet_closure.py tests/test_vet_command.py tests/test_vet_isolation.py
```

**11 failed, 52 passed, 59 subtests passed in 6.58 s**. The three old markings
assertions pass on base, confirming the new-key interaction. All eleven vet
failures reproduce with the same unresolved/missing nested fixtures, including
`sim.parts.gear`; these remain unrelated and unmodified.

Root approved a test-only semantic correction: real `FixturePlate` markings
are temporarily set to `None` through `ExitStack`, asserting discovery becomes
empty, its same-author key remains unchanged, and declarations restore. The
cross-module STL bytes and piece identity remain compared, with distinct
external-wrapper keys now expected. SCAD normalizes only complete exact quoted
solid artifact paths (each appears once), retains strict whole-code equality,
and explicitly excludes `.marking-` decal artifact imports. No production
behavior changed to accommodate these tests.

Root also requested unchanged fresh rebuilds for the genuinely different
native-adjustment cases: both now call `assemble()`/`build_stls()` on fresh
instances with exact and STL producers patched, asserting zero exports and
both current. New fixtures, independent review and the whole markings module:
**116 passed, 68 subtests passed in 7.37 s**, four existing warnings. Root
explicitly requested a final expanded selected rerun rather than another
full native run after these test-only changes.

## Documentation checks and disposition

Root accepted source/design review before ADR extraction. ADR-155 extends
ADR-026/063 narrowly; the architecture, ADR index and a dated ADR-026 extension
record only the external-wrapper qualification. No reader manual or Studio API
change is needed. The wart gains measured resolution without rewriting its
original failure.

From each checkout's `docs/`, with a distinct temporary output directory:

```sh
sphinx-build -b html -E -W --keep-going -q . <temporary-output>
sphinx-build -b html -n -E -W --keep-going -q . <temporary-output>
```

Ordinary strict build: exit 0, no warnings on WT and unchanged base. Nitpicky
build: exit 1 with the same five baseline warnings on each: missing targets
`AssemblyNode.simulate`, `AssemblyNode.time`, `name keyword`, and the prose
return labels in `Sim.initial`/`Sim.state`. These are not repaired or described
as a fully green nitpicky build.

## Completion record

Final expanded selected command is the 18-file command above plus the whole
`tests/test_markings.py`: **591 passed, 574 subtests passed in 20.59 s**, six
existing warnings. Root reviewed the actual final fixture diff, native
zero-producer assertions, production/docs/ADR and caller evidence and cleared
completion. The two delta specs were intelligently merged and verified against
their baselines, preserving all unrelated requirements/scenarios. Workflow
note archival corrects its historical status and relative wart link.

OpenSpec is archived at
`openspec/changes/archive/2026-09-27-external-wrapper-cache-identity/`, with both
baseline specs synced and ADR-155 linked to the archived record. The supported
archive CLI warned that only the final workflow validation/commit task remained;
root had explicitly authorized that ordered completion, and this task is now
completed in the implementation record.

Post-archive checks:

```sh
python -m pytest -q tests/test_external_wrapper_identity.py tests/test_external_wrapper_review.py tests/test_markings.py tests/test_missing_source_file.py tests/test_cli_lazy_imports.py
openspec validate --all --strict
git diff --check
```

**154 passed, 88 subtests passed in 8.80 s**, four existing warnings;
**37 baseline specs passed, 0 failed**; diff whitespace clean. This is the
single implementation completion commit after the planning-only commit.
Root owns integration/teardown and post-integration checks. Nothing was pushed
or published, and no caller or Studio file was changed by this apply agent.
