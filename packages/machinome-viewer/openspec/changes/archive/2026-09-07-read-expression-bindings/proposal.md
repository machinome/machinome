## Why

The framework has stopped writing the same arithmetic out over and over,
and the document it now publishes is one this viewer refuses.

`share-expression-subtrees` (ADR-043) fixed the *frame*: a repeated
subexpression is resolved once per evaluation pass, whichever operation
asks for it. It could not fix the *wire*. 3DPrintedClocks'
`wall_clock_53_grasshopper` still publishes 31,638,555 bytes, of which
31,611,478 are operation expression text — 116 expressions, 30 distinct
strings, about seven million written subexpressions over 263 distinct
ones — and still costs ~7.65 s of one-time parsing and ~111 MB resident
as strings before a frame is drawn. That redundancy is in the document,
and only the producer can remove it.

The producer now removes it. solid-node's `expression-bindings` cycle
(archived `2026-09-07-expression-bindings`, ADR-080, on branch
`expression-bindings` and not yet in the framework's main) publishes each
subexpression that occurs more than once as one named entry in an ordered
top-level `bindings` array, referenced by bare name everywhere it
occurred, and declares **`version: 4`** for a document carrying one. On
the grasshopper clock, measured by the framework at implementation:

| | before | after |
|---|---|---|
| expression text in the document | 31,611,478 B | 3,130 B (**10,099×**) |
| the document itself | 31,638,555 B | 32,227 B (**981.7×**) |
| longest published expression | 3,322,703 chars | 212 chars |
| bindings published | — | 56 |
| numeric parity against the flat document | — | exact, 348 checks, 0 mismatches |

**The empirical chain.** 3DPrintedClocks needed a grasshopper escapement
→ building it from reused symbolic values published a 31.6 MB document
→ the framework now publishes a shared subexpression once, as a named
binding, and calls that document version 4 → **this viewer must read it.**

The contract is specified on the framework side and this change is
written against it: `specs/export/spec.md`'s "A shared subexpression is
published once", "Binding names cannot collide with anything the consumer
resolves" and — the requirement this change is the other half of — "What a
binding name means to a consumer", whose three rules are that dependence
flows transitively through a binding, that a binding name is resolved
before any undeclared-driver refusal, and that every other name is
unchanged.

**What this viewer does with a version-4 document today**, checked
against the real one (`grasshopper-viewer-v4.json`, 32,227 bytes,
`version: 4`, 56 bindings, 46 nodes, 76 operations, an empty `drivers`
table). Three separate refusals stand between it and a frame, and the
third is the one that would be silent:

1. `assertRenderable` refuses the version: `RENDERED_VERSIONS` is
   `[1, 2, 3]`.
2. Were the version accepted, every one of the 116 operation expressions
   names `_b0`…`_b55`, and the document's `drivers` table is empty — so
   the undeclared-driver refusal fires on 56 names at once.
3. Were both accepted, **nothing would move.** Not one of the 116
   operation expressions contains `$t` as text; 22 of them are
   time-dependent, every one of them through the table. A viewer reading
   free variables off the expression alone finds no `$t` anywhere in the
   document, so `WidgetTree.animated` is false — the timeline bar is never
   built, and no operation is ever re-evaluated when time changes. The
   clock would mount, stand still, and offer no way to play it.

That third one is why this is a consumer change and not a version-number
edit.

## What Changes

- The viewer **accepts document version 4** and reads its `bindings`
  table: an ordered array of `{name, expression}` entries, each naming
  only `$t`, declared driver ids, and entries before it.
- A binding name resolves **where it is used** — in an operation's
  expression, in a flexible leaf's `params`, or in another entry — to the
  value of that entry's expression under the same inputs, and it is
  resolved **before** the name is judged a driver id, so a binding name is
  never reported as an undeclared driver.
- **Dependence flows through the table.** An operation naming an entry
  that resolves through to `$t` is a time-dependent operation: it is
  re-evaluated when time changes, it makes the document animated, and it
  gets a timeline. An operation naming an entry over `x_axis.motor`
  re-evaluates when that driver moves and not otherwise. The bounding rule
  itself — a node is re-evaluated only when an input it reads changed — is
  unchanged; what changes is that the inputs are read through the table.
- An entry is evaluated **only if something reads it**, and then once per
  evaluation pass, like any other subexpression: bindings enter the
  existing hash-consed DAG rather than a forward pass of their own
  (`design.md` D1). A binding shared by fourteen operations costs one
  resolution per frame.
- The table is **document-scoped**. Two documents mounted on one page may
  each define `_b3` differently; neither can read the other's value
  (`design.md` D2, D3).
- A table the viewer cannot resolve is **refused when the document is
  loaded**, beside the refusals already made there: a malformed array or
  entry, a duplicate name, an entry naming a later entry or itself, a name
  colliding with a declared driver id, and a name referenced by the
  document but absent from the table. The refusal names the entry. Never
  a wrong pose.
- The committed cross-runtime **parity fixture is replaced** by the
  framework's regenerated one: 451 cases (the 421 already pinned, each
  under the same key, expression and expected value, plus 30 new), a
  4-entry `bindings` array, and a fourth driver `share`. The viewer's
  `parity-fixture.test.ts` installs the table so the cases that name
  entries resolve, which is how the fixture now pins the table's semantics
  and not only the function semantics.
