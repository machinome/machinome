## 0. Preconditions

- [x] 0.1 The pilot ratifies this proposal: the three fields and their place
  (D1), the transition inside the incoming shot (D2), the continued outgoing
  shot (D3), the chrome staying above the transition (D4), the background as
  the default fade colour (D5), the refusals (D7) and the preview proofs (D8),
  settling or deferring each open question.
- [x] 0.2 `keyframes-and-easing` is implemented on `film-motion`: format
  `machinome-video-draft/0.4` is accepted, and `src/easing.mjs` exports the
  vocabulary `linear`, `smooth`, `in`, `out`, `in-out` with each easing
  mapping 0 to 0 and 1 to 1. Record its commit. The field is `ease`; the end rate under eased
  model segments and the 0.4 frame shape are settled in design.md's
  Ratification section.

## 1. Red tests (fail before any implementation; record the failures)

- [x] 1.1 `test/transitions.test.mjs` (new, Node only), on a 0.4 fixture of
  five shots with `fadeIn`, a `dissolve` (`ease: linear`), a `fade`, a `slide`,
  a `wipe` and `fadeOut`, the first shot a code shot and one shot carrying an
  overlay and a highlight that run to its end and one that ends earlier:
  - the fixture passes `validateEpisode`;
  - `frameAt` gives `transition: null` outside transitions; inside the
    dissolve at a quarter of it, progress 0.25; with the default easing, the
    smoothstep value; the frame's own fields deep-equal the same instant with
    no transition declared (the incoming timeline is untouched);
  - the outgoing frame is the outgoing shot's: model time `to + r·u` over the
    export duration, camera at its last key, the cues that run to its end
    present and the earlier one absent, code complete with no cursor, its own
    hidden paths; a held outgoing shot keeps its model time;
  - the fade's plate rises to 1 at its midpoint over the outgoing picture and
    falls over the incoming one; `fadeIn` is 1 at time 0 and 0 at its end;
    `fadeOut` is 0 at its start and exactly 1 at `end − 1/fps`;
  - `direction` defaults to `left`; `right` is carried through;
  - each D7 refusal throws naming the shot: the fields in 0.3 and in 0.2,
    unknown field, kind `cut`, direction `up`, `ease: bounce`, direction on a
    dissolve, colour on a wipe, colour `black`, a defaulted colour with
    `style.background: cream`, a one-frame duration, a transition longer than
    the outgoing and than the incoming shot, `transition` on the first shot,
    `fadeIn` on the second, `fadeOut` before the last, an incoming transition
    and a fade-out overlapping in one shot, and an outgoing model that would
    pass `expectedDurationSeconds` (while the same transition after a held
    shot at the export's end is accepted);
  - `requiredViewerApi` is unchanged by adding transitions.
- [x] 1.2 The existing "0.2 episodes are unchanged" and "constant up and field
  of view are unchanged" pins stay green untouched, and the 0.3 fixtures of
  `test/annotations.test.mjs`, `test/highlight.test.mjs` and
  `test/camera.test.mjs` still produce their pinned frames.
- [x] 1.3 `test/render.test.mjs`, a real-browser case: extend the viewer double
  with an option that paints its canvas a colour computed from model time, so
  the continued outgoing shot and the incoming one differ and continuation is
  visible. A 0.4 episode joining a code shot to a model shot by each kind in
  turn must pass `preview`, with the report's transition proofs present:
  dissolve largest difference at most 2 and the pictures differing; wipe and
  slide exact; `fadeIn`'s first frame and `fadeOut`'s last exactly the colour
  outside the masthead and rule; replay inside each transition exact. The
  outgoing canvas colour at a transition's midpoint equals the colour of the
  continued model time. `render` produces the expected frame count, and a
  transition frame rendered in a fresh session is byte-identical to the same
  frame from the full run. An outgoing arrow that runs to its shot's end on a
  double whose part vanishes after that end is refused with `/not on screen/`,
  the outgoing shot's id and a time past its end.

## 2. Implementation

- [x] 2.1 `src/episode.mjs`: validate `transition`, `fadeIn`, `fadeOut` (D1,
  D5, D7), accepted only in 0.4, with the continuation check against
  `model.expectedDurationSeconds`.
- [x] 2.2 `src/timeline.mjs`: factor the shot-local frame into one function
  used for the incoming frame and the continued outgoing frame (D3); add
  `transition` to 0.4 frames only (D4, D6), using `src/easing.mjs`.
- [x] 2.3 `src/film.html`, `src/film.js`: a transition layer above the stage,
  annotations, overlays and code panel and below the masthead and progress
  rule; picture-only mode for sub-captures; the plate, the clipped or
  translucent image and the offset images, rebuilt every frame, awaiting image
  decode.
- [x] 2.4 `src/render.mjs`: compose in `pose` from sub-poses of the same
  instant (D6), each through the existing checks; preview's stills and proofs
  (D8), keeping images on failure; the existing highlight and lens comparisons
  pose with the transition removed; `src/easing.mjs` and any new module in the
  frame identity.
- [x] 2.5 `docs/FORMAT.md`: in "Timing and rendering semantics", replace
  "Shot boundaries are hard cuts; no crossfade or automatic framing is implied"
  with the rule for 0.2/0.3 and a pointer to the new section; add a 0.4
  section "Joining shots" beside the other 0.4 sections with the D1 example,
  the placement (D2), the continuation rule (D3), each kind's drawing and
  direction (D4), the default colour (D5), the refusals (D7) and what preview
  proves (D8). `README.md`: in "Produce an episode", the `preview` bullet gains
  the transition stills and proofs, and the output note says transition frames
  cost two or three poses each.
- [x] 2.6 `npm test` green; record the red and green runs in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [x] 3.1 In the Leonardo project, beside the other campaign demos and never in
  this repository, author `videos/demo-shot-transitions` in format 0.4: the
  dark sequence's edit as the format allows it (moving whole sawmill, then the
  architecture source in the split code layout, then the closer moving
  mechanism), with `fadeIn` on the first shot, a `dissolve` into the source, a
  `fade` back to the machine, a `slide` and a `wipe` between two machine
  views, and `fadeOut` on the last shot. Whether it is committed there is the
  pilot's decision.
