Red first, everywhere. Each group names the failing test before the change
that turns it green, and "prove red" means the test was seen to fail for the
reason it is about — not merely to error on a missing import.

## 1. The fixture project

- [x] 1.1 Create `tests/markings_project/` as a package (`__init__.py`,
  `pyproject.toml` alongside the other fixture projects), holding a small
  **committed** SVG `label.svg`: at least two closed regions, one of them with
  a hole (so the nested-hole rule is exercised), authored so its extents are
  known to three decimals and written into the test as expected values, plus
  one deliberate open path so the ignored-wire rule has something to ignore.
- [x] 1.2 Add the fixture parts across three modules, in BOTH leaf kinds the
  invariants need — an exact leaf (it has a `.brep` to compare and it declares
  a tessellation precision) and a faceted one (it has neither):
  - `Dial`, a `CadQueryNode` — a plain cylinder is enough, and an exact
    dial is the originating shape, the Curta's own. It declares a
    NON-DEFAULT `linear_deflection` (0.05, against `ExactLeafNode`'s 0.1) so
    4.2 can tell "the part's declared deflection" from the framework default,
    and one `Wrapped` marking.
  - `Dial` of the SAME name and the same parameters in a second module,
    declaring NO marking, for the byte-identity and `uniq_id` comparisons of
    5.1 and 5.2.
  - `Plate`, an `StlNode` over a committed STL — copy the smallest mesh from
    `tests/stl_project` — declaring one `Flat` marking and a second `Wrapped`
    one, for the two-markings-on-one-part cases and for the faceted half of
    every invariant: an `StlNode` writes no `.brep` and declares no
    `linear_deflection`, so its decals are meshed at the framework default.
  - `Plate` of the same name declaring no marking, so 5.1's faceted half has
    its comparison too.
  Write ONE of the markings in a plain (non-node) mixin class in a third
  module, mixed into its node exactly as the Curta's
  `class FittedDialType1(ClearingGearFit, ResultsDialType1)` is, so 2.3 and
  3.1 have the real shape to test.
- [x] 1.3 Add `assembly.py` placing both parts under an `AssemblyNode` with a
  `Revolute` joint on the dial, so the ride-the-placement scenario and the
  document tests have one tree to read.
- [x] 1.4 Add `tests/test_markings.py` with the fixture plumbing the other
  fixture-backed suites use (`tests/conftest.py`, the build-dir fixtures) and
  no tests yet; confirm it collects.

## 2. The declaration, refused where it is written

- [x] 2.1 **Red**: a rigid leaf declaring `digits = Marking(Svg(...),
  Wrapped(...), color='#FFFFFF')` can be created, is named `digits`, and the
  class reports one declared marking in declaration order. Fails: no `Marking`.
- [x] 2.2 Write `solid_node/node/markings.py` with `Marking`, `Svg`, `Wrapped`
  and `Flat` as inert value objects carrying `marking_kind`, `__set_name__`
  naming the marking and capturing the declaring module's file, and
  `declared_markings(node_class)` walking `reversed(cls.__mro__)` in the shape
  of `declared_children` (`declarative.py:878-890`), with `None` **removing**
  an inherited entry. Standard library only at module import (design D7).
- [x] 2.3 **Red**: inheritance and dropping — a subclass inherits the base's
  marking; a subclass assigning `digits = None` declares none while the base
  still does; two markings keep declaration order; and a marking declared in
  the body of a PLAIN MIXIN in one module is collected on the node class in
  another that inherits it (Python calls `__set_name__` on the mixin whatever
  its metaclass, and the MRO walk is over `cls.__mro__`, not over node
  classes). Green in 2.2 if the MRO walk is right; prove each red first by
  stubbing the walk.
- [x] 2.4 **Red**: `AssemblyNode` and `FlexibleNode` subclasses declaring a
  marking each raise at CLASS CREATION, naming the class and the attribute.
  Also: the same declaration on a rigid leaf and on a `FusionNode` is accepted.
- [x] 2.5 **Red**: a marking whose attribute name is also a declared parameter,
  a declared child, a port, or a joint coordinate of the same class raises at
  class creation naming the class, the attribute and the collision. Note in the
  test why `_DeclaringNamespace.__setitem__` does not already catch it
  (`declarative.py:686-701`, `_refuse_coordinate_clash` returns unless both are
  coordinates).
- [x] 2.6 **Red**: a marking named for an attribute every node already carries
  — `color` first, because `color = Marking(...)` would make `self.color` a
  `Marking` and break `_colorize` (`base.py:1002-1010`), then `files`, `model`
  and `stl_file` — raises at class creation naming the class, the attribute and
  the node attribute it would shadow. A parameter is already refused this two
  ways (`parameters.py:138-143` `_RESERVED`, and the MRO walk in
  `Declaration.__set_name__` right after it, which is what catches `color`);
  a marking is read as an attribute of its node in the same way, so refuse it
  the same way.
- [x] 2.7 **Red**: a `Marking` with a bad `color` raises `ValueError` at class
  creation; one with a non-artwork first argument or a non-placement second
  argument raises naming the class and the attribute.
- [x] 2.8 Extend `NodeMeta.__new__` (`declarative.py:798-826`) with
  `_validate_markings(cls, name, namespace)`, duck-typed on `marking_kind`
  exactly as `_validate_controls` is on `control_kind`, importing nothing new
  into `declarative.py`. It enumerates the class's own declared parameters,
  children, ports and joint coordinates AND walks `cls.__mro__[1:]` for a
  non-marking attribute of the same name, in the shape
  `Declaration.__set_name__` already uses. Validation runs on the NODE class,
  so a marking inherited from a plain mixin is refused here and not in the
  mixin, which knows nothing about rigidity. Turns 2.4, 2.5, 2.6 and 2.7
  green.
- [x] 2.9 **Red**: `from solid_node.node.markings import Marking, Wrapped,
  Flat, Svg` works, and `from solid_node.node import Marking, Wrapped, Flat,
  Svg` resolves the same objects. Add the four names to `_EXPORTS` in
  `solid_node/node/__init__.py` and to `EXPECTED_EXPORTS` in
  `tests/test_node_lazy_exports.py`, and confirm the fresh-interpreter probe
  still shows nothing imported until named.

## 3. Artwork and placement, as pure functions

- [x] 3.1 **Red**: an `Svg` whose path does not exist is refused at class
  creation with `solid_node.node.sources.MissingSourceFile` (a
  `FileNotFoundError` subclass, `sources.py:41-61`), and one resolving to a
  directory with `ValueError` — pin BOTH types, not just "it raises", so
  whatever handles that family keeps handling this one. Assert the message
  names the class, the attribute, the declared value and the absolute path, and
  that `.filename` is the resolved path, which is the only thing develop-mode
  reload actually reads (`builder.py:505-533` watches `exc.filename`; nothing
  in `builder.py` names `MissingSourceFile`, so there is no recovery of ours to
  test). Implement through `require_source_file` (`sources.py:63-102`). Resolve
  the path against the DECLARING module and prove it twice: with a subclass in
  another module inheriting the marking, and with the plain mixin from 1.2,
  whose module is the one the path must resolve against.
- [x] 3.2 **Red**: the fixture SVG reduces to its closed regions with holes
  nested, its open path contributes nothing, and an SVG of open paths only is
  refused naming the file. The ignored count is **logged**: assert with
  `assertLogs` that building the marking emits one INFO record naming the
  artwork file and the number of open paths ignored (INFO is the level the
  build already uses for an artifact notice, `base.py:87`; `sheet_leaf.py` and
  `adapters/stl.py` log nothing of their own). Implement with
  `build123d.import_svg(path, align=None)` keeping `Face`s, imported INSIDE
  the function (design D7). Assert the measured extents from 1.1.
- [x] 3.3 **Red**: `Svg('...', scale=25.4)` multiplies every artwork
  coordinate.
- [x] 3.4 **Red**: `Flat` — points land on the declared plane, artwork X runs
  along the orthogonalized `x_axis`, artwork Y along `normal × x_axis`,
  `origin` shifts the artwork, and an `x_axis` parallel to `normal` is refused
  naming both. Test the placement as a pure vertex map, before any artifact
  exists.
- [x] 3.5 **Red**: `Wrapped` — every point at the declared radius about the
  declared axis; artwork Y is height along the axis from `at`; arc length is
  preserved (an artwork 2πR wide closes on itself exactly once); a
  non-positive `radius` is refused.
- [x] 3.6 **Red**: the angular zero. With `start=0` and the artwork origin at
  artwork x = 0, that point sits on `+X` for `axis=(0,0,1)`, `+Y` for
  `(1,0,0)`, `+Z` for `(0,1,0)` and `−X` for `(0,0,-1)`; positive angle turns
  right-handed about the axis. `zero=(0,1,0)` overrides it; a `zero` parallel
  to `axis` is refused; `axis=(1,1,1)` with no `zero` is refused naming `zero`
  as the remedy. Implement design D4's σ rule.
- [x] 3.7 **Red**: `pitch=36` stamps the artwork ten times at 36° intervals;
  `pitch=50` is refused naming the value and the nearest whole count; a
  non-positive pitch is refused.

## 4. The artifact and its own currency

- [x] 4.1 **Red**: building the fixture writes one marking artifact per
  declared marking, beside the part's `.stl`, under the same basename and
  distinguished by the marking's name; a part declaring none writes none and
  its build directory holds exactly what it held before.
- [x] 4.2 **Red**: the wrapped decal follows its cylinder — no vertex departs
  from the nominal radius by more than the part's own tessellation precision,
  asserted on BOTH fixture kinds so the rule is read from the part and not
  hard-coded: the exact `Dial` at its declared `linear_deflection = 0.05`, and
  the faceted `Plate`, which declares none, at the framework's 0.1 mm. Verified
  on an artwork whose regions span several millimetres of arc, and verified to
  FAIL when the subdivision step is removed, and to fail for the `Dial` if the
  framework default is used in place of its declared value (that is the red
  this task is about). Implement with `trimesh.remesh.subdivide_to_size` at
  `max_edge = 2√(2Rt − t²)` (design D5).
- [x] 4.3 **Red**: the decal sits on the nominal surface with NO offset —
  every vertex at exactly the declared radius / on exactly the declared plane,
  to floating-point tolerance.
- [x] 4.4 Add the artifact path and the build to `AbstractBaseNode`
  (`base.py`): `<basepath>.marking-<name>.stl`, written through
  `_atomic_write_bytes` (`base.py:130-151`) with its own digest, fingerprint
  and stamp, from `_prepare` (`base.py:884-905`) so a `FusionNode` and a leaf
  both reach it (`_prepare` is defined once in the node tree; `assemble` calls
  it unconditionally, `base.py:848-856`). Put the marking pass OUTSIDE
  `_prepare`'s `if not self._prepare_can_be_skipped():` block, so it runs
  whether or not the solid is current, each marking guarded by its own
  `_up_to_date`-shaped predicate over its own artifact and its own tracked set,
  and after the `if self._prepared:` early return so it runs once per node per
  process.
- [x] 4.5 **Red**: the marking artifact records a producer recipe — a build
  whose recorded recipe differs from the one the code would produce now
  re-derives the decal even though every source is unchanged, and an unchanged
  recipe reuses it. Return `marking-svg-v1:<effective tolerance>` from
  `_artifact_recipe` (`base.py:1413-1415`) for a marking path, deferring to
  `super()` for every other path, and pass it through `_atomic_write_bytes`'s
  `recipe` argument as `FusionNode` already does (`fusion.py:44-47`,
  `fusion.py:148`). The tolerance belongs in the recipe because a part that
  declares none is meshed at a framework default that is in no project file
  (design D5); assert the STL, the BREP and the `.scad` still record no
  recipe.
- [x] 4.6 **Red**: the two halves that distinguish this design from the sheet
  leaf's, and the red is the SPY, not the artifact:
  - a current marking is not rewritten — patch the marking writer and assert it
    is not called, as `tests/test_sheet_leaf.py:389-398` does for the DXF;
  - a deleted or stale marking artifact alone regenerates that marking on the
    next build while the node's `render()` is NOT called — spy on `render()`
    (and on `materialize`) and assert zero calls, on the `StepNode`-shaped
    case as well if one is cheap, since there `render()` is the STEP load plus
    `adjust()`;
  - the same spy DOES see `render()` called when the STL itself is stale, which
    is what proves the test is about the skip decision and not about nothing.
  `LeafNode._render_can_be_skipped` and `_prepare_can_be_skipped`
  (`leaf.py:41-65`) are left UNTOUCHED: widening them, as `SheetLeafNode` does
  for its DXF (`sheet_leaf.py:157-170`), would make a lost decal re-derive the
  solid, because `_prepare` calls `render()` whenever the predicate is False
  (`base.py:884-905`). The sheet leaf widens its own because its DXF comes
  from the rendered profile; a marking never does (design D5).
- [x] 4.7 **Red**: editing the ARTWORK file regenerates only the marking —
  the part's `.stl` and `.brep` report current and their bytes and mtimes are
  unchanged. Implement the marking's own tracked set (`node.files` ∪ the
  artwork) through `currency.source_digest` / `currency.source_fingerprint`,
  and assert the artwork is NOT in `node.files`.
