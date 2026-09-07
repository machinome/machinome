## Context

`evaluator.ts` is a thin layer over the `jokenizer` package. `evalExpr`
rewrites exponent literals to plain decimal, tokenizes, rewrites parsed `^`
nodes into `pow` calls (`powify`, which rebuilds the whole tree), caches the
result in a module-level `Map<string, tokens>`, and hands it to jokenizer's
`evaluate` with a freshly spread scope `{...context, ...drivers, $t}`.
`freeVariables` walks the same cached tree with `collectFree` and caches the
resulting set beside it.

Three properties of that arrangement decide this design:

1. **jokenizer's `evaluate` cannot memoize.** It is a visitor over its own
   AST shape, with no node identity to key a memo on and no place to put
   one. Two structurally identical subtrees are two objects, and it visits
   both.
2. **The caches are keyed by expression string.** Sharing therefore stops at
   the expression boundary — and the escapement's 1.66 MB expression appears
   inside fourteen operations of the grasshopper clock.
3. **The token cache is the memory.** It retains the parse tree of every
   distinct expression the page has ever evaluated: 723 MB for one clock,
   measured, against 111 MB for the loaded document itself.

The consumers are `tree.ts` (matrix per operation, bounded by
`needsUpdate`), `flexible.ts` (`params` per flexible node, bounded the same
way), and `viewer.ts` (`assertRenderable`'s free-variable check, and the
`scope()` it hands down on every `setTime`, `driveTo` and animation frame).
The headless capture and the development server mount the same bundle
through the same contract and appear nowhere in this change.

Measurements quoted here are from the grasshopper clock's published
document, `jokenizer` 1.0.1, node v24.11.1, on the pilot's workstation; the
`^`/interning prototype lives in this cycle's scratch and is not committed.

## Goals / Non-Goals

**Goals:**

- One frame costs the document's *distinct* subexpressions.
- Sharing across expressions, not only within one.
- Nothing of the parse trees retained once an expression is prepared.
- Exact numeric parity: the parity fixture and every evaluator test pass
  untouched.
- `freeVariables()` unchanged in meaning, so driver- and time-bounded
  re-evaluation is unchanged.
- The win asserted as work performed, not as elapsed time.

**Non-Goals:**

- Any document format change. The producer's own de-duplication is a later
  solid-node change; this one must speed up documents already published.
- A new expression language, new functions, or a different grammar.
- Vectorising, compiling to JavaScript source (`new Function`), or a WASM
  evaluator. A memoized DAG walk is already ~24,000× fewer node visits per
  frame; a code generator would add a second numeric implementation to keep
  in parity for no measured need — and `new Function` is refused by a
  strict Content-Security-Policy, which a static export may well be served
  under.
- Changing `tree.ts`'s bounding rule, the handle, the API version, or the
  `scope()` the viewer builds per pass.

## Decisions

### D1. Keep `tokenize`; replace `evaluate`

`jokenizer` stays a dependency and stays the parser. The grammar, the
literal rules and the operator precedence are the parity-proven half of the
package and the half this change has no quarrel with; the tree-walking
evaluator is the half that cannot memoize. `plainLiterals` keeps running in
front of `tokenize` unchanged.

So the new module owns a *builder* (jokenizer AST → shared node table) and
an *evaluator* (node id + scope → value), and jokenizer's `evaluate` and
`ExpressionVisitor` are no longer imported.

The evaluator reproduces jokenizer's semantics deliberately and verbatim
where they are visible: unary `-` as `-1 * v` (not `-v`), binary operators
by the same JavaScript operators, `&&`/`||` short-circuiting their right
side, a name resolved by `in` (so a driver whose value is `0` is found),
and an unresolved name yielding `undefined` rather than throwing — a
missing driver still reaches `evalExpr`'s `Number(value)` as `NaN`, exactly
as today.

### D2. Hash-consing key: kind, operator, and child ids

The builder walks the parse tree bottom-up, so every child already has an
id — a small integer — when its parent is keyed. The key is a string of the
node's kind, its operator or name, and its children's ids:

| kind    | key                          | payload                        |
|---------|------------------------------|--------------------------------|
| const   | `c` + typeof + `:` + value   | the literal value              |
| name    | `n` + dotted name            | the name split into path parts |
| unary   | `u` + operator + `:` + id    | operator, child id             |
| binary  | `b` + operator + `:` + l,r   | operator, two child ids        |
| call    | `f` + callee id + `:` + args | callee id, arg ids             |
| member  | `m` + owner id + `:` + name  | owner id, name                 |
| index   | `i` + owner id + `:` + key id| owner id, key id               |
| ternary | `?` + p `:` + t `:` + f      | three child ids                |
| array   | `[` + item ids               | item ids                       |
| object  | `{` + name:id pairs          | names, value ids               |

Constants are keyed by value *and* `typeof`, so the number `1` and the
string `"1"` do not collide; a numeric zero is keyed `-0` or `0` by
`Object.is`, because `String(-0)` is `"0"` and the two are different
literals. The table is a `Map<string, number>` beside parallel arrays
indexed by node id (kind, operator/name, child ids, literal value) — arrays
rather than objects so the per-node overhead is a few slots, and the memo
below can be a plain array indexed by the same id.

A key string is built once per parse node, discarded immediately unless it
interns a new node, and never rebuilt: interning is a one-time cost on the
load path, measured at ~1.2 s on top of `tokenize`'s 7.65 s for the whole
31.6 MB clock.

### D3. A dotted driver id is one name node

`x_axis.motor` parses as `Member{owner: Variable{x_axis}, name: motor}`.
The builder folds a `Member` chain rooted in a `Variable` into a single
**name node** carrying the dotted string and its split path — which is
exactly what today's `dottedName()` does for `freeVariables`, moved into the
builder so evaluation and dependency reading share one answer. Resolution
walks the path against the nested driver map, so nothing about
`DriverScope` changes.

A `Member` whose owner is not a plain name chain (`f(1).x` — nothing the
producer emits, but jokenizer accepts it) stays a generic member node, and
its free variables come from its owner, as today.

### D4. `^` folds into the DAG; `powify` disappears

The `^` → `pow(...)` rewrite, including the rule that a leading unary minus
stays *outside* the call (`-2 ^ 2` is `-(2^2)`, as OpenSCAD binds it), moves
into the builder's `Binary` case. Today it is a separate recursive pass that
copies every node of the tree — a second million-node allocation for the
clock's largest expression — and after this change there is no tree to copy.

A call node's callee is a node like any other, usually the name node `pow`
or `sin`. It is resolved through the same lookup as any other name at
evaluation time, so a document that declares a driver named `sin` shadows
the math context exactly as the spread scope shadows it today.

### D5. Name resolution replaces the per-call spread

Today every `evalExpr` call allocates `{...context, ...drivers, $t: time}`:
some forty non-enumerable `Math` properties copied per operation
expression, hundreds of times per frame. The DAG evaluator resolves the
first part of a name directly, in the order that spread established:

1. `$t` (the exact name), from `scope.time`;
2. the driver map, `in`-checked (so a driver whose value is `0` is found,
   and prototype-chain names such as `toString` resolve to the same
   function the merged object resolved them to);
3. the OpenSCAD math context, the same way;
4. otherwise `undefined`.

Every further part of a dotted name — `motor` in `x_axis.motor` — is
resolved by reproducing jokenizer's `readVar` in the shape it has, because
its edge cases are the parity claim and they are not all obvious. Measured
against `jokenizer` 1.0.1 today:

| owner value                    | `x_axis.motor` today                        |
|--------------------------------|---------------------------------------------|
| absent from the scope           | `undefined` (`(x_axis.motor * 2)` is `NaN`) |
| `null`, or any falsy primitive  | `undefined`                                 |
| a truthy primitive, e.g. `5`    | **throws** `TypeError: Cannot use 'in' operator to search for 'motor' in 5` |
| an object without the key       | `undefined`                                 |
| an object with the key          | the value                                   |

The evaluator therefore resolves a part as `owner && (part in owner) ?
owner[part] : undefined` — the falsy guard before the `in`, exactly as
jokenizer has it, so the falsy-primitive case yields `undefined` and the
truthy-primitive case throws the identical native `TypeError` with the
identical message. Nothing is invented and nothing is smoothed over: a
document that reaches either path is malformed, and `assertRenderable`
refuses an expression naming an undeclared driver id before any of it is
evaluated, so these paths are reachable only from a direct `evalExpr` call
(the tests) or from a host that bypasses the loader.

