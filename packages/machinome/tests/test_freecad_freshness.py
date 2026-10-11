# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Native source replacement and exact-artifact currency regression tests."""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import shutil
import importlib.util
import sys

from tests.freecad_support import skip_without_runtime

skip_without_runtime()

import cadquery as cq
import numpy as np
import pytest

from machinome.source_generation import SourceChanged, SourceGeneration
from machinome.node.freecad import FreeCADAssemblyNode
from machinome.node.freecad import runtime
from tests.test_freecad_public import FIXTURE, Machine

def copied(tmp_path):
    source = tmp_path/'Assembly.FCStd'
    shutil.copyfile(FIXTURE,source)
    shutil.copyfile(FIXTURE.with_name('Parts.FCStd'),tmp_path/'Parts.FCStd')
    return source

def test_native_limit_only_replacement_has_equal_solids_and_saved_poses(tmp_path):
    source = copied(tmp_path)
    first = runtime.load_snapshot(source)
    shutil.copyfile(FIXTURE.with_name('Maximum120.FCStd'),source)
    second = runtime.load_snapshot(source)
    assert first['joints'][0]['range'] == [0,180]
    assert second['joints'][0]['range'] == [0,120]
    for a,b in zip(first['occurrences'],second['occurrences']):
        assert a['volume'] == pytest.approx(b['volume'],abs=1e-9,rel=0)
        assert np.asarray(a['world']) == pytest.approx(np.asarray(b['world']),abs=1e-9,rel=0)

def test_old_linked_timestamp_and_missing_document_invalidate(tmp_path):
    source = copied(tmp_path)
    os.utime(source,ns=(2_000_000_000_000_000_000,)*2)
    first = runtime.load_snapshot(source)
    parts = tmp_path/'Parts.FCStd'
    previous = parts.stat()
    # A real native geometry edit below the future-dated root timestamp.
    replacement = tmp_path/'replacement.FCStd'
    shutil.copyfile(FIXTURE.with_name('PartsTall.FCStd'),replacement)
    # FCStd ZIP permits harmless trailing bytes: equalize size to reproduce
    # a same-size content replacement without touching production parsing.
    size = max(parts.stat().st_size, replacement.stat().st_size)
    for path in (parts,replacement):
        with path.open('ab') as stream:
            stream.write(b'\0' * (size-path.stat().st_size))
    before_replace = runtime.load_snapshot(source)
    assert before_replace['occurrences'][0]['volume'] == pytest.approx(192)
    os.replace(replacement,parts)
    os.utime(parts,ns=(previous.st_atime_ns,previous.st_mtime_ns))
    second = runtime.load_snapshot(source)
    assert second['occurrences'][0]['volume'] == pytest.approx(384)
    parts.unlink()
    with pytest.raises(runtime.NativeAssemblyError):
        runtime.load_snapshot(source)

def test_symlink_relink_is_discovered_natively(tmp_path):
    source = copied(tmp_path)
    parts = tmp_path/'Parts.FCStd'
    target1 = tmp_path/'PartOne.FCStd'
    target2 = tmp_path/'PartTwo.FCStd'
    parts.rename(target1)
    shutil.copyfile(target1,target2)
    parts.symlink_to(target1.name)
    first = runtime.load_snapshot(source)
    parts.unlink()
    parts.symlink_to(target2.name)
    second = runtime.load_snapshot(source)
    assert str(parts) in first['files']
    assert str(parts) in second['files']
    assert first['occurrences'][0]['document'] == str(target1)
    assert second['occurrences'][0]['document'] == str(target2)

def test_changed_during_native_resolution_caches_no_success(tmp_path,monkeypatch):
    source = copied(tmp_path)
    initial_keys = set(runtime._cache)
    invoke = runtime._invoke
    def change(root,path,mode,expected=()):
        result = invoke(root,path,mode,expected)
        if mode == 'resolve':
            shutil.copyfile(FIXTURE.with_name('Maximum120.FCStd'),source)
        return result
    monkeypatch.setattr(runtime,'_invoke',change)
    with pytest.raises(SourceChanged):
        runtime.load_snapshot(source)
    assert set(runtime._cache) == initial_keys

def test_worker_failure_caches_no_success(tmp_path,monkeypatch):
    source = copied(tmp_path)
    keys = set(runtime._cache)
    invoke = runtime._invoke
    def fail(root,path,mode,expected=()):
        if mode == 'resolve':
            raise runtime.NativeAssemblyError('injected native failure')
        return invoke(root,path,mode,expected)
    monkeypatch.setattr(runtime,'_invoke',fail)
    with pytest.raises(ValueError,match='injected'):
        runtime.load_snapshot(source)
    assert set(runtime._cache) == keys

