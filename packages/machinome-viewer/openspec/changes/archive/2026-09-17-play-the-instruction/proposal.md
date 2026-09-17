## Why

**The clocked Curta's one button is dead, and the pilot asked to watch the
stroke.** The originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`,
READ-ONLY), whose clocked sibling builds at `_build/clocked_curta/viewer.json`
— a **version 8** document of 952 464 bytes, 23 drivers, 18 states, 39
committing relations, 35 bounds, `clocked.clock: "time"` — and declares
exactly one instruction:

```json
"instructions": {"Turn crank": {"by": {"crank_rotation": 360}, "duration": 2}}
```

This build LISTS that button and DISABLES it
(`src/clockedControls.ts:99-109, 206-208`, the reason being ADR-062's own
"a clocked machine publishes its instruction table and gives it no runtime
meaning"), and the machine handle refuses the verb by name
(`src/clocked/machine.ts:402-408`). So the only way to turn that crank in a
browser is a NUDGE or a typed value: one request, the crank jumps 360°, every
tooth and carry fires, the tree poses ONCE, and nothing is seen moving.

The pilot's requirement, verbatim: *"I need it to be animated fast between
states with smooth transition just like the fast_curta, but holding state."*
The `fast_curta` sibling (`_build/fast_curta/viewer.json`, a version 4 posed
document, 8 drivers, 7 instructions, `'Turn crank': targets crank_turns 1
over 6 s`) gets that from `Ramp` in `src/drivers.ts:64-85`: the driver
interpolated linearly from where it stands to the converted target over
`duration`, one pose per frame, advanced by the render loop's wall seconds.

solid-node's **ADR-129** (branch `play-the-instruction`, HEAD `2ab9505`,
READ-ONLY at `solid-node/WTs/play-the-instruction`) closed the producer's
half and handed this one everything it needs:

- an instruction under a clocked root MEANS one request — `by` a
  `move(id, by=travel)`, `targets` a `move(id, to=value)` — and `trigger`
  RETURNS it;
- an instruction there names **exactly one driver**, refused where the
  machine is compiled, so *published implies playable* and no consumer needs
  arity logic;
- `Request` gained `origin` and `end`, the two ends of the path it travelled,
  taken verbatim from the bank and in the input's NATIVE units, so a drawer
  never re-derives a float the machine stood at;
- `duration` is carried and silent: what it says is **how long a CONSUMER
  draws the transition**;
- the corpus records a `trigger` step, so what a BUTTON does is part of the
  contract and not merely what `move` does.

The pilot's decision about HOW is already taken, and this cycle implements
exactly it: **the machine runs ONCE per gesture, before the first frame; the
viewer DRAWS the returned transition over the instruction's duration; no
machine work in the frame loop.** Slicing an instruction into per-frame
requests is REJECTED, with the originating project's own measurement behind
the rejection: one stroke costs **0.07875 s** in Python and **36.95 ms** in
Chromium, while the same stroke in 20 requests/poses costs **1.56363 s** and
**647.7 ms** — and a 2-second instruction at 60 fps is 120 slices, not 20.
That is the `operating_curta` structure the clocked discipline exists to
replace, and ADR-063's per-frame clock transport is NOT the precedent for
this: a clock has seconds to spend per frame, and a request has a path.

## What Changes

- **`trigger(name)` on the machine EXECUTES.** It resolves the declared
  instruction, makes the one request it states — `by` a travel, `targets` a
  landing, both in design units, converted through the driver's own scale and
  dtype exactly as every other request is — through the SAME in-thread
  executor of ADR-062, and RETURNS the `ClockedRequest`. The refusal it
  replaces is gone from the cadence list; `rate` and `step` stay refused, and
  an unknown name is refused listing the declared ones.
- **`ClockedRequest` gains `origin` and `end`**, mirroring the producer field
  for field as it already mirrors `input`, `by`, `to`, `commits`, `admitted`
  and `stops`. The corpus records both on all 65 recorded requests — 63
  `move` steps and the two `trigger`s — so this is contract and not a
  convenience.
- **A DRAWING is the new thing** (`src/clocked/drawing.ts`, pure and decided
  in node like `clockedControls.ts`): given the request, the bank the machine
  stood at BEFORE it and the declared duration, it answers, for an elapsed
  time, the moved input's value between `origin` and `end` and the bank with
  every commit whose `fraction` is at or before the elapsed fraction applied
  in path order. The last frame is the request's own `end` with every commit
  applied, so the drawing finishes ON the machine's bank rather than near it.
  Commits are keyed on the published **fraction** — direction-free, exact, and
  immune to the whole-number rounding a drawn integer value takes.
- **The render loop draws it**, in the same place ADR-063's clock frame runs,
  through the same `posed()` change set and the same `clockedScope`: what a
  frame costs is a POSE of the ids that moved, and the machine is not called
  at all. The bank is FINAL from the press, so a readback during the drawing
  reports the transition's end.
- **The chrome enables the button.** `INSTRUCTIONS_DISABLED` goes;
  `ClockedInstructionControl` carries an `outcome` the way
  `RunInstructionControl` does, the button indicates while its drawing runs
  and reports the travel admitted, the stops or the refusal where it was
  pressed. While a drawing runs the panel FOLLOWS it through one narrow
  writer (`ClockedChrome.follow`) rather than the whole-panel rebuild a
  gesture makes, so a maker reads what the model is showing.
- **One authority over the pose.** Any other thing that would move or repose
  the machine — another press, a handle gesture, a host request, a restore, a
  reset — LANDS the drawing first and then acts, so two presses give two
  strokes and nothing ever poses twice in a frame. Starting a drawing stops
  the clock's transport where the machine declares one.
- **The loader refuses an instruction it could not play**, by name and at
  load, in the place ADR-062 already refuses a malformed `clocked` object:
  neither form or both, no driver or several, a name that is a state, the
  clock or nothing, a duration that is not a finite number of seconds at or
  above zero. The producer's compile refuses each before a document exists, so
  a document carrying one cannot be trusted to say what a press means.
- **The corpus is re-copied and replayed whole.**
  `src/clocked-corpus.json` becomes the producer's regenerated file byte for
  byte — **145 673 bytes**, md5 `bc4174cf47f844b035125ed3afcee3aa`, 30
  machines, **81 steps**, **917 recorded numbers**, `"tolerance": {"float":
  0.0}` — from 139 262 bytes / 76 / 722. The replay gains the `trigger` verb
  (which it throws on today) and compares `origin` and `end` on every step;
  the derived census moves with it, including the 13 bounded machines' step
  count (36 → 41).
- **The API version rises 18 → 19.** Playing a declared instruction is a
  capability a host may require before it mounts a bundle that would list the
  same button and refuse it. `solidNodeDocumentVersions` does NOT move: the
  document is byte for byte the one it already was (ADR-129 §"The document
  does not change"), and `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` is
  untouched.
- **The viewer handle's own posed `trigger` is refused under a clocked
  document**, pointing at the machine's. It ramps the driver table today,
  which poses nothing at all for a document posed from the machine's bank —
  a silent no-op that becomes a trap the moment the same word gets a meaning.
- **NOT** a change to the document's shape, to the framework, to the clock
  transport of ADR-063, to the run's worker, to document versions 1–7 or to
  the posed `Ramp`.

## Capabilities

### New Capabilities

None. One refused verb of an existing handle gets a meaning, one existing
value object gets two fields, and an existing chrome's listed button becomes
pressable.

### Modified Capabilities

- `viewer-package`: **ADDED** — "The viewer plays a clocked instruction as one
  drawn transition" (the trigger, the one solve before the first frame, the
  drawing rule, the landing, the stops, the zero duration, the refusals, the
  one authority over the pose). **MODIFIED** — "The viewer executes a clocked
  machine's requests" (a request reports BOTH ENDS of its path); "A clocked
  machine the viewer cannot execute is refused by name" (an unplayable
  instruction refused at load; `trigger` leaves the cadence list and an
  unknown name is refused by name); "The two runtimes agree on the clocked
  corpus" (the `trigger` step, the two path ends, the census); "A maker
  operates a clocked machine on screen" (instructions pressable, the button's
  indication and report, the panel following the drawing, a handle's gesture
  still one immediate request); "A host triggers declared instructions" (the
  posed trigger refused under a clocked document); "The viewer declares its
  API version" (19).

Two scenarios are REPLACED rather than carried, because this cycle makes each
say the opposite of what is true: "A declared instruction is shown and
unavailable" becomes "A declared instruction is pressed and played", and the
cadence scenario's `WHEN` drops the trigger it names. Every other scenario of
every modified requirement is carried verbatim under its exact title.

## Impact

- `solid_node_viewer/widget/src/clocked/machine.ts` — `ClockedRequest` gains
  `origin` and `end` (already in hand at the return: `origin` at `:292`, the
  clipped target at `:364`); `trigger` stops being `never` and becomes the
  instruction's one request; the instruction table reaches the machine through
  `LoadedMachine.instructions`, which it already carries (`document.ts:177`).
- `solid_node_viewer/widget/src/clocked/drawing.ts` (new) and its test — the
  whole decision, pure.
- `solid_node_viewer/widget/src/clocked/document.ts` — `readInstructions`
  (`:468-482`) validates what it reads for a version 8 document and refuses by
  name.
- `solid_node_viewer/widget/src/clockedControls.ts` — `ClockedInstructionControl`
  (`:99-109`) carries an outcome instead of `disabled`/`reason`;
  `INSTRUCTIONS_DISABLED` removed.
- `solid_node_viewer/widget/src/viewer.ts` — the drawing held beside the
  clock's transport (`:392-410`), advanced in the render loop beside
  `clockFrame` (`:1476-1510`), landed by `clockedRequest` and by the handle's
  wrappers (`:1060-1090`, `:1628-1660`); the clocked instruction button and
  `ClockedChrome.follow` (`:3404-3420`, `:3176-3178`); `MachineHandle`
  (`:178-186`), which inherits the machine's `trigger` unchanged; the posed
  `trigger` refusal (`:1626`).
- `solid_node_viewer/widget/src/clocked-corpus.json` (re-copied byte for byte)
  and `src/clocked/clocked-corpus.test.ts` (the `trigger` verb, both ends, the
  census).
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi: 19`;
  `src/version.test.ts`.
