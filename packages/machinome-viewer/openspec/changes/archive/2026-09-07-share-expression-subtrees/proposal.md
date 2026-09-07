## Why

A real clock will not animate. 3DPrintedClocks' `wall_clock_53_grasshopper`
publishes a 31.6 MB document whose escapement expressions are megabytes of
text, and the viewer plays it at about two frames per second while the whole
machine stutters.

Nothing is wrong with the numbers: the text is. The producer builds an
expression by string concatenation (solid2's `OpenSCADConstant`), so every
reuse of a value pastes its full text again, and the escapement nests those
reuses. The document's 116 operation expressions are 30 distinct strings
holding 4.28 million parsed nodes — and **293 distinct subexpressions**. The
widget parses each string once and then walks every one of those nodes on
every frame `$t` changes.

Measured on the published document
(`projects/3DPrintedClocks/_build/wall_clock_53_grasshopper/viewer.json`,
version 2, 46 nodes, 76 operations, 22 of them time-dependent, no drivers),
with this package's own `jokenizer` 1.0.1 on node v24.11.1:

| operation                                 | text    | parsed nodes | distinct subexpressions |
|-------------------------------------------|---------|--------------|-------------------------|
| escape wheel (and 5 arbors, 5 rods)       | 1.66 MB | 328,336      | 193                     |
| cannon pinion, hands, arbor, hour holder  | 3.32 MB | 656,718      | 224                     |
| entry arm / exit arm                      | 23 KB   | 4,536        | 75                      |
| whole document                            | 31.6 MB | ~7 million   | 293                     |

| what one animated frame costs            | today       | with shared subtrees |
|------------------------------------------|-------------|----------------------|
| parsed nodes visited                      | 6,247,876   | 255                  |
| one `evaluate` of the largest expression  | 57 ms       | (shared; not repeated) |
| wall clock, 60 animated frames            | ~30 s¹      | 29 ms                |
| parse memory retained for the document    | 723 MB      | 267 interned nodes²  |
| one-time parse at load                    | 7.65 s      | 8.86 s               |

¹ Extrapolated from the ~0.5 s per frame the pilot observes in the browser;
every other row is measured, the "today" column against the shipped
`evaluator.ts` path and the "with shared subtrees" column against a
throwaway prototype of the design below.

² The prototype interns 267 where the structural count above is 293: it
folds `^` into `pow` and keys constants by value, so a few nodes coincide.

The 723 MB is the module-level token cache: it holds the full parse tree of
every distinct expression for the life of the page, which is the memory
pressure the pilot feels as the machine stuttering rather than as the viewer
being slow.

The producer-side fix — teaching `solid_node.math` to emit shared
subexpressions — is a separate, later change in solid-node. This change is
the viewer alone: no document format change, and every document the
framework has already published gets the benefit.

## What Changes

- The viewer's expression evaluation stops walking parse trees. Each parsed
  expression is turned once into a **hash-consed DAG**: structurally
  identical subtrees become one shared node, across the whole document and
  not only within one expression, and the parse tree is dropped as soon as
  the DAG is built. Evaluation walks that DAG with a per-pass memo, so one
  frame costs the document's distinct subexpressions rather than its text.
- The module-level token cache goes away with it. What the viewer retains
  for an expression is its root node id and the shared node table; the
  expression strings themselves stay where they already are, in the loaded
  document.
- Numbers do not move. The parser stays `jokenizer`'s `tokenize`, the
  exponent-literal rewrite stays in front of it, and the OpenSCAD semantics
  (degree trig, `^` as `pow` with the unary-minus rule, `mod`, `ln`,
  `log(base, value)`) are carried onto the DAG unchanged, pinned by the
  existing parity fixture.
- `freeVariables()` keeps its exact meaning — a dotted driver id is one
  name, a call's callee is never a variable — and is now read off the DAG,
  so the per-node re-evaluation bounding that drivers and flexible parts
  depend on is untouched.
- The widget gains a test-visible count of subexpression resolutions and of
  the shared table's size, so the win is asserted as work performed rather
  than as elapsed time.
- An expression form the shared evaluation cannot support — an inline
  function, which nothing the producer emits carries — is refused when the
  document is loaded, beside the refusals already made there, so it can
  never surface first inside an animation frame.
- The viewer API version does **not** rise: no interface changes and no
  capability a host may require is added (see `tasks.md` 5.1).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a new requirement that a repeated subexpression is
  resolved once per evaluation pass, and that nothing of a document's parse
  trees is retained after its expressions are prepared; and the producer
  numerics requirement gains the statement that sharing may not move a
  number, plus the refusal of an expression form the evaluation cannot
  support.

## Impact

- `solid_node_viewer/widget/src/expressions.ts` — new: the shared node
  table, the DAG builder over `tokenize`'s output, the memoized evaluator,
  free-variable derivation, lifetime and metrics.
- `solid_node_viewer/widget/src/evaluator.ts` — keeps its public face
  (`evalExpr`, `freeVariables`, `TIME_ID`, `EvalScope`, `DriverScope`) and
  the OpenSCAD math context; hands the exponent-literal rewrite to the new
  module, where parsing lives, and loses `jokEvaluate`, `powify` as a
  whole-tree copy, `collectFree` and both caches.
- `solid_node_viewer/widget/src/viewer.ts` — retains the store at mount and
  releases it on dispose. No change to `setTime`, `driveTo`, the animation
  loop or the handle.
- `tree.ts`, `flexible.ts`, `drivers.ts` — unchanged.
- `solid_node_viewer/capture.py`, `server.py`, the development app — unchanged;
  they mount the same bundle through the same contract.
- `docs/adrs/EXPORT/ADR-043-hash-consed-expression-evaluation.md` — promoted
  on archive.
- `CHANGELOG.md` (0.1.0 unreleased). No `package.json` version change, no
  new dependency; `jokenizer` stays, as the parser.
