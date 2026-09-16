# Design: mirror the kink guard

## 1. What this cycle is

A FIXTURE-AND-GUARD cycle, of exactly the shape
`openspec/changes/archive/2026-09-16-mirror-the-gate-guard/` established:
the producer regenerated its conformance corpus and added a required
feature to its generator; this repository holds a byte-for-byte copy of
that corpus and a hand-written mirror of the generator's coverage rule,
so both need the same update, and the update is proved against THIS
engine rather than assumed from the producer's.

No line of engine source changes. The evidence that the engine needs no
change is measured, not asserted (§3).

## 2. The base, measured

Worktree `solid-node-viewer/WTs/curta-speed`, branch `curta-speed`, head
`a35957d`. `npx vitest run` → 37 files, 962 tests, 37.3 s; `npx tsc
--noEmit` clean. Package `0.2.0` unreleased, `solidNodeViewerApi: 16`,
`solidNodeDocumentVersions: [1..7]`, highest ADR 060.

Do NOT run `npm ci`, `npm install` or `scripts/check-dist` in this
worktree: `solid_node_viewer/widget/node_modules` is a SYMLINK to the
primary checkout's, and `npm ci` through it empties the primary's.

## 3. The corpus diff, exactly

Against `solid-node/WTs/curta-speed`'s `tests/running-corpus.json` at
`debd760` (read-only):

- md5 `7b9eb6c894c3863710cdbaac68c5fe74` (263 308 bytes) here, against
  `651a3b5750c49eecad4587438dc9a85a` (267 185 bytes) there.
- `generated_by` = `tools/generate_running_corpus.py`, `corpus` =
  `tests/running_project/machine.py` and `tolerance` = `{float: 1e-09}`
  in both.
- 19 → 20 entries, 16 → 17 distinct machine names, 356 → 360 ticks.
- Scenario keys `(name, dt, steps)`: one ADDED, `('KinkedStop', 0.1, 4)`,
  at the END of the list; none removed; every shared key's entry equal
  under a key-sorted comparison — script, document and ticks alike.

`KinkedStop` is the producer's own §11 case C: a `version: 5` document
with ONE law edge, `lever drives slide.travel` published as
`(4 + (72 * min(max(((lever - 113.5) / 11.25), 0.0), 1.0)))` with
`affine: [false]` and `plans: [null]`, and a span `slide.travel`
high `40`. The script moves `lever` by 40 over 0.1 s at tick 1; the bound
lies on the SLOPED piece and the path starts on the FLAT one, so a
consumer that divides once over the whole tick puts the stop at half way.
The corpus records the stop at `t = 0.478125`, `lever` committed at
`119.125`, `h0` blocked with `19.125` admitted.

## 4. The engine needs no change, and here is the measurement

The refreshed file replayed scenario by scenario through the SHIPPED
engine on this base: all 20 green. Running the whole `src/run/` suite
with the new file dropped in gives ONE failure — the census assertion —
and 339 other tests green. So the corpus swap alone breaks nothing.

