## Why

The pilot's first wish for the next film (roadmap item 7) is graphics on the
picture: rings, boxes, lines and callouts, placed freely, with animated
entrances. Today a shot can point at a part with an `arrow` or name it with a
`label` (`annotate-a-part`), and both appear in one frame and vanish in one
frame. The Leonardo episodes ask for two things beyond that, and for no more:

- **A mark that singles out a part without words.** *Revolutions*
  (`projects/Leonardo/videos/machinome-revolutions`) shot `pawls` (39.5–49.5 s)
  says "Pull · advance one tooth" and then "Return · hold that progress" in a
  `top` caption while the two pawls the words are about move somewhere below
  it; nothing on screen says which pawl each caption means. The didactic draft
  (`machinome-revolutions-v2`) asks its `two-rope-reduction` shot to
  "Distinguish rope unwinding from its large section and the SECOND rope winding
  onto its thin centre", and its `whole-machine` shot to "Show the opening kerf
  as a visual illustration". The same drafts restrain words: "no caption repeats
  speech" (`ratchet-and-pawls`), "No mechanical lesson labels" (*Revolutions*
  `revolution`), "Label rope 1 / rope 2 if helpful". Each of those targets is a
  part of the export (`Driving pawl`, `Holding pawl`, `Large-radius rope reserve`,
  `Central small-radius take-up`, `Uncut wood at the kerf`), and the camera moves
  in two of the shots. What they want is a ring drawn around a part, following
  it, carrying no text.
- **Marks that arrive and leave instead of popping.** The campaign demo
  `demo-feed-mechanism` shot `name-the-pawls` makes its arrow appear at 0.2 s
  and its label at 1.9 s in a single frame each; the restaged `pawls` shot needs
  the driving pawl's ring to go as the holding pawl's ring comes. A fade, and a
  stroke that draws itself on, are the two arrivals these shots need; a fade is
  the one departure.

## What Changes

- In format `machinome-video-draft/0.4` (opened by `keyframes-and-easing`) the
  existing `annotations` list gains one kind, `ring`: an ellipse in
  `style.accent` drawn around a part's on-screen rectangle (the same rectangle,
  and the same union for a multi-path layer, that places an arrow's tip), with
  an optional `padding`, following the part every frame.
- A callout (words on a plate with a leader to what they name) is the existing
  `arrow` with `text`; FORMAT.md says so, and no second spelling is added.
- Every annotation kind, the existing arrow and label included, may declare
  `enter` and `leave`, each `{kind, duration, ease?}`: `enter` is a `fade` or a
  stroke `draw`-on, `leave` is a `fade`. `ease` is a name of the campaign
  vocabulary (`src/easing.mjs`, default `smooth`). Both are a pure function of
  the cue's local time. A draw-on reveals a ring around its ellipse and an arrow
  from its words to its tip; a label has no stroke, and a draw-on there is
  refused. An entrance or exit never moves the mark: where it ends up is where
  it is drawn without one.
- `check` refuses, naming the shot and annotation: an unknown kind, entrance or
  exit kind or easing; a ring aimed at a `point` or given `text`, `place` or
  `offset`; a `padding` out of range or on another kind; a draw-on on a label;
  an entrance or exit shorter than two frames or longer than the cue, or the two
  overlapping; a ring on a part the shot hides (the existing rule); any of the
  new fields in a 0.2 or 0.3 episode. At every posed frame, `preview` and
  `render` refuse a ring whose part is not wholly on the model stage, or whose
  drawn ring leaves the frame, as an arrow whose target leaves the stage is
  refused today.
- `preview` samples every entrance and exit at its first frame, midpoint and
  end, and proves in pixels that a fade's midpoint is the blend its easing
  predicts, that a draw-on's midpoint shows part of the stroke and not the
  rest, that an entrance starts from nothing, and that an entrance's end and an
  exit's start are the mark drawn plainly. The exact pixel-replay check is
  unchanged.
- 0.2 and 0.3 episodes, and 0.4 episodes that use none of the new fields, keep
  their exact frames and pixels. No new Viewer API: rings use the
  `partOnScreen` that annotations already need (API 28).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `part-annotations`: gains the `ring` kind, entrances and exits, and their
  refusals, in format 0.4. Its existing requirements stay true as written:
  unknown kinds are still refused, and arrows and labels without the new fields
  are drawn as before.

## Impact

`src/episode.mjs` (0.4 annotation validation: `ring`, `padding`, `enter`,
`leave`, the format refusal in 0.2/0.3), `src/timeline.mjs` (ring cues, and
opacity and drawn fraction for cues with an entrance or exit, through `ease`),
`src/film.js` (ring drawing, per-annotation opacity, draw-on reveals, geometry
in the frame report), `src/render.mjs` (per-frame ring refusals, preview
entrance samples and pixel proofs), tests, `docs/FORMAT.md`, `README.md`. It
uses `ease` from `src/easing.mjs` (`keyframes-and-easing`) and the pixel
comparison that `shot-transitions` introduces for its proofs, and redefines
neither. No viewer, simulation or CAD change. The consuming demo episode is
authored untracked in the Leonardo project; whether *Revolutions* or its draft
adopts rings or entrances is the pilot's decision.

## Non-goals

Left out because no episode asks for them (design D9 writes down what each would
mean, for the day a shot does): `box`, `line`, shapes at a fixed place on the
screen, rings on a world `point`, a `scale` entrance, draw-off exits, per-mark
colours or stroke widths, entrance presets in `production.yaml`. Also out:
fades of `top`/`lower-third`/`center` overlays and titles (`text-animation`),
fades of highlights (a viewer matter), transitions (`shot-transitions`),
pictures (`stills-and-clips`), and any restyle of the existing arrow (design
Open Questions). No publication.
