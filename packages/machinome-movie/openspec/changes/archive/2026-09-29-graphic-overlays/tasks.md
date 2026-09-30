## 0. Preconditions

- [x] 0.1 Confirm the existing 29 September ratification under the pilot's
  delegation still covers this proposal: the ring and its geometry (D2), a callout as an arrow with text
  (D1), the `enter`/`leave` spelling and defaults (D3), the time functions
  (D4), the refusals (D7), the pixel proofs (D8) and what is left out (D9).
  `stills-and-clips` already adopted the shared `enter`/`leave` spelling.
- [x] 0.2 `keyframes-and-easing` and `shot-transitions` are implemented and
  archived on branch `film-motion`; this change is applied before
  `text-animation` and `stills-and-clips`. Record the base commit in
  `evidence.md`, and the name of the pixel-comparison helper that
  `shot-transitions` added (reuse it; do not add a second).

## 1. Red tests (written before any implementation; record each failure)

- [x] 1.1 `test/graphic-overlays.test.mjs` (new, Node only). Red before 2.1–2.2.
  - A 0.4 fixture (the `annotated()` shape of `test/annotations.test.mjs`,
    declared 0.4, `output.fps` 30) with a ring on a path, a ring on a two-path
    layer, an arrow with `enter: {kind: draw, duration: 0.8, ease: out}` and a
    label with `enter: {kind: fade, duration: 0.5}` and
    `leave: {kind: fade, duration: 0.4}` validates.
  - `frameAt` emits the ring as `{index, kind: 'ring', target: {paths}, padding:
    0.01, safeInset}` (default padding explicit; the layer resolved to both
    paths), and an explicit `padding: 0.02` as given.
  - `opacity` and `drawn`, with `assert.equal`: the label's `opacity` is exactly
    0 at `from`, `ease('smooth', 0.5)` at the entrance midpoint, exactly 1 at
    `from + 0.5` and at `to − 0.4`, `1 − ease('smooth', 0.5)` at the exit's
    midpoint; its `drawn` is 1 throughout. The arrow's `drawn` is exactly 0 at
    `from`, `ease('out', 0.5)` (0.875) at the midpoint and exactly 1 from
    `from + 0.8`; its `opacity` is 1 throughout. Each of the five easing names on
    an entrance gives `ease(name, u)` at `u = 0.25`.
  - A cue without `enter`, `leave` or `padding`, in 0.4, is deep-equal to the same
    cue in 0.3 (no `opacity`, no `drawn`).
  - With a `shot-transitions` dissolve into the next shot: a cue running to its
    shot's end with a `leave` is absent from the continued outgoing frame (the
    outgoing frame `shot-transitions` attaches to the incoming frame); the
    same cue without `leave` is present with no `opacity` field, and with an
    `enter` present at `opacity` 1 and `drawn` 1.
  - Refusals, each matching its message and the shot id: `kind: callout`;
    `kind: ring` with `point`, with `text`, with `place`, with `offset`;
    `padding: -0.1`, `padding: 0.3`, `padding` on an arrow and on a label;
    `enter: fade` (not a mapping); `enter: {kind: fade, durration: 1}`
    (`Unknown entrance field: durration`); `leave: {kind: fade, duration: 0.4,
    eas: in}` (`Unknown exit field: eas`); `enter.kind: scale`; `leave.kind: draw`;
    `enter: {kind: draw}` on a label; `ease: bounce` (the vocabulary's message);
    a duration of `1/60` at 30 fps; an entrance longer than the cue; an entrance
    and exit exceeding the cue (the overlap message with both durations); a ring
    on a part inside a hidden layer (`Annotated part is hidden`).
  - In a 0.3 episode each of `kind: ring`, `padding`, `enter`, `leave` is refused
    with `Rings, entrances and exits need format machinome-video-draft/0.4: shot
    pawls`; in 0.2, the existing `Annotations need format ... 0.3` message.
  - `requiredViewerApi` of the 0.4 fixture is `{api: 28, reasons:
    ['annotations (shot pawls)']}`, unchanged by rings and entrances.
- [x] 1.2 Pins, green by design before and after (record green on the base):
  `test/annotations.test.mjs` passes unchanged; the whole `frameAt` objects of the
  0.3 annotated fixture at 0.25, 1 and 1.5 s, and of the same fixture declared 0.4
  (whatever frame-level keys the earlier 0.4 cycles added), are pinned literally.
- [x] 1.3 `test/render.test.mjs` (real browser, the API 28 viewer double).
  Red before 2.3–2.4. Add double options, off by default so existing cases are
  unchanged: `rectSize: [w, h]` for the part's on-screen rectangle.
  - A 0.4 episode with a ring on `pawl` (0 to 2 s): preview passes with exact
    replay; at two instants the reported ring's centre is the rect's centre, both
    differ, and every rect corner satisfies `((x−cx)/rx)² + ((y−cy)/ry)² < 1`;
    `rx = √2·(w/2 + P)`, `ry = √2·(h/2 + P)` within 1e-6 with `P = 0.01·Ws`; in a
    3×3 neighbourhood of the ring's rightmost point `(cx + rx, cy)` some pixel is
    within 24 levels of the accent.
  - The same ring with `enter: {kind: draw, duration: 1, ease: linear}`: at 0.5 s
    the report gives `drawn` 0.5 and the `inside` and `outside` points; the
    `inside` neighbourhood has an accent pixel (within 24 levels) and every pixel
    of the `outside` neighbourhood is the double's flat canvas colour (within 2
    levels); `inside` lies right of `cx` and `outside` left of it (clockwise from
    the top). Preview's `entranceChecks` record the draw midpoint, start and end
    as passed.
  - An arrow with text and `enter: {kind: fade, duration: 1, ease: linear}` and a
    label with `leave: {kind: fade, duration: 1}`: preview passes and
    `entranceChecks` record the fade midpoints with `largestDifference <= 2` and
    `vacuous: false`, the entrance start equal to "without" and the entrance end
    and exit start equal to "full". Include overlapping cues so the full and
    without captures hold the other cue in its authored state. A cue whose
    `enter.duration` equals its `to − from` records `enter-end` skipped with
    `cue ends at this exclusive boundary`, while its start and midpoint are
    checked; no capture at `to` claims a visible mark.
  - Refusals: a ring whose double rect is wider than the stage
    (`Ring target is not wholly on screen: pawls #0 (ring)`); a ring with
    `padding: 0.25` whose ellipse leaves the 640×360 frame (`Ring leaves the
    frame: pawls #0 (ring)`); a double whose rect goes null mid-cue, with a ring,
    (`Annotation target is not on screen`).
  - The proofs' failure paths, without test-only code in `film.js`: the fade
    and draw-on comparisons are functions of decoded images, unit-tested (Node)
    on small synthetic images: a composed image 9 levels off the predicted blend
    is refused with `/fade does not blend as its easing predicts/` naming the
    shot, annotation and time; an `outside` neighbourhood that differs from
    "without" is refused as a draw-on showing the rest of its stroke; an
    `inside` neighbourhood equal to "without" is refused as showing none of it;
    identical "full" and "without" images are recorded `vacuous: true`.

