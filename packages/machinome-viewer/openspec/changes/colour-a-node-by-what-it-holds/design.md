## Context

The navigator (ADR-050, change `mount-the-navigator`) decides its rows in `src/navtree.ts` as pure data and renders them in `src/navigator.ts`. A row's colour today is its node's snapshot colour, read through: `NavigatorRow.color = node.color` (`navtree.ts:105`); `chipState` fills the chip `'color'` when the row is shown and its colour is not null, `'neutral'` when it is null, `'none'` when hidden (`navtree.ts:132-138`); `navigator.ts` writes the row's colour, or the neutral variable, to `--machinome-nav-node-color` on the row (`navigator.ts:317-318`), which the stylesheet paints on a checked chip only.

The snapshot's colour is the node's effective inherited colour: `WidgetTree` takes `data.color ?? inheritedColor` (`tree.ts:306`) and `assembly()` reports the current resolved choice, `color: this.color` (`tree.ts:724`). A node with a non-null effective colour therefore has only non-null effective colours beneath it: a child's `null` inherits, and a conditional colour resolves to one of its two choices, which document admission requires to be six-digit hex strings (`color.ts:9-21`, `resolveColor` at `:30-39`).

What a node holds, as the snapshot can tell it: `AssemblyNode` carries `name`, `path`, `color`, `model` and `children` (`tree.ts:64-70`), and `model` is `this.model !== undefined` (`tree.ts:725`), true only for a node carrying a model file. A flexible leaf has no model file (`types.ts:77-79`, "neither a model nor children"), so it reports `model: false`, exactly as an empty assembly does. The framework writes a rigid node as "a terminal model reference" and a flexible leaf as "a terminal `flexible` object" (`packages/machinome/machinome/core/serializer.py:1003-1008`), so in what the producer writes, every drawn part is a node without children. `WidgetTree` would still draw a node that had both a model and children (`tree.ts:313-335`), and nothing in the viewer refuses one.

Measured on the Enigma I document (proposal): 878 nodes with children, all reporting `color: null`; 3,295 without, of which 2,868 rigid, 426 flexible, one empty (`operation`); no node with both a model and children; no node with children carrying a flexible spec.

## Goals / Non-Goals

**Goals:**

- A row with children shows the colour of what its node holds, when everything it holds shows one colour.
- Everything else a row shows stays as it is: rows without children, rows whose parts differ, the chip's three states, the checked state and the accessible name.
- The snapshot a host reads, the viewer API and the document versions stay as they are.
- One pass over the tree per redraw.

**Non-Goals:**

- Chips that follow the pose. A colour the machine chooses reaches the navigator when an assembly change is notified, as today (Decision 4); that is recorded as a finding, not changed.
- A colour for a group of mixed parts (a blend, a stripe, a count). The request is about one colour.
- Any option to turn the rule off, any new CSS custom property, any new field of the snapshot.
- Telling a flexible part from an empty assembly in the snapshot (Decision 1, finding W2).

## Decisions

### 1. What "everything inside" means: the nodes without children beneath, and the node's own model

A node's parts are every node without children at or beneath it, each taken at its own snapshot colour (its effective inherited colour, which is what its own row shows), together with the node itself when it reports `model: true`. When the parts all report one same non-null string, the row shows that string. Parts are counted whatever is expanded, focused, hidden or obscured.

The starting position was "the drawn parts at or beneath the node ... each taken at the colour its own row displays". It is corrected in one respect, by the code: the snapshot cannot tell which nodes are drawn. `model` is false for a flexible leaf (`tree.ts:725`; `types.ts:77-79`), so counting only `model: true` nodes would drop the 426 flexible parts of the Enigma I from every group; read that way, 39 of the Enigma's 878 groups would hold no drawn part at all (measured), and a group of grey rigid parts and one flexible part of another colour would show grey. A node without children is what the producer writes every drawn part as (`serializer.py:1003-1008`), so counting those counts every rigid and every flexible part.

