# Evidence — carry markings on a part

Worktree `solid-node/WTs/markings`, branch `markings`, base `main` at
`710d86f` (fast-forwarded from `1aac0ff` on the pilot's order before
implementation; nothing this cycle touches changed between the two, and
the ADR plan moved from 119 to 120 because 119 was taken by the
renumbered named-project-models record). Planning commit `23b45e7`.
Proposal written by an Opus agent and revised by a second after review;
implementation by an Opus agent; two closure findings by a Sonnet agent;
adversarial review of proposal, revision, implementation and closure by
the repository agent, standing in for pilot ratification under the
delegation of 2026-09-07. Test command throughout:

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests -q

## Design evidence, before proposing (workspace venv, real Curta artwork)

- `build123d.import_svg(path, align=None)` on
  `projects/Calculators/Curta-Type-I-3x/Drawings/results_dial.svg`: 10
  faces (the digits, counters as holes: 0 → 1, 8 → 2) and 4 open wires
  (the sheet border). Face extent 56.438 × 6.000 mm; full extent
  59.376 × 10.500 mm. 2π × 9.45 = 59.376 mm: the border IS the unwrapped
  circumference, which is why open paths are counted rather than dropped
  silently and why `origin=` exists.
- `upper_housing_numbers.svg`: 14 faces, full width 224.860 mm — the
  224.8 mm the wart records upstream sizing that artwork by.
- DXF, deferred with this: cadquery `importDXF` on
  `Manual/Painting/results dial.dxf` fails to close its chains at 1e-4 and
  1e-3 mm tolerance ("inner wire is not closed"); at 1e-2 mm it yields ONE
  face of 512.9 mm² — the border with the digits as holes, the stencil,
  not the glyphs.
- Full pipeline spike on `results_dial.svg` at R = 9.45: OCCT tessellation
  4 508 vertices / 4 499 triangles; `trimesh.remesh.subdivide_to_size` at
  max edge 2.742 mm (t = 0.1) cost 12 triangles; every wrapped vertex at
  radius 9.45 ± 3e-15; 69.48 mm² of artwork; 226 kB binary STL;
  `is_watertight` False as intended.

## Red, per task group (implementer's run, this worktree)

- **2 Declaration.** 2.1 `ModuleNotFoundError: No module named
  'solid_node.node.markings'`. 2.3 red twice by stubbing
  `declared_markings`: walking `[node_class]` instead of
  `reversed(__mro__)` failed inheritance and the plain-mixin case;
  dropping the `None` branch failed the drop case. 2.4–2.7: 15
  "TypeError/ValueError not raised" before `_validate_markings`; the four
  clash tests re-proven red by disabling the collision branch. 2.9 red as
  `'Svg' not found in __all__` and the fresh-interpreter probe.
- **3 Artwork and placement.** 3.1 red by resolving against the node's
  module and dropping `require_source_file` (four of five failed; the
  subclass-in-another-module case only became a real test once
  `Svg.resolve` stopped caching). 3.2/3.3 `'Svg' object has no attribute
  'regions'`. 3.4–3.7: 23 failures before the placement maths.
- **4 Artifact and currency.** 4.1–4.3 "no attribute `marking_file`" /
  missing artifacts. 4.2 measured: with the subdivision removed the exact
  dial's surface departs the cylinder by **0.834 mm** (allowed 0.05) and
  the faceted plate's by **0.661 mm** (allowed 0.1); meshing the dial at
  the framework default instead of its declared 0.05 gives **0.0529 mm**
  > 0.05. The departure is measured at edge midpoints (the chord
  sagitta), since every vertex lies on the cylinder exactly (that is 4.3).
  4.5 red by returning no recipe for a marking path. 4.6 red twice:
  moving the marking pass inside the `_prepare_can_be_skipped()` block
  ("a deleted decal comes back" fails) and removing the currency guard
  (the `mesh_bytes` spy fires "must not re-mesh"). 4.7 red by dropping
  the artwork from the marking's tracked set. 4.8 red by making the
  declaration edit a no-op. `LeafNode`'s skip predicates are untouched and
  a test asserts both still report `True` with a decal missing.
