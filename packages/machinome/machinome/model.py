"""Read actual model occurrences and pinned rigid artifacts on demand."""

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping
import errno
import hashlib
import inspect
from contextlib import contextmanager, nullcontext


class ModelInputChangedError(RuntimeError):
    """A bound source or consumed artifact changed; bind a fresh model."""


@dataclass(frozen=True)
class Reference:
    model_type: type
    path: tuple[str, ...]

    def __post_init__(self):
        if not isinstance(self.model_type, type):
            raise TypeError("Reference model_type must be a model class")
        if not isinstance(self.path, tuple) or any(
            not isinstance(p, str) or not p.isidentifier() or p.startswith("_")
            for p in self.path
        ):
            raise ValueError(
                "Reference path must be a tuple of public attributes"
            )


@dataclass(frozen=True)
class Occurrence:
    path: str
    parent_path: str | None
    kind: str
    model_type: type
    parameters: Mapping
    source_paths: tuple[Path, ...]
    sheet_thickness_mm: float | None = None
    nominal_dxf: bool = False


@dataclass(frozen=True)
class GeometryFacts:
    content_id: str
    size_mm: tuple[float, float, float] | None
    volume_mm3: float | None
    watertight: bool
    artifact_kind: str
    artifact_sha256: str


def _observe(path):
    from machinome._artifact import ArtifactSnapshot

    with ArtifactSnapshot(path) as opened:
        return (
            opened.observation,
            hashlib.sha256(opened.read_bytes()).hexdigest(),
        )


def reference_path(model_type, target):
    """Adapt a child declaration or explicit reference to attribute paths."""
    from machinome.node.declarative import (
        ChildDeclaration,
        RepeatDeclaration,
        declared_children,
    )
    from machinome.motion.couplings import PathRef

    if isinstance(target, Reference):
        if not issubclass(model_type, target.model_type):
            raise ValueError("reference belongs to a foreign model")
        return target.path
    if isinstance(target, type):
        if not issubclass(model_type, target):
            raise ValueError("root target belongs to a foreign model")
        return ()
    segments = ()
    root = target
    if isinstance(target, PathRef):
        root, segments = target.root, target.segments
    if isinstance(root, (ChildDeclaration, RepeatDeclaration)):
        # An ancestor's field reference keeps addressing that field after a
        # subclass replaces its declaration; selection reads the actual value.
        for owner in model_type.__mro__:
            for name, declaration in declared_children(owner).items():
                if declaration is root:
                    return (name,) + segments
    raise ValueError("target is not a child reference of this model")


def is_reference(target):
    """Recognize supported model selectors without constructing any model."""
    from machinome.node.base import AbstractBaseNode
    from machinome.node.declarative import ChildDeclaration, RepeatDeclaration
    from machinome.motion.couplings import PathRef

    if isinstance(target, Reference):
        return True
    if isinstance(target, type):
        return issubclass(target, AbstractBaseNode)
    if isinstance(target, PathRef):
        target = target.root
    return isinstance(target, (ChildDeclaration, RepeatDeclaration))


