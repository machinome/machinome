# Evidence: `select-a-step-product`

Everything below was measured in the `fix-warts` worktree at
`d3dfba7`, with the workspace venv:

    cd /home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python …
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/solid …

No framework source was changed. The fixtures are the committed generators
in `tests/step_project/` (the `.step` files themselves are gitignored and
written by each test module's `setUpModule`); the probes are in
`evidence/`, the generated samples in `evidence/generated/`.

Originating projects and findings, all in `workflow/warts.md`:
YouCanBuildDog (three products named `COMPOUND`), orcahand_hardware
(15 products named `SHELL`, and a generated module raising
`IndentationError`), Voron-2 (118 products named `SOLID`).

---

## §1. The fixture, and the refusal as it stands

`tests/step_project/duplicate_names.step` already exists — written by
`tests/test_step_node.py`'s `build_duplicate_names`, whose comment records
that duplicate names need two assembly levels because `cadquery.Assembly`
refuses two same-named children at one level. It holds two distinct products
named `Pin`: a 1 mm cube in `Sub1` and a 2 mm cube in `Sub2`.
`tests/test_step_node.py::StepSelectionTest::test_an_ambiguous_name_is_refused_describing_both`
already asserts the refusal. **No new fixture is needed for part 1.**

    evidence/probe_select.py

    == fixture: …/tests/step_project/duplicate_names.step
    -- document order / entries / names / kinds / candidate
      entry='0:1:1:1' name='Root' kind=root assembly is_free=True is_assembly=True candidate=False occurrences=1
      entry='0:1:1:2' name='Sub1' kind=sub-assembly is_free=False is_assembly=True candidate=True occurrences=1
      entry='0:1:1:3' name='Pin' kind=part is_free=False is_assembly=False candidate=True occurrences=1
      entry='0:1:1:4' name='Sub2' kind=sub-assembly is_free=False is_assembly=True candidate=True occurrences=1
      entry='0:1:1:5' name='Pin' kind=part is_free=False is_assembly=False candidate=True occurrences=1
    -- find("Pin") -> ['0:1:1:3', '0:1:1:5']

    == refusal through StepNode (parts.AmbiguousPin)
    ValueError: AmbiguousPin: …/duplicate_names.step has 2 products named 'Pin'; the name is ambiguous between:
      Pin: part, 1 occurrence, 1 solid, bounds (-0.500, -0.500, -0.500)..(0.500, 0.500, 0.500), volume 1.000
      Pin: part, 1 occurrence, 1 solid, bounds (-1.000, -1.000, -1.000)..(1.000, 1.000, 1.000), volume 8.000

The two products are distinguishable in the listing (1.000 against 8.000
mm³) and nothing in the class can say which. This is the wart's claim,
reproduced.

The public reader cannot say it either — `ProductInfo` carries no identity,
so its two `Pin` entries are indistinguishable, and `Occurrence` names its
product and its parent by NAME:

      product ProductInfo(name='Pin', kind='part', occurrence_count=1, solid_count=1, color=None)
      product ProductInfo(name='Pin', kind='part', occurrence_count=1, solid_count=1, color=None)
      occurrence identity='0:1:1:1:1' label_name='10' product_name='Sub1' parent=None
      occurrence identity='0:1:1:2:1' label_name='Pin' product_name='Pin' parent='Sub1'
      occurrence identity='0:1:1:1:2' label_name='12' product_name='Sub2' parent=None
      occurrence identity='0:1:1:4:1' label_name='Pin' product_name='Pin' parent='Sub2'

`Occurrence.identity` is the COMPONENT label's entry (`0:1:1:2:1`), which
identifies a placement. The PRODUCT entries (`0:1:1:3`, `0:1:1:5`) are
computed by the reader and published nowhere.

---

## §2. `solid import-step` on that same document: two classes, one selector, wrong children

    solid import-step tests/step_project/duplicate_names.step --into <scratch> --model dup

**`parts.py` — 2 classes, both carrying the same unusable selector**
(`evidence/generated/duplicate_names/parts.py`; the long relative
`step_source` is an artifact of generating into a scratch directory):

    class Pin(StepNode):
        step_source = '…/duplicate_names.step'
        part = 'Pin'
        angular_deflection = 0.5

    class Pin_2(StepNode):
        step_source = '…/duplicate_names.step'
        part = 'Pin'
        angular_deflection = 0.5

Building either raises §1's `ValueError`. The command scaffolds an assembly
it cannot build — orcahand's finding, on the framework's own fixture.

**`assembly.py` — the name-keyed bookkeeping has already collapsed**
(`evidence/generated/duplicate_names/assembly.py`):

    from .parts import Pin_2

    class Sub1(AssemblyNode):
        pin = Pin_2()
        …
    class Sub2(AssemblyNode):
        pin = Pin_2()

`generate_parts` writes `class_names[product.name] = class_name`, so the
second `Pin` product's class overwrites the first's; `_child_expression`
then resolves both occurrences to `Pin_2`. The class `Pin` is emitted, named
in no import, and referenced nowhere. `Sub1` holds the 1 mm cube in the
document and the 2 mm cube in the generated model: this is a silent geometry
error, not only a build failure.

---

## §3. Same-named SUB-ASSEMBLIES merge into one class

`generate_assembly` keys `_ordered_assembly_names`, `occurrences_by_parent`
and `assembly_class_names` on names too. `evidence/probe_dup_subassembly.py`
authors a three-level document: `Root` holds `Left` and `Right`, each
holding a sub-assembly named `Stage`, holding `Alpha` (1 mm) and `Beta`
(2 mm) respectively.

    -- products
       entry=0:1:1:1    name=Root     kind=root assembly
       entry=0:1:1:2    name=Left     kind=sub-assembly
       entry=0:1:1:3    name=Stage    kind=sub-assembly
       entry=0:1:1:4    name=Alpha    kind=part
       entry=0:1:1:5    name=Right    kind=sub-assembly
       entry=0:1:1:6    name=Stage    kind=sub-assembly
       entry=0:1:1:7    name=Beta     kind=part
    -- occurrences
       identity=0:1:1:1:1    product='Left' parent=None
       identity=0:1:1:2:1    product='Stage' parent='Left'
       identity=0:1:1:3:1    product='Alpha' parent='Stage'
       identity=0:1:1:1:2    product='Right' parent=None
       identity=0:1:1:5:1    product='Stage' parent='Right'
       identity=0:1:1:6:1    product='Beta' parent='Stage'

The generated source holds ONE `Stage`, carrying BOTH children, used by
both `Left` and `Right`:

    class Stage(AssemblyNode):

        alpha = Alpha()
        beta = Beta()

        def render(self):
            # Alpha (dup_subassembly.step)
            self.alpha.translate((1.0, 0.0, 0.0))
            # Beta (dup_subassembly.step)
            self.beta.translate((2.0, 0.0, 0.0))

    class Left(AssemblyNode):
        stage = Stage()
        …
    class Right(AssemblyNode):
        stage = Stage()

Five assembly products (`Root`, `Left`, `Stage`, `Right`, `Stage`) produced
four classes, and the model holds four solids where the document has two.
`Occurrence.parent_name` being a name is the direct cause: the walk knows
which `Stage` it descended into, and throws that away.

---

## §4. A generated `render()` with no statement does not parse

`_placement_lines` always emits a comment first (the occurrence's name and
the document) and adds `# <attr> is placed at the identity` when neither a
rotation nor a translation is emitted. So `render_lines` in
`_assembly_class_source` is empty only for an assembly with NO child, and
the existing `render_lines if render_lines else ['        pass']` fallback
never fires for the case that occurs: every child at the identity.

Compiling the `assembly.py` generated for each existing `StepNode` fixture:

    duplicate_names      IndentationError: expected an indented block after
                         function definition on line 20 (at line 25)
    wrapped_single_part  IndentationError: expected an indented block after
                         function definition on line 20 (at line 22)
    single_product       IndentationError: expected an indented block after
                         function definition on line 20 (at line 22)
    two_products         IndentationError: expected an indented block after
                         function definition on line 21 (at line 25)
    nested_assembly      compiles OK
    repeated_product     compiles OK

The generated body reads (`evidence/generated/wrapped_single_part/assembly.py`):

    class M(AssemblyNode):

        solopart = SoloPart()

        def render(self):
            # SoloPart (wrapped_single_part.step)
            # solopart is placed at the identity

Three of the six generate an unparseable module, and the generated
`parts.py` compiles in every case — the defect is confined to `assembly.py`.
`tests/test_import_step.py`'s three faithfulness tests import the generated
module, and pass only because their three fixtures (`import_simple`,
`import_nested`, `import_repeated`) all carry non-identity placements; no
existing test compiles generated source for a document that does not.

---

## §5. Why the selector is name-relative, not the OCCT entry

`evidence/probe_stability.py` exports the `duplicate_names` model three
times: unchanged, with an unrelated `Bracket` appended after the two
sub-assemblies, and with the same `Bracket` inserted before them.

    -- original
       entry=0:1:1:1    name=Root       index-among-same-name=1 volume=9.000
       entry=0:1:1:2    name=Sub1       index-among-same-name=1 volume=1.000
       entry=0:1:1:3    name=Pin        index-among-same-name=1 volume=1.000
       entry=0:1:1:4    name=Sub2       index-among-same-name=1 volume=8.000
       entry=0:1:1:5    name=Pin        index-among-same-name=2 volume=8.000
    -- extra product appended last
       entry=0:1:1:3    name=Pin        index-among-same-name=1 volume=1.000
       entry=0:1:1:5    name=Pin        index-among-same-name=2 volume=8.000
       entry=0:1:1:6    name=Bracket    index-among-same-name=1 volume=343.000
    -- extra product inserted first
       entry=0:1:1:2    name=Bracket    index-among-same-name=1 volume=343.000
       entry=0:1:1:4    name=Pin        index-among-same-name=1 volume=1.000
       entry=0:1:1:5    name=Sub2       index-among-same-name=1 volume=8.000
       entry=0:1:1:6    name=Pin        index-among-same-name=2 volume=8.000
    -- original, read again (same process, cold cache)
       … identical to `-- original`

Both `Pin` entries moved when the unrelated product was inserted ahead of
them (`0:1:1:3 → 0:1:1:4`, `0:1:1:5 → 0:1:1:6`), while the name-relative
index kept naming the same 1.000 and 8.000 mm³ solids. `0:1:1:5` in the
re-export is `Sub2`, a sub-assembly — an `entry = '0:1:1:5'` selector would
have to be cross-checked against `part` to avoid selecting a different
product of a different name. The reading is deterministic across reads of
one file, so the entry remains the correct INTERNAL key.

---

## §6. Why the selector may not be spelled `index`

`evidence/probe_index_name.py` declares a `StepNode` carrying `index = 2`
and repeats it:

    TypeError: Bracket.bolts: cannot repeat Bolt, which already declares
    'index' (2). Each copy a repeat realizes carries its own 0-based
    position as the plain instance attribute 'index', and a declaration of
    that name on Bolt would win over it silently -- the framework's value
    would sit in the instance dict, unread. Rename Bolt's 'index', or
    declare the children individually or in a list instead of repeating
    them.

`solid_node/node/declarative.py`'s `_check_index` refuses it. A repeated
`StepNode` is the ordinary case (the step-assembly spec's fourteen-bolt
scenario), so `index` would make the two STEP features mutually exclusive.

---

## §7. Summary of what must change

| Measured defect | Where |
| --- | --- |
| Ambiguity refusal is terminal — no selector exists | `step.py` `_select`, `_ambiguity_error` |
| Product identity is computed and published nowhere | `ProductInfo`, `Occurrence` |
| `class_names` keyed on product name — later product wins | `import_step.py` `generate_parts` |
| Children resolved by product name — wrong class used | `_child_expression` |
| Assembly classes keyed on name — two products merge | `_ordered_assembly_names`, `occurrences_by_parent` |
| A `render()` of comments only does not parse | `_placement_lines`, `_assembly_class_source` |

## Reproducing

    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/select-a-step-product/evidence/probe_select.py
    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/select-a-step-product/evidence/probe_index_name.py
    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/select-a-step-product/evidence/probe_stability.py <scratch-dir>
    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/select-a-step-product/evidence/probe_dup_subassembly.py <scratch-dir>

(`.venv` is the workspace venv at
`/home/asa/devel/libresolid-studio/.venv`. `probe_select.py` and
`probe_dup_subassembly.py` write fixtures into the gitignored
`tests/step_project/` and into the scratch directory respectively.)
