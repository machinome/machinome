## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/clocked-machine`, branch `clocked-machine`,
      head `4a63aaa` (ADR-061 Accepted; package `0.2.0` unreleased,
      `solidNodeViewerApi: 16`, `solidNodeDocumentVersions: [1..7]`,
      highest EXPORT ADR 061). `npx tsc --noEmit` clean; `npx vitest run`
      → **37 files, 999 tests, 29.3 s, all green**.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`,
      `npm install` or `scripts/check-dist` here — through that symlink
      they EMPTY the primary's (it happened on 2026-09-15). `npx vitest
      run` and `npx tsc --noEmit` are safe. `dist/solid-widget.js` is
      gitignored and kept current by the package itself (ADR-059): there
      is no bundle to commit.
- [x] 0.2 The producer, recorded. solid-node branch `clocked-machine`,
      head `2d2dc2b`, eight commits ahead of main `81c5364`,
      UNINTEGRATED. ADR-125, ADR-126, ADR-127, ADR-128 accepted
      2026-09-17. `tests/clocked-corpus.json`: **139 262 bytes, md5
      `852b86b804ebd785f6e6b1f5568fb01a`**, `"tolerance": {"float":
      0.0}`, 30 machines, 76 script steps, **722 recorded numbers**.
- [x] 0.3 The refusal this cycle lifts, read off the base:
      `src/viewer.ts:1941` declares `RENDERED_VERSIONS = [1..7]` and
      `:2052-2058` refuses anything else — "declares document version 8,
      which this viewer does not render; it renders versions 1, 2, 3, 4,
      5, 6, 7." `package.json` declares `solidNodeDocumentVersions:
      [1,2,3,4,5,6,7]`, the ONE declaration `bundle.py:59-79` reads.
      `src/types.ts:84` still types `ManifestVersion = 1|2|3|4|5` and is
      already stale by two versions; this cycle brings it current.
- [x] 0.4 The corpus census, computed from the file (design §8, §15):
      **13 of 30 machines declare a `clocked.bounds` entry** — `Pawl`,
      `Stroke`, `ScaledStroke`, `Lock`, `Kinked`, `Freeze`, `Gate`,
      `Shut`, `Lift`, `Decorative`, `Untouchable`, `Standing`,
      **`Calculator`** — carrying **36 of the 76 steps**, which is why
      the clip is in this cycle. **Three machines declare a clock** —
      `Regulator`, `ClockAlone`, `Lift` — and each MOVES it at its FIRST
      step. So this cycle replays **68 of 76 steps** exactly (**652 of
      722 recorded numbers**), asserts **3** clock-request refusals as a
      stated departure, and defers **5** steps downstream of them
      (`Regulator` 1–4, `Lift` 1 — **22 numbers**). Commit `at`
      primitives covered: `floor`, `ceil`, `sign`, `>`, `>=`. Bound
      level shapes covered: `affine` (most), `kinked` (`Kinked`),
      jumped plans (`Pawl`, `Lock`, `Freeze`, `Calculator`), empty
      `shapes` (`Decorative`, `Untouchable`). Recorded refusals
      reproduced: `TooManyEvents` (`Counter` 6), `ClockedError`
      (`Conflict` 0), `JointRangeError` (`Shut` 0); deferred:
      `ValueError` (`Regulator` 2).
- [x] 0.5 The primitives already owned, so nothing is written twice:
      `branchOf` (`src/run/jumps.ts:75`), `ordinalOf`/`fromOrdinal`
      (`:108`, `:114`), `ulpOf` (`:121`), `nextAfter` (`:128`),
      `copySign` (`:135`), `along` (`:188`), `surfacesOf` (`:200`),
      `deduplicated` (`:243`), `merged` (`:264`), `kinkBreaks` (`:296`),
      `onSurface` (`:694`), `planCuts` (`:1377`). The far-side walk is
      NOT owned as a reusable piece: it is `Walk.farSide`, private, at
      `:1217-1273` — task 2.

## 1. The corpus, taken and pinned RED

- [x] 1.1 Copy solid-node `tests/clocked-corpus.json` byte for byte to
      `src/clocked-corpus.json`; assert its size, md5 and
      `tolerance.float === 0` in the test's own first case, and record in
      the file header the producer branch and commit it came from.
- [x] 1.2 Write `src/clocked/clocked-corpus.test.ts` against the module
      that does not exist yet: every machine loaded, every step replayed
      with `toBe`, the three clock steps asserted as this build's own
      refusal, the five downstream steps named as deferred, and the
      CENSUS of task 0.4 asserted. **Red**: the module is missing. Record
      the failure count.
- [x] 1.3 Write the census guard so it derives the departure FROM THE
      FILE — a `move` whose input is that machine's own `clocked.clock` —
      and never from a list, and prove it by hand-editing a scratch copy
      (adding a machine) and watching it fail. Do not commit the scratch
      copy.

## 2. `farSideOf`, extracted, with no running landing moved

- [x] 2.1 Lift `Walk.farSide` (`src/run/jumps.ts:1217-1273`) to an
      exported free function `farSideOf(branchAt, near, ownStar,
      direction, unlanded, scale = 0)`, body unchanged, step
      `ulpOf(Math.max(Math.abs(ownStar), Math.abs(scale)))`; `Walk` calls
      it with no `scale` (design §5, mirroring
      `solid_node/simulation/program.py:1578-1646`).
- [x] 2.2 **The running corpus replays byte-identically afterwards.** Run
      `src/run/running-corpus.test.ts`, `run.test.ts`, `jumps.test.ts`
      and `edges.test.ts` before and after and record that nothing moved
      by one bit. This is the gate on the whole cycle: if a running
      landing moves, the extraction is wrong.
- [x] 2.3 Unit-test `farSideOf` with a non-zero `scale` at a landed value
      of exactly `0.0`, which is ADR-128 closure 2's own case: the ulp of
      zero is a denormal and 200 doublings of it reach ~1e-263. Test it
      in BOTH walk directions, because the clip walks backwards (§8).

## 3. The document read, and refused by name

- [x] 3.1 Red: `src/clocked/document.test.ts` over the corpus's own
      embedded documents — every key of the `clocked` object read, the
      `states` table read as a second driver table, ids disjoint from
      `drivers`, expressions closed over the `bindings` table, the
      reserved own-name and each constraint's branch placeholders
      admitted as free names.
- [x] 3.2 `src/clocked/document.ts`: `loadClocked(document, sourceUrl,
      bindings)` returning the bank order (design §2), the commits, the
      constraints (chain, bound, plan, per-input shapes, node, joint,
      description) and the limits. `src/types.ts` gains `ManifestState`,
      `ManifestClocked`, `ManifestBound` and a current `ManifestVersion`.
- [x] 3.3 Red then green, one refusal per case, each naming the offending
      key and value: no `clocked` object under version 8; `program` and
      `clocked` together; a missing or mistyped key; an `at.primitive`
      outside the four kinds a commit level admits; a commit `shapes`
      value that is neither `affine` nor `kinked`; `law` not aligned with
      `targets`; a `bounds` entry with a missing key, a `side` that is
      neither `low` nor `high`, a malformed `plan`, or a `shapes` entry
      whose `level`/`jumps` are outside `constant|affine|kinked`; a
      `states` entry that is not a declaration; a name collision; an
      expression naming an undeclared identifier.
- [x] 3.4 `assertRenderable` (`src/viewer.ts:2052`, `:2079`) gains the
      version 8 branch; `RENDERED_VERSIONS` becomes `[1..8]`; a version 9
      document meets the same sentence version 8 met.

## 4. The event solve and the commit

- [x] 4.1 Red: `src/clocked/events.test.ts` — the level's crossings on a
      path, both ends closed, affine solved and kinked cut; the opening
      surface added when the path starts on one; the landing by
      `farSideOf` with the segment scale; a landing beyond the endpoint
      skipped; rising read at the landing (design §6, mirroring
      `solid_node/simulation/clocked.py:143-265`).
- [x] 4.2 Green: `src/clocked/events.ts`.
- [x] 4.3 Red then green: `src/clocked/commit.ts` — the published law
      evaluated over the PRE-EVENT bank with the input at the landing,
      the result coerced to a number, `dtype: "int"` rounded half to EVEN,
      no scaling, a non-finite result refusing (design §7).
- [x] 4.4 Red then green: `src/clocked/machine.ts` — the request loop
      (`clocked.py:2016-2113`): design-unit `by`/`to` converted through
      the driver's `scale` and `dtype` and the admitted travel converted
      back; earliest event; ties by identity of the landing; synchronous
      pre-event reads; two writers refusing by name; commits in path
      order; resume from the landing; `max_crossings` refusing; one pose
      at the end; and ATOMICITY — a refused request leaves bank and pose
      standing, proved by asserting the bank before and after a refusal.
- [x] 4.5 Red then green: `snapshot`, `restore` with the `identity`
      guard, and `reset` (design §12).
- [x] 4.6 Red then green: `halfToEven` pinned by hand-computed cases
      (`0.5 → 0`, `1.5 → 2`, `2.5 → 2`, `-0.5 → -0`, `-1.5 → -2`,
      `-2.5 → -2`), with `Math.round`'s answers quoted beside them in the
      test so the difference is visible; cross-check against Python's
      `round` in `evidence.md` (design §14).
- [x] 4.7 Red then green: the refusal kinds and their mapping onto the
      corpus's `TooManyEvents` / `ClockedError` / `ValueError` /
      `JointRangeError` (design §11).

## 5. The 17 UNBOUNDED machines replay exactly

- [x] 5.1 Turn the unbounded half of task 1.2 green: the 17 machines that
      declare no constraint carry 40 steps, of which **34** are replayed
      with `toBe` — `Regulator`'s and `ClockAlone`'s first steps move the
      clock and `Regulator`'s remaining 4 stand behind one. Record the
      step and number counts reached.
- [x] 5.2 Where any operation cannot agree bit for bit, **STOP and
      report** (design §15). Do not widen a comparison, edit the fixture,
      or omit a machine. Record every disagreement met and how it was
      closed at the operation.

## 6. The CLIP, red first on the 13 bounded machines

- [x] 6.1 Red: with the event solve green, the 13 bounded machines fail
      on their first clipped step — record which assertion fails for each
      (`Calculator` step 2 admits `1.0` where the corpus records `0.0`,
      and so on). That failure list IS the red for this group.
- [x] 6.2 Red then green: `src/clocked/bounds.ts` — per constraint, the
      chain evaluated over the bank at the request's START and bound to
      the published own-name; the bound evaluated with it; the level as
      the consumer's own subtraction per `side`; the threshold
      `h = max(0, g(0))`; the path partitioned through the published
      `plan` with `planCuts` and branches read at each piece's midpoint;
      the first exceeding found per piece with a left end already above
      it taken as the cut behind; a `kinked` skeleton cut further inside
      the piece; the zero-travel case said OFF THE CROSSING; the landing
      by `farSideOf(satisfied, 0, star, -direction, …, scale)`; and the
      fraction computed as the producer computes it, `-0.0` included
      (design §8, mirroring `clocked.py:1209-1307`).
- [x] 6.3 Red then green: the clip ACROSS constraints and the stop report
      (`clocked.py:2118-2145`) — the earliest landing truncating `delta`
      before any event is located, every constraint landing there
      reported as a stop with `coordinate`, `side`, `bound`, `value`,
      `input` and `fraction`, and a zero-travel request ADMITTED with its
      stops.
- [x] 6.4 Red then green: the END-OF-REQUEST judgement
      (`clocked.py:2147-2158`, `_commit_out_of_range` `:1479-1504`) —
      every constraint judged over the final bank through the same
      chains, with the own-name still at the request's start, refusing
      the whole request as `JointRangeError` by name and posing nothing.
      Red on `Shut`, whose only step the corpus records refused.
- [x] 6.5 Green: the 13 bounded machines carry 36 steps, of which **34**
      replay exactly (`Lift`'s first step moves the clock and its second
      stands behind it), `Calculator`
      included — its clipped `setting` moves, its ratchet-stopped crank,
      its clearing sweep, its exact-HALF integer commits (`halved`
      walking 2, 2, 4, 4, 6) and its snapshot/restore/reset.
- [x] 6.6 Turn the whole of task 1.2 green: 68 steps, 652 recorded
      numbers, 3 stated clock departures, 5 named deferrals, census
      green.
- [x] 6.7 Prove the corpus is exact and not merely green: move ONE
      recorded landing by ONE representable value in a scratch copy and
      watch the replay fail; do the same for one recorded STOP fraction.
      Do not commit the scratch copies.

## 7. The pose, the handle and the chrome

- [x] 7.1 Red then green: the clocked pose scope — the bank as the driver
      scope, `$t` sweeping rather than pinned to 0 (design §10,
      `src/run/pose.ts:27-34`) — and the tree posed once per accepted
      request through the existing change set.
- [x] 7.2 Red then green: `machine(): MachineHandle | null` on the mount
      handle, `run()` null for a version 8 document, the clock request
      refused by name (design §9), and the cadence verbs (`trigger`,
      `rate`, `step`) refused by name (design §4).
- [x] 7.3 Red then green: `src/clockedControls.ts` — drivers as handles
      with an editable design-unit readout, ± nudge and a slider where a
      `range` is declared; states and the clock as follow-only readouts;
      instructions listed and disabled; outcomes reported where the
      gesture was made, INCLUDING the stops that truncated a request;
      snapshot/restore/reset; no transport (design §13).
- [x] 7.4 Red then green, both halves of §13's claim: splitting a
      recorded request into N consecutive sub-requests over the same path
      leaves the SAME bank over the 17 machines that declare no bound
      (the machines covered named in the test); and on `Gate` it does
      NOT — one `move('crank', by=1000)` admits 300 where 200 then 800
      admits 1000, which is ADR-126's own recorded behaviour.
- [x] 7.5 `viewer.ts` renders the clocked chrome from that data, and the
      `$t` timeline is presented exactly as it is for a document carrying
      no machine.

## 8. The capture's animation rule

- [x] 8.1 Red: a staged version 8 document with a non-zero `--time` is
      refused today by `assert_instant`
      (`solid_node_viewer/capture.py:137-155`) through `carries_program`
      (`:59-74`), and `tests/test_capture.py:255-265` pins the wrong
      answer.
- [x] 8.2 Green: split the question — "carries a compiled program"
      (rest-state posing) from "animates `$t`" (true for every document
      but one carrying a `program` object) — and update the Python tests.
      A clocked staging photographs its INITIAL BANK.

## 9. The acceptance: the Curta-shaped machine in a real page

- [x] 9.1 Export `tests/clocked_project/calculator.py:Calculator`
      VERBATIM from a throwaway copy of solid-node at branch
      `clocked-machine` head `2d2dc2b` with `solid export … --no-widget`;
      commit the written `manifest.json` as
      `tests/fixtures/calculator/viewer.json` with its models, record its
      md5 and byte size, and write the fixture README on
      `tests/fixtures/clearing/README.md`'s pattern. Nothing about the
      document is edited.
- [x] 9.2 A fixture test: every model path resolves beside the document,
      the document declares version 8, carries `states` and `clocked`
      with three `bounds`, carries NO `program` and NO `controls`, and
      its identity is the producer's.
- [x] 9.3 Playwright acceptance beside `tests/test_clearing_document.py`,
      replaying the corpus's own `Calculator` expectations against the
      screen (design §16): the page opens at the initial bank;
      `operand → 4` admits 3.0; a 1100° crank request fires three strokes
      and the four dials read 2, 1, 0, 0; `setting` by 1 admits **0.0**
      with the freeze's stop reported and the knob visibly still; a −30°
      crank request admits **−2.0** on the ratchet's last seated tooth;
      `ring` by 500° clears the dials; a request naming an undeclared
      input leaves every dial where it was. Two screenshots written to
      `tests/_shots/` as evidence.

## 10. What a request costs

- [x] 10.1 `src/clocked/cost.test.ts` on `src/run/cost.test.ts`'s
      pattern: on `Calculator`, one stroke (`move('crank', {by: 360})`),
      one clearing sweep (`move('ring', {by: 500})`) and one CLIPPED
      selector move (`move('setting', {by: 1})` off rest); `Counter` per
      EVENT over its recorded 3700° request; the pose separately. Print
      every number; assert floors an order of magnitude below the bench.
- [x] 10.2 Time the same three `Calculator` requests IN THE PAGE, inside
      task 9.3's Chromium, and print them: the main-thread decision
      (design §3) is falsifiable only there — a request over one 16 ms
      frame budget would stutter a drag.
- [x] 10.3 Compare against the running Curta's recorded
      **40.52 / 42.31 / 43.70 ms per crank tick** (ADR-060's `Measured`
      table, unmoved by ADR-061) with the same care those cycles took —
      same host, node version and run count recorded, three runs — and
      state the comparison's limits in the evidence and the ADR: it is
      FIXTURE-to-PROJECT (the Curta's own clocked model does not exist
      yet) and a running TICK is not a clocked REQUEST (design §14).

## 11. Publication and the record

- [x] 11.1 `package.json`: `solidNodeViewerApi: 17`,
      `solidNodeDocumentVersions: [1..8]`; `src/version.test.ts` updated;
      `RELEASED_DOCUMENT_VERSIONS` left at `[1,2,3,4]`.
- [x] 11.2 `npx tsc --noEmit` clean and `npx vitest run` green; the whole
      Python suite run and its skips reported honestly.
- [x] 11.3 `README.md`'s version table gains the `0.2.0 | 17 | 1..8` row
      (reconciling the deliberate 13 gap note), and `CHANGELOG.md` gains
      its entry under `0.2.0 — unreleased`.
- [x] 11.4 `docs/adrs/EXPORT/ADR-062` extracted AFTER implementation from
      what was actually built — consuming solid-node ADR-125, ADR-126 and
      ADR-128, extending ADR-045 and ADR-047, building on ADR-054,
      ADR-057, ADR-058, ADR-060 and ADR-061 — and `docs/adrs/README.md`
      updated.
- [x] 11.5 `evidence.md` inside this change: every red log, the corpus
      census and its 652 numbers, the measurements of task 10, the
      `halfToEven` cross-check, and every finding reported rather than
      silently resolved.
- [x] 11.6 Record as warts for the pilot: what an instruction means under
      a clocked root (ADR-128 §14); and anything the clip's mirror turned
      up that belongs to the producer rather than here.
- [x] 11.7 Sync the delta specs into `openspec/specs/`, archive the
      change, and commit the implementation record. Two commits for the
      cycle and no more. (Synced and archived here; the implementation
      commit is the cycle's second and is the orchestrator's.)
