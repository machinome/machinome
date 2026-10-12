## Why

`drive-the-run-on-screen` gave a running document a panel, and closed with
a promise in ADR-048's own Consequences: *"Constrained dragging of a part
is deliberately out: the next viewer cycle binds a pick to a declared
input through this same command interface, with the same blocked-travel
reporting."* This is that cycle. The pilot's ask has been the same since
2026-09-12 — **click the dial, and the dial advances** — and the panel
only ever answered half of it: a maker drives the Pascaline module by
reading its inputs' qualified ids off a list, not by touching the machine
in front of them.

The other half is now possible because the framework built it. The
archived solid-node change `declare-controls-on-parts` (ADR-112) lets an
assembly declare `controls` beside `instructions` — `Button(part,
instruction)` and `Turn(part, input)` — and publishes them as a top-level
`controls` table in a version 5 document, additively, with the gesture's
geometry (`joint`, `coordinate`, `axis`, `origin`) read off the tree and
the ratio (`per_unit`) measured off the compiled program. The viewer
cannot infer any of that for itself: `tens.input.turn` is reached by two
inputs, and the number drum turns without anybody being allowed to turn
it. The binding is a declaration, and this change is the viewer reading
it.

## What Changes

- **A part a document names in its `controls` table becomes touchable.**
  On hover it takes a pointer cursor, a light highlight and its control's
  display names as a title; every other part orbits the camera exactly as
  it does today. A part the navigator has hidden or focused out is not
  touchable, and a part behind another part is not reached through it.

- **A press submits the declared instruction.** `pointerdown` on a control
  part captures the pointer, suspends orbiting for the gesture, and a
  `pointerup` within a small movement threshold issues
  `run().trigger(instruction)` — the same call the panel's button makes.
  The outcome is reported through one path: a transient label at the press
  point and the panel's own button for that instruction. A press into a
  paused run starts it, exactly as ADR-048 rule 7 says for the panel.

- **A drag turns the part by whole quanta.** Movement past the threshold is
  a drag about the control's joint: the pointer ray meets the plane through
  the joint's world origin normal to its world axis, and the swept angle
  about that origin is measured against the `pointerdown` angle. Each time
  the accumulated sweep crosses one **quantum** — the input's current nudge
  amount times `per_unit`, one digit = 36° on a Pascaline dial — one
  `move(input, {by: ±amount, duration})` is issued, at most one at a time
  because the run gives an input one owner. **The part never follows the
  pointer; it follows commits.** A blocked outcome does not advance the
  sweep origin and leaves no backlog, so a drag against the ratchet reports
  blocked and moves nothing. The gesture ends on the same five sides a jog
  does: pointerup, pointercancel, lost capture, lost window focus, and a
  page that stops being displayed.

- **A `controls` table the viewer cannot resolve is refused by name**,
  before anything renders — a `part` or `joint` path that does not resolve
  in the document's own tree, an `instruction`, `input` or `coordinate`
  that is not a key of the table it must belong to, a `kind` that is
  neither `button` nor `turn`, a `per_unit` of zero, a joint node whose own
  first operation is not the rotation the control names. This is the
  refusal surface an undeclared driver id and an unreadable program already
  stand on.

- **A new mount option, `partControls: 'inline' | 'none'`**, independent of
  `driverControls`, because a host that builds its own instrument panel
  still wants the dial pressable. **A new handle operation,
  `controls()`**, listing the document's controls with each part's current
  on-screen rectangle and a point a press actually reaches, for hosts and
  for tests.

- **The declared API version rises from 11 to 12.** A host that means to
  present a machine a maker can touch needs a number it can check before
  mounting, and there is no other number to check it by.

- **Nothing else moves.** No two-way binding, and nothing anywhere writes a
  coordinate. There is no slider and no timeline. A document that carries
  no `controls` key is exactly the document of today, and versions 1 to 4
  reach the code they always did. The worker protocol is untouched: a press
  is a `trigger` and a turn is a sequence of `move`s, indistinguishable
  from the panel's.

## Capabilities

### New Capabilities

None. The widget's running chrome already has a home.

### Modified Capabilities

- `viewer-package`: three new requirements — a maker presses and turns the
  part itself; a host reads the controls a document's parts carry; a
  `controls` table the viewer cannot resolve is refused by name — and three
  modified ones: the loader reads a version 5 document's optional
  `controls` table, the host's presentation choice gains an independent
  switch for the part affordance, and the declared API version becomes 12.

Capabilities needing no delta:

- `viewer-distribution`: `apiVersion` is already specified as coming from
  the widget package's own single declaration, so the rise to 12 moves no
  distribution contract and changes no sentence there.
- `snapshot-capture`: the framework's capture publishes no `controls` table
  at all, by ADR-112's own decision, and the capture's contract already
  fixes what the picture contains. It passes `partControls: 'none'` as
  belt-and-braces; no requirement changes.
- `viewer-assembly-navigation`: part controls obey the visibility the
  navigation requirements already define; they add nothing to it.
- `inspector-layout`, `development-server`: both mount the same widget and
  inherit the behaviour through options they already pass through.

## Impact

- `solid_node_viewer/widget/src/partControls.ts` — **new**: the `controls`
  table's types, its load-time validation, and the gesture's planning as
  pure data and pure vector math — sweep to quanta, the blocked-origin
  rule, the one-outstanding rule, the plane and its edge-on fallback. No
  DOM, no three.js, tested in plain node beside `runControls.ts`.
- `solid_node_viewer/widget/src/viewer.ts` — the pick, the hover
  affordance, the gesture and its five release paths, the transient
  outcome label, `controls()` on the handle, and the mesh→control map
  rebuilt on every load, republish and artifact change.
- `solid_node_viewer/widget/src/types.ts` — `ManifestControl` and
  `Manifest.controls`.
- `solid_node_viewer/widget/src/options.ts` — `partControls` and
  `showsPartControls`.
- `solid_node_viewer/widget/package.json`, `src/version.ts` (unchanged
  mechanically), `src/version.test.ts` — API version 12.
- `solid_node_viewer/capture.py` — `partControls: 'none'` in the mount
  options.
- `solid_node_viewer/widget/src/tree.ts` — nothing. `requirePath` and the
  public `group` already give a control's part and its meshes.
- `tests/fixtures/touched/` — **new**: a real version 5 document carrying
  six controls, published by the framework from the Pascaline module's own
  classes, beside stand-in cube meshes at the fifteen paths it names.
- `tests/test_running_document.py` — the acceptance grows a third class: a
  maker presses a dial and reads the run, and drags one against the ratchet
  and reads blocked.
- `tests/test_bundle.py`, `tests/test_widget_e2e.py` — the declared API
  version.
- `README.md`, `CHANGELOG.md` (still 0.2.0, unreleased), and one new ADR in
  `docs/adrs/EXPORT/`, the next number after ADR-052.
- **Depends on** solid-node's archived `declare-controls-on-parts` for the
  document it reads. That change is implemented and archived in the
  framework worktree; this cycle needs no framework code, only a document
  built through it, which the fixture carries.
