# Native FreeCAD adapter: primary adversarial review

Status: accepted for the explicitly corrected Dum-E source after the approved
revision, independent simulation and primary reruns. The original remains
rejected; earlier failed gates are preserved below as history. Experimental,
unreleased and not integrated into adapter main. 2026-10-01.

Origin: Dum-E must consume authored FreeCAD joints and limits without a second
mechanical definition. This review belongs to `native-freecad-assembly` in
the LGPL adapter repository, not to the Apache framework. The independent
Dum-E simulation author was dispatched after the adapter review and correction
checks passed, using only the package's documented public API.

## Reference state and independently executed checks

- Adapter planning commit: `73d6b553c47140070301a9d9c8070137e5b2208d`.
- Framework: `8a8a26711bcd7fd33c6daf7f8866d10004574f8c`, source 0.7.1.
  Primary framework checkout remained clean after the baseline checks.
- Core baseline: `tests/test_step_node.py`, `test_step_assembly.py`,
  `test_mates.py`, `test_joints.py`, `test_running_simulation.py`,
  `test_running_stops.py`, `test_export.py`, `test_source_generation.py`:
  578 passed, 2 skipped, 730 subtests passed in 36.55 seconds. These ran with
  the workspace interpreter, whose old editable distribution metadata still
  says 0.7.0; the source commit above, not that metadata, identifies the test.
- The same core regression selection was then rerun with the adapter's isolated
  interpreter and matching 0.7.1 distribution metadata: **578 passed, 2 skipped,
  2 expected deprecation warnings, 730 subtests in 38.71 seconds**. The core
  checkout remained clean.
- Adapter checks use its isolated `.venv`, with matching local 0.7.1
  distribution metadata. The first two native public API tests were rerun
  independently: 2 passed in 6.77 seconds. Synthetic native maximum 180
  completed a 150-degree command; maximum 120 blocked at 120.
- Public import and class declaration with `MACHINOME_FREECAD_ROOT` unset
  passed and did not import `FreeCAD` into the host interpreter.
- A synthetic exact leaf's `shape()` returned a valid 192 mm3 solid through
  native BREP transfer. An ordinary `machinome build` in `tests/` exited 0
  and generated the usual exact-solid and SCAD artifacts.
- Primary full adapter run at 09:52 UTC: 40 passed, 1 failed in 99.92
  seconds. The sole failure was the prior-artifact publication-race test:
  its second materialization was already current, so it never injected a
  publication race. The test must force a new recipe generation while retaining
  the previous outputs before it can establish rollback of those outputs.
- Corrected rollback regression independently rerun: 4 passed in 13.73 seconds
  (changed/deleted source, with/without prior outputs). Final full suite
  independently rerun: **44 passed in 103.90 seconds**.
- Primary also reran `scripts/smoke_dist.py` against the recorded core source:
  wheel/sdist member inspection, physical Machinome 0.7.1 and adapter wheel
  installation into an external temporary environment, blocked/120 public
  simulation, and ordinary build all passed. Nothing was uploaded.
- After the diagnostic-only correction, the primary reran the entire current
  adapter suite: **52 passed in 103.95 seconds**. This includes the eight added
  diagnostic tests, not just the earlier 44-test suite.

The native runtime is the provisioned official FreeCAD 1.1.4 AppImage,
SHA-256 `f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434`.
Its native `Part.OCC_VERSION` reports `7.8.1`; exact transfer was checked
against the framework's OCP 7.8 bindings, not a cross-major compatibility claim.
The primary's project-local, ignored probes opened original Dum-E through
FreeCAD without saving it. Native `assembly.solve()` returned 0, with maximum
observed saved/resolved translation drift about 7.56e-14 mm and zero reported
orientation drift. The two upstream CAD hashes still matched the workflow
record afterward.

The native motion oracle successfully moved the turntable from about
39.7391947543 to 49.7391947543 degrees while holding the other three revolutes
at their saved coordinates. `Motion.Formula` uses radians;
`generateSimulation` returns 0, while Python `updateForFrame` returns `None`.
This is native-oracle groundwork, not adapter/Dum-E motion parity.

## Findings and dispositions

1. **Native unit API mismatch.** The initial worker compared `str(Unit)` with
   `"deg"` and read `.Value` from `getValueAs("deg")`. A runtime probe showed
   that the former includes a descriptive unit signature and the latter
   returns a float. The implementation now compares with `App.Units.Angle`
   and converts the returned float. The public native tests pass this path.

