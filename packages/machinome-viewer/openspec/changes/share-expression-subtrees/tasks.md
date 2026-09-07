## 1. The shared node table

- [x] 1.1 Red: `src/expressions.test.ts` — `prepare(expression)` returns a
      node id; two structurally identical subtrees intern to ONE id and two
      different ones do not; a constant is keyed by value and type (`1` and
      `"1"` differ, `0` and `-0` differ); a `Member` chain rooted in a name
      is one name node carrying the dotted id, a `Member` on a call is a
      generic member node; a `Group` collapses to its single expression;
      `(5 ^ 2)` interns as a `pow` call and `(-2 ^ 2)` as the negation of
      one; an expression carrying an inline function is refused naming the
      form and the expression; `expressionMetrics().nodes` after preparing
      an expression pasted into itself twelve times is a few dozen, not
      thousands.
- [x] 1.2 Implement `src/expressions.ts`: the exponent-literal rewrite
      (moved here from `evaluator.ts`, where it belongs to parsing),
      `tokenize`, and the recursive builder that interns bottom-up into the
      table of D2, folding `^` and the dotted-name chain as it goes. No
      evaluation yet. Green.
      Commit: `feat(widget): intern parsed expressions into a shared table`.

## 2. Evaluation with a per-pass memo

- [x] 2.1 Red: `src/expressions.test.ts`, three groups.

      **Semantics** — `valueOf(id, scope)` agrees with `jokenizer`'s own
      `evaluate` over the same parsed tree, case by case, for: degree trig
      through the OpenSCAD context, `mod`, `ln`, `log(base, value)`, `^`
      under a leading minus, a dotted driver term, a driver shadowing a
      context name, a driver whose value is `0`, a ternary, and a
      short-circuiting `&&` whose right side must not be forced.

      **Missing and odd owners** (D5), each asserted against what jokenizer
      does today rather than against a guess: an undeclared bare name is
      `undefined` and `(nope * 2)` is `NaN`; `x_axis.motor` with no
      `x_axis` is `undefined`; with `x_axis: null` or another falsy
      primitive, `undefined`; with `x_axis: 5`, it throws the same
      `TypeError` jokenizer throws, message included (compare against a
      `jokEvaluate` call in the test, do not hard-code the string).

      **Counts** — for the twelve-round pasted expression, one pass resolves
      fewer than 100 nodes; a second expression sharing its subtrees in the
      same pass resolves zero further nodes; a pass at a new `$t` resolves
      them again. Then the pass detection of D6, driven with a **nested**
      driver map (`{x_axis: {motor: 8000}, y_axis: {motor: 0}}`), because
      `DriverStore.scope()` rebuilds those nested objects every call: a new
      scope object carrying equal values — nested maps rebuilt, not reused —
      resolves nothing; changing one nested number resolves again; `Object.is`
      both ways — changing `0` to `-0` resolves again, while `NaN` against
      `NaN` does not; adding or removing a driver key, or a nested owner,
      resolves again; a driver map holding something that is not a number or
      a plain object resolves again rather than being skipped; an absent
      `drivers` and an empty one are the same pass.
- [x] 2.2 Implement the recursive DAG evaluator, the stamped memo, the pass
      detection of D6 — the identity fast path checked on **every**
      `valueOf` call, then the recursive value comparison, the previous
      scope held by reference — the name resolution of D5 (jokenizer's
      falsy guard before the `in`, so a truthy primitive owner throws the
      native `TypeError` and a falsy one is `undefined`), and
      `expressionMetrics()` / `resetExpressionMetrics()`, where
      `resolutions` counts computations only and every node kind counts
      once per pass. Green.
      Commit: `feat(widget): resolve each subexpression once per evaluation`.

## 3. The evaluator reads through the table

