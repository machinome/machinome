import json
import pytest

from machinome.model import Reference
from machinome.node.assembly import AssemblyNode
from machinome.node.leaf import LeafNode
from machinome.parameters import Count
from machinome.components import Standard
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Printed, Sourced
from machinome.production.errors import (
    DeclarationError,
    ProductionConflictError,
)


class Nut(LeafNode):
    def render(self):
        raise AssertionError("sourced reports must never render geometry")


class Submodel(AssemblyNode):
    count = Count(2)
    nuts = Nut().repeat(count)


class Root(AssemblyNode):
    left = Submodel(count=2)
    right = Submodel(count=3)


NUT = Standard("DIN 934", designation="M4x0.7")


class SubProduction(Production[Submodel]):
    arbitrary_name = Item(Submodel.nuts, Sourced(NUT))


class RootProduction(Production[Root]):
    left = SubProduction(Root.left)
    right = SubProduction(Root.right)


def test_actual_nested_quantities_and_sourced_laziness(tmp_path):
    model = Root()
    profile = RootProduction(model)
    assert profile.left.arbitrary_name.target_paths == (
        "left/nuts-0",
        "left/nuts-1",
    )
    assert profile.right.bom[0].quantity == 3
    assert profile.bom[0].quantity == 5
    assert profile.bom[0].requirement == NUT
    assert profile.mass.unknown_occurrences == profile.bom[0].occurrence_paths
    assert not profile.mass.complete
    assert not profile.findings
    exported = profile.export(tmp_path / "bundle")
    manifest = json.loads((exported.path / "production.json").read_text())
    assert manifest["draft"] is True
    assert manifest["executed_code_provenance"] == "unverified-direct-binding"
    assert manifest["bom"][0]["quantity"] == 5


def test_empty_profile_reports_every_unknown_candidate():
    class Empty(Production[Root]):
        pass

    profile = Empty(Root())
    assert len(profile.bom) == 5
    assert all(
        line.status == "unassigned" and line.quantity == 1
        for line in profile.bom
    )
    assert len(profile.mass.unknown_occurrences) == 5
    assert {f.code for f in profile.findings} == {"unassigned"}


def test_delegation_ownership_conflict_has_all_declarations():
    class Conflict(Production[Root]):
        child = SubProduction(Root.left)
        duplicate = Item(Reference(Root, ("left", "nuts")), Sourced(NUT))

    profile = Conflict(Root())
    overlap = [f for f in profile.findings if f.code == "overlap"]
    assert overlap
    assert overlap[0].declarations == ("child", "duplicate")
    with pytest.raises(ProductionConflictError):
        profile.bom


class Twice(Production[Submodel]):
    a = Item(Submodel.nuts, Sourced(NUT))
    b = Item(Submodel.nuts, Sourced(NUT))


def test_an_overlap_refuses_only_the_reports_of_its_scope(tmp_path):
    class OverlapInRight(Production[Root]):
        left = SubProduction(Root.left)
        right = Twice(Root.right)

    profile = OverlapInRight(Root())
    left = profile.left
    assert [(line.status, line.quantity) for line in left.bom] == [
        ("assigned", 2)
    ]
    assert left.stock == ()
    assert left.steps == ()
    assert not left.mass.complete
    assert left.findings == ()
    assert left.export(tmp_path / "left").coverage_complete
    overlaps = profile.findings
    assert [(f.code, f.occurrences) for f in overlaps] == [
        ("overlap", ("right/nuts-0",)),
        ("overlap", ("right/nuts-1",)),
        ("overlap", ("right/nuts-2",)),
    ]
    assert profile.right.findings == overlaps
    for read in (
        lambda: profile.right.bom,
        lambda: profile.bom,
        lambda: profile.mass,
    ):
        with pytest.raises(
            ProductionConflictError, match="right/a, right/b claim"
        ):
            read()
    with pytest.raises(ProductionConflictError):
        profile.export(tmp_path / "root")
    assert not (tmp_path / "root").exists()


