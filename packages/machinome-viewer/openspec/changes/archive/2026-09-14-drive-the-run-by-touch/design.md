# Design — drive the run by touch

## Context

This change is the viewer half of the controls-on-parts campaign, cut from
`solid-node/workflow/docs/controls-on-parts.md` §5. It depends on no
framework code: what it needs is a **document**, and the framework's
archived change `declare-controls-on-parts` (ADR-112) publishes it.

The interaction model is **ratified, not proposed**. The pilot's
2026-09-12 ratification named the three things a control can be —
"clicking a button, holding a jog control or **dragging a part**" — and
ADR-048 promised this cycle by name. What this design decides is only what
those records leave open: how the table is read and refused, how a mesh is
found and how a pick reaches it, how a sweep becomes requests the run will
accept, where the mount surface goes, and what each of those must not do.

### What the document carries

A version 5 document MAY carry a top-level `controls` object beside
`instructions`, keyed by qualified control name. Verbatim from the
framework's export spec, each entry carries, in this order:

- `kind` — `"button"` or `"turn"`;
- `part` — the list of node names, from the document root down, of the node
  a person touches;
- `instruction` (button) — a key of the same document's `instructions`; or
  `input` (turn) — a key of the same document's `drivers` — and `per_unit`,
  the coordinate units the part moves per DESIGN unit the input travels,
  measured at the rest bank;
- `joint` — the node-name list of the node the control's coordinate poses;
- `coordinate` — a key of `program.coordinates`;
- `axis` — three numbers in the joint node's own frame;
- `origin` — three numbers in the same frame, the point the joint turns
  about.

The key is **absent** when nothing is declared, the version stays 5, and
the entry carries no expression, so `bindings` and the program's
`identity` are untouched. The viewer's API version is the capability gate.
The acceptance document — the Pascaline module built through that
framework — carries six entries: three `button` on `Add one` / `Add ten` /
`Add hundred`, three `turn` with `per_unit` `-36.0`, every one with
`joint` `[<column>, "input"]`, `coordinate` `<column>.input.turn`, `axis`
`[1, 0, 0]` and `origin` `[0, 0, 0]`.

### What exists here to build on

- `run()` — `trigger(name)`, `move(input, {by, duration})`, `rate(input,
  rate)`, each resolving when its commands RETIRE with the travel admitted.
  `request(key, unit, issue)` in `viewer.ts` is the one door every
  on-screen control already goes through: it starts a paused run, marks the
  control busy, and writes the outcome to the panel.
- `runControls.ts` — the running chrome decided as pure data and tested in
  plain node. This change repeats that split exactly.
- `WidgetTree` — `requirePath(path)` resolves a node-name path to a subtree
  and refuses an unknown or ambiguous one by name; `group` is a public
  `THREE.Group`; `applyVisibility` sets `group.visible` for a hidden
  subtree and `mesh.visible` for everything outside the focused one.
- `operationsMatrix` composes a node's operations as `M_n · … · M_1`, so a
  node's `matrixWorld` maps points of that node's OWN frame to world.

## Goals / Non-Goals

**Goals:**

- A part a document names is pressable and turnable, through the same
  `run()` command interface the panel uses, with the same outcome
  reporting.
- A `controls` table this viewer cannot resolve is refused by name before
  anything renders.
- A host can suppress the affordance and still read the table and drive the
  run.
- Every decision the gesture makes is pure data, tested in plain node.

**Non-Goals:**

- **No two-way binding.** Nothing here writes a coordinate. The part is
  posed only by the committed bank, and follows commits, never the pointer.
- **No slider, no timeline**, for a running document — unchanged from
  ADR-048.
- **No new protocol.** A press is a `trigger` and a turn is a sequence of
  `move`s; `run/protocol.ts`, `run/run.ts` and the worker are untouched.
- **No `Slide`** (a prismatic drag). The framework proposes none, and this
  change reads only the two kinds it publishes.
- **No dialling by position** (a stylus set at digit *n* and turned to the
  stop). That is the historical Pascaline's gesture and belongs to the
  module, not to the viewer.
- **No change to the posed chrome** of versions 1 to 4, and no change to
  the navigator, the inspector layout or the export page beyond the options
  they already pass through.

## Decisions

### 1. Reading the table

#### D1. The table is validated at load, on the same surface as an undeclared driver id

