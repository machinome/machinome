## Red first

The two new focused checks were run against the unchanged 96% panel:

- `src/inspector.test.ts`: **1 failed, 20 passed** — the inspector stylesheet
  carried no suppression rule for its duplicate chrome controls.
- `CalculatorInABrowserTest::test_the_inspector_keeps_clocked_controls_in_a_side_rail`:
  **failed** with all four fixture descendant buttons visible. The previously
  captured originating Curta at 1440×900 showed the clocked panel covering 96%
  of the viewer pane, with seventeen `result_*` / `turns_*` buttons across its
  top and Reset at its foot.

The worktree initially lacked ignored `node_modules` and `dist/`; `npm ci`
from the committed lock and `npm run build` made that bench complete. No source
or assertion was changed to accommodate the environment.

## Green focused proof

- `npx vitest run src/inspector.test.ts`: **21 passed**.
- `pytest -q tests/test_calculator_document.py::CalculatorInABrowserTest::test_the_inspector_keeps_clocked_controls_in_a_side_rail`:
  **1 passed**.

The browser assertion proves both contexts: in the inspector no descendant
button or separator is displayed and Reset is absent, while a real input, a
real instruction and `machine().reset()` remain; after remounting the same
document with plain `mount()`, both a descendant button and Reset are visible.

## Originating Curta visual proof

Served from this worktree against
`projects/Calculators/Curta-Type-I-3x/_build/clocked_curta` at 1440×900:

| measurement | result |
| --- | ---: |
| viewer pane | 1146px wide |
| control rail | 343.796875px wide (30.0%) |
| control rail viewport | 900px high |
| control content | 1835px high |
| computed overflow | `auto` |
| visible descendant buttons | 0 of 17 |
| visible descendant separators | 0 |
| Reset display | `none` |

The screenshot was inspected at original resolution. The whole Curta remains
visible beside the rail, the first handles are immediately operable, and the
remaining handles are reachable by scrolling the rail without moving the page.
The assembly navigator still contains every `result_*` and `turns_*` child.

## Full validation

- `npm run typecheck`: clean.
- `npx vitest run`: **46 files, 1220 tests passed**.
- `pytest -q tests/test_calculator_document.py tests/test_widget_e2e.py tests/test_bundle.py tests/test_packaging.py`:
  **57 passed**, 28 pre-existing Pillow deprecation warnings.
- `openspec validate compact-clocked-controls --strict`: valid.
- `git diff --check`: clean.

The built bundle remains generated/ignored. `solidNodeViewerApi` stays **19**,
document versions stay **1 … 8**, and no framework or project file changed.
