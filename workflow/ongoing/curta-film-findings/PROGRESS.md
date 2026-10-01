# Curta film findings — progress

Execution index of the bench `curta-findings`. Dates are 2026.

| when | what | where |
|---|---|---|
| 1 Oct | Bench `curta-findings` created from `main` 8a8a267 with `scripts/dev-env curta-findings setup` (slot 1); this plan written | this commit |
| 1 Oct | `sim-through-a-symlink` reviewed and merged (planning 707a8c8, implementation 6d49854, fast-forward): `AbstractBaseNode` resolves its source file where it enters the node, so a project reached through a symlinked `PYTHONPATH` builds under its own `_build`; build-pipeline spec gains the resolved-anchor rule and the symlink scenario; changelog (`docs/project/changelog.rst`, Unreleased), node-tree concept page and `docs/architecture.md` updated; no ADR (ADR-159 released). Red first in `tests/test_project_through_a_symlink.py` (2 failed on the unfixed bench, re-run by the orchestrator: 2 failed; on the cycle: 2 passed); whole suite 4178 passed, 4 skipped, 807 s (verdict store off in the suite's conftest); caller `Sim(ClockedCurta())` through the symlinked path constructs and builds in `/mnt/data/…/_build/simulation`, the same directory as from the real path (needs `python -P` to reproduce: a plain `python -c` imports through the resolved cwd). Orchestrator's note: the brief named `HISTORY.rst` for the changelog; the agent found the precedent and used `docs/project/changelog.rst`, which is right | this commit |
