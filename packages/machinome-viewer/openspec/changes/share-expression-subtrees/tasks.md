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

- [ ] 5.1 API version: `solidNodeViewerApi` stays **6**. Record the
      reasoning in the CHANGELOG entry and the ADR: the mount options, the
      handle, the document versions read and every published name are
      unchanged, and the metrics surface is a widget-source export for
      tests, not something a host can require. The version rises on an
      incompatible interface change or a new host-requirable capability, and
      this change is neither. Nothing in `widget/package.json` changes, and
      `version.test.ts` keeps its number.
- [ ] 5.2 Validation: `npm test`, `npm run typecheck`, `npm run build` in
      `solid_node_viewer/widget`; `.venv/bin/python -m pytest` for the Python
      package (the capture and server contracts must be untouched). Record
      the counts here.
- [ ] 5.3 `CHANGELOG.md` — a 0.1.0 (unreleased) entry in the house style:
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
- [ ] 5.5 Caller check on the model that started this.

      The workspace venv installs this package **editable** (`pip show
      solid-node-viewer` reports `Editable project location:
      .../solid-node-viewer`, and `bundle.describe()` returns
      `solid_node_viewer/widget/dist/solid-widget.js` inside this
      repository), so `npm run build` in the widget is the whole deployment:
      the shop floor and `solid develop` serve the rebuilt file. Do not
      reinstall anything.

      Numbers first, then eyes. Before rebuilding, record with the CURRENT
      bundle the value of every time-dependent operation expression of
      `projects/3DPrintedClocks/_build/wall_clock_53_grasshopper/viewer.json`
      at `$t` = 0, 1/3 and 2/3 (a short node script over the built module,
      kept in the cycle's scratch, not committed); after rebuilding, record
      them again and assert every number is identical — that is what
      "the escapement's motion is unchanged" means here, not a glance at
      the animation.

      Then open the model in `solid develop` or on the shop floor, play it,
      and record here: frames per second before and after, and the tab's
      memory before and after (browser task manager, or
      `performance.memory.usedJSHeapSize`), beside a note that the
      escapement, the train and the hands still move as they did. A green
      suite is not the evidence for this change; a clock that runs is.
