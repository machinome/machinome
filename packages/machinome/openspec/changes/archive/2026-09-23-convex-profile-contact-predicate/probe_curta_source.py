"""Bounded source-profile Curta trial; NOT installed-print admission.

Run with this framework worktree before the project on PYTHONPATH, from the
Curta project root, passing the pinned exploratory native-plus-mesh JSONL.
The trial substitutes one pointwise angular flag inside the already-tested
single-crank local axial Bound. It never changes the production model.
"""

import argparse
from contextlib import ExitStack, nullcontext
import hashlib
import inspect
import json
import logging
from pathlib import Path
from time import process_time
import unittest
from unittest.mock import patch

from machinome.math import cos, max, min, sin
from machinome.motion.joints import Bound
from machinome.simulation.profile import ConvexProfile
from machinome.simulation import Sim
import machinome.simulation.profile as contact_module
import machinome.simulation.run as run_module

from simulation.reverser_contact_trial import contact_windows
from simulation.running import OperatingCurta
import simulation.test_reverser_contact_trial as existing
import simulation.test_running_reverser_wrong_order as contracts


AXIS = (-26.032898192, 31.024799946)
DRUM_REFERENCE = (-.016356142, .223394941)
ONE_CRANK = -90.0  # the local trial's internal crank coordinate


def _profiles(path):
    raw = path.read_bytes()
    reports = {row['part']: row for row in
               (json.loads(line) for line in raw.splitlines())}
    def value(part):
        row = reports[part]
        loops = [[row['points'][i] for i in polygon]
                 for polygon in row['polygons']]
        loops.extend(row['mesh_cover_polygons'])
        return ConvexProfile(loops)
    return value('FittedCounterPinion'), value('NineToothTurnsStepDrumSegment'), hashlib.sha256(raw).hexdigest()