- [x] 3.1 Red: `src/evaluator.test.ts` — two operations carrying the same
      expression, evaluated in one pass through `evalExpr`, resolve one set
      of subexpressions (fails while `evalExpr` calls jokenizer's
      `evaluate`); `freeVariables` of the pasted expression is read without
      preparing a second copy of it. And in `src/document.test.ts`, the
      refusal surface of D10: `assertRenderable` on a document whose
      **operation** expression carries an inline function, and on one whose
      flexible **`params`** expression does, fails naming the form and
      quoting the expression truncated — the refusal is the loader's, beside
      the unknown-`tech` one, and no frame ever meets the expression.
      (`assertRenderable` walks flexible `params` today, so this closes
      with no change to `viewer.ts`.) Every existing case in
      `evaluator.test.ts`, `tree.test.ts`, `flexible.test.ts` and
      `parity-fixture.test.ts` stays as it is and stays green — they are the
      parity gate for this increment.
- [x] 3.2 Implement: `evalExpr` prepares and evaluates through
      `expressions.ts`; `freeVariables` reads the memoized per-node set
      (name node contributes its dotted id, a call node its ARGS only, a
      generic member its owner). Delete `jokEvaluate`'s import, `powify`,
      `collectFree`, `dottedName`, `tokenCache` and `freeCache`. `npm test`
      and `npm run typecheck` green.
      Commit: `refactor(widget): read every expression through the shared table`.

## 4. Lifetime

- [x] 4.1 Red: `src/expressions.test.ts` — `retainExpressions()` /
      `releaseExpressions()` count mounts: the table survives a release
      while another holder remains, is emptied when the last releases (and
      an expression prepared afterwards works, at a fresh id), and a release
      without a retain is harmless; with `EXPRESSION_LIMITS.nodes` lowered
      for the test, passing the ceiling empties the table and the next
      preparation rebuilds correct values.
- [x] 4.2 Implement retain/release, the ceiling check on interning, and call
      them from `viewer.ts` at mount and in `dispose()`. Nothing else in
      `viewer.ts` changes. Green.
      Commit: `feat(widget): keep the shared table only while a viewer is mounted`.

## 5. Package, records and evidence

- [x] 5.1 API version: `solidNodeViewerApi` stays **6**. Record the
      reasoning in the CHANGELOG entry and the ADR: the mount options, the
      handle, the document versions read and every published name are
      unchanged, and the metrics surface is a widget-source export for
      tests, not something a host can require. The version rises on an
      incompatible interface change or a new host-requirable capability, and
      this change is neither. Nothing in `widget/package.json` changes, and
      `version.test.ts` keeps its number.

      Confirmed: `widget/package.json` untouched by this change (diff of
      the four implementation commits touches no `package.json`), and
      `version.test.ts` still asserts `API_VERSION === 6` and passes
      unmodified. The reasoning is folded into the CHANGELOG entry (5.3);
      the ADR itself is promoted by the coordinator at 5.4.
