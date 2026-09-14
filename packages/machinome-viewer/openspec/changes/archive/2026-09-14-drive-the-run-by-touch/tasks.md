## 0. Before anything else

- [x] 0.1 Confirm the base: this worktree is `drive-the-run-by-touch` off
      viewer main `644b504` (`openspec: archive ship-the-inspector-layout;
      accept ADR-051 and ADR-052`), package `0.2.0` unreleased, declared
      API version 11. Do not start on a branch that lacks
      `ship-the-inspector-layout`.
- [x] 0.2 Record the baseline, measured on this base and pasted into
      evidence: `npm test` in `solid_node_viewer/widget` → **642 passed,
      34 files**; `npm run typecheck` clean; `npm run build` writes
      `dist/solid-widget.js`; the Python suite with the workspace venv
      (`PYTHONPATH=<worktree> .venv/bin/python -m pytest`) → **96 passed**,
      naming anything it skips. The evidence lives in
      `openspec/changes/drive-the-run-by-touch/evidence.md`, in the house
      style of the archived running cycles: every red pasted verbatim,
      counts, screenshots named.
- [x] 0.3 Read, and keep open: solid-node's archived
      `declare-controls-on-parts` `specs/export/spec.md` (the authority on
      every field of the table) and `docs/adrs/NODE/ADR-112-…` §3 (the
      consumer rule this cycle's geometry rests on). Nothing in this
      repository restates them; where this cycle and that spec disagree,
      that spec is right.

## 1. The fixture: a real document with real controls

- [x] 1.1 Commit `tests/fixtures/touched/viewer.json` — the framework's own
      published build of the Pascaline module's classes with a `controls`
      table, **verbatim**, 31,972 bytes, version 5, root `Touched`, four
      instructions, three inputs, six controls (three `button` on
      `Add one`/`Add ten`/`Add hundred`, three `turn` with `per_unit`
      `-36.0`, each `joint` `[<column>, "input"]`, `coordinate`
      `<column>.input.turn`, `axis` `[1, 0, 0]`, `origin` `[0, 0, 0]`).
      Nothing here edits it and nothing here regenerates it.
- [x] 1.2 Commit the fifteen stand-in meshes it names, each a copy of the
      684-byte unit cube `tests/fixtures/pascaline/vendor/…` already uses
      (three of the fifteen paths differ from that fixture's, so this one
      carries its own `vendor/` tree). Write
      `tests/fixtures/touched/README.md` saying exactly what is verbatim
      and what is a stand-in, in the voice of the `pascaline` fixture's.
- [x] 1.3 Add `TOUCHED = FIXTURES / 'touched'` and a staging helper beside
      `published_run` in `tests/support.py`. Assert in a plain test that
      every model path in the document resolves in the fixture directory,
      so a missing mesh fails as a missing mesh rather than as a blank
      canvas.

## 2. Reading the table, refused by name (design D1–D3)

- [x] 2.1 Red: `src/partControls.test.ts` in plain node — `readControls`
      over hand-written documents. One failing case per refusal in design
      D1: a table that is not an object; an entry that is not an object; a
      `kind` that is neither; a `part` or `joint` that is not a list of
      strings; a `part` or `joint` naming no node or an ambiguous one; a
      `joint` that is not an ancestor-or-self of its `part`; an
      `instruction`, `input` or `coordinate` absent from the table it must
      belong to (each refusal naming what IS declared); a `per_unit`
      missing, non-finite or zero; an `axis`/`origin` that is not three
      finite numbers; a zero-length `axis`; a joint whose leading
      operations are not zero or more translations and then a bare
      rotation over the entry's `coordinate` (with, as ACCEPTING cases,
      both shapes the producer publishes: the rotation alone, and
      translate / rotate / translate-back with `origin` equal to the
      negated leading translation); two controls of one kind on one part;
      a table on a document with no program. Assert
      the MESSAGE names the document, the control key and the offending
      value — a refusal nobody can act on is not a refusal.
- [x] 2.2 Red: the accepting cases — a document with no `controls` key
      yields `[]`; the committed `touched` fixture yields exactly six
      entries in the document's own key order with every field carried
      through unchanged.
- [x] 2.3 Green: `ManifestControl` and `Manifest.controls` in
      `src/types.ts`; `readControls(document, sourceUrl)` in the new
      `src/partControls.ts`, importing neither the DOM nor three.js.
- [x] 2.4 Red then green: `src/document.test.ts` — `assertRenderable`
      refuses each of 2.1's documents before anything is rendered, and
      returns the parsed controls on `LoadedDocument` for a good one;
      every existing document test passes unedited.

## 3. The gesture, decided as data (design D10–D11)

