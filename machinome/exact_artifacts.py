# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Publishing an exact node's artifacts: its `.brep` and tessellated `.stl`.

The engine writes the bytes (`machinome.exact_engine`); this module owns
what the framework adds around them -- a temporary file, the source mtime
stamp, the source record published beside the artifact in the same step,
the degenerate-triangle cleanup the mesh engine needs -- and the validation
of the tessellation precision a node declares. Importing it imports no
engine.
"""

import math
import os
import tempfile
import time

from machinome import currency
from machinome.exact_engine import require_exact_engine


def _atomic_export(path, mtime_ns, exporter, digest=None, fingerprint=None):
    """Write, stamp, and vouch for one exact artifact.

    `digest` and `fingerprint` are the node's source record, written beside the
    artifact by `currency.publish` in the same step that puts it in place -- an
    artifact and the record of what produced it are written together or
    not at all. Defaulting the digest to None means "no record", which costs a
    rebuild and never a stale answer, so a caller outside a node (an
    assertion helper, a test) is served correctly without one.
    """
    directory = os.path.dirname(path) or '.'
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f'.{os.path.basename(path)}.', suffix='.tmp', dir=directory)
    os.close(descriptor)
    try:
        exporter(temporary)
        os.utime(temporary, ns=(time.time_ns(), mtime_ns))
        currency.publish(temporary, path, digest, fingerprint)
    except Exception:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise


def _engine(path, artifact):
    return require_exact_engine(f'writing {path}',
                                f'it is the exact {artifact} artifact')


def write_brep(shape, path, mtime_ns, digest=None, fingerprint=None):
    """Publish `shape`'s BREP at `path`, written by the engine."""
    engine = _engine(path, 'BREP')
    _atomic_export(path, mtime_ns,
                   lambda temporary: engine.write_brep(shape, temporary),
                   digest, fingerprint)


def write_stl(shape, path, mtime_ns, linear_deflection, angular_deflection,
             digest=None, fingerprint=None):
    """Tessellate `shape` to an STL artifact without degenerate triangles.

    The engine tessellates and writes the raw STL. OCCT's mesher emits
    zero-area triangles on some vendor solids (shafts, standoffs, stepper
    frames); they add nothing to the surface and break the mesh engine's
    edge pairing, so every exact artifact -- a leaf's or a fused solid's --
    drops them, after tessellating at whatever precision the caller asks
    for. That cleanup is framework policy, so it is made here.

    `linear_deflection` and `angular_deflection` are required rather than
    defaulted: the framework's historical values (0.1 mm, 0.1 rad) live in
    exactly one place, the class attribute declarations on `ExactLeafNode`
    and `FusionNode` (see `deflections`), not duplicated here as a second
    default a reader could find and trust.
    """
    engine = _engine(path, 'STL')

    def export(temporary):
        import trimesh
        engine.write_stl(shape, temporary, linear_deflection,
                         angular_deflection)
        mesh = trimesh.load(temporary, file_type='stl', process=False)
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.remove_unreferenced_vertices()
        mesh.export(temporary, file_type='stl')

    _atomic_export(path, mtime_ns, export, digest, fingerprint)


_DEFLECTION_UNITS = {
    'linear_deflection': 'millimetres',
    'angular_deflection': 'radians',
}


def _validated_deflection(node, attribute):
    value = getattr(node, attribute)
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0):
        unit = _DEFLECTION_UNITS[attribute]
        raise ValueError(
            f'{node.name}.{attribute} must be a positive finite number '
            f'of {unit}, not {value!r}')
    return float(value)


def deflections(node):
    """Read and validate the tessellation precision `node` declares.

    Reads `node.linear_deflection` and `node.angular_deflection` -- class
    attributes `ExactLeafNode` and `FusionNode` declare with the
    framework's historical defaults (0.1 mm, 0.1 rad) -- at the point the
    artifact is about to be written, which is what lets a node whose
    artifacts are already current skip the validation entirely.

    A value is refused unless it is a real number (`bool` excluded --
    `True` is not a deflection), finite, and strictly positive; the error
    names the node and the offending attribute.
    """
    return (_validated_deflection(node, 'linear_deflection'),
            _validated_deflection(node, 'angular_deflection'))
