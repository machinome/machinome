# Evidence — drive the run by touch

Every number below was produced in the worktree
`solid-node-viewer/WTs/drive-the-run-by-touch` (branch
`drive-the-run-by-touch`), with the widget suite run from
`solid_node_viewer/widget` and the Python suite with the workspace venv
and `PYTHONPATH` at the worktree root.

## 0. Before anything else

### 0.1 The base

```
$ git log --oneline -3
110fa91 openspec(drive-the-run-by-touch): propose pressing and turning the part
644b504 openspec: archive ship-the-inspector-layout; accept ADR-051 and ADR-052
fea5f16 fix(server): never cache a build artifact; steady the sidebar width test
```

`644b504` is viewer main with `ship-the-inspector-layout` archived and
ADR-051/ADR-052 accepted; `110fa91` is this change's own ratified
planning commit and the head this implementation starts from. The
package declares `"version": "0.2.0"` (unreleased) and
`"solidNodeViewerApi": 11`.

### 0.2 The baseline

```
$ npm run typecheck          # solid_node_viewer/widget
> tsc --noEmit
(clean)

$ npm test
 Test Files  34 passed (34)
      Tests  642 passed (642)
   Duration  4.13s

$ npm run build
  dist/solid-widget.js  660.2kb
⚡ Done in 123ms

$ PYTHONPATH=<worktree> .venv/bin/python -m pytest -q
96 passed, 24 warnings in 66.64s (0:01:06)
```

Nothing is skipped: the bundle is built, Playwright and a headless
Chromium are installed in the workspace venv, and Pillow is present, so
`needs_bundle`, `needs_chrome`, `needs_playwright` and `needs_pil` all
pass. (The archived `drive-the-run-on-screen` baseline had one skip,
`test_server.py`'s development-app browser test; the development app is
built in this bench and that test runs.)

### 0.3 The framework's authority, read and kept open

- `solid-node/WTs/controls-on-parts/openspec/changes/archive/`
  `2026-09-14-declare-controls-on-parts/specs/export/spec.md`,
  requirement *"A running document publishes the controls its parts
  carry"* — the field-by-field authority on the table this change
  consumes: `kind`, `part`, `instruction` | (`input`, `per_unit`),
  `joint`, `coordinate`, `axis`, `origin`; the table additive within
  version 5; `per_unit` a reading AT REST; a control whose part a render
  omitted dropped at publication rather than refused.
- `solid-node/WTs/controls-on-parts/docs/adrs/NODE/ADR-112-a-control-is-`
  `a-declaration-on-the-model-and-the-gesture-comes-from-the-tree.md`
  §3 — *"`axis` and `origin` are the values the joint's own placement
  used, in the joint node's frame — the site carry applied — so a
  consumer computes the world line from one node's world matrix with no
  case analysis."* That sentence is what D6 rests on, and the reviewer's
  decision 3 is what it is checked by.

Nothing in this repository restates them.

## 1. The fixture

### 1.1 The document, verbatim

```
$ cmp <probe build>/_build/viewer.json tests/fixtures/touched/viewer.json
(identical)
$ wc -c tests/fixtures/touched/viewer.json
31972 tests/fixtures/touched/viewer.json
```

Version 5, root `Touched`, four instructions (`Add hundred`, `Add one`,
`Add ten`, `Back one`), three drivers (`hundreds_entry`, `tens_entry`,
`units_entry`), twelve program coordinates, and six controls in the key
order the producer writes: `hundreds dial`, `tens dial`, `turn
hundreds`, `turn tens`, `turn units`, `units dial`. Each `turn` carries
`per_unit -36.0`, `joint [<column>, "input"]`, `coordinate
<column>.input.turn`, `axis [1, 0, 0]`, `origin [0, 0, 0]`.

Each joint node's operations are
`[["r", "<column>.input.turn", [1, 0, 0]], ["t", [...]]]` — the rotation
naming the coordinate is the whole leading run, at index 0 of 2. Every
one of the nine joints in the document is that first shape, so D6's
condition holds by inspection and the acceptance never exercises the
off-centre one; a node test does (2.2 below).

### 1.2 The meshes

