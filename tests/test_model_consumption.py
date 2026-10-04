import pytest

from machinome.node.assembly import AssemblyNode
from machinome.node.leaf import LeafNode
from machinome.node.fusion import FusionNode
from machinome.node.flexible import FlexibleNode
from machinome.parameters import Count
from machinome.model import ModelSnapshot, Reference
from tests.test_source_generation import ScratchLoadProject


class Part(LeafNode):
    def render(self):
        raise AssertionError("structural reads never render leaves")


class Compound(FusionNode):
    a = Part()
    b = Part()


class Wire(FlexibleNode):
    def render(self):
        raise AssertionError("structural reads never deform wires")


class Machine(AssemblyNode):
    count = Count(2)
    pieces = Part().repeat(count)
    compound = Compound()
    wire = Wire()
    omitted = Part()

    def render(self):
        self.omitted.omit()

    def simulate(self):
        raise AssertionError("structural reads never simulate")


def test_actual_structure_and_piece_boundaries():
    model = Machine(count=3)
    snapshot = ModelSnapshot(model)
    assert [o.path for o in snapshot.select(Machine.pieces)] == [
        "pieces-0",
        "pieces-1",
        "pieces-2",
    ]
    assert snapshot.select(Reference(Machine, ("omitted",))) == ()
    assert snapshot.select(Reference(Machine, ("pieces",))) == snapshot.select(
        Machine.pieces
    )
    kinds = {o.path: o.kind for o in snapshot.occurrences}
    assert kinds["compound"] == "rigid-piece"
    assert kinds["compound/a"] == "rigid-feature"
    assert kinds["wire"] == "flexible-piece"
    assert snapshot.select(Machine.pieces) == snapshot.select(Machine.pieces)
    with pytest.raises(TypeError):
        snapshot.occurrences[0].parameters["count"] = 9


def test_selection_shape_distinguishes_absence_from_empty_repetition():
    empty = ModelSnapshot(Machine(count=0))
    assert empty.empty_selection(Machine.pieces)
    assert empty.selection_is_many(Machine.pieces)
    assert not empty.empty_selection(Machine.omitted)
    assert not empty.selection_is_many(Machine.omitted)
    one = ModelSnapshot(Machine(count=1))
    assert not one.empty_selection(Machine.pieces)
    assert one.selection_is_many(Machine.pieces)
    assert not one.selection_is_many(Machine.compound)


def test_inherited_field_reference_reads_actual_replacement():
    class Base(AssemblyNode):
        part = Part()

    class Replacement(Part):
        pass

    class Derived(Base):
        part = Replacement()

    model = Derived()
    snapshot = ModelSnapshot(model)
    assert snapshot.select(Base.part) == snapshot.select(Derived.part)
    assert snapshot.select(Base.part)[0].model_type is Replacement


def test_zero_repeat_and_legacy_constructor_children():
    class Legacy(AssemblyNode):
        def __init__(self):
            super().__init__()
            self.real = Part()

        def render(self):
            return [self.real]

    model = Legacy()
    snap = ModelSnapshot(model)
    assert snap.select(Reference(Legacy, ("real",)))[0].path == "real"
    assert model.real is snap._node(snap.occurrences[1])
    assert ModelSnapshot(Machine(count=0)).select(Machine.pieces) == ()


def test_malformed_rest_is_refused():
    class Bad(AssemblyNode):
        def render(self):
            return "bad"

    with pytest.raises(ValueError, match="list"):
        ModelSnapshot(Bad()).occurrences