def test_a_parent_reaching_into_one_child_leaves_its_sibling_readable():
    class Reach(Production[Root]):
        left = SubProduction(Root.left)
        right = SubProduction(Root.right)
        extra = Item(Reference(Root, ("left", "nuts")), Sourced(NUT))

    profile = Reach(Root())
    assert [line.quantity for line in profile.right.bom] == [3]
    for read in (lambda: profile.left.bom, lambda: profile.bom):
        with pytest.raises(ProductionConflictError, match="extra, left claim"):
            read()


def test_invalid_declarations_and_no_profile_inheritance():
    with pytest.raises(DeclarationError):

        class Bad(Production[Root]):
            x = Item(Submodel.nuts, Sourced(NUT))

    with pytest.raises(DeclarationError):

        class Inherited(RootProduction):
            pass


def test_bad_constructor_inputs_fail_immediately():
    from machinome.production.errors import BindingError

    for value in (7, "bad", object(), Nut(), Nut):
        with pytest.raises(BindingError):
            RootProduction(value)
    with pytest.raises(DeclarationError):
        Production[int]


def test_missing_model_source_is_refused_at_binding(tmp_path):
    from machinome.model import ModelInputChangedError
    from machinome.production.errors import ProductionExportError

    missing = tmp_path / "never-existed.txt"
    model = Root()
    model.left.nuts[0].files.add(str(missing))
    with pytest.raises(ProductionExportError) as refused:
        RootProduction(model)
    message = str(refused.value)
    assert "RootProduction cannot bind" in message
    assert "Nut 'nuts-0'" in message
    assert str(missing) in message
    assert not isinstance(refused.value, ModelInputChangedError)


def test_captured_profile_does_not_change_after_class_edit():
    class Captured(Production[Submodel]):
        first = Item(Submodel.nuts, Sourced(NUT))

    profile = Captured(Submodel())
    original = Captured._declarations
    try:
        Captured._declarations = {}
        assert profile.bom[0].requirement == NUT
    finally:
        Captured._declarations = original


def test_zero_repeat_is_not_absent_and_single_repeat_child_stays_tuple():
    assert SubProduction(Submodel(count=0)).bom == ()

    class Repeated(AssemblyNode):
        children_here = Submodel(count=1).repeat(1)

    class P(Production[Repeated]):
        children_here = SubProduction(Repeated.children_here)

    assert isinstance(P(Repeated()).children_here, tuple)


@pytest.mark.parametrize("count", [1, 2])
def test_tuple_binding_members_are_always_indexed(tmp_path, count):
    expected = [f"kids-{index}/arbitrary_name" for index in range(count)]

    class Holder(AssemblyNode):
        n = Count(count)
        kids = Submodel(count=1).repeat(n)

    class Repeated(Production[Holder]):
        kids = SubProduction(Holder.kids)

    repeated = Repeated(Holder())
    assert isinstance(repeated.kids, tuple)
    assert [
        kid.arbitrary_name.declaration_path for kid in repeated.kids
    ] == expected
    assert [line.declaration_paths for line in repeated.bom] == [
        tuple(expected)
    ]
    bundle = repeated.export(tmp_path / "bundle")
    manifest = json.loads((bundle.path / "production.json").read_text())
    assert [b["declaration_path"] for b in manifest["bindings"]] == [""] + [
        f"kids-{index}" for index in range(count)
    ]

    class Tupled(Production[Root]):
        kids = SubProduction(
            (Reference(Root, ("left",)), Reference(Root, ("right",)))[:count]
        )

    tupled = Tupled(Root())
    assert isinstance(tupled.kids, tuple)
    assert [
        kid.arbitrary_name.declaration_path for kid in tupled.kids
    ] == expected

    class Single(Production[Root]):
        kid = SubProduction(Root.left)

    single = Single(Root())
    assert single.kid.arbitrary_name.declaration_path == "kid/arbitrary_name"


