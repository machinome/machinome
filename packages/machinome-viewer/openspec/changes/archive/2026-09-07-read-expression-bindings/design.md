## Context

The framework's `expression-bindings` cycle publishes a document whose
expressions no longer repeat themselves. Its contract is written down on
the producer's side — `openspec/specs/export/spec.md` in solid-node, the
requirements "A shared subexpression is published once", "Binding names
cannot collide with anything the consumer resolves" and "What a binding
name means to a consumer", plus ADR-080 — and this change is the consumer
half of exactly that text. Everything below is a decision about *how this
package* satisfies it; nothing below re-decides the format.

The three consumer rules, quoted from that spec, are the whole
obligation:

> **Bindings resolve first.** A name appearing in an operation's
> expression, in a flexible leaf's `params`, or in another binding SHALL be
> resolved as a binding before it is treated as a driver id. […]
>
> **Dependence flows through a binding.** […] an expression naming a
> binding SHALL be treated as depending on every input that binding
> transitively depends on.
>
> **Every other name is unchanged.**

What is already here, from `share-expression-subtrees` (ADR-043):

- `expressions.ts` owns a **page-scoped, hash-consed DAG**. `prepare(text)`
  returns the root node id of an interned expression; `valueOf(id, scope)`
  walks the DAG with a memo stamped by an evaluation *pass*, where a pass
  is a set of scope values rather than a syntactic event; `freeNames(id)`
  is a per-node memoized free-variable set. Name resolution order is `$t`
  → the driver map → the OpenSCAD math context → `undefined`. The store is
  retained by a mount count and dropped at zero or at a node ceiling
  (`EXPRESSION_LIMITS.nodes`, 50,000).
- `evaluator.ts` is three-line delegations: `evalExpr`, `freeVariables`.
- `viewer.ts` refuses, in `assertRenderable` and before any tree exists: a
  document version outside `[1, 2, 3]`, a flexible technology or spec it
  cannot evaluate, an expression form it cannot support, and an expression
  naming a qualified id the document's `drivers` table does not declare.
- `tree.ts` bounds re-evaluation by a node's free variables (`needsUpdate`,
  and `animated` off the same set); `flexible.ts` does the same for a
  leaf's `params`.

Two facts about the real document decide most of what follows. Both were
measured in this cycle's scratch against
`grasshopper-viewer-v4.json` and the flat `viewer.json` beside it:

1. **Not one of the 116 operation expressions contains `$t` as text.**
   Twenty-two of them are time-dependent, every one of them through the
   table; 17 are a bare binding name and nothing else; 11 distinct entry
   names are referenced from operations; all 56 entries resolve through to
   `$t`. A consumer that reads free variables off the expression string
   alone concludes the document is not animated.
2. **Substituting the table back reproduces the flat document exactly.**
   Expanding every binding reference in all 116 version-4 operation
   expressions yields, character for character, the 116 expressions of the
   31.6 MB version-2 document — 31,611,478 characters, 116 of 116
   identical. The two documents are the same expressions, differently
   written.

## Goals / Non-Goals

**Goals:**

- A version-4 document mounts, poses and animates exactly as the flat
  document it was published from does.
- Dependence flows transitively through the table, everywhere the viewer
  reads an expression's inputs: `needsUpdate`, `animated`, a flexible
  leaf's `free`, and the undeclared-driver refusal.
- A table this viewer cannot resolve is refused when the document is
  loaded, naming the entry — never a wrong pose, and never first met
  inside a frame.
- Bindings cost what the DAG already costs: one resolution per distinct
  subexpression per pass, no forward pass, no per-pass allocation of a
  values map.
- A document without a table is byte-for-byte the same code path it is
  today.
- Two documents on one page cannot read each other's bindings.

**Non-Goals:**

- Any change to the document format, or to what the producer publishes.
  The table's shape, ordering, naming and version rule are ADR-080's and
  are consumed as given.
- A new expression language or grammar. A binding reference is an ordinary
  name; nothing marks it.
- Re-deciding `share-expression-subtrees`. The DAG, the memo, the pass
  detection, the store lifetime and the metrics surface stand as they are,
  extended only where a binding forces it.
- Rewriting a document, flattening a table, or caching a substituted
  expression string. The 31.6 MB form must never be reconstructed in the
  browser.