- [x] 3.1 Red: `src/partControls.test.ts` — the geometry, as pure vector
      math over plain tuples: `worldLine(matrixWorld, axis, origin)` giving
      the world origin and a unit axis, pinned on both placement shapes
      (a rotation alone, and translate / rotate / translate-back with a
      non-zero `origin`) at two different joint angles, so the line is
      shown not to move under the joint's own rotation; `intersectPlane` returning null for
      a ray parallel to the plane; `sweepAngle` giving the signed angle
      about the axis between two directions, right-handed, in degrees;
      unwrapping across more than half a turn by accumulating per-move
      deltas.
- [x] 3.2 Red: the mode choice — in-plane when
      `|ray.direction · axis| ≥ EDGE_ON` (0.15), screen otherwise, and
      screen when the pointerdown point lands within `MIN_RADIUS` of the
      axis; the choice is made once from the pointerdown ray and does not
      change for the gesture. Pin the screen fallback's sign against an
      axis pointing toward and away from the camera, and pin the
      documented `+1` convention exactly edge-on.
- [x] 3.3 Red: the planner — `quantum = |amount × per_unit|`; a quantum is
      issued only when `|sweep − origin| ≥ quantum`; the request's sign is
      `sign((sweep − origin) / per_unit)`, so a sweep of −36° on
      `per_unit = −36` asks for `+1`; **at most one request in flight**,
      the next issued only when the previous retires; the owed count
      derived from `sweep − origin` and never queued, so forward-then-back
      nets out; `completed` advances `origin` by one quantum and asks
      again; `blocked`, `refused` and `cancelled` leave `origin` where it
      is and stall that direction until `|sweep − origin| < quantum`
      again; a stalled direction issues nothing however long the gesture
      is held.
- [x] 3.4 Green: the planner and the geometry in `src/partControls.ts`.
      Nothing in the module touches the DOM, three.js or the run.

## 4. The pick and the affordance (design D4–D7)

- [x] 4.1 Green: `viewer.ts` builds a `Map<THREE.Mesh, LoadedControl[]>`
      from `tree.requirePath(control.part)` after every `replaceTree`,
      `manifestChanged` and `artifactChanged`. `tree.ts` is not modified.
- [x] 4.2 Red then green: the visibility filter, as a pure predicate
      testable in node — a hit is kept only when the mesh and every
      ancestor up to the scene are `visible`. Pin it against the fact that
      this three.js version's raycaster does not consult `visible` at all,
      so a test that removed the filter would pass a hidden part.
- [x] 4.3 Green: the pick — cast against the whole tree, keep the nearest
      VISIBLE hit, act only when that mesh is in the map. A part in front
      of a control is not pressed through.
- [x] 4.4 Green: the hover affordance — pointer cursor on the canvas, the
      canvas `title` set to the display names of every control naming the
      hovered part, and an emissive lift on each of the part's meshes whose
      material carries one, restored on unhover. Cleared on unhover, on
      gesture end, on dispose and before any reconcile. Raycast at most
      once per animation frame, and install none of this when the document
      declares no control or `partControls` is `'none'`.

## 5. The press and the turn on screen (design D8, D9, D12, D13)

- [x] 5.1 Green: the gesture's entry — a capture-phase `pointerdown` on the
      CONTAINER (an ancestor of the canvas, so it runs before
      `OrbitControls`' own listener whatever registration order would
      decide) that, on a control hit, stops propagation, sets
      `controls.enabled = false`, captures the pointer on the canvas, and
      opens the gesture.
- [x] 5.2 Green: press versus drag — a press until the pointer has moved
      more than `PRESS_SLOP` (4 CSS px), a drag thereafter for the rest of
      the gesture; a `pointerup` while still a press issues
      `run().trigger(instruction)` through the existing `request(...)`; a
      press on a part carrying only a turn does nothing.
- [x] 5.3 Green: `request(key, unit, issue, at?)` gains the optional client
      point and, when given, writes a transient label there —
      `formatOutcome`'s own words, `role="status"`, replaced by the next
      report, removed after a few seconds and on dispose. The panel's
      control for the same key still reports, through the same call.
- [x] 5.4 Green: the drag issues the planner's requests through the same
      `request(...)`, keyed by the input id, so the panel's input row
      reports what the gesture got.
- [x] 5.5 Red then green: the five release paths — `pointerup`,
      `pointercancel`, `lostpointercapture`, the window's `blur`, a
      `visibilitychange` to hidden — each ending the gesture, restoring
      `controls.enabled`, releasing the capture and clearing the
      affordance. A `move` already in flight is left to retire and report;
      the gesture does not cancel it.
