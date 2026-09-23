"""Project-origin control: reuse native drums without editing Curta source.

Run from the Curta project with the selected framework worktree first on
PYTHONPATH. `--limit 2` reaches the original failing midpoint; the default
checks all ten world64-seeded transitions at crank 173, height -3. This
reconstructs the *uncommitted* native-cache trial from a committed fresh-
native reader and makes no claim to recover that trial's source bytes.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import struct
import time

from OCP.BRep import BRep_Tool

from simulation.tools import refine_reverser_native as refine
from simulation.tools import reverser_tooth_envelope as envelope
from simulation.tools.reverser_tooth_envelope import DRUMS


def input_fingerprint(shape):
    """Hash topology counts, all vertex coordinates and subshape tolerances."""
    vertices, edges, faces = shape.Vertices(), shape.Edges(), shape.Faces()
    digest = hashlib.sha256()
    for count in (len(vertices), len(edges), len(faces)):
        digest.update(struct.pack('!I', count))
    for vertex in vertices:
        for coordinate in vertex.toTuple():
            digest.update(struct.pack('!d', coordinate))
        digest.update(struct.pack('!d', BRep_Tool.Tolerance_s(vertex.wrapped)))
    for items in (edges, faces):
        for item in items:
            digest.update(struct.pack('!d', BRep_Tool.Tolerance_s(item.wrapped)))
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--baseline', type=Path,
                        help='Compare every native boundary endpoint exactly')
    parser.add_argument('--copy-operands', action='store_true',
                        help='Test private deep copies with default destructive kernel')
    parser.add_argument('--single-169', action='store_true',
                        help='Check the fresh-input pose invalid only in protected mode')
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_bytes().splitlines()]
    row = next(row for row in rows if row['station'] == 1 and
               row['crank'] == 173 and row['height'] == -3)
    row = dict(row, boundaries=row['boundaries'][:args.limit])

    if args.copy_operands:
        original_intersect = envelope.intersect_shapes

        def copied_intersect(first, second, first_name, second_name):
            return original_intersect(first.copy(), second.copy(),
                                      first_name, second_name)

        envelope.intersect_shapes = copied_intersect

    setup_start = time.process_time()
    refine.setup_reader(1)
    setup_cpu = time.process_time() - setup_start
    reader = refine._reader
    if args.single_169:
        posed = reader.posed(169.0, 150.7459411621095, -3.0, 0,
                            kernel='native')
        results = {}
        for name in DRUMS:
            common = envelope.intersect_shapes(posed[reader.gear], posed[name],
                                                reader.gear, name)
            results[name] = dict(valid=common.isValid(),
                                 solids=len(common.Solids()),
                                 volume_mm3=common.Volume())
        top, bottom = (results[name] for name in DRUMS)
        print(json.dumps(dict(
            project=subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                            text=True).strip(),
            reader_sha256=hashlib.sha256(Path(
                'simulation/tools/reverser_tooth_envelope.py'
            ).read_bytes()).hexdigest(),
            copy_operands=args.copy_operands,
            pose=dict(crank=169.0, shaft=150.7459411621095,
                      height=-3.0, lift=0), results=results,
            expected_default_result=(top['valid'] and top['solids'] == 2 and
                                     top['volume_mm3'] == 4.241072983936974e-09
                                     and bottom['valid'] and
                                     bottom['volume_mm3'] == 0))))
        if not (top['valid'] and top['solids'] == 2 and
                top['volume_mm3'] == 4.241072983936974e-09 and
                bottom['valid'] and bottom['volume_mm3'] == 0):
            raise SystemExit(2)
        return
    fresh_pose = reader.posed
    drums = {}
    pending = {}
    mutations = []

    def reused_pose(crank, shaft, height, lift=0, *, kernel='world64'):
        posed = fresh_pose(crank, shaft, height, lift, kernel=kernel)
        if kernel != 'native':
            return posed
        key = crank, lift
        if key not in drums:
            drums[key] = {name: posed[name] for name in DRUMS}
        operands = {reader.gear: posed[reader.gear], **drums[key]}
        pending.clear()
        pending.update((name, (shape, input_fingerprint(shape)))
                       for name, shape in operands.items())
        return operands

    reader.posed = reused_pose
    native_volume = reader.volumes
    last = {}
    calls = 0

    def counted(crank, shaft, height, lift=0, *, kernel='world64'):
        nonlocal calls
        calls += 1
        last.update(crank=crank, shaft=shaft, height=height, lift=lift,
                    kernel=kernel)
        try:
            return native_volume(crank, shaft, height, lift, kernel=kernel)
        finally:
            for name, (shape, before) in pending.items():
                after = input_fingerprint(shape)
                if after != before:
                    mutations.append(dict(call=calls, operand=name,
                                          before=before, after=after))
            pending.clear()

    reader.volumes = counted
    common = dict(project=subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                   text=True).strip(),
                  copy_operands=args.copy_operands,
                  reader_sha256=hashlib.sha256(Path(
                      'simulation/tools/reverser_tooth_envelope.py'
                  ).read_bytes()).hexdigest(),
                  input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  rows=len(row['boundaries']))
    try:
        refine_start = time.process_time()
        result = refine.refine_row(row)
    except Exception as error:
        print(json.dumps(dict(common, status='refused', calls=calls,
                              last=last, input_mutations=mutations,
                              error=f'{type(error).__name__}: {error}')))
        raise SystemExit(1) from None
    boundaries = [dict(left=one['left'], right=one['right'])
                  for one in result['boundaries']]
    report = dict(common, status='complete', calls=calls,
                  input_mutations=mutations,
                  setup_cpu_seconds=setup_cpu,
                  refine_cpu_seconds=time.process_time()-refine_start,
                  boundaries_sha256=hashlib.sha256(json.dumps(
                      boundaries, sort_keys=True).encode()).hexdigest())
    if args.baseline is not None:
        records = [json.loads(line) for line in args.baseline.read_bytes().splitlines()]
        baseline = next(record for record in records if record['station'] == 1
                        and record['crank'] == 173 and record['height'] == -3)
        expected = [dict(left=one['left'], right=one['right'])
                    for one in baseline['boundaries'][:args.limit]]
        report['fresh_native_exact_match'] = boundaries == expected
        report['boundary_classification_match'] = all(
            actual[side]['shaft'] == reference[side]['shaft'] and
            actual[side]['contact'] == reference[side]['contact'] and
            all((actual[side]['volumes_mm3'][name] > 0) ==
                (reference[side]['volumes_mm3'][name] > 0) for name in DRUMS)
            for actual, reference in zip(boundaries, expected)
            for side in ('left', 'right'))
        report['fresh_native_sha256'] = hashlib.sha256(json.dumps(
            expected, sort_keys=True).encode()).hexdigest()
        if not report['fresh_native_exact_match']:
            report['differences'] = [
                dict(index=index, side=side,
                     shaft=(actual[side]['shaft'], reference[side]['shaft']),
                     contact=(actual[side]['contact'], reference[side]['contact']),
                     top_volume=(actual[side]['volumes_mm3'][DRUMS[0]],
                                 reference[side]['volumes_mm3'][DRUMS[0]]))
                for index, (actual, reference) in enumerate(zip(boundaries, expected))
                for side in ('left', 'right') if actual[side] != reference[side]
            ]
        print(json.dumps(report))
        if not report['boundary_classification_match'] or mutations:
            raise SystemExit(2)
    else:
        print(json.dumps(dict(report, boundaries=boundaries)))


if __name__ == '__main__':
    main()
