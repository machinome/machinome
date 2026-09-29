# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

# The fixture projects contain test_*.py files written for the solid
# runner, some of them deliberately failing. They must only ever run
# inside the subprocess tests/test_meta.py spawns — never be collected
# by pytest itself. The vet fixture projects (tests/vet_projects/) are
# read by `machinome vet` as bytes and never imported or run at all.
collect_ignore = ['meta_project', 'vet_projects']

# The verdict store (ADR-156) is on by default and keeps verdicts under a
# project's build root between runs. The framework's own suite runs with it
# OFF: `tests/base.py` and the meta-tests use one absolute build directory
# across runs, and the boolean-counting tests (test_intersection_memo.py,
# test_flexible_cache_performance.py, test_exact_placement_cache.py,
# test_broad_phase_culling.py) would otherwise be served one another's
# verdicts. The environment pin reaches every `machinome test` subprocess;
# suspending the store in this process also covers the policies tests
# construct positionally, whose fourth field defaults on. The store's own
# tests switch it on explicitly, on a temporary build root.
import os  # noqa: E402

from machinome import _verdict_store  # noqa: E402

os.environ['SOLID_TEST_VERDICT_STORE'] = 'off'
_verdict_store._suspended = True
