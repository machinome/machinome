# Originating evidence — 2026-09-21

Status: reproduced failure and read-only source inspection; no fix applied.

Originating independent project: `projects/Calculators/Curta-Type-I-3x`,
`simulation.result_bank_operating_trial:ResultBankOperatingTrial`.
Project commit `50f0726` records the mount failure in
`simulation/docs/evidence/result-bank-browser-mount-2026-09-21.json`
and its reproducer `simulation/tools/result_bank_operating_browser.py`.
This is the real nine-channel remaining-result-bank restraint trial, not
a hypothetical large model: 213 coordinates, 24 inputs and 25 controls.

| Identity | Value |
| --- | --- |
| Viewer commit | `1995aa1f58d44dfeea7bfa62502d71349891327a` |
| Bundle SHA-256 | `5f3ec29aede4934106bb0cbbdaa7454dcec39d2ba04a233f431a4ce279fef610` |
| Framework commit | `e6a42c80e6dcc686c180b8a6d94037301c4213a5` |
| Export SHA-256 | `c545d8807846ec9c8ba404bc253e39e0b98418b50062e49ce006ef25313a5884` |
| Program identity | `c693fd960131c22da87b2afb9111536a04bb344ea50d18719234536d7377f24c` |

From the project repository, using the workspace Python environment and
the pinned framework on PYTHONPATH, run:

```sh
python -m simulation.tools.result_bank_operating_browser --build _build_result_bank_trial
```

The build directory is a project-local generated artifact, not committed
viewer fixture data. The reproducer serves its assets through intercepted
`http://result-bank.test/` requests and uses public `MachinomeViewer.mount`,
with autoplay disabled. Run Chromium without a process virtual-memory cap.

The unmodified bundle fails before the first request or screenshot:
`TypeError: Cannot read properties of undefined (reading 'kind')` in
expression shape classification. Completed requests: zero. This is not an
accepted browser result and says nothing about mechanism parity yet.

Read-only diagnostic instrumentation of the loaded bundle string records:

- generation before expression preparation: 1; after: 1;
- expression root: 7742; pool size: 16,573;
- after binding roots: generation 2; pool size: 23,478;
- bindings: 30,159; index 7742 exists in the new pool, which does NOT
  establish that it still denotes the original expression.

No package file, cache limit or expression was modified by that diagnostic.
It intentionally stops on the generation change and proves no successful
mount. The committed project record pins its script and log hashes, plus
the original failure report and log hashes.

Source inspection at the viewer commit corroborates the mechanism:
`expressions.ts:prepare` may reset before a new expression;
`bindings.ts:roots` can cross that boundary while building its map;
`run/program.ts:classify` obtains its root before asking for the map.
Existing generation tests exercise one binding and a reset between calls,
not this within-operation case. Other retained-reference hazards are an
audit obligation in the plan, not additional reproduced failures.

The framework Python profile is separate evidence for a separate task.
This viewer proposal contains no Python performance change or speedup claim.
