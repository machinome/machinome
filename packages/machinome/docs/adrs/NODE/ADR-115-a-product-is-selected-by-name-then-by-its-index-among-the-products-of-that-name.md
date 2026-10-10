# ADR-115: A product is selected by name, then by its index among the products of that name

**Status:** Accepted

**Date:** 2026-09-14

**Change:** `select-a-step-product`

**Extends:**
- [ADR-078: The STEP part as an exact external-file
  leaf](ADR-078-the-step-part-as-an-exact-external-file-leaf.md)

**Amends:**
- [ADR-079: Reading a STEP document's placements and scaffolding
  declarative
  source](ADR-079-reading-a-step-documents-placements-and-scaffolding-source.md)

## Context and Problem Statement

`StepNode.part` (ADR-078) is a name, and a STEP document routinely
carries several distinct products under one name — three `COMPOUND`s in
YouCanBuildDog's `dog02_9g.stp`, 15 `SHELL`s in orcahand's
`ORCA_v1.step`, 118 `SOLID`s in Voron-2's frame export
(`workflow/warts.md`). The framework's ambiguity refusal is already
correct and already excellent — it lists every match with its kind,
occurrence count, solid count, bounding box and volume — so the
products *are* distinguishable. There is simply no way for a `part`
declaration to say which one is meant, and all three projects wrote
their own STEP splitter to get past it.

`solid import-step` (ADR-079) makes the same gap worse twice over. Its
bookkeeping was keyed on the product NAME throughout: `generate_parts`
built `class_names[product.name] = class_name`, so on a document with a
duplicate name the second product's class silently overwrote the
first's, and `generate_assembly`'s `_ordered_assembly_names`,
`occurrences_by_parent` and `assembly_class_names` collapsed the same
way for a duplicate ASSEMBLY name — a document with two distinct
sub-assemblies sharing one name generated one merged class holding both
their children (measured: `evidence.md` §2 and §3 of this change,
reproduced on the framework's own fixtures). And every class generated
for a shared name declared the same unusable `part = '<name>'`, so the
command scaffolded an assembly it could not itself build. Independently,
`_placement_lines` always emitted a comment first, so the
`render_lines or ['        pass']` fallback in `_assembly_class_source`
never fired for the case that actually occurs — an assembly whose
children all stand at the identity — and three of the five `StepNode`
fixtures already generated an `assembly.py` that raises
`IndentationError` on import (`evidence.md` §4); orcahand met the same
defect on 53 generated adapters.

Nothing on the public surface could express "the second `Pin`":
`ProductInfo` carried name/kind/occurrence_count/solid_count/color with
no identity, and `Occurrence` named the product it places and the
product it is placed in by NAME (`product_name`, `parent_name`), even
though `Occurrence.identity` itself is already the COMPONENT label's own
entry — a placement's identity, not a product's.

## Decision Drivers

- One public, stable, readable way for a `StepNode` to say which of
  several same-named products it means, printed by the failure that
  already teaches the maker the document's contents.
- A selector that stays correct across the ordinary edit a vendor file
  gets — an unrelated product added or reordered elsewhere in the
  document.
- A generator whose bookkeeping cannot collapse: one generated class per
  PRODUCT, whatever the document calls it, whether the product is a
  part or a sub-assembly.
- Generated source that always parses.
- No behaviour change whatever for a document whose product names are
  distinct — every existing test fixture but one, every existing
  scenario, and most vendor files.

## Considered Options

For the selector's spelling (`part_index` chosen):

1. **`part_index = N`, 1-based, relative to the declared name, in
   document order** (chosen)
2. `entry = '0:1:1:5'`, the OCCT tag-path identity `StepAssembly`
   already computes
3. `index = N`
4. `occurrence = N`
5. A composite `part = 'Pin#2'`
6. `within = 'Sub2'`, the parent assembly's name

For the generator's bookkeeping key: keep it on the product NAME, or
move it to the product's own identity (chosen).

For a `render()` whose children are all at the identity: drop the
identity comment entirely, or keep every comment and append an inert
`pass` (chosen).

## Decision Outcome

Chosen: **`part_index`, a 1-based index relative to the declared `part`
name, in document order** — `_select` resolves `matches =
document.find(part)` exactly as before and then applies the index:
`matches[part_index - 1]`, refusing an index below 1, beyond
`len(matches)`, or declared with no `part`. `StepAssembly` publishes the
same fact as everyone's shared read: `ProductInfo.identity` and
`.part_index`, `Occurrence.product_identity` and `.parent_identity`.
`solid import-step`'s generator is keyed on `product.identity`
throughout, class names still derived from the product NAME by the
existing rule, and emits `part_index` only on a class whose name is
shared. `_assembly_class_source` appends `pass` whenever the class it
is writing emitted no rotate/translate statement at all.

### `part_index` is relative to the name, not to the document

Four alternatives to `part_index` were measured and rejected.

**The OCCT tag-path entry** (`'0:1:1:5'`) is the document's own stable
per-read identity, and `StepAssembly` already computes it — no new
derivation needed. Rejected on a measurement
(`evidence/probe_stability.py`, `evidence.md` §5): exporting the same
model with one unrelated `Bracket` product inserted ahead of the two
`Pin`s moves BOTH pins' entries (`0:1:1:3 → 0:1:1:4`,
`0:1:1:5 → 0:1:1:6`), while their name-relative indices stay 1 and 2
and keep naming the same 1 mm³ and 8 mm³ solids. Worse, `0:1:1:5` in the
re-export is a different product entirely — the sub-assembly
`Sub2` — so a stale entry selector would need a cross-check against
`part` just to avoid silently selecting the wrong product. The entry is
also an OCCT/XCAF implementation detail to publish into project source,
and it collides visually with `Occurrence.identity`, which already
means a placement, not a product. Kept as the reader's own internal key
(`ProductInfo.identity`), where none of these objections apply — a
`StepAssembly` is read live against the file in hand, so its identity
is exact for that read; a node's `part_index` is written into source
that outlives the export.