- `tests/fixtures/calculator/` — re-exported from the producer's own
  `tests/clocked_project/calculator.py:Calculator`, which now declares
  `'Stroke'` and `'Set four'`; its README records the new bytes, md5 and the
  framework commit. `tests/test_calculator_document.py` presses the button in
  a real browser. A second, SKIPPABLE acceptance measures the Curta's own two
  builds where the pilot's workspace has them, copying nothing into this
  repository.
- `CHANGELOG.md` under `0.2.0 — unreleased`, `README.md`'s version table; ONE
  new decision record, `docs/adrs/EXPORT/ADR-064`, extracted after
  implementation, consuming solid-node ADR-129 and **amending** ADR-062 on its
  "listed and disabled" section, and `docs/adrs/README.md`.
- Nothing in the framework, nothing in the Curta, nothing in another checkout,
  and nothing of the document's shape.

### Non-goals

Each is named in `design.md` with its reason.

- **The shop floor's use of the button.** The studio's own follow-up, in its
  own repository.
- **The Curta's own edits** — the unneeded `Time.elapsed()` it still declares,
  and anything else the project wants — are the project's, in its repository.
- **Per-frame requests on a driver**, of any kind: rejected by the pilot and
  measured against above.
- **ADR-063's clock transport**, the run's worker, the posed `Ramp`, document
  versions 1–7 and the document's shape: untouched, asserted by diff and by
  fixture.
- **An instruction naming several drivers**: the producer refuses it before a
  document exists; this viewer refuses a document that carries one and
  designs nothing for it.
- **A drawing over the CLOCK**: no instruction may name it, and nothing asks.