- [x] 5.6 Red then green: DOM tests in jsdom for everything jsdom can
      reach — the label's text and lifetime, the cursor and title, the
      release paths and the `controls.enabled` restoration — through the
      seam pattern `inspector.test.ts` already uses for `mount`.

## 6. The mount surface (design D14–D16)

- [x] 6.1 Red then green: `src/options.test.ts` — `partControls` defaults
      to `'inline'`, accepts `'none'`, is independent of `driverControls`
      in all four combinations, and `showsPartControls(mode, hasControls)`
      is false for a document that declares none.
- [x] 6.2 Red then green: `controls()` on the handle — the declaration
      fields carried through; `rect` and `point` in viewport CSS pixels;
      `point` found by raycasting the rect centre and then a bounded grid
      inside it under the same nearest-visible-hit rule, so the point
      reported is a point a press actually reaches; `null` for both when
      the part is hidden, off screen or reached nowhere; `[]` for a
      document with no table; the full listing even when `partControls` is
      `'none'`.
- [x] 6.3 Green: API version 11 → 12 in `package.json`; update
      `src/version.test.ts`'s narrative and its `toBe(12)`;
      `solidNodeDocumentVersions` is unchanged and a test asserts it.
- [x] 6.4 Green: `tests/test_bundle.py` and `tests/test_widget_e2e.py`
      expect 12; `tests/test_running_document.py`'s existing assertion
      expects 12. No other Python test changes.
- [x] 6.5 Green: `capture.py`'s `mount_options` adds
      `"partControls": "none"`, with the one-line reason. `tests/test_capture.py`
      asserts the option is in the mount page; no capture requirement moves.

## 7. The acceptance: a maker touches the Pascaline (design D18)

- [x] 7.1 Red: a new Playwright class in `tests/test_running_document.py`
      on the `touched` fixture, mounted with default options — assert the
      handle lists six controls with the declared names, kinds, parts,
      instructions, inputs and `per_unit` `-36.0`, and that each reports a
      rectangle and a point.
- [x] 7.2 Red: **a press.** Move the real mouse over the units dial's
      reported point and assert the canvas cursor is `pointer` and the
      title names the control; press there; wait for the panel's `Add one`
      button to stop indicating a run; assert the outcome label beside the
      pointer and the panel's button both read completed, the
      `units_entry` readout reads one digit, and the run's
      `units.drum.turn` has moved.
- [x] 7.3 Red: **a blocked drag.** Drag the units dial in the direction the
      ratchet forbids, through more than one quantum, and assert: the
      report reads blocked, `units_entry` is unchanged, `units.drum.turn`
      is unchanged, and holding the drag there issues no further request
      (assert the run's tick advances while no new outcome arrives). The
      document's own span makes this exact — `units.input.turn`'s high
      bound is `36·ceil(turn/36)`, which at the rest bank is where the
      coordinate already stands.
- [x] 7.4 Red: **a forward drag.** Drag one quantum the other way and
      assert one digit admitted, one request issued, and the drum turned.
- [x] 7.5 Red: a part the table does not name — press and drag the lid and
      assert the camera moved and no request reached the run.
- [x] 7.6 Screenshots: the hover affordance, mid-press, after the forward
      drag, and the blocked report. Inspected by eye and recorded in
      evidence. Pixels are evidence; a green suite is not an inspection.

## 8. The whole suite, the docs and the records

- [x] 8.1 `npm run typecheck`, `npm test`, `npm run build` and the Python
      suite. Record final counts against 0.2's baseline (642 widget tests,
      96 Python tests) and confirm every pre-existing test passes unedited
      except the API-version assertions this change deliberately moved.
- [x] 8.2 `README.md`: the opening list says a maker can press and turn the
      part itself on a document that declares controls; the `partControls`
      option beside `driverControls`; `controls()` beside `run()`; and the
      versions table gains `0.2.0 | 12 | 1, 2, 3, 4, 5` in place of 11.
- [x] 8.3 `CHANGELOG.md`: the same unreleased `0.2.0` section gains the
      part controls — the declaration it reads, the press, the quantised
      turn, the blocked-travel rule, the refusal surface, `controls()`,
      `partControls`, and the API version. Say plainly what is not in it:
      no `Slide`, no dialling by position, no keyboard gesture.
- [x] 8.4 Write the ADR design §"The ADR to extract" names — the next
      number after ADR-052, in `docs/adrs/EXPORT/` — and add it to
      `docs/adrs/README.md`'s index in order, with its status.
- [x] 8.5 Record, in `evidence.md`, what the implementation learned about
      each of design §Open Questions and §Reviewer decisions.
- [x] 8.6 `openspec validate drive-the-run-by-touch --strict` passes.
