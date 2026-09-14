## 1. Red first: pin every defect on the framework's own fixtures

`tests/step_project/duplicate_names.step` already exists and already carries
two distinct products named `Pin` (`evidence.md` §1) — no new fixture is
needed for the selector. One new fixture generator IS needed for §3's
same-named sub-assemblies, and it belongs in `tests/test_import_step.py`
beside `build_simple` / `build_nested` / `build_repeated`, which write into
the gitignored `tests/step_project/`.

- [ ] 1.1 In `tests/step_project/parts.py`, add two `StepNode` subclasses
      over `duplicate_names.step` declaring `part = 'Pin'` with
      `part_index = 1` and `part_index = 2`. In
      `tests/test_step_node.py::StepSelectionTest`, add a failing test that
      each builds and that their volumes are 1.000 and 8.000 mm³
      respectively (`evidence.md` §1 measured both). It must fail today with
      the ambiguity `ValueError`.
- [ ] 1.2 Add failing tests for each refusal: `part_index = 3` on a name two
      products carry (the message names the index and the count), a
      `part_index` below 1, and a `part_index` declared with no `part` (the
      message says an index selects among the products of a declared name).
      Each must report the document's inventory.
- [ ] 1.3 Add a failing test that `duplicate_names.step`'s inventory numbers
      the shared name — `Pin #1` and `Pin #2` — and that the ambiguity
      message names `part_index`. Add a test that
      `two_products.step`'s inventory carries NO `#`, pinning the
      no-change-for-unique-names promise; it must pass both before and
      after.
- [ ] 1.4 In `tests/test_step_assembly.py`, add failing tests that
      `StepAssembly(duplicate_names.step).products` reports two distinct
      identities and the selectors 1 and 2 for the two `Pin` entries, and
      that each occurrence reports the identity of the product it places and
      of its parent (`None` at the root).
- [ ] 1.5 In `tests/test_import_step.py`, add `build_dup_subassembly`
      (`evidence/probe_dup_subassembly.py` is the authoring code, verbatim)
      and a failing test that the generated `assembly.py` declares TWO
      `Stage` classes, one holding `Alpha` alone and one `Beta` alone. It
      must fail today with one merged class (`evidence.md` §3).
- [ ] 1.6 Add a failing test that `generate_parts` over
      `duplicate_names.step` returns two distinct classes, that each carries
      its own `part_index`, and that `generate_assembly` gives `Sub1` and
      `Sub2` DIFFERENT child classes. It must fail today with both naming
      `Pin_2` (`evidence.md` §2).
- [ ] 1.7 Add a failing test that COMPILES the `assembly.py` and `parts.py`
      generated for every fixture this module and `test_step_node.py`
      author — at minimum `import_simple`, `import_nested`,
      `import_repeated`, `single_product`, `wrapped_single_part`,
      `two_products`, `duplicate_names`, the new dup-sub-assembly file.
      Today three of them raise `IndentationError` (`evidence.md` §4).
- [ ] 1.8 Add a failing faithfulness test over `duplicate_names.step`
      through `GeneratedModelFaithfulnessTest._write_and_import`: the
      generated model must import, build, and place each `Pin` at its own
      occurrence's world matrix. Note that `_assert_faithful` matches a leaf
      to an occurrence by `leaf.part` alone, so it must first be taught to
      match on the selector, or it silently pairs the wrong occurrence.

## 2. The selector on the leaf

- [ ] 2.1 Add `StepNode.part_index = None` with a docstring stating: 1-based,
      among the products carrying the declared `part` name, in document
      order; required only when the name is shared; refused without `part`.
- [ ] 2.2 Rework `_select` to resolve `document.find(self.part)` once and
      then apply `part_index`: no index and one match selects it; no index
      and several is the existing ambiguity refusal; an index selects
      `matches[part_index - 1]`; an index below 1 or beyond `len(matches)`
      is refused naming both numbers; an index with `part is None` is
      refused before the candidate rule is reached.
