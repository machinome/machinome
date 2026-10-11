# Native FreeCAD adapter implementation evidence

Status: implementation and corrected-source Dum-E proof accepted by primary
review. Experimental and unreleased; not integrated into adapter main. This
chronological record retains earlier red and provisional gates. Final acceptance
and primary reruns are recorded in the adjacent adversarial review. 1 October 2026.

## Content and environment

The historical clean planning commit is `73d6b553c47140070301a9d9c8070137e5b2208d`,
one commit above adapter base `c2441d5c446d04901fc90c1d772443b07f68a07f`.
Implementation is confined to the independent LGPL-2.1-or-later adapter
worktree. No Apache framework source changes or monkeypatches are required.

The tested framework source is local prepared Machinome 0.7.1 at
`8a8a26711bcd7fd33c6daf7f8866d10004574f8c`. The adapter's isolated Python
3.12 venv installs that source with matching 0.7.1 metadata, leaving the
workspace's editable 0.7.0 metadata untouched. A venv-local `.pth` appends
the workspace dependency directory; it does not replace framework metadata.
The distribution smoke separately installs a physical framework wheel and
adapter wheel in an external throwaway environment.

Native runtime: official FreeCAD 1.1.4 AppImage, git
`4fd3bf320d9566a27e60069fc8387448aaa3a094`, AppImage SHA-256
`f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434`,
bundled Python 3.11, `GuiUp=0`, native Part OCCT 7.8.1. Host CadQuery 2.7.0
uses OCP 7.8. BREP compatibility was measured for this specific pair, not
claimed for other runtimes. Neither native binaries nor Dum-E CAD are bundled.

Set `MACHINOME_FREECAD_ROOT` to the extracted runtime's `squashfs-root`.
The validation runtime is at
`/home/asa/devel/machinome/projects/Robotic-Arms/Dum-E/.tools/freecad-1.1.4/squashfs-root`.

## Red-first and subsequent gates

The initial command `.venv/bin/python -m pytest -q tests/test_public.py`
failed collection with `ModuleNotFoundError: machinome_freecad` (exit 2),
before importer implementation. It contained the literal public declaration
and native maximum-only variant acceptance tests. The first implementation
slice then passed both tests: 2 passed in 6.78 s. The 180-degree source
completed a 150-degree command; the geometry-identical 120-degree variant
blocked the same command at 120 through the existing physical-stop compiler.

Synthetic fixtures are original licensed boxes authored by
`tests/generate_fixtures.py` through native FreeCAD APIs. Their metadata names
the author and LGPL-2.1-or-later license. The independent native reference
script uses actual native `generateSimulation` and sequential
`updateForFrame`, with angular formulas in radians. Four connector variants
(oblique, reversed endpoint order, antiparallel connector Z, and native
non-detached offsets) compare all three occurrence matrices at four
coordinates each, with absolute matrix tolerance 1e-9 and relative tolerance
zero. Own-frame BREP volume is 192 mm³ and placement is removed once.

The public suite passed 25 tests in 77.24 s before the final additional
product/boundary tests. An intermediate full suite passed 39 tests and failed
one synthetic distinct-product fixture: preceding invalid-fixture edits had
left its saved native angle near zero, slightly below its enabled zero lower
bound. Restoring the native authored 35-degree placement fixed the fixture;
the targeted distinct-product test passed. This was not addressed by
loosening adapter range admission.

Freshness tests first exposed actual stale exact-shape reuse when a changed
native recipe replaced BREP at the same source timestamp: expected 384 mm³,
observed 192 mm³. Native recipe now participates in ordinary source currency
but not structural identity; the adapter evicts the rebuilt exact BREP path
through the existing core cache helper. Nine freshness tests then passed in
29.71 s. Additional publication race coverage exposed an actual newly
published artifact after source change (12 passed, 1 failed). Adapter-owned
leaf materialization now preserves the four explicit BREP/STL and currency
sidecar paths and restores them upon `SourceChanged`.