- Warning about, or optimising for, document size. That was the producer's
  half and it is done.

## Decisions

### D1. A binding name resolves into the shared DAG — there is no forward pass

The framework's spec says a consumer "SHALL therefore be able to evaluate
the table in one forward pass, into the same scope in which it resolves
`$t` and driver values". That is a *guarantee about the table's ordering*,
not an instruction about mechanism, and this viewer does something
strictly better with it.

**Rejected — (a) a per-pass values map.** Walk the table top to bottom at
the start of each pass, evaluating each entry into a
`Record<string, number>`, and consult that map during name resolution
between `$t`/drivers and the math context. It is the obvious reading of
the spec sentence and it is about fifteen lines.

Against it:

- It computes **every** entry on every pass, whether or not anything
  re-evaluating this pass reads it. `driveTo` re-evaluates only the
  operations naming the moved driver — but a forward pass would evaluate
  all 56 of the grasshopper's entries, every one of which is over `$t`,
  to answer a driver move that touches none of them. That is the exact
  bound `share-expression-subtrees` bought, given back.
- It allocates a map per pass. D5 of the archived design removed the
  per-call scope spread for precisely this reason; re-introducing an
  allocation of the same shape one level up is a regression with a new
  name.
- It forces evaluation eagerly, so a binding whose evaluation throws (the
  `TypeError` a truthy-primitive owner produces, kept verbatim from
  jokenizer in ADR-043 D5) throws while the *scope* is being built,
  outside any expression, rather than where the flat expression would have
  thrown.
- It needs a second cache invalidation story: the map must be rebuilt
  exactly when the pass advances, which means duplicating the pass
  detection outside the module that owns it.

**Chosen — (b) intern each entry and let the name node resolve to it.**
At load, each entry's expression is `prepare`d, exactly as an operation's
is, giving a root node id. An entry naming an earlier entry parses to a
*name node* for that entry, so the table's dependency structure is already
the DAG's edge structure — no ordering pass is needed at evaluation time
because the DAG's own recursion is the order. Name resolution gains one
step:

1. `$t` (the exact name), from `scope.time`;
2. **a binding, if `scope.bindings` has this name → `valueOf(root, scope)`**;
3. the driver map, `in`-checked;
4. the OpenSCAD math context;
5. otherwise `undefined`.

Step 2 sits where the framework's rule puts it: before the driver map, so
a binding name is never a driver id. `$t` stays first and cannot collide —
no name begins with `$`.

What this buys, and what had to be checked before choosing it:

- **The memo carries.** A binding's root is a node like any other, so it
  is stamped and memoized per pass. The grasshopper's `_b0`
  (`($t * 43200.0)`) is resolved once per frame however many of the 56
  entries and 116 operations reach it — and the 17 operations that are a
  bare binding name resolve *zero* further nodes after the first.
- **Cross-expression sharing carries, and improves.** The producer's table
  is the same DAG the viewer would have hash-consed, handed over already
  built: the entries intern into the same node table the operations do, so
  an operation that spells a subexpression out and a binding that names it
  still become one node.
- **`freeNames` carries unchanged.** A name node contributes its name;
  `freeNames(root of "_b3")` is `{"_b3"}`. That is *not* the transitive
  set, deliberately — see D5.
- **Laziness.** An entry nothing reads this pass costs nothing, which is
  what makes `driveTo` on a time-only document still free.
- **The pass detection needed one addition** (D3) and **the store reset
  needed a guard** (D4). Neither is optional; both are the price of (b)
  and both are cheap.

### D2. The table is document-scoped and travels in the scope

The DAG store is **page-scoped**: one module-level table shared by every
mount, which is the whole point of ADR-043 D8. Binding names are
**document-scoped**: `_b3` is one expression in this document and may be
another in the next one republished, or in a second widget mounted beside
it on the same page.

So a module-global `Map<name, NodeId>` is out. Two mounted documents would
overwrite each other's entries and one of them would render a wrong pose,
silently — the failure this whole change exists to prevent.

The binding map therefore travels **in the evaluation scope**, exactly as
driver values do:

```ts
export interface EvalScope {
  time: number;
  drivers?: DriverScope;
  /** name -> the interned root of that binding's expression. */
  bindings?: ReadonlyMap<string, NodeId>;
}
```

