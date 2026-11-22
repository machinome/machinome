# Evidence: colour-a-node-by-what-it-holds

Bench: framework worktree `machinome/WTs/colour-a-node-by-what-it-holds`,
branch `colour-a-node-by-what-it-holds`, one planning commit `748b85e4`
above base `6ee00abc221872a959d3e0dbf714e8314b0e67ec`, clean before work
began; `openspec validate colour-a-node-by-what-it-holds --strict` reported
the change valid. Node v24.11.1, vitest from the bench's root
`node_modules`. Every test file was run on its own, one after another.

## Red on the base (task 2.4)

The tests of 2.1 to 2.3 were written and run against the unchanged
`navtree.ts` and `navigator.ts`.

`src/navtree.test.ts`: 54 tests, 6 failed, 48 passed. Each failure is on
its colour assertion:

| test | failed with |
| --- | --- |
| N1 | `expected null to be '#a0a0a0'` (G's row) |
| N4 | `expected null to be '#a0a0a0'` at `Outer/Inner`, its first assertion |
| N6 | `expected '#ff0000' to be '#0000ff'` (G's row colour) |
| N8, first case | `expected null to be '#a0a0a0'` |
| N9 | `expected null to be '#a0a0a0'`, at its first case (G collapsed) |
| N11 | the shown chip's `fill` was `"neutral"` where `"color"` was expected |

Passed on the base, as the design says they must: N2, N3, N5, N7, N8's
second case, N10, N12 (the marked-document test with `row.color` added to
its tuples), and N13 on both shapes. That the base reads each node's
`children` at most twice is inferred from its source (`visit` reads
`.length` and `.forEach`), not measured; the test asserts the bound of 4.

`src/navigator.test.ts`: 29 tests, 3 failed, 26 passed.

| test | failed with |
| --- | --- |
| D1 | `expected 'var(--machinome-nav-chip-neutral)' to be '#a0a0a0'`, at G's row (line 486, its first assertion) |
| D2 | the same, at its last assertion (line 505), after the chip was unchecked, `setVisible(['G'], false)` was called and both `aria-label`s read `Visibility for G` |
| D3 | `expected 'var(--machinome-nav-chip-neutral)' to be '#ff9b32'`, at G's row after the first push (line 518) |

`src/tree.test.ts`: 72 tests, all passed, T1 ("keeps reporting a group's
own colour when its parts share another") among them, run with the
verbose reporter to see it listed.

## The rule (task 3.3)

After 3.1 and 3.2: `npm run typecheck` exited 0 with no output beyond the
command line. `src/navtree.test.ts` 54 passed; `src/navigator.test.ts` 29
passed; `src/tree.test.ts` 72 passed. The only line of an existing test
that changed is N12's: the two tuples of "presents one row per part and
none for any marking" gained `row.color` (`git diff -U0` over the three
test files removes nothing else).

## Mutations (task 3.4)

`navtree.ts` was saved before the mutations (SHA256
`a24e4d2520639969325116e675eda3a4bfbae8355ac127af3dd529bcea70300e`) and
copied back after each; after the last it was byte-equal to the saved copy
(`cmp`, same SHA256).

| mutation | edit | `src/navtree.test.ts` |
| --- | --- | --- |
| (a) combine the colours the child rows show | the pass returns `result ?? node.color` to its parent, so a group's fallback stands in for its parts | 1 failed, 53 passed: N5, `expected '#ff0000' to be null` (Outer) |
| (b) drop the node's own model | `children.length === 0 ? node.color : undefined` | 1 failed, 53 passed: N7, `expected '#a0a0a0' to be null` |
| (c) a walk per row | the up-front `gather(assembly)` removed, and each row's colour taken as `gather(node)` inside `visit` | 1 failed, 53 passed: N13 over the chain of 200 groups, `expected 203 to be less than or equal to 4`; the flat group of 2,000 parts stayed green, since there each row's own subtree is one level deep |

## Gate (tasks 4.1 and 4.2)

Whole widget suite, from the widget directory,
`vitest run --no-file-parallelism` (file parallelism off so that files run
one at a time, per the bench's rule; otherwise the suite as `npm test`
runs it): 78 files, 77 passed and 1 skipped; 2,139 tests, 2,137 passed and
2 skipped, none failed, 197 s. The two skips are environment-gated:

- `src/run/profile-contact.test.ts`, "loads the pinned actual-cover v13
  Bound and replays its numeric stop": `it.skipIf` with
  `CURTA_PROFILE_V13_DOCUMENT` unset.
- `src/run/profile-installed-benchmark.test.ts`, "reports one pinned
  installed Curta v13 integration attempt": `it.skipIf` with
  `CURTA_INSTALLED_PROFILE_DOCUMENT` unset.

`npm run typecheck`: exit 0.

`npm run build`: exit 0, `dist/machinome-viewer.js` 920.0 kb. Bundle
SHA256 after the build
`13706c2b36206de89fdc2651465396e438d38ab26fd6f4107af62aaa8b1c07e8` (before
it, the bench's stale bundle was
`3ee8073f3a676d6657098eaab58be824763a8e5c281682187a9d9e79d7d7f6e8`). The
bundle is ignored by git and is not part of the change.

Viewer Python suite on the bench's venv,
`.venv/bin/python -m pytest tests -rs` from `packages/machinome-viewer`,
run after the build and before the CHANGELOG and warts edits: 304 passed,
3 skipped, 0 failed, 71 warnings (Pillow's `getdata` deprecation in
`test_widget_e2e.py`), 331 s. Skips, with the reasons pytest printed:

- `tests/test_curta_drawing.py:375` and `:469`: "the Curta's own builds are
  not at `.../machinome/WTs/projects/Calculators/Curta-Type-I-3x/_build`"
  (the test looks for the projects beside the worktree, where there are
  none).
- `tests/test_follow_the_slider.py:380`: "Playwright's firefox is not
  installed at the revision it expects".

After the CHANGELOG, warts and evidence edits, three files were run again
on their own: `tests/test_documentation.py` 13 passed,
`tests/test_version.py` 3 passed, `tests/test_licence.py` 6 passed with
184 subtests (it did not ask for this untracked file to be staged).

## Records (tasks 6.1 to 6.3)

The CHANGELOG bullet of task 6.1 sits at the top of "Unreleased", in the
words the task gives. Two entries end `workflow/warts.md`: W1 "A navigator
chip whose colour the machine chooses shows the choice of the last
assembly change, not of the pose" and W2 "`AssemblyNode.model` is false for
a flexible part". Every line reference they cite was read on the bench
before writing them (`navigator.ts:248`, `:423`, `:443`, `:516`,
`:518-519`; `tree.ts:725`, `:797-799`; `viewer.ts:2118`, `:2194`, `:2567`,
`:2630`, `:2651`; `types.ts:77-79`; `viewer-handle.rst:139`).

Manual (task 6.3): `grep -rniE "chip|swatch|colou?r"` over
`packages/machinome/docs/howto/browser-viewer.rst` and
`packages/machinome/docs/reference/viewer/layouts.rst` finds only
`layouts.rst:38` ("per-row depth/color properties"), `:203`, `:212`,
`:213` (the variable table), `:218` ("`--machinome-nav-depth` and
`--machinome-nav-node-color` are per-row data, not theme settings; the
component writes them as the model changes"), `:245` and `:247`; nothing
in `browser-viewer.rst`. The navigator sections of both pages ("Inspect
the assembly"; "Navigator", "Navigator variables") were read: neither
states which colour a row or its chip shows. No page was edited.

## Departures from the design

None in the rule. Routine differences:

- N8 is two `it`s, its first and second case, so the second can be seen
  passing on the base while the first fails; N13 is one `it.each` over its
  two shapes.
- The stylesheet comment of task 3.2 is on `navigator.ts:46`, not 45; its
  words were changed as the task says.
- The whole widget suite was run with `--no-file-parallelism` (above).

## Enigma I counts (task 5.2, reviewer)

Counted by the reviewer on 22 November 2026 on the Enigma I document
(`projects/enigma-i` at `68dc6be`, `_build/viewer.json`, SHA256
`563a2fdc...`), in a scratch vitest file in the widget's `src/`, deleted
afterwards. It built the snapshot the viewer would report from the
document (each node at its own or inherited colour, `model` true for a
node with a model file) and ran `navigatorRows` over it with every row
expanded, once from the base's `navtree.ts` (`git show 6ee00abc:`) and
once from this change's.

This departs from task 5.2 as written: no page was mounted. One mounted
copy of this document takes about 4.2 GB, and the pilot assesses the page
in the browser. A conditional colour was therefore read at both of its
choices instead of at the mount's pose, which was not evaluated, and no
screenshot or custom property was read from a page.

| every conditional colour at | rows | rows with children | showing a colour, base | showing a colour, change | rows without children whose colour moved |
| --- | --- | --- | --- | --- | --- |
| `off` | 4,173 | 878 | 0 | 607 | 0 |
| `on` | 4,173 | 878 | 0 | 315 | 0 |

`keyboard/guide/n8_Anti_Twist_Device_Group_1` shows `#a0a0a0` and its
parent `keyboard/guide` shows no colour, at both choices. One call with
every row expanded took 1.6 to 2.0 ms from the base and 2.7 to 4.1 ms
from the change (mean of 20 calls each, one run).

Five faults planted by the reviewer in the pass, each run against
`src/navtree.test.ts` and restored (byte-equal): a part with no colour
no longer keeping the group from sharing one (N5, N7 red); only the
first child read (N2, N3, N4, N5, N8's second case and an existing test
red); a group's declared colour counted as a part (N6 red); the shared
colour shown only while expanded (N9 red); a hidden group losing its
colour (N9 red). None survived.
