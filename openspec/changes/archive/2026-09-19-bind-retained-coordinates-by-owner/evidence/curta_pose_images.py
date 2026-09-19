"""Capture actual Curta world meshes after retained requests and restore.

Run with the candidate framework first on PYTHONPATH. The project is an
explicit input; its source is imported unchanged. Generated meshes and images
belong in a temporary output directory, not in either source repository.
"""

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

import machinome
from machinome.core.builder import anchor_build_dir
from machinome.simulation import Sim


def rotation(degrees):
    angle = math.radians(degrees)
    return np.array(((math.cos(angle), -math.sin(angle), 0),
                     (math.sin(angle), math.cos(angle), 0), (0, 0, 1)))


def picture(rows, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    figure = plt.figure(figsize=(15, 11), layout='constrained')
    for row_index, (label, captures, titles) in enumerate(rows):
        points = np.concatenate([mesh.vertices for mesh in captures])
        low, high = points.min(axis=0), points.max(axis=0)
        center = (low + high) / 2
        radius = max(high - low) * .62
        # Track one material vertex so a symmetric ring's rotation is visible.
        marker_index = np.argmax(captures[0].vertices[:, 0])
        for column, (mesh, title) in enumerate(zip(captures, titles)):
            axes = figure.add_subplot(2, 3, row_index * 3 + column + 1,
                                      projection='3d')
            collection = Poly3DCollection(
                mesh.vertices[mesh.faces], facecolor=('#3983bc', '#dd9933')[row_index],
                edgecolor='none', alpha=1)
            axes.add_collection3d(collection)
            marker = mesh.vertices[marker_index]
            axes.scatter(*marker, color='#b71925', s=35, depthshade=False)
            axes.set(xlim=(center[0] - radius, center[0] + radius),
                     ylim=(center[1] - radius, center[1] + radius),
                     zlim=(center[2] - radius, center[2] + radius))
            axes.set_title(f'{label}\n{title}', fontsize=10)
            axes.set_xlabel('world X (mm)', fontsize=8)
            axes.set_ylabel('world Y (mm)', fontsize=8)
            axes.set_zlabel('world Z (mm)', fontsize=8)
            axes.tick_params(labelsize=7)
            axes.set_box_aspect((1, 1, 1))
            axes.set_proj_type('ortho')
            axes.view_init(elev=48, azim=-55)
    figure.suptitle('Operating Curta: actual world meshes after retained requests\n'
                   'Red marker tracks the same mesh vertex through each row',
                   fontsize=13)
    figure.savefig(output, dpi=135)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    build = output / 'build'
    anchor_build_dir(str(build), str(build))
    sys.path.insert(0, str(project))
    from simulation.running_motion import RunningMotionBench

    node = RunningMotionBench()
    sim = Sim(node, dt=.1, meshes=True)
    saved = sim.snapshot()
    dial = node.carriage.registers.result_register.p_10203_1.results_dial_type_1
    plate = node.carriage.registers.clearing_ring.clearing_cover
    dial_joint = node.carriage.registers.result_register.p_10203_1.turn
    dial_key = 'carriage.registers.result_register.p_10203_1.turn'
    ring_joint = node.carriage.registers.clearing_ring.turn
    ring_key = 'carriage.registers.clearing_ring.turn'
    dial_rest, plate_rest = dial.mesh.copy(), plate.mesh.copy()

    sim.move('carriage_elevation', to=6)
    sim.move('carriage_rotation', to=20)
    dial_shift = dial.mesh.copy()
    expected_dial = dial_rest.vertices @ rotation(20).T + (0, 0, 6)
    shift = {'bank': sim.state[dial_key], 'bound': dial_joint.value,
             'max_vertex_error_mm': float(np.max(np.abs(
                 dial_shift.vertices - expected_dial)))}
    sim.restore(saved)
    dial_restored = dial.mesh.copy()
    assert sim.snapshot() == saved

    sim.move('carriage_elevation', to=6)
    sim.move('clearing_rotation', by=90)
    plate_clear = plate.mesh.copy()
    expected_plate = plate_rest.vertices @ rotation(-90).T + (0, 0, 6)
    clear = {'bank': sim.state[ring_key], 'bound': ring_joint.value,
             'max_vertex_error_mm': float(np.max(np.abs(
                 plate_clear.vertices - expected_plate)))}
    sim.restore(saved)
    plate_restored = plate.mesh.copy()
    assert sim.snapshot() == saved

    report = {
        'framework_module': str(Path(machinome.__file__).resolve()),
        'project_head': subprocess.check_output(
            ['git', '-C', str(project), 'rev-parse', 'HEAD'], text=True).strip(),
        'carriage_shift': shift,
        'clearing': clear,
        'dial_restore_exact': bool(np.array_equal(
            dial_rest.vertices, dial_restored.vertices)),
        'plate_restore_exact': bool(np.array_equal(
            plate_rest.vertices, plate_restored.vertices)),
    }
    print(json.dumps(report, indent=2), flush=True)
    picture([
        ('Result dial', [dial_rest, dial_shift, dial_restored],
         ['Rest', 'Carriage lifted 6 mm and turned 20 degrees', 'Snapshot restored']),
        ('Clearing cover', [plate_rest, plate_clear, plate_restored],
         ['Rest', 'Carriage lifted 6 mm; clearing ring at -90 degrees', 'Snapshot restored']),
    ], output / 'curta-retained-poses.png')
    assert shift['bank'] == shift['bound']
    assert clear['bank'] == clear['bound']
    assert shift['max_vertex_error_mm'] < .00001
    assert clear['max_vertex_error_mm'] < .00001
    assert report['dial_restore_exact'] and report['plate_restore_exact']


if __name__ == '__main__':
    main()