Fifteen unique model paths, referenced 42 times, each a copy of the
684-byte unit cube `tests/fixtures/pascaline/vendor/printables-28807/`
`0_base-Base-7b47361aad19.stl`. Three of the fifteen
(`group_a-05-CarryWheel40`, `group_a-12-CarryCamA`,
`group_b-12-CarryCamB`) differ from the `pascaline` fixture's, so this
fixture carries its own `vendor/` tree. `tests/fixtures/touched/` is
43,232 bytes over 17 files, and `README.md` there says what is verbatim
and what is a stand-in.

### 1.3 RED, then green

`tests/support.py` gained `TOUCHED` and `published_touched`, and
`tests/test_running_document.py` gained `TouchedFixtureTest`. Written
first:

```
$ python -m pytest tests/test_running_document.py -q -x
ImportError while importing test module '…/tests/test_running_document.py'.
tests/test_running_document.py:21: in <module>
    from tests.support import (
E   ImportError: cannot import name 'TOUCHED' from 'tests.support'
1 error in 0.16s
```

Then:

```
$ python -m pytest tests/test_running_document.py::TouchedFixtureTest -q
...                                                                  [100%]
3 passed in 0.08s
```

A missing mesh now fails as a missing mesh rather than as a blank
canvas.

## 2. Reading the table, refused by name

### 2.1 / 2.2 RED

`src/partControls.test.ts` — 22 cases, one per refusal in D1 plus the
accepting ones — written against the tree as the planning commit left
it:

```
 FAIL  src/partControls.test.ts [ src/partControls.test.ts ]
Error: Cannot find module './partControls' imported from
'…/src/partControls.test.ts'
 ❯ src/partControls.test.ts:18:1
     18| import { readControls } from './partControls';

 Test Files  1 failed (1)
      Tests  no tests
```

### 2.3 GREEN

`ManifestControl` and `Manifest.controls` in `src/types.ts`;
`readControls(document, sourceUrl, program)` in the new
`src/partControls.ts`, importing neither the DOM nor three.js (its only
import is `type { Manifest, ManifestControl, ManifestNode }`).

```
$ npx vitest run src/partControls.test.ts
 ✓ src/partControls.test.ts (22 tests) 9ms
      Tests  22 passed (22)
```

The exact refusal messages, one line each, are listed in §9 below.

### 2.4 RED then GREEN — `assertRenderable`

Nine cases appended to `src/document.test.ts`, run before the loader
knew of controls:

```
 × assertRenderable on a document carrying controls > hands back the parsed controls, in the document's own key order
   TypeError: Cannot read properties of undefined (reading 'map')
 × … > hands back [] for a document carrying no controls key
   AssertionError: expected undefined to deeply equal []
 × … > refuses a part its own tree does not contain, naming it
   AssertionError: expected [Function] to throw an error
 × … > refuses an instruction the document does not declare
   AssertionError: expected [Function] to throw an error
 × … > refuses a ratio of zero, saying the gesture has no quantum
   AssertionError: expected [Function] to throw an error
 × … > refuses a joint whose leading operations are not the placement
   AssertionError: expected [Function] to throw an error
 × … > accepts a joint placed off its node's origin
   TypeError: Cannot read properties of undefined (reading '0')
 × … > refuses a controls table on a document that carries no program
   AssertionError: expected [Function] to throw error matching /controls.*no program/s
     but got '/m.json has expressions naming undecl…'
 × … > refuses the table before the tree is walked for driver ids
   AssertionError: expected [Function] to throw error matching /quantum/
     but got '/m.json has expressions naming undecl…'

 Test Files  1 failed (1)
      Tests  9 failed | 35 passed (44)
```

The last two are the interesting reds: before the change the
undeclared-driver walk answered first. `LoadedDocument` gained
`controls`, and `assertRenderable` calls `readControls` after
`loadProgram` and before `visit(document.root)`:

```
$ npx vitest run src/document.test.ts
 ✓ src/document.test.ts (44 tests) 27ms
      Tests  44 passed (44)
```

Every pre-existing case in that file passes unedited.

## 3. The gesture, decided as data

### 3.1 / 3.2 / 3.3 RED

The geometry, the mode choice, the planner and the pick's visibility
predicate were first drafted into `partControls.ts` in the same write
that carried `readControls`. That would have made their red an assertion
about code already on disk, so they were **backed out of the module
before their tests were written** and put back only after the red below.
`readControls`'s own 22 cases stayed green throughout.

