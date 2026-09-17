## Why

solid-node's ADR-125 gave the framework a third state discipline — a
machine with MEMORY and no cadence: a few retained values, closed-form
positions between events, and a COMMIT of the retained values at each
event. ADR-126 gave it interlocks, ADR-127 a clock, and ADR-128 lifted
the publication refusal the first three held: a tree that declares a
`State` now publishes a **version 8** document carrying a `states` table
beside `drivers` and a `clocked` object — the compiled machine itself,
with its commits, its constraints, its reserved names and its two limits.

This viewer renders versions 1–7 and refuses version 8 by name
(`src/viewer.ts:1941`, `2052`), which is correct (ADR-034, ADR-110) and
is now the only thing between a clocked machine and a browser:

```text
…/viewer.json declares document version 8, which this viewer does not
render; it renders versions 1, 2, 3, 4, 5, 6, 7. The document is written
to a schema this build cannot read: refusing it rather than rendering
part of a machine it does not understand.
```

The originating project is the Curta
(`projects/Calculators/Curta-Type-I-3x`). Its RUNNING model reaches the
browser today and costs **40.52 / 42.31 / 43.70 ms per crank tick** on
ADR-060's own bench, a figure ADR-061 then measured again and did not
move — a generality the machine does not use, paid once for every 1/240
of a second of the machine's own time.
The clocked model exists to beat that, and it is worth nothing to its
pilot until a browser can crank it. ADR-128 says so in its own
consequences: "the viewer's cycle owes a bit walk, not an epsilon walk".

**The contract is the corpus, and it is EXACT.** The framework publishes
`tests/clocked-corpus.json` — 30 machines, 30 scenarios, 76 steps,
139 262 bytes — carrying `"tolerance": {"float": 0.0}` as a FIELD of the
file rather than a convention of its reader. A clocked executor has no
window inside which it declines to distinguish two values: two relations
are ONE event exactly when their landings are the SAME float, and the
corpus's `UlpPair` machine is built on two surfaces one ulp apart. A
consumer within `1e-9` of a landing would merge events this framework
keeps apart.

**The interlocks come with it, because the corpus says they must.**
Measured on that file: **13 of the 30 machines declare a compiled
constraint** — a `clocked.bounds` entry — carrying 36 of the 76 steps,
and the Curta-shaped `Calculator` is one of them. A request on such a
machine is CLIPPED before a single event is located (ADR-126): the
declared range is a STOP, the travel is truncated to where the machine's
interlocks allow, and what the commits carried is judged again at the
end. A build that skipped the clip would not merely lose the stop
report — it would locate events on a path the machine never travels
(`Calculator`'s own step 2 admits `0.0` where an unclipped build admits
`1.0` and slides a selector the crank holds). So this cycle executes the
clip as well as the commit, and the only thing it leaves to the next is
the CLOCK: a request that advances elapsed seconds, the events on it, and
the playback of an elapsed base.

## What Changes

- **Version 8 is read.** `documentVersions` becomes `[1 … 8]` and the
  declared widget API version rises **16 → 17**: executing a clocked
  machine is a capability a host may require before it mounts a bundle
  that would refuse the Curta by name. `bundle.py`'s
  `RELEASED_DOCUMENT_VERSIONS` does not move.
