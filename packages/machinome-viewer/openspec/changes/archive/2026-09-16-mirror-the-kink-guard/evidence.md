# Evidence: `mirror-the-kink-guard`

All commands run inside
`/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/curta-speed`,
one job at a time. `solid_node_viewer/widget/node_modules` is the SYMLINK
to the primary checkout's own `node_modules`; it was used as is, and
neither `npm install` nor `npm ci` was run anywhere in this session.

## §0 — measured on the base (proposal time), reproduced here

Re-confirmed rather than re-derived, all matching `tasks.md`'s section 0:

- Base head `a35957d` reproduced: `npx vitest run` → **37 files, 962
  tests**, 36.92 s; `npx tsc --noEmit` clean.
- Corpus diff against the producer's `debd760`
  (`/home/asa/devel/libresolid-studio/solid-node/WTs/curta-speed`,
  read-only): committed copy md5 `7b9eb6c894c3863710cdbaac68c5fe74`
  (263 308 bytes, 19/16/356), producer's md5
  `651a3b5750c49eecad4587438dc9a85a` (267 185 bytes, 20/17/360) —
  confirmed by `md5sum` and `wc -c` on both files and `node -e` reading
  `machines.length` on the producer's file (20).
- The producer's file replayed through the shipped engine before any test
  edit: `npx vitest run src/run/running-corpus.test.ts` → 25 tests, ONE
  failure (the census assertion), 24 green including `KinkedStop` as
  scenario 20.

## Task 1 — the corpus, replaced

- **1.1** `cp` of the producer's file over the widget's copy, byte for
  byte. MD5s after the copy:

  ```text
  651a3b5750c49eecad4587438dc9a85a  solid_node_viewer/widget/src/running-corpus.json
  651a3b5750c49eecad4587438dc9a85a  /home/asa/devel/libresolid-studio/solid-node/WTs/curta-speed/tests/running-corpus.json
  ```

  Identical, and identical to task 0.2's recorded "producer's at
  `debd760`" hash. The stale copy this cycle replaced (this worktree's
  base copy, md5 `7b9eb6c894c3863710cdbaac68c5fe74`) was kept at
  `/tmp/claude-1000/-home-asa-devel-libresolid-studio/9b8ccec9-3ed5-4ac3-bcd3-9ac4f70f8826/scratchpad/stale-corpus/running-corpus.json.stale`
  for task 2.4's scratch comparison (never committed, never placed in any
  worktree).

- **1.2 RED.** `npx vitest run src/run/running-corpus.test.ts`:

  ```text
  FAIL  src/run/running-corpus.test.ts > the running corpus > is the framework's own fixture, unedited
  AssertionError: expected [ …(20) ] to have a length of 19 but got 20
   ❯ src/run/running-corpus.test.ts:226:30
      224|     expect(fixture.generated_by).toBe('tools/generate_running_corpus.p…
      225|     expect(fixture.corpus).toBe('tests/running_project/machine.py');
      226|     expect(fixture.machines).toHaveLength(19);
  Test Files  1 failed (1)
       Tests  1 failed | 24 passed (25)
  ```

  Exactly the one failure design D5.1 predicted — nothing else moved,
  and `KinkedStop` (scenario 20) was already green before the census was
  corrected.

- **1.3** Corrected `toHaveLength(19)` → `20`, the unique-name-count `16`
  → `17`, and the tick total `356` → `360`
  (`running-corpus.test.ts:226-229`). Green again:
  `npx vitest run src/run/running-corpus.test.ts` → **25/25 passed**.

- **1.4** Full widget suite with the new corpus in place, engine
  untouched: **37 files, 963 tests** (base 962 + the one new replay),
  38.17 s. No other test file moved: the six other corpus-importing
  files (`jumps.test.ts`, `program.test.ts`, `run.test.ts`,
  `cost.test.ts`, `runtime.test.ts`, `republish.test.ts`) read only the
  byte-identical shared documents.

