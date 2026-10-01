# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compile native immutable mechanics into ordinary machinome nodes."""
import inspect
from importlib.metadata import version
from pathlib import Path
import io
import math
import os
import hashlib
import json
import shutil
import tempfile

import numpy as np
from scipy.spatial.transform import Rotation as SpatialRotation

from machinome.node import AssemblyNode
from machinome.motion.couplings import CoordinateRef, OwnRef, ResolvedEnd
from machinome.motion.joints import Revolute
from machinome.motion.ports import RotationalPort, run_owned
from machinome.node.operations import Rotation, Translation
from machinome.source_generation import track_sources, observation_key, SourceChanged

from .runtime import load_snapshot, NativeAssemblyError, _observe

def _aliases(cls):
    declarations = {}
    for base in reversed(cls.__mro__):
        declarations.update(vars(base))
    return {name: ref for name, ref in declarations.items() if isinstance(ref, FreeCADJoint)}

class FreeCADJoint(CoordinateRef):
    """Internal-Name reference to one imported physical revolute coordinate."""
    def __init__(self, name):
        if not isinstance(name, str) or not name or not name.isidentifier():
            raise TypeError('FreeCADJoint requires a native internal Name string')
        self.native_name = name
        self.name = None
        self.owner = None
        # Class-side type information only, never installed or bound on a node.
        self._metadata = RotationalPort(unit='deg')

    def __set_name__(self, owner, name):
        if self.owner is not None and (self.owner is not owner or self.name != name):
            raise TypeError('Create a separate FreeCADJoint reference for each alias')
        self.owner, self.name = owner, name
        self._metadata.owner, self._metadata.name = owner, name

    def key(self):
        return ('freecad', self.owner, self.native_name)

    def declaration(self):
        return self._metadata

    def coordinate(self):
        return self._metadata

    def described(self):
        return f'{self.name or self.native_name} (FreeCAD {self.native_name})'

    def check_declared_on(self, owner, relation):
        if not any(self is ref for ref in _aliases(owner).values()):
            raise TypeError(f'{owner.__name__}: foreign FreeCADJoint {self.described()}')

    def resolve(self, instance):
        if not isinstance(instance, FreeCADAssemblyNode):
            raise TypeError('FreeCADJoint belongs to a FreeCADAssemblyNode')
        instance._ensure_native_assembly()
        item = instance._native_coordinates.get(self.native_name)
        if item is None:
            inventory = instance._native_joint_inventory
            kind = inventory.get(self.native_name, {}).get('type', 'missing')
            raise NativeAssemblyError(f'{instance._native_path}: selector {self.native_name!r} '
                                      f'is {kind}; moving Names: '
                                      + ', '.join(instance._native_coordinates))
        node, joint = item
        return ResolvedEnd(node, joint, OwnRef(joint))

    def __get__(self, instance, owner=None):
        return self if instance is None else self.resolve(instance).slot

    def __set__(self, instance, value):
        end = self.resolve(instance)
        end.declared.__set__(end.node, value)

def _place(node, matrix):
    vector = SpatialRotation.from_matrix(matrix[:3, :3]).as_rotvec()
    angle = np.linalg.norm(vector)
    if angle > 1e-14:
        node.operations.append(Rotation(math.degrees(angle), tuple(map(float, vector / angle)), node))
    if np.linalg.norm(matrix[:3, 3]) > 1e-14:
        node.operations.append(Translation(tuple(map(float, matrix[:3, 3])), node))

def _rigid(matrix, name):
    value = np.asarray(matrix, dtype=float)
    if (value.shape != (4, 4) or not np.isfinite(value).all()
            or not np.allclose(value[3], (0, 0, 0, 1), atol=1e-10)
            or not np.allclose(value[:3, :3].T @ value[:3, :3], np.eye(3), atol=1e-10)
            or not np.isclose(np.linalg.det(value[:3, :3]), 1, atol=1e-10)):
        raise NativeAssemblyError(f'non-rigid native transform: {name}')
    return value