def test_shared_consumed_artifact_invalidates_held_child_and_root_export(
    tmp_path,
):
    from tests.test_model_consumption import NativeBox
    from machinome.production.errors import ProductionInputChangedError

    class Model(AssemblyNode):
        box = NativeBox()

    class Child(Production[NativeBox]):
        box = Item(NativeBox, Printed())

    class P(Production[Model]):
        box = Child(Model.box)

    model = Model()
    model.box.basepath = str(tmp_path / "box")
    model.box.stl_file = str(tmp_path / "box.stl")
    production = P(model)
    child = production.box
    child.bom
    artifact = tmp_path / "box.stl"
    artifact.write_bytes(artifact.read_bytes())
    with pytest.raises(ProductionInputChangedError):
        child.mass
    with pytest.raises(ProductionInputChangedError):
        production.export(tmp_path / "never-published")
    assert not (tmp_path / "never-published").exists()


def test_manufactured_bom_mass_and_pinned_draft_bundle(tmp_path):
    from tests.production_project.model import Pair
    from tests.production_project.profile import Draft

    model = Pair()
    for name in ("first", "second"):
        node = getattr(model, name)
        node.basepath = str(tmp_path / name)
        node.stl_file = str(tmp_path / f"{name}.stl")
    profile = Draft(model)
    assert [line.status for line in profile.bom] == [
        "assigned",
        "assigned",
        "unassigned",
    ]
    assert profile.mass.known_grams == pytest.approx(3.524)
    assert profile.mass.unknown_occurrences == ("unknown",)
    assert not profile.mass.complete
    assert profile.mass.basis[0].basis == "homogeneous-solid"
    bundle = profile.export(tmp_path / "draft")
    manifest = json.loads((bundle.path / "production.json").read_text())
    assert len(manifest["artifacts"]) == 2
    assert not manifest["coverage_complete"]
    assert len(manifest["files"]) == 3
    import hashlib

    for artifact in manifest["artifacts"]:
        assert (
            hashlib.sha256(
                (bundle.path / artifact["file"]).read_bytes()
            ).hexdigest()
            == artifact["sha256"]
        )


def test_invalid_assembly_recipe_never_erases_descendant_mass():
    class Invalid(Production[Root]):
        invalid = Item(Root.left, Printed())

    profile = Invalid(Root())
    assert len(profile.mass.unknown_occurrences) == 5
    assert (
        sum(
            line.quantity
            for line in profile.bom
            if line.status == "unassigned"
        )
        == 5
    )
    assert profile.bom[0].status == "invalid"


def test_markdown_refusal_is_contextual_and_leaves_no_target(tmp_path):
    from machinome.production.profile import _markdown
    from machinome.production.errors import ProductionExportError

    for text in (
        "![x](local.png)",
        "[x][file]\n\n[file]: local.pdf",
        '<iframe src="local.html"></iframe>',
        "<ftp://remote.test/x>",
    ):
        with pytest.raises(ProductionExportError):
            _markdown(text, "declared/step", tmp_path / "instruction.md")


@pytest.mark.parametrize(
    "text",
    [
        "if a<b then c>d ok",
        "keep x<y and z>w",
        "5 < 6 > 4",
        'write `<img src="x.png">` to embed',
        "``a ` <script src=x> ` b``",
        '```html\n<img src="x.png">\n```\n',
        '~~~\n<link href="x.css">\n~~~',
        "press <kbd>Ctrl</kbd> and <br/> then <sub>2</sub>",
        '<div class="note">\nplain\n</div>',
        "`[x](local.png)`",
        "```\n[ref]: local.pdf\n```\n[x](https://example.com) and [y](#here)",
        "Plain *Markdown* with `code` and <https://example.com>.",
        "unclosed fence swallows the rest\n```\n<img src=x>",
        "> quoted `<img src=x.png>` code",
        "- item `<script src=x>` code",
    ],
)
def test_markdown_gate_accepts_what_is_not_a_dependency(tmp_path, text):
    from machinome.production.profile import _markdown

    assert (
        _markdown(text, "declared/step", tmp_path / "instruction.md") is None
    )