## Task 2 — the guard, red first

- **2.1 RED.** Appending `'a stop on a kinked determiner inside a tick'`
  to `REQUIRED`, no detection written:

  ```text
  FAIL  src/run/running-corpus.test.ts > the corpus's width > exercises every feature the producer's generator requires
  AssertionError: expected [ Array(1) ] to deeply equal []
  - []
  + [
  +   "a stop on a kinked determiner inside a tick",
  + ]
   ❯ src/run/running-corpus.test.ts:587:49
  Test Files  1 failed (1)
       Tests  1 failed | 24 passed (25)
  ```

  Exactly the one feature named, nothing else.

- **2.2 implementation choice.** Design D2's option 1 was taken:
  `callsOf(expression, bindings)` is a TEST-LOCAL function beside
  `freeNamesOf`, reading a callee as an identifier immediately followed
  by `(` (`/([A-Za-z_][A-Za-z0-9_]*)\s*\(/g`) rather than extending
  `structureOf` (`src/expressions.ts`), which deliberately reports a
  call's ARGUMENTS and not its callee — an engine module this guard must
  not change for a test's benefit. The bindings-table closure reuses
  `freeVariables` exactly as `freeNamesOf` already does, and `freeVariables`
  already never reports a callee as a free name (the parser's own `Call`
  node keeps it out of that set), so the walk cannot mistake a callee for
  a name to resolve. No engine source (`src/expressions.ts`,
  `src/evaluator.ts`) was touched.

  **Constructed-fixture proof (task 2.2's own requirement)**, measured
  with `callsOf` exported for one scratch run and then reverted to
  module-local (it has no caller outside this file):

  ```text
  callsOf('(_b1 + c)', { _b1: 'min(a, b)' })   → Set { 'min' }   (through a binding)
  callsOf('min(a, b)', {})                      → Set { 'min' }   (callee found, args not)
  callsOf('lerp(a, b, t)', {})                  → Set { 'lerp' }  (no substring false positive)
  ```

  All three passed (`npx vitest run` on a temporary scratch spec file
  under `src/run/`, then the file was deleted and the `export` keyword
  reverted — `git status --short` before and after task 2.2 shows only
  `running-corpus.test.ts` and `running-corpus.json` modified, confirming
  nothing scratch survived).

- **2.3 implementation.** `kinkedLawsOf(edges, bindings)` mirrors
  `_kinked_laws` (`tools/generate_running_corpus.py:503-521`): for each
  `law` edge and each driven end whose `plans` entry (an absent `plans`
  array counting as all-null, exactly as the producer's own
  `plans = edge.get('plans') or [None] * len(edge.get('gives', ()))`) is
  null, and whose `expressions` entry for that end is present, `callsOf`
  closed over the document's bindings meets `KINKS = ['abs', 'min',
  'max']` (copied verbatim from the producer's own `KINKS` constant).
  The tick rule (mirroring `:491-493`) is inserted directly into the
  existing `for (const stop of tick.stops)` loop: a stop whose
  `stop.coordinate` is in `kinked` and whose `stop.t` is strictly between
  0 and 1 supplies the feature. `kinked` is computed once per machine,
  alongside the existing `reads` and `blockGives`/`selectors`
  derivations, from `program.edges` and the document's bindings table
  only — never from `loadProgram` or any run-engine classification.

  On `KinkedStop`'s own document — one law edge, `expressions: ["(4 +
  (72 * min(max(((lever - 113.5) / 11.25), 0.0), 1.0)))"]`, `plans:
  [null]` — `kinkedLawsOf` finds `{'slide.travel'}`, and the corpus
  records that scenario's one stop on `slide.travel` at `t = 0.478125`
  (strictly between 0 and 1), which is what supplies the feature.

- **2.4 GREEN.** Over the new (committed) corpus:
  `npx vitest run src/run/running-corpus.test.ts` → **25/25 green**,
  `uncoveredFeatures(fixture.machines)` → `[]`.

  Over the STALE copy (kept at the scratch path above, `machines` read
  with `JSON.parse(readFileSync(...))` from a temporary scratch spec
  file that imported the exported `uncoveredFeatures`, then removed):
  `uncoveredFeatures(stale.machines)` still contains `'a stop on a kinked
  determiner inside a tick'` — the copy this cycle replaces still fails
  to supply the feature, which is what makes task 1.1 load-bearing
  rather than cosmetic.