- [x] 4.8 **Red**: editing the DECLARATION (the placement numbers) regenerates
  the part's artifacts as any source edit does. This is the accepted
  consequence of design D5; the test pins it so it cannot change by accident.

## 5. The document, and what must not change

- [x] 5.1 **Red**: two classes of the same name and the same parameters, one
  declaring a marking and one not, build identical STL bytes, the same piece id
  and the same `uniq_id` — run it on BOTH fixture pairs, and on the exact
  `Dial` pair additionally assert the `.brep` bytes are identical. The exact
  pair is what makes the BREP half a real comparison: an `StlNode` writes no
  `.brep`, so the faceted `Plate` pair asserts the STL, the piece id and the
  `uniq_id` and asserts that neither part wrote one.
- [x] 5.2 **Red**: `assertNoIntersectingSolids`, `assertNoDisconnectedSolids`
  and a pairwise sweep over the fixture assembly return the same verdicts with
  and without the markings, under `--faceted` and `--exact` alike; volume and
  bounds are unchanged; `children` is empty; the assembly's part count is
  unchanged; no tree node is named for a marking.
- [x] 5.3 **Red**: a rigid node declaring `digits` then `arrows` publishes a
  `markings` list of two entries in that order, each with `name`, `model`,
  `color` and `mtime`, with no placement and no `piece`; a node declaring none
  has no `markings` key; the `pieces` inventory is byte-identical with and
  without the markings.