**`index = N`** is refused outright by the framework:
`declarative._check_index` (`solid_node/node/declarative.py:573`)
raises `TypeError` on `.repeat()` of any class declaring a class
attribute named `index`, because each realized copy carries its own
0-based position under that exact name. A repeated `StepNode` is the
ordinary case (the step-assembly spec's own fourteen-bolt scenario), so
this spelling would make the framework's two STEP-facing features
mutually exclusive — confirmed directly
(`evidence/probe_index_name.py`, `evidence.md` §6).

**`occurrence = N`** — the wart log's own working phrase — is wrong in
this capability's own vocabulary: an occurrence is a PLACEMENT
(`StepAssembly.occurrences`, the `Occurrence` class, the step-assembly
spec's "every occurrence of the document is walked"), and the
inventory's own line for the very product this selector would call
number 2 already says "1 occurrence". This ADR's title and the spec use
"product" throughout; the change's directory name keeps the older word
only for continuity with the originating briefing.

**A composite `part = 'Pin#2'`** was rejected because the step-assembly
spec makes `part` the record of the product name exactly as the file
carries it — the fact that makes the product recoverable from generated
source — and `#` is a legal character in a STEP product name, so this
spelling is ambiguous on exactly the documents that need it most.

**`within = 'Sub2'`** (the parent assembly's name) is readable but not a
function: a product may be placed in several parents, two same-named
products may share one parent, and — the case this change's own
sub-assembly fixture is built to show (`evidence.md` §3) — the parents
themselves can share a name too.

`part_index` has a property none of the rejected spellings has: being
relative to the declared name, it can never contradict it. There is no
"the entry says one product and the name says another" state to specify
or refuse.

### `StepAssembly` publishes the product's identity and its selector

`ProductInfo` gains `identity` (the product's own document entry) and
`part_index` (its 1-based position among products of its own name, 1
when the name is unique); `Occurrence` gains `product_identity` and
`parent_identity` (`None` at the document root, matching
`parent_name`). `Occurrence.identity` keeps its existing meaning — the
COMPONENT label's entry, a placement — untouched. `part_index` is
derivable from `identity` plus document order, so strictly only the
identities are needed by the generator; it is published anyway because
the reader is the document's public inspection surface and the selector
is exactly what a reader of it is looking for, and deriving it costs
one counter over a list the constructor already walks.

### The generator is keyed on identity end to end; class-naming and attribute-naming rules are untouched

`generate_parts` returns `{product.identity: class_name}` instead of
`{product.name: class_name}`. `generate_assembly`'s
`_ordered_assembly_names` becomes `_ordered_assembly_identities` — the
same children-before-parents walk, now over identities, `None` still
standing for the document root — `occurrences_by_parent` groups on
`parent_identity`, and `_child_expression` resolves
`occurrence.product_identity`. Class NAMES still come from product
names through ADR-079's existing rule, and the existing `_unique`
suffix (`Pin`, `Pin_2`) already distinguishes two classes derived from
one name — it was always there; what was missing is that the two
classes were never both reachable, because the dict that held them
collapsed first.

`_attribute_names` stays keyed on the product NAME, deliberately: its
`_1`/`_2` suffix answers "does this parent place this name more than
once", which is the readable question for a human-facing attribute.
Keying it on identity would regress that: one parent holding two
DIFFERENT `Pin` products would then produce `pin` and `pin_2` instead of
`pin_1` and `pin_2`.

`_part_class_source` emits `part_index = N` only when the product's
name is shared by another product of the document, so generated source
for an ordinary document — every existing fixture but one — is
byte-identical to before this change (confirmed for `import_simple`,
`import_nested` and `import_repeated`).

### `pass` is emitted exactly when a `render()` states no operation

`_placement_lines` now returns whether it emitted a rotate or a
translate line alongside its lines; `_assembly_class_source` tracks
whether ANY child of the class emitted one, and appends `        pass`
after the comment block when none did. The pre-existing
`render_lines or ['        pass']` fallback for a class with no child at
all is subsumed by the same check. Every comment is kept: a comment is
what tells a pilot which occurrence sits where, and the `pass` beneath
it changes no placement. Dropping the identity comment entirely instead
was considered and rejected: a class body that mentions a child and
then never mentions it again in `render()` reads worse than one that
says explicitly it is placed at the identity, and the spec already asks
for a comment per placement.

### The inventory prints the index only where a name is shared

`_Document` now counts, at index time, how many products of the
document share each declared name, and each named product's 1-based
position among them. `describe` appends ` #N` after the display name
only for a product whose name another product shares; a product whose
name is its own prints exactly as it always has — confirmed for every
pre-existing inventory scenario and test, and pinned by a dedicated test
that `two_products.step`'s inventory carries no `#` at all, before and
after this change. `_ambiguity_error` gains one trailing sentence naming
`part_index` as the way to choose; the per-match listing it already
built from `describe` carries the new index for free.

## Pros and Cons of the Options

### `part_index`, relative to the name (chosen)

- **Good**: Cannot contradict `part` — there is no "entry says X, name
  says Y" state
- **Good**: Survives the ordinary edit — an unrelated product inserted
  or appended elsewhere in the document — that the OCCT entry does not
  (`evidence.md` §5)
- **Good**: Printed on the exact inventory line the maker is already
  reading for bounds, solid count and volume
- **Bad**: A `part_index` written against one export can silently
  select a different product after a re-export that adds or removes a
  same-named product ahead of it (accepted — the out-of-range refusal
  catches the shrinking case loudly, and nothing can prevent the
  general one for any selector short of content hashing the geometry)

### The OCCT tag-path entry as the node's own selector

- **Bad**: Moves under a re-export that changes unrelated products
  (`evidence.md` §5), an XCAF implementation detail to publish into
  project source, and visually collides with `Occurrence.identity`
  (a placement, not a product)

### `index = N`

- **Bad**: Refused outright by `declarative._check_index` on any
  `.repeat()`'d class — makes selection and repetition mutually
  exclusive (`evidence.md` §6)

### `occurrence = N`

- **Bad**: Wrong in the capability's own vocabulary — an occurrence is
  a placement, and the very inventory line this selector would be read
  off already says "1 occurrence" for the product it would call number 2

### A composite `part = 'Pin#2'`

- **Bad**: `#` is a legal STEP product-name character, so the spelling
  is ambiguous on exactly the documents needing it most, and it breaks
  `part`'s existing promise to carry the exact document name

### `within = 'Sub2'`, the parent's name

- **Bad**: Not a function — several parents, several same-named
  children of one parent, and same-named parents are all real shapes a
  vendor document takes

## Consequences

- New: `StepNode.part_index`; `StepAssembly`'s `ProductInfo.identity` /
  `.part_index` and `Occurrence.product_identity` /
  `.parent_identity`; `_Document.name_is_shared` / `.part_index`, and
  the ` #N` the inventory prints for a shared name.
- Changed: `_select`, `_ambiguity_error`, `_Document.describe` in
  `solid_node/node/adapters/step.py`; `generate_parts`,
  `_ordered_assembly_names` (renamed `_ordered_assembly_identities`),
  `_child_expression`, `_placement_lines`, `_assembly_class_source` in
  `solid_node/manager/import_step.py`.
- `tests/test_import_step.py`'s `_assert_faithful` matched a generated
  leaf to an occurrence by `leaf.part` alone; it now resolves
  `(leaf.part, leaf.part_index)` through `assembly.products` to the
  product's own identity before matching an occurrence, or a
  duplicate-name document would silently pair a leaf with whichever
  occurrence a name-only lookup found first — the exact defect this
  change repairs, not a hypothetical one.
- Nothing changes for a document whose product names are all distinct:
  the inventory prints no index, generated source is byte-identical,
  and every pre-existing scenario and test passes unchanged.
- Not built here: per-solid selection of a multi-solid product (a
  `solid` index beside `part`, YouCanBuildDog's other ask), selecting a
  product the document leaves unnamed, and the pre-existing collapse of
  several free root products into one generated root class. Recorded in
  `workflow/warts.md`, untouched by this change.
- The three originating projects — YouCanBuildDog, orcahand_hardware,
  Voron-2 — may retire their project-local STEP splitters at their own
  pace; `workflow/warts.md` records the resolution against each finding.

## References

- `solid_node/node/adapters/step.py` — `StepNode.part_index`, `_select`,
  `_ambiguity_error`, `_index_range_error`, `_index_without_part_error`,
  `_Document.name_is_shared` / `.part_index` / `.describe`; `ProductInfo`,
  `Occurrence`
- `solid_node/manager/import_step.py` — `generate_parts`,
  `_ordered_assembly_identities`, `_child_expression`,
  `_placement_lines`, `_assembly_class_source`, `generate_assembly`
- `tests/test_step_node.py::StepSelectionTest` — the selector, its
  refusals, and the inventory's index
- `tests/test_step_assembly.py::StepAssemblyIdentityTest` — the
  reader's identity and selector fields
- `tests/test_import_step.py` — the generator keyed on identity, the
  compiled-source proof, and the faithfulness fix
- `docs/leaf-nodes.rst`, `:ref:`step-import`` — `part_index` documented
  beside `part`
- `docs/cli.rst`, `:ref:`import-step`` — the command's emitted selector
- `workflow/warts.md` — "YouCanBuildDog", "orcahand_hardware", "Voron-2"
  — the three originating findings this change resolves
- OpenSpec change `select-a-step-product`, capabilities `step-import`
  and `step-assembly`