`assertRenderable(document, sourceUrl)` is where this viewer already
refuses a version it cannot read, a flexible technology it cannot
evaluate, a bindings table it cannot resolve, a program it cannot execute
and an expression naming an undeclared driver — **before a single thing is
rendered**, so a broken producer is loud rather than half-drawn. The
`controls` table joins it, after `loadProgram` (which the entries
reference) and before the tree walk. `LoadedDocument` gains
`controls: LoadedControl[]`, the parsed and checked entries in the
document's own key order; a document with no key gets `[]`.

Refused, each naming the document, the control's key and the offending
value:

1. `controls` present and not an object; an entry that is not an object.
2. `kind` neither `"button"` nor `"turn"`.
3. `part` or `joint` not a list of strings, or not resolving to exactly one
   node of the document's tree — reusing `requirePath`'s own
   `Unknown`/`Ambiguous assembly path` vocabulary.
4. `joint` not an ancestor-or-self of `part`. ADR-112 §2 derives the
   coordinate from "the nearest ancestor-or-self of the part that declares
   a joint the run banks", so this cannot be true of a well-formed
   document, and if it is false the gesture's geometry is meaningless.
5. `instruction` (button) not a key of `instructions`; `input` (turn) not a
   key of `drivers`; `coordinate` not a key of `program.coordinates` — each
   listing the keys that do exist, as the run's own refusals do.
6. `per_unit` (turn) missing, not finite, or zero. The framework refuses a
   zero at publication; a zero reaching here would make the quantum
   infinite and the drag dead.
7. `axis` or `origin` not three finite numbers; `axis` of zero length.
8. The joint node's operations do not **begin** with the joint's own
   placement: zero or more translations and then a rotation whose
   expression is exactly `coordinate`. Both shapes the framework publishes
   qualify — `['r', id, axis]` alone for a joint through its node's origin,
   and `['t', -a], ['r', id, axis], ['t', a]` for a `Revolute(at=a)` — and
   the second is exactly what the entry's `origin` exists for. See D6.
9. Two controls of the **same kind** naming the same part (see D3).
10. A `controls` table on a document that carries no program — every
    version 1 to 4 document, and a version 5 one without a run. The
    framework refuses a control under a non-running root; a table here has
    nothing to submit a request to, and ignoring it silently would hide a
    producer's mistake.

*Alternative that lost:* read the table lazily and skip an entry that does
not resolve. It would put a viewer on screen that is missing exactly the
control the author cared about, with no message — the posture this
repository refuses everywhere else. The one thing the framework itself
drops silently is a control whose part **this render omitted**, and it
drops it *at publication*: such a control never reaches a document, so
there is nothing here to be lenient about.

#### D2. A document without the key is byte-for-byte the document of today

No `controls` key means `[]`, no listeners, no raycasting, no hover
handler, and `controls()` answering `[]`. Versions 1 to 4 reach exactly
the code they reach today, which is the same promise `bindings` and
`program` were added under.

#### D3. Two controls of one kind on one part are refused

A part may legitimately carry a `button` **and** a `turn` — the Pascaline's
dials carry both, and a press and a drag are different gestures on the same
mesh. Two buttons on one part is different: a press has one meaning and the
viewer would have to invent which. The document's key order is stable, so
picking the first would be deterministic; it would not be what the author
asked for, and a maker would never learn which one they got.

*Alternative recorded, not taken:* present the part with the first button
by key order and list every naming control in the title. It never refuses a
legal document, and it silently answers a question only the author can.
**This is an open question for the reviewer** (§Open Questions 1): it is
the one place this design refuses a document the framework permits.

### 2. The affordance

#### D4. A mesh finds its control through the tree, not through a back-reference

§5 of the plan note expected "each mesh gets a back-reference to its tree
node at load". `tree.ts` needs no such field: `tree.requirePath(control.part)`
already returns the part's subtree and refuses an unknown path by name, and
`subtree.group.traverse` enumerates its meshes. So `viewer.ts` builds one
`Map<THREE.Mesh, LoadedControl[]>` per load, keyed by the meshes actually
in the scene, and rebuilds it after every `replaceTree`, `manifestChanged`
and `artifactChanged` — the three places a mesh can be replaced. `tree.ts`
is not touched at all.

*Why this is better:* a `userData` field on a mesh survives into
`artifactChanged`'s freshly loaded replacement only if every construction
site remembers to set it; a map rebuilt at the three points the tree
changes cannot go stale without one of those three failing loudly.