```
   × worldLine reads the gesture's line off the joint (D6) > carries the origin by the full map and the axis by its rotation
   × … > gives the SAME line whatever angle the joint stands at -- the rotation-alone shape
   × … > gives the SAME line whatever angle the joint stands at -- the translate / rotate / translate-back shape
   × … > normalises the axis even when the declared one is not unit
   × intersectPlane and sweepAngle > meets the plane where the ray crosses it
   × … > answers null for a ray parallel to the plane
   × … > measures a signed, right-handed angle in degrees about the axis
   × … > unwraps past half a turn by accumulating per-move deltas
   × chooseMode fixes the measurement at pointerdown (D10) > measures in the joint's plane when the ray is not edge-on
   × … > falls back to the screen below EDGE_ON
   × … > falls back to the screen when the pointer came down ON the axis
   × … > signs the screen fallback by which way the axis points
   × TurnPlanner commits quanta, one at a time (D11) > is one nudge amount times the published ratio
   × … > issues nothing until the sweep crosses one whole quantum
   × … > signs the request through the ratio, not through the sweep
   × … > keeps at most ONE request in flight, because the run says so
   × … > derives what is owed from where the pointer stands, so forward and back nets out
   × … > leaves the origin where it is when a request does not complete
   × … > releases the stall when the maker backs off, and at once when they reverse
   × … > issues nothing at all when the nudge amount is zero
   × … > ignores a retire with nothing in flight
   × visibleUpTo filters the pick three.js will not (D5) > keeps a hit whose mesh and every ancestor up to the scene are shown
   × … > drops a hit on a hidden mesh
   × … > drops a hit under a hidden GROUP -- what `applyVisibility` sets for a subtree the navigator hid
   × … > stops at the scene, so a hidden scene root hides everything

TypeError: (0 , worldLine) is not a function
TypeError: (0 , intersectPlane) is not a function
TypeError: (0 , sweepAngle) is not a function
TypeError: (0 , chooseMode) is not a function
TypeError: TurnPlanner is not a constructor
TypeError: (0 , visibleUpTo) is not a function

 Test Files  1 failed (1)
      Tests  25 failed | 22 passed (47)
```

### 3.4 GREEN

```
$ npx vitest run src/partControls.test.ts
 ✓ src/partControls.test.ts (47 tests) 13ms
      Tests  47 passed (47)
```

One case went red a second time on the way, and it is worth recording
because the design contradicted itself for one value:

```
 FAIL  … > signs the screen fallback by which way the axis points
AssertionError: expected -1 to be 1 // Object.is equality
 ❯ src/partControls.test.ts:577:29
    577|     expect(edge.screenSign).toBe(1);
```

D10 says the sign is `+1` when `A · (O − camera) < 0` and `−1`
otherwise, and then that *"exactly edge-on, that dot product is zero
and the sign is genuinely arbitrary; the convention is `+1`"*. A literal
`< 0 ? 1 : -1` gives `−1` at zero. The code implements the stated
CONVENTION — `facing <= 0 ? 1 : -1` — because that is the sentence the
spec delta carries. Recorded under Deviations below.

`partControls.ts` imports exactly one thing:
`import type { Manifest, ManifestControl, ManifestNode } from './types'`.
No DOM, no three.js, no run.

## 4-5. The pick, the affordance and the gesture

### 4.1 / 4.3 / 4.4 GREEN

`viewer.ts` builds `Map<THREE.Mesh, LoadedControl[]>` (and the reverse
`Map<controlName, THREE.Mesh[]>` the highlight needs) from
`tree.requirePath(control.part).group.traverse(...)`, rebuilt in
`replaceTree`, `manifestChanged` and `artifactChanged`. `tree.ts` is
UNCHANGED: `git diff --stat` names it nowhere.

The pick casts `raycaster.intersectObject(scene, true)`, walks the hits
in distance order, skips anything failing `visibleUpTo(mesh, scene)`, and
answers the controls of the FIRST surviving hit — `null` when that mesh
names none, which is what makes a part in front of a control not pressed
through.

### 5.6 / 5.5 RED (mutation) then GREEN

The gesture's DOM behaviour needed a seam jsdom can call, because
`mount()` builds a `THREE.WebGLRenderer`. `viewer.ts` gained two
module-level exported factories — `partSurfaceWith(host)` and
`outcomeLabelIn(container)` — and `mount()` calls them with the real
collaborators, which is exactly `inspector.ts`'s `mountInspectorWith`
pattern. `src/partSurface.test.ts` (28 cases, jsdom) drives them.

