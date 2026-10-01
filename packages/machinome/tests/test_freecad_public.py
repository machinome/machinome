"""Original synthetic adapter tests, LGPL-2.1-or-later."""
from pathlib import Path
import json
import os
import subprocess

import numpy as np

import pytest

from machinome.motion.ports import Time
from machinome.simulation import Driver, Sim
from machinome_freecad import FreeCADAssemblyNode, FreeCADJoint

FIXTURE = Path(__file__).parent / 'fixtures' / 'Assembly.FCStd'

class Machine(FreeCADAssemblyNode):
    freecad_source = FIXTURE
    time = Time.running()
    turntable = FreeCADJoint('Joint001')
    turn = Driver(default=0, unit='deg')
    turn.drives(turntable)

def test_literal_running_example():
    node = Machine()
    sim = Sim(node, dt=0.02)
    command = sim.move('turn', to=150, duration=1.0)
    sim.run(1.0)
    assert command.status == 'completed'
    assert node.turntable.value == pytest.approx(150)

def test_maximum_limit_only_variant():
    class Reduced(Machine):
        freecad_source = FIXTURE.with_name('Maximum120.FCStd')
    node = Reduced()
    sim = Sim(node, dt=0.02)
    command = sim.move('turn', to=150, duration=1.0)
    sim.run(1.0)
    assert command.status == 'blocked'
    assert node.turntable.value == pytest.approx(120)

def world_poses(node, parent=None, result=None):
    parent = np.eye(4) if parent is None else parent
    result = {} if result is None else result
    children = node.render()
    matrix = np.eye(4)
    for operation in node.operations:
        matrix = operation.matrix() @ matrix
    world = parent @ matrix
    result[node.name] = world
    if isinstance(children, (list, tuple)):
        for child in children:
            world_poses(child, world, result)
    return result

@pytest.mark.parametrize('filename,targets', [('Assembly.FCStd',[0,35,90,150]),
                                             ('Reversed.FCStd',[-90,-35,0,75]),
                                             ('Antiparallel.FCStd',[0,35,90,150]),
                                             ('FixedOppositeX.FCStd',[0,35,90,150]),
                                             ('FixedOppositeY.FCStd',[0,35,90,150]),
                                             ('FixedOppositeZ.FCStd',[0,35,90,150]),
                                             ('StaleConnectors.FCStd',[0,35,90,150]),
                                             ('Offsets.FCStd',[0,35,90,150])])