- **A version 8 document is LOADED and VALIDATED field by field**: the
  `states` table (a driver's five fields, and never a handle), and the
  `clocked` object — `identity`, `clock`, `own`, `commits`, `bounds`,
  `limits` — with a refusal BY NAME for every shape this engine cannot
  execute, on the surface `loadProgram` already refuses a program on.
  The bank's id order is DERIVED (drivers, then states, then the clock):
  ADR-128 §4 publishes no `coordinates` table because every number is
  already in the document.
- **A REQUEST is executed, synchronously, on the main thread.** One
  input moves along a straight path from its banked value; every
  `commits` entry whose `shapes` names that input is examined; crossings
  are solved (affine by division, a kinked level cut at its own `abs` /
  `min` / `max` breakpoints); the landing is the nearest representable
  value on the FAR side of the surface, found by a bisection in float
  ORDINAL space with its first step sized by the SEGMENT (ADR-128
  closure 2); only RISING steps fire; a crossing belongs to the request
  whose path contains its LANDING (closure 1); relations landing on the
  SAME float are one synchronous event whose reads are all PRE-EVENT;
  commits are in path order and the solve resumes from each landing; an
  `int` target is rounded half to EVEN, once. Then ONE pose from the
  bank, through the existing expression DAG. A refused request leaves the
  bank, the tree and the pose exactly as they stood.
- **A declared STOP CLIPS the request.** Per `bounds` entry whose
  `shapes` names the moving input: the published chain evaluated over the
  bank at the request's START and held under the machine's reserved
  own-name for the whole request; the bound evaluated with it; the LEVEL
  formed by the consumer's own subtraction per `side`; the threshold
  `h = max(0, g(0))`; the path partitioned at the level's own jump
  surfaces through the published plan and each piece solved by its
  published classification; the EARLIEST landing across every constraint,
  found by the SAME far-side walk run backwards so it lands on the last
  value that still satisfies; and `delta` truncated there BEFORE any
  event is located. A request stopped at zero travel is ADMITTED with its
  stop — an interlock that holds is the machine working. Each stop is
  reported per (coordinate, side) with the bound, the coordinate's value,
  the input's value and the fraction. After the last event and before the
  pose, every constraint is judged again over the FINAL bank: a COMMIT
  that carried a coordinate out of range refuses the whole request by
  name.
- **The clocked conformance corpus is committed and replayed EXACTLY** —
  bit for bit, `tolerance.float` read from the file and `toBe` and
  nothing else — over ALL 30 machines: 68 of the 76 steps and 652 of the
  722 recorded numbers, their whole banks, admitted travels, commits with
  landings and targets, stops with their bounds and fractions, and three
  of the corpus's four recorded refusals by KIND and by the qualified
  names their messages carry. The 8 steps left are the CLOCK's: three
  clock requests this build refuses instead of admitting, and the five
  steps standing downstream of them. A CENSUS guard derives that
  partition from the file (76 = 68 + 3 + 5) so a regenerated corpus
  cannot narrow this suite by accident.
- **A maker operates a clocked machine on screen.** A third chrome
  (`clockedControls.ts`), pure data like the running one: a driver is a
  HANDLE whose every gesture submits one `move(id, {to})` request and
  reports its outcome — the travel admitted, the STOPS an interlock held
  it at, or the refusal's own message — where the gesture was made; a
  state is a follow-only READOUT and never a handle; a clock is a readout
  too; declared instructions are listed DISABLED, because ADR-128 §14
  publishes them with no runtime meaning; snapshot, restore and reset are
  session-local and `identity` guards a restored bank against another
  machine.
- **`$t` animates a clocked document while its bank stands** (ADR-128
  §10): a version 8 document publishes an ordinary `animation` object,
  so the timeline is presented exactly as it is for a version 1–4
  document. Under an elapsed root `time` is a bank value STANDING at its
  initial; the timeline plays nothing of it, and a `move` naming the
  clock is refused by name until the next cycle.
- **The capture's animation rule is corrected.** `carries_program` reads
  `version >= 5` as "carries a program, and therefore has no animation
  cycle" (`solid_node_viewer/capture.py:59-74`), which makes
  `assert_instant` refuse `--time` on a version 8 document that DOES
  animate `$t`. A clocked document is photographed at its initial bank,
  and a non-zero `--time` is honoured rather than refused.
- **A version 8 document with GEOMETRY runs in a real page**: the
  framework's own `tests/clocked_project/calculator.py:Calculator` — the
  Curta-shaped fixture, four wheels of one class, a stroke over four
  digits and an operand, a clearing relation per wheel, a selector wired
  through a port, an anti-reversal ratchet and an off-rest freeze —
  exported verbatim and committed as `tests/fixtures/calculator/`,
  mounted in Chromium, cranked, read back off the dials, and felt when
  the freeze holds the knob.
- **The cost is MEASURED and printed**, in thread and in the page, with
  ADR-060/061's own care: the per-request cost of one stroke, one
  clearing sweep and one CLIPPED selector move on `Calculator`, and the
  per-EVENT cost on `Counter`, against the running Curta's recorded
  40.52 / 42.31 / 43.70 ms per crank tick (ADR-060's own bench table,
  unmoved by ADR-061). The comparison is labelled for what it is: the
  Curta's OWN clocked model does not exist yet — its project migration is
  pending — so this is fixture-to-project, and a running TICK is not a
  clocked REQUEST.
- **NOT** a change to the document's shape, to the framework, or to the
  contract between the two packages; not a time request, not a clock that
  advances, not an instruction with meaning, and nothing of the viewer's
  code moves into solid-node.

## Capabilities

### New Capabilities

None. This cycle widens capabilities the viewer already has.

### Modified Capabilities

- `viewer-package`: **ADDED** — "The viewer executes a clocked machine's
  requests" (the version 8 load, the request, the event solve, the
  commit, the pose, the atomicity, snapshot/restore/reset); "A declared
  stop stops a clocked request on its path" (the clip, the stop report,
  the zero-travel admission and the end-of-request judgement); "A clocked
  machine the viewer cannot execute is refused by name" (the malformed
  `clocked` object, the clock request, the cadence verbs); "The two
  runtimes agree on the clocked corpus" (the exact replay and its census
  guard); "A maker operates a clocked machine on screen" (handles,
  readouts, stops reported at the control, disabled instructions,
  outcomes, session state). **MODIFIED** — "One loader reads either
  published document" (the rendered version list becomes 1–8 and what a
  version 8 document carries); "The viewer declares its API version" (17).