def test_failed_legacy_read_restores_preceding_placements():
    from machinome.simulation import Driver

    class Bad(AssemblyNode):
        angle = Driver(default=0)
        part = Part()

        def render(self):
            self.part.translate([1, 2, 3])
            self.part.rotate(self.angle, [0, 0, 1])

    model = Bad()
    model.user_data = {"held": []}
    held_user_data = model.user_data
    held_children = model.children
    held_operations = model.part.operations
    before = list(model.part.operations)
    snap = ModelSnapshot(model)
    for _ in range(2):
        with pytest.raises(ValueError, match="structure-only"):
            snap.occurrences
        assert model.part.operations == before
        assert model.part.operations is held_operations
        assert model.children is held_children
        assert model.user_data is held_user_data
        assert "_rest" not in vars(model)


def test_public_reference_recognition():
    from machinome.model import is_reference

    assert is_reference(Machine)
    assert is_reference(Machine.pieces)
    assert is_reference(Machine.compound.a)
    assert is_reference(Reference(Machine, ("compound", "a")))
    assert not is_reference(12)
    assert not is_reference("compound")
    assert not is_reference(str)


def test_advanced_binding_preserves_drivers_and_operations():
    from tests.test_simulate_split import Arm, serialized

    model = Arm()
    model.set_state(angle=57)
    before = serialized(model.box)
    value = model.angle
    snap = ModelSnapshot(model)
    assert snap.occurrences is snap.occurrences
    assert model.angle == value
    assert serialized(model.box) == before


def test_advanced_running_bank_and_motion_remain_identical(monkeypatch):
    from machinome.simulation import Sim
    from tests.running_project.machine import Train
    from tests.test_simulate_split import serialized

    model = Train()
    sim = Sim(model, 0.1, state={"crank": 17})
    sim.rate("crank", 90)
    sim.run(0.3)
    before = sim.snapshot()
    motions = {
        name: serialized(getattr(model, name))
        for name in ("first", "second", "slide", "wheel")
    }
    monkeypatch.setattr(
        model, "simulate", lambda: pytest.fail("no simulation read")
    )
    snapshot = ModelSnapshot(model)
    snapshot.occurrences
    snapshot.select(Train.first)
    assert sim.snapshot() == before
    assert {
        name: serialized(getattr(model, name)) for name in motions
    } == motions


def test_actual_legacy_constructor_parameters():
    class Legacy(AssemblyNode):
        def __init__(self, width=2, *, enabled=True):
            self.width = width
            self.enabled = enabled
            super().__init__()
            self.part = Part()

        def render(self):
            return [self.part]

    snap = ModelSnapshot(Legacy(9, enabled=False))
    assert snap.occurrences[0].parameters == {"width": 9, "enabled": False}


def test_scoped_reference_cannot_escape_through_external_alias():
    class Child(AssemblyNode):
        part = Part()

    class Root(AssemblyNode):
        child = Child()
        outside = Part()

    model = Root()
    model.child.alias = model.outside
    snap = ModelSnapshot(model)
    child = snap.select(Root.child)[0]
    assert snap.select(Reference(Child, ("alias",)), scope=child) == ()


def test_source_replacement_invalidates_every_access(tmp_path):
    from machinome.model import ModelInputChangedError

    source = tmp_path / "input.txt"
    source.write_text("aaa")
    model = Machine()
    model.files.add(str(source))
    snap = ModelSnapshot(model)
    snap.occurrences
    stamp = source.stat().st_mtime_ns
    source.write_text("bbb")
    import os

    os.utime(source, ns=(stamp, stamp))
    with pytest.raises(ModelInputChangedError, match="input changed"):
        snap.select(Machine.pieces)
    with pytest.raises(ModelInputChangedError):
        snap.observe_input(source)


class NativeBox(LeafNode):
    renders = 0

    def render(self):
        import trimesh

        type(self).renders += 1
        return trimesh.creation.box(extents=(2, 3, 4))

    def materialize(self, rendered):
        self.publish_artifact(
            self.stl_file, lambda path: rendered.export(path, file_type="stl")
        )

    def present(self, rendered):
        raise AssertionError("native consumption never presents SCAD")

    def _build_markings(self):
        raise AssertionError("production never builds markings")