2. **Canonical linked-path cache blind spot.** Checking only previously
   resolved canonical filenames could miss an external symlink switching to
   another document. The implementation agent reports replacing this fast
   path with native discovery and authoritative loading on each fresh
   construction. The primary full suite passed the relink regressions, and
   the public guide records two native processes per fresh model.
   A subsequent primary native probe
   copied the synthetic assembly into a temporary directory and symlinked its
   `Parts.FCStd`: native `Document.FileName` retained that logical filename.
   The worker's own `.resolve()` had discarded it. Preserve both spellings
   and targets through the source-generation checks to cover relinking during
   loading and publication, not just before fresh construction.

3. **External parts outside the assembly's directory.** `Path.relative_to`
   would reject a normal `../parts/` dependency even within one project.
   This was changed to a stable relative-path identity. The primary full suite
   passed the native sibling-directory and source-preserving relocation test.

4. **Native recipe versus artifact currency.** A fresh snapshot does not by
   itself invalidate existing BREP/STL/SCAD when the native runtime or importer
   recipe changes with unchanged CAD and wrapper source. The initial exact
   leaf inherited currency based only on those files. The agent reproduced
   this with a native recipe replacement and changed solid. The adapter now
   incorporates native snapshot/recipe into ordinary currency, not structural
   identity. A second failure exposed the core exact-shape cache's path/mtime
   key returning the old 192 mm3 shape after a 384 mm3 rewrite with equal
   timestamps. The adapter evicts its rebuilt BREP through the existing cache
   helper. The primary full run independently passed that regression.

5. **A render-once guard is not a producing-phase guard.** The initial native
   source observation check lived only in the assembly's authored `render`.
   Core `AssemblyNode._rest` caches that method after the first call. A
   post-render source edit therefore needs coverage at actual producing
   boundaries; otherwise old in-memory data might be stamped as current.
   Raw source receipts now guard currency and exact geometry consumption.
   The primary full run passed changed-source and relinked-source regressions
   after an earlier render. Reinterpreting an active run is not requested.

6. **Reference shape is not reference resolution.** Native
   `UtilsAssembly.isRefValid` validates a reference's container/strings, not
   the existence of its subelements. Explicit native subelement resolution
   was requested and added; the primary full run passed the missing-edge
   native refusal fixture.

7. **Parity tolerance must be literal.** `pytest.approx(..., abs=...)` retains
   its default relative tolerance. The claimed strict native parity needs
   `rel=0` or explicitly computed translation/orientation errors. Final
   evidence must report measured errors, not just a nominal assertion value.

8. **Snapshot adoption race.** Recapturing source observations after a native
   load could associate old resolved mechanics with a new file generation.
   The runtime now returns the admitted receipts with the immutable snapshot;
   the assembly adopts and checks them without recertification. The primary
   full run passed the change-immediately-after-load regression.

9. **Publication is earlier than phase completion.** A source change injected
   inside the core exact writer's currency publication was eventually refused
   by the phase guard but left artifacts from the failed generation. The
   adapter now backs up/restores only its leaf's BREP/STL and their two currency
   sidecars. Both prior-output byte-identical restoration and no-prior-output
   cleanup passed independently for source replacement and deletion. This is not a
   cross-process atomic transaction: generated files may exist transiently.
   Review also found source deletion raised `FileNotFoundError` instead of
   `SourceChanged`, bypassing the scoped rollback. The correction chains the
   original observation error into `SourceChanged`; deletion regressions now
   pass too. The Apache core remains unchanged.

10. **Restored timestamps need changed mechanics.** Replacing a file with
    identical bytes proves metadata detection but not refreshed geometry.
    The regression now replaces the linked native solid with a genuinely
    taller solid, pads the test ZIP copies to equal size, and restores mtime
    below a newer root timestamp. The primary run passed the measured
    192-to-384 mm3 change. Padding is test setup, not a production FCStd parser.

11. **Refusal diagnostics must identify the native machine.** Final spec/code
    comparison found graph and solver refusals that gave only a generic reason
    or status. They now include the source path, assembly Name and candidate
    native occurrence/joint Names. No valid-source admission behavior changed.
    The primary independently ran the diagnostic assertions and existing native
    refusal fixtures: 14 passed, 21 deselected in 15.55 seconds. Injected worker
    status checks are labelled as diagnostic tests, not native solver evidence.

