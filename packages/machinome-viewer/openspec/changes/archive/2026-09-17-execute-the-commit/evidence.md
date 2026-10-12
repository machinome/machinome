# Evidence — `execute-the-commit`

Every red seen, every number measured, and every finding reported rather
than silently resolved. Host: one Linux box, node **v24.11.1**, this
package's own worktree `solid-node-viewer/WTs/clocked-machine` on branch
`clocked-machine` over base main `4a63aaa`, planning commit `230e188`.

## 0. The base and the producer, as measured

| | |
| --- | --- |
| base suite | `npx vitest run` → **37 files, 999 tests**, 29.6 s, all green; `npx tsc --noEmit` clean |
| package before | `solidNodeViewerApi: 16`, `solidNodeDocumentVersions: [1..7]` |
| producer | solid-node branch `clocked-machine`, head **`1a959d3`** |

**The producer moved by one commit while this cycle was written, and the
corpus did not.** The design records head `2d2dc2b`; the branch head when
the corpus was taken is `1a959d3`, "fix(simulation): a non-finite commit
refuses the request; correct two scenario sentences" — a narrow adjustment
under the archived `publish-the-clocked-machine`. `tests/clocked-corpus.json`
is **byte-identical** across the two (139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`; the generator regenerates it
unchanged, which that commit's own message states and this cycle
verified by md5). What the follow-up added is a REFUSAL this cycle
therefore implements: a commit computing an infinity or a NaN refuses the
whole request by name rather than banking it. It carries the kind
`ClockedError`, which design §11's table lists only against the conflict;
the non-finite refusal is the second error of that kind, and
`src/clocked/commit.ts` says so.

## 1. The red log

Every red below was SEEN, with the failure line recorded. Where a
behaviour's test was written after the code that satisfies it, the red
was produced by MUTATING the implementation and is marked so — no red is
claimed that was not observed.

| # | task | what was red, and why |
| --- | --- | --- |
| R1 | 1.2 | `npx vitest run src/clocked/clocked-corpus.test.ts` → `Error: Cannot find module './document'`; **no tests collected at all**. The module did not exist. |
| R2 | 3.x | First run with the modules present: **9 failed / 33 passed (42)**. Eight were `its clocked.bounds[0].bound is 0, not a string` (`Stroke`, `ScaledStroke`, `Lock`, `Gate`, `Shut`, `Lift`, `Decorative`, `Untouchable`) — the loader required an expression where ADR-128 §7 publishes a NUMBER or an expression. One was `Standing step 0 stop 0 fraction: expected -0 to be +0`. |
| R3 | 1.1, 15 | R2's `-0` failure is a **finding about the harness, not the engine**: the bundler's JSON import round-trips the file through `JSON.stringify`, which turns `-0.0` into `0`, and `Standing`'s recorded stop fraction IS `-0.0`. Every clocked suite therefore reads the bytes with `readFileSync` + `JSON.parse`, which preserves it; a browser reading a real document goes through `Response.json()`, which preserves it too. A test case pins the negative zero itself. |
| R4 | 2.3 | `farSideOf(gate, 0, 0, 1, broken)` with no `scale` → `LandingInvariantError`: the ulp of zero is a denormal and 200 doublings of it reach ~4e-264. With the segment, `farSideOf(gate, 0, 0, 1, broken, 2)` lands on 1. Both directions pinned. |
| R5 | 3.3 (mutation) | `refuse()` neutered in `document.ts` → **17 failed / 12 passed** in `document.test.ts`: every refusal case is exercised by its own test. |
| R6 | 6.1 | The CLIP disabled (`clipped` returning the request unchanged) → **9 of the 13 bounded machines fail**: `Pawl`, `Stroke`, `ScaledStroke`, `Lock`, `Kinked`, `Freeze`, `Standing`, `Calculator` refuse with `JointRangeError` from the end-of-request judgement, and `Gate` fails as `admitted: expected 1000 to be 300`. `Shut` (whose only step the corpus records refused), `Decorative` and `Untouchable` (numeric chains with `shapes: {}`) and `Lift` (a clock departure) stay green, which is the clip's own shape showing through. **Design note:** §8's rejected-alternative prose predicts `Calculator` step 2 "admits `1.0`" unclipped; what an unclipped build actually does is refuse the whole request by name at §8's end-of-request judgement (`knob.travel` high bound of 0 mm reached at 6). The conclusion is the design's, sharper. |
| R7 | 5.1 | The same run: **all 17 machines that declare no bound replay exactly on the event solve alone** — the separability §8 claims, measured. |
| R8 | 4.x, 6.x (mutations) | Ten mutations of the implementation, each reverted, recording which tests bite. Table below. |
| R9 | 8.1 | `tests/test_capture.py` → 3 failed: a staged version 8 document with `--time 0.5` was refused by `assert_instant` through `carries_program`, and `carries_program({"version": 8})` was pinned `True`. |
| R10 | 9.3 | The acceptance's first browser run: `viewer.json has expressions naming undeclared drivers (_own)`. A real exported document's BINDINGS table carries the subexpressions its bounds share, and two of the fixture's name the reserved own-name (`_b33 = (_own / 6.0)`, `_b38 = (54.0 - _own)`). The corpus documents carry none, so only the page found it. `assertRenderable` now admits `machine.own` among the names a BINDINGS ENTRY may read — beside a plan's placeholders, for the same reason — and still refuses `_own` reached from an OPERATION. |
| R11 | 9.3 | Second browser run: `the dials did not turn on screen`. A request made through the `machine()` handle posed the tree but never rendered it; the `pose` hook now renders, so a gesture reaches the screen whether it came from the panel or from a host's own handle. |
| R12 | 3.4, 11.1 | The version bump turned four standing tests red at once: `RENDERED_VERSIONS`, `DOCUMENT_VERSIONS`, the version-8 refusal sentence and the package declaration. Updated, with version **9** now taking the sentence version 8 used to. |

### R8, the mutation battery

Each mutation applied to the implementation alone, the clocked suite run,
then reverted.

| mutation | tests that went red |
| --- | --- |
| `halfToEven` → `Math.round` | 4: the two `halfToEven` cases, the commit's rounding case, and the corpus's `Calculator` |
| the event landing walked with **no segment scale** | **none** — see finding F1 |
| closure 1's opening-surface `nextAfter` guard removed | 12, incl. `KinkedCounter`, `Register`, `Clearer`, `SamePair` |
| rising read at the SOLVED point rather than the landing | 17 |
| threshold without `max(0, g(0))` | 2: `Untouchable`, `Standing` |
| the zero-travel case NOT said off the crossing | 1: `Standing` |
| the stop landing walked with **no segment scale** | **none** — see finding F1 |
| the end-of-request judgement removed | 3: `Shut`, the atomicity case, the four-kinds case |
| ties by identity → the first relation only | 6: `SamePair`, `SwappedPair`, `Conflict`, … |
| commits reading the POST-event bank | 1: `SamePair` |

## 2. The corpus, as measured

`src/clocked/clocked-corpus.json` is solid-node's
`tests/clocked-corpus.json`, copied byte for byte: **139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`**, `"tolerance": {"float": 0.0}`, 30
machines, 76 steps, 722 recorded numbers. Every comparison is `toBe`
(`Object.is`) and the tolerance is READ from the file.

| | machines | steps | recorded numbers |
| --- | --- | --- | --- |
| replayed EXACTLY | 30 load; 27 replay whole | **68** | **652** |
| the clock requests this build refuses | 3 | **3** | 48 |
| deferred, standing downstream of one | — | **5** | 22 |
| total | 30 | 76 | 722 |

Derived from the file, never from a list: a departure is a `move` whose
input is that machine's own `clocked.clock`. The three are `Regulator`
step 0, `ClockAlone` step 0 and `Lift` step 0 — each its machine's FIRST
step; the five deferred are `Regulator` 1–4 and `Lift` 1. **13 of 30
machines declare a `clocked.bounds` entry, carrying 36 of the 76 steps.**
Three of the four recorded refusals are reproduced by kind and by every
qualified name their messages carry: `Counter` 6 (`TooManyEvents`),
`Conflict` 0 (`ClockedError`), `Shut` 0 (`JointRangeError`). The fourth,
`Regulator` 2's `ValueError`, is one of the five deferred.

**The census guard is derived and it bites.** With a 31st machine written
into the file on disk, six cases go red at once (the byte check, the
thirty-machines check, and all four census cases). The file was restored
and its md5 re-verified `852b86b8…`. The one-representable-value drift
guards (a landing on `UlpPair`, a stop fraction on `Pawl`) are in the
suite permanently rather than as a scratch copy, so they run on every
suite rather than once.

**No operation had to be widened, and no corpus value was edited.** Every
disagreement met is in the red log above, and every one was closed at the
operation.

## 3. Suites

| | |
| --- | --- |
| `npx tsc --noEmit` | clean |
| `npx vitest run` | **44 files, 1139 tests, all green** (from 37/999) |
| `PYTHONPATH=$PWD .venv/bin/python -m pytest tests -q` | **168 passed, 18 subtests passed**, 0 skipped, 131 s |

**One transient failure, reported rather than hidden.** One full
`npx vitest run` out of six -- the one started while the Python suite's
Chromium was still settling -- reported `1 failed | 1138 passed` without
the run being captured; five consecutive runs before and after it, and
three consecutive runs of `src/clocked/cost.test.ts` alone, are clean at
1139/1139. The only time-sensitive assertions in the suite are the cost
floors, and this cycle's are the design's own -- an order of magnitude
below ADR-060's 40.52 ms bench, so 4 ms against a measured 0.26-0.95 ms
-- which leaves four to fifteen times' headroom on an idle box and less
on a loaded one. Left at the ratified number rather than quietly widened;
the pilot should know it is the one assertion in this cycle that can be
made to fail by load alone.

The Python suite reports **no skips**: playwright, Pillow and a bundle
are all present on this host. `dist/solid-widget.js` was rebuilt in THIS
worktree with `npm run build` (gitignored, and what `bundle.py` serves);
the PRIMARY checkout's bundle was not touched, and `npm ci`,
`npm install` and `scripts/check-dist` were never run.

## 4. What a request costs

### In thread (`src/clocked/cost.test.ts`), three runs each

| | ms |
| --- | --- |
| `Calculator` one stroke (`crank` by 360) | 6.76 / 1.20 / 0.95 |
| `Calculator` one clearing sweep (`ring` by 500) | 1.69 / 1.79 / 1.43 |
| `Calculator` one CLIPPED selector move (`setting` by 1, crank off rest) | 0.97 / 0.29 / 0.26 |
| `Counter`, ten events on one path (`crank` by 3700) | 0.54 / 0.36 / 0.33 |
| `Counter` per EVENT | 0.054 / 0.036 / 0.033 |
| the whole corpus: 76 steps over 30 machines | 13.6 |

The first stroke carries the expression DAG's own warm-up; the second and
third are what a warm page pays. Nothing here poses a tree — this
machine has none — so these are the SOLVE alone.

### In a real page (`tests/test_calculator_document.py`, Chromium), three runs each

| | ms |
| --- | --- |
| `Calculator` one stroke, SOLVE AND POSE | 0.40 / 0.20 / 0.20 |
| `Calculator` one CLIPPED selector move | 0.20 / 0.30 / 0.10 |
| `Calculator` one clearing sweep | 0.70 / 0.30 / 0.30 |
| the POSE alone (a `restore`, which solves nothing) | 0.10 / 0.10 / 0.00 |

Each is asserted under **one 16 ms frame budget**, which is what makes
design §3's main-thread decision falsifiable: a request costing more than
a frame would stutter a drag, and none does by two orders of magnitude.

### Against what

ADR-060's own `Measured` table for the operating Curta, unmoved by
ADR-061: **40.52 / 42.31 / 43.70 ms per crank TICK** (idle 9.52 / 9.57 /
9.86). The clocked side's widest gesture — a whole stroke, four digits
and a carry — costs **~1 ms in thread and ~0.2 ms in the page**.

**What the comparison is NOT**, stated plainly and printed in the test
itself: it is FIXTURE-to-PROJECT (the Curta's own clocked model does not
exist yet; the clocked side is `Calculator`'s four wheels, not the
Curta's seventeen), and a running TICK is not a clocked REQUEST (a
running crank turn is a sequence of 1/240-second ticks at ~40 ms each; a
clocked crank turn is ONE request). The claim is the RATIO on one host.

## 5. `halfToEven`, cross-checked against Python

Hand-computed from the rule, with `Math.round`'s answers beside them, and
checked against the framework's own `round`:

| value | `halfToEven` | Python `round` | `Math.round` |
| --- | --- | --- | --- |
| 0.5 | 0 | 0 | 1 |
| 1.5 | 2 | 2 | 2 |
| 2.5 | 2 | 2 | 3 |
| 3.5 | 4 | 4 | 4 |
| 4.5 | 4 | 4 | 5 |
| -0.5 | 0 | 0 | -0 |
| -1.5 | -2 | -2 | -1 |
| -2.5 | -2 | -2 | -2 |

**One correction to design §14.** It lists `-0.5 → -0`. Python's `round`
returns an **int**, and an int has no signed zero: `round(-0.5)` is `0`.
`Object.is(0, -0)` is false, so a `-0` here would not compare equal to a
banked `0`, and the same task (4.6) names the cross-check against
Python's `round` as the authority. The implementation normalises an
integer result of zero to `+0` and a test pins that
`Object.is(halfToEven(-0.5), -0)` is false while
`Object.is(Math.round(-0.5), -0)` is true. Recorded rather than silently
resolved; it is a notation slip in the design, not a change of rule.

**One correction to task 6.5.** It says `Calculator`'s `halved` walks
"2, 2, 4, 4, 6". The corpus's own `move('feed', by=350)` records THREE
commits, `2, 2, 4`; `2, 2, 4, 4, 6` is the walk of a longer feed. The
corpus is the authority and the test states its number.

## 6. Findings

**F1 — the corpus does not discriminate `farSideOf`'s `scale` on the
clocked side.** Dropping the segment scale in BOTH clocked callers (the
event landing and the stop landing) leaves all 104 clocked tests green.
The reason is structural and is the framework's own: the ulp-of-zero
hazard closure 2 fixes is reached only where the walk starts from a value
of zero, and the clip **says the zero-travel case off the crossing**
rather than leaving it to the walk (`Bounded.clip`'s `crossed == 0`
branch) — which is closure 1, and which masks closure 2 on every corpus
fixture. The behaviour is pinned instead by a direct unit test of
`farSideOf` in both directions (`src/run/jumps.test.ts`), where it is
unambiguous. Worth the pilot's attention because the same is presumably
true of the framework's own suite.

**F2 — a machine's identity is not a function of the machine.**
`Clocked.described` opens with `root {klass.__module__}.{klass.__qualname__}`,
so the same class exported two ways gets two identities. The corpus's
`Calculator` publishes
`6eb8e57724cde8a15bc10a2966d02e039ba6fa4aee8c3392bb02c951064eb4a7`
(imported as `tests.clocked_project.calculator`); the acceptance fixture,
produced by `solid export tests/clocked_project/calculator.py:Calculator`,
publishes `979b1a0ef4fe214106f329844ef1c5af789dd18608b5d883eaf22bfdc73ba684`.
**Every other field of the two `clocked` objects is byte-identical** —
`clock`, `own`, all six `commits`, all three `bounds`, `limits` — as are
the `drivers`, `states`, `instructions` and `bindings` tables. Verified
directly: importing the class as `tests.clocked_project.calculator` in a
throwaway copy reproduces the corpus's identity exactly. A snapshot taken
against one export is therefore refused against the other, which is not
what ADR-128 §13 means by "a bank taken against one machine is refused
against another". A producer-side finding, for the pilot; nothing here
works around it, and the fixture's README records it.

**F3 — a published `bound` may be a NUMBER.** ADR-128 §7 and design §8
both say so; the first loader did not. A numeric bound is turned into its
own literal text so the LEVEL is one expression, and the literal is
CHECKED to read back as the very same double — a bound this evaluator
could not re-read exactly is refused by name rather than clipped against
a value the document did not state.

**F4 — a real document's BINDINGS table names the reserved own-name.**
No corpus document does; the acceptance fixture publishes two such
entries. See R10.

**F5 — the clocked limits carry no sampling resolution.** ADR-128
publishes `crossing_tolerance` and `max_crossings` and nothing else, so
`subdivisions`, `bisectionRounds` and `agreement` are **NaN** on a
clocked host: a number invented here would be a sampling resolution this
document never stated. That is safe because a clocked level is SOLVED —
every published shape is `constant`, `affine` or `kinked`, anything else
is refused at load, and a test asserts both facts over all 30 machines.

**F6 — the framework's `_leveled` is narrower than the run's
`levelOf`.** The framework refuses a non-finite level only for
`floor`, `ceil` and `%`; this viewer's RUNNING `levelOf` refuses one for
every primitive. The clocked module mirrors the framework
(`src/clocked/events.ts`'s `leveled`), so a comparison or a `sign` on an
infinite level is an ordinary reading here as it is there. The running
side is untouched.

**F7 — `move('time', …)` on a machine that declares NO clock.** The
framework answers "names this machine's clock, and X declares no time
base"; the consumer cannot, because the document publishes `clock: null`
and never the reserved word, so such a request meets the ordinary
undeclared-input refusal. Same kind (`ValueError`), different prose; the
corpus pins neither.

## 7. What is asserted UNCHANGED

- **The running corpus replays BYTE-IDENTICALLY after the `farSideOf`
  extraction**, and this was measured rather than assumed. A scratch
  harness replayed all 20 running-corpus scenarios through the engine
  and wrote every number it produced at full round-trip precision —
  1 988 lines: every bank value of every tick, every crossing's level
  and `t`, every stop's value and `t`, every command's admitted travel.
  Run against `HEAD`'s `jumps.ts` and then against the extracted one:
  **md5 `f6bb20782b1a27c6c1ab7504811588e6` both times, `diff` empty**.
  The harness was deleted; the gate was the whole cycle's precondition
  and it passed before a line of clocked code was written.
  `running-corpus.test.ts`, `run.test.ts`, `jumps.test.ts` and
  `edges.test.ts`: 180 tests, green.
- `RELEASED_DOCUMENT_VERSIONS` stays `[1, 2, 3, 4]`.
- Every version 1–7 document loads, poses, animates, drives and runs
  exactly as it did: the clocked branch is entered only when the
  document declares version 8 or carries a `clocked` object, and
  `run()` is untouched.
- Nothing of the framework, no other checkout, and no document shape.
  The framework worktree at `solid-node/WTs/clocked-machine` is clean.

## 8. Warts for the pilot

1. **What an instruction MEANS under a clocked root** (ADR-128 §14, and
   the design's own open question). The table is published with no
   runtime meaning; this build lists it DISABLED with the reason. If the
   answer is "an instruction is a request on its targets", it is a later
   cycle in both repositories.
2. **F2, the module-path in a machine's identity** — producer-side.
3. **F1, the corpus not discriminating the segment scale** — likely true
   of the framework's own suite too.

## 9. What this cycle did NOT do

Per the assignment: no ADR (candidate ADR-062), no spec sync, no
archive, no `CHANGELOG.md` / `README.md` / `docs/` edit, no commit, and
no rebuild of the PRIMARY checkout's bundle. The clock is the next
cycle's: a request that advances elapsed seconds, the events on it, and
the playback of an elapsed base.