`expressions.ts` knows nothing of documents: it takes a map of names to
node ids. The document-level object that owns validation, the closure and
the map lives in a new module, `bindings.ts`, which imports from
`expressions.ts` and is imported by `viewer.ts`, `tree.ts` and
`flexible.ts` — one direction, no cycle.

```ts
// bindings.ts
export interface BindingTable {
  /** name -> root node id, for the scope. Empty when the document has no table. */
  roots(): ReadonlyMap<string, NodeId> | undefined;
  /** `names` with every binding name replaced by what it transitively reads. */
  closure(names: ReadonlySet<string>): ReadonlySet<string>;
}
export const EMPTY_BINDINGS: BindingTable;      // no table: roots() is undefined
export function bindingTable(document: Manifest, sourceUrl: string): BindingTable;
```

`viewer.ts` holds one table per mounted document and builds it into
`scope()`:

```ts
const scope = (): EvalScope =>
  ({ time, drivers: drivers.scope(), bindings: bindings.roots() });
```

`roots()` returns `undefined` for a document with no table, so a version
1–3 document produces the scope object it produces today, takes the
resolution path it takes today, and compares as it compares today. "A
document with nothing to bind is unchanged" is structural here, not a
promise.

Rejected: rewriting binding names to be document-unique at load (a text
rewrite, defeating the interning that makes two identical documents share
nodes), and keying the DAG store per document (throwing away the
page-scoped sharing ADR-043 established).

### D3. The pass comparison must include the binding map

This is the correctness hazard (b) introduces, and it is not obvious.

The name node for `_b3` is **one node id for the whole page** — it is
interned by name, and both documents spell the name the same way. Its
memoized value is stamped by the pass. Consider two widgets on one page,
document A with `_b3 = floor($t)` and document B with `_b3 = ($t * 2)`,
both updated at `$t = 0.5` with no drivers. Under today's pass rule the
two scope objects carry equal values, so the pass *stands*, and B's
`valueOf` of the `_b3` name node returns **A's** memoized value. A wrong
pose, from equal-looking inputs.

So `scopesEqual` gains the binding map, compared the way the driver maps
are compared and for the same reason (`DriverStore.scope()` rebuilds a
fresh object every call, so identity alone is not a usable equality):

- identity first — true for every `evalExpr` call of one `tree.update`,
  and true across passes of one mounted document, since the table object
  and its map are built once per load;
- otherwise equal iff the same size and every name maps to the same node
  id;
- an absent map (`undefined`) counts as an empty one, so a version 1–3
  document compares exactly as it does today.

Two documents whose maps compare equal have, by construction, identical
binding expressions interned to identical roots — so sharing a pass
between them is correct, not a coincidence.

The same rule is what makes a republish safe: `manifestChanged` builds a
new table, so a document republished with a changed `_b3` gets a new map,
which compares unequal, which advances the pass. A republish that changed
nothing compares equal and costs nothing.

### D4. A store reset must not leave a held node id pointing at a new node

The second hazard of (b), and the sharper one. A `BindingTable` holds node
ids *outside* the store. `resetStore()` — reached when the last mount
releases, and when `prepare` finds the table past
`EXPRESSION_LIMITS.nodes` at the start of a new preparation — empties the
intern table and hands ids out again **from zero**. A binding map built
before such a reset then names nodes that no longer exist, or worse, nodes
that now hold something else entirely.

That is reachable in ordinary use: a long `solid develop` session
republishing hundreds of document versions is exactly the case the ceiling
exists for, and the ceiling can trip *during* a load, between preparing the
table and preparing the operations.

The guard is a generation counter:

- `expressions.ts` keeps `storeGeneration`, incremented in `resetStore()`,
  and exports `expressionGeneration(): number`.
- A `BindingTable` remembers the generation its roots were prepared in,
  and keeps the entries' expression **strings**, which are the document's
  and cost nothing.
- `roots()` compares the generation and re-prepares the entries when it
  moved. `scope()` calls `roots()` once per pass, so the check is one
  integer comparison per pass and a re-prepare only after an actual reset.

The transitive closure (D5) is keyed by *name*, computed from expression
strings, and holds no node id — so it survives a reset untouched and is
computed once per document.

Rejected: pinning the store against resets while a table is held (the
ceiling exists to bound a long session's memory, and a table would defeat
it), and re-preparing unconditionally on every pass (a map rebuild per
frame for a hazard that fires almost never).

