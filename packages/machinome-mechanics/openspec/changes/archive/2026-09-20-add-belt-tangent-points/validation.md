# Belt tangent points validation

## Package

Planning commit `38fa3bf6d084738ca7c75534a36d0fd1a6dc88e0`.
Tested uncommitted `machinome_mechanics/belts.py` SHA-256:
`28e693a5b2b213526c6f235615306fbad0a47f0ad0fca579d2aa1142f5db8cab`.
Commands use workspace Python, cwd this worktree and `PYTHONPATH="$PWD"`.

- Red: `python -m pytest -q tests/test_belt_tangents.py` failed collection
  because belt_tangent_points did not exist, before implementation.
- A test utility import then needed correction for pytest's importlib mode.
  The final test file was rechecked against merged pre-helper main: from /tmp,
  `PYTHONPATH=/home/asa/devel/machinome-studio/machinome-mechanics` with the
  absolute new test path, again fails specifically on missing helper import.
- Green: `python -m pytest -q`: 78 passed, 24 subtests.
- Twenty-one new tests cover known outer/inner contacts, twelve transformed
  four-sense cases, independent angular references, radius closure,
  perpendicularity, traversal sense, reverse traversal, impossible nested/
  crossed tangents, coincident centers, zero-span limit, point contacts and
  actual deferred Solid2 coordinate/radius expressions at five samples.
- `python -m sphinx -q -b doctest -W --keep-going docs docs/_build/doctest`:
  102 examples, no failures.
- `python -m sphinx -q -b html -n -W --keep-going docs docs/_build/html`: pass.
- `python scripts/check-dist`: both distributions built, metadata checked,
  installed exports and numeric/symbolic smoke checks passed. No upload.
- `git diff --check` and `openspec validate --all --strict`: pass.

Dependency heads observed after package validation: framework clean
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`, viewer clean
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`. Consumers record their own
validation observations; these are not a frozen environment claim.

## Consumers

Thor, Prusa3-vanilla, Kossel, Hangprinter and Metamaquina2 have natural
directed tangent geometry. Actuator's closed scalar length law and Windmill
2's proxy belt shape are not rewritten into tangent calculations just to add
consumers. All five Sol migrations have now passed final review.

### Thor

- Original main `d57ae064b94a2f9bc580a7d66eb27af0e96b80f7`.
- Migration `81ab279310e45b8cbc610ab52b8e29968e0e0ec8`.
- Project tangent wrapper retains truthy/false turn marker mapping and its
  exact numeric reach guard/error. Only contact arithmetic delegates to helper.
- Parent reran docs/verify_belt_tangent_points.py after reviewing the diff.
  Actual elbow/wrist contact errors are below 2e-15 mm; four-circle back-idler
  case below 4e-15 mm. Loop lengths unchanged at 462.9770193306483,
  223.52395515247483 and 519.7691931675917 mm; wraps within 3e-14 degrees.
  The extra back-idler route is algebraic coverage, not a changed physical belt.
- All four arbitrary sense pairs agree below 9e-16 mm. Invalid wrapper message
  unchanged. Wrapper stays numeric-only; supported deferred inputs are tested
  at package boundary, not claimed for its old math.hypot guard.
- Compilation/root build passed; exact Thor 31/33, all belt checks pass and
  only established overlap failures remain (260/272, same first pair/volume).
- Sol inspected home/driven OpenSCAD images; parent inspected home. Enclosed
  contacts are not visible: images establish exterior pose coherence only.
- Full commands: docs/mechanics-belt-tangent-points.md. Framework/viewer stayed
  clean at 0ce71cd/4355da1. No helper regression.

### Hangprinter

- Original version_4 `2cc703793e9029e19313b22a00472be030173e69`.
- Migration `12f74a6f00f0275cd2f289c703b0d122cc1875a9`.
- Private _tangents adapter shares contact pairs between spans and normals,
  retains string turn markers and zero-radius normal recovery. Unused _touch
  removed; fitting, phases, controls and station ordering unchanged.
- Actual winch old/new normal error below 9e-16, span components and arcs below
  5.7e-14 mm. Back-idler arcs unchanged; both-zero radii retain zero arc lengths.
  The limiting zero-span route retains zero total length and all-zero stations.
  No modulo full-revolution discrepancy found in these comparisons.