- [x] 3.2 `check`, then `preview` with the Viewer API 28 bundle: record each
  transition's proofs, the replay results and the stills; confirm the
  unchanged sawmill, *Revolutions* and 0.3 demo episodes still pass `check`
  and `preview`, and that a scratch copy of the demo declaring format 0.3 is
  refused by `check` rather than rendered with cuts.
- [x] 3.3 Render the demo, silent unless narration is commissioned; decode
  frames on both sides of and inside each transition and inspect them; record
  the MP4's hash in `evidence.md` and leave the video as the campaign's
  artifact.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The pilot judges each kind in motion on the demo, chooses which the
  *Revolutions* source edit should use, and settles the open questions
  (masthead under fades, default easing, continue or freeze). Automated proofs
  show the composition is exact and reproducible, not that it reads well.
- [ ] 4.2 Publication, pushing and final release renders need the pilot's
  explicit request; nothing here implies them.

Implementation note (29 September 2026): 0.1 was ratified by the orchestrating
agent as the campaign's review gate under the pilot's delegation (design.md,
"Ratification"); the pilot's own judgement of the kinds in motion is 4.1. 0.2:
`keyframes-and-easing` was implemented in `bc13655`. 3.1 was authored as the
ratification settles the demo (source and machine joined by `fade`, model
shots by dissolve, slide and wipe) as the untracked Leonardo episode
`videos/demo-shot-transitions/`; nothing was committed to Leonardo. 2.5's
README note gives the cost as one pose for a fade and two for a dissolve, wipe
or slide, because every transition frame is drawn from captures (evidence.md,
finding 2). The Revolutions and sawmill episodes fail `check` in place before
and after this change; 3.2 used the 0.3 demos and the re-pinned scratch copy of
the sawmill rehearsal; see evidence.md. The human review items remain open.