The primary independently ran 40 passing tests with one failed prior-output
publication test: the test had not forced a rewrite of an up-to-date artifact.
That regression now constructs a new recipe at the same structural identity,
then checks the genuine rewrite boundary. Final targeted publication command:
`.venv/bin/python -m pytest -q tests/test_freshness.py -k publication`
passed all 4 cases in 13.30 s (replace/delete source, prior/no prior output).
Missing-source `OSError` is converted to chained `SourceChanged` so deletion
also follows rollback. Existing output and sidecars are restored byte-for-byte;
no-prior-output cases leave none of those explicit paths. Files may be
transiently replaced during the failing operation; this is not a cross-process
atomic transaction.

The sibling-linked document and source-preserving relocation command
`.venv/bin/python -m pytest -q tests/test_freshness.py -k relocation`
passed 1 test in 6.14 s. The native nested assembly links `../Parts.FCStd`;
two source-preserving project relocations retain the same structural leaf
identity. Repeated products share geometry identity while occurrences remain
separate, and equal product Names in different native documents are distinct.

Source regressions include a real 192-to-384 mm³ linked-file edit with restored
mtime and equalized file size, future-dated root, deleted and relinked linked
dependencies, source change during native resolution, source change between
snapshot return and adapter receipt adoption, changed-after-first-render
production, worker failure, and mutation isolation of cached JSON. Native
loading is bracketed by a discovery pass and authoritative closure pass;
the already-admitted receipt is adopted rather than recertifying old geometry
from later disk observations. Native filename spellings are retained, including
file-level symlinks. Fresh constructions have no unvalidated fast cache path.

`openspec validate native-freecad-assembly --strict` passed.
Wheel/sdist builds passed with isolated setuptools 76.1.0. The external smoke
`.venv/bin/python scripts/smoke_dist.py /home/asa/devel/machinome/machinome`
passed distribution inspection, installed physical Machinome 0.7.1 plus adapter
wheel outside the repository, blocked the literal command at 120 degrees,
and ran ordinary `machinome build` producing BREP/STL/SCAD artifacts. It
uploaded nothing.

The pre-diagnostic distribution was rebuilt after the deletion guard and sibling
fixture additions, then the external smoke was rerun successfully. Current
SHA-256 values at that gate: wheel
`016d05b70ee82309daa63bd54fcc71a7797b1d16a40ef2b9cae750b413a1a53b`,
sdist `daa0ffd3646d7c2c59c0951c8b0dd2d45765449bd06e432d5aab42f39146aaa4`.

Final command with the recorded native environment:
`.venv/bin/python -m pytest -q` — **44 passed in 104.32 s**.
This includes the four publication rollback cases, source-preserving
relocation, distinct native products and inclusive physical boundary.
Final `openspec validate native-freecad-assembly --strict` and
`git diff --check` also passed. Generated `_build` outputs and locks, FCStd
backups, validation venv and distributions are ignored and not staged.

## Diagnostic-only primary review correction

Primary's final spec/code cross-check requested native source/assembly and
candidate occurrence/joint Names in graph and solver refusals. The initial
diagnostic test run failed all six adapter graph-message assertions and the
real native disconnected-fixture assertion because source/inventory context
was missing. The isolated worker harness initially stopped at closure admission;
after correcting its expected root digest, its targeted test failed at the
actual solver branch: the message was only `native assembly solver status 7`.
Injected failures test messages only and establish no new native parity claim.

The correction adds diagnostic context to existing duplicate-Name, missing
ground, invalid-endpoint, count/loop/disconnected and worker solver/unsupported
graph refusals. It changes no graph or solver admission semantics or public API.
`MACHINOME_FREECAD_ROOT=<recorded root> .venv/bin/python -m pytest -q
tests/test_diagnostics.py tests/test_public.py -k 'diagnostics or native_refusals'`
passed **14 tests in 14.28 s**. The two literal valid-source running examples
passed **2 tests in 6.36 s**. Strict OpenSpec validation and diff checks pass.
The primary separately reran the preceding full suite (44 passed in 103.90 s)
and matching isolated core baseline (578 passed, 2 skipped, 730 subtests in
38.71 s). The new diagnostic cases are additional targeted coverage, not a
claim that a 52-test full suite has been rerun.

After this correction the wheel/sdist were rebuilt, inspected, installed outside
the repository against physical local Machinome 0.7.1 and smoked again through
the unchanged public 120-degree command plus ordinary build; all passed.
Refreshed SHA-256: wheel
`1b6a8b16f4b3ba3dd7f33cbea69345a86f2a99f6041a57a022d02002b7605a33`,
sdist `ea36fffea3849f151111ddcdf4d98e9990ba1a4d70878e2e5a7645cb5347884a`.