## 2. Implementation

- [x] 2.1 `src/episode.mjs`: in 0.4, `ring` and its fields, `padding`,
  `enter`/`leave` with their closed lists, kinds, durations and easing, the
  overlap rule (D2, D3, D7); in 0.3 the format message for the new fields; the
  annotation field list extended (D10). Every existing message unchanged.
- [x] 2.2 `src/timeline.mjs`: ring cues with explicit padding; `opacity` and
  `drawn` through `ease` for cues with `enter` or `leave` (D4, D5); no
  continuation of a cue with `leave` past its `to` (D5). Cues without the new
  fields emitted exactly as before.
- [x] 2.3 `src/film.js`: ring path, dash and clip reveals, the same-instant
  opaque full/absent subset captures and weighted raster composition for
  animated fades, and the report fields (D6); cues without the new fields
  drawn by the unchanged code.
- [x] 2.4 `src/render.mjs`: the two ring refusals in `pose` (D7); preview's
  entrance and exit samples, the pixel proofs with the shared comparison helper,
  including a skipped `enter-end` at the cue's exclusive `to`, kept failure
  images and `entranceChecks` (D8); any new frame-path module in the render
  identity (D10).
- [x] 2.5 `docs/FORMAT.md`: "Pointing at parts" gains the ring (target, geometry,
  padding, look, the D2 example) and the sentence "a callout is an arrow with
  text"; a new section "Entrances and exits" (the fields, fade and draw-on per
  kind, the D3 example, what an entrance never changes, the continuation rule
  into a transition, the refusals, the preview proofs); "Format 0.4" lists the
  annotation fields added and the 0.3 refusal. `README.md`: the `preview` bullet
  names the entrance and exit proofs and the ring refusals.
- [x] 2.6 `npm test` green; record the red runs of 1.1 and 1.3, the green pins
  of 1.2 before and after, and the green run in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [x] 3.1 In the Leonardo project, as an untracked demo episode (nothing
  committed there), `videos/demo-graphic-overlays/` in format 0.4 on the sawmill
  export: the restaged *Revolutions* `pawls` shot of D2 (two rings, draw-on and
  fade, the two `top` captions kept); the restaged `name-the-pawls` shot of D3
  (arrow drawn on, label faded in and out); and a short `two-rope-reduction`
  shot on the `rope-wide` to `reduction` camera move, with rings on layers
  holding the export's `Large-radius rope reserve` and `Central small-radius
  take-up` in turn and labels "Rope 1" and "Rope 2" fading in.
- [x] 3.2 `check`, then `preview` with the Viewer API 28 bundle: record the
  `entranceChecks`, each ring's geometry at two instants of a moving pawl and
  during the camera move, the exact replay result and the stills.
- [x] 3.3 With one viewer bundle, `demo-annotate-a-part` and
  `demo-feed-mechanism` (0.3) pass `check`, and their preview stills before (base
  commit) and after this change are byte-identical. One browser at a time.
- [x] 3.4 The orchestrating agent renders a short silent clip of the demo at
  full frame rate (`--width 960 --fps 30 --silent`) so draw-ons and fades can
  be judged in motion; record its hash.

## 4. Delegated film review and archive gate

- [x] 4.1 After implementation tests pass, the orchestrating agent performs an
  adversarial review of the result against this plan and the rendered pixels,
  resolving findings before archival. Review the ellipse through the grown
  rectangle, default padding, stroke width, draw-on and fade pacing, and whether
  a ring breathing with a turning part reads clearly. Automated checks prove
  geometry, blends, reveals and reproducibility; record visual findings from
  inspected video frames separately, without claiming the pilot reviewed them.
- [x] 4.2 The orchestrating agent inspects the feature demonstration video from
  Leonardo `videos/demo-graphic-overlays/` with vision,
  records its path, hash and review findings, then syncs and archives this change.
  A proposed arrow restyle or adoption by *Revolutions* is a separate pilot
  decision, not a completion task in this cycle. Publication and pushing remain
  outside this campaign.