- [ ] 2.3 Extend `_ambiguity_error` to name `part_index` as the way to
      choose, keeping the existing listing (`describe` per match) intact.
- [ ] 2.4 Teach `_Document` which names are shared (one counter over
      `self.order`, computed at index time) and have `describe` print
      ` #N` after the display name for a product whose name is shared, and
      nothing otherwise. Confirm every existing inventory test still passes
      unchanged.

## 3. The identity on the reader

- [ ] 3.1 Add `identity` and `part_index` to `ProductInfo` (`__slots__`,
      `__init__`, `__repr__`) and fill them in `StepAssembly.__init__`,
      counting same-named products over `document.order`.
- [ ] 3.2 Add `product_identity` and `parent_identity` to `Occurrence`
      (`__slots__`, `__init__`) and fill them in `_walk`, both for the
      component branch (`target_product.entry`, and the parent's entry or
      `None` when the parent is free) and for the bare-file branch, which
      already uses the product's own entry as its `identity`.
- [ ] 3.3 Confirm `Occurrence.identity` is untouched and still the COMPONENT
      label's entry; the reader's existing identity tests must pass
      unchanged.

## 4. The generator, keyed on identity

- [ ] 4.1 `generate_parts`: key the returned mapping on
      `product.identity`; emit `part_index = N` in `_part_class_source` only
      when the product's name is shared by another product of the document.
- [ ] 4.2 `generate_assembly`: order and name assembly classes by identity
      (`_ordered_assembly_names` becomes an identity walk, `None` still the
      document root), group occurrences by `parent_identity`, and resolve
      `_child_expression` on `occurrence.product_identity`.
- [ ] 4.3 Leave `_attribute_names` keyed on the product NAME (design D3) and
      add a comment saying why, so a later reader does not "fix" it.
- [ ] 4.4 Confirm the part-import line (`sorted(set(class_names.values()))`)
      now names every generated class, including the ones a duplicate name
      previously stranded.

## 5. Generated source that parses

- [ ] 5.1 Have `_placement_lines` report whether it emitted an operation,
      and `_assembly_class_source` append `        pass` when no child of
      that class emitted one — subsuming the existing childless-assembly
      fallback. Keep every comment.
- [ ] 5.2 Confirm 1.7 goes green for every fixture, and that the generated
      source for `import_simple`, `import_nested` and `import_repeated` is
      byte-identical to today's.

## 6. Documentation, decision record, and validation

- [ ] 6.1 Document `part_index` where `part` is documented (the `StepNode`
      class docstring, the module docstring's "selected, not guessed"
      paragraph, and the user documentation for the STEP leaf), with the
      inventory's `#N` shown.
- [ ] 6.2 Document in the `import-step` CLI documentation that the command
      emits the selector for a shared name.
- [ ] 6.3 Write ADR-115 (confirm the number is still free): a product is
      selected by name and, where the name is shared, by its index among the
      products of that name; the document entry stays the internal identity
      and the generator is keyed on it. Extends ADR-078, amends ADR-079.
      Carry design D1's rejected alternatives with their measurements. Add
      it to `docs/adrs/README.md` in chronological order and mark ADR-079
      amended.
- [ ] 6.4 Update `docs/architecture.md` where it describes STEP selection.
- [ ] 6.5 Run `tests/test_step_node.py`, `tests/test_step_assembly.py` and
      `tests/test_import_step.py` green, then the full suite once.
- [ ] 6.6 Mutation-check the two halves: reverting `_select`'s index lookup
      to `matches[0]` must fail 1.1; reverting `generate_parts` to
      name-keying must fail 1.6; removing the `pass` must fail 1.7.
- [ ] 6.7 Record in `workflow/warts.md` that the YouCanBuildDog, orcahand
      and Voron-2 duplicate-name findings are resolved here, and that
      per-solid selection remains open.
- [ ] 6.8 `openspec validate select-a-step-product --strict`, sync the
      baseline specs, and archive.