## Scope and remaining gates

The existing CoordinateRef seam is sufficient: aliases resolve to the original
physical BoundPort/OwnRef endpoint, and generated ordinary Revolute carriers
participate in the normal constructor, Sim, command and stop lifecycle. No
replacement proxy coordinate, extra alias bank slot, viewer engine or export
format was introduced. The primary recorded the relevant core baseline:
578 passed, 2 skipped, 730 subtests in 36.55 s (STEP, assemblies, mates, joints,
running, stops, exports and source generation).

Compatibility is intentionally pinned to prepared local Machinome 0.7.1 and
FreeCAD 1.1.4. Core 0.7.1 `vet` does not recognize the adapter members/source
attribute, so this package does not claim vet conformance or bypass vet.
Supported graph is one grounded rigid fixed/revolute tree; invalid subelements,
suppression, loops, disconnected graphs, competing grounding and other joint
types are refused. Native worker process isolation is not a security sandbox:
FCStd restores Python proxies and only trusted projects may be opened.

Generic core artifact-cache/phase-publication observations are future
maintenance evidence, not scope for this change. The adapter's narrow existing
currency/cache seams and exact-leaf rollback close its producing boundary.

Four physical Dum-E coordinates, nine-occurrence pose parity, native project
180/120 variants, geometry-only STEP comparison, independent public wrapper,
primary final review, studio contract disposition and cycle closure remain
tasks 4.5/7/8 gates. This record does not assert those are completed.

## Primary and originating-project checkpoint

The primary subsequently reran the complete current adapter suite: **52 passed
in 103.95 seconds**, including the diagnostic additions. It reran the matching
0.7.1 core selection: 578 passed, 2 skipped, 730 subtests in 38.71 seconds.
The independent Dum-E wrapper's two public tests also passed under primary
execution in 9.80 seconds. The project established native-limit-only
completed/150 versus blocked/120 with identical Python, equivalent exact
geometry, and automatic reopening of the copied native closure.

The headless and GUI native motion references, however, both change the
relative orientation across Fixed `Joint002` while reaching the turntable
target. This prevents nine-occurrence motion parity acceptance. Native solver
status alone did not establish a valid reference. No source repair, fallback
mechanical definition or relaxed tolerance is accepted. The originating
project preserves the failure and the passing independent gates separately.
Studio adoption is explicitly deferred; its contract remains unchanged.
Final architecture, baseline sync, archive and the implementation commit are
held pending a pilot decision, as detailed in the workflow and primary review.

## Ratified residual admission revision

The pilot approved fail-closed native constraint admission and a separately
authored project-owned native correction, leaving upstream CAD and runtime
untouched. The primary released amended planning commit
`dd2cba0f47f9317bf34dcfc418e7650ad9efecc5` after review and strict validation.
This replaces active planning identity, not historical evidence above.
The apply agent reread revised context through supported OpenSpec status/apply
instructions before the delta. No implementation commit, archive, baseline
sync, project edit or core edit is authorized here.

The isolated adapter interpreter physically imports
`/home/asa/devel/machinome/machinome/WTs/freecad-compat-8a8a/machinome/__init__.py`
and reports metadata 0.7.1. The frozen detached checkout is at recorded
`8a8a26711bcd7fd33c6daf7f8866d10004574f8c`, rather than moved primary.
The primary separately reran its exact eight-file core selection there:
**578 passed, 2 skipped, 730 subtests in 31.15 s**, two expected warnings.
This is primary evidence, not an apply-agent rerun.

### Actual preimplementation red

After generating original inconsistent Fixed/Revolute fixtures through native
APIs, this command ran before residual implementation:

```sh
MACHINOME_FREECAD_ROOT=<recorded runtime root> \
MACHINOME_FREECAD_DUME_SOURCE=/home/asa/devel/machinome/projects/Robotic-Arms/Dum-E/upstream/MA_Dum_E_v2_Assembly.FCStd \
  .venv/bin/python -m pytest -q tests/test_constraints.py
```