### D5. The transitive closure lives in the document's table, and `freeVariables` keeps its meaning

Two different questions are asked of an expression and they now have
different answers:

- **Which names does this expression mention?** `freeVariables(text)` /
  `freeNames(id)`, unchanged: `{"_b56"}` for the escape wheel's rotation.
  It is per-node memoized in a page-scoped store and must stay
  document-independent, so it cannot be made binding-aware.
- **Which inputs does this expression read?** The closure: `{"$t"}` for the
  same expression. That is document-dependent, so it belongs to the
  document's table.

`BindingTable.closure(names)` replaces each binding name by what that
entry transitively reads, leaving every other name alone. It is computed
once per document, in table order, at construction: the table is
forward-only, so

```
inputs(_bK) = union over n in freeVariables(entry K):
                  n is an entry ? inputs(n) : {n}
```

reaches only entries already computed. Fifty-six entries, one pass, no
recursion depth to speak of. For a document with no table the closure is
the identity function.

**A name that is not an entry is left in the set.** That is what turns a
dangling reference — `_b99` with no such entry — into the existing
undeclared-driver refusal (D7) rather than into a silent `undefined`.

`evaluator.ts`'s public surface does not change: `freeVariables` keeps its
exact meaning, so the "a dotted driver id is one name, a call's callee is
never a variable" contract the parity work pinned is untouched.

### D6. Where the closure is applied: the free set each node already keeps

`tree.ts` and `flexible.ts` each compute, once and memoize, the union of
their own expressions' free variables. Two things read it: `needsUpdate`,
inside `update(scope, changed)`, and `animated`, which is read **outside**
any update — it is what decides whether an animation bar is built at all.

That rules out deriving the closure from the scope handed to `update`: a
document whose time dependence is entirely inside the table (which is
every operation of the grasshopper clock) would report `animated === false`
and get no timeline. The table has to be reachable from the node itself.

So the closure is applied **where the free set is built**:

```ts
this.freeVars = this.bindings.closure(rawNames);
```