## Task 3 — the narrowed-corpus test

- **3.1** Added `expect(uncoveredFeatures(trimmed)).toContain('a stop on
  a kinked determiner inside a tick')` beside the self-read's three, the
  selection's one and the block's one, with the reason in a comment:
  `Train` DOES carry a kinked plan-less determiner (`slide.travel`, a
  `min`/`max`/`abs` law with no jump plan) but records no stop on it at
  all. Measured green immediately, as design D4 predicted: `npx vitest
  run src/run/running-corpus.test.ts` → 25/25.

## Task 4 — the suite, the types and the build

- **4.1** `npx vitest run` → **37 files, 963 tests**, 37.56 s (base:
  37 files, 962 tests, 36.92 s — the count rose by exactly the one new
  replay; task 2.2's unit checks were kept as a scratch run per the
  design's own recommendation and are not part of the committed suite,
  matching `mirror-the-gate-guard`'s own disposition of its constructed
  fixture). `npx tsc --noEmit` → clean (exit 0), matching task 0.1's
  baseline.

- **4.2** No bundle rebuild. `grep -rn "running-corpus.json" src
  --include="*.ts" | grep -v '\.test\.ts'` returns nothing: only test
  files (`running-corpus.test.ts`, `runtime.test.ts`, `republish.test.ts`,
  `jumps.test.ts`, `cost.test.ts`, `expressions.test.ts`, `run.test.ts`,
  `program.test.ts`) import the corpus. `dist/solid-widget.js` was not
  rebuilt and cannot have changed. `npm ci`, `npm install` and
  `scripts/check-dist` were never run in this worktree.

- **4.3** The Python suite was NOT run: the corpus is a widget test
  fixture imported only by TypeScript test files, is not packaged, and
  `bundle.py`, `server.py` and `capture.py` cannot observe this change.

- **4.4** Untouched-surfaces confirmed by diff:
  `git status --short` shows only `solid_node_viewer/widget/src/run/
  running-corpus.test.ts` and `solid_node_viewer/widget/src/
  running-corpus.json` modified (CHANGELOG.md and this file are the
  record, added separately). `package.json`'s `solidNodeViewerApi`
  stays `16`, `solidNodeDocumentVersions` stays `[1, 2, 3, 4, 5, 6, 7]`;
  `viewer.ts`'s `RENDERED_VERSIONS` stays `[1, 2, 3, 4, 5, 6, 7]`;
  `README.md` and `docs/adrs/` untouched; every file under `src/run/`
  other than `running-corpus.test.ts` untouched (`git diff --name-only
  -- solid_node_viewer/widget/src/run/` names only that one file).

## Deviations from the design

None. Design D2's recommended option (test-local `callsOf`) was taken
without escalation; `src/expressions.ts` was not touched.

## Follow-ups

- `solve-at-the-kink` (planning commit already on this branch, untouched
  by this cycle) is what closes task 0.4's nine bit-level disagreements —
  the searched `KinkedStop` stop's 9.09e-14 fraction and the four ticks'
  bank/admitted values that follow from it — by solving the kinked
  determiner instead of searching it. This cycle's guard is what that
  cycle's audit is read against, per its own proposal.
- The `openspec validate mirror-the-kink-guard --strict` check is green;
  archiving under the change's dated name is left for the reviewer, as
  instructed.