def test_geometry_copy_is_exact_and_same_instance_reuses_native_currency(
    tmp_path,
):
    import hashlib

    node = NativeBox()
    node.basepath = str(tmp_path / "box")
    node.stl_file = str(tmp_path / "box.stl")
    initial = NativeBox.renders
    snapshot = ModelSnapshot(node)
    occurrence = snapshot.occurrences[0]
    facts = snapshot.geometry(occurrence)
    destination = tmp_path / "copied.stl"
    assert (
        snapshot.copy_artifact(occurrence, "stl", destination)
        == facts.artifact_sha256
    )
    assert (
        hashlib.sha256(destination.read_bytes()).hexdigest()
        == facts.artifact_sha256
    )
    assert facts.volume_mm3 == pytest.approx(24)
    other = ModelSnapshot(node)
    assert other.geometry(other.occurrences[0]) == facts
    assert NativeBox.renders == initial + 1


def test_consumed_artifact_replacement_invalidates_shared_snapshot(tmp_path):
    import os
    from machinome.model import ModelInputChangedError

    node = NativeBox()
    artifact = tmp_path / "box.stl"
    node.basepath = str(tmp_path / "box")
    node.stl_file = str(artifact)
    snapshot = ModelSnapshot(node)
    occurrence = snapshot.occurrences[0]
    snapshot.geometry(occurrence)
    original = artifact.read_bytes()
    stamp = artifact.stat().st_mtime_ns
    artifact.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    os.utime(artifact, ns=(stamp, stamp))
    with pytest.raises(
        ModelInputChangedError, match="consumed artifact changed"
    ):
        snapshot.copy_artifact(occurrence, "stl", tmp_path / "copy.stl")
    with pytest.raises(ModelInputChangedError):
        snapshot.occurrences


def test_rigid_rest_placements_reused_by_normal_lifecycle():
    class Positioned(FusionNode):
        a = Part()

        def render(self):
            self.a.translate([1, 2, 3])

    model = Positioned()
    snapshot = ModelSnapshot(model)
    snapshot.occurrences
    before = list(model.a.operations)
    assert tuple(model.render()) == (model.a,)
    assert model.a.operations == before


def test_artifact_read_race_poisoning_is_contextual(tmp_path, monkeypatch):
    from machinome._artifact import ArtifactSnapshot
    from machinome.model import ModelInputChangedError
    from pathlib import Path

    node = NativeBox()
    node.basepath = str(tmp_path / "box")
    node.stl_file = str(tmp_path / "box.stl")
    snap = ModelSnapshot(node)
    occurrence = snap.occurrences[0]
    original = ArtifactSnapshot.read_bytes

    def replacing(opened):
        if opened.path == node.stl_file:
            path = Path(opened.path)
            path.write_bytes(path.read_bytes())
        return original(opened)

    monkeypatch.setattr(ArtifactSnapshot, "read_bytes", replacing)
    with pytest.raises(
        ModelInputChangedError, match="artifact consumption failed"
    ):
        snap.geometry(occurrence)
    with pytest.raises(ModelInputChangedError):
        snap.select(NativeBox)


class VerifiedModelGenerationTest(ScratchLoadProject):
    def test_verified_loader_carries_executed_generation_and_closure(self):
        from machinome.model import ModelInputChangedError
        import os

        node = self.load_generation()
        snapshot = ModelSnapshot(node)
        assert (
            snapshot.executed_code_provenance == "verified-source-generation"
        )
        assert os.path.abspath(self.dimensions) in snapshot.input_hashes
        self.write("dimensions.py", "VALUE = 2\n")
        with self.assertRaises(ModelInputChangedError):
            snapshot.occurrences

    def test_changed_executed_source_cannot_be_bound_as_verified(self):
        from machinome.model import ModelInputChangedError

        node = self.load_generation()
        self.write("dimensions.py", "VALUE = 2\n")
        with self.assertRaises(ModelInputChangedError):
            ModelSnapshot(node)
