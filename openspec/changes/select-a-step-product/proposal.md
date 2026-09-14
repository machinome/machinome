## Why

A STEP document routinely carries several distinct products under one name —
three `COMPOUND`s in YouCanBuildDog's `dog02_9g.stp`, 15 `SHELL`s in
orcahand's `ORCA_v1.step`, 118 `SOLID`s in Voron-2's frame export — and
`StepNode.part` is a name and nothing else. The framework refuses the
ambiguity correctly and describes every match, so the products *are*
distinguishable; there is simply no way to say which one is wanted, and all
three projects had to write their own STEP splitter to get past it
(`workflow/warts.md`: "# YouCanBuildDog" first bullet, "# orcahand_hardware"
both bullets, "# Voron-2" second bullet).

`solid import-step` makes it worse twice over. Its bookkeeping is keyed on
the product NAME, so on a document with duplicate names the later product
overwrites the earlier one's class and the generated assembly places the
wrong geometry; and every generated class it emits for those products
carries the same unusable `part = '<name>'`, so the command cannot build the
assembly it just scaffolded. Independently, a generated `render()` whose
children all sit at the identity contains comments and no statement, so the
generated module does not parse at all — measured here on three of the five
existing test fixtures, and met in the field on orcahand's 53 generated
adapters.

## What Changes

- A `StepNode` subclass SHALL be able to select one of several same-named
  products by declaring `part_index` beside `part`: the 1-based position of
  the product among the products of that name, in document order. The
  selector is relative to the name, so it can never contradict it.
- The ambiguity refusal and the document inventory SHALL print that number
  beside every product whose name is shared, so the maker copies the
  selector out of the failure that taught them the document's contents. A
  product whose name is unique SHALL print exactly as it does today.
- A `part_index` that names no product — out of range, below 1, or declared
  with no `part` — SHALL be refused by name with the same inventory, never
  silently rounded to a neighbour.
- `StepAssembly` SHALL report each product's own identity within the
  document and the selector a node must declare to select it, and each
  occurrence SHALL report the identity of the product it places and of the
  product it is placed in — so a reader of the structure, and the generator
  built on it, can tell two same-named products apart.
- `solid import-step` SHALL key every class it generates on the product's
  identity rather than on its name — one `StepNode` subclass per part
  product and one `AssemblyNode` subclass per assembly product, whatever
  their names — and SHALL emit `part_index` on a generated class whose
  product name is shared by another product of the document.
- Every module `solid import-step` writes SHALL parse: a generated `render()`
  with no executable placement SHALL carry `pass`.
- **Out of scope**, recorded here so it is not read into this change:
  per-solid selection of a multi-solid product (a `solid` index beside
  `part`, or `solid import-step --per-solid`), which YouCanBuildDog also
  asked for; selecting a product the document leaves unnamed; and a document
  with several free root products, whose children still collapse into one
  generated root class.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `step-import`: the requirement "One part selected out of the document by
  product name" gains the index that resolves a shared name, the refusals
  for an index that names no product, and the numbering the inventory
  prints.
- `step-assembly`: "The document's assembly structure is readable" gains the
  product's identity and its selector; "Every occurrence of the document is
  walked" gains the identity of the product placed and of its parent;
  "Generated part source" gains the emitted selector and is keyed on the
  product rather than on its name; "Generated assembly source" becomes one
  class per assembly PRODUCT rather than per assembly NAME, and must always
  parse.

## Impact

- `solid_node/node/adapters/step.py` — `StepNode.part_index`, `_select`,
  `_selection_error`, `_ambiguity_error`, `_Document.describe` /
  `inventory` / `find`; `ProductInfo` and `Occurrence` gain their identity
  fields and `StepAssembly` fills them.
- `solid_node/manager/import_step.py` — `generate_parts`,
  `generate_assembly`, `_ordered_assembly_names`, `_child_expression`,
  `_placement_lines`, `_assembly_class_source`.
- `tests/test_step_node.py`, `tests/test_step_assembly.py`,
  `tests/test_import_step.py` — new red-first tests; `test_import_step.py`'s
  faithfulness helper matches a generated leaf to its occurrence by `part`
  alone today and must match on the selector.
- `docs/` — the STEP leaf's and the import command's documentation.
- Projects: YouCanBuildDog, orcahand_hardware and Voron-2 can drop their
  project-local STEP splitters for the products they only needed to name.
  Nothing existing breaks: `part_index` is optional and a document of
  unique names behaves exactly as before.
- New ADR: the selector's spelling and the generator's identity are a
  public-interface decision extending ADR-078 and amending ADR-079.