**These tests were written after the code they cover** — tasks 5.1-5.4
are stated as "Green", and the surface was extracted from working code
rather than grown from a test. Their red is therefore a MUTATION red,
which is stronger evidence than an absence red and is recorded as what
it is. Each mutation was applied to `src/viewer.ts`, the suite run, and
the file restored from a copy taken beforehand:

```
=================== M1: drop the window blur and visibilitychange release paths
   × a gesture ends on every side an interaction can (D13) > ends on the window losing focus, and gives the camera back
     → expected true to be false
   × … > ends on the page ceasing to be displayed, and gives the camera back
     → expected true to be false
      Tests  2 failed | 26 passed (28)
=================== M2: never give the camera back
   × a press is a pointerup inside the threshold (D8) > suspends the camera, captures the pointer and stops the event
     → expected false to be true
   × … ends on a release / a cancelled pointer / lost pointer capture / the
     window losing focus / the page ceasing to be displayed, and gives the
     camera back                                     (5 more, same assertion)
      Tests  6 failed | 22 passed (28)
=================== M3: no title on hover
   × hover is a cursor, a title and a highlight (D7) > names every control on the hovered part
     → expected null to be 'units dial · turn units'
      Tests  1 failed | 27 passed (28)
=================== M4: the label's clock is never restarted
   × the transient outcome label (D9) > is taken away after a few seconds, and the clock restarts on each report
     → expected null not to be null
      Tests  1 failed | 27 passed (28)
=================== M5: a blocked quantum advances the origin anyway
   × a drag issues one quantum at a time (D11, D12) > leaves the origin where it is when a request is blocked, and issues nothing more while the drag is held there
     → expected [ Array(2) ] to have a length of 1 but got 2
      Tests  1 failed | 27 passed (28)
```

Restored: `Tests  28 passed (28)`.

## 6. The mount surface

### 6.1 RED then GREEN

```
   × resolveOptions: the part affordance > presents it by default, like the panel
     AssertionError: expected undefined to be 'inline'
   × … > lets a host suppress it
     AssertionError: expected undefined to be 'none'
   × … > is independent of driverControls in all four combinations
     AssertionError: expected undefined to be 'inline'
   × showsPartControls > presents the affordance for a document that declares controls
   × showsPartControls > presents nothing for a document that declares none
   × showsPartControls > presents nothing when the host asked for none
     TypeError: (0 , showsPartControls) is not a function
      Tests  6 failed | 32 passed (38)
```

Then `Tests  38 passed (38)`.

### 6.2 `controls()`

The listing needs a real camera and a real canvas, so it is proved in
the browser rather than in node: `TouchedByHandTest` asserts the six
entries with their declaration carried through, each with a rectangle
and a point INSIDE that rectangle; that a hidden part reports
`rect: null, point: null` while its declaration stays intact; that the
full listing (rects and points included) answers under
`partControls: 'none'`; and `RunningDocumentTest` asserts `[]` on the
`pascaline` document, which declares no table.

### 6.3 / 6.4 RED then GREEN — the API version

```
   × API_VERSION > declares the part-controls API as version 12
     AssertionError: expected 11 to be 12 // Object.is equality
      Tests  1 failed | 5 passed (6)
```

`package.json`'s `solidNodeViewerApi` 11 → 12; `version.test.ts`'s
narrative and its `toBe`; `tests/test_bundle.py`,
`tests/test_widget_e2e.py` and `tests/test_running_document.py`'s
existing assertions. `solidNodeDocumentVersions` is untouched and
`version.test.ts` still asserts `[1, 2, 3, 4, 5]` and its equality with
`RENDERED_VERSIONS`.

### 6.5 RED then GREEN — the capture

```
>       self.assertEqual(mount_options(time=0.25),
E       AssertionError: {'animation': 'external', 'time': 0.25, 'driverControls': 'none'}
                     != {'animation': 'external', 'time': 0.25, 'driverControls': 'none',
                         'partControls': 'none'}
>       self.assertIn('"partControls": "none"', page)
E       AssertionError: '"partControls": "none"' not found in '<!doctype html> … {"animation":
        "external", "time": 0.5, "driverControls": "none", "fov": 22.5} …'
3 failed, 14 passed
```

Then `26 passed` for `test_capture.py` + `test_bundle.py`. No capture
requirement moved.

## 7. The acceptance: a maker touches the Pascaline