#### D5. A pick is the nearest VISIBLE mesh, and it must belong to a control

§5 says the ray is cast "against control meshes only". This design casts
against the whole tree and takes the nearest hit, then asks whether that
mesh is in the map.

The reason is occlusion. three.js's `Raycaster` in this version does **not**
consult `Object3D.visible` at all (`intersectObject` tests only
`layers`), so visibility has to be filtered here whatever else is decided:
a hit is kept only when the mesh and every ancestor up to the scene are
`visible`. That single filter is what makes "a part the navigator hid, or
focused out, is not pressable" true — `applyVisibility` sets
`mesh.visible = inFocusedSubtree` and `group.visible = false` for a hidden
subtree. Having paid for the filter, casting against the whole tree costs
one more traversal of ~45 meshes with bounding-sphere pre-tests, and buys
the rule a maker expects: **a part in front of a control is in front of
it**, and a dial under a closed lid is not pressed through the lid.

Hover raycasting is throttled to at most one cast per animation frame, and
is installed only when the document has controls and `partControls` is
`'inline'`.

*This is a deviation from §5, recorded with its reason.*

#### D6. The gesture's world line comes from the joint node's `matrixWorld`

ADR-112 §3 states the consumer rule: "a consumer computes the world line
from one node's world matrix with no case analysis". Concretely, with `W`
the joint node's `matrixWorld`:

- world origin `O = W · origin`;
- world axis `A = normalize(W's rotation · axis)`.

This is exact, and it is exact *while the joint turns*: the joint's own
rotation `R` maps its own axis line to itself, so `W · L` is the same line
whichever angle the joint stands at. The plane therefore does not move
under the drag that is moving the part.

It is exact **on one condition**: the joint's placement must be the
LEADING run of its node's operations, so that `axis` and `origin` — which
the framework publishes in the node's OWN frame, before any of its
operations — really are in the frame `matrixWorld` maps from. The
framework's placement takes two shapes and both satisfy it: `r` alone for
a joint through the node's placed origin, and `t(−a), r, t(a)` for a
`Revolute(at=a)`, whose entry publishes `origin = a`. In both, the
composite of the leading run is a rotation about the own-frame line
`(origin, axis)`, which it fixes, so `W · origin` and `W`'s rotation of
`axis` are the world line at every joint angle. Only motion applied to the
node *before* the joint's slot — hand-written `apply_motion` ahead of the
joint, which ADR-112 §2's narrowing does not itself refuse — would put
`origin` in a different frame, and that is what D1 refusal 8 guards: the
operations must begin with translations only and then the rotation naming
`coordinate`. A test pins the off-centre shape by asserting that `origin`
equals the negated leading translation of such a node. Every one of the
nine joints in the acceptance document is the first shape, at index 0 of
2. A document that fails the check is refused by name rather than turned
about a wrong line.

Handedness: `operationsMatrix` builds a rotation with
`makeRotationAxis(axis, degrees→rad)`, right-handed about `axis`, and a
document's operations are only `t` and `r` — no mirror — so `W` is rigid
and a right-handed sweep about `A` is in the same units and the same sense
as the coordinate. A sweep of `s` degrees about `A` is a coordinate delta
of `s`.

#### D7. Hover is a cursor, a title and an emissive lift

On hover over a control part: `cursor: pointer` on the canvas; the canvas's
`title` set to the display names of every control naming that part
(`"units dial · turn units"`); and, for each of the part's meshes whose
material carries an `emissive` colour, that colour lifted to a dim grey and
restored on unhover. A node with no declared colour renders through
`MeshNormalMaterial`, which has no `emissive`: it gets the cursor and the
title and no lift, and that is said out loud rather than worked around. The
highlight is cleared on unhover, on gesture end, on dispose and before any
tree reconcile, because `setColor` replaces materials.

*Alternative that lost:* a `Box3Helper` outline around the part's world
bounds. It is material-independent and easy to assert, and it draws a box
around a dial, which is worse to look at than no highlight at all.

### 3. The press

#### D8. A press is a pointerup inside the movement threshold

`pointerdown` on a control part (D5) in the capture phase on the
**container** — an ancestor of the canvas, so it runs strictly before
`OrbitControls`' own listener on the canvas, whatever registration order
would otherwise decide — does four things: `stopPropagation()` so
OrbitControls never sees the event, `controls.enabled = false` for the
gesture, `setPointerCapture` on the canvas, and the gesture record.