- `snapshot-capture`: **MODIFIED** — "A staged document is photographed
  with a transparent background" (a clocked document is photographed at
  its initial bank and its `$t` instant is honoured, where a document
  carrying a `program` object still has no animation instant).

## Impact

- `solid_node_viewer/widget/src/clocked/` (new): `document.ts` (the
  `clocked` object read and refused by name), `machine.ts` (the bank, the
  request, the session), `events.ts` (`next_event`, `_located`, the
  landing), `commit.ts` (the law at the landing, half-to-even),
  `bounds.ts` (the chain and the threshold at the request's start, the
  clip, the stops, the end-of-request judgement), and their tests.
- `solid_node_viewer/widget/src/run/jumps.ts` — `farSideOf` extracted
  from `Walk.farSide` as a free function with a `scale` argument
  defaulting to 0, so the clocked request lands by the SAME walk and no
  running landing moves (the framework's own extraction,
  `solid_node/simulation/program.py:1578-1646`).
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS`, the
  version 8 branch beside the program gate, and `machine()` on the
  handle; `src/types.ts` — `ManifestVersion`, `ManifestState`,
  `ManifestClocked`.
- `solid_node_viewer/widget/src/clockedControls.ts` (new) and the chrome
  `viewer.ts` renders from it; `src/run/pose.ts` — the clocked pose
  scope, where `$t` sweeps and the bank stands.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi`,
  `solidNodeDocumentVersions`; `src/version.test.ts`.
- `solid_node_viewer/widget/src/clocked-corpus.json` (new, the
  framework's own file byte for byte, taken at solid-node branch
  `clocked-machine` HEAD `2d2dc2b`) and
  `src/clocked/clocked-corpus.test.ts`; `src/clocked/cost.test.ts`.
- `solid_node_viewer/capture.py` — the animation-instant rule;
  `tests/test_capture.py`.
- `tests/fixtures/calculator/` (new), `tests/support.py`, and a new
  Playwright acceptance beside `tests/test_clearing_document.py`.
- `CHANGELOG.md` under `0.2.0 — unreleased`, `README.md`'s version table;
  ONE new decision record, `docs/adrs/EXPORT/ADR-062`, extracted after
  implementation and consuming solid-node's ADR-125, ADR-126 and
  ADR-128, and `docs/adrs/README.md`.
- Nothing in the framework, nothing in another checkout, and nothing of
  the document's shape.