@pytest.mark.parametrize(
    "text",
    [
        '<img src="x.png">',
        '<a href="x.pdf">x</a>',
        '<a href="https://example.com">x</a>',
        '<link rel="stylesheet" href="x.css">',
        "<script>fetch('x')</script>",
        "<style>@import 'x.css';</style>",
        "<IMG SRC=x.png>",
        '<span style="background:url(x.png)">x</span>',
        '<svg><use xlink:href="x.svg#a"/></svg>',
        '<a title="x>y" href="z">z</a>',
        # A tag that starts before a backtick wins over the code span.
        '<img src="`x.png"> `',
        # An escaped backtick opens no code span.
        "\\` <img src=x.png> `",
        # A code span never crosses a blank line.
        "use ` here\n\n<img src=x.png>\n\nand ` there",
        # Inside an HTML block, backticks and fences are raw HTML.
        '<div>\n`<img src="x.png">`\n</div>',
        "<div>\n```\n<img src=x.png>\n```\n</div>",
        "<pre>\n\n`<img src=x.png>`\n</pre>",
        "<!--\n\n```\n-->\n<img src=x.png>",
        # An HTML block inside a block quote or a list item is raw HTML too.
        "> <div>\n> `<img src=x.png>`",
        "- <div>\n  `<img src=x.png>`",
        "1. <div>\n   ```\n   <img src=x.png>\n   ```",
        # A definition inside fenced code resolves no reference.
        "[x][ref]\n\n```\n[ref]: https://example.com\n```",
    ],
)
def test_markdown_gate_refuses_html_dependencies_outside_code(tmp_path, text):
    from machinome.production.profile import _markdown
    from machinome.production.errors import ProductionExportError

    with pytest.raises(ProductionExportError):
        _markdown(text, "declared/step", tmp_path / "instruction.md")


def test_an_inequality_in_a_step_is_read(tmp_path):
    text = "if a<b then c>d ok\n"
    module = _profile_module(
        tmp_path / "profile",
        "production_inequality",
        """
from tests.test_production import Submodel, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.instruction import Step, Markdown
class Profile(Production[Submodel]):
    nuts = Item(Submodel.nuts, Sourced(NUT))
    step = Step(nuts, instructions=Markdown('assembly.md'))
""",
        {"assembly.md": text},
    )
    profile = module.Profile(Submodel())
    assert profile.steps[0].instruction_text == text
    bundle = profile.export(tmp_path / "bundle")
    assert text in (bundle.path / "instructions.md").read_text()


def _profile_module(directory, name, source, files=None):
    import importlib.util
    import sys

    directory.mkdir(parents=True, exist_ok=True)
    for filename, content in (files or {}).items():
        (directory / filename).write_text(content)
    path = directory / f"{name}.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_child_export_file_set_is_independent_of_prior_root_reads(tmp_path):
    _profile_module(
        tmp_path / "child",
        "production_child_files",
        """
from tests.test_production import Submodel, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.instruction import Step, Markdown
class Child(Production[Submodel]):
    nuts = Item(Submodel.nuts, Sourced(NUT))
    assembly = Step(nuts, instructions=Markdown('assembly.md'))
""",
        {"assembly.md": "Child-only instruction."},
    )
    parent_module = _profile_module(
        tmp_path / "parent",
        "production_parent_files",
        """
from tests.test_production import Root
from production_child_files import Child
from machinome.production.profile import Production
from machinome.production.instruction import Step, Markdown
class Parent(Production[Root]):
    left = Child(Root.left)
    right = Child(Root.right)
    assembly = Step(left, right, instructions=Markdown('assembly.md'))
""",
        {"assembly.md": "Parent-only instruction."},
    )
    first, second = parent_module.Parent(Root()), parent_module.Parent(Root())
    first.steps
    a = first.left.export(tmp_path / "a")
    b = second.left.export(tmp_path / "b")
    manifests = [
        json.loads((result.path / "production.json").read_text())
        for result in (a, b)
    ]
    assert manifests[0]["files"] == manifests[1]["files"]
    assert len(manifests[0]["files"]) == 1
    assert list(manifests[0]["files"])[0].endswith("child/assembly.md")
    root = first.export(tmp_path / "root")
    manifest = json.loads((root.path / "production.json").read_text())
    assert len(manifest["files"]) == 2
    assert [s["scope_path"] for s in manifest["steps"]] == [
        "left",
        "right",
        ".",
    ]


