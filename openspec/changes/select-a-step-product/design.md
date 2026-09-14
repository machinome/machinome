## Context

Three mechanisms in two modules identify a STEP product, and only one of
them does it correctly.

**The document reader.** `_Document.__init__`
(`solid_node/node/adapters/step.py:168`) indexes every product by
`_entry(label)` — `TDF_Tool.Entry_s`'s tag path from the document root,
`"0:1:1:5"` — and `self.order` keeps them in the order `GetShapes` listed
them. The entry is the only thing in the module that identifies a product;
`_Product.name` is whatever the writer put on the label, and nothing forbids
two labels carrying one name.

**The leaf's selection.** `StepNode._select` (`step.py:476`) calls
`_Document.find(self.part)` (`step.py:215`), which returns EVERY product of
that name in document order, and refuses when there is more than one
(`_ambiguity_error`, `step.py:500`). The refusal is good — it describes each
match with its kind, occurrence count, solid count, bounds and volume — but
`part` is the only selector the class has, so the refusal is terminal. In
the field this is three projects and a hand-written splitter apiece
(`workflow/warts.md`: YouCanBuildDog's three `COMPOUND`s, orcahand's 15
`SHELL`s, Voron-2's 118 `SOLID`s).

**The generator.** `generate_parts` (`solid_node/manager/import_step.py:130`)
builds `class_names[product.name] = class_name`, and `generate_assembly`
(`:272`) keys `_ordered_assembly_names`, `occurrences_by_parent` and
`assembly_class_names` on names as well, because `Occurrence` carries
`product_name` and `parent_name` and no identity for either. Every one of
those dicts collapses on a duplicate name, so the generator is broken before
the selector question is even reached — measured in `evidence.md` §2 and §3:
on `duplicate_names.step` both sub-assemblies are given the SECOND `Pin`,
and on a two-`Stage` document the two sub-assemblies merge into one class
holding both children, doubling the model's solids.

Independently of names, `_placement_lines` (`:233`) always emits a comment
first, so `render_lines` in `_assembly_class_source` (`:255`) is empty only
when the assembly has no child at all — and the `['        pass']` fallback
therefore never fires for the case that actually occurs: an assembly whose
children all stand at the identity, whose `render()` body is comments only
and whose module raises `IndentationError` on import. Three of the five
`StepNode` fixtures already generate an unparseable `assembly.py`
(`evidence.md` §4); orcahand met it on 53 generated adapters.

Nothing on the public surface can express "the second `Pin`". `ProductInfo`
(`step.py:537`) carries name/kind/occurrence_count/solid_count/color;
`Occurrence` (`step.py:557`) carries `identity` — the COMPONENT label's
entry, which identifies a placement, not a product — plus `product_name` and
`parent_name`.

## Goals / Non-Goals

**Goals:**

- One public, stable, readable way for a `StepNode` to say which of several
  same-named products it means, printed by the failure that taught the maker
  the document's contents.
- A generator whose bookkeeping cannot collapse: one generated class per
  product, whatever the document calls it.
- Generated source that always parses.
- No behaviour change whatever for a document whose product names are
  distinct — which is every existing test fixture but one, every existing
  scenario, and most vendor files.

**Non-Goals:**

- Per-solid selection of a multi-solid product (`--per-solid`, a `solid`
  index beside `part`). YouCanBuildDog asks for it and it is the general
  answer to "an upstream product is not a printed piece", but it is a
  different question — which piece of one product — and a different unit of
  geometry. Recorded in `workflow/warts.md`, untouched here.
- Selecting a product the document leaves unnamed (`find` compares against
  `None`, and `part = None` already means selection by omission).
- A document with several free root products, whose children all report
  `parent_name = None` and collapse into one generated root class today.
  Pre-existing, unchanged, out of scope.
- Any change to how geometry, colour, frames, admission or the document
  cache work.

## Decisions

### D1. The selector is `part_index`: 1-based, among the products of the declared name, in document order

A subclass writes

    class UpperPin(StepNode):

        step_source = 'vendor/hinge.step'
        part = 'Pin'
        part_index = 2

and the inventory it copies that from reads

      Pin #1: part, 1 occurrence, 1 solid, bounds (-0.500, …)…, volume 1.000
      Pin #2: part, 1 occurrence, 1 solid, bounds (-1.000, …)…, volume 8.000

`_select` becomes: resolve `matches = document.find(part)` exactly as today,
then take `matches[part_index - 1]` when an index is declared, refusing
`part_index` without `part`, below 1, or beyond `len(matches)`.

Four alternatives were weighed.

**(a) `entry = '0:1:1:5'`, the OCCT tag path.** The document already carries
it, `Occurrence.identity` already publishes one, and it needs no new
derivation. Rejected on a measurement (`evidence.md` §5): exporting the same
model with one unrelated product inserted ahead of the pins moves BOTH pins'
entries — `0:1:1:3 → 0:1:1:4` and `0:1:1:5 → 0:1:1:6` — while their
name-relative indices stay 1 and 2 and keep naming the same 1 mm³ and 8 mm³
solids. Worse, `0:1:1:5` in the new document is a SUB-ASSEMBLY named `Stage`,
so a stale entry selector would have to be caught by a cross-check against
`part` to avoid selecting something else entirely. The entry is also an XCAF
implementation detail to publish into project source, and it collides
visually with `Occurrence.identity`, which is a *component* label entry of
the same shape and means a placement, not a product. Kept as the INTERNAL
key (D3) where none of those objections apply.

**(b) `index = 2`.** Shortest and most obvious, and refused outright by the
framework: `declarative._check_index`
(`solid_node/node/declarative.py:573`) raises `TypeError` on `.repeat()` of
any class that declares a class attribute named `index`, because each
realized copy carries its 0-based position under that name. A repeated
`StepNode` is the ordinary case — the step-assembly spec's own
fourteen-bolt scenario — so this spelling would make the framework's two
STEP-facing features mutually exclusive. Measured in `evidence.md` §6.

**(c) `occurrence = 2`.** The wart log's own phrasing, and wrong in this
capability's vocabulary: an occurrence is a PLACEMENT
(`StepAssembly.occurrences`, the `Occurrence` class, the spec requirement
"Every occurrence of the document is walked"), and the inventory line this
selector is copied from says "1 occurrence" for the very product it would
call number 2. The change's directory name keeps the word for continuity
with the briefing; the ratified vocabulary does not.

**(d) A composite `part = 'Pin#2'`.** Rejected because the step-assembly
spec makes `part` the record of the product name exactly as the file carries
it — that is what makes the product recoverable from generated source — and
`#` is a legal character in a STEP product name, so the spelling is
ambiguous on the documents that need it most.

**(e) `within = 'Sub2'`, the parent assembly.** Readable, and not a
function: a product may be placed in several parents, two same-named
products may share one parent, and the parents themselves can share a name
(`evidence.md` §3 is exactly that document).

`part_index` also has a property none of the others has: being relative to
the name, it cannot contradict it. There is no "the entry says one product
and the name says another" state to specify or to refuse.

### D2. `StepAssembly` publishes the product's identity and its selector

`ProductInfo` gains `identity` (the product's entry) and `part_index`;
`Occurrence` gains `product_identity` and `parent_identity` (`None` at the
document root, matching `parent_name`). `Occurrence.identity` keeps its
meaning — the component label's entry, a placement — and is untouched.

`part_index` is derivable from `identity` plus document order, so strictly
only the identities are needed by the generator. It is published anyway
because the reader is the document's public inspection surface and the
selector is what a reader is looking for; deriving it costs one counter over
a list the constructor already walks.

The entry is published here and NOT as the node's selector because the two
uses differ: `StepAssembly` is read live against the file in hand, where the
entry is exact and stable, while a node's `part_index` is written into
source that outlives the export (D1's measurement).

### D3. The generator is keyed on the product's identity, end to end

`generate_parts` returns `{product_identity: class_name}`. `generate_assembly`
orders and names assembly classes by identity (`_ordered_assembly_names`
becomes a walk over identities, with `None` still standing for the document
root), groups occurrences by `parent_identity`, and `_child_expression`
resolves `occurrence.product_identity`. Class NAMES continue to come from
product names through the existing rule, and the existing `_unique` suffix
(`Pin`, `Pin_2`) already distinguishes two classes derived from one name —
it was always there; what was missing is that the two classes were never
both reachable.

Attribute naming (`_attribute_names`, `:194`) stays keyed on the product
NAME and is not changed. Its `_1`/`_2` suffix answers "does this parent
place this name more than once", which is the right question for a
human-readable attribute, and its defensive de-duplication loop already
keeps every name unique. Keying it on identity would REGRESS readability:
one parent holding two different `Pin` products would produce `pin` and
`pin_2` instead of `pin_1` and `pin_2`.

`_part_class_source` emits `part_index = N` only when the product's name is
shared by another product of the document, so generated source for an
ordinary document is byte-identical to today's.

### D4. `pass` is emitted when a `render()` states no operation

`_assembly_class_source` tracks whether any child produced a rotate or a
translate line — `_placement_lines` already knows (`emitted`), and returning
that flag beside the lines is the whole mechanism — and appends
`        pass` after the comment block when none did. The existing
`render_lines or ['        pass']` fallback for a childless assembly is
subsumed by the same test. Comments are kept: they are what tells the pilot
which occurrence sits where, and a `pass` under them changes no placement.

An alternative was to drop the "`# <attr> is placed at the identity`"
comment and emit nothing for an identity child; rejected, because a class
body that mentions a child and never mentions it again in `render()` is
harder to read than one that says so, and the spec already asks for a
comment per placement.

### D5. What the inventory prints

`_Document.describe` prefixes nothing today. It gains `#N` after the display
name for a product whose name another product of the document shares, and
prints unchanged otherwise, so every existing inventory scenario and test
holds verbatim. `_ambiguity_error` gains one sentence naming `part_index` as
the way to choose. The listing itself is `describe` for each match, so the
numbering appears there for free.

## Risks / Trade-offs

- **A `part_index` written against one export silently selects a different
  product after a re-export that adds or removes a same-named product.** →
  Nothing can prevent that; a name-relative index is the most robust
  selector measured (D1(a)), and the cheap defence is that adding an
  unrelated product does not disturb it. The refusal for an out-of-range
  index catches the shrinking case loudly.
- **A maker copies the number off a line whose bounds and volume they did
  not read.** → The number is printed on the same line as the bounds, solid
  count and volume, which is exactly what the wart log praises about the
  existing refusal; nothing else about the line changes.
- **Publishing four new public attributes on `StepAssembly` widens a young
  public surface.** → Each is a fact the reader already computes
  (`_Product.entry` and document order); none carries geometry, none is
  optional-in-some-documents, and the generator — the reader's one
  in-framework consumer — needs three of them.
- **The faithfulness test in `tests/test_import_step.py` matches a generated
  leaf to an occurrence by `leaf.part` alone.** → It must match on the
  selector; on a duplicate-name document the name-only match silently pairs
  a leaf with the wrong occurrence's matrix, which is precisely the defect
  under repair. Task 1.6 makes that test red first.
- **`part_index` is a new attribute name on a widely-subclassed adapter.** →
  A project class already declaring `part_index` would be shadowing the
  selector. No such name exists in any project in this workspace; the
  attribute defaults to `None` and an undeclared class behaves exactly as
  today.

## Migration Plan

None required. `part_index` defaults to `None`; a document of unique names
produces identical selection behaviour, an identical inventory, and
byte-identical generated source. The generated-`pass` change alters only
modules that do not parse today. Projects that built STEP splitters may
retire them at their own pace.

## Open Questions

1. **The change's name says "occurrence" and the selector says "product".**
   The directory name comes from the briefing; the ratified vocabulary in
   the specs is "product" throughout (D1(c)). Confirm the directory name
   stands, or rename the change before archive.
2. **Should `solid import-step` emit `part_index` on EVERY generated class,
   not only on the shared names?** Uniform output is easier to reason about
   and makes a later re-export's drift visible; the proposal emits it only
   where it is needed so that generated source for ordinary documents does
   not change. Pilot's call.
3. **Should the ambiguity refusal stay an error at all when a document's
   same-named products are geometrically identical?** Not proposed — the
   framework cannot cheaply prove two B-reps equal — but Voron-2's 118
   `SOLID`s are the case where a maker would ask.
4. **ADR number.** ADR-115 is the next free number under `docs/adrs/NODE/`
   at the time of writing; confirm before promotion.

Reviewer's resolution of open question 1, before the planning commit: the change is
named `select-a-step-product`, in the capability's own vocabulary -- a PRODUCT is what
`part`/`part_index` select; an OCCURRENCE is a placement. The wart log's plan entry
used the older name.