The gesture is a **press** until the pointer has moved more than
`PRESS_SLOP = 4` CSS pixels from the down point; after that it is a drag
for the rest of the gesture and a later `pointerup` is not a press. A
`pointerup` while still a press, on a part carrying a `button`, issues
`request(instruction, null, () => run.trigger(instruction))`. A press on a
part carrying only a `turn` does nothing and reports nothing: there is no
instruction to submit, and inventing one would move the machine in a way
nobody declared.

Four pixels is the same order as a native click's slop and small enough
that a dial's quantum (36° of sweep) is never reached inside it.

#### D9. The outcome is reported twice through one path

`request(key, unit, issue)` already writes the outcome to the panel's
control for `key`. It gains one optional argument — the client point the
request was made at — and, when given, also shows a **transient label**
there: a small absolutely-positioned element inside the container carrying
`formatOutcome(report)`, `role="status"`, replaced by the next report and
removed after a few seconds or on dispose. One code path, two places, and
`formatOutcome` is the existing function, so a press that is blocked says
exactly what a nudge that is blocked says.

When the panel is suppressed (`driverControls: 'none'`) the label is the
only report; when part controls are suppressed and the panel is not, the
panel is. Neither switch affects what the run does.

### 4. The turn

#### D10. The sweep is measured in the joint's plane, and the mode is fixed at pointerdown

At `pointerdown`: build the ray through the pointer (`Raycaster.setFromCamera`),
take `O` and `A` from D6, and choose the measuring mode **once**:

- **In-plane** when `|ray.direction · A| ≥ EDGE_ON`. The ray meets the plane
  `{x : (x − O) · A = 0}` at `Q`; the reference direction is
  `u₀ = normalize(Q₀ − O)`.
- **Screen** when it is below `EDGE_ON`, or when `|Q₀ − O|` is within
  `MIN_RADIUS` of zero (the pointer came down on the axis itself, where the
  angle is undefined). `O` is projected to client pixels and the angle is
  measured about that point in screen space.

`EDGE_ON = 0.15` — about 8.6° between the ray and the plane. Below it the
intersection runs away toward infinity and a pixel of pointer movement
becomes an unbounded jump in angle; above it the in-plane measurement is
the honest one, because it is the angle the maker's hand is actually making
about the part's own axle. The mode is fixed for the gesture, so the sweep
cannot discontinuously change meaning half-way through — and it need not
change, because orbiting is suspended and the camera cannot move.

The screen fallback's sign: a rotation about an axis pointing **toward** the
viewer reads counter-clockwise on screen, so the screen angle (measured in
a y-up frame, which is the CSS frame with `dy` negated) is multiplied by
`+1` when `A · (O − cameraPosition) < 0` and `−1` otherwise. Exactly
edge-on, that dot product is zero and the sign is genuinely arbitrary; the
convention is `+1`, and the maker who finds the dial turning the wrong way
orbits a few degrees and gets the in-plane mode. Said plainly in the spec
rather than hidden.

The sweep is **unwrapped**: each `pointermove` adds the signed angle from
the previous direction to the current one, so a drag of more than half a
turn keeps counting instead of folding back.

#### D11. A quantum is committed, not accumulated, and only one is ever outstanding

The quantum is `|nudge.amount × per_unit|` degrees of sweep — the input's
**current** nudge amount, the one the panel's field configures, so a maker
who sets the nudge to 5 digits drags in fives. At the default it is
`1 × 36 = 36°`, one digit of a Pascaline dial.

The planner (pure, in `partControls.ts`) holds:

- `origin` — the sweep value the last **committed** quantum ended at, 0 at
  pointerdown;
- `sweep` — the unwrapped total;
- `outstanding` — whether a `move` this gesture issued has yet to retire;
- `stalled` — the direction, if any, whose last request did not complete.

On each sweep update, and again whenever a request retires, the planner is
asked what to do. It issues one quantum when `|sweep − origin| ≥ quantum`,
nothing is outstanding, and that direction is not stalled. The request is
`move(input, {by: sign × amount, duration: seconds})` where
`sign = sign((sweep − origin) / per_unit)` — division, because `per_unit`
is coordinate units per input unit and may be negative, which on the
Pascaline it is: a sweep of −36° asks for `+1` digit.

When it retires:

- `completed` → `origin += sign × quantum`; `stalled` cleared; ask again
  (the pointer may already be another quantum ahead, which is how a fast
  drag catches up).