One deviation is deliberate. jokenizer binds a resolved function value to
the scope it found it in (`v.bind(scope)`); the DAG evaluator calls it
directly. Every function in the OpenSCAD context is a plain function that
ignores `this` — `Math.sin` bound to a scope object and `Math.sin` called
directly return the same number — and a driver map holds numbers, never
functions. The parity fixture covers the trig chains that would show any
difference.

No object is allocated per evaluation, and the resolution order is the one
the parity fixture already pins.

### D6. The memo is a stamped array, and a pass is a set of scope values

Evaluation keeps two arrays indexed by node id: `value` and `stamp`. A node
is computed when its stamp is not the current pass's, and the stamp — never
the value — decides a hit, so a node whose value is `undefined` or `NaN`
memoizes correctly.

The pass counter advances when the scope's *values* change. `valueOf`
checks this on every call, because callers hand it one scope object per
`tree.update` walk and nothing announces a pass boundary:

1. **Identity fast path.** `scope === lastScope` — true for every
   `evalExpr` call of one `tree.update`, since `viewer.ts` builds one scope
   object and passes it down — and the pass stands.
2. **Value comparison.** Otherwise compare against the remembered scope:
   `Object.is(scope.time, last.time)`, then the driver maps by the rule
   below. Equal means the pass stands; different means the counter
   advances.

The driver maps are compared **recursively**, not one level deep, and the
reason is `DriverStore.scope()` (`drivers.ts:216`): it builds a fresh nested
object for every qualified owner on every call. Two scopes carrying
identical values therefore share no nested object, so a comparison that
stopped at the owner would call every qualified-driver document changed on
every call — and the "second walk of a playing frame is free" claim below
would hold only for documents with no qualified drivers. Skipping objects
instead would return stale numbers. The rule, applied to a map and to each
nested map:

- an absent map counts as an empty one;
- the key sets must match — same size, every key of one present in the
  other;
- a `number` is compared with `Object.is` (so `NaN` equals `NaN` and `0`
  differs from `-0`);
- a plain object is compared by this same rule, recursively;
- **anything else** — a function, a string, `null`, `undefined`, an array —
  counts as changed, so an unexpected shape costs a recomputation and never
  a stale number.

Nesting is one level deep for every document the producer writes (an owner
and its drivers), so the comparison is tens of `Object.is` calls; the
recursion is there so a deeper map can never be silently skipped.

The remembered scope is the previous scope **object**, held by reference,
not a copy: `DriverStore` rebuilds rather than mutates, so the reference's
values stay the values that were compared, and it pins nothing but a map of
tens of numbers.

Two consequences:

- Sharing spans expressions and callers within a pass: the escapement
  expression under fourteen operations is resolved once, and so is any
  subexpression it shares with the cannon pinion's.
- A pass whose values equal the previous pass's is free. That matters
  today: while playing, `viewer.ts` updates the tree twice per frame — once
  inside `setTime`, once in the animation loop — with two different scope
  objects carrying the same numbers, nested driver maps included. The
  second walk now costs nothing.
  (Removing the second walk is a separate question; see Open Questions.)

The correctness condition is that a scope object is not mutated between
`evalExpr` calls of one pass. Nothing in the widget mutates one — `scope()`
builds a fresh object and `DriverStore.scope()` a fresh nested map — and the
value comparison catches a caller that rebuilds rather than mutates. The
module documents the contract.

Rejected alternatives: a `WeakMap` keyed on scope identity (loses the
value-equal second pass, and a mutated scope becomes a wrong number rather
than a rebuild); and an explicit `beginPass()` token threaded through
`tree.update` and `flexible.evaluate` (correct, but changes every caller
and every test scope to buy nothing the value check does not).

### D7. Recursion, not an explicit stack

Both walks — the builder over the parse tree and the evaluator over the DAG
— are recursive. The measured maximum parse depth over the whole 31.6 MB
document is **120 jokenizer nodes** (66 in the equivalent Python AST): the
expressions are enormously *wide*, not deep, and jokenizer's own
recursive-descent parser must already exceed that depth to have produced the
tree at all. A recursive builder also needs no side map from parse node to
id — it returns ids — where an explicit stack would have to retain one entry
per parse node, a million-entry map for the clock's largest expression.

