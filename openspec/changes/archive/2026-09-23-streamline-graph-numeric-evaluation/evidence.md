# Originating Curta scalar-evaluator evidence

This is a local, unmeshed `Sim(make_trial(evidence)(), dt=.1, meshes=False)` request of `crank_rotation` to 18° over 0.1 seconds. It exercises the unchanged installed reverser profile trial, not an adopted reverser predicate or a complete Curta arithmetic operation. The test uses one pinned CPU (12), `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `SOLID_BUILD_DIR=/tmp/curta_graph_actual_build`. Setup happens before the timed `sim.run(.1)`; timings are process CPU seconds for that run, not wall time. Other users of the host are not controlled.

Inputs and code:

- Framework base: `8d0fd156787f5136174fb752be78451ce172bce8`; candidate branch base is the same commit plus the uncommitted narrow `scad_expression.py` loop edit, whose tested file SHA-256 is `60cf3d89c76f8825852372fdd58e7ad97b794c8cfa79d527a6b3e213961e3887`. No project source was edited by this cycle.
- Project trial source `simulation/tools/reverser_installed_trial.py`: SHA-256 `7072a3fc2a9811b9cee375d224b5e6a96eedfde22ec3485710c16d02126021bb`. Reference `_build_checks/reverser-installed-profile-reference-a428dea.jsonl`: SHA-256 `d41e1b46ee7f4c92b61d2ddae586f01242574213942d7dd93f0e9c4aefad01a3`.
- Process-local diagnostic script `/tmp/curta_graph_scalar_codegen_probe.py`: SHA-256 `c65ad50f56567b5f9c23703d0e535760fd3ba0607aa908de31799b03fbe63638`. For the final real-source comparison, no `SCALAR_*` switch is set; the script only wraps the imported `GraphValue.evaluate` to digest ordered returned IEEE-754 bits. The framework source root is selected by the first `PYTHONPATH` entry.
- Command shape: `taskset -c 12 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 SOLID_BUILD_DIR=/tmp/curta_graph_actual_build PYTHONPATH=<framework-root>:<Curta-project-root> /home/asa/devel/machinome-studio/.venv/bin/python /tmp/curta_graph_scalar_codegen_probe.py`, alternating `<framework-root>` between primary `machinome` and `machinome/WTs/streamline-graph-numeric-evaluation`.

The following values are transcribed from six terminal JSON results (not machine-captured log files), in run order. The JSON `candidate` field belongs to the diagnostic's *process-local override* switch and remains false in both base and changed-source runs; `mode` below identifies the source actually imported.

| Run | Mode | CPU seconds | Ordered GraphValue result SHA-256 | Full 214-bank bit SHA-256 | Calls | Status |
| --- | --- | ---: | --- | --- | ---: | --- |
| 1 | base | 8.843663232 | `22dd70b636d6d3fe77dcb92df4d3ddd063f3c23570e34c3e456f1f0c1d9fda32` | `3e44081383251e2e2c12b91a58f03336ff887a465e840b8a26d88788d686983d` | 439729 | completed |
| 2 | candidate | 7.740824495 | same | same | 439729 | completed |
| 3 | base | 8.292269645 | same | same | 439729 | completed |
| 4 | candidate | 8.500541659 | same | same | 439729 | completed |
| 5 | base | 8.843014387 | same | same | 439729 | completed |
| 6 | candidate | 8.481217924 | same | same | 439729 | completed |

The three paired differences (base minus candidate) are +1.102839, −0.208272 and +0.361796 CPU seconds. Median source-level times are 8.843014 base and 8.481218 candidate, a 0.361796-second or 4.1% saving; one pair is negative under host variance. The earlier process-local direct-dispatch prototype, with an unchanged live per-call operator map, measured 8.907→7.829, 8.558→7.827 and 8.958→8.339 seconds (median paired saving 0.731 seconds) and the same ordered/bank hashes. Generated straight-line evaluator compilation was slower and is not included in the implementation.

The request completed, so no stop was issued. This evidence supports a modest interpreter-cost improvement on this originating path, not real-time operation or a contact-law change. The viewer has a separate JavaScript evaluator and was not modified or benchmarked by this cycle.
