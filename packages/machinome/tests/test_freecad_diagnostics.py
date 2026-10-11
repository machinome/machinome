# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Refusal diagnostics; injected failures do not establish native parity."""
from copy import deepcopy

from tests.freecad_support import skip_without_runtime

skip_without_runtime()

import pytest

from machinome.node.freecad import FreeCADAssemblyNode
from machinome.node.freecad import adapter, runtime
from tests.test_freecad_public import FIXTURE

@pytest.fixture(scope='module')
def native_snapshot():
    return runtime.load_snapshot(FIXTURE)

@pytest.mark.parametrize('failure', ['duplicate','ground','endpoint','count','loop','disconnected'])
def test_adapter_graph_refusal_names_source_and_inventory(native_snapshot,monkeypatch,failure):
    snapshot = deepcopy(native_snapshot)
    if failure == 'duplicate':
        snapshot['joints'].append(deepcopy(snapshot['joints'][0]))
    elif failure == 'ground':
        snapshot['ground'] = 'MissingGround'
    elif failure == 'endpoint':
        snapshot['joints'][0]['endpoints'][1] = 'MissingOccurrence'
    elif failure == 'count':
        snapshot['joints'].pop()
    else:
        snapshot['joints'][0]['endpoints'] = ['Ground','Moving']
        snapshot['joints'][1]['endpoints'] = ['Ground','Moving']
        if failure == 'disconnected':
            snapshot['ground'] = 'FixedChild'
    monkeypatch.setattr(adapter,'load_snapshot',lambda unused:snapshot)
    class Invalid(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    with pytest.raises(runtime.NativeAssemblyError) as error:
        Invalid()
    message = str(error.value)
    for name in (str(FIXTURE),'Assembly','Ground','Moving','FixedChild','Joint001'):
        assert name in message

def test_native_unsupported_graph_refusal_has_context():
    class Invalid(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name('Disconnected.FCStd')
    with pytest.raises(runtime.NativeAssemblyError) as error:
        Invalid()
    for name in (str(Invalid.freecad_source),'Assembly','Disconnected','Joint001'):
        assert name in str(error.value)

def test_worker_solver_refusal_names_native_candidates(monkeypatch):
    # Exercise the actual worker refusal branch without replacing its solve
    # algorithm in production or inventing a native inconsistent fixture.
    import sys
    from types import SimpleNamespace
    from machinome.node.freecad import worker
    monkeypatch.setattr(sys,'path',sys.path[:])
    placement = object()
    occurrences = [SimpleNamespace(Name=name) for name in ('Ground','Moving')]
    group = SimpleNamespace(TypeId='Assembly::JointGroup',
                            Group=[SimpleNamespace(Name='Joint001')])
    assembly = SimpleNamespace(Name='Assembly',TypeId='Assembly::AssemblyObject',
                               OutList=[group],solve=lambda:7)
    document = SimpleNamespace(FileName=str(FIXTURE),Objects=[assembly],recompute=lambda:None)
    assembly.State = []
    monkeypatch.setitem(sys.modules,'FreeCAD',SimpleNamespace(
        Version=lambda:['1','1','4'],openDocument=lambda unused:document,
        listDocuments=lambda:{'NativeFixture':document}))
    monkeypatch.setitem(sys.modules,'Part',SimpleNamespace())
    monkeypatch.setitem(sys.modules,'UtilsAssembly',SimpleNamespace(
        getMovablePartsWithin=lambda unused:occurrences,
        getGlobalPlacement=lambda *unused:placement))
    with pytest.raises(ValueError) as error:
        worker.resolve({'source':str(FIXTURE),'runtime_root':'/unused',
                        'acceptance_recipe':worker.ACCEPTANCE_RECIPE,
                        'expected':{str(FIXTURE):worker.digest(FIXTURE)},'mode':'resolve'})
    message = str(error.value)
    for name in (str(FIXTURE),'Assembly','Ground','Moving','Joint001','status 7'):
        assert name in message
