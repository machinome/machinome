# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Native constraint admission; Dum-E remains external negative evidence."""
import os
from pathlib import Path
import subprocess
import json
from copy import deepcopy
import math

import numpy as np
import pytest

from machinome_freecad import FreeCADAssemblyNode, runtime
from machinome_freecad import worker
from test_public import FIXTURE, world_poses

@pytest.mark.parametrize('filename,joint,kind,endpoints', [
    ('FixedQuarterTurn','JointFixed','Fixed',['Moving','FixedChild']),
    ('RevoluteDisplaced','Joint001','Revolute',['Ground','Moving']),
    ('RevoluteTilted','Joint001','Revolute',['Ground','Moving']),
])
def test_native_inconsistent_constraint_is_refused(filename,joint,kind,endpoints):
    class Invalid(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name(filename+'.FCStd')
    before = dict(runtime._cache)
    with pytest.raises(runtime.NativeAssemblyError) as error:
        Invalid()
    message = str(error.value)
    for text in (str(Invalid.freecad_source),joint,kind,*endpoints,
                 'residual','tolerance','mm','deg','direction_cosines'):
        assert text in message
    assert runtime._cache == before

@pytest.mark.parametrize('filename',['FixedOppositeX','FixedOppositeY','FixedOppositeZ','Antiparallel','StaleConnectors'])
def test_native_valid_opposite_axis_branch_is_accepted(filename):
    class Valid(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name(filename+'.FCStd')
    node = Valid()
    assert len(world_poses(node)) >= 4

def test_native_fixed_quarter_turn_has_success_status_and_stable_pose():
    # Independent native observation: the exact source must reproduce the
    # solve-status admission hole, not a synthetic mocked successful worker.
    source = FIXTURE.with_name('FixedQuarterTurn.FCStd')
    root = Path(os.environ['MACHINOME_FREECAD_ROOT'])
    script = '''import sys,json,math
from pathlib import Path
import FreeCAD as App
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'usr/Mod/Assembly'),str(root/'usr/Mod')]
import JointObject,UtilsAssembly as U
doc=App.openDocument(sys.argv[2]);child=doc.getObject('FixedChild');saved=App.Placement(child.Placement)
doc.recompute();status=doc.getObject('Assembly').solve();joint=doc.getObject('JointFixed')
delta=saved.inverse()*child.Placement
relative=U.getJcsGlobalPlc(joint.Placement1,joint.Reference1).inverse()*U.getJcsGlobalPlc(joint.Placement2,joint.Reference2)
print('EVIDENCE '+json.dumps([status,delta.Base.Length,math.degrees(delta.Rotation.Angle),relative.toMatrix().A21]))
'''
    completed = subprocess.run([str(root/'AppRun'),'python','-c',script,str(root),str(source)],
        env=dict(os.environ,PYTHONPATH=str(root/'usr/lib')),text=True,capture_output=True,check=True)
    line = next(line for line in completed.stdout.splitlines() if line.startswith('EVIDENCE '))
    status,translation,angle,residual = json.loads(line[9:])
    assert status == 0
    assert translation < 1e-9
    assert angle < 1e-9
    assert abs(residual) == pytest.approx(1,abs=1e-9,rel=0)

def test_native_stale_cache_is_real_and_recompute_restores_without_pose_drift():
    source = FIXTURE.with_name('StaleConnectors.FCStd')
    root = Path(os.environ['MACHINOME_FREECAD_ROOT'])
    script = '''import sys,json,math
from pathlib import Path
import FreeCAD as App
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'usr/Mod/Assembly'),str(root/'usr/Mod')]
import JointObject,UtilsAssembly as U
doc=App.openDocument(sys.argv[2]);joint=doc.getObject('Joint001')
native1=joint.Proxy.findPlacement(joint,joint.Reference1,0)
native2=joint.Proxy.findPlacement(joint,joint.Reference2,1)
cache_error=joint.Placement1.inverse()*native1
relative=U.getJcsGlobalPlc(native1,joint.Reference1).inverse()*U.getJcsGlobalPlc(native2,joint.Reference2)
m=relative.toMatrix()
saved={name:App.Placement(doc.getObject(name).Placement) for name in ('Ground','Moving','FixedChild')}
initial=[cache_error.Base.Length,math.degrees(cache_error.Rotation.Angle),relative.Base.Length,m.A31,m.A32]
doc.recompute()
restored=joint.Placement1.inverse()*joint.Proxy.findPlacement(joint,joint.Reference1,0)
drifts=[saved[name].inverse()*doc.getObject(name).Placement for name in saved]
print('EVIDENCE '+json.dumps(initial+[restored.Base.Length,math.degrees(restored.Rotation.Angle),
    max(delta.Base.Length for delta in drifts),max(math.degrees(delta.Rotation.Angle) for delta in drifts)]))
'''
    completed = subprocess.run([str(root/'AppRun'),'python','-c',script,str(root),str(source)],
        env=dict(os.environ,PYTHONPATH=str(root/'usr/lib')),text=True,capture_output=True,check=True)
    line = next(line for line in completed.stdout.splitlines() if line.startswith('EVIDENCE '))
    distance,angle,*valid = json.loads(line[9:])
    assert distance > 10
    assert angle > 80
    assert all(abs(value) < 1e-9 for value in valid), valid

def test_original_dume_is_negative_admission_evidence():
    configured = os.environ.get('MACHINOME_FREECAD_DUME_SOURCE')
    if not configured:
        pytest.skip('Set MACHINOME_FREECAD_DUME_SOURCE for external untouched source refusal')
    source = Path(configured)
    before = dict(runtime._cache)
    with pytest.raises(runtime.NativeAssemblyError) as error:
        runtime.load_snapshot(source)
    for text in (str(source),'Joint002','Fixed','Turn_table','Shoulder',
                 'residual','tolerance','direction_cosines'):
        assert text in str(error.value)
    assert runtime._cache == before

@pytest.mark.parametrize('kind',['Fixed','Revolute'])
@pytest.mark.parametrize('invalid',['translation','tilt','nan','infinity'])
def test_residual_rejects_nonfinite_and_outside_tolerances(kind,invalid):
    first, second = np.eye(4), np.eye(4)
    if invalid == 'translation':
        second[0,3] = .0101
    elif invalid == 'tilt':
        angle = math.radians(.0011)
        second[1:3,1:3] = [[math.cos(angle),-math.sin(angle)],
                           [math.sin(angle),math.cos(angle)]]
    else:
        second[0,3] = float('nan' if invalid == 'nan' else 'inf')
    with pytest.raises(ValueError) as error:
        worker.constraint_residual(kind,[first.tolist(),second.tolist()],
                                   'source.FCStd Joint endpoints Ground Moving')
    for text in ('source.FCStd','Joint','Ground','Moving',kind,'residual','direction_cosines','0.01mm','0.001deg'):
        assert text in str(error.value)

@pytest.mark.parametrize('kind',['Fixed','Revolute'])
def test_residual_accepts_measured_within_tolerance(kind):
    first, second = np.eye(4), np.eye(4)
    angle = math.radians(.0009)
    second[0,3] = .0099
    second[1:3,1:3] = [[math.cos(angle),-math.sin(angle)],
                       [math.sin(angle),math.cos(angle)]]
    residual = worker.constraint_residual(kind,[first.tolist(),second.tolist()],'native test')
    assert residual['distance_mm'] == pytest.approx(.0099,rel=0,abs=1e-12)
    assert residual['orientation_deg'] == pytest.approx(.0009,rel=0,abs=1e-12)

@pytest.mark.parametrize('old_recipe',[None,'pre-residual-provisional'])
def test_old_provisional_worker_response_is_not_certified_or_cached(monkeypatch,old_recipe):
    admitted = runtime.load_snapshot(FIXTURE)
    assert admitted['acceptance_recipe'] == worker.ACCEPTANCE_RECIPE
    assert all(key[-1] == worker.ACCEPTANCE_RECIPE for key in runtime._cache
               if key[0] == str(FIXTURE.resolve()) and len(key) == 4)
    # Even an earlier successful payload with matching geometry/files cannot
    # acquire the new acceptance certificate by falling back after failure.
    provisional = deepcopy(admitted)
    if old_recipe is None:
        provisional.pop('acceptance_recipe')
    else:
        provisional['acceptance_recipe'] = old_recipe
    before = dict(runtime._cache)
    invoke = runtime._invoke
    def old_response(root,source,mode,expected=()):
        if mode == 'resolve':
            return provisional
        return invoke(root,source,mode,expected)
    monkeypatch.setattr(runtime,'_invoke',old_response)
    with pytest.raises(runtime.NativeAssemblyError,match='acceptance recipe'):
        runtime.load_snapshot(FIXTURE)
    assert runtime._cache == before

def test_unknown_residual_convention_is_refused():
    with pytest.raises(ValueError,match='unknown native residual convention Slider'):
        worker.constraint_residual('Slider',[np.eye(4).tolist()]*2,'source Joint')

def test_pre_residual_cache_entry_cannot_admit_now_invalid_source(monkeypatch):
    source = FIXTURE.with_name('FixedQuarterTurn.FCStd')
    root, identity = runtime.runtime()
    # A historical three-component importer key/payload is deliberately seeded.
    old_key = (str(source.resolve()),identity,'pre-residual-worker')
    monkeypatch.setitem(runtime._cache,old_key,('old closure','old observations','old payload'))
    before = dict(runtime._cache)
    with pytest.raises(runtime.NativeAssemblyError,match='constraint residual'):
        runtime.load_snapshot(source)
    assert runtime._cache == before