- **5 Document.** 5.1 red by stubbing `uniq_id += '-marked'`. 5.2 is a
  pin; the verdict harness was shown not vacuous by driving the dial into
  the plate. 5.3/5.4 red as "unexpected keyword argument 'marking_path'".
  A real defect surfaced here: the serializer's recursion did not forward
  `marking_path`, so nothing below the root published — caught by
  5.7/5.8. 5.6 red by publishing the key unconditionally; 5.8 red by not
  collecting marking references in the sweep. `tests/base_documents/` is
  untouched and `ByteIdentityTest` passes over its existing captures.

## Green

- Implementer's full suite, uncontended: `2866 passed, 4 skipped, 53
  warnings, 1580 subtests passed in 309.11s`.
- Reviewer's independent full suite on the same content: `2866 passed,
  4 skipped, 53 warnings, 1580 subtests passed in 311.06s`, exit 0.
- `openspec validate carry-markings-on-a-part --type change --strict`:
  valid.

## Real caller — `projects/Calculators/Pascaline-module`

With `PYTHONPATH` = this worktree (plus the viewer worktree its README
names): `solid build` exit 0; `pytest tests/test_document.py` 6 passed,
18 subtests; `pytest tests/test_sources.py` 4 passed;
`solid test --faceted simulation/flexibles.py:RatchetBench` 5 passed;
`solid test --faceted simulation/pascaline.py:Pascaline` 37 passed, 0
failed. The project declares no marking yet; this proves no regression.
Its git status stayed empty.

## Underspecified in the ratified design, and how it was resolved

1. `assertNoIntersectingSolids` does not exist; the API is
   `assertNoSolidInterference` (plus the deprecated
   `assertNoPairwiseIntersections`). 5.2 exercises both, faceted and exact.
2. `Builder._artifacts_are_current` was not named in the design but had to
   learn markings: without it a lost decal never came back through
   `solid build` and the republished document named a missing file. It
   checks each marking over its own tracked set, guarded on `node.rigid`.
3. Node doubles (`SimpleNamespace`, `FakeNode`, `Mock`) stand in for rigid
   nodes in the parity and lifecycle fixtures; `marking_entries` and the
   builder ask through `getattr`, the shape `exact` already uses.
4. `require_source_file` is called with the DECLARING class (the mixin
   where there is one) because its message names that class's module.
5. `Svg.resolve` does not cache, so an inherited marking re-resolves
   against the declaring module on every class creation.
6. `declared_markings()` is memoized per instance under a private key the
   child-naming scan skips; `_artifact_recipe` short-circuits on the path
   prefix before enumerating.

## Review findings on the implementation, and their closure

1. **A same-body clash was pinned as "still the second".** The spec
   scenario refuses a marking taking a parameter's name; the
   implementation refused only the inherited case and pinned that
   `digits = Length(4.0)` followed by `digits = Marking(...)` in one body
   silently keeps the second. `_DeclaringNamespace.__setitem__` sees both
   values, so the same-body case is refused there. (Closure below.)
2. **The MRO scan asked instances for `marking_kind`.** `getattr(value,
   'marking_kind', None)` on every class-body value enters
   `ChildDeclaration.__getattr__`, which resolves any non-underscore name
   through `read_through` on every node class created. The marker is now
   looked up on `type(value)`. (Closure below.)

Everything else in the diff was verified against design D1–D8 line by
line: the marking pass sits outside `_prepare`'s skip block and after the
`_prepared` early return; the leaf predicates are untouched; the artwork
is not in `node.files`; `_up_to_date` and `_content_verified` take the
tracked set as a parameter so one predicate answers for the solid and the
decal; the recipe is `marking-svg-v1:<tolerance>`; `marking_path` is
threaded through the three producers and the serializer's recursion; the
sweep spares by reference; export copies with an atomic copy under the
model containment guard; the snapshot stages decals beside models.

- Reviewer's final full suite on the archived content, before commit 2:
  `2869 passed, 4 skipped, 53 warnings, 1580 subtests passed in 321.13s`,
  exit 0; `openspec validate --all`: 33 passed, 0 failed.