def test_absent_child_findings_are_scoped():
    class Child(Production[Submodel]):
        missing = Item(Reference(Submodel, ("absent",)), Sourced(NUT))

    class Parent(Production[Root]):
        left = Child(Root.left)
        right = SubProduction(Root.right)

    profile = Parent(Root())
    assert any(f.code == "absent-target" for f in profile.left.findings)
    assert not any(f.code == "absent-target" for f in profile.right.findings)


def test_empty_assembly_delegation_is_an_ownership_boundary():
    class Empty(AssemblyNode):
        def render(self):
            return []

    class Model(AssemblyNode):
        empty = Empty()

    class Child(Production[Empty]):
        pass

    class Parent(Production[Model]):
        delegated = Child(Model.empty)
        bought = Item(Model.empty, Sourced(NUT))

    profile = Parent(Model())
    assert any(f.code == "overlap" for f in profile.findings)
    with pytest.raises(ProductionConflictError):
        profile.mass


def test_manufacturing_groups_include_direct_step_content_and_material(
    tmp_path,
):
    from tests.production_project.model import Pair

    module = _profile_module(
        tmp_path / "profiles",
        "production_grouping",
        """
from tests.production_project.model import Pair
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Printed
from machinome.production.instruction import Step, Markdown
from machinome.production.material import Material
class Same(Production[Pair]):
    a = Item(Pair.first, Printed())
    b = Item(Pair.second, Printed())
class Finish(Production[Pair]):
    a = Item(Pair.first, Printed())
    b = Item(Pair.second, Printed())
    finish = Step(a, instructions=Markdown('finish.md'))
class Materials(Production[Pair]):
    a = Item(Pair.first, Printed(Material('a')))
    b = Item(Pair.second, Printed(Material('b')))
""",
        {"finish.md": "Finishing changes manufacturing identity."},
    )
    model = Pair()
    for name in ("first", "second"):
        node = getattr(model, name)
        node.basepath = str(tmp_path / name)
        node.stl_file = str(tmp_path / f"{name}.stl")
    same = module.Same(model)
    assert [
        line.quantity for line in same.bom if line.status == "assigned"
    ] == [2]
    finish = module.Finish(model)
    assert [
        line.quantity for line in finish.bom if line.status == "assigned"
    ] == [1, 1]
    materials = module.Materials(model)
    materials.mass
    assert [
        line.quantity for line in materials.bom if line.status == "assigned"
    ] == [
        1,
        1,
    ]