Result: **4 failed, 5 passed in 16.17 s**. FixedQuarterTurn, RevoluteTilted and
untouched Dum-E were wrongly admitted; RevoluteDisplaced was refused only by
generic saved/resolved pose drift without named joint/residual context.
Independent native quarter-turn fixture proof reports status 0, stable saved
occurrence placement and direction-cosine magnitude 1. This is real native
evidence, not a mocked solver-success response.

### Implemented admission boundary and targeted green

The worker checks actual native recomputed markers before solve and again
after solve. Origins are coincident to 0.01 mm; angular branch/axis distance
is at most 0.001 degree and raw native zero-target direction-cosines are bounded
by `sin(0.001°)`. Fixed accepts identity and all three proper π branches;
Revolute accepts parallel or antiparallel Z axes with free twist. Nonfinite
values and unknown conventions fail closed. Diagnostics name source, assembly,
joint, type, endpoints, measured residuals and applicable tolerances. The saved
versus resolved occurrence drift guard remains: recompute's adjustment of
RevoluteDisplaced is refused with involved native joint/residual context.
No pre-recompute cached-frame admission policy or implicit CAD repair is used.

Primary review caused an intermediate gate to fail **1 test, 28 passed in
20.96 s** after moving validation after recompute: the displaced fixture was
natively adjusted and reached the old generic drift diagnostic. Named
drift/resolved-residual context corrected that gap; no tolerance was loosened.

The targeted admission/diagnostics/native moving-parity command with external
original source enabled passed **31 tests, 30 deselected in 68.00 s**:

```sh
.venv/bin/python -m pytest -q tests/test_constraints.py tests/test_diagnostics.py \
  tests/test_public.py -k 'constraint or original_dume or opposite or solver_refusal or native_solver_pose_parity'
```

All three valid Fixed π branches and the antiparallel Revolute retain native
moving poses at four coordinates, comparing all three occurrence matrices
with absolute 1e-9 tolerance and relative tolerance zero. StaleConnectors also
compares moving poses after native recomputation resolves valid references and
offsets. The stricter public boundary was handed to the independent author for
repaired-Dum-E checks; no positive project proof is asserted by this agent.

Acceptance recipe `native-fixed-revolute-residual-v1` participates in worker
requests/responses, cache identity and snapshot/artifact currency. Missing/old
provisional response recipes are rejected, even with matching files and an
existing successful cache entry. There is no fallback to an old payload on
refusal. Pure-math finite/boundary cases and native refusal cases remain
distinct evidence; injected cache/recipe tests claim no native parity.
NOTICE records pinned OndselSolver conventions, licence, copyright and the
original Python validator adaptation; no native solver function/binary is
copied or patched.

### Full revision gate and native cache-order proof

With both `MACHINOME_FREECAD_ROOT` and external `MACHINOME_FREECAD_DUME_SOURCE`
set as above, `.venv/bin/python -m pytest -q` passed **81 tests in 145.57 s**.
This includes original-source refusal (not skipped), all native branch moving
comparisons, missing/old provisional recipe refusals, seeded old-key failure
without fallback, and acceptance-recipe-only artifact invalidation/rewrite at
unchanged structural identity and unchanged CAD.

After the full run, primary requested a native assertion that StaleConnectors
actually retains a bad cached Placement on initial opening. The added
independent native test passed **1 test, 24 deselected in 1.65 s**:

```sh
MACHINOME_FREECAD_ROOT=<recorded runtime root> \
  .venv/bin/python -m pytest -q tests/test_constraints.py -k stale_cache
```

The raw cached Placement1 differs from `Joint.Proxy.findPlacement` by more than
10 mm and 80 degrees; reference-derived connector residuals are valid. Native
recompute restores cached Placement1 and retains all three saved occurrence
placements within 1e-9 mm/degree. Thus the source's successful admission really
pins authoritative recomputation rather than a saveAs-normalized fixture.
Current suite has 82 tests; the primary will independently rerun that complete
current suite. No adapter test process remains from this handoff.

The first revised wheel/sdist build and external ordinary build smoke passed
against frozen core. The smoke asserted and printed physical core location
`/tmp/machinome-freecad-wheel-smoke-58n2574a/env/lib/python3.12/site-packages/machinome/__init__.py`,
alongside actual adapter wheel location under that same environment, rather
than relying only on metadata. The package manifest subsequently added
repository-owned workflow Markdown so its README/API links also exist in the
sdist; linked workflow/review/evidence archive assertions are now required.
Any primary closeout relocation of those records requires a fresh final build
and smoke with updated paths. None of these operations uploads artifacts.

