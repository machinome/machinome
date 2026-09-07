# ADR-043: Hash-consed expression evaluation

**Status:** Proposed

**Date:** 2026-09-07

**Change:** `share-expression-subtrees`

**Amends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

## Context

Operation and flexible-parameter expressions arrive in a published document
as text and are evaluated in the browser on every frame an input changes.
Until now that meant `jokenizer`: `tokenize` to a tree, a module-level cache
from expression string to that tree, and `evaluate` — a visitor that walks
every node of the tree, every time.

That is affordable only while expressions are small, and the producer does
not guarantee they are. solid2's `OpenSCADConstant` builds an expression by
string concatenation, so every reuse of a value pastes its full text again.
3DPrintedClocks' `wall_clock_53_grasshopper` publishes 31.6 MB of
expressions: 116 operations, 30 distinct strings, 4.28 million parsed nodes
— and 293 distinct subexpressions. The viewer walked 6.25 million nodes per
animated frame (~0.5 s per frame) and retained 723 MB of parse trees for the
life of the page.

Nothing about the numbers is wrong, and no document format change can reach
the documents already published. The cost is structural: the evaluator has
no way to notice that it is computing the same thing again, because two
identical subtrees are two objects and its visitor has nowhere to put a
memo.

## Decision

The viewer evaluates a **hash-consed DAG**, not a parse tree.

- `jokenizer`'s `tokenize` stays the parser — the grammar, the literal rules
  and the precedence are the parity-proven half of the package — and its
  `evaluate` is replaced by an evaluator this package owns.
- Each parsed expression is interned bottom-up into one module-level table
  keyed structurally (kind, operator or name, and the ids of already-interned
  children), so structurally identical subtrees become one node across the
  whole document, not only within one expression. The parse tree is dropped
  as soon as its root is interned.
- Evaluation walks the DAG with a memo indexed by node id and stamped by an
  evaluation pass, where a pass is a set of scope values: an identity fast
  path, and behind it a value comparison that recurses through the driver
  map, because the viewer rebuilds those nested maps on every call and
  identity would report them changed every time. One frame therefore costs
  the distinct subexpressions the frame's operations read.
- The OpenSCAD semantics move onto the builder and the evaluator unchanged:
  degree trig, `mod`, `ln`, `log(base, value)`, the exponent-literal rewrite
  in front of the parser, and `^` folded into a `pow` call with the rule
  that a leading unary minus stays outside it. Name resolution keeps the
  order the old spread scope established: `$t`, then the driver map, then
  the math context, reproducing jokenizer's member-access edge cases
  (a missing or falsy owner yields `undefined`; a truthy primitive owner
  throws the same native `TypeError`) rather than tidying them.
- A dotted driver id interns as ONE name node, so free variables — which
  bound re-evaluation for drivers and flexible parts — are read off the DAG
  with exactly the rules they had: a dotted id is one name, a call's callee
  is never a variable.
- The table is retained while a viewer is mounted and emptied when the last
  one is disposed of, with a node ceiling behind that for long
  republish sessions. It is a pure cache: emptying it costs a re-parse and
  can never cost a wrong number.
- The win is asserted as counted subexpression resolutions, exported from
  the widget's source for its own tests. It is not on the host handle, so
  the viewer API version does not move.

## Alternatives considered

- **Keep jokenizer's `evaluate` and cache more.** Rejected: its visitor
  cannot memoize — there is no node identity to key on — and caching whole
  expressions is what already exists and what costs the 723 MB.
- **Compile each expression to JavaScript with `new Function`.** Rejected:
  a second numeric implementation to hold in parity for a win the memo
  already delivers (~24,000× fewer node visits per frame), and `new
  Function` is refused under a strict Content-Security-Policy, which a
  static export may well be served under.
- **Wait for the producer to emit shared subexpressions.** Rejected as the
  answer *here*: it is the right fix upstream and is a separate solid-node
  change, but it cannot help any document already published, and the viewer
  must render what the framework has already written.
- **De-duplicate the text before parsing.** Rejected: a textual
  common-subexpression pass is a parser in disguise, and it would still hand
  the tree walker the work.
- **Intern per document rather than per page.** Rejected as the primary
  key: sharing across documents costs nothing and helps the development
  server's republishes; lifetime is handled by mount refcounting instead.

## Consequences

- A frame of the grasshopper clock resolves 255 nodes instead of walking
  6.25 million; sixty frames take 29 ms where the pilot measured about half
  a second each.
- Retained expression state for a document falls from hundreds of megabytes
  of parse trees to a table of a few hundred nodes.
- Preparing an expression costs the interning walk on top of parsing
  (measured ~16% more one-time work for the clock, 8.86 s against 7.65 s);
  frame cost falls by four orders of magnitude.
- `freeVariables` becomes a walk of distinct nodes rather than of the whole
  parse tree, which speeds the load path that reads dependencies.
- This package now owns a numeric evaluator. The producer-parity fixture,
  which was already the contract, becomes the thing that holds it honest,
  and a builder-level comparison against jokenizer's own `evaluate` guards
  the seam while the two coexist.
- An expression form the DAG does not support — an inline function — is
  refused by name when the document is loaded, beside the existing refusals
  for an unknown document version, an unknown flexible technology and an
  undeclared driver id, because the loader's own free-variable walk is what
  prepares every expression. Nothing the producer emits carries one, and no
  such expression can first be met inside a frame.
- The viewer API version stays 6: no interface change and no capability a
  host may require.