`TouchedByHandTest` in `tests/test_running_document.py`, on the committed
`touched` fixture, mounted with default options, driven with
`page.mouse.move/down/up` in headless Chromium against the built bundle.
No host code in it calls `run()` to move anything.

### The geometry the fixture actually gives

The dial is a 684-byte stand-in cube, so it is **3.56 x 3.72 CSS pixels**
on screen at the default frame, and `controls()` reports its reachable
point at `(362.18, 249.34)` — inside its own rectangle, found by the
grid search rather than assumed. `point` is what makes the acceptance
possible at all: the press lands on a speck a test could not have
guessed.

Two consequences were MEASURED rather than assumed, and both are
recorded in the test as constants with their reason:

- A press lands essentially ON the joint's axle, so a straight drag
  *through* the press point sweeps almost nothing — the first probes
  (down 120 px, and a screen arc of radius 30-60 px) issued no request
  at all. The sweep only becomes worth a quantum once the pointer is far
  from the axle.
- The sweep is strongly non-linear in screen pixels, because the joint's
  plane is seen at about 23 degrees. Measured on this fixture and this
  default camera: leftward 100 px issues nothing, **120 px is exactly
  one quantum**, 140-180 px is three to four, and 300 px is still four
  (the plane intersection runs away). Downward, **140 px and beyond is
  one blocked report and nothing more**, at 140, 180 and 250 px alike —
  the stall latch, on the real machine.

`FORWARD_DRAG = (-120, 0)` and `BLOCKED_DRAG = (0, 200)` are those
measurements.

### 7.1 The listing

Six controls in the document's own key order, each `kind`, `part`,
`joint`, `coordinate`, `instruction` / `input` equal to the document's
own value, every `turn` at `perUnit -36.0`, every one with a rectangle
and a point, and every point inside its rectangle. `setVisible(['units',
'input', 'dial'], false)` then gives `turn units` `rect: null, point:
null` with its declaration intact while `turn tens` still reports one,
and a pointer at the dial's former point gets no cursor.

### 7.2 A press

Hover at the reported point: `canvas.style.cursor === 'pointer'` and
`canvas.title === 'turn units · units dial'` — both controls naming the
part. Press there and the panel's `Add one` button stops indicating:

- the transient label reads `completed`;
- the panel's own button for `Add one` reads `completed`;
- `units_entry` reads `1.0000`;
- `run().state()` gives `units_entry === 1` and
  `units.drum.turn === 36`;
- exactly one outcome reached `run().onOutcome`: `['completed', 1]`.

### 7.3 A blocked drag

`BLOCKED_DRAG` (200 px down, ten steps), the way the ratchet forbids:

- `window.__out === [['blocked', 0]]` — one request, blocked, zero
  admitted;
- the label reads `blocked after 0 digit` and the panel's `units_entry`
  row reads the same;
- `units_entry === 0` and `units.drum.turn === 0`;
- held there for eight further moves and 0.6 s, the run's `tick()`
  advances and **no second outcome arrives**;
- releasing leaves `units_entry === 0`: nothing was stored.

### 7.4 A forward drag

`FORWARD_DRAG` (120 px left) — one quantum:

- `window.__out === [['completed', 1]]`;
- `units_entry === 1`, `units.input.turn === -36`,
  `units.drum.turn === 36`. The sweep's sign went through the RATIO: a
  negative sweep on `per_unit = -36` asked for `+1` digit;
- the label reads `completed` and the readout `1.0000`.

### 7.5 A part the table does not name

The lid is found by hiding it and diffing two screenshots — every
stand-in mesh is the same cube, so the picture alone cannot say which
one is a lid — excluding the panel's and the transport's rectangles,
which are TRANSLUCENT (a press there lands on the panel, not the
canvas). The units column's lid turned out to be entirely under the
panel, so the three columns are tried in turn.

At that point: no cursor, no title; pressing and dragging orbits the
camera (`view().camera` changes), `window.__out` stays empty, and
`run().state()` is identical before and after.

Under `partControls: 'none'` the same is true of the DIAL: no cursor, no
title, the camera orbits, nothing reaches the run — and `controls()`
still answers all six with their rects and points.

### 7.6 The screenshots, inspected by eye

Written to `tests/_shots/`:

- **`touched-dial-plain.png` / `touched-dial-hovered.png`** — the units
  input assembly focused, so the dial is a cube 44 px across instead of
  a 3.5 px speck. Four coloured cubes on the dark ground; in the hovered
  frame the pale grey one top right — the dial — is visibly brighter,
  and nothing else changes. `ImageChops.difference` confirms it by
  measurement: the only changed pixels are `(493, 214)-(537, 258)`,
  which is that cube alone.

  This pair is why `HOVER_EMISSIVE` moved. At the proposed `0x333333`
  the same diff measured a maximum channel sum of **30** (about 10/255
  per channel) — real, and not a "visible change distinguishing it from
  the parts around it". At `0x777777` it measures **140**, which is what
  the two frames above show. `Color.setHex` reads sRGB and stores
  linear, so the lift a viewer sees is far smaller than the hex reads.

- **`touched-hover.png`** — the whole model with the pointer on the
  units dial. The panel lists three inputs at `0.0000 digit`, four
  instruction buttons, the transport at `0:00.00`, and three brown lids
  with about forty small coloured cubes. The affordance is honestly
  invisible here: the dial is 3.5 px and a screenshot captures no
  cursor. That is what the close-up pair is for.

- **`touched-press.png`** — the same frame with the pointer down on the
  dial, before the release. Nothing has been requested: the transport
  still reads `Run` and `0:00.00`, and every readout is `0.0000 digit`.
  That is the point: a press is not a request until the pointer comes
  up.

- **`touched-after-forward-drag.png`** — the label `completed` sits mid
  canvas where the drag ended; `units_entry` reads `1.0000 digit` with
  `completed` beside it in the panel; the transport reads `Pause` and
  `0:01.41`, because the request started the paused run.

- **`touched-blocked.png`** — the label `blocked after 0 digit` sits
  where the drag ended, and the panel's `units_entry` row carries the
  same words in the amber it uses for a refusal, while its readout still
  says `0.0000 digit`. One outcome, two places, the same sentence.

## 8.5 What the implementation learned about the open questions

### Open question 1 — two controls of one kind on one part

**Reviewer decision 1: refuse.** Implemented as `readControls`'s ninth
refusal, keyed by `(kind, part)`, with the message naming BOTH control
keys and the part. Nothing in the acceptance document trips it — the
three dials each carry exactly one `button` and one `turn`, which is the
legal shape D3 exists to keep legal, and a node test pins that it is
accepted. Cost of the decision: one map and one message. The framework
follow-up (a matching compile-time refusal) is untouched by this cycle.

### Open question 2 — should a partially admitted quantum advance the origin?