@pytest.mark.parametrize(
    "text",
    [
        "![x](local.png)",
        "[x](../outside.md)",
        "[x][ref]\n\n[ref]: local.pdf",
        "[x][missing]",
        '<video src="x"></video>',
        '<object data="x"></object>',
        '<script src="x"></script>',
        "<mailto:x@example.com>",
    ],
)
def test_requested_steps_and_export_refuse_unsupported_dependencies(
    tmp_path, text
):
    from machinome.production.errors import ProductionExportError

    module = _profile_module(
        tmp_path / "profile",
        "production_bad_markdown",
        """
from tests.test_production import Submodel, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.instruction import Step, Markdown
class Profile(Production[Submodel]):
    nuts = Item(Submodel.nuts, Sourced(NUT))
    step = Step(nuts, instructions=Markdown('assembly.md'))
""",
        {"assembly.md": text},
    )
    profile = module.Profile(Submodel())
    # Sourced grouping requires no finishing files or geometry.
    assert profile.bom[0].quantity == 2
    with pytest.raises(ProductionExportError, match="step"):
        profile.steps
    with pytest.raises(ProductionExportError):
        profile.export(tmp_path / "refused")
    assert not (tmp_path / "refused").exists()


def test_source_instruction_and_symlink_changes_invalidate_binding(tmp_path):
    from machinome.production.errors import (
        ProductionInputChangedError,
        ProductionExportError,
    )

    source = """
from tests.test_production import Submodel, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.instruction import Step, Markdown
class Profile(Production[Submodel]):
    nuts = Item(Submodel.nuts, Sourced(NUT))
    step = Step(nuts, instructions=Markdown('assembly.md'))
"""
    module = _profile_module(
        tmp_path / "profile",
        "production_change",
        source,
        {"assembly.md": "Original."},
    )
    profile = module.Profile(Submodel())
    profile.steps
    (tmp_path / "profile" / "assembly.md").write_text("Replaced.")
    with pytest.raises(ProductionInputChangedError):
        profile.bom
    outside = tmp_path / "outside.md"
    outside.write_text("Outside.")
    instruction = tmp_path / "profile" / "assembly.md"
    instruction.unlink()
    instruction.symlink_to(outside)
    with pytest.raises(ProductionExportError, match="escapes"):
        module.Profile(Submodel())


def test_sourced_assembly_replaces_descendant_weight(tmp_path):
    module = _profile_module(
        tmp_path / "profile",
        "production_bought_assembly",
        """
from tests.test_production import Root, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.mass import MeasuredMass
class Profile(Production[Root]):
    left = Item(Root.left, Sourced(NUT),
                mass=MeasuredMass(8, evidence='measurement.md'))
""",
        {"measurement.md": "Illustrative measured assembly."},
    )
    profile = module.Profile(Root())
    assert profile.mass.known_grams == 8
    assert profile.mass.unknown_occurrences == (
        "right/nuts-0",
        "right/nuts-1",
        "right/nuts-2",
    )
    assert len(profile.mass.basis) == 4


def test_export_refuses_nonempty_destination(tmp_path):
    from machinome.production.errors import ProductionExportError

    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep").write_text("user file")
    with pytest.raises(ProductionExportError):
        RootProduction(Root()).export(target)
    assert (target / "keep").read_text() == "user file"


def test_representative_exact_cut_stock_and_lazy_nominal_dxf(tmp_path):
    from tests.sheet_project.frame_panel import FramePanel
    from machinome.production.process import Cut
    from machinome.production.material import Material
    from machinome.production.stock import Sheet

    class Panels(AssemblyNode):
        panels = FramePanel().repeat(4)

    stock = Sheet(Material("MDF", density_kg_m3=700), thickness_mm=6)

    class Profile(Production[Panels]):
        panels = Item(Panels.panels, Cut(stock))

    model = Panels()
    for index, panel in enumerate(model.panels):
        panel.basepath = str(tmp_path / f"panel-{index}")
        panel.stl_file = panel.basepath + ".stl"
        panel.brep_file = panel.basepath + ".brep"
        panel.dxf_file = panel.basepath + ".dxf"
    profile = Profile(model)
    assert profile.stock[0].finished_count == 4
    assert profile.stock[0].purchased_quantity is None
    assert not list(tmp_path.glob("*.dxf"))
    assert not profile.findings
    bundle = profile.export(tmp_path / "cut")
    manifest = json.loads((bundle.path / "production.json").read_text())
    assert manifest["artifacts"][0]["kind"] == "dxf"
    assert (bundle.path / manifest["artifacts"][0]["file"]).exists()
    assert manifest["stock"][0]["finished_count"] == 4
    assert manifest["stock"][0]["purchased_quantity"] is None