- `blocked`, `refused` or `cancelled` → `origin` unchanged, and that
  direction is `stalled` until `|sweep − origin| < quantum` again — that
  is, until the maker backs off or reverses.

Two rules are doing work here.

**One outstanding, because the run says so.** `Run.claim` throws when an
input already has an active command: "an input has one owner at a time".
A drag that issued a second `move` while the first was running would get a
refusal rather than a movement, on every quantum after the first. So the
planner issues the next quantum only when the previous retires, and keeps
at most one in the air. It deliberately does **not** queue a backlog: the
count of quanta owed is not stored, it is *recomputed* from `sweep − origin`
each time, so a maker who drags forward and back nets out instead of
paying for both.

**A blocked outcome does not advance the origin**, which is ADR-048's
"a blocked request accumulates no hidden movement" applied to a gesture: a
drag into the ratchet reports blocked and leaves nothing to be executed
later. The cost is that a *partially* admitted quantum leaves the pointer
leading the part by the unadmitted remainder. That is the same trade the
framework already states about `per_unit` being measured at rest — the
gesture is less tight, and never wrong, because the part is posed only by
what the run commits.

*Alternative recorded, not taken:* advance the origin by the travel
actually admitted. It keeps pointer and part in register through a partial
block, and it adds a second rule to a place where one rule is provably
enough for the acceptance machine (whose ratchet admits exactly zero).
**Open question 2.**

**The stall latch** exists so that holding a drag against a hard stop does
not fire one blocked request every retire, forever. Without it the maker
would get a string of identical blocked reports and the run a request every
0.2 simulated seconds; with it, one report, and nothing until the gesture
means something new.

#### D12. The part never follows the pointer

Nothing in the gesture writes a coordinate, sets a matrix, or poses
anything. The only effect a drag has on the scene is through the run's
committed frames, which reach the tree through `posed(frame.moved)` exactly
as they do for a panel nudge. So the pointer may run ahead and the dial
catch up at the nudge's duration, and a machine that refuses to move does
not move.

#### D13. The gesture ends on the same five sides a jog does

`pointerup`, `pointercancel`, `lostpointercapture`, the window's `blur`,
and a `visibilitychange` to hidden. Each restores `controls.enabled`,
releases the capture, clears the highlight and forgets the planner. A
`move` already in flight is left to retire and report on its own — it is a
movement the machine agreed to make, and ADR-048's rule for a jog (cancel
the *rate*) does not apply: a `move` has an end of its own, and cancelling
it would be the viewer inventing a stop the maker did not ask for.

### 5. The mount surface

#### D14. `partControls` is its own switch

`ViewerOptions.partControls?: 'inline' | 'none'`, default `'inline'`,
resolved in `options.ts` beside `driverControls`, with
`showsPartControls(mode, hasControls)` mirroring `showsRunControls`. It is
**independent** of `driverControls`, because "a host that builds its own
instrument panel still wants the dial pressable" — the shop floor is
exactly that host. What is gated is the pixels and the pointer, never the
interface: `controls()` answers, and the run API is whole, either way.

`InspectorOptions extends ViewerOptions`, so the inspector layout, the
development page and the export page pass it through with no change of
their own. `capture.py`'s `mount_options` adds `partControls: 'none'`:
the framework's capture publishes no `controls` table at all, so this can
never matter, and a still photograph is the last place a hover affordance
should be able to appear.

#### D15. `controls()` reports where each part is, and a point that reaches it

```ts
interface PartControlView {
  name: string;                    // the table's key
  kind: 'button' | 'turn';
  part: string[];
  instruction?: string;            // button
  input?: string;                  // turn
  perUnit?: number;                // turn
  joint: string[];
  coordinate: string;
  /** The part's on-screen bounds in CSS pixels, in the viewport frame a
   * DOMRect uses; null when the part is not visible or is wholly off
   * screen. */
  rect: { x: number; y: number; width: number; height: number } | null;
  /** A point in the same frame at which a press reaches this control
   * right now, or null when none does. */
  point: { x: number; y: number } | null;
}
controls(): PartControlView[];
```

Viewport coordinates, not canvas-relative ones, because that is what every
DOM rectangle around them is and what a test's `page.mouse.click(x, y)`
takes. `rect` is the projection of the part's visible meshes' world bounds.