12. **Independent native preparation is itself a proof obligation.** The
    project author first produced copies with incorrect relative external-link
    spellings after `saveAs`; explicit preloading of the parts hid that error.
    After the link correction, saved variants still had null Joint proxies
    without restoration metadata. The adapter refused both forms rather than
    inventing missing mechanics. The implementation agent's read-only diagnosis
    confirmed that original and untouched closure-first copies restore all
    eight Joint proxies and solve with status 0; those invalid saved variants
    did not. No adapter change was made. The author corrected preparation by
    copying the closure together before native editing and explicitly loading
    the installed native `JointObject` classes before document restoration.
    Fresh automatic reopening must verify both closure and proxies. Native
    motion status 0/frame count alone was also insufficient: the reference
    now needs to assert the actual requested joint angles before admitting its
    pose output. These are native-authoring/reference failures, not passing
    adapter evidence or upstream modifications.

13. **Native motion must preserve the fixed graph as well as target angles.**
    The independent reference reached turntable zero but initially left the
    fixed shoulder behind, changing their relative orientation by about
    39.739 degrees. All eight native proxies were restored and the diagnostic
    ASMT included the fixed connection. Recomputing after frame playback
    changed both that relative pose and the requested turntable coordinate;
    it was therefore rejected as a correction. Neither a zero solver status,
    the right frame count, nor one correct endpoint establishes a valid native
    reference. Full native target and fixed-relative invariants remain required
    before accepting moving-pose parity. This is an unresolved reference
    investigation, not permission to weaken acceptance. Official GUI
    `AssemblyWorkbench` initialization and native `Simulation`/`Motion`
    classes under Xvfb reproduce the discrepancy: generate status 0, six
    frames, target approximately zero, but fixed-relative yaw changes from
    90.0000093347 to 129.739204089 degrees. The primary's old angle-only
    probe also leaves the shoulder behind on a positive 10-degree move.
    The primary measured the untouched fixed joint's global connector-frame
    discrepancy at about 90 degrees; other fixed connector frames align.
    Source consistency and adapter admission must be reconciled before
    acceptance. No native source repair or runtime patch was performed.