**Reviewer decision 2: it does not.** Implemented, and the acceptance
cannot tell the two apart, exactly as the design predicted: the
document's ratchet admits `0` — the blocked report reads `blocked after
0 digit`, not "blocked after 0.4". So this cycle produced **no evidence
either way**; the rule stands on the spec's "no remainder" sentence and
on ADR-048's own. A machine with a soft stop would be the first to tell
them apart, and none exists in this repository's fixtures.

### Open question 3 — should the framework state the frame?

**Reviewer decision 3: the frame is already stated**, and the viewer's
check is that the placement is the LEADING RUN of the joint node's
operations. Implemented as `leadingRotation(node)`: scan from index 0,
skip translations, require the first rotation's expression to equal the
entry's `coordinate`.

What the fixture shows: every one of the nine joints in the acceptance
document is `[["r", "<column>.input.turn", [1, 0, 0]], ["t", [...]]]` —
the rotation is the whole leading run, at index 0 of 2, and the
translation that follows is the joint's placement in its column. So the
off-centre shape is never exercised by the acceptance and is pinned by
node tests instead, including the assertion the corrected D6 asks for:
`origin` equals the negated leading translation of a
`t(-a), r, t(a)` node.

**The correction mattered.** The proposal's first draft required the
rotation to be the very FIRST operation. That check would have accepted
this fixture (its rotation is first) and silently refused every
`Revolute(at=...)` — the exact shape `origin` exists for, and one no
fixture here would have caught. The reviewer's correction is what makes
the check match what the framework actually publishes.

### Open question 4 — should a press take the instruction's own duration?

**Reviewer decision 4: yes**, and nothing in the implementation touches
it: a press calls `run().trigger(name)`, and the run reads the
instruction's declared duration. A press and a panel button are the same
call. A DRAG's duration is a different number — the input's current
nudge `seconds`, captured at pointerdown — because a drag issues `move`s
rather than an instruction.

### Open question 5 — crossings and stops

**Reviewer decision 5: deferred**, and nothing here reads them.

## Deviations

Three, each preserving the specs' observable behaviour.

1. **`chooseMode`'s screen sign at exactly edge-on is `+1`, not `−1`.**
   D10 says "multiplied by `+1` when `A · (O − cameraPosition) < 0` and
   `−1` otherwise", then "exactly edge-on, that dot product is zero and
   the sign is genuinely arbitrary; the convention is `+1`". A literal
   `< 0 ? 1 : -1` gives `−1` at zero and contradicts the stated
   convention. The code implements the convention (`<= 0 ? 1 : -1`),
   which is the sentence the spec delta carries. Red pasted in §3.4.

2. **`HOVER_EMISSIVE` is `0x777777`, not the `0x333333` D7 sketched.**
   `THREE.Color.setHex` reads sRGB and stores linear, so `0x333333`
   measured a maximum channel change of 30/255 across the hovered
   part — real, and not the "visible change distinguishing it from the
   parts around it" the spec requires. `0x777777` measures 140/255 on
   the same materials. Measurement and the two frames in §7.6.

3. **The gesture's DOM lives in `partSurfaceWith(host)` and the
   transient label in `outcomeLabelIn(container)`, both exported from
   `viewer.ts`.** The design put them "in `viewer.ts`" without saying
   how; task 5.6 asks for jsdom tests "through the seam pattern
   `inspector.test.ts` already uses for `mount`", and `mount()` cannot
   run in jsdom. These two factories are that seam, in the same file the
   Impact list names, and `mount()` calls them with the real
   collaborators. No new module was published, `partControls.ts` is
   still free of the DOM and three.js, and every decision is still in
   it — the surface owns listeners, the cursor, the title, the capture
   and the camera's suspension, and nothing else.

Two further things worth the reviewer's eye, neither a deviation:

- **`MIN_RADIUS = 1e-6` world units.** D10 leaves the number open
  ("within `MIN_RADIUS` of zero … where the angle is undefined"). It is
  implemented as a CONDITIONING bound — below it `normalize3` has
  nothing to normalise — not a human-scale tolerance, and it is
  documented as such. A human-scale value would need a scale the
  document does not publish.
- **`tests/test_cli.py` changed.** Task 6.5 says "no other Python test
  changes"; `test_cli.py` pins `mount_options`' whole dictionary in an
  `assert_called_once_with`, so adding `partControls: 'none'` to the
  capture's options fails it. One line added, no behaviour asserted
  differently.

## Framework-side findings

Two, stated plainly for the reviewer to carry across; neither blocks
this cycle.

1. **The leading-run guarantee is a coincidence the export spec does not
   state.** ADR-112 §3 says a consumer "computes the world line from one
   node's world matrix with no case analysis", and that is true only
   while the joint's placement is the leading run of its node's
   operations. Nothing in the framework's export spec says it will be,
   and ADR-112 §2's narrowing does not itself refuse motion applied to a
   node *before* its joint's slot — a hand-written `apply_motion` ahead
   of the joint would put `axis` and `origin` in a different frame and
   make the published line wrong, silently. This viewer refuses such a
   document by name (D1.8), which is the safe half. The framework's half
   is to either state the guarantee in the export spec or refuse motion
   applied before a controlled joint at compile.

2. **The framework permits two controls of one kind on one part; this
   viewer refuses it.** Recorded by reviewer decision 1 as a framework
   follow-up, and repeated here because it is the one document shape
   where the two disagree: the framework would publish it and this
   viewer will not mount it.

One more, smaller, about the acceptance rather than the contract:

3. **`per_unit` alone does not tell a consumer how big the part is.**
   The gesture is measured in the joint's plane, so how many SCREEN
   pixels one quantum costs depends entirely on where the camera stands
   and how the plane is foreshortened — on this fixture, 100 px of drag
   issues nothing and 120 px issues one quantum, while 300 px still
   issues only four. That is inherent to measuring an angle about a real
   axle and is not a fault in the published table; it is worth knowing
   before anyone specifies a gesture in pixels.

## 8.1 The whole suite

```
$ npm run typecheck          # solid_node_viewer/widget
> tsc --noEmit
(clean)

$ npm test
 Test Files  36 passed (36)
      Tests  732 passed (732)