class _NativeCurrency:
    """Use ordinary source-currency sidecars with native recipe included."""
    def _check_native_generation(self):
        for path, expected in getattr(self, '_native_observations', {}).items():
            # Bypass the active census's frozen observation at this boundary.
            try:
                stat = os.stat(path)
            except OSError as error:
                raise SourceChanged(
                    f'Native source unavailable; construct a fresh model: {path}') from error
            actual = (str(Path(path).resolve()), stat.st_dev, stat.st_ino,
                      stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
            if actual != expected[0]:
                raise SourceChanged(f'Native source changed; construct a fresh model: {path}')

    def _tracked_fingerprint(self, files):
        self._check_native_generation()
        found = super()._tracked_fingerprint(files)
        recipe = getattr(self, '_native_recipe', '')
        return hashlib.sha256((str(found) + recipe).encode()).hexdigest() if found else None

    def _tracked_digest(self, files):
        self._check_native_generation()
        found = super()._tracked_digest(files)
        recipe = getattr(self, '_native_recipe', '')
        return hashlib.sha256((str(found) + recipe).encode()).hexdigest() if found else None

class _Carrier(_NativeCurrency, AssemblyNode):
    def get_source_file(self):
        return self._wrapper_source

    def render(self):
        self._check_native_generation()
        return self._native_children

    def simulate(self):
        if self._rest_coordinate is not None:
            joint, saved = self._rest_coordinate
            slot = joint.__get__(self)
            if slot._value is None and not run_owned(slot):
                joint.__set__(self, saved)

def _leaf_class(wrapper_source, product_key):
    from machinome.node.exact_leaf import ExactLeafNode
    class _Solid(_NativeCurrency, ExactLeafNode):
        namespace = 'cadquery'
        def get_source_file(self):
            return wrapper_source
        def materialize(self, rendered):
            from machinome import currency
            self._check_native_generation()
            replaced = not self._up_to_date(self.brep_file)
            paths = (self.brep_file, self.stl_file,
                     currency.sidecar(self.brep_file), currency.sidecar(self.stl_file))
            # Exact writers publish immediately. Preserve this leaf's existing
            # state until its native source receipt passes the post-boundary.
            # A failed native generation must not leave new certified outputs.
            with tempfile.TemporaryDirectory(prefix='freecad-publication-') as temp:
                backups = {}
                for index, path in enumerate(paths):
                    if os.path.isfile(path):
                        backup = str(Path(temp)/str(index))
                        shutil.copy2(path, backup)
                        backups[path] = backup
                try:
                    super().materialize(rendered)
                    self._check_native_generation()
                except SourceChanged:
                    for path in paths:
                        if path in backups:
                            shutil.copy2(backups[path], path)
                        elif os.path.exists(path):
                            os.unlink(path)
                    from machinome.exact import _evict
                    _evict(self.brep_file)
                    raise
            if replaced:
                # Core exact-shape cache keys only path+mtime; native recipe
                # changes can replace a BREP while source mtime stays equal.
                # Invalidate this rebuilt path through its existing helper.
                from machinome.exact import _evict
                _evict(self.brep_file)
        def render(self):
            self._check_native_generation()
            import cadquery as cq
            from OCP.BRep import BRep_Builder
            from OCP.BRepTools import BRepTools
            from OCP.TopoDS import TopoDS_Shape
            shape = TopoDS_Shape()
            BRepTools.Read_s(shape, io.BytesIO(self._brep.encode()), BRep_Builder())
            result = cq.Shape.cast(shape)
            if not result.Solids() or not result.isValid():
                raise NativeAssemblyError('Native BREP transfer contains no valid solid')
            return result
    _Solid.__qualname__ = '_NativeSolid_' + product_key
    return _Solid

class FreeCADAssemblyNode(_NativeCurrency, AssemblyNode):
    """A native grounded fixed/revolute FCStd tree, resolved at construction."""
    freecad_source = None

    def __init__(self, *args, **kwargs):
        if version('machinome') != '0.7.1':
            raise NativeAssemblyError('machinome-freecad requires tested machinome 0.7.1')
        super().__init__(*args, **kwargs)
        self._ensure_native_assembly()
        for ref in _aliases(type(self)).values():
            ref.resolve(self)

    def _ensure_native_assembly(self):
        if '_native_coordinates' in self.__dict__:
            return
        declaring = next((base for base in type(self).__mro__
                          if 'freecad_source' in vars(base)), None)
        source = getattr(declaring, 'freecad_source', None)
        if source is None:
            raise NativeAssemblyError(f'{type(self).__name__}: declare freecad_source')
        origin = Path(inspect.getfile(declaring)).resolve().parent
        self._native_path = Path(source)
        if not self._native_path.is_absolute():
            self._native_path = origin / self._native_path
        from machinome.node.sources import require_source_file
        require_source_file(declaring, 'freecad_source', source, self._native_path)
        snapshot = load_snapshot(self._native_path)
        observations = {path: (tuple(observation[0]), observation[1])
                        for path, observation in snapshot['_source_observations'].items()}
        self._native_observations = observations
        # Adopt the worker handshake's receipt; never recertify old in-memory
        # geometry from a newer file generation after snapshot acceptance.
        self._check_native_generation()
        contributors = set(snapshot['files']) | {str(self._native_path)}
        contributors.update(str(Path(__file__).with_name(name)) for name in
                            ('adapter.py','runtime.py','worker.py'))
        # The snapshot and native/importer runtime recipe are currency, never
        # part of structural product identity. ExactLeaf writes these digests
        # through its existing BREP/STL publication path.
        recipe = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
        self._native_recipe = recipe
        self.files.update(contributors)
        track_sources(self.files)
        inventory = {o['name']: o for o in snapshot['occurrences']}
        joints = {j['name']: j for j in snapshot['joints']}
        context = (f'{self._native_path}: assembly {snapshot["assembly"]}; '
                   f'occurrences: {", ".join(sorted(inventory))}; '
                   f'joints: {", ".join(sorted(j["name"] for j in snapshot["joints"]))}')
        if len(joints) != len(snapshot['joints']):
            raise NativeAssemblyError(f'{context}: duplicate native joint Names')
        ground = snapshot['ground']
        if ground not in inventory:
            raise NativeAssemblyError(f'{context}: ground {ground} missing from native occurrences')
        adjacent = {name: [] for name in inventory}
        for joint in joints.values():
            a, b = joint['endpoints']
            if a == b or a not in adjacent or b not in adjacent:
                raise NativeAssemblyError(f'{context}: invalid endpoints {joint["name"]}: {a}, {b}')
            adjacent[a].append((b, joint))
            adjacent[b].append((a, joint))
        if len(joints) != len(inventory)-1:
            raise NativeAssemblyError(f'{context}: native graph is disconnected or contains a loop')
        seen = set()
        coordinates = {}
        wrapper = str(Path(self.src).resolve())
        from hashlib import sha256
        def build(name, parent=None, edge=None):
            if name in seen:
                raise NativeAssemblyError(f'{context}: native graph loop at {name}')
            seen.add(name)
            occurrence = inventory[name]
            world = _rigid(occurrence['world'], name)
            relative = world if parent is None else np.linalg.inv(
                _rigid(inventory[parent]['world'], parent)) @ world
            attrs = {'__module__': type(self).__module__,
                     '__qualname__': type(self).__qualname__ + '._Occurrence_' + name}
            joint = None
            if edge and edge['type'] == 'Revolute':
                frame = _rigid(edge['frames'][0], edge['name'])
                inverse = np.linalg.inv(world)
                sign = 1 if name == edge['endpoints'][1] else -1
                axis = sign * inverse[:3, :3] @ frame[:3, 2]
                at = (inverse @ frame[:, 3])[:3]
                joint = Revolute(axis=tuple(axis), at=tuple(at),
                                 range=tuple(edge['range']), unit='deg')
                attrs[edge['name']] = joint
                motion = Translation(tuple(at)).matrix() @ Rotation(
                    edge['saved'], tuple(axis)).matrix() @ Translation(tuple(-at)).matrix()
                relative = relative @ np.linalg.inv(motion)
            cls = type('_NativeOccurrence', (_Carrier,), attrs)
            # Constructor fields exist before super: defaults run only later.
            node = object.__new__(cls)
            node._wrapper_source = wrapper
            node._rest_coordinate = (joint, edge['saved']) if joint else None
            node._native_children = []
            node._native_recipe = recipe
            node._native_observations = observations
            cls.__init__(node, name=name)
            node.files.update(contributors)
            _place(node, relative)
            product_origin = os.path.relpath(occurrence['document'], self._native_path.resolve().parent)
            product_key = sha256((wrapper.rsplit('/', 1)[-1] + '|' + type(self).__qualname__
                                  + '|' + product_origin + '|' + occurrence['product']).encode()).hexdigest()[:16]
            leaf_cls = _leaf_class(wrapper, product_key)
            leaf = leaf_cls(name='solid')
            leaf._brep = occurrence['brep']
            leaf._native_recipe = recipe
            leaf._native_observations = observations
            leaf.files.update(contributors)
            node._native_children.append(leaf)
            if joint:
                coordinates[edge['name']] = node, joint
            for child, connection in adjacent[name]:
                if child != parent:
                    node._native_children.append(build(child, name, connection))
            node._link_children(node._native_children)
            return node
        root = build(ground)
        if len(seen) != len(inventory):
            raise NativeAssemblyError(f'{context}: disconnected native occurrences: '
                                      + ', '.join(sorted(set(inventory)-seen)))
        self._native_children = [root]
        self._link_children(self._native_children)
        self._native_joint_inventory = joints
        self._native_coordinates = coordinates
        self._native_observations = observations
        self._native_snapshot = snapshot

    def render(self):
        # A built instance denotes one source generation. Fresh construction is
        # required after edits, instead of silently reinterpreting an active run.
        self._check_native_generation()
        return self._native_children
