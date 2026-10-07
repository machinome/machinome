"""Independent lazy production bindings over actual model occurrences."""

from dataclasses import fields, is_dataclass
from pathlib import Path
from types import MappingProxyType
import ast
import csv
import hashlib
import inspect
import json
import math
import os
import re
import shutil
import sys
import tempfile

from machinome.model import (
    ModelSnapshot,
    ModelInputChangedError,
    reference_path,
)
from .errors import (
    DeclarationError,
    BindingError,
    ProductionConflictError,
    ProductionInputChangedError,
    ProductionExportError,
)
from .item import Item, BoundItem
from .instruction import Step
from .process import Printed, Cut, Sourced
from .mass import MeasuredMass, SolidMass
from .results import (
    Finding,
    BomLine,
    StockLine,
    ResolvedStep,
    MassBasis,
    MassSummary,
    ExportResult,
)


def _join(scope, name):
    return name if not scope else f"{scope}/{name}"


def _within(path, scope):
    return scope == "." or path == scope or path.startswith(scope + "/")


def _serial(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, type):
        return f"{value.__module__}:{value.__qualname__}"
    if is_dataclass(value):
        result = {
            f.name: _serial(getattr(value, f.name)) for f in fields(value)
        }
        result["type"] = f"{type(value).__module__}:{type(value).__qualname__}"
        return result
    if isinstance(value, (dict, MappingProxyType)):
        return {str(k): _serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serial(v) for v in value]
    return value


def _identity(value):
    return json.dumps(_serial(value), sort_keys=True, separators=(",", ":"))


def _profile_sources(klass):
    """Loaded local module closure, captured without importing new code."""
    module = sys.modules.get(klass.__module__)
    file = Path(inspect.getfile(klass)).absolute()
    root = next(
        (
            p
            for p in (file.parent, *file.parents)
            if (p / "pyproject.toml").exists()
        ),
        file.parent,
    )
    found = set()

    def walk(current):
        path = getattr(current, "__file__", None)
        if not path or Path(path).suffix != ".py":
            return
        path = Path(path).absolute()
        if path in found or not path.is_relative_to(root):
            return
        found.add(path)
        try:
            tree = ast.parse(path.read_bytes())
        except (OSError, SyntaxError):
            return
        package = getattr(current, "__package__", "") or ""
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = node.module or ""
                if node.level:
                    bits = package.split(".")
                    prefix = ".".join(
                        bits[: len(bits) - node.level + 1]
                        + ([prefix] if prefix else [])
                    )
                names = [prefix] + [prefix + "." + a.name for a in node.names]
            for name in names:
                loaded = sys.modules.get(name)
                if loaded is not None:
                    walk(loaded)

    if module:
        walk(module)
    found.add(file)
    return tuple(sorted(found, key=str))


def _local_file(klass, spelling, declaration, source_file=None):
    directory = Path(source_file or inspect.getfile(klass)).resolve().parent
    supplied = Path(spelling)
    if supplied.is_absolute():
        raise ProductionExportError(
            f"{declaration}: expected a declaring-module relative file: "
            f"{spelling}"
        )
    path = directory / supplied
    if not path.resolve().is_relative_to(directory):
        raise ProductionExportError(
            f"{declaration}: file escapes declaring source directory: "
            f"{spelling}"
        )
    return path.absolute()