def test_native_solver_pose_parity(filename,targets,tmp_path):
    class Pose(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name(filename)
        time = Time.running()
        alias = FreeCADJoint('Joint001')
        command = Driver(default=targets[0], unit='deg')
        command.drives(alias)
    root = Path(os.environ['MACHINOME_FREECAD_ROOT'])
    output = tmp_path/'reference.json'
    env = dict(os.environ, PYTHONPATH=str(root/'usr/lib'))
    completed = subprocess.run([str(root/'AppRun'),'python',
        str(Path(__file__).with_name('native_reference.py')),
        str(Pose.freecad_source), json.dumps(targets),str(output)],
        env=env,text=True,capture_output=True)
    assert completed.returncode == 0, completed.stderr
    reference = json.loads(output.read_text())
    for target in targets:
        node = Pose()
        sim = Sim(node,dt=.1,state={'command':target})
        poses = world_poses(node)
        assert reference[str(target)]['_coordinate'] == pytest.approx(target, abs=1e-7)
        for name in ('Ground','Moving','FixedChild'):
            assert poses[name] == pytest.approx(np.array(reference[str(target)][name]), abs=1e-9,rel=0)

def test_no_relation_saved_default_and_independent_instances():
    class Rest(FreeCADAssemblyNode):
        freecad_source = FIXTURE
        time = Time.running()
        joint = FreeCADJoint('Joint001')
    first, second = Rest(), Rest()
    first.render()
    second.render()
    assert first.joint.value == pytest.approx(35)
    assert second.joint.value == pytest.approx(35)
    first.joint = 85
    first.render()
    second.render()
    assert first.joint is not second.joint
    assert second.joint.value == pytest.approx(35)
    sim = Sim(second,dt=.1)
    assert len([key for key in sim.state if key.endswith('.Joint001')]) == 1
    assert len(sim.state) == 1 # one physical coordinate; no alias slot

@pytest.mark.parametrize('name,kind',[('missing','missing'),('JointFixed','Fixed'),('Revolute','missing')])
def test_unused_aliases_validate_at_construction(name,kind):
    class Invalid(FreeCADAssemblyNode):
        freecad_source = FIXTURE
        unused = FreeCADJoint(name)
    with pytest.raises(ValueError,match=kind):
        Invalid()

def test_duplicate_alias_same_physical_endpoint():
    class Aliases(Machine):
        second = FreeCADJoint('Joint001')
    node = Aliases()
    assert node.turntable is node.second
    class Duplicate(Machine):
        second = FreeCADJoint('Joint001')
        extra = Driver(default=0,unit='deg')
        extra.drives(second)
    with pytest.raises(ValueError,match='bound|writer|driven|relation'):
        Sim(Duplicate(),dt=.1)

def test_foreign_reference_refused_without_native_load():
    with pytest.raises(TypeError,match='foreign'):
        class Foreign(FreeCADAssemblyNode):
            freecad_source = FIXTURE
            driver = Driver(default=0,unit='deg')
            driver.drives(Machine.turntable)

@pytest.mark.parametrize('filename,span', [('MaximumOnly.FCStd',(None,180)),
                                         ('MinimumOnly.FCStd',(0,None)),
                                         ('Disabled.FCStd',(None,None))])
def test_enabled_only_ranges(filename,span):
    class Limits(Machine):
        freecad_source = FIXTURE.with_name(filename)
    node = Limits()
    assert node.turntable.declaration.unit == 'deg'
    from machinome.motion.joints import declared_joints
    carrier = node.turntable.node
    joint = declared_joints(type(carrier))['Joint001']
    assert joint.arguments(carrier)[2] == span

def test_initial_request_outside_imported_bounds():
    with pytest.raises(ValueError,match='Joint001|180'):
        Sim(Machine(),dt=.1,state={'turn':181})

def test_source_declaration_origin_and_inheritance(monkeypatch,tmp_path):
    from origin_model import DeclaringModule
    class Relative(FreeCADAssemblyNode):
        freecad_source = 'fixtures/Assembly.FCStd'
    class Inherited(DeclaringModule):
        pass
    monkeypatch.chdir(tmp_path)
    assert len(Inherited().render()) == 1

def test_exact_geometry_transfer_and_fixed_leaf_occurrences():
    node = Machine()
    Sim(node,dt=.1)
    poses = world_poses(node)
    leaves = []
    def walk(current):
        children = current.render()
        if isinstance(children,(tuple,list)):
            for child in children:
                walk(child)
        else:
            leaves.append(current)
    walk(node)
    assert len(leaves) == 3
    assert all(leaf.exact for leaf in leaves)
    assert len({id(leaf) for leaf in leaves}) == 3
    assert len({leaf.uniq_id for leaf in leaves}) == 1
    for leaf in leaves:
        shape = leaf.render()
        assert shape.Volume() == pytest.approx(192,abs=1e-8)
        assert shape.BoundingBox().xmin == pytest.approx(0,abs=1e-8)

def test_optional_runtime(monkeypatch):
    monkeypatch.delenv('MACHINOME_FREECAD_ROOT',raising=False)
    class Lazy(FreeCADAssemblyNode):
        freecad_source = FIXTURE
        alias = FreeCADJoint('Joint001')
    with pytest.raises(ValueError,match='runtime required'):
        Lazy()

@pytest.mark.parametrize('filename', ['Suppressed','Unsupported',
                                    'MissingEdge','Disconnected','SecondGround','Loop'])
def test_native_refusals(filename):
    class Invalid(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name(filename+'.FCStd')
    with pytest.raises(ValueError):
        Invalid()

def test_distinct_same_named_native_products_and_repeated_occurrences():
    class Products(FreeCADAssemblyNode):
        freecad_source = FIXTURE.with_name('DistinctProducts.FCStd')
    node = Products()
    leaves = []
    def walk(current):
        rendered = current.render()
        if isinstance(rendered,(list,tuple)):
            for child in rendered:
                walk(child)
        else:
            leaves.append(current)
    walk(node)
    assert [leaf.render().Volume() for leaf in leaves] == pytest.approx([192,192,384])
    assert leaves[0].uniq_id == leaves[1].uniq_id
    assert leaves[2].uniq_id != leaves[0].uniq_id

def test_inclusive_boundary_completes():
    node = Machine()
    sim = Sim(node,dt=.02)
    command = sim.move('turn',to=180,duration=1)
    sim.run(1)
    assert command.status == 'completed'
    assert node.turntable.value == pytest.approx(180)