def solid(node):
    children = node.render()
    if isinstance(children,(list,tuple)):
        for child in children:
            found = solid(child)
            if found:
                return found
    else:
        return node

def test_native_recipe_refreshes_existing_exact_artifacts(monkeypatch):
    import machinome.node.freecad.adapter as adapter
    class Currency(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    first = Currency()
    leaf = solid(first)
    leaf.materialize(leaf.render())
    assert cq.Shape.cast(leaf.shape()).Volume() == pytest.approx(192)
    identity = leaf.uniq_id
    load = adapter.load_snapshot
    def modified(source):
        snapshot = load(source)
        shape = cq.Workplane('XY').box(4,6,16).val()
        import io
        stream = io.BytesIO()
        shape.exportBrep(stream)
        for occurrence in snapshot['occurrences']:
            occurrence['brep'] = stream.getvalue().decode()
        snapshot['runtime_identity'] = ['changed native recipe']
        return snapshot
    monkeypatch.setattr(adapter,'load_snapshot',modified)
    second = Currency()
    updated = solid(second)
    assert updated.uniq_id == identity
    assert not updated._up_to_date(updated.brep_file)
    assert cq.Shape.cast(updated.shape()).Volume() == pytest.approx(384)
    updated.materialize(updated.render())
    assert updated._up_to_date(updated.brep_file)
    assert cq.Shape.cast(updated.shape()).Volume() == pytest.approx(384)

def test_acceptance_recipe_alone_invalidates_existing_artifact_currency(monkeypatch):
    import machinome.node.freecad.adapter as adapter
    class Recipe(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    first = Recipe()
    leaf = solid(first)
    leaf.materialize(leaf.render())
    assert leaf._up_to_date(leaf.brep_file)
    old_recipe = first._native_recipe
    load = adapter.load_snapshot
    def revised(source):
        snapshot = load(source)
        snapshot['acceptance_recipe'] += '-test-next'
        return snapshot
    monkeypatch.setattr(adapter,'load_snapshot',revised)
    second = Recipe()
    fresh = solid(second)
    assert fresh.uniq_id == leaf.uniq_id
    assert second._native_recipe != old_recipe
    assert not fresh._up_to_date(fresh.brep_file)
    fresh.materialize(fresh.render())
    assert fresh._up_to_date(fresh.brep_file)
    assert cq.Shape.cast(fresh.shape()).Volume() == pytest.approx(192)

def test_old_rendered_node_refuses_materialization_after_source_change(tmp_path,monkeypatch):
    import machinome.node.freecad.adapter as adapter
    source = copied(tmp_path)
    # Isolate generation behavior from project-source containment; the public
    # class remains ordinary and owns a genuine native resolved snapshot.
    load = adapter.load_snapshot
    monkeypatch.setattr(adapter,'load_snapshot',lambda unused:load(source))
    class Guard(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    node = Guard()
    leaf = solid(node)
    leaf.render()
    shutil.copyfile(FIXTURE.with_name('Maximum120.FCStd'),source)
    with pytest.raises(SourceChanged):
        leaf.materialize(leaf.render())

def test_complete_closure_joins_core_generation(tmp_path):
    source = copied(tmp_path)
    with SourceGeneration(tmp_path) as generation:
        snapshot = runtime.load_snapshot(source)
        assert {str(Path(p).resolve()) for p in snapshot['files']} <= {o.path for o in generation.observations}

def test_invalid_ranges_are_refused_after_native_resolution(monkeypatch):
    import machinome.node.freecad.adapter as adapter
    load = adapter.load_snapshot
    def bad(source):
        snapshot = load(source)
        snapshot['joints'][0]['range'] = [180,120]
        return snapshot
    monkeypatch.setattr(adapter,'load_snapshot',bad)
    with pytest.raises(ValueError,match='range|lower|upper'):
        Machine()

@pytest.mark.parametrize('prior',[False,True])
@pytest.mark.parametrize('mutation',['replace','delete'])
def test_publication_source_race_publishes_no_artifact(tmp_path,monkeypatch,prior,mutation):
    import machinome.node.freecad.adapter as adapter
    from machinome import currency
    source = copied(tmp_path)
    load = adapter.load_snapshot
    monkeypatch.setattr(adapter,'load_snapshot',lambda unused:load(source))
    class Race(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    node = Race()
    leaf = solid(node)
    rendered = leaf.render()
    paths = (leaf.brep_file,leaf.stl_file,currency.sidecar(leaf.brep_file),currency.sidecar(leaf.stl_file))
    if prior:
        leaf.materialize(rendered)
        # A new native recipe must replace genuine current prior output, not
        # skip the writer and accidentally test only an up-to-date cache hit.
        def new_recipe(unused):
            snapshot = load(source)
            snapshot['runtime_identity'] = ['new publication recipe']
            return snapshot
        monkeypatch.setattr(adapter,'load_snapshot',new_recipe)
        leaf = solid(Race())
        rendered = leaf.render()
        assert not leaf._up_to_date(leaf.brep_file)
    else:
        # These four paths are exclusively this test leaf's generated output.
        for path in paths:
            Path(path).unlink(missing_ok=True)
    publish = currency.publish
    def changed(temporary,path,*args,**kwargs):
        if mutation == 'delete':
            source.unlink(missing_ok=True)
        else:
            shutil.copyfile(FIXTURE.with_name('Maximum120.FCStd'),source)
        return publish(temporary,path,*args,**kwargs)
    monkeypatch.setattr(currency,'publish',changed)
    before = {p:Path(p).read_bytes() if Path(p).is_file() else None for p in paths}
    with SourceGeneration(tmp_path) as generation:
        with pytest.raises(SourceChanged):
            with generation.phase(leaf.files,label='native publication race'):
                leaf.materialize(rendered)
    for path, payload in before.items():
        assert (Path(path).read_bytes() if Path(path).is_file() else None) == payload

def test_relinked_spelling_after_first_render_is_refused(tmp_path,monkeypatch):
    import machinome.node.freecad.adapter as adapter
    source = copied(tmp_path)
    parts = tmp_path/'Parts.FCStd'
    target1, target2 = tmp_path/'One.FCStd',tmp_path/'Two.FCStd'
    parts.rename(target1)
    shutil.copyfile(target1,target2)
    parts.symlink_to(target1.name)
    load = adapter.load_snapshot
    monkeypatch.setattr(adapter,'load_snapshot',lambda unused:load(source))
    class Relink(FreeCADAssemblyNode):
        freecad_source = FIXTURE
    node = Relink()
    leaf = solid(node)
    leaf.render()
    parts.unlink()
    parts.symlink_to(target2.name)
    with pytest.raises(SourceChanged):
        leaf.materialize(leaf.render())

def test_native_snapshot_reuse_never_shares_mutable_state(tmp_path):
    source = copied(tmp_path)
    first = runtime.load_snapshot(source)
    first['joints'][0]['range'][1] = 12
    second = runtime.load_snapshot(source)
    assert second['joints'][0]['range'][1] == 180

def test_source_change_after_snapshot_return_is_not_recertified(tmp_path,monkeypatch):
    import machinome.node.freecad.adapter as adapter
    source = copied(tmp_path)
    load = adapter.load_snapshot
    def changed(unused):
        snapshot = load(source)
        shutil.copyfile(FIXTURE.with_name('Maximum120.FCStd'),source)
        return snapshot
    monkeypatch.setattr(adapter,'load_snapshot',changed)
    with pytest.raises(SourceChanged):
        Machine()

def test_sibling_linked_document_and_source_preserving_relocation(tmp_path):
    identities = []
    for index in range(2):
        root = tmp_path/str(index)
        (root/'assembly-dir').mkdir(parents=True)
        shutil.copyfile(FIXTURE.parent/'assembly-dir'/'Assembly.FCStd',
                        root/'assembly-dir'/'Assembly.FCStd')
        shutil.copyfile(FIXTURE.with_name('Parts.FCStd'),root/'Parts.FCStd')
        (root/'pyproject.toml').write_text('[tool.machinome]\nmodel="model:Relocated"\n')
        source = root/'model.py'
        source.write_text('from machinome.node.freecad import FreeCADAssemblyNode\n'
                          'class Relocated(FreeCADAssemblyNode):\n'
                          '    freecad_source="assembly-dir/Assembly.FCStd"\n')
        name = f'freecad_relocated_{index}'
        spec = importlib.util.spec_from_file_location(name,source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
            leaf = solid(module.Relocated())
            assert cq.Shape.cast(leaf.render()).Volume() == pytest.approx(192)
            identities.append(leaf.uniq_id)
        finally:
            sys.modules.pop(name,None)
    assert identities[0] == identities[1]