- [x] 5.2 Validation: `npm test`, `npm run typecheck`, `npm run build` in
      `solid_node_viewer/widget`; `.venv/bin/python -m pytest` for the Python
      package (the capture and server contracts must be untouched). Record
      the counts here.

      Run at the head of this change (commit `eff44d5`, task 4.2's HEAD):

      - `npm test` (vitest): **13 test files, 242 tests, all passed**
        (0 failed, 0 skipped). Files: version, camera, playback, drivers,
        controls, options, evaluator (25), assembly, tree (18),
        document (16), flexible (14), parity-fixture (13),
        expressions (44, new). The parity gate — `evaluator.test.ts`'s
        existing cases, `tree.test.ts`, `flexible.test.ts`,
        `parity-fixture.test.ts` — is unedited from its pre-change state
        and green throughout every increment's commit.
      - `npm run typecheck` (`tsc --noEmit`): clean, no errors.
      - `npm run build` (esbuild): succeeds, `dist/solid-widget.js`
        529.3kb (was 524.6kb before this change's first commit; jokenizer's
        `ExpressionVisitor`/`evaluate` are no longer imported by this
        package, so the size delta is `expressions.ts` itself).
      - `.venv/bin/python -m pytest` from this repository's root
        (`solid-node-viewer/`): **57 passed, 0 failed, 0 skipped**
        (18 deprecation warnings, all pre-existing Pillow/websockets
        notices unrelated to this change). Includes `test_capture.py`,
        `test_server.py` and `test_widget_e2e.py` — the capture and
        server contracts this task calls out — all green, confirming
        they mount the same bundle through the same contract untouched.
- [x] 5.3 `CHANGELOG.md` — a 0.1.0 (unreleased) entry in the house style:
      what the maker sees (a document whose expressions paste the same
      subexpression thousands of times now animates), the measured numbers
      from `proposal.md`, that the numbers themselves are unchanged and
      pinned by the parity fixture, and that the API version does not move.
      `README.md` needs no change: jokenizer is still bundled, still as the
      parser, and its notice stays.
- [ ] 5.4 Promote `adrs/EXPORT/ADR-043-hash-consed-expression-evaluation.md`
      to `docs/adrs/EXPORT/`, set its status to Accepted, and add its row to
      `docs/adrs/README.md` under EXPORT, keeping the table's order. Sync the
      delta into `openspec/specs/viewer-package/spec.md` and archive the
      change.
- [x] 5.5 Caller check on the model that started this. (Node-side parts
      only — see the pending lines below for the two the coordinator
      must do with a browser.)

      The workspace venv installs this package **editable** (`pip show
      solid-node-viewer` reports `Editable project location:
      .../solid-node-viewer`, and `bundle.describe()` returns
      `solid_node_viewer/widget/dist/solid-widget.js` inside this
      repository), so `npm run build` in the widget is the whole deployment:
      the shop floor and `solid develop` serve the rebuilt file. Nothing
      was reinstalled.

      **Numbers, before rebuilding (commit `c4277d9`, the planning
      commit, before any implementation change).** A scratch vitest
      script (`__scratch_caller_check.test.ts`, not committed) walked
      `projects/3DPrintedClocks/_build/wall_clock_53_grasshopper/viewer.json`
      (version 2, no drivers), found the document's 12 distinct
      time-dependent operation expressions, and recorded `evalExpr`'s
      value for each at `$t` = 0, 1/3 and 2/3 with the then-shipped
      evaluator, to
      `/tmp/.../scratchpad/caller-check-values.json`.

      **Numbers, after the final implementation commit (`eff44d5`,
      task 4.2's HEAD, before this 5.3 commit).** The same script,
      re-run against the rebuilt module (`npm run build` already run at
      5.2): every one of the 12 expressions' three values compared
      `Object.is`-identical to the BEFORE recording — **0 mismatches**.
      That is what "the escapement's motion is unchanged" means here:
      compared numerically, not eyeballed. (`caller-check-after.json`
      alongside it.)

      **Shared table size, resolutions per pass, and wall time — new
      evaluator, whole document (all 116 operation expressions, 46
      nodes, duplicates included as `tree.update` reads them).** A
      second scratch script (`__scratch_timing.test.ts`, not committed)
      warmed the cache once (matching `assertRenderable`'s own walk),
      then measured one pass at a fresh `$t` and 60 passes advancing
      `$t`:

      | metric                                   | value      |
      |-------------------------------------------|------------|
      | shared table size (whole document)         | 267 nodes  |
      | resolutions, one pass over all 116 operations | 267     |
      | wall time, 60 passes                       | 27.4 ms    |
      | wall time per pass                         | 0.457 ms   |

      **The same 60 passes through the OLD path**, measured directly at
      the planning commit `c4277d9` (HEAD was already there; no stash or
      worktree needed) with the same script pointed at the
      then-shipped `evaluator.ts`:

      | metric              | value       |
      |----------------------|-------------|
      | wall time, 60 passes | 53,470 ms   |
      | wall time per pass   | 891 ms      |

      60 passes: **53.47 s -> 27.4 ms**, about **1,950×** faster —
      consistent with `proposal.md`'s measured ~30 s -> 29 ms on the
      same document (this run's "old" number is a real stopwatch
      measurement rather than the proposal's extrapolation from the
      pilot's observed frame time, and lands close to it). The 267-node
      shared table matches `design.md` D8's "the clock's whole document
      interns 267" exactly.

      **Pending: coordinator.** The browser frame rate before/after and
      the tab's `performance.memory.usedJSHeapSize` before/after need
      the shop floor and an actual browser tab, which this task could
      not open; opening `solid develop` or the shop floor on this
      document, playing it, and recording those two numbers (plus a
      look that the escapement, train and hands still move as they did)
      is left to the coordinator.