def test_profile_fields_cannot_hide_output_or_lifecycle_members():
    with pytest.raises(DeclarationError, match="bom"):

        class Bad(Production[Submodel]):
            bom = Item(Submodel.nuts, Sourced(NUT))


def test_imported_step_and_mass_evidence_keep_their_declaring_module(tmp_path):
    _profile_module(
        tmp_path / "records",
        "production_imported_records",
        """
from tests.test_production import Submodel, NUT
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.mass import MeasuredMass
from machinome.production.instruction import Step, Markdown
item = Item(Submodel.nuts, Sourced(NUT),
            mass=MeasuredMass(2, evidence='mass.md'))
step = Step(item, instructions=Markdown('assembly.md'))
""",
        {
            "assembly.md": "Instructions in record defining module.",
            "mass.md": "Measured mass evidence.",
        },
    )
    module = _profile_module(
        tmp_path / "profile",
        "production_imported_profile",
        """
from tests.test_production import Submodel
from machinome.production.profile import Production
from production_imported_records import item, step
class Profile(Production[Submodel]):
    nuts = item
    finish = step
""",
    )
    profile = module.Profile(Submodel())
    assert (
        profile.steps[0].instruction_path
        == tmp_path / "records" / "assembly.md"
    )
    assert profile.mass.known_grams == 4
    assert (
        profile.mass.basis[0].evidence_path == tmp_path / "records" / "mass.md"
    )


@pytest.mark.parametrize(
    "density, large, expected",
    [(1e308, False, 2.4e303), (1e-320, False, None), (1e308, True, None)],
)
def test_solid_mass_scales_before_overflow_and_refuses_underflow(
    density, large, expected
):
    from tests.test_model_consumption import NativeBox
    from machinome.production.material import Material
    from machinome.production.mass import SolidMass

    class LargeBox(NativeBox):
        def render(self):
            import trimesh

            return trimesh.creation.box(extents=(1000, 1000, 1000))

    model_type = LargeBox if large else NativeBox

    class Profile(Production[model_type]):
        piece = Item(
            model_type,
            Printed(Material("numeric fixture", density_kg_m3=density)),
            mass=SolidMass(),
        )

    result = Profile(model_type()).mass
    basis = result.basis[0]
    if expected is None:
        assert basis.grams is None
        assert basis.reason == "finite positive solid mass unavailable"
        assert not result.complete
        assert result.unknown_occurrences == (".",)
    else:
        assert basis.grams == pytest.approx(expected)
        assert result.known_grams == pytest.approx(expected)
        assert result.complete


def test_mass_subtotal_overflow_refuses_contextually(tmp_path):
    from machinome.production.errors import ProductionExportError

    module = _profile_module(
        tmp_path / "profile",
        "production_mass_overflow",
        """
from tests.test_production import Submodel, NUT
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.mass import MeasuredMass
class Profile(Production[Submodel]):
    nuts = Item(Submodel.nuts, Sourced(NUT),
                mass=MeasuredMass(1e308, evidence='mass.md'))
""",
        {"mass.md": "Numeric regression fixture, not physical evidence."},
    )
    with pytest.raises(OverflowError, match="mass subtotal.*finite"):
        module.Profile(Submodel()).mass
    destination = tmp_path / "overflow-bundle"
    with pytest.raises(
        ProductionExportError, match="mass subtotal.*finite"
    ) as caught:
        module.Profile(Submodel()).export(destination)
    assert isinstance(caught.value.__cause__, OverflowError)
    assert not destination.exists()
    assert not tuple(tmp_path.glob(".overflow-bundle.*"))