def trial(pin, drum):
    def active(crank, shaft, lift):
        # Keep exactly the existing local trial's single-pose gate. The
        # predicate replaces only its temporary angular chart.
        gated = ((crank >= ONE_CRANK) * (crank <= ONE_CRANK) *
                 (lift >= 0.0) * (lift <= 0.0))
        x, y = DRUM_REFERENCE
        center = (cos(crank) * x - sin(crank) * y,
                  sin(crank) * x + cos(crank) * y)
        contact = contact_module.profile_overlap(
            pin, drum, shaft, 2.604082802 + crank,
            left_xy=AXIS, right_xy=center)
        return gated * contact

    def lower(own, crank, shaft, lift):
        contact = active(crank, shaft, lift)
        limit = -6.9425
        for low, high in contact_windows(lift):
            chosen = contact * (own >= (low + high) / 2)
            limit = max(limit, chosen * high + (1 - chosen) * -6.9425)
        return limit

    def upper(own, crank, shaft, lift):
        contact = active(crank, shaft, lift)
        limit = 3.9075
        for low, high in contact_windows(lift):
            chosen = contact * (own < (low + high) / 2)
            limit = min(limit, chosen * low + (1 - chosen) * 3.9075)
        return limit

    class SourceProfileContactTrial(OperatingCurta):
        def get_source_file(self):
            # The diagnostic class lives in framework evidence but its CAD
            # leaves live in the Curta project. Use the project trial's
            # manifest root; run with an isolated SOLID_BUILD_DIR so this
            # source-path adaptation cannot reuse production artifacts.
            return inspect.getfile(existing.LocalReverserContactTrial)

        OperatingCurta.main_drive.reversing_lever.reversing_lever_1.reversing_lever_knob_1.lift.constrain(
            range=(Bound(lower, reads=(
                OperatingCurta.main_drive.crank.turn,
                OperatingCurta.transmission.turns.ones.turn,
                OperatingCurta.main_drive.crank.lift)),
                   Bound(upper, reads=(
                OperatingCurta.main_drive.crank.turn,
                OperatingCurta.transmission.turns.ones.turn,
                OperatingCurta.main_drive.crank.lift))))

    return SourceProfileContactTrial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--uncached', action='store_true',
                        help='Diagnostic only: disable integration-local profile reuse')
    parser.add_argument('--instrument', action='store_true',
                        help='Diagnostic only: count profile and Sim phase work')
    args = parser.parse_args()
    logging.disable(logging.INFO)
    start = process_time()
    pin, drum, digest = _profiles(args.profiles)
    machine_class = trial(pin, drum)

    class BoundedProof(existing.LocalReverserContactTrialTest):
        model = machine_class

    class FreeHistory(contracts.RunningReverserWrongOrderTest):
        model = machine_class

    cases = (BoundedProof('test_long_request_cannot_cross_contact_into_a_later_clear_band'),
             FreeHistory('test_a_different_retained_phase_can_withdraw_from_the_same_crank_pose'))
    counters = dict(predicate_calls=0, in_scope_calls=0, placed_calls=0,
                    pair_inserts=0, placement_inserts=0, pair_evictions=0,
                    placement_evictions=0, sim_init_cpu=0.0,
                    move_cpu=0.0, run_cpu=0.0)
    keys = set()
    original_predicate = contact_module.profile_overlap
    original_placed = contact_module._placed
    original_key = contact_module._placement_key
    original_remember = contact_module._remember
    original_init, original_move, original_run = Sim.__init__, Sim.move, Sim.run

    def predicate(*args, **kwargs):
        counters['predicate_calls'] += 1
        if contact_module._INTEGRATION_CACHE.get() is not None:
            counters['in_scope_calls'] += 1
        return original_predicate(*args, **kwargs)

    def placed(*args, **kwargs):
        counters['placed_calls'] += 1
        return original_placed(*args, **kwargs)

    def key(*args, **kwargs):
        value = original_key(*args, **kwargs)
        if value is not None:
            keys.add(value)
        return value

    def remember(entries, cache_key, value, limit):
        name = 'pair' if limit == 1024 else 'placement'
        counters[name + '_inserts'] += 1
        if len(entries) == limit and cache_key not in entries:
            counters[name + '_evictions'] += 1
        return original_remember(entries, cache_key, value, limit)

    def timed(name, fn):
        def wrapped(*args, **kwargs):
            begun = process_time()
            try:
                return fn(*args, **kwargs)
            finally:
                counters[name + '_cpu'] += process_time() - begun
        return wrapped

    with ExitStack() as stack:
        if args.uncached:
            stack.enter_context(patch.object(run_module, '_profile_integration_cache',
                                             nullcontext))
        if args.instrument:
            stack.enter_context(patch.object(contact_module, 'profile_overlap', predicate))
            stack.enter_context(patch.object(contact_module, '_placed', placed))
            stack.enter_context(patch.object(contact_module, '_placement_key', key))
            stack.enter_context(patch.object(contact_module, '_remember', remember))
            stack.enter_context(patch.object(Sim, '__init__', timed('sim_init', original_init)))
            stack.enter_context(patch.object(Sim, 'move', timed('move', original_move)))
            stack.enter_context(patch.object(Sim, 'run', timed('run', original_run)))
        results = []
        per_case = []
        for case in cases:
            begun = process_time()
            result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite((case,)))
            results.append(result)
            per_case.append(dict(test=case._testMethodName,
                                 cpu_seconds=process_time() - begun,
                                 successful=result.wasSuccessful()))
    report = dict(profile_sha256=digest, tests=sum(r.testsRun for r in results),
                  failures=sum(len(r.failures) for r in results),
                  errors=sum(len(r.errors) for r in results),
                  cpu_seconds=process_time() - start,
                  scope='Source-placed profiles, single crank/lift pose; not installed-print or full operating adoption',
                  uncached=args.uncached, per_case=per_case)
    if args.instrument:
        report.update(counters)
        report['unique_placement_keys'] = len(keys)
    print(json.dumps(report, sort_keys=True))
    if not all(result.wasSuccessful() for result in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