`point` earns its place: the centre of a dial's bounding rectangle is its
axle, which on a real dial may be a hole, and a host or a test that clicked
the centre would miss the part and get nothing, confusingly. So the widget
finds the point the way a press finds it — by raycasting, D5's nearest-
visible-hit rule included — starting at the rect's centre and then walking
a bounded grid inside the rect, and reports the first point that actually
reaches the control. `null` says honestly that nothing does.

`controls()` answers for a document with no table (`[]`), for a suppressed
affordance (the full list, rects and all), and for a part the navigator
has hidden (`rect: null, point: null`). One question, one truthful answer.

#### D16. The API version rises to 12

A host that means to present a machine a maker can touch — the shop floor,
a gallery page — needs to know the bundle it is about to mount can do it,
and the API version is the only number that answers. Declared once in
`package.json`, pinned by `version.test.ts`, reported by `describe`,
`bundle.py` and every handle, and written into the README's table. The
document versions this build reads do **not** change: `controls` is
additive within version 5, exactly as ADR-112 decided.

### 6. Tests

#### D17. The planner is pure data and pure vector math, tested in node

`partControls.ts` imports neither the DOM nor three.js — vectors are
`[number, number, number]` tuples, rays are an origin and a direction,
and rectangles are plain objects — so every decision above is a node test
beside `runControls.test.ts`: the load-time refusals one by one; the mode
choice at `EDGE_ON`; the plane intersection and the unwrapped sweep; the
screen fallback and its sign; sweep→quanta with the sign of a negative
`per_unit`; the one-outstanding rule; the blocked-origin rule; the stall
latch and its release. `viewer.ts` keeps the three.js and the DOM, and
decides nothing.

#### D18. The acceptance drives a real document with real controls

`tests/fixtures/touched/` is a **real** version 5 document with six
controls, published by the framework from the Pascaline module's own
classes (it imports `simulation.module` and `simulation.pascaline`
unchanged; only the root class differs, to declare the `controls` table
the module itself does not carry until its own later cycle). It is
committed verbatim, like the `pascaline` fixture beside it, and beside it
sit stand-in cube meshes at the fifteen model paths it names — the same
684-byte unit cube that fixture already uses, because this repository tests
a run and a gesture, not a mesh.

Three of its fifteen model paths differ from the `pascaline` fixture's, so
it carries its own `vendor/` tree rather than borrowing that one; the whole
directory is about 42 kB.

The Playwright acceptance in `tests/test_running_document.py`:

- presses a dial with the real mouse at the point `controls()` reports, and
  reads the run — the units input at one digit, the drum turned, the
  transient label and the panel's own button both reporting completed;