A pathological deep expression (a chain of thousands of `+`) would overflow
the stack, as it already would in `tokenize` today; the failure mode is not
new.

### D8. One module-level store, retained by mounts, with a ceiling

The store is module-level, as the token cache is today, so `evalExpr` and
`freeVariables` keep their signatures and every caller stays as it is. What
changes is what it holds and how long:

- `Map<string, nodeId>` from expression text to its DAG root. The strings
  are the ones the loaded document already holds; the map adds an entry, not
  a copy.
- The shared node table, plus a memoized free-variable set per node.
- **No parse trees.** The builder's tree is unreferenced the moment its root
  is interned.

Lifetime is a mount count: `retainExpressions()` at mount, `releaseExpressions()`
on dispose, and the store is emptied when the count reaches zero. It is a
pure cache, so emptying it is always safe — the cost of being wrong is a
re-parse, never a wrong number — and refcounting keeps one widget's dispose
from stalling another widget's animation.

A ceiling backs it up for the long `solid develop` session that republishes
a document hundreds of times: when the table passes 50,000 nodes the whole
store is dropped and rebuilt on demand. The clock's whole document interns
267, so the ceiling is roughly two hundred republished versions of the
worst document seen, and it can never be reached by one document. The
ceiling lives in an exported `EXPRESSION_LIMITS` object so a test can lower
it rather than build fifty thousand nodes to reach it.

Emptying the store — at the ceiling, or when the last mount releases it —
resets **everything keyed by node id**: the intern table, the expression
string map, the free-variable sets, and with them the memo's `value` and
`stamp` arrays, the pass counter and the remembered last scope. Node ids
are handed out again from zero after a reset, so a surviving stamp array
would let a new node inherit an old node's value; fresh arrays, a counter
that restarts and a forgotten last scope make the first pass after a reset
an ordinary cold one.

### D9. What a test can observe

The module exports `expressionMetrics()` → `{ nodes, resolutions }` and
`resetExpressionMetrics()`. `nodes` is the size of the shared table;
`resolutions` counts node computations: incremented on the compute path
only and never on a memo hit (one integer add against work that is at least
a function call). Every node kind counts the same — a constant and a name
are resolved and stamped like any other node, so each is counted once per
pass and not once per occurrence, which is exactly the quantity the tests
assert against the distinct-subexpression count.

This is a widget-source export, not a handle method: nothing a host can
require, so the viewer API version does not move (tasks 5.1). The red-first
assertions it makes possible are counts, not milliseconds:

- an expression built by repeated textual substitution (`e = "(sin(e) +
  cos(e))"`, twelve rounds: ~2^12 pasted nodes, a few dozen distinct)
  evaluates to the same number as jokenizer's `evaluate` on the same text,
  and resolves fewer than 100 nodes;
- the second operation carrying the same expression in one pass resolves
  zero further nodes;
- a pass at a new `$t` resolves them again;
- interning that expression grows the table by the distinct count, not the
  textual one.

### D10. Which expression forms the DAG supports

Literal, Variable, Group (collapsed to its single expression, as jokenizer
requires), Member, Indexer, Unary, Binary, Call, Ternary, Array and Object
are built and memoized. `Array` and `Object` nodes return the same object to
every use within a pass; nothing in the viewer mutates an evaluated value.

`Func` (an arrow function) and a bare `Assign` are refused at build time,
naming the form and the expression. jokenizer's `evaluate` accepts a lambda
inside a call (a bare one it already refuses, "Invalid Func expression
usage"); memoizing one would need a scope stack per invocation, which is a
language the producer does not emit and this viewer has never rendered.
Refusing is the posture the loader already takes toward a flexible `tech` it
cannot evaluate: say so rather than return a number that may be wrong.

**The refusal is a load-time refusal, and that matters more than the rule.**
`assertRenderable` (`viewer.ts`) already walks every expression of a
document before anything is rendered — every operation's, and every
flexible node's `params` (`Object.values(node.flexible.params).forEach(note)`,
confirmed in the current source) — and it walks them by calling
`freeVariables`. Once `freeVariables` reads the DAG, preparing an
expression is what that walk does, so an unsupported form throws there:
inside `loadDocument`, before a `WidgetTree` exists, alongside the refusals
for an unreadable document version, an unknown flexible `tech` and an
undeclared driver id. A mount fails with it; a `reload()` or
`manifestChanged()` fails with it and leaves the standing model alone,
which is the behaviour "A failed update leaves the model standing" already
requires. No such expression can first be met inside an animation frame.