What that costs: an empty assembly (a node with neither a model, a flexible spec nor children) counts too, at its own effective colour. Its row is a leaf row that shows that colour today (or the neutral chip), so the group rule counts exactly what the leaf rows show. A group holding an empty assembly that inherits no colour shows no colour of its parts. On the Enigma I the one empty assembly, `operation`, sits under the root, whose parts are mixed anyway: counting nodes without children and counting rigid-or-flexible nodes give the same 302 (by declaration) and 607 (by `off` choice) uniform groups (measured, both readings).

The node's own model is counted because `WidgetTree` draws it (`tree.ts:313-314`), though the producer never writes one on a node with children; it costs one condition.

Colours are compared as the strings the snapshot reports, exactly. Two spellings of one colour (`#24211D` and `#24211d`, `#f00` and `#ff0000`) count as two. The Enigma I has 70 distinct colour strings and no two differ only in case (measured); normalising would need a colour parser in a module that imports no three.js (`mount-the-navigator` design D2), for a case no project has shown.

Alternatives rejected:

- **Only `model: true` parts.** The flexible parts would not count; above.
- **A `flexible` (or `drawn`) field on `AssemblyNode`, or `model: true` for a flexible part.** Either changes the snapshot a host reads, and the first adds API, which ADR-035 and ADR-050 point 8 make a new viewer API version. Nothing in the request needs the navigator to tell a flexible part from an empty assembly. Recorded as finding W2 instead.
- **Recursing on the colours the child rows show** (a group shows a colour when its children's rows all show it). A child row with mixed parts falls back to its own effective colour, and that fallback would then stand in for parts of other colours: a subassembly declaring red that holds blue and green parts shows red, and its parent, holding it and one red part, would show red although only that one part beneath it is red. The rule reads the parts, never a group's fallback (spec scenario "A group's own colour does not stand in for its parts").
- **Counting only visible parts.** The chip describes the node, not the current visibility: hiding a part would recolour its group, and the colour would change under the maker's own gesture, which the visibility control is meant to report separately (Decision 6).

### 2. Where the rule lives: the navigator's row decision only

`navigatorRows` computes the colour each row shows and puts it in `NavigatorRow.color`, whose meaning changes from "the node's effective, inherited colour" to "the colour this row shows". `row.node.color` stays the snapshot's. `AssemblyNode.color` and `WidgetTree.assembly()` do not change, nor do the baseline requirement "A viewer host can inspect the rendered assembly" or `viewer-handle.rst`'s description of the snapshot.

Who reads the snapshot's colour: this package's navigator; the browser tests of conditional colour (`tests/test_state_color.py`, and `tree.test.ts`'s "exposes stable paths and effective inherited colours"), which pin the effective colour; and no host source. The Studio mounts the navigator (`machinome-studio/floor/frontend/src/main.tsx:305-306`) and declares `AssemblyNode` in `floor/frontend/src/machinome-viewer.d.ts:18-24`, but no Studio source reads `.color` of a node (searched: `git grep` over the Studio, its generated design build excluded; its fake bundle in `tests/fixtures/fake_machinome.py` computes the effective colour itself).

The API version does not move. ADR-035 raises it for an incompatible interface change; ADR-050 point 8 raises it when "a capability a host may require is added to the bundle". Neither happens: no method, option, field, class or custom property is added or changes meaning; `--machinome-nav-node-color` was always "per-row data, not theme settings" the component writes (`layouts.rst`, "Navigator variables"), and stays that. The CHANGELOG records behaviour changes of this kind with "Viewer API 30 and document versions 1 through 14 are unchanged", as every bullet under "Unreleased" does.

Alternative rejected: **the rule in the snapshot** (`AssemblyNode.color` becomes the held colour). It would change the meaning of a published field that the baseline spec, the manual and the conditional-colour tests define as the effective inherited colour; a host that recolours its own UI from the snapshot would see a group's colour change for a reason that is the navigator's presentation; and by ADR-035 it is an incompatible change, a new API version, for a request about the navigator.

### 3. What a node shows when its parts are not one colour, and the edge cases

| case | row shows | why |
| --- | --- | --- |
| parts all one non-null colour C | C | the request |
| parts of two or more colours | the node's own effective colour, else neutral | today's |
| a part with no colour among coloured ones | the node's own effective colour, else neutral | a part with no colour is drawn by surface direction (`tree.ts:76-79`, `MeshNormalMaterial`), not in any one colour; and by `tree.ts:306` the node itself then has no effective colour, so the row is neutral, as today |
| all parts without colour | neutral | the node then has no effective colour either (`tree.ts:306`); today's |
| node declares A, parts all show B | B | what the maker sees in the scene is B; the snapshot still reports A (Decision 2) |
| node declares A, parts mixed | A | today's |
| node with a colour and nothing drawn beneath | cannot arise as a row with children: every node with children has at least one node without children beneath it, and that node counts (Decision 1); a node with `children: []` is a leaf row and shows its own colour, as today | |
| a hidden or obscured part | counted | Decision 1; the chip describes the node |
| a hidden group | chip empty with its border, as today | `chipState` fills `'none'` when hidden, whatever the colour |
| a leaf row | its own effective colour | unchanged |

### 4. Colours the machine chooses

What a conditional leaf's chip shows today: the choice its node had when the navigator last received an assembly. The navigator reads `viewer.assembly()` once at mount (`navigator.ts:248`, drawn at `:516`) and redraws from the assembly each notification carries (`navigator.ts:518-519`, `:443`); an expand or a collapse redraws from the assembly it already holds (`navigator.ts:423`). A pose (a driver, a clocked request, a run tick, a reset) recolours the scene through `WidgetTree.update` → `setColor` (`tree.ts:797-799`) and notifies nobody: the viewer notifies only from `replaceTree` (`viewer.ts:2118`), `focusOn` (`:2194`), `artifactChanged` (`:2567`), `manifestChanged` (`:2630`) and `setVisible` (`:2651`), which is the baseline contract ("each accepted operation that publishes a tree or changes the focused root or the visibility state"). So after a key press on the Enigma I the scene lights a current path and the navigator's chips stay at the mount's choice until the maker hides, shows or focuses something or the document is republished, and then jump to the choice at that moment. Read from the source, not observed on a page.

The group rule reads only the assembly the navigator holds, the same one its leaf rows are drawn from, in the same call. So a group row is exactly as current as its parts' rows: whenever they all show one choice, the group shows it; whenever one differs, the group falls back. Group and parts never disagree on screen (spec scenario "A group's colour agrees with parts whose colour the machine chooses").

Today's leaf behaviour is a defect against what the maker sees in the scene, not against the ratified text, which says nothing about when a chip follows a pose. Making chips follow the pose would need a notification the viewer does not send, or the navigator subscribing to poses: a change of the notification contract (ADR-049) and a redraw of up to 4,173 rows per frame on the Enigma I. The rule can be stated honestly without it, so it is not taken up; it is recorded as finding W1 in `workflow/warts.md` (tasks 6.2).

### 5. Cost

One post-order pass over the whole snapshot at the start of each `navigatorRows` call, before the row walk, computes for every node with children the single colour its parts share or that they share none, keeping the result per node object for the row walk to read. Each node is visited once and does constant work (compare one string against the colour its children's subtrees reported). `navigatorRows` is called once per notification or mount (`navigator.ts:443`) and once per expand or collapse (`navigator.ts:423`). The bound is therefore O(N) per redraw for N nodes in the snapshot, 4,173 on the Enigma I, whatever is expanded; the existing row walk is O(rows presented), and `reconcileLocal` already walks all N nodes on every notification (`navtree.ts:223-226`). No walk per row.

The pass is recursive, as `visit` and `collect` already are; the Enigma I is 8 levels deep (measured).

A test pins the bound by counting reads of each node's `children` during one call (tasks 2.1, N13): a constant per node, independent of the tree's size, where a walk per row reads the root's children once per row.

Alternative rejected: **memoising the pass per assembly object** (a `WeakMap` keyed by the snapshot root, so an expand or collapse reuses it). It saves one O(N) pass per expand on a tree where the redraw rebuilds the DOM of every presented row anyway; no measurement shows the pass matters. Not built.

### 6. Visibility does not depend on colour

`chipState` decides `checked` from `row.hidden` and `label` from `row.node.name`, `row.obscured` and `row.hidingAncestor` (`navtree.ts:133-137`); only `fill` reads `row.color`. The change touches `row.color` alone, so neither the checked state nor the accessible name can come to depend on colour; `chipState` is not edited. A test asserts that a uniform group's chip and a mixed group's chip, in the same visibility, have equal `checked` and `label` (tasks 2.1, N11; spec scenario "A group's control carries its parts' colour").

### 7. The ADR question: none

ADR-050 decides that the navigator is a plain-DOM component of the bundle, mounted from a handle alone, holding no copy of the viewer's state, observing and gesturing apart, telling hidden from obscured, styled by a class contract and custom properties, not shadow DOM, publishing no new file, at API 10. It names "effective colour inheritance" as one of the contracts the package took over from the Studio's panel (Context), which is the snapshot's (Decision 2, unchanged), and "visibility that does not depend on colour" (Consequences), which holds (Decision 6). Which colour a row's chip shows is not decided there: `mount-the-navigator` design D5 and D6 settle it as presentation inside the component. This change is a presentation rule inside ADR-050's component, changes none of its points, and needs no ADR.

### 8. Tests

`src/navtree.test.ts`, node environment, a new `describe('the colour a row shows')` with hand-written `AssemblyNode` trees, every row expanded unless the test says otherwise:

- N1 A group with no colour of its own (`G`, `color: null`) holding `p` and `q`, both `#a0a0a0`, `model: true`: `G`'s row colour is `#a0a0a0`. Red on the base: `null`.
- N2 A group of mixed parts (`#a0a0a0`, `#191919`) with no colour: `null`. A group with effective colour `#336699` whose parts are `#a0a0a0` and `#336699`: `#336699`. Passes on the base (today's fallback).
- N3 A part with no colour beside a coloured one, in a group with no colour: `null`. Passes on the base.
- N4 Nested, inner uniform, outer mixed: `Outer(null)` → [`Inner(null)` → [`#a0a0a0`, `#a0a0a0`], `#191919`]: `Inner` `#a0a0a0`, `Outer` `null`. Red on the base at `Inner`.
- N5 A group's own colour does not stand in for its parts: `Outer(null)` → [`Inner(#ff0000)` → [`#0000ff`, `#00ff00`], `#ff0000`]: `Inner` `#ff0000`, `Outer` `null`. Passes on the base; fails an implementation that recurses on the rows' colours (Decision 1).
- N6 Declared colour, parts all override to one other: `G(#ff0000)` → [`#0000ff`, `#0000ff`]: `G`'s row `#0000ff`, `G`'s `node.color` still `#ff0000`. Red on the base: `#ff0000`.
- N7 The node's own model counts: `G(null, model: true)` → [`#a0a0a0`]: `null`; `G(#a0a0a0, model: true)` → [`#a0a0a0`]: `#a0a0a0`. Passes on the base; fails an implementation that ignores the node's own model.
- N8 A flexible part (`model: false`, no children) counts: `G(null)` → [rigid `#a0a0a0`, flexible `#a0a0a0`]: `#a0a0a0` (red on the base); `G(null)` → [rigid `#a0a0a0`, flexible `#ff0000`]: `null`.
- N9 Expansion, focus and visibility do not change it: N1's tree with `G` collapsed; with `p` hidden; with `G` hidden; with `navigation.root` `['G']` and with `['G', 'p']`: `G`'s row `#a0a0a0` in each. Red on the base.
- N10 Rows without children are unchanged: in every tree of N1 to N9, every row without children has `row.color === row.node.color`. Passes on the base.
- N11 The chip of a uniform group, from rows `navigatorRows` returns (not overridden): shown, `{ checked: true, fill: 'color', label: 'Visibility for G' }`; hidden, `{ checked: false, fill: 'none', label: 'Visibility for G' }`; and in each visibility the `checked` and `label` equal those of N2's mixed group's chip renamed to `G`. Red on the base at `fill` (`'neutral'`).
- N12 The marked fixture: the existing "presents one row per part and none for any marking" test gains `row.color` in its compared tuples, so markings change no row's colour. Passes on the base.
- N13 The bound: N1's shape scaled to a chain of 200 nested groups over one part each and to a flat group of 2,000 parts, each node's `children` replaced by a getter that counts reads; one `navigatorRows` call with every row expanded reads no node's `children` more than 4 times. Passes on the base (which reads at most 2); fails a walk per row.

`src/navigator.test.ts`, jsdom, against the stub handle:

- D1 A stub tree `Root(null)` → [`G(null)` → [`p #a0a0a0`, `q #a0a0a0`], `Leaf(null)`]: `G`'s row writes `--machinome-nav-node-color: #a0a0a0`; `Root`'s writes the neutral variable. Red on the base at `G`.
- D2 `G` hidden through its chip (a `change` event on the checkbox): its chip is unchecked, its `aria-label` is `Visibility for G` before and after, and its row still writes `#a0a0a0`. Passes on the base except the colour (red at the colour).
- D3 Colours the machine chooses: push a change whose `G` holds `p` and `q` both `#ff9b32` (`G` row `#ff9b32`), then push one where `q` is `#393d43` (`G` row neutral, `p` row `#ff9b32`, `q` row `#393d43`). Red on the base at the first push.

`src/tree.test.ts`:

- T1 The snapshot keeps the group's own colour: a `WidgetTree` of `group(null)` → [`#a0a0a0`, `#a0a0a0`] and of `group(#ff0000)` → [`#0000ff`, `#0000ff`] reports `color: null` and `color: '#ff0000'` for the group, and the parts' own colours. Passes on the base by design: it pins Decision 2.

The existing tests stay as they are and pass unmodified, `navtree.test.ts`'s "carries the node's already-effective colour through unchanged" included (its root holds a red part and a part with no colour, so it falls back to `null`; `A` holds only red). Its name is kept.

## What the Enigma should show (predictions)

Before: no row with children shows a colour, at any pose (measured on the document: no node with children has an effective colour). After, at the mount's pose: at least 302 rows with children show a colour (the groups whose parts share one declaration resolve to one colour at every pose, because one declaration resolves one way under one scope), and 607 if every conditional colour resolves to its `off` choice at the mount (a prediction; the document's defaults were not evaluated). `keyboard/guide/n8_Anti_Twist_Device_Group_1` shows `#a0a0a0`; its parent `keyboard/guide`, holding `#a0a0a0` and `#191919` parts, shows the neutral chip (measured on the document).

## Risks / Trade-offs

- [A group's chip now says "everything in here is this colour", where a chip with a colour used to mean "this node declares or inherits it"] → A maker reading a chip cannot tell a declared colour from a shared one. The snapshot still says which; the request asks for the shared colour.
- [An empty assembly that inherits no colour keeps its group neutral] → Decision 1; no occurrence changes a count on the Enigma I.
- [Spellings of one colour count as two] → Decision 1; none on the Enigma I.
- [Group chips are as stale as leaf chips under a pose] → Decision 4; consistent with the leaf rows, recorded as W1.
- [One extra O(N) pass per expand or collapse] → Decision 5; same order as the notification's own `reconcileLocal`.

## Open Questions

- Whether the pilot wants a sentence in `packages/machinome/docs/howto/browser-viewer.rst` ("Inspect the assembly") saying what a row's colour means. No page states the rule today, before or after, so the change adds none.
- Findings W1 (chips do not follow a pose) and W2 (`model` is false for a flexible part) are the pilot's to triage.