- [x] 5.4 **Red**: a marking entry's `mtime` moves when its artwork is edited
  and the node's own `mtime` and `model` do not.
- [x] 5.5 Add the keyword-only `marking_path=None` callback to
  `serialize_node` (`serializer.py:627-673`), in the shape `piece_id` already
  has, and pass it from `core/builder.py:654`, `core/export.py:115` and
  `viewers/browser.py:83`. Confirm every existing `serialize_node` caller that
  passes only `model_path` still publishes the document it published.
- [x] 5.6 **Red**: byte-identity, WITHOUT recapturing anything. The seven
  captures under `tests/base_documents/` already exist and are the base's
  documents (`tests/test_running_document.py:234-280`); regenerating them with
  this cycle's code would make the assertion vacuous. So:
  - leave every existing capture byte-for-byte as it is, and require
    `ByteIdentityTest` to keep passing unchanged over its existing table — that
    is the red that would catch an accidental non-additive document change;
  - do NOT add the marking fixture to that table: the tree did not exist at any
    base, so there is no pre-marking capture of it to compare against. Assert
    its marking-free pair STRUCTURALLY instead — no node carries a `markings`
    key, the document declares the version its content already needed, and
    every node field is the set published today.
- [x] 5.7 **Red**: export copies every named marking under `models/`,
  preserving its build-relative path, with no parent traversal; a marking
  artifact outside the build directory fails export before the output
  directory is created or modified. Use an ordinary atomic copy, not
  `PieceInventory.copy_artifact`, which only serves registered pieces
  (`core/pieces.py:273-276`).