- drags the units dial **backward** across more than one quantum and reads
  **blocked**: at the rest bank `units.input.turn` stands at its own stop
  (the ratchet's span is `high = 36·ceil(turn/36)`, which at rest is the
  coordinate's own value), so the very first backward quantum is refused
  travel and the drum does not move. That is the plan's "drag against the
  ratchet reports blocked and leaves no backlog", on the real machine;
- drags it **forward** one quantum and reads one digit admitted;
- and photographs the hover affordance, the press and the blocked drag.
  Pixels are evidence.

## Risks / Trade-offs

- **A partial block leaves the pointer ahead of the part** (D11) →
  Accepted, with its reason stated in the spec: the part follows commits,
  so the gesture is looser and never wrong. The alternative is one line
  away if the reviewer prefers it (Open question 2).

- **`per_unit` is a reading at rest** (the framework's own caveat) → A law
  whose response to that input changes with state makes the dial lead or
  lag the pointer. The same mitigation: the machine is posed by what the
  run commits. Nothing here can be wrong because of it.

- **Edge-on drags are a guess** (D10) → Below `EDGE_ON` the sign of a screen
  sweep is not derivable from the geometry. Mitigated by choosing the mode
  once, by saying so in the spec, and by the fact that orbiting a few
  degrees restores the exact mode.

- **A joint whose placement is not its node's first operation** (D6) →
  Refused by name at load rather than drifting silently. If such a document
  ever exists, the fix is a framework-side statement of which frame
  `axis`/`origin` are in, not a guess here. **Open question 3.**

- **A whole-tree raycast per hover frame** (D5) → ~45 meshes with
  bounding-sphere pre-tests, one cast per animation frame at most, and only
  for a document that declares controls with the affordance presented. If a
  much larger assembly ever makes this measurable, the mitigation is a
  precomputed bounds hierarchy, not giving up occlusion.

- **A hovered part with no declared colour gets no highlight** (D7) →
  `MeshNormalMaterial` has no `emissive`. The cursor and the title still
  say the part is touchable. Said in the spec rather than hidden.

- **Refusing two buttons on one part** (D3) → The one document shape this
  viewer refuses that the framework permits. Open question 1.

- **The fixture is a probe build, not the module's own** (D18) → It is
  produced by the real framework from the real module's classes, and the
  module's own `turn-the-dials` cycle will carry the identical table. If
  the module's eventual declaration differs, the fixture is replaced from
  its build, as the `pascaline` fixture would be.

## Migration Plan

None. The change is additive in every direction: a document without the
key behaves exactly as it does today, a host that passes no new option gets
the affordance for a document that declares one, and a host that wants none
passes `partControls: 'none'`. The API version rise is the only thing a
consumer must notice, and noticing it is what it is for.

## Open Questions

1. **Two controls of one kind on one part: refuse, or take the first by key
   order?** D3 refuses. The framework permits the document. Refusing is
   this repository's posture everywhere else ("nothing is substituted"),
   and it is the only place this design is stricter than the producer.
2. **Should a partially admitted quantum advance the sweep origin by the
   travel actually admitted?** D11 does not, following the plan note. The
   alternative keeps pointer and part in register and costs one more rule.
   The acceptance machine cannot tell the two apart (its ratchet admits
   zero), so this is a judgement about machines not yet built.
3. **Should the framework state the frame `axis` and `origin` are in, rather
   than the viewer checking?** D6 checks the joint's first operation because
   the published rule ("compute from one node's world matrix") is only true
   when the joint's placement is first. Every joint in the acceptance
   document satisfies it. Whether that is a guarantee or a coincidence is
   the framework's to say.
4. **Should a press take the instruction's own duration?** It does — the
   instruction declares it and the button references it, which is the
   pilot's rule. Whether a *touched* instruction should be faster than a
   *panelled* one is a knob on the model, not a decision here; noted
   because the plan note's §6 raises it for the module.
5. **Should a drag show the crossings and stops the run records?** They
   arrive on every frame and they are what makes a carry legible.
   `drive-the-run-on-screen`'s own open question 2 deferred this "to the
   dragging cycle"; this design defers it again, because the transient
   label is already the report a gesture needs and a stream of crossings is
   a different feature.

## Reviewer decisions, 2026-09-14

Ruled at the ratification gate the pilot delegated, so implementation does
not wait on them:

1. **Refuse two controls of one kind on one part** (D3), as proposed. The
   viewer is stricter than the producer here; the matching compile-time
   refusal is a framework follow-up, recorded outside this cycle, so the
   two agree.
2. **A partially admitted quantum does not advance the origin** (D11), as
   proposed; the spec's "no remainder" is the rule and the acceptance
   machine admits zero.
3. **The frame is already stated by the framework**: `axis` and `origin`
   are in the joint node's own frame, before any of its operations. The
   viewer's check is therefore that the placement is the LEADING run of
   the node's operations (translations, then the rotation), which accepts
   both shapes the framework publishes. The proposal's first draft of D1.8
   and D6 required the rotation to be the very first operation, which
   would have refused the off-centre `Revolute(at=...)` that `origin`
   exists for; corrected during review. A framework follow-up may state
   the leading-run guarantee in the export spec, or refuse motion applied
   before a controlled joint.
4. **A press takes the instruction's own duration.** A faster touched
   instruction is a knob on the model.
5. **Crossings and stops stay deferred.**

## The ADR to extract

One, in this repository's log, the next number after ADR-052, in `EXPORT`:

- **A pick is bound to a declared control through the same request
  interface; the part follows commits, never the pointer.** The decision
  that a part becomes touchable only because the document says so; that a
  press is the declared instruction and a drag is a sequence of relative
  moves on the declared input, issued through the same `run()` handle and
  reported the same way; that the gesture's geometry is read off the
  joint's world matrix and its ratio off the published `per_unit`, so
  nothing is measured twice; that a quantum is committed rather than
  accumulated, one at a time, with a blocked outcome leaving no backlog;
  and that nothing in the gesture writes a coordinate. Beside ADR-048,
  which promised it, and consuming solid-node's ADR-112, which declared it.

Not written now. It is extracted after implementation, from what the
implementation proved.
