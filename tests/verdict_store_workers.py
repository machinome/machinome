# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Targets for the verdict store's multi-process tests.

They run in `multiprocessing` children started with the `spawn` context
(OCCT's thread pool does not survive `fork`), so they live in a module that
imports nothing but the store itself: a child re-imports its target's
module, and a child that imported the test module would pay for the whole
geometry stack only to write a few synthetic records. No CAD runs here.
"""

import hashlib
import os

from machinome import _verdict_store as store


def synthetic_records(seed, count, last_use=1000):
    """`count` records with keys derived from `seed`, never from time."""
    records = []
    for index in range(count):
        key = hashlib.sha256(f'{seed}:{index}'.encode()).digest()
        records.append((key, index % 2 == 0, float(index) / 7.0,
                        index % 3 == 0, last_use + index))
    return records


def write_behind_barrier(root, seed, flushes, per_flush, barrier):
    """One writer: wait for the others, then flush `flushes` segments."""
    writer = store.Store(root)
    barrier.wait()
    for flush in range(flushes):
        for key, is_empty, volume, exact, _ in synthetic_records(
                f'{seed}:{flush}', per_flush):
            writer.pending[key] = (is_empty, volume, exact, 1000 + flush)
        writer.flush()
        if writer.failed is not None:
            raise RuntimeError(f'writer {seed} failed: {writer.failed}')


def compact_behind_barrier(root, rounds, barrier):
    """One compactor: wait for the writers, then force `rounds` loads."""
    barrier.wait()
    for _ in range(rounds):
        compactor = store.Store(root)
        compactor.load(compact=True)
        if compactor.failed is not None:
            raise RuntimeError(f'compactor failed: {compactor.failed}')


def compact(root):
    """Force one compaction of the store under `root`."""
    compactor = store.Store(root)
    compactor.load(compact=True)
    if compactor.failed is not None:
        raise RuntimeError(f'compactor failed: {compactor.failed}')
    return sorted(os.listdir(compactor.directory))
