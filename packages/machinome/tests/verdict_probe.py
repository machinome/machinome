# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A child probe that counts what a `machinome test` process decided.

The default run's output may not change (ADR-073/090), so nothing in the
product announces a store hit. Proof across processes is by count instead:
this snippet, run as `python -c <PROBE> test <reference> ...`, wraps the
verdict memo, calls the real CLI, and writes one line of counts to stderr
at exit -- the technique of the measurement the change started from
(design.md §12). It adds no product surface.

For every computation it also records the two artifact names the key was
built from, so a test can say WHICH pairs a run recomputed.

`VERDICT_PROBE_KILL_AFTER_FLUSH`, when set, makes every queued record flush
at once and SIGKILLs the process right after its first segment is
published: a run killed while it keeps verdicts.
"""

import json
import re


PROBE = r'''
import json
import os
import signal
import sys

import machinome.test as _framework

_counts = dict(keyed_asks=0, inprocess_hits=0, computations=0,
               uncacheable=0, computed_pairs=[])
_memoized = _framework._memoized


def _name(identity):
    if isinstance(identity, tuple) and identity and isinstance(
            identity[0], str) and identity[0] != 'flexible':
        return os.path.basename(identity[0])
    return repr(identity[0]) if isinstance(identity, tuple) else None


def _counted(key, compute):
    if key is None:
        _counts['uncacheable'] += 1
        return compute()
    _counts['keyed_asks'] += 1
    if key in _framework._verdict_cache:
        _counts['inprocess_hits'] += 1

    def computed():
        _counts['computations'] += 1
        _counts['computed_pairs'].append([_name(key[0]), _name(key[1])])
        return compute()

    return _memoized(key, computed)


_framework._memoized = _counted

if os.environ.get('VERDICT_PROBE_KILL_AFTER_FLUSH'):
    from machinome import _verdict_store as _store
    _store.FLUSH_INTERVAL = 0.0
    _write = _store.write_segment

    def _write_then_die(*arguments, **keywords):
        written = _write(*arguments, **keywords)
        os.kill(os.getpid(), signal.SIGKILL)
        return written

    _store.write_segment = _write_then_die


def _report():
    store = sys.modules.get('machinome._verdict_store')
    _counts['store_hits'] = (None if store is None
                             else store.counters['served'])
    sys.stderr.write('VERDICT_PROBE ' + json.dumps(_counts) + '\n')


from machinome.cli import manage

try:
    manage()
finally:
    _report()
'''

_LINE = re.compile(r'^VERDICT_PROBE (?P<counts>\{.*\})$', re.MULTILINE)


def counts(stderr):
    """The counts a probed child reported, or an AssertionError naming
    what it printed instead."""
    found = _LINE.findall(stderr)
    if len(found) != 1:
        raise AssertionError(f'expected one probe line, found {len(found)}'
                             f'\nstderr:\n{stderr}')
    return json.loads(found[0])