- [x] 5.8 **Red**: the sweep keeps every marking the snapshot names, and
  removes a marking artifact whose declaration was deleted, leaving the part's
  own artifacts untouched. Collect marking references in
  `_sweep_unreferenced_artifacts` (`core/builder.py:727-745`) so they are
  spared by reference, not by kind.
- [x] 5.9 **Red**: the OpenSCAD path is unaffected — a model whose parts
  declare markings renders through the OpenSCAD snapshot renderer exactly as
  the same model without them, and neither the build nor the render fails.

## 6. Documentation and the record

- [x] 6.1 Write `docs/markings.rst` — what a marking is and is not, the
  declaration, `Svg` and the open-wire rule, `Wrapped` (with the angular-zero
  convention stated outright and the `results_dial` circumference worked
  through), `Flat`, the colour, what the build writes, and what the viewer does
  and does not yet do. Voice and depth of `docs/leaf-nodes.rst`'s `StlNode`
  and `Build123dSheetNode` sections.
- [x] 6.2 Link it from `docs/index.rst`, and add the cross-reference from
  `docs/leaf-nodes.rst` and `docs/declaring.rst` where a reader would look
  first. Run the docs export test (`tests/test_docs_exports.py`).
- [x] 6.3 Add the `HISTORY.rst` Unreleased entry: what a marking is, that it
  adds no solid, no part and no piece, the additive document growth, and that
  the viewer draws it in its own release.
- [x] 6.4 Run the full suite plus a real caller —
  `projects/Calculators/Pascaline-module` — and record both results.
- [x] 6.5 AFTER implementation, extract the ADR: a marking is a declaration on
  a part that produces an artifact and no solid. Confirm the next free number
  at that moment (ADR-119 is the highest on this base, `main` at 710d86f,
  after the cycle branch was fast-forwarded on 2026-09-15: 118 is the
  skip-and-xfail record and 119 the renumbered named-project-models record,
  so expect **ADR-120**), write
  it under `docs/adrs/NODE/`, add its row to `docs/adrs/README.md` in
  chronological order, and update `docs/architecture.md` — the "Node model"
  section for the fourth declaration kind, "Build pipeline" for the per-marking
  artifact and its separate currency, "Export and embedding" for the additive
  `markings` list, and "Load-bearing invariants" for "a marking contributes no
  solid and no piece".