- Actual Solid2 deferred helper expressions evaluated at five samples. Project
  wrappers remain numeric. Initial private test-evaluator import failed; the
  durable probe uses the framework parser and a self-contained evaluator.
- Faceted/exact winch 5/5 each, root 19/19 each, build succeeds. Sol inspected
  focused winch and rest/z=300 snapshots; parent inspected focused winch.
  Visible routing is coherent; no force, tension or elasticity certification.
- Full runnable probes/commands: docs/belt-tangent-points.md. Framework/viewer
  stayed clean 0ce71cd/4355da1. Parent reviewed final diff and complete record.

### Metamaquina2

- Original main `a652e8369551c540cd5dd71d82c34af28cf4080a`.
- Migration `42013334c43b036bacbf68b881f01704bae20ba6`.
- Spans consume helper contacts; normal recovery retains nonzero/point-contact
  behavior and string turn markers. Fitted radii/periods, phases and topology
  remain unchanged.
- Runnable docs/probes/belt_tangent_points.py compares independent old normal,
  contacts, arcs and station arithmetic on real X/Y, mixed back-idler,
  collinear-equal and zero-radius routes at absolute 1e-12. All pass.
  X/Y loop lengths remain 803.8854513557229 and 1036.4343190090678 mm;
  all four/eight stations agree, with no tooth count or fitting change.
- Supported deferred Solid2 expressions remain deferred; independent sampled
  evaluation is covered by the package tests, not substituted with SymPy.
- Exact root 67/67 in 462.66s. Existing jhead.scad parser diagnostic persists
  without failing the suite. Parent and Sol inspected current driven web image:
  coherent exterior, insufficient scale for contact certification.
- Full commands/source identity: docs/belt-tangent-points-verification.md.
  Framework/viewer stayed at 0ce71cd/4355da1, viewer clean after capture.
  Parent reviewed final source/probe/evidence; no helper regression.

### Prusa3-vanilla and Kossel

- Prusa original master `b8212ccfc613ac1cae4c11d344862b07aa6ab894`;
  migration `46c9e5741dde0ef07eefb89a4975749f95d52872`.
- Kossel original master `44d9349a64386c1099cbf5cd660770b7d86a3435`;
  migration `159ad7eb228d83819f4e91c82cd58f33a5a1f0f7`.
- Spans use contacts directly; normals recover from first/second nonzero
  signed radius or the perpendicular center line for point contacts. Marker
  meanings, topology, fitted radii, arcs/stations and Kossel anchor bug unchanged.
- Parent reviewed and reran scripts/check-belt-tangent-points in both repos.
  Six/five routes respectively match old full metrics at absolute 1e-12:
  actual X/Y or tower loop, reverse-bend idler, zero-first, both-zero and
  limiting zero-span. Closed loops also exercise reversed pair ordering.
  No wrap/station discontinuity found. Scripts print 'match exactly', but
  their actual gate is the explicit 1e-12 tolerance, not bit equality.
- Prusa X/Y faceted and exact suites all 6/6; root build exit 0.
  Kossel Tower faceted 9/9, root faceted 15/15; build exit 0. Unrelated known
  Effector exact failure is outside this gate and was not rerun.
- Initial OpenSCAD preview captures failed without diagnostic after SCAD
  generation. Default-renderer retries succeeded with fresh images. Parent
  and Sol inspected Prusa center and Kossel driven poses: coherent visible
  routes and assembly. These 640x480 overviews do not certify tooth contacts.
- Full commands/provenance: docs/mechanics-belt-tangent-points.md in each repo.
  Framework/viewer stable 0ce71cd/4355da1. No helper regression.

## Completion

Independent Sol review of the helper found no substantive contract or
implementation issue and reran 21 focused tests successfully. All five final
source diffs, runnable probes, evidence records and representative images have
been reviewed. A later full package repeat passed 78 tests and 24 subtests.
The baseline contains the complete added requirement, with strict spec and
diff checks before archival. Local integration follows the completed-cycle
commit and is recorded in the next cycle's campaign ledger.