class ModelSnapshot:
    """Lazy rest topology and immutable facts for one supplied model instance.

    Structural reading never simulates. Rigid geometry is materialized only
    by geometry/copy_artifact. Direct instances retain explicitly unverified
    executed-code provenance; observed input bytes are guarded from binding.
    """

    def __init__(self, model):
        from machinome.node.base import AbstractBaseNode

        if not isinstance(model, AbstractBaseNode):
            raise TypeError("ModelSnapshot requires an existing node instance")
        self._model = model
        self._generation = model.__dict__.get("_source_generation")
        self.executed_code_provenance = (
            "verified-source-generation"
            if self._generation is not None
            else "unverified-direct-binding"
        )
        self._inputs = {}
        self._artifacts = {}
        self._nodes = {}
        self._by_identity = {}
        self._occurrences = None
        self._invalid = None
        if self._generation is not None:
            self.validate()
            for observation in self._generation.observations:
                self.observe_input(observation.path)
        self._capture_existing(model, set())
        self.validate()

    def _capture_existing(self, node, seen):
        from machinome.node.base import AbstractBaseNode

        if id(node) in seen:
            return
        seen.add(id(node))
        for path in self._sources(node):
            if path not in self._inputs and not path.exists():
                raise FileNotFoundError(
                    errno.ENOENT,
                    f"{type(node).__name__} '{node.name}' names an input "
                    f"file that does not exist",
                    str(path),
                )
            self.observe_input(path)
        for value in vars(node).values():
            members = value if isinstance(value, (list, tuple)) else (value,)
            for member in members:
                if isinstance(member, AbstractBaseNode):
                    self._capture_existing(member, seen)

    def _existing_nodes(self):
        """Known children, without invoking properties or rendering."""
        from machinome.node.base import AbstractBaseNode

        found = {}

        def visit(node):
            if id(node) in found:
                return
            found[id(node)] = node
            for value in vars(node).values():
                for member in (
                    value if isinstance(value, (list, tuple)) else (value,)
                ):
                    if isinstance(member, AbstractBaseNode):
                        visit(member)

        visit(self._model)
        return tuple(found.values())

    @staticmethod
    def _parameters(node):
        values = node.__dict__.get("_parameters")
        if values is not None:
            return MappingProxyType(dict(values))
        # Legacy authors retain their resolved constructor values as public
        # attributes. Read those values, never infer a default or reconstruct.
        values = {}
        for name in inspect.signature(type(node).__init__).parameters:
            value = node.__dict__.get(name)
            if (
                name != "self"
                and not name.startswith("_")
                and type(value) in (int, float, bool)
            ):
                values[name] = value
        return MappingProxyType(values)

    def _sources(self, node):
        paths = set(node.files)
        for klass in type(node).__mro__:
            try:
                paths.add(inspect.getfile(klass))
            except (TypeError, OSError):
                pass
        return tuple(sorted((Path(p).absolute() for p in paths), key=str))

    def observe_input(self, path):
        """Pin a consumer's source or evidence into this shared generation."""
        path = Path(path).absolute()
        if self._invalid:
            raise ModelInputChangedError(self._invalid)
        try:
            if path in self._inputs:
                from machinome._artifact import observe_artifact

                expected = self._inputs[path]
                if observe_artifact(path) != expected[0]:
                    self._fail(f"input changed: {path}")
                return expected[1]
            observed = _observe(path)
        except ModelInputChangedError:
            raise
        except Exception as error:
            self._fail(f"input observation failed: {path}: {error}")
        expected = self._inputs.setdefault(path, observed)
        if expected != observed:
            self._fail(f"input changed: {path}")
        return observed[1]

    @property
    def input_hashes(self):
        self.validate()
        return MappingProxyType(
            {str(p): digest for p, (_, digest) in self._inputs.items()}
        )

    def _fail(self, message):
        self._invalid = message
        raise ModelInputChangedError(message)

    def validate(self):
        """Refuse changes to inputs, including consumed geometry."""
        if self._invalid:
            raise ModelInputChangedError(self._invalid)
        try:
            if self._generation is not None:
                self._generation.checkpoint("production model read")
            from machinome._artifact import observe_artifact

            for path, expected in self._inputs.items():
                if observe_artifact(path) != expected[0]:
                    self._fail(f"input changed: {path}")
            for path, (observation, _, _) in self._artifacts.items():
                if observe_artifact(path) != observation:
                    self._fail(f"consumed artifact changed: {path}")
        except ModelInputChangedError:
            raise
        except Exception as error:
            self._fail(f"input validation failed: {error}")

    @contextmanager
    def _source_phase(self, paths=(), *, label):
        """Re-enter the verified importer for lazily discovered producers."""
        if self._generation is None:
            yield
            return
        from machinome.source_generation import (
            current_generation,
            current_phase,
            SourceChanged,
        )

        active = current_generation()
        if active is not None and active is not self._generation:
            self._fail(
                "model read belongs to a different active source generation"
            )
        generation = self._generation if active is None else nullcontext()
        phase = (
            self._generation.phase(paths, label=label)
            if current_phase() is None
            else nullcontext()
        )
        try:
            with generation, phase:
                yield
            for observation in self._generation.observations:
                self.observe_input(observation.path)
        except SourceChanged as error:
            self._fail(str(error))

    @property
    def occurrences(self):
        self.validate()
        if self._occurrences is None:
            from machinome.node.internal import InternalNode
            from machinome.node.assembly import AssemblyNode, _rest_children
            from machinome.node.sheet_leaf import SheetLeafNode

            found = []
            # Refusal must not leave a half-rendered legacy tree with new
            # placements, omitted marks or cached rest children.
            missing = object()
            cache_keys = (
                "_rest",
                "_legacy_render",
                "_production_rest",
                "_omitted_record",
                "_rendering",
                "_omitted",
            )
            saved = [
                (
                    node,
                    node.operations,
                    tuple(node.operations),
                    {key: vars(node).get(key, missing) for key in cache_keys},
                )
                for node in self._existing_nodes()
            ]

            def walk(node, path, parent, rigid_inside):
                if id(node) in self._by_identity or path in self._nodes:
                    raise ValueError(
                        f"duplicate model instance or occurrence path: {path}"
                    )
                self._nodes[path] = node
                kind = (
                    ("rigid-feature" if rigid_inside else "rigid-piece")
                    if node.rigid
                    else ("flexible-piece" if node.flexible else "assembly")
                )
                sources = self._sources(node)
                for source in sources:
                    self.observe_input(source)
                occurrence = Occurrence(
                    path,
                    parent,
                    kind,
                    type(node),
                    self._parameters(node),
                    sources,
                    (
                        float(node.thickness)
                        if isinstance(node, SheetLeafNode)
                        else None
                    ),
                    isinstance(node, SheetLeafNode),
                )
                self._by_identity[id(node)] = occurrence
                found.append(occurrence)
                if isinstance(node, InternalNode):
                    if isinstance(node, AssemblyNode):
                        children = _rest_children(node, structure_only=True)
                    else:
                        if "_production_rest" not in node.__dict__:
                            # Preparation already ran this instance's render
                            # and positioned its children; running it again
                            # would apply every placement a second time.
                            children = node.__dict__.get("_prepared_rendered")
                            if children is None:
                                from machinome.node import phase

                                token = phase._structure_only.set(True)
                                try:
                                    children = node.render()
                                finally:
                                    phase._structure_only.reset(token)
                            node.validate(children)
                            node.__dict__["_production_rest"] = tuple(children)
                        children = node.__dict__["_production_rest"]
                        node._link_children(children)
                    for child in children:
                        child_path = (
                            child.name
                            if path == "."
                            else f"{path}/{child.name}"
                        )
                        walk(
                            child, child_path, path, rigid_inside or node.rigid
                        )

            try:
                with self._source_phase(label="model structure"):
                    walk(self._model, ".", None, False)
                self.validate()
            except Exception as error:
                for node, operations, previous, caches in saved:
                    # Preserve held operation lists and runtime/user objects.
                    # Only framework placements and rest bookkeeping are ours.
                    operations[:] = previous
                    for key, value in caches.items():
                        if value is missing:
                            node.__dict__.pop(key, None)
                        else:
                            node.__dict__[key] = value
                self._nodes.clear()
                self._by_identity.clear()
                if isinstance(error, ModelInputChangedError):
                    raise
                raise ValueError(
                    f"model structure cannot be read: {error}"
                ) from error
            self._occurrences = tuple(found)
        return self._occurrences

    def _node(self, occurrence):
        self.occurrences
        if (
            self._by_identity.get(id(self._nodes.get(occurrence.path)))
            is not occurrence
        ):
            raise ValueError("occurrence belongs to another snapshot")
        return self._nodes[occurrence.path]

    def select(self, reference, *, scope=None):
        """Select active bound attributes, expanding lists in model order."""
        return self._selection(reference, scope=scope)[0]

    def empty_selection(self, reference, *, scope=None):
        """Whether selection is empty because an actual repetition is empty.

        An omitted or missing named child is absent, not an empty repetition.
        """
        selected, empty, _ = self._selection(reference, scope=scope)
        return not selected and empty

    def selection_is_many(self, reference, *, scope=None):
        """Whether the actual attribute traversal expands a list or tuple."""
        return self._selection(reference, scope=scope)[2]

    def _selection(self, reference, *, scope):
        self.occurrences
        base = self._model if scope is None else self._node(scope)

        def in_scope(node):
            occurrence = self._by_identity.get(id(node))
            return occurrence is not None and (
                scope is None
                or scope.path == "."
                or occurrence.path == scope.path
                or occurrence.path.startswith(scope.path + "/")
            )

        paths = reference_path(type(base), reference)
        selected = [base]
        empty = many = False
        for segment in paths:
            next_selected = []
            for node in selected:
                value = getattr(node, segment, None)
                if isinstance(value, (list, tuple)):
                    many = True
                    empty |= not value
                next_selected.extend(
                    value if isinstance(value, (list, tuple)) else (value,)
                )
            selected = [node for node in next_selected if in_scope(node)]
        return (
            tuple(self._by_identity[id(node)] for node in selected),
            empty,
            many,
        )

    def _ensure(self, occurrence, kind):
        node = self._node(occurrence)
        if occurrence.kind not in ("rigid-piece", "rigid-feature"):
            raise ValueError(f"{occurrence.path}: no rigid artifact")
        if kind not in ("stl", "dxf") or (
            kind == "dxf" and not occurrence.nominal_dxf
        ):
            raise ValueError(
                f"{occurrence.path}: unsupported artifact kind {kind}"
            )

        def prepare(current):
            from machinome.node.internal import InternalNode

            if isinstance(current, InternalNode):
                for child in current.__dict__.get("_production_rest", ()):
                    prepare(child)
                    current.files.update(child.files)
                current.children = list(
                    current.__dict__.get("_production_rest", ())
                )
                current.generate_stl()
            else:
                # Rigid leaves have no simulate lifecycle. Avoid _prepare's
                # marking production: decals are unrelated to manufacturing.
                if not current._prepare_can_be_skipped():
                    rendered = current.render()
                    current.validate(rendered)
                    current._prepared_rendered = rendered
                    current.materialize(rendered)
                current.generate_stl()

        path = Path(getattr(node, f"{kind}_file")).absolute()
        if path not in self._artifacts:
            with self._source_phase(node.files, label="model artifact"):
                prepare(node)
            for source in self._sources(node):
                self.observe_input(source)
        self.validate()
        return path

    def geometry(self, occurrence):
        """Canonical STL identity and volume from one pinned artifact read."""
        self.validate()
        path = self._ensure(occurrence, "stl")
        if path not in self._artifacts:
            from machinome.core.pieces import (
                _digest_bytes,
                _geometry_facts_from_bytes,
            )

            with self._artifact_read(path) as opened:
                data = opened.read_bytes()
                size, volume, watertight = _geometry_facts_from_bytes(
                    path, data
                )
                facts = GeometryFacts(
                    _digest_bytes(data),
                    tuple(size) if size else None,
                    volume,
                    watertight,
                    "stl",
                    hashlib.sha256(data).hexdigest(),
                )
                self._artifacts[path] = (opened.observation, facts, data)
        self.validate()
        return self._artifacts[path][1]

    @contextmanager
    def _artifact_read(self, path):
        from machinome._artifact import ArtifactSnapshot, ArtifactChanged

        try:
            with ArtifactSnapshot(path) as opened:
                yield opened
        except (ArtifactChanged, OSError) as error:
            self._fail(f"artifact consumption failed: {path}: {error}")

    def copy_artifact(self, occurrence, kind, destination):
        """Copy the exact pinned artifact bytes; return their byte SHA-256."""
        self.validate()
        path = self._ensure(occurrence, kind)
        if kind == "stl":
            self.geometry(occurrence)
        elif path not in self._artifacts:
            with self._artifact_read(path) as opened:
                data = opened.read_bytes()
                facts = GeometryFacts(
                    hashlib.sha256(data).hexdigest(),
                    None,
                    None,
                    False,
                    kind,
                    hashlib.sha256(data).hexdigest(),
                )
                self._artifacts[path] = (opened.observation, facts, data)
        self.validate()
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self._artifacts[path][2])
        self.validate()
        return self._artifacts[path][1].artifact_sha256