Two details the message needs: it names the form (`Func`) and it quotes the
expression **truncated** — the offending expression may be megabytes, and an
error that pastes 3.3 MB into a console is its own failure. The first
eighty characters and an ellipsis are enough to find it in a document.

### D11. `freeVariables` comes off the DAG

A node's free-variable set is computed once per *node* and memoized beside
it: a name node contributes its dotted name, a call node the union of its
**args only** (never its callee), a generic member node its owner's set.
Those are today's three rules verbatim. The result is that
`freeVariables('…3.3 MB…')` costs the expression's distinct nodes instead of
walking every one of its 993,675 parse nodes — a load-path win nobody asked
for, on the path `assertRenderable` and `WidgetTree.free` take.


### D12. The module surface

`expressions.ts` exports exactly what the layers above need and what its own
tests observe:

- `prepare(expression: string): number` — the expression's root node id,
  parsing and interning it the first time and reading the string map after.
- `valueOf(id: number, scope: EvalScope): unknown` — the memoized DAG walk.
- `freeNames(id: number): ReadonlySet<string>` — the per-node memoized set.
- `expressionMetrics(): { nodes: number; resolutions: number }` and
  `resetExpressionMetrics()`.
- `retainExpressions()`, `releaseExpressions()`, `EXPRESSION_LIMITS`.

`evaluator.ts` keeps `evalExpr`, `freeVariables`, `TIME_ID`, `EvalScope`,
`DriverScope` and the OpenSCAD context, and becomes three-line delegations
over the four functions above. No other module's imports change.

## Risks / Trade-offs

- **Load time grows by the interning walk.** Measured 8.86 s against
  `tokenize`'s 7.65 s for all 30 distinct expressions of the clock: ~16%
  more one-time work, against ~0.5 s saved on every animated frame
  thereafter. Today's parse is lazy (first evaluation of each expression) and
  stays lazy, so the shape of the wait does not change either.
- **Peak memory during the build is unchanged**, and it is large: one
  3.32 MB expression parses to 993,675 nodes and ~161 MB before it is
  interned and dropped. What goes away is the *retained* 723 MB. A document
  with a single expression bigger than memory was already unopenable.
- **A mutated scope object would return stale numbers.** Mitigated by the
  value comparison (D6) and stated as a contract in the module. The parity
  fixture reuses scope objects across cases, which is exactly the safe
  direction: equal values, equal results.
- **Two numeric implementations exist during the cycle** — jokenizer's, and
  ours. The parity fixture, the evaluator suite and a builder test that
  compares the DAG's value against `jokEvaluate` on the same tree keep them
  pinned while the second one is written; the comparison test may stay
  afterwards as a cheap guard.
- **A lambda in an expression stops working.** Nothing produces one; no test
  covers one; the refusal names it.

## Migration Plan

Internal to the widget. No document, host, capture, server or CLI contract
changes, the bundle's published names are untouched, and the API version
stays 6. A host that mounts the new bundle over an old document sees the
same numbers faster. Nothing to migrate; nothing to fall back to.

## Open Questions

1. **The tree is updated twice per playing frame.** `setTime` updates and
   renders, and the animation loop updates and renders again with the same
   values. The memo makes the second walk free, so this cycle leaves it
   alone — but it is still two full `tree.update` traversals and two
   `renderer.render` calls per frame, and the pilot may want it looked at
   separately.
2. **The document is still 31.6 MB on the wire**, ~111 MB resident as
   strings, and ~9 s of one-time parsing. Only the producer can fix that
   (solid-node emitting shared subexpressions, a later change). Whether the
   viewer should also warn about a document this shape is the pilot's call.
3. **Should the metrics surface be permanent?** It is proposed as a widget
   source export for tests. If a host should ever be able to read it, that
   is a handle addition and an API bump — deliberately not this change.
