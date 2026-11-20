# Enigma I: what evaluating the formulas costs, and two prototypes

A viewer-side measurement on a committed mechanical project's own page, and
two prototypes of the evaluator made in a scratch copy of the widget's
source, taken to decide whether a change should be cut. No project or
framework source is copied here; the page is an ignored build artifact of
the project. The prototypes are in
`enigma-formula-evaluation-2026-11-20.patch` beside this file, as a diff
against `src/expressions.ts` and `src/tree.ts` at `e87683e3`; they are
evidence, not a proposed implementation.

## Pinned inputs

- Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
  `a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`:
  214,278 bindings, 546,768 expression nodes once mounted.
- Viewer source at `e87683e3` (`keep-a-live-model-parsed`,
  `rebuild-only-changed-flexible-parts` and
  `draw-a-press-from-its-first-frame` integrated), built unminified from the
  widget's own entry with a handle on the scene and with
  `WidgetTree.prototype.update`, `admit` and `FlexibleShape.prototype.evaluate`
  wrapped to count and time.
- Headless Chromium through Playwright on an AMD Ryzen 9 5900X virtual
  machine, no GPU. Every WebGL draw call is counted and not executed, so the
  times are script only. Single runs; differences of a tenth between two
  runs of one configuration were seen and are noise.

## Where a key press frame goes

On `e87683e3` a changing frame of a Press is about 190 to 210 ms of script.
The tree update is about 160 ms of it: about 100 ms in the flexible
evaluations, of which about 45 ms is the evaluation of their 36,415
parameters and the rest the rebuild of the seven parts that change, and
about 60 ms in the transforms. Counted in the evaluator, one Press
(a judgement and ten changing frames) computes 5.95 million node values:
about 540,000 a pass, the whole graph.

## What the graph depends on

Read from the mounted document, through its bindings, for the 540,941 nodes
any pose had reached:

| Input | Nodes that depend on it |
| --- | ---: |
| `operation.press` | 518,888 |
| `operation.key` | 507,600 |
| `operation.held_key` | 507,596 |
| `operation.stage` | 507,224 |
| `operation.right` | 507,200 |
| `operation.middle` | 507,178 |
| `operation.left` | 507,104 |
| `operation.engaged` | 185,711 |
| `operation.pending` | 177,415 |
| `rotors_out` | 112,813 |
| `supply_connected` | 22,705 |
| `case_open` | 21 |
| `flap_open` | 19 |
| `hood_open` | 16 |
| nothing | 21,529 |

About 507,000 nodes depend on all of the first seven at once. The bindings
themselves are 214,278 small steps in 81 distinct shapes (`(B * B)` 35,638
times, `(B + B)` 22,428, `(B / B)` 20,548, `max(N, B)` 20,121, …), with
32,568 calls of `max`, 13,240 of `abs`, 8,171 of `sqrt`, 4,854 of `min`,
2,757 `<=` and no ternary, `&&` or `||`. `operation.key` is read directly by
three bindings.

## Prototype 1: keep a value whose inputs did not change

A node's value survives a new pass when none of the inputs it depends on,
through bindings, differs from the previous pass's scope (a bit mask of
inputs per node, a union of what changed over the last eight passes). The
same prototype reads the scope's `bindings` once per pass instead of
through the scope's getter at every name.

A self-check recomputed every kept value: a first version kept 21 stale
values, because it gave an input its bit only when a dependency set first
named it, after the pass's changed mask had been taken, and a wheel step
did not move on screen; with every input given its bit before any mask is
taken, 378,079 kept values were recomputed with no mismatch.

It does not pay. A Press computed 4.69 million node values instead of 5.95
million, and its changing frame was 224 ms against 210 ms without it: there
is almost nothing a moved operation input does not feed. Reading the
bindings once per pass, alone, gave a key selection's click 137 ms against
182 ms, a Press's click 167 against 197 ms and its changing frame 191
against 210 ms, in single runs.

## Prototype 2: one flat pass

The graph reached from the binding roots is compiled once into a program in
dependency order over typed arrays: an opcode, a destination and up to three
operands per node, values in one `Float64Array` indexed by node id, a mask of
the inputs each node depends on. `WidgetTree.update` and `admit` run it in
one loop before they evaluate anything, skipping every entry no changed input
feeds; `valueOf` then reads a compiled node's value from the array, and
anything not compiled stays with the recursive walk. It covers numeric
constants, `$t`, driver inputs, binding names (as copies of their roots),
unary `-`, `+`, `!`, the arithmetic and comparison operators, `&&`, `||`, and
calls of the OpenSCAD context's functions with numeric arguments. A
comparison's result is held as 1 or 0. A scope that lacks one of the
program's inputs, or holds something other than a number there, is left to
the recursive walk for that pass.

On this page: 433,678 of the 546,768 nodes compiled, a program of 419,864
entries over 14 inputs, compiled in about 310 ms at the first pose; nothing
reached from a binding root was left out. A run costs about 4.3 ms on a Press
(about 416,000 entries recomputed, about 10 ns each).

A self-check after every pose compared each compiled node's value with the
recursive walk's (`Object.is`, a boolean taken as its number): 30,650,072
comparisons over 73 poses, no mismatch.

Timed in one session, the prototype off and on:

| Instruction (declared seconds) | Press task, ms | Script per changing frame, ms | Frames that changed the picture |
| --- | ---: | ---: | ---: |
| Key B (0), a different key | 136 → 85 | none | 0 |
| Press (2) | 186 → 97 | 187 → 111 | 11 → 19 |
| Release (2) | 160 → 88 | 186 → 113 | 11 → 18 |
| Right wheel on (0.4) | 104 → 31 | 46 → 58 | 1 → 1 |
| Right wheel back (0.4) | 89 → 37 | 38 → 62 | 1 → 1 |
| Open flap (1.5) | 7 → 9 | 28 → 33 | 49 → 41 |
| Close flap (1.5) | 6 → 9 | 31 → 30 | 42 → 43 |

The flap's frames each ran the program's loop for about 1.4 ms to recompute
about twelve entries: the loop tests every entry's mask. The wheel step's
one changing frame is its landing and its figure moved the wrong way within
the noise of one sample.

What is left of a Press frame with the prototype is about 66 ms in the
flexible evaluations (the seven parts rebuilt), about 20 ms in the
transforms and about 27 ms in the renderer's bookkeeping.

## Limits

- One document, one viewer, one browser, one host; single runs.
- The self-check covers the nodes this document compiles, at the poses these
  seven instructions reach. It does not cover a document with ternaries,
  short-circuits whose right side throws, member or index reads, strings,
  or a call whose result is not a number, none of which this document has.
- The prototype is entered only from poses. What the clocked machine's own
  solving, a running program's ticks or `PathValue` cost was not measured,
  and they were not routed through it.
- Nothing here is a statement about a GPU.
