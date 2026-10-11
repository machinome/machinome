# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
# Residual conventions derived from OndselSolver: Copyright (c) 2023 Ondsel, Inc.
# Original Python adaptation added 2026-10-01; see the framework's CREDITS.md.
"""Executed only by FreeCAD's Python; uses native APIs, never FCStd XML.

Trusted documents only: restoring Python proxies executes source code.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

ACCEPTANCE_RECIPE = 'native-fixed-revolute-residual-v1'
POSITION_TOLERANCE_MM = 0.01
ORIENTATION_TOLERANCE_DEG = 0.001

def constraint_residual(kind, frames, context):
    """Validate pinned native marker constraints, including opposite branches.

    Original Python validator, informed by OndselSolver FixedJoint/RevoluteJoint
    at 30e9b64e8bf881d438d4b88834f9ba3674865418; see NOTICE.md.
    """
    if kind not in ('Fixed', 'Revolute'):
        raise ValueError(f'{context}: unknown native residual convention {kind}')
    if not all(math.isfinite(v) for frame in frames for row in frame for v in row):
        raise ValueError(f'{context}: nonfinite native {kind} constraint residual frames {frames}; '
                         'direction_cosines unavailable; '
                         f'tolerances {POSITION_TOLERANCE_MM}mm, {ORIENTATION_TOLERANCE_DEG}deg')
    first, second = frames
    delta = [second[i][3]-first[i][3] for i in range(3)]
    distance = math.sqrt(sum(v*v for v in delta))
    relative = [[sum(first[k][i]*second[k][j] for k in range(3))
                 for j in range(3)] for i in range(3)]
    direction_cosines = ([relative[1][0], relative[2][0], relative[2][1]]
                         if kind == 'Fixed' else [relative[2][0], relative[2][1]])
    if kind == 'Fixed':
        # Native zero direction-cosines permit four proper diagonal rotations,
        # not just identity. Measure distance to each permissible branch.
        angles = []
        for signs in ((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)):
            rotation = [[signs[i]*relative[i][j] for j in range(3)] for i in range(3)]
            sine = .5*math.sqrt(sum((rotation[i][j]-rotation[j][i])**2
                                   for i,j in ((2,1),(0,2),(1,0))))
            cosine = max(-1., min(1., (sum(rotation[i][i] for i in range(3))-1)/2))
            angles.append(math.degrees(math.atan2(sine,cosine)))
        angle = min(angles)
    else:
        # Both parallel and antiparallel native Z axes are valid; twist is free.
        angle = math.degrees(math.atan2(math.hypot(*direction_cosines),abs(relative[2][2])))
    cosine_tolerance = math.sin(math.radians(ORIENTATION_TOLERANCE_DEG))
    residual = {'origin_delta_mm':delta, 'distance_mm':distance,
                'orientation_deg':angle, 'direction_cosines':direction_cosines}
    if (not all(math.isfinite(v) for v in (distance,angle,*direction_cosines))
            or distance > POSITION_TOLERANCE_MM or angle > ORIENTATION_TOLERANCE_DEG
            or any(abs(v) > cosine_tolerance for v in direction_cosines)):
        raise ValueError(f'{context}: native {kind} constraint residual {residual}; '
                         f'zero targets; tolerances {POSITION_TOLERANCE_MM}mm, '
                         f'{ORIENTATION_TOLERANCE_DEG}deg, direction_cosines {cosine_tolerance}')
    return residual

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def matrix(placement):
    m = placement.toMatrix()
    return [[getattr(m, f'A{i}{j}') for j in range(1, 5)] for i in range(1, 5)]

def resolve(request):
    if request.get('acceptance_recipe') != ACCEPTANCE_RECIPE:
        raise ValueError('unsupported native acceptance recipe')
    import FreeCAD as App
    import Part
    if tuple(App.Version()[:3]) != ('1', '1', '4'):
        raise ValueError('Only recorded FreeCAD 1.1.4 is currently supported: ' + repr(App.Version()))
    root = Path(request['runtime_root'])
    for path in (root / 'usr/Mod', root / 'usr/Mod/Assembly'):
        sys.path.insert(0, str(path))
    import UtilsAssembly
    # Pre-observe the discovered closure before App.openDocument can read it.
    expected = request['expected']
    for path, wanted in expected.items():
        if digest(path) != wanted:
            raise ValueError(f'source changed before native loading: {path}')
    document = App.openDocument(request['source'])
    documents = list(App.listDocuments().values())
    # Keep native filename spellings: resolving a file symlink here would lose
    # the very link identity the host generation needs to guard publication.
    files = sorted({str(Path(d.FileName).absolute()) for d in documents if d.FileName})
    if request['mode'] == 'discover':
        return {'files': files}
    if set(files) != set(expected):
        raise ValueError('consumed linked document closure changed')
    assemblies = [o for o in document.Objects if o.TypeId == 'Assembly::AssemblyObject']
    if len(assemblies) != 1:
        raise ValueError('expected one native Assembly::AssemblyObject; found '
                         + repr([o.Name for o in assemblies]))
    assembly = assemblies[0]
    occurrences = UtilsAssembly.getMovablePartsWithin(assembly)
    candidate_joints = [obj.Name for group in assembly.OutList
                        if group.TypeId == 'Assembly::JointGroup' for obj in group.Group]
    context = (f'{request["source"]}: assembly {assembly.Name}; '
               f'occurrences: {", ".join(sorted(o.Name for o in occurrences))}; '
               f'joints: {", ".join(sorted(candidate_joints))}')
    if not occurrences or len({o.Name for o in occurrences}) != len(occurrences):
        raise ValueError(f'{context}: empty or ambiguous native occurrence inventory')
    def global_placement(obj):
        return UtilsAssembly.getGlobalPlacement((obj, ['', '']), obj)
    saved = {o.Name: global_placement(o) for o in occurrences}
    # Resolve authored references/offsets natively before checking residuals.
    # Cached connector Placement properties are not the source authority.
    def validate_constraints(phase):
        measured = {}
        for group in assembly.OutList:
            if group.TypeId != 'Assembly::JointGroup':
                continue
            for obj in group.Group:
                kind = str(getattr(obj, 'JointType', ''))
                if kind not in ('Fixed', 'Revolute'):
                    continue
                if type(obj.Proxy).__name__ != 'Joint':
                    raise ValueError(f'{context}: unrestored native Joint proxy: {obj.Name}')
                frames, endpoints = [], []
                for side in (1,2):
                    ref = getattr(obj, 'Reference'+str(side))
                    if not UtilsAssembly.isRefValid(ref,2):
                        raise ValueError(f'{context}: unresolved {obj.Name}.Reference{side}')
                    moving = UtilsAssembly.getMovingPart(ref)
                    if moving is None:
                        raise ValueError(f'{context}: unresolved {obj.Name}.Reference{side}')
                    endpoints.append(moving.Name)
                    plc = getattr(obj,'Placement'+str(side))
                    frames.append(matrix(UtilsAssembly.getJcsGlobalPlc(
                        plc,ref)))
                measured[obj.Name] = {'type':kind,'endpoints':endpoints,
                    'residual':constraint_residual(kind,frames,
                        f'{context}; joint {obj.Name} endpoints {endpoints}; {phase}')}
        return measured
    for doc in documents:
        doc.recompute()
        for obj in doc.Objects:
            if any(s in obj.State for s in ('Invalid', 'Error')):
                raise ValueError(f'native recompute error: {doc.FileName}:{obj.Name} {obj.State}')
    validate_constraints('recomputed, before solve')
    # Native solve is necessary but insufficient: marker residuals are checked
    # independently before and after it; no implicit source repair is admitted.
    status = assembly.solve()
    if status != 0:
        raise ValueError(f'{context}: native assembly solver status {status}')
    resolved_constraints = validate_constraints('resolved')
    inventory = []
    for occurrence in occurrences:
        if occurrence.TypeId not in ('App::Link', 'PartDesign::Body', 'Part::Feature'):
            raise ValueError(f'unsupported rigid occurrence {occurrence.Name}:{occurrence.TypeId}')
        if hasattr(occurrence, 'Scale') and abs(occurrence.Scale - 1) > 1e-12:
            raise ValueError(f'non-rigid occurrence scale: {occurrence.Name}')
        if hasattr(occurrence, 'ScaleVector') and any(abs(v - 1) > 1e-12 for v in occurrence.ScaleVector):
            raise ValueError(f'non-rigid occurrence scale vector: {occurrence.Name}')
        world = global_placement(occurrence)
        difference = saved[occurrence.Name].inverse() * world
        drift = difference.Base.Length
        angle = math.degrees(difference.Rotation.Angle)
        if drift > POSITION_TOLERANCE_MM or min(angle, 360-angle) > ORIENTATION_TOLERANCE_DEG:
            involved = {name:result for name,result in resolved_constraints.items()
                        if occurrence.Name in result['endpoints']}
            raise ValueError(f'{context}: saved/resolved pose drift residual '
                             f'{occurrence.Name}: {drift}mm {angle}deg; '
                             f'tolerances {POSITION_TOLERANCE_MM}mm, '
                             f'{ORIENTATION_TOLERANCE_DEG}deg; '
                             f'resolved involved native constraints {involved}')
        product = occurrence.getLinkedObject() if occurrence.TypeId == 'App::Link' else occurrence
        if product is None or not hasattr(occurrence, 'Shape'):
            raise ValueError(f'unresolved native occurrence: {occurrence.Name}')
        shape = occurrence.Shape.copy()
        shape.Placement = App.Placement()
        if not shape.Solids or not shape.isValid() or shape.Volume <= 0:
            raise ValueError(f'non-solid native occurrence: {occurrence.Name}')
        inventory.append({'name': occurrence.Name, 'label': occurrence.Label,
                          'product': product.Name,
                          'document': str(Path(product.Document.FileName).resolve()),
                          'world': matrix(world), 'saved_world': matrix(saved[occurrence.Name]),
                          'drift_mm': drift, 'drift_deg': angle,
                          'volume': shape.Volume,
                          'brep': shape.exportBrepToString()})
    members = {o.Name: o for o in occurrences}
    groups = [o for o in assembly.OutList if o.TypeId == 'Assembly::JointGroup']
    if len(groups) != 1:
        raise ValueError(f'{context}: expected one native JointGroup: '
                         + repr([o.Name for o in groups]))
    group = groups[0]
    grounds = [o for o in group.Group if hasattr(o, 'ObjectToGround')]
    if len(grounds) != 1 or grounds[0].ObjectToGround not in occurrences:
        raise ValueError(f'{context}: expected exactly one grounded occurrence; found '
                         + repr([g.Name for g in grounds]))
    joints = []
    for obj in group.Group:
        if hasattr(obj, 'ObjectToGround'):
            continue
        if not hasattr(obj, 'JointType'):
            raise ValueError(f'{context}: unsupported native joint object {obj.Name}:{obj.TypeId}')
        kind = str(obj.JointType)
        if kind not in ('Fixed', 'Revolute'):
            raise ValueError(f'{context}: unsupported joint {obj.Name}: {kind}')
        if bool(getattr(obj, 'Suppressed', False)):
            raise ValueError(f'{context}: suppressed joint {obj.Name}')
        if type(obj.Proxy).__name__ != 'Joint':
            raise ValueError(f'unrestored native Joint proxy: {obj.Name}')
        endpoints = []
        frames = []
        for side in (1, 2):
            ref = getattr(obj, 'Reference' + str(side))
            if not UtilsAssembly.isRefValid(ref, 2):
                raise ValueError(f'unresolved reference {obj.Name}.Reference{side}: {ref}')
            target = UtilsAssembly.getObject(ref)
            if target is None:
                raise ValueError(f'unresolved object {obj.Name}.Reference{side}: {ref}')
            for sub in ref[1]:
                element = UtilsAssembly.getElementName(sub)
                if element and target.Shape.getElement(element) is None:
                    raise ValueError(f'unresolved subelement {obj.Name}.Reference{side}: {sub}')
            moving = UtilsAssembly.getMovingPart(ref)
            if moving is None or moving.Name not in members or members[moving.Name] is not moving:
                raise ValueError(f'foreign endpoint {obj.Name}.Reference{side}: {ref}')
            # Native proxy recomputes subelement frames plus authored offsets.
            plc = getattr(obj, 'Placement' + str(side))
            if not getattr(obj, 'Detach' + str(side)):
                native = obj.Proxy.findPlacement(obj, ref, side-1)
                delta = plc.inverse() * native
                if delta.Base.Length > 1e-7 or delta.Rotation.Angle > 1e-7:
                    raise ValueError(f'unresolved connector drift {obj.Name}.Placement{side}')
            endpoints.append(moving.Name)
            frames.append(matrix(UtilsAssembly.getJcsGlobalPlc(plc, ref)))
        span = [None, None]
        q = None
        if kind == 'Revolute':
            q = math.degrees(UtilsAssembly.getJointXYAngle(obj))
            for i, side in enumerate(('Min', 'Max')):
                if getattr(obj, 'EnableAngle' + side):
                    quantity = getattr(obj, 'Angle' + side)
                    if quantity.Unit != App.Units.Angle:
                        raise ValueError(f'invalid angle unit {obj.Name}: {quantity.Unit}')
                    value = float(quantity.getValueAs('deg'))
                    if not math.isfinite(value):
                        raise ValueError(f'nonfinite limit {obj.Name}')
                    span[i] = value
            if all(v is not None for v in span) and span[0] > span[1]:
                raise ValueError(f'reversed enabled bounds {obj.Name}: {span}')
        residual = constraint_residual(kind,frames,
            f'{context}; joint {obj.Name} endpoints {endpoints}; resolved')
        joints.append({'name': obj.Name, 'label': obj.Label, 'type': kind,
                       'endpoints': endpoints, 'frames': frames,
                       'constraint_residual': residual,
                       'saved': q, 'range': span, 'unit': 'deg' if q is not None else None})
    for path, wanted in expected.items():
        if digest(path) != wanted:
            raise ValueError(f'source changed during native resolution: {path}')
    return {'files': files, 'runtime': App.Version(), 'occt': Part.OCC_VERSION,
            'acceptance_recipe': ACCEPTANCE_RECIPE,
            'constraint_tolerances': {'position_mm':POSITION_TOLERANCE_MM,
                                      'orientation_deg':ORIENTATION_TOLERANCE_DEG},
            'assembly': assembly.Name,
            'ground': grounds[0].ObjectToGround.Name,
            'occurrences': inventory, 'joints': joints}

if __name__ == '__main__':
    output = Path(sys.argv[1])
    try:
        response = resolve(json.loads(sys.argv[2]))
    except Exception as error:
        response = {'error': str(error), 'traceback': traceback.format_exc()}
        output.write_text(json.dumps(response))
        sys.exit(1)
    output.write_text(json.dumps(response))