$ npm run build
  dist/solid-widget.js  674.6kb

$ PYTHONPATH=<worktree> .venv/bin/python -m pytest -q
105 passed, 27 warnings in 92.31s (0:01:32)
```

Nothing is skipped, as at the baseline.

**Widget: 642 → 732, +90, in 34 → 36 files.** Every one accounted for:

| where | + | what |
| --- | --- | --- |
| `src/partControls.test.ts` (new) | 47 | the table's refusals and accepting cases (22), the geometry, the mode choice, the planner and the visibility predicate (25) |
| `src/partSurface.test.ts` (new) | 28 | the gesture's DOM behaviour and the transient label, in jsdom |
| `src/document.test.ts` | 9 | `assertRenderable` on a document carrying controls |
| `src/options.test.ts` | 6 | `partControls` and `showsPartControls` |

No pre-existing widget test was edited except `src/version.test.ts`,
whose narrative and single `toBe(11)` this change deliberately moved to
12. Its other five cases are untouched.

**Python: 96 → 105, +9.** Every one accounted for:

| where | + | what |
| --- | --- | --- |
| `TouchedFixtureTest` (new) | 3 | the committed fixture is complete, is a version 5 run carrying six controls, and stages whole |
| `TouchedByHandTest` (new) | 6 | the listing, the listing under a suppressed affordance, a press, a blocked drag, a forward drag, an undeclared part |

Pre-existing Python tests changed in exactly four places, all
deliberate: `test_bundle.py` and `test_widget_e2e.py`'s API-version
assertions (11 → 12); `test_running_document.py`'s own API-version
assertion, plus one added line asserting `controls() === []` on the
`pascaline` document, which declares no table; `test_capture.py`'s two
`mount_options` dictionaries and one added `assertIn`; and
`test_cli.py`'s `mount_options` dictionary, which pins the whole dict in
an `assert_called_once_with` (see Deviations).

`openspec validate drive-the-run-by-touch --strict` → `Change
'drive-the-run-by-touch' is valid`.

## 9. The refusal messages, verbatim

Printed from `readControls` against hand-written documents. Each names
the document, the control's key and the offending value.

```
viewer.json carries a "controls" table that is not an object ("everything"). Refusing the document rather than presenting an affordance nobody declared.

viewer.json carries a "controls" table (turn units) and no program. A control has nothing to submit a request to: refusing the document rather than presenting an affordance with nothing to ask.

viewer.json declares the control "turn units" whose entry is not an object (7). Refusing the document rather than presenting a control the viewer cannot resolve.

viewer.json declares the control "turn units" with kind "slide", which is neither "button" nor "turn". …

viewer.json declares the control "turn units" whose "part" is not a list of node names ("units.input.dial"). …

viewer.json declares the control "turn units" whose path does not resolve: Unknown assembly path: units/input/knob. …

viewer.json declares the control "turn units" whose path does not resolve: Ambiguous assembly path: units/input/dial. …

viewer.json declares the control "turn units" whose joint units/drum is neither the part units/input/dial nor one of its ancestors; a control's coordinate is the one owned by the nearest ancestor-or-self of the part, so the gesture's geometry would be meaningless. …

viewer.json declares the control "turn units" naming the instruction "Add two", which its instructions table does not declare; it declares: Add one. …

viewer.json declares the control "turn units" naming the input "tens_entry", which its drivers table does not declare; it declares: units_entry. …

viewer.json declares the control "turn units" naming the coordinate "units.carry.turn", which its program does not publish; it publishes: units_entry, units.input.turn, units.drum.turn. …

viewer.json declares the control "turn units" whose "per_unit" is 0, which is not a finite non-zero number: the gesture would have no quantum. …

viewer.json declares the control "turn units" whose "axis" is not three finite numbers ([1,0]). …

viewer.json declares the control "turn units" whose "axis" has no direction (it is [0, 0, 0]). …

viewer.json declares the control "turn units" whose joint units/input is not posed by "units.input.turn" as the leading run of its own operations -- zero or more translations and then one rotation over that coordinate; it is posed by "units.drum.turn". …

viewer.json declares the control "turn units again" on the part units/input/dial, which "turn units" already declares a "turn" on; one gesture would have two meanings and the viewer would have to choose. …
```

Every one of the fifteen ends with the same sentence the first two carry
in full: *"Refusing the document rather than presenting a control the
viewer cannot resolve."*