- The viewer **API version rises to 7**. Reading a version-4 document is a
  capability a host may require — `solid develop`, the shop floor's live
  viewer and the standalone export page all mount documents the framework
  will publish at version 4 — and it is exactly the kind of capability the
  API version rose to 5 for when version-3 flexible documents arrived
  (`design.md` D9).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: three new requirements — a named binding resolves
  where it is used; dependence flows transitively through a binding; a
  bindings table the viewer cannot resolve is refused at load — and three
  modified ones: the loader accepts version 4 and reads the table, the
  producer-numerics requirement covers a corpus carrying bindings, and the
  declared API version rises to 7 (correcting a baseline that still records
  5 while the shipped package declares 6).

Capabilities needing no delta, and why:

- `viewer-distribution`: the entry point already reports the declared
  `apiVersion`; this change moves the number, not the contract that
  publishes it.
- `development-server`, `snapshot-capture`: neither reads an expression.
  `solid-node-viewer serve` serves the bundle and `capture` photographs a
  page; a version-4 document reaches them through the same widget. The
  framework's `solid snapshot --renderer web` stages a keyframed, numerically
  baked document that shares nothing and stays at version 2 or 3
  (framework ADR-080), so the capture path never meets a table at all.
- `viewer-assembly-navigation`: assembly identity is names and structure,
  never an expression.

## Impact

- `solid_node_viewer/widget/src/bindings.ts` — **new**: the document's
  binding table. Validation at load, the name→root map the scope carries,
  and the transitive free-input closure, all document-scoped.
- `solid_node_viewer/widget/src/expressions.ts` — `EvalScope` gains an
  optional binding map; name resolution consults it between `$t` and the
  drivers; the pass comparison includes it; a store generation counter so a
  reset can never leave a held node id pointing at a reallocated node.
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS` becomes
  `[1, 2, 3, 4]`; `assertRenderable` builds and validates the table and
  resolves free names through it; `loadDocument` hands the table back;
  `scope()` carries it; `replaceTree` and `manifestChanged` install it.
- `solid_node_viewer/widget/src/tree.ts`, `flexible.ts` — the free-variable
  set each node already computes is closed over the table, so `animated`
  and the re-evaluation bounding both follow a binding, and a reconcile
  carrying a different table invalidates that set even when the node's
  operations did not change. No change to the bounding rule, to
  `operationsMatrix` or to `evaluate`.
- `solid_node_viewer/widget/src/types.ts` — `ManifestBinding`,
  `Manifest.bindings`, and `ManifestVersion` gains `4`.
- `solid_node_viewer/widget/src/parity-fixture.json` — replaced with the
  framework's regenerated fixture; `parity-fixture.test.ts` installs its
  table.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi` 6 → 7;
  `version.test.ts` follows.
- `solid_node_viewer/capture.py`, `server.py`, `bundle.py`, the development
  app, the mount options and the handle — **unchanged**. They mount the
  same bundle through the same contract; nothing about a binding reaches
  them.
- `README.md` (the version table gains document version 4 at API 7),
  `CHANGELOG.md` (0.1.0, unreleased), and
  `docs/adrs/EXPORT/ADR-044-a-binding-name-resolves-into-the-shared-dag.md`,
  promoted on archive.
- **The producer half is a separate change in a separate repository** and
  is done: solid-node's `expression-bindings`, archived on its branch. This
  change carries no framework edit. The `viewer` extra's version floor —
  the first published viewer that reads version 4 — is the framework's
  follow-up once this package is released (framework `design.md` D11);
  nothing here can write it.
- **Ordering.** The framework cycle is integrated into solid-node's main at
  the pilot's discretion, and until this change lands, a version-4 document
  is refused by every viewer in the workspace. This change is what makes
  that ordering free.