def _markdown(text, declaration, path):
    """Refuse dependencies that a version-one portable bundle cannot carry."""
    destinations = re.findall(r"!?\[[^\]]*\]\(\s*<?([^\s)>]+)", text)
    definitions = dict(
        re.findall(r"^\s*\[([^\]]+)\]:\s*<?([^\s>]+)", text, re.M)
    )
    destinations += list(definitions.values())
    references = re.findall(r"!?\[([^\]]+)\]\[([^\]]*)\]", text)
    for label, key in references:
        if (key or label) not in definitions:
            raise ProductionExportError(
                f"{declaration}: unresolved Markdown reference in {path}: "
                f"{key or label}"
            )
    # Shortcut reference syntax and HTML dependencies must not escape the
    # explicitly referenced file inventory.
    if re.search(r"</?[a-z][a-z0-9:-]*(?:\s[^>]*|/?)>", text, re.I):
        raise ProductionExportError(
            f"{declaration}: unsupported HTML dependency in {path}"
        )
    if re.search(r"!\[[^\]]*\](?!\()", text):
        raise ProductionExportError(
            f"{declaration}: unsupported image dependency in {path}"
        )
    for destination in destinations:
        if not destination.startswith(("http://", "https://", "#")):
            raise ProductionExportError(
                f"{declaration}: unsupported local or URL dependency "
                f"{destination!r} in {path}"
            )
    for destination in re.findall(r"<([a-z][a-z0-9+.-]*:[^>]*)>", text, re.I):
        if not destination.startswith(("https://", "http://")):
            raise ProductionExportError(
                f"{declaration}: unsupported URL dependency in {path}"
            )
    if re.search(r"<(?:file|data):", text, re.I):
        raise ProductionExportError(
            f"{declaration}: unsupported URL dependency in {path}"
        )