and `needsUpdate`, `animated`, `touchedBy` and the flexible leaf's `free`
are unchanged — they read the same set, which now names inputs rather than
mentions. The bounding rule in the spec ("an operation is re-evaluated
only when `$t` or one of its own free variables changed") is preserved
word for word; what changed is what "its own free variables" resolves to.

The table reaches the node as an **optional trailing constructor
parameter defaulting to `EMPTY_BINDINGS`**, on `WidgetTree` (passed down
its own recursion), `WidgetTree.reconcile`, `FlexibleShape` and
`FlexibleShape.rebind`. Defaulting keeps the ~20 existing construction
sites in `tree.test.ts`, `flexible.test.ts`, `assembly.test.ts` and
`parity-fixture.test.ts` compiling and green unedited, which is what makes
those suites the parity gate for this change too.

**A republish that changes only the table still changes every node's
answer.** `reconcile` invalidates `freeVars` today where it assigns the
node's new operations — an invalidation driven by the operations having
been replaced. That is no longer sufficient, and the case it misses is an
ordinary `solid develop` one: an operation's text can stay exactly `_b3`
while the entry `_b3` changes from `($t * 2)` to `(x_axis.motor * 2)`, or
the reverse. The operations are identical strings; what the node reads is
entirely different, and its closure, its `animated` answer and its
re-evaluation bounding must all follow. A node left holding the old
closure would keep a timeline the document no longer has, or lose the one
it just gained, and would ignore the driver it now reads.

So the rule is stated on the table rather than on the operations: **a
reconcile carrying a table that differs from the one the node holds
invalidates that node's free set — and its flexible leaf's — whether or
not its operations changed.** Difference is the map comparison of D3,
identity first and then name by name, so a republish that changed nothing
invalidates nothing. `FlexibleShape.rebind` already forgets `freeVars`
unconditionally and needs only to be given the new table.

The scope's map moves with it. `viewer.ts` holds the table it loaded, and
`scope()` reads `bindings: table.roots()` off that field — so `replaceTree`
and `manifestChanged` install the newly loaded table into the field
**before** the `tree.update(scope())` that follows, in the same place and
the same order `drivers.reconcile(...)` already runs before that update.
D3 then advances the pass, because the new map compares unequal, so no
node can read a value memoized against the old table.

Rejected: a `tree.setBindings(table)` call after construction (`animated`
could be read before it, and `reconcile` would have to re-apply it — two
ways to get it wrong), and threading the table through `update` (fails
`animated`, as above).

### D7. What is refused, and when

Everything is refused in `assertRenderable`, inside `loadDocument`, before
a `WidgetTree` exists — beside the refusals already there. A `reload()` or
`manifestChanged()` that hits one fails and leaves the standing model
standing, which "A failed update leaves the model standing" already
requires.

`assertRenderable` builds the table first, then walks the document with
the closure in hand. Refusals, each naming the entry or the name:

| condition | why |
|---|---|
| `bindings` present and not an array | not the published shape |
| an entry that is not an object, or whose `name`/`expression` is not a string | not the published shape |
| a duplicate `name` | two entries, one name: which one an expression meant is unknowable |
| an entry naming itself or a later entry | the forward-only guarantee is what makes the DAG acyclic; without it, resolution recurses forever |
| an entry name equal to a declared driver id | the producer lengthens its prefix to prevent exactly this (framework D4); if it reaches here, one of the two is unreachable and the machine or its controls is wrong |
| a name that is neither `$t`, nor an entry, nor a declared driver id, reached from any operation, any `params`, or any entry | this is the existing undeclared-driver refusal, now with binding names resolved away first. A dangling `_b99` arrives here, and the message says the name is in neither table rather than guessing which the producer meant |
| an entry whose expression carries an unsupported form, or does not parse | `prepare` throws it, as it already does for an operation — the D10 refusal surface of ADR-043 now covers the table |

Two things are deliberately **not** refused:

- **A version-4 document with no `bindings` key**, or an empty one. There
  is nothing to resolve and nothing to get wrong; it renders correctly. The
  posture is to refuse what would be a wrong pose, not what is merely
  unexpected.
- **A `bindings` table on a document declaring version 2 or 3.** The table
  is read whenever it is present, whatever the declared version. Honouring
  it renders the machine the producer described; refusing it would turn a
  renderable document away over a number. The producer never publishes
  this, so the rule costs nothing and can only ever save a case.

  This was left open in the first draft and is **decided**: read the table
  whenever it is present. The posture this whole change is built on is to
  refuse a wrong pose and never a renderable document, and a version
  number disagreeing with a table the viewer can resolve is not a wrong
  pose. Refusing would be loudness for its own sake, over a case the
  producer cannot emit.

Entries the document never references are validated too — an entry naming
an undeclared driver is a malformed table by the producer's own rule, and
checking it costs one closure lookup.

### D8. Version acceptance is a set, and 5 is still refused

`RENDERED_VERSIONS` becomes `[1, 2, 3, 4]`. The refusal message keeps its
shape and now lists four numbers; version 5 is refused by it exactly as
version 4 is today. Framework D12 keeps the ladder linear and consumers
accepting by membership, so there is nothing else to decide here.

`ManifestVersion` in `types.ts` gains `4`, and `Manifest` gains
`bindings?: ManifestBinding[]` with
`ManifestBinding = { name: string; expression: string }`. The key is
absent from a document with nothing shared, so the type is optional and a
version 1–3 document is typed exactly as it is today.

### D9. The API version rises to 7

`openspec/config.yaml`'s rule: the API version "rises on incompatible
interface changes or when a capability a host may require is added."

Nothing about the mount options, the handle, or any published name
changes. But **reading a version-4 document is a capability a host may
require**, and the baseline spec already treats exactly this kind of
capability as one — its "A host requires flexible geometry" scenario reads
"WHEN a host needs `version: 3` documents rendered / THEN the declared API
version tells it whether the capability is available", and the version
rose from 4 to 5 for it. A host that mounts documents the framework now
publishes at version 4 — `solid develop`, the shop floor's live viewer,
the standalone export page — needs a number it can check before mounting,
and there is no other number: the package version is not published yet, and
`bundle.describe()` reports `apiVersion` precisely so a framework can ask
without executing the bundle.

So: **`solidNodeViewerApi` 6 → 7**, `version.test.ts` follows.

The framework's side of this is D11 of its design: the `viewer` extra
stays unbounded until there is a released viewer version to pin, and the
floor is written by the change that publishes the first viewer reading
version 4. That floor is a *package version* (`solid-node-viewer >= x.y.z`)
and cannot be written here; the API version is what a host can check at
runtime today, and this change supplies it. The two are complementary, and
recording both in `tasks.md` is what stops the follow-up being lost.

**A correction rides along.** The baseline requirement in
`openspec/specs/viewer-package/spec.md` still says the declared version
"SHALL be 5, reflecting the addition of flexible-geometry rendering",
while the shipped package has declared 6 since `real-time-playback` — that
cycle raised the number in `package.json` and its spec delta modified only
the animation requirement, so the API-version requirement never synced.
This change's delta states 7 and records the correction in the same
parenthetical style the requirement already carries for the previous drift.

### D10. The parity fixture is replaced, and its table installed

The fixture is the framework's artifact, regenerated by
`tools/generate_parity_fixture.py`, and committing it here is this change's
business. Diffed against the committed one:

| | committed | regenerated |
|---|---|---|
| `cases` | 421 | 451 |
| of those, present under the same key, with the same `expression` and the same `expected` | — | **all 421** |
| new cases | — | 30, from a `SharedValueTree` corpus |
| `bindings` | absent | 4 entries |
| `drivers` | 3 | 4 (`share` added) |
| `conversions` | 22 | 22, unchanged |
| `flexible` | — | byte-identical |

Not one pinned expected value moves and not one existing case's expression
is rewritten, so the existing parity assertions stay exactly as they are —
they are the gate that this change moved no number.

The table pins the semantics this change adds:

```json
[{"name": "_b0", "expression": "(360.0 * $t)"},
 {"name": "_b1", "expression": "floor(_b0)"},
 {"name": "_b2", "expression": "(share * 2.0)"},
 {"name": "_b3", "expression": "(_b1 + _b2)"}]
```

— an entry naming an earlier entry (`_b1`, `_b3`), an entry over a driver
rather than `$t` (`_b2`), and entries referenced from more than one case.
Of the 30 new cases, 21 name an entry and some are a bare entry name
(`"expression": "_b3"`), which is what makes the test fail loudly if the
table is not installed: `_b3` would resolve to `undefined` and
`Number(undefined)` is `NaN`.

`parity-fixture.test.ts` builds a table from `fixture.bindings` once and
adds its map to each case's scope. Each case carries its own scope object,
so the pass advances between cases exactly as it does today.

### D11. Proof: what is asserted, and why the caller check is exact

Red-first, and every assertion is on a value or on work performed, never on
elapsed time.

The one that needs its tolerance argued is the caller check on the real
document: every time-dependent operation of the version-4 grasshopper
document, at `$t` = 0, 1/3 and 2/3, against the same operations of the flat
31.6 MB document under the current evaluator.

**It is asserted with `Object.is`, plus a finiteness check, and it must
pass exactly.** The reason is measured, not assumed: expanding every
binding reference in all 116 version-4 operation expressions reproduces the
116 flat expressions **character for character** — 116 of 116, 31,611,478
characters. The two documents therefore hold the same expressions with the
same parenthesisation, and the bound reading differs from the flat one only
by *reusing* a value it already computed. Reuse of an IEEE-754 double
computed from identical inputs by an identical operation sequence is
bit-identical by definition, so any deviation at all is a defect, not
rounding — and a tolerance would hide it. The framework's own parity check
against the flat document was exact for the same reason, and it is the same
claim from the other side.

`Object.is` alone would pass `NaN` against `NaN`, which is why finiteness
is asserted beside it: both readings failing identically is not agreement.

The rest of the proof:

- **A bound document poses like the flat one.** Build the same synthetic
  document twice — once with a table, once with every reference written
  out — mount both, and compare every operation's matrix element for
  element. This is the test that would fail if step 2 of the resolution
  order were missing, or ordered wrong.
- **Dependence, both kinds.** An operation whose whole expression is an
  entry name over `$t` re-evaluates on `setTime` and makes the document
  `animated`; one over `x_axis.motor` re-evaluates on `driveTo` of that
  driver and not on `driveTo` of another; an entry reached through two
  further entries still carries both.
- **Refusals.** A binding name is not an undeclared driver (the
  grasshopper's own shape: an empty `drivers` table and every expression a
  binding name); a dangling reference is refused naming it; a duplicate
  name, a forward-only violation, a name colliding with a driver id and a
  malformed entry are each refused naming the entry; the existing
  undeclared-driver refusal is unchanged for a document with no table.
- **Isolation.** Two tables defining the same name differently, evaluated
  at the same time and drivers, give each their own value — the D3 test,
  which fails without the binding map in the pass comparison.
- **Reset.** With `EXPRESSION_LIMITS.nodes` lowered so a reset happens
  between building a table and evaluating through it, the pose is still
  right — the D4 test.
- **Work performed.** An operation that is a bare entry name resolves the
  entry's chain once; a second operation naming the same entry resolves
  zero further nodes in the same pass; a pass at a new `$t` resolves them
  again.
- **Versions.** 4 accepted, 5 refused naming it and the four rendered.
- **The fixture**, with its table installed, and the 421 pinned cases
  unmoved.

### D12. What does not change

Stated because a reviewer should be able to check it by diff:

- `capture.py`, `server.py`, `bundle.py`, and the Python suite. The capture
  path photographs a page mounting the same bundle; the framework's
  `solid snapshot --renderer web` bakes constants and never publishes a
  table at all.
- The development app (`solid_node_viewer/app`).
- The mount options, the mount handle, `SolidNodeWidget`, `solid-widget.js`,
  `data-solid-widget`, the `/_viewer` and `/build/` routes.
- The bounding rule, `operationsMatrix`, `FlexibleShape.evaluate`,
  `DriverStore`, the animation loop, `setTime`, `driveTo`.
- `evaluator.ts`'s public surface, and `freeVariables`' meaning.
- The metrics surface: still a widget-source export, still not a host
  capability.
- Every number the parity fixture pins.

## Risks / Trade-offs

- **A held node id outliving a store reset would be a silently wrong
  pose.** The sharpest risk in the change. *Mitigation:* D4's generation
  guard, checked once per pass, with a test that forces a reset between
  building a table and evaluating through it.
- **Two documents sharing a pass would be a silently wrong pose.**
  *Mitigation:* D3, with a test that mounts two tables defining one name
  differently at identical time and drivers.
- **The closure is computed from expression strings at load, and a
  document with a large table pays for it.** Fifty-six entries on the
  worst document known; the closure is one forward pass over sets of a few
  names. Immaterial against the parse it sits beside.
- **An optional constructor parameter is easy to forget.** A call site
  that omits the table gets `EMPTY_BINDINGS` and a node that does not
  follow its bindings — a still clock, not a wrong pose. *Mitigation:* the
  synthetic bound-vs-flat mount test goes through `assertRenderable` and
  `replaceTree`, which is the path that must pass it, and the caller check
  is on the real document.
- **The producer's half is not in solid-node's main yet.** This change is
  written against an archived cycle on a branch. *Mitigation:* the contract
  is the archived spec text, quoted above; the fixture and the version-4
  document this change is tested against are that cycle's own artifacts.
- **The viewer now trusts the table's forward-only ordering for
  termination.** A cyclic table would recurse forever. *Mitigation:* it is
  validated at load, before anything is evaluated, and refused naming the
  entry.

## Migration Plan

None for a host and none for a document. A version 1–3 document takes the
path it takes today, with `bindings` absent from its scope, and its
numbers are pinned unmoved by the fixture. A version-4 document, which no
released viewer can open, becomes openable.

The API version rises to 7, which is a number a host reads rather than
state it migrates. A host pinned to 6 sees 7 and decides; nothing it
already calls changes.

The one ordering fact worth writing down is the framework's, and it is
already recorded there: until this change is released, solid-node's
`expression-bindings` on main makes nearly every animated model in the
workspace refuse to open in `solid develop`, the shop floor's live viewer
and the standalone export page. This change is what closes that window,
and the `viewer` extra's version floor is the framework's follow-up once
this package is published.

## Open Questions

Whether the viewer should read a `bindings` table on a document declaring
version 2 or 3 was open in the first draft and is decided in D7: read it
whenever it is present.

1. **The `viewer` extra's version floor** is the framework's to write,
   after this package is released and has a version to pin. Recorded as a
   follow-up to report, not as work.
2. **Should a host be able to ask which document versions this build
   reads**, rather than inferring it from the API version? Today the
   mapping lives in `README.md`'s table. That would be a handle addition
   and another API bump; deliberately not this change.