14. **Critical: successful solve and stable saved poses are not sufficient
    admission checks.** Read-only implementation-agent review confirmed the
    native Fixed convention in the pinned
    [OndselSolver FixedJoint implementation](https://github.com/FreeCAD/OndselSolver/blob/30e9b64e8bf881d438d4b88834f9ba3674865418/OndselSolver/FixedJoint.cpp).
    Its connector direction-cosine constraints target zero, not an arbitrary
    saved relative orientation. After recompute and `solve()==0`, Dum-E's
    `Joint002` still has an angular residual approximately -1 rather than zero.
    The primary independently observed its approximately 90-degree connector
    mismatch and inspected the pinned constraint implementation. The current
    adapter admits this source and preserves its saved relative occurrence
    placement, which is not proof that the authored native constraint is
    satisfied. This is an **unfixed adapter admission defect**, not merely a
    bad test oracle. The 52 passing adapter tests do not cover it. Fail-closed
    residual validation and reconciliation of the source/runtime discrepancy
    are required before acceptance. Why FreeCAD reports success is not yet
    established; neither a source repair nor a solver patch is silently made.

The primary inspected the project's generated `snapshot-rest.png` and
`snapshot-posed.png`: the full arm, base and phone holder are visible, and the
posed view shows articulation with connected components. These ignored images
are visual evidence only; they do not settle the numerical reference issue.

## Originating-project gates established independently

The single project author recorded `simulation/evidence/independent-gates.json`
in the independent Dum-E repository, explicitly withholding moving-pose parity.
The primary reviewed the numerical record and independently reran its two
public simulation tests: **2 passed in 9.80 seconds**. Four physical joint
coordinates are present; a turn-only command preserves the other three saved
values, and all four declared operating inputs execute through the public API.

The project author subsequently converted the tests to public `TestCase`
ownership, added exact-solid checks and retained an explicit native-moving-pose
acceptance test. Its final pytest result is **3 passed, 1 failed**; ordinary
exact-contract invocation reproduces the parity failure. The earlier two-test
green result is historical subset evidence, not the current project verdict.
The project report and `simulation/evidence/status.json` retain the headless
and GUI failures, original hashes, provisional limit observations, corrected
STEP/adapter agreement and snapshot identities. The single validator has
finished its handoff without repairing CAD, syncing, archiving or committing
the incomplete implementation.

Both native variants use the same `active.FCStd` path and wrapper SHA-256
`39d55245a9a08b9a468cd67cb37c17a3eccf4b92e181c4160776da5ffbcd5b9b`.
The only measured joint semantic change is `Joint001.AngleMax`, 180 to 120.
The unchanged 150-degree command completes at 150 for the first and is blocked
at 120, with 30 degrees remaining, for the second. Native realization took
3.31/3.23 seconds and exact builds 2.18/2.01 seconds in that run. Fresh automatic
reopening resolves only the project-owned copied closure. All nine variants'
own-frame volumes/bounds and saved placements agree within the stated
tolerances; BREP serialization bytes need not be identical. This establishes
semantic-limit refresh under the current provisional admission, not full native
motion parity or acceptance of a mechanically consistent source. Finding 14
qualifies these passing observations.

The primary rechecked the original submodule: clean, with both original FCStd
hashes unchanged. No upstream CAD, joint, offset or placement was saved over.

## Known boundary, not silently repaired here

Machinome 0.7.1's `vet` universe does not list `machinome_freecad` or the
`freecad_source` attribute. This is an empirical integration finding for a
separate framework decision, not authority to modify or bypass the checker.
Do not describe this experimental adapter as accepted by that version's
purity checker. Native process separation is ABI/process isolation, not a
security sandbox: restored FreeCAD documents can execute Python proxies and
must be trusted.

## Studio contract disposition

The existing Studio-owned framework API skill is deliberately unchanged in
this cycle. This is a new, unreleased optional package, not a core public API
change, and the framework's current `vet` contract does not admit it. Its own
public API/runtime guides are the authoritative supplement explicitly supplied
to the independent project author. No Studio profile, dependency declaration
or general support claim advertises it. A separate Studio adoption change
must decide installation and the unsupported `vet` boundary before advertising
this capability to ordinary floor agents. This is the explicit coherent
deferral allowed by task 7.6, not a claim that Studio integration is finished.

## Historical held acceptance before the approved revision

The negative/source-race, artifact, code review and distribution gates have
passed. One separate Sol 6.1 agent authored and simulated Dum-E using
documented public APIs only. The unchanged-code 180/120 limit experiment and
inspected visual evidence are established; full native moving-pose parity is
not. The corrected STEP control agrees with the adapter, which is not an
independent native reference. No fixture success is a substitute for that
originating-project proof. The two-commit empirical workflow requires a pilot
decision before changing the source/acceptance contract. Keep the cycle open,
implementation uncommitted, baseline unsynchronized and architecture unpromoted.

## Approved revision and isolated dependency checkpoint

The pilot subsequently approved correcting the project-owned native assembly
and requested a durable project issue register. The primary reviewed both
revised OpenSpec changes. Adapter planning commit `dd2cba0` replaces the earlier
`73d6b55` planning state; only planning artifacts were staged for the amendment,
and all implementation and historical evidence remained uncommitted. Strict
validation passed with zero issues. The implementation gate is now released
for native residual refusal and independent project-owned correction, not for
a FreeCAD fork, runtime patch, upstream change or Python replacement mechanics.

The original pinned source must be refused naming inconsistent `Joint002`.
The repaired source must independently satisfy native constraints and preserve
its nine saved occurrence poses and geometry before all motion, limit-only
and STEP gates are rerun. Project issue IDs and reproduction/resolution links
belong in Dum-E's `docs/issues.md`; passing repaired evidence cannot erase the
original failure. No sync, archive or completion commit is permitted until
these gates and primary review pass.

The independently advancing core primary is now at `3e071c2`. Validation retains
the recorded `8a8a26711bcd7fd33c6daf7f8866d10004574f8c` dependency in the clean,
detached `machinome/WTs/freecad-compat-8a8a` checkout. The isolated adapter venv
was relinked to it. Its dependency-path bridge initially let the workspace's
old editable path take precedence; correcting only that venv's ignored `.pth`
restored the intended import. Actual `machinome.__file__` now names the detached
checkout and distribution metadata is 0.7.1. The shared workspace environment
and all core source remain unchanged. This extra import-origin check is needed:
distribution metadata alone did not identify the code being tested.

Primary independently reran the eight-file core regression selection in that
detached checkout using the isolated adapter interpreter: **578 passed,
2 skipped, 730 subtests passed in 31.15 seconds**, with the same two expected
deprecation warnings. This establishes the frozen compatibility baseline;
adapter residual and repaired-project validation remain separate pending gates.

The independent author's native correction writes only `Joint002.Offset2` in
the copied closure, composing the previous offset with the measured second-to-
first connector transform. The primary reviewed the original preparation tool
and `simulation/evidence/correction.json`: only Offset2 and its native-derived
Placement2 change mechanically. All original saved poses, coordinates and
own-frame solids remain equivalent; maximum measured translation is about
9.66e-14 mm, bounds difference 1.39e-13 mm and volume difference 1.09e-11 mm³.
Reopening only the copied assembly restores its own linked closure and proxies.

Primary independently ran the native oracle on that corrected source at
turntable/shoulder/elbow/wrist targets **90 / 10 / 120 / -30 degrees**. All four
targets were reached within 1.5e-14 degrees. All eight connection residual
checks passed; largest reported connector translation was 5.86e-14 mm, and
fixed-relative translation drift was at most 7.30e-14 mm with zero reported
orientation drift. Grounding was unchanged. The ignored numerical receipt is
Dum-E's `.tools/primary-corrected-reference.json`. This verifies native repair,
not yet full adapter parity. Both original CAD hashes were independently
rechecked unchanged, and the upstream submodule remained clean.

Primary then exercised only the public adapter/project API against that native
receipt. The untouched `OriginalSource` refuses `Joint002` with source, Fixed
type, both endpoints, measured approximately -1 direction-cosine residual and
explicit tolerances. Corrected `DumE` reaches 90 / 10 / 120 / -30 degrees;
all nine world poses agree with the independent native receipt to at most
2.59e-13 mm and 1.71e-6 degrees. The state contains four physical joint entries
and four operating drivers, not extra alias coordinates. This focused primary
handoff check releases the independent author's full public validation batch;
it does not replace the required complete corpus, limit refresh or STEP proof.

## Revised independent project proof

The single independent author completed `simulation/tools/evaluate.py` through
the documented public API. Primary inspected the tool and its recorded
`simulation/evidence/empirical.json`. Eight moving cases cover turntable
0 / 45 / 90 / 150 degrees, each remaining coordinate and simultaneous motion.
All nine occurrence poses agree with native FreeCAD to at most **5.1539e-13 mm
and 2.41484e-6 degrees**. The native subprocess asserts its target coordinates,
all eight connector checks, grounding and all fixed-relative invariants before
publishing a reference; the host comparison also asserts its fixed graph.
Native fixed-relative drift is at most 8.41e-14 mm and zero reported degrees.

All nine exact solids remain valid and nonempty. Native-to-imported own-frame
bounds differ by at most 1.00000122e-7 mm and volumes by 6.91216e-11 mm³.
Both corrected native limit variants use unchanged wrapper SHA-256
`151f5ee3eceebe72e75a4bc1a387999f5d389e03a56ae2890683ead7cd421832`.
The only measured mechanical difference between them is `Joint001.AngleMax`:
180 completes at 150 degrees; 120 blocks at 120 with 30 degrees remaining.
Native realization takes 3.261 / 3.456 seconds and exact build 2.145 / 2.227
seconds in the author's recorded run. The shared native correction is not
counted as part of this limit-only difference.

The actual STEP control is compared against the same valid native reference
at 0 / 150 / 120 degrees, with maximum error 8.59151e-6 mm / 2.41484e-6 degrees.
While the active native source has maximum 120, the frozen STEP declaration
still completes at 150; only its explicit manual maximum edit gives the same
120-degree block. This directly establishes the duplicated-mechanics burden,
not a claim about every STEP application protocol.

Two review corrections protect the meaning of this result. Native admission
checks recomputed connectors before solve and resolved connectors after it;
cached connector properties alone cannot refuse a valid authored source.
Saved occurrence drift remains a distinct refusal, including the case where
native recomputation adjusts an initially displaced Revolute. Separately,
the project's preparation test now uses its own ignored CAD/STEP/manifest
closure and proves the production source/layout/manifest hashes unchanged.
The evaluator checks the correction receipt against the actual consumed source
hashes. Dum-E issue DUME-010 records the former test-output coupling; earlier
failure reports remain preserved rather than relabelled as passing evidence.

## Final adapter regression and confirmed implementation

Primary independently ran `.venv/bin/python -m pytest -q` with the pinned native
runtime and external untouched Dum-E source explicitly enabled: **82 passed in
145.52 seconds**. This includes finite/tolerance boundaries, original-source
refusal, all valid Fixed branches, native stale-connector proof, the complete
source-freshness/publication regressions and ordinary public API behavior.
The frozen core baseline remains 578 passed / 2 skipped / 730 subtests. No
Apache core, viewer or Studio source change is part of this implementation.

Tests confirm the already-ratified package design: a separate LGPL adapter
uses a native worker to avoid interpreter/OCCT ABI coupling; native documents
own mechanics; imported aliases resolve to existing physical coordinates;
and existing machinome carriers, exact leaves, running stops and export format
consume the result. Native recomputation, solver status, connector residuals
and saved-pose stability jointly gate admission. Source receipts and acceptance
recipe invalidate stale generations. No FreeCAD fork, copied solver, new core
hook, alternate mechanical model or custom viewer format was necessary.
These are confirmations of the package's existing design record, not changes
to the framework's architecture or authority to alter its ADRs.

Primary reviewed the project's delivery command recorder and receipt: both
public exact-contract invocations, ordinary build, running export and all three
snapshot commands exit 0. `vet` still exits 1 for the documented unsupported
adapter universe; it is not bypassed. Build and export documents remain version
11 with nine pieces, four physical coordinates, four operating inputs and four
laws. The nonwatertight Wrist tessellation finding remains explicit despite its
valid exact solid.

Primary visually inspected the corrected rest, posed and final axis images.
The complete arm/base/phone holder are visible and connected; the posed image
shows articulation, and the axis view is uncropped at the recorded distance
1300. Their SHA-256 identities are respectively
`f4564e3dc3873c798404886cd1d13b7a58d704d7d70f306b90e49da3ae1bbec0`,
`40f8d56813970cbfc958c9e7e532646d2e31b20d754989271b42c20aecf3b804`, and
`fe902e9965a2c4c64bf713ed83d0bb70a17df396c09c98f917c40d61dab73d54`.
These ignored images supplement numerical kinematics; they establish neither
collision freedom nor hardware safety or CAD redistribution permission.

## Final acceptance

Primary independently reran all seven project tests: **7 passed in 34.72 s**.
It then reran the complete empirical CLI to the separate ignored receipt
`.tools/primary-empirical.json`, preserving the author's tracked report. All
eight pose cases, native constraint/target/fixed invariants, exact geometry,
180/120 limit-only results and three STEP comparisons passed again. Maximum
world-pose errors match the author's 5.153902587572203e-13 mm and
2.4148365394514667e-6 degrees. The tested corrected assembly SHA-256 is
`25c23df5aabe10108170e2655d17e3ecd2f0143a104e9af3c78da840ab8d3f9d`;
its copied parts retain the original parts hash. Both upstream CAD hashes and
the clean submodule were rechecked, and the frozen core checkout remains clean.

The primary accepts the implementation and originating-project proof. The
package's OpenSpec baseline and completed change can now be synchronized and
archived for the second local commit. No core ADR is changed: the already
ratified independent package design is confirmed above and in its design
record. Studio adoption, `vet` support, the Wrist tessellation finding and
upstream licence clarification remain explicit separate limitations, not
unfinished obligations disguised as green checks. Why native solve originally
reported success is still undetermined; no upstream solver repair is claimed.

Final code identity (SHA-256, before documentation-only closeout):

- `machinome_freecad/__init__.py`: `b26e505c861446445e4aaca83de975011c2fc795ab1925c8e2ae7128196279e8`
- `machinome_freecad/adapter.py`: `c89fe1efea498b82a76e790f56cb5e13bd08b1810316e39d0adc41fc951ffbba`
- `machinome_freecad/runtime.py`: `3a4b158d479e839ddfcddf1b0d635d7f16e1b2d7fd12ee92a64fd5cdb7cbdc0a`
- `machinome_freecad/worker.py`: `fc528ba67b2a195616f8e72c378532c255d8ff06caabca4fedd229068b467fc7`