class Production:
    """A reusable profile bound to one compatible existing model instance.

    Declare Items, nested productions and Steps in Production[Model]. Read
    bom, stock, steps, mass or findings directly; export creates a draft.
    Construction observes sources but performs no geometry work.
    """

    _model_type = None
    _typed_base = False
    _declarations = MappingProxyType({})

    @classmethod
    def __class_getitem__(cls, model_type):
        from machinome.model import is_reference

        if not isinstance(model_type, type) or not is_reference(model_type):
            raise DeclarationError(
                "Production type argument must be a model class"
            )
        return type(
            f"ProductionFor{model_type.__name__}",
            (Production,),
            {
                "_model_type": model_type,
                "_typed_base": True,
                "__module__": cls.__module__,
            },
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("_typed_base"):
            return
        if any(
            base is not Production and not base.__dict__.get("_typed_base")
            for base in cls.__bases__
        ):
            raise DeclarationError(
                "inheritance from a concrete production profile is unsupported"
            )
        if cls._model_type is None:
            raise DeclarationError("profiles must subclass Production[Model]")
        declarations = {
            name: value
            for name, value in vars(cls).items()
            if isinstance(value, (Item, Step, Production))
        }
        identities = {}
        for name, value in declarations.items():
            if name.startswith("_") or hasattr(Production, name):
                raise DeclarationError(
                    f"{name}: profile declaration hides an output or "
                    "lifecycle member"
                )
            if id(value) in identities:
                raise DeclarationError(
                    f"{name}: declaration reused as {identities[id(value)]}"
                )
            identities[id(value)] = name
            if isinstance(value, (Item, Production)):
                targets = (
                    value.target if isinstance(value, Item) else value._target
                )
                targets = targets if isinstance(targets, tuple) else (targets,)
                if not targets:
                    raise DeclarationError(f"{name}: empty target tuple")
                try:
                    for target in targets:
                        reference_path(cls._model_type, target)
                except (ValueError, TypeError) as error:
                    raise DeclarationError(
                        f"{cls.__name__}.{name}: {error}"
                    ) from error
        for name, value in declarations.items():
            if isinstance(value, Step):
                if any(
                    id(subject) not in identities or isinstance(subject, Step)
                    for subject in value.subjects
                ):
                    raise DeclarationError(
                        f"{name}: Step subjects must be Items or children "
                        "of this profile"
                    )
        cls._declarations = MappingProxyType(declarations)

    def __new__(cls, supplied):
        return object.__new__(cls)

    def __init__(self, supplied):
        self._target = None
        self._shared = None
        self._scope = None
        self._declaration_scope = ""
        self._cache = {}
        self._children = {}
        self._declarations = MappingProxyType(dict(type(self)._declarations))
        if isinstance(supplied, self._model_type):
            try:
                self._shared = _Shared(ModelSnapshot(supplied))
                self._shared.capture_profile(type(self))
            except OSError as error:
                reason = (
                    f"{error.strerror}: {error.filename}"
                    if error.filename
                    else str(error)
                )
                raise ProductionExportError(
                    f"{type(self).__name__} cannot bind: {reason}"
                ) from error
            self._shared.root = self
        else:
            from machinome.model import is_reference

            if (is_reference(supplied) and not isinstance(supplied, type)) or (
                isinstance(supplied, tuple)
                and supplied
                and all(is_reference(ref) for ref in supplied)
            ):
                # Child references include existing typed declarations. Node
                # instances are never silently treated as declarations.
                self._target = supplied
            elif supplied is self._model_type:
                self._target = supplied
            else:
                raise BindingError(
                    f"{type(self).__name__} requires "
                    f"{self._model_type.__name__}"
                )

    def __getattribute__(self, name):
        if not name.startswith("_"):
            declarations = object.__getattribute__(self, "__dict__").get(
                "_declarations", {}
            )
            declaration = declarations.get(name)
            if isinstance(declaration, Item):
                return self._bound_item(declaration)
            if isinstance(declaration, Production):
                self._resolve()
                return self._children[name]
        return object.__getattribute__(self, name)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        instance._resolve()
        return instance._children[instance._name_of(self)]

    def _name_of(self, declaration):
        return next(
            name
            for name, value in self._declarations.items()
            if value is declaration
        )

    @property
    def parameters(self):
        self._resolve()
        return self._scope.parameters

    def _resolve(self):
        if self._shared is None:
            raise BindingError(
                "a child production declaration must be bound by its parent"
            )
        try:
            self._shared.snapshot.validate()
            if self._scope is None:
                self._scope = self._shared.snapshot.occurrences[0]
            self._shared.resolve()
        except ModelInputChangedError as error:
            raise ProductionInputChangedError(str(error)) from error

    def _bound_item(self, item):
        self._resolve()
        path = _join(self._declaration_scope, self._name_of(item))
        occurrences = self._shared.item_targets[path]
        return BoundItem(
            tuple(o.path for o in occurrences), item.process, item.mass, path
        )

    def _read(self, name, build):
        self._resolve()
        try:
            if name != "findings" and any(
                f.code == "overlap" for f in self._shared.findings
            ):
                raise ProductionConflictError(
                    "overlapping ownership: "
                    + "; ".join(
                        f.message
                        for f in self._shared.findings
                        if f.code == "overlap"
                    )
                )
            if name not in self._cache:
                self._cache[name] = build()
            self._shared.snapshot.validate()
            return self._cache[name]
        except ModelInputChangedError as error:
            raise ProductionInputChangedError(str(error)) from error

    def _records(self):
        return [
            record
            for record in self._shared.records
            if _within(record[2].path, self._scope.path)
        ]

    @property
    def findings(self):
        return self._read(
            "findings",
            lambda: tuple(
                f
                for f in self._shared.findings
                if (
                    any(
                        _within(path, self._scope.path)
                        for path in f.occurrences
                    )
                    or (
                        not f.occurrences
                        and any(
                            _within(path, self._declaration_scope or ".")
                            for path in f.declarations
                        )
                    )
                )
            ),
        )

    @property
    def steps(self):
        return self._read("steps", lambda: self._shared.steps_for(self))

    @property
    def bom(self):
        def build():
            groups = {}
            diagnostics = []
            for (
                binding,
                item,
                occurrence,
                declaration,
                codes,
            ) in self._records():
                if codes:
                    diagnostics.append(
                        BomLine(
                            "",
                            "invalid",
                            None,
                            item.process,
                            1,
                            (occurrence.path,),
                            (declaration,),
                            occurrence.source_paths,
                            codes,
                        )
                    )
                    continue
                process = item.process
                material = (
                    process.material
                    if isinstance(process, Printed)
                    else (
                        process.stock.material
                        if isinstance(process, Cut)
                        else None
                    )
                )
                facts = None
                if isinstance(process, Sourced):
                    key = ("sourced", process)
                else:
                    facts = self._shared.snapshot.geometry(occurrence)
                    fingerprints = self._shared.item_step_fingerprints(
                        declaration
                    )
                    evidence_digest = (
                        self._shared.read_file(
                            binding,
                            item.mass.evidence,
                            declaration,
                            source_file=item.mass._source_file,
                        )[2]
                        if isinstance(item.mass, MeasuredMass)
                        else None
                    )
                    key = (
                        "made",
                        facts.content_id,
                        process,
                        _identity((item.mass, evidence_digest)),
                        fingerprints,
                    )
                group = groups.setdefault(
                    key, [process, material, facts, [], [], []]
                )
                group[3].append(occurrence.path)
                group[4].append(declaration)
                group[5].extend(occurrence.source_paths)
            lines = []
            for (
                process,
                material,
                facts,
                paths,
                declarations,
                sources,
            ) in groups.values():
                lines.append(
                    BomLine(
                        "",
                        "assigned",
                        process,
                        None,
                        len(paths),
                        tuple(paths),
                        tuple(dict.fromkeys(declarations)),
                        tuple(sorted(set(sources), key=str)),
                        (),
                        facts.content_id if facts else None,
                        material,
                        (
                            process.requirement
                            if isinstance(process, Sourced)
                            else None
                        ),
                        (
                            process.offer
                            if isinstance(process, Sourced)
                            else None
                        ),
                    )
                )
            for occurrence in self._shared.candidates:
                if (
                    _within(occurrence.path, self._scope.path)
                    and occurrence.path not in self._shared.covered
                ):
                    diagnostics.append(
                        BomLine(
                            "",
                            "unassigned",
                            None,
                            None,
                            1,
                            (occurrence.path,),
                            (),
                            occurrence.source_paths,
                            ("unassigned",),
                        )
                    )
            for declaration, binding in self._shared.absent:
                if _within(binding._scope.path, self._scope.path):
                    diagnostics.append(
                        BomLine(
                            "",
                            "absent-target",
                            None,
                            None,
                            0,
                            (),
                            (declaration,),
                            tuple(_profile_sources(type(binding))),
                            ("absent-target",),
                        )
                    )
            from dataclasses import replace

            return tuple(
                replace(line, line_id=f"line-{index + 1}")
                for index, line in enumerate(lines + diagnostics)
            )

        return self._read("bom", build)

    @property
    def stock(self):
        def build():
            groups = {}
            for _, item, occurrence, _, codes in self._records():
                if not codes and isinstance(item.process, Cut):
                    groups.setdefault(item.process.stock, []).append(
                        occurrence.path
                    )
            return tuple(
                StockLine(stock, len(paths), None, tuple(paths))
                for stock, paths in groups.items()
            )

        return self._read("stock", build)

    @property
    def mass(self):
        def build():
            bases = []
            owned = set()
            for (
                binding,
                item,
                occurrence,
                declaration,
                codes,
            ) in self._records():
                if codes and occurrence.kind not in (
                    "rigid-piece",
                    "flexible-piece",
                ):
                    continue
                owned.update(self._shared.obligations(occurrence))
                grams = None
                evidence = None
                reason = "invalid recipe" if codes else "no mass basis"
                basis = "unknown"
                if not codes and isinstance(item.mass, MeasuredMass):
                    evidence, _, _ = self._shared.read_file(
                        binding,
                        item.mass.evidence,
                        declaration,
                        source_file=item.mass._source_file,
                    )
                    grams, basis, reason = item.mass.grams, "measured", None
                elif not codes and isinstance(item.mass, SolidMass):
                    basis = "homogeneous-solid"
                    material = (
                        item.process.material
                        if isinstance(item.process, Printed)
                        else (
                            item.process.stock.material
                            if isinstance(item.process, Cut)
                            else None
                        )
                    )
                    if occurrence.kind == "flexible-piece":
                        reason = "flexible volume unsupported"
                    elif material is None or material.density_kg_m3 is None:
                        reason = "density unknown"
                    elif occurrence.kind != "rigid-piece":
                        reason = "solid volume unsupported"
                    else:
                        facts = self._shared.snapshot.geometry(occurrence)
                        if (
                            facts.watertight
                            and facts.volume_mm3 is not None
                            and math.isfinite(facts.volume_mm3)
                            and facts.volume_mm3 > 0
                        ):
                            volume, volume_exponent = math.frexp(
                                facts.volume_mm3
                            )
                            density, density_exponent = math.frexp(
                                material.density_kg_m3
                            )
                            try:
                                computed = math.ldexp(
                                    volume * density / 1_000_000,
                                    volume_exponent + density_exponent,
                                )
                            except OverflowError:
                                computed = math.inf
                            if math.isfinite(computed) and computed > 0:
                                grams, reason = computed, None
                            else:
                                reason = (
                                    "finite positive solid mass unavailable"
                                )
                        else:
                            reason = "positive watertight volume unavailable"
                bases.append(
                    MassBasis(occurrence.path, grams, basis, reason, evidence)
                )
            for occurrence in self._shared.candidates:
                if (
                    _within(occurrence.path, self._scope.path)
                    and occurrence.path not in owned
                ):
                    bases.append(
                        MassBasis(
                            occurrence.path, None, "unknown", "unassigned"
                        )
                    )
            unknown = tuple(
                b.occurrence_path for b in bases if b.grams is None
            )
            absent = any(
                _within(binding._scope.path, self._scope.path)
                for _, binding in self._shared.absent
            )
            subtotal = sum(b.grams for b in bases if b.grams is not None)
            if not math.isfinite(subtotal):
                raise OverflowError(
                    f"{self._scope.path}: mass subtotal is not finite"
                )
            return MassSummary(
                subtotal,
                not unknown and not absent,
                unknown,
                tuple(bases),
            )

        return self._read("mass", build)

    def export(self, destination):
        """Atomically create a portable draft bundle at a new or empty path."""
        self._resolve()
        target = Path(destination).absolute()
        if target.exists() and (not target.is_dir() or any(target.iterdir())):
            raise ProductionExportError(
                f"destination must be new or empty: {target}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(
            tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent)
        )
        try:
            bom, stock, steps, mass, findings = (
                self.bom,
                self.stock,
                self.steps,
                self.mass,
                self.findings,
            )
            files = {}
            used_files = {step.instruction_path for step in steps}
            used_files.update(
                b.evidence_path for b in mass.basis if b.evidence_path
            )
            for path in sorted(used_files, key=str):
                _, digest, data = self._shared.files[path]
                relative = Path("files") / digest / path.name
                copied = stage / relative
                copied.parent.mkdir(parents=True, exist_ok=True)
                copied.write_bytes(data)
                files[str(path)] = str(relative)
            artifacts = []
            for line in bom:
                if line.status != "assigned" or isinstance(
                    line.process, Sourced
                ):
                    continue
                kind = "dxf" if isinstance(line.process, Cut) else "stl"
                occurrence = self._shared.occurrences[line.occurrence_paths[0]]
                temporary = stage / ".artifact"
                digest = self._shared.snapshot.copy_artifact(
                    occurrence, kind, temporary
                )
                relative = Path("artifacts") / f"{digest}.{kind}"
                copied = stage / relative
                copied.parent.mkdir(parents=True, exist_ok=True)
                temporary.replace(copied)
                artifacts.append(
                    {
                        "line_id": line.line_id,
                        "kind": kind,
                        "sha256": digest,
                        "geometry_id": line.geometry_id,
                        "file": str(relative),
                    }
                )
            complete = not any(line.status != "assigned" for line in bom)
            manifest = {
                "format": "machinome-production",
                "version": 1,
                "draft": True,
                "coverage_complete": complete,
                "executed_code_provenance": (
                    self._shared.snapshot.executed_code_provenance
                ),
                "model": _serial(self._scope.model_type),
                "profile": _serial(type(self)),
                "parameters": _serial(self._scope.parameters),
                "bindings": self._shared.binding_records(self),
                "occurrences": _serial(
                    tuple(
                        o
                        for o in self._shared.snapshot.occurrences
                        if _within(o.path, self._scope.path)
                    )
                ),
                "owners": self._shared.owner_records(self),
                "bom": _serial(bom),
                "stock": _serial(stock),
                "steps": _serial(steps),
                "mass": _serial(mass),
                "findings": _serial(findings),
                "checks": {
                    "structure": "checked",
                    "recipe": "checked",
                    "manufactured-geometry": "checked",
                    "mass": "checked",
                },
                "input_hashes": dict(self._shared.snapshot.input_hashes),
                "files": files,
                "artifacts": artifacts,
                "instruction_files": {
                    step.step_id: files[str(step.instruction_path)]
                    for step in steps
                },
                "mass_evidence_files": {
                    basis.occurrence_path: files[str(basis.evidence_path)]
                    for basis in mass.basis
                    if basis.evidence_path
                },
            }
            (stage / "production.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
            with (stage / "bom.csv").open("w", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(
                    (
                        "line_id",
                        "status",
                        "process",
                        "description",
                        "quantity",
                        "occurrence_paths",
                        "finding_codes",
                    )
                )
                for line in bom:
                    writer.writerow(
                        (
                            line.line_id,
                            line.status,
                            (
                                type(line.process).__name__
                                if line.process
                                else ""
                            ),
                            (
                                _identity(line.requirement or line.material)
                                if line.process
                                else line.status
                            ),
                            line.quantity,
                            json.dumps(line.occurrence_paths),
                            json.dumps(line.finding_codes),
                        )
                    )
            with (stage / "stock.csv").open("w", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(
                    (
                        "stock",
                        "finished_count",
                        "purchased_quantity",
                        "occurrence_paths",
                    )
                )
                for line in stock:
                    writer.writerow(
                        (
                            _identity(line.stock),
                            line.finished_count,
                            "",
                            json.dumps(line.occurrence_paths),
                        )
                    )
            instructions = [
                "# Draft maker instructions\n\n"
                "Coverage is not fabrication acceptance.\n"
            ]
            for step in steps:
                instructions.append(
                    f"\n## {step.step_id}\n\nScope: {step.scope_path}"
                    "\n\nSubjects: "
                    + ", ".join(step.subject_paths)
                    + "\n\n"
                    + step.instruction_text
                    + "\n"
                )
            for basis in mass.basis:
                if basis.evidence_path:
                    instructions.append(
                        f"\nMass evidence for {basis.occurrence_path}: "
                        f"[{basis.evidence_path.name}]"
                        f"({files[str(basis.evidence_path)]})\n"
                    )
            (stage / "instructions.md").write_text("".join(instructions))
            self._shared.snapshot.validate()
            if target.exists():
                target.rmdir()
            os.replace(stage, target)
            return ExportResult(
                target,
                complete,
                findings,
                self._shared.snapshot.executed_code_provenance,
            )
        except ModelInputChangedError as error:
            raise ProductionInputChangedError(str(error)) from error
        except (
            ProductionInputChangedError,
            ProductionConflictError,
            ProductionExportError,
        ):
            raise
        except Exception as error:
            raise ProductionExportError(
                f"draft export failed: {error}"
            ) from error
        finally:
            if stage.exists():
                shutil.rmtree(stage)


class _Shared:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.root = None
        self.resolved = False
        self.records = []
        self.findings = []
        self.absent = []
        self.item_targets = {}
        self.files = {}
        self.covered = set()
        self.bindings = []
        self._captured = set()
        self.profile_declarations = {}
        self.child_targets = {}

    def capture_profile(self, klass):
        if klass in self._captured:
            return
        self._captured.add(klass)
        self.profile_declarations[klass] = MappingProxyType(
            dict(klass._declarations)
        )
        for path in _profile_sources(klass):
            self.snapshot.observe_input(path)
        for name, declaration in self.profile_declarations[klass].items():
            if isinstance(declaration, Production):
                self.child_targets[id(declaration)] = declaration._target
                self.capture_profile(type(declaration))
            spelling = (
                declaration.instructions.path
                if isinstance(declaration, Step)
                else (
                    declaration.mass.evidence
                    if isinstance(declaration, Item)
                    and isinstance(declaration.mass, MeasuredMass)
                    else None
                )
            )
            if spelling is not None:
                source_file = (
                    declaration._source_file
                    if isinstance(declaration, Step)
                    else declaration.mass._source_file
                )
                self.snapshot.observe_input(source_file)
                path = _local_file(klass, spelling, name, source_file)
                if path.exists():
                    self.snapshot.observe_input(path)

    def obligations(self, occurrence):
        if occurrence.kind == "assembly":
            return {
                o.path
                for o in self.candidates
                if _within(o.path, occurrence.path)
            }
        return {occurrence.path}

    def selected(self, binding, target, declaration):
        refs = target if isinstance(target, tuple) else (target,)
        found = []
        for ref in refs:
            selected = self.snapshot.select(ref, scope=binding._scope)
            if not selected:
                # Empty actual repetitions are valid zero quantities. A named
                # omitted/missing target carries a separate absent diagnostic.
                empty = self.snapshot.empty_selection(
                    ref, scope=binding._scope
                )
                if not empty:
                    self.absent.append((declaration, binding))
                    self.findings.append(
                        Finding(
                            "absent-target",
                            "warning",
                            (),
                            (declaration,),
                            f"{declaration}: named target absent from "
                            "active model",
                        )
                    )
            found.extend(selected)
        if len({o.path for o in found}) != len(found):
            raise BindingError(
                f"{declaration}: duplicate selected occurrences"
            )
        return tuple(found)

    def resolve(self):
        if self.resolved:
            return
        self.records = []
        self.findings = []
        self.absent = []
        self.item_targets = {}
        self.covered = set()
        self.bindings = []
        self.occurrences = {o.path: o for o in self.snapshot.occurrences}
        self.candidates = tuple(
            o
            for o in self.occurrences.values()
            if o.kind in ("rigid-piece", "flexible-piece")
        )
        local_claims = {}

        def populate(binding):
            self.bindings.append(binding)
            local = []
            for name, declaration in binding._declarations.items():
                path = _join(binding._declaration_scope, name)
                if isinstance(declaration, Item):
                    selected = self.selected(binding, declaration.target, path)
                    self.item_targets[path] = selected
                    for occurrence in selected:
                        process, codes = declaration.process, []
                        if (
                            isinstance(process, Printed)
                            and occurrence.kind != "rigid-piece"
                        ):
                            codes.append("unsupported-print-target")
                        elif isinstance(process, Cut):
                            if (
                                occurrence.kind != "rigid-piece"
                                or not occurrence.nominal_dxf
                            ):
                                codes.append("unsupported-cut-target")
                            elif not math.isclose(
                                occurrence.sheet_thickness_mm,
                                process.stock.thickness_mm,
                                rel_tol=0,
                                abs_tol=1e-9,
                            ):
                                codes.append("stock-thickness-mismatch")
                        elif (
                            isinstance(process, Sourced)
                            and occurrence.kind == "rigid-feature"
                        ):
                            codes.append("unsupported-source-target")
                        self.records.append(
                            (
                                binding,
                                declaration,
                                occurrence,
                                path,
                                tuple(codes),
                            )
                        )
                        obligations = self.obligations(occurrence)
                        if (
                            occurrence.kind
                            in ("rigid-piece", "flexible-piece")
                            or not codes
                        ):
                            self.covered.update(obligations)
                        reservation = (
                            {
                                o.path
                                for o in self.occurrences.values()
                                if _within(o.path, occurrence.path)
                            }
                            if occurrence.kind == "assembly"
                            else obligations
                        )
                        local.append((path, reservation))
                        for code in codes:
                            self.findings.append(
                                Finding(
                                    code,
                                    "warning",
                                    (occurrence.path,),
                                    (path,),
                                    f"{path}: recipe incompatible with "
                                    f"{occurrence.path}",
                                )
                            )
                elif isinstance(declaration, Production):
                    target = self.child_targets[id(declaration)]
                    selected = self.selected(binding, target, path)
                    children = []
                    for index, occurrence in enumerate(selected):
                        if not issubclass(
                            occurrence.model_type, declaration._model_type
                        ):
                            raise BindingError(
                                f"{path}: selected model is incompatible "
                                "with child production"
                            )
                        child = object.__new__(type(declaration))
                        child._target = None
                        child._shared = self
                        child._scope = occurrence
                        child._declaration_scope = (
                            path if len(selected) == 1 else f"{path}-{index}"
                        )
                        child._cache = {}
                        child._children = {}
                        child._declarations = self.profile_declarations[
                            type(declaration)
                        ]
                        children.append(child)
                        populate(child)
                    # A repeat or tuple remains a tuple even with one member.
                    is_many = isinstance(target, tuple) or len(selected) != 1
                    is_many = is_many or self.snapshot.selection_is_many(
                        target, scope=binding._scope
                    )
                    binding._children[name] = (
                        tuple(children) if is_many else children[0]
                    )
                    reservation = {
                        o.path
                        for o in self.occurrences.values()
                        if any(
                            _within(o.path, chosen.path) for chosen in selected
                        )
                    }
                    local.append((path, reservation))
            for index, (declaration, obligations) in enumerate(local):
                remaining = local[index + 1:]
                for other, other_obligations in remaining:
                    overlaps = tuple(sorted(obligations & other_obligations))
                    if overlaps:
                        competitors = tuple(sorted((declaration, other)))
                        self.findings.append(
                            Finding(
                                "overlap",
                                "error",
                                overlaps,
                                competitors,
                                f'{", ".join(competitors)} claim '
                                f'{", ".join(overlaps)}',
                            )
                        )
            local_claims[binding._declaration_scope] = local

        populate(self.root)
        for occurrence in self.candidates:
            if occurrence.path not in self.covered:
                self.findings.append(
                    Finding(
                        "unassigned",
                        "warning",
                        (occurrence.path,),
                        (),
                        f"{occurrence.path}: no production recipe",
                    )
                )
        self.findings = tuple(
            sorted(
                self.findings,
                key=lambda f: (f.code, f.occurrences, f.declarations),
            )
        )
        self.resolved = True

    def read_file(self, binding, spelling, declaration, *, source_file=None):
        path = _local_file(type(binding), spelling, declaration, source_file)
        if not path.is_file():
            raise ProductionExportError(
                f"{declaration}: cannot read missing instruction/evidence "
                f"file: {path}"
            )
        try:
            digest = self.snapshot.observe_input(path)
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ProductionInputChangedError(
                    f"{declaration}: file changed while reading: {path}"
                )
            text = data.decode("utf-8")
            _markdown(text, declaration, path)
            self.snapshot.validate()
        except (OSError, UnicodeDecodeError) as error:
            raise ProductionExportError(
                f"{declaration}: cannot read {path}: {error}"
            ) from error
        self.files[path] = (text, digest, data)
        return path, text, digest

    def steps_for(self, root):
        found = []

        def walk(binding):
            for child in binding._children.values():
                for member in child if isinstance(child, tuple) else (child,):
                    walk(member)
            for name, declaration in binding._declarations.items():
                if not isinstance(declaration, Step):
                    continue
                path = _join(binding._declaration_scope, name)
                subjects = []
                for subject in declaration.subjects:
                    name = binding._name_of(subject)
                    if isinstance(subject, Item):
                        subjects.extend(
                            o.path
                            for o in self.item_targets[
                                _join(binding._declaration_scope, name)
                            ]
                        )
                    else:
                        children = binding._children[name]
                        if isinstance(children, tuple):
                            subjects.extend(
                                child._scope.path for child in children
                            )
                        else:
                            subjects.append(children._scope.path)
                file, text, digest = self.read_file(
                    binding,
                    declaration.instructions.path,
                    path,
                    source_file=declaration._source_file,
                )
                found.append(
                    ResolvedStep(
                        path,
                        binding._scope.path,
                        tuple(subjects),
                        file,
                        text,
                        digest,
                    )
                )

        walk(root)
        return tuple(found)

    def item_step_fingerprints(self, declaration):
        found = []
        for binding in self.bindings:
            for name, step in binding._declarations.items():
                if isinstance(step, Step) and any(
                    isinstance(subject, Item)
                    and _join(
                        binding._declaration_scope, binding._name_of(subject)
                    )
                    == declaration
                    for subject in step.subjects
                ):
                    step_id = _join(binding._declaration_scope, name)
                    found.append(
                        self.read_file(
                            binding,
                            step.instructions.path,
                            step_id,
                            source_file=step._source_file,
                        )[2]
                    )
        return tuple(found)

    def binding_records(self, root):
        return [
            {
                "profile": _serial(type(b)),
                "scope_path": b._scope.path,
                "declaration_path": b._declaration_scope,
                "parameters": _serial(b._scope.parameters),
            }
            for b in self.bindings
            if _within(b._scope.path, root._scope.path)
        ]

    def owner_records(self, root):
        owners = {
            o.path: None
            for o in self.candidates
            if _within(o.path, root._scope.path)
        }
        for _, _, occurrence, declaration, codes in root._records():
            if not codes or occurrence.kind in (
                "rigid-piece",
                "flexible-piece",
            ):
                for path in self.obligations(occurrence):
                    owners[path] = declaration
            owners[occurrence.path] = declaration
        return owners