`KinkedStop` passes because the viewer SEARCHES that determiner (64
samples plus bisection, `run.ts`'s `searched`) and the search lands
9.09e-14 from the producer's solved answer, inside the corpus's own
`1e-9` relative window. That is the tolerance doing its job, and it is
exactly what ADR-123 predicted of a consumer that has not learned to cut
at a kink: "correct, and slower".

**It is worth recording that this is the ONLY place the two runtimes are
not bit-identical.** Of the 2 018 floats the refreshed corpus records,
this engine reproduces 2 009 exactly and disagrees on 9 — the stop's
fraction, and the `lever` bank value and `h0` admitted travel of all four
ticks that follow from it. The `solve-at-the-kink` cycle closes that, and
this design states the number so that cycle's audit has a baseline it did
not compute itself.

## 5. The guard, and what it must and must not read

`uncoveredFeatures` (`src/run/running-corpus.test.ts`) is a deliberate
SECOND implementation of `tools/generate_running_corpus.py`'s
`uncovered_features`, written against the corpus's own documents and tick
logs and never against `loadProgram`. The file states why: it must be RED
on a narrowed corpus even when the engine is broken. That rule is
unchanged here, and it acquires a second edge after `solve-at-the-kink`:
the engine will then classify kinks itself, and this guard SHALL still
not ask it.

### D1. The producer's derivation, verbatim

`_kinked_laws(program, bindings)` (`tools/generate_running_corpus.py`):

- for each edge with `kind == 'law'`;
- for each driven end `index`, where `plans[index] is None` (a law with
  NO jump node at all — `plans` absent entirely counts as all-null);
- where `expressions[index]` exists and is not null;
- the set of functions that expression CALLS, closed over the document's
  `bindings` table — `_calls` walks the parsed expression, collects every
  `call` node's operator, and pushes the expression of any `name` node
  the bindings table defines — meets `{'abs', 'min', 'max'}`;
- then that end's driven id is a KINKED DETERMINER.

And in the tick loop:

```python
for stop in tick['stops']:
    if stop['coordinate'] in kinked and 0 < stop['t'] < 1:
        seen.add('a stop on a kinked determiner inside a tick')
```

### D2. What the mirror needs that the guard does not already have

The guard already walks a document's bindings table for FREE NAMES
(`freeNamesOf`, mirroring `free_names`). It has no walk for CALLS. The
widget's `freeVariables` deliberately does not report a callee — its own
comment says "the callee is never a variable" — so `callsOf` is a new
function beside `freeNamesOf`, of the same shape:

- parse the expression;
- collect the name of every call node's callee;
- for every free NAME the bindings table defines, push that binding's
  expression and continue, so a kink reached only through a shared
  subexpression is found.

`structureOf` in `src/expressions.ts` deliberately reports a call's
ARGUMENTS and not its callee, so the guard cannot read the callee
through it either. Two ways are open and the applier picks one, with the
reason recorded in `evidence.md`:

1. a small regex/parse over the expression text inside the test file,
   reusing `freeVariables` for the binding-name walk — a test-local
   reading, in the spirit of the guard's "never borrowed from the
   engine";
2. extending `structureOf` with the callee's name.

**Option 1 is the one this design recommends**, for the guard's own
stated reason and because option 2 changes an engine module for a test's
benefit. Whatever is chosen, the guard SHALL find `min`/`max` reached
through a binding: none of the corpus's documents needs it today
(`KinkedStop` has an empty bindings table), so the applier proves it on a
constructed fixture rather than on the corpus.

### D3. Where the entry goes

`REQUIRED` gains `'a stop on a kinked determiner inside a tick'` in the
producer's own position — LAST, after `'an in-block gate crossing inside
a tick'` — and in the producer's own spelling. The list is a mirror; a
re-ordering or a re-wording is a drift.

### D4. The narrowed-corpus test

`'is refused when the corpus is narrowed'` trims the corpus to `Train`
and asserts a list of features it no longer covers. `Train` DOES carry a
kinked plan-less determiner (`slide.travel`) but records no stop on it at
all, so the new feature joins that list. That is the assertion, and it is
also the finding that makes the new scenario necessary rather than
decorative.

### D5. Red first, in this order

1. The corpus lands (task 1.1). The census assertion is RED —
   `expected [ …(20) ] to have a length of 19` — and nothing else in the
   suite is. Record the text.
2. The census is corrected (19 → 20, 16 → 17, 356 → 360). Everything is
   green again, and the guard is SILENT about the new feature because
   `REQUIRED` does not name it — which is the hole.
3. `REQUIRED` gains the entry (task 2.1). The width test is RED, naming
   exactly `'a stop on a kinked determiner inside a tick'`, for BOTH
   corpora. Record the text.
4. The derivation is mirrored (tasks 2.2, 2.3). GREEN over the new
   corpus; and the SAME guard over the stale copy still names the
   feature, which is what makes task 1.1 load-bearing. Record both.
5. The narrowed-corpus assertion (task 3.1).

## 6. What is deliberately not done

- **No engine change.** Measured in §4: the engine replays all 20
  scenarios green as it stands.
- **No ADR.** A fixture refresh and a coverage guard decide nothing about
  the architecture; ADR-047 already decided that the corpus is the
  contract, and ADR-123 (the producer's) already decided that the
  published `affine` flag stays two-valued. `mirror-the-gate-guard` is
  the precedent for the disposition.
- **No bundle rebuild.** No `src/` module imports the corpus, so
  `dist/solid-widget.js` cannot change. The applier confirms by diff
  rather than by rebuilding.
- **No second scenario.** The producer added one; this repository mirrors
  what the producer publishes and does not invent corpus entries.

## 7. Risks

- **A mirror that drifts by re-wording.** The entry's text is a string
  compared against nothing — a typo makes the guard permanently red or
  permanently silent. Mitigated by copying the producer's line and by
  task 2.1's recorded RED naming the exact string.
- **A `callsOf` that stops at a binding name.** It would miss a kink
  reached through a shared subexpression and quietly under-report. D2
  requires a constructed fixture for that case; the corpus does not
  exercise it.
- **A `callsOf` that counts a callee as a free name.** The opposite
  error, which would classify `lerp(a, b, t)` as a kink if the text
  happened to contain `min` as a substring. A regex over identifiers
  followed by `(` is the shape to get right, and it is why D2 prefers a
  parse to a search.