### Independent originating-project report

The primary reports the independent author's repaired-source empirical result:
eight cases compare all nine occurrence poses with maximum errors
5.1539e-13 mm / 2.41484e-6 degree; native target/residual/fixed invariants pass.
Corrected 180-degree baseline completes 150 and corrected 120 variant blocks
at 120 with unchanged wrapper SHA-256
`151f5ee3eceebe72e75a4bc1a387999f5d389e03a56ae2890683ead7cd421832`;
only native `Joint001.AngleMax` differs between those variants. Geometry-only
STEP control reports 8.59151e-6 mm / 2.41484e-6 degree, while stale manually
declared 180 remains at 150 under the native 120 variant. Those are independent
project/primary results, not apply-agent project work. Detailed authority is
project-owned `simulation/evidence/empirical.json` and the primary review.
Exact/build/snapshot results, primary final review, final documentation/status,
spec sync/archive and completion commit remain parent-owned closeout gates.

The primary independently reran the complete final suite with external original
source refusal enabled: **82 passed in 145.52 s**. It reviewed authoritative
recompute/solve residual flow and reports no remaining code findings. Per its
handoff instruction, tasks 1–6 are restored as achieved against historical and
revision evidence, including the separately reported repaired-source portion
of 4.5. Project/primary tasks 7 and closeout tasks 8 remain untouched for parent
reconciliation and completion authority.

The final pre-closeout distribution smoke also passed after workflow Markdown
was included: wheel/sdist member inspection and referenced-record assertions,
physical core/adapter installation outside the repository, blocked/120 public
command and ordinary build. It printed core path
`/tmp/machinome-freecad-wheel-smoke-2w5tmyji/env/lib/python3.12/site-packages/machinome/__init__.py`.
The tested pre-closeout wheel SHA-256 is
`519c89806c34b380b55ad0c6038dba892b274eaf60be22c7ebdfb20b918399a8`;
sdist SHA-256 is
`78bff08810065a6be132901d52da2fc47eeba7c236d00e009b81976a14df43e6`.
This final evidence append and any subsequent primary record/archive changes
require final sdist rebuilding; the hashes describe the smoke-tested gate,
not a claim that a later amended record was already packaged.
Strict OpenSpec validation, diff whitespace checks and Python compilation pass.
All implementation remains unstaged; no commits, archives, publication, core
or project edits were made by the apply agent. Apply editing now stops for
primary final status/spec-sync/archive/commit and project visual gates.

## Primary closeout disposition

The primary completed all project/visual gates and independently reran seven
project tests (34.72 s), the full eight-pose/limit-only/STEP empirical CLI and
the 82-test adapter suite (145.52 s). The original source remains rejected;
the explicitly corrected native copy is accepted with geometry and saved-pose
preservation. The adjacent review records exact identities, limitations and
the confirmed implementation decisions. The completed workflow records now
live in `workflow/archive/native-freecad-assembly/`; the smoke helper checks
these archived records in the source distribution. The post-relocation rebuild
and external physical-install smoke passed: archived-record member assertions,
physical core/adapter installation, public blocked/120 simulation and ordinary
build. The smoke printed core location
`/tmp/machinome-freecad-wheel-smoke-knnkx02u/env/lib/python3.12/site-packages/machinome/__init__.py`.
The final evidence text is rebuilt and smoke-checked again before committing;
no distribution is uploaded.

All ten added requirements were synchronized verbatim into the new baseline
after its package-owned Purpose. Strict validation passed for change and spec;
the supported archive operation then created
`openspec/changes/archive/2026-10-01-native-freecad-assembly/`. Its
`specsUpdated: false` receipt means baseline synchronization was already verified
before using `--skip-specs`, not that synchronization was omitted. Final baseline
strict validation passed. The two-commit cycle is based on bootstrap
`c2441d5c446d04901fc90c1d772443b07f68a07f`, with amended planning
`dd2cba0f47f9317bf34dcfc418e7650ad9efecc5` and the implementation commit
containing this completed record. It is not integrated into main.
