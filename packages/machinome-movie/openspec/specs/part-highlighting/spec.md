# part-highlighting Specification

## Purpose
Lift named parts for a timed interval while the rest of the model is kept,
dimmed or ghosted, so a mechanism is seen inside its context instead of hiding it.
## Requirements
### Requirement: A named part stands out while the rest is kept, dimmed or ghosted

The author SHALL add timed highlights to a view: in an episode, `highlight`
cues of a shot, applied to the shot's view; in a movie document, `highlight`
actions on a view element the shot places, lasting from their cue's `at` to
its `until`. Each names the parts to lift (production layer names or assembly
paths), what happens to every other part of that view (`keep`, `dim` or
`ghost`, default `keep`) and optionally a tint colour (default the production
accent). While a highlight is active the audience SHALL see, in that view,
the named parts tinted and the others unchanged, dimmed, or ghosted: still
drawn, translucent, so parts behind them show through. A highlight belongs to
its view: another view of the same shot MUST be unaffected. Highlighting MUST
NOT change the model's pose, the camera, or which parts are hidden.

#### Scenario: See the pawls through the frame
- **WHEN** the *Revolutions* pawls shot highlights the driving pawl and ratchet
  with `others: ghost` instead of hiding the timber structure
- **THEN** the pawl and ratchet stand out in the accent tint while the frame
  around them remains visible as a translucent context.

#### Scenario: Cue ends or the shot cuts
- **WHEN** video time reaches a cue's end, or the next shot begins
- **THEN** every part's appearance is restored exactly as it was before the cue.

#### Scenario: The waterwheel lit on its word
- **WHEN** a cue of *Cut and Advance*'s `coupling` highlights the waterwheel on
  `mill` from the spoken "waterwheel" until the spoken "crankshaft", with
  `others: ghost`
- **THEN** the view in the split's right-hand box shows the waterwheel tinted
  and the rest ghosted over that interval, and the source panel beside it is
  unchanged.

### Requirement: Hidden layers keep their meaning

Parts a view hides (an episode shot's `hiddenLayers`, a view element's `hide`)
SHALL stay hidden during a highlight, whatever happens to the other parts.
Production MUST refuse a highlight naming a part its view hides.

#### Scenario: Ghosting does not reveal hidden parts
- **WHEN** a shot hides the water layer and ghosts all parts but the crank
- **THEN** the water stays hidden and only the visible parts are ghosted.

#### Scenario: Contradictory request
- **WHEN** a shot hides the feed layer and highlights the driving pawl
- **THEN** `check` refuses it, naming the shot.

### Requirement: Highlighted frames are reproducible

A highlighted frame MUST depend only on its video time and the episode. Seeking
in any order, or resuming a render, SHALL yield identical pixels, and returning
to an unhighlighted instant SHALL yield the pixels it had before any highlight.

#### Scenario: Revisit around a highlight
- **WHEN** preview poses an unhighlighted instant, a highlighted instant, and the
  unhighlighted instant again
- **THEN** both unhighlighted captures match exactly, and the highlight is
  visibly present in the highlighted capture.

### Requirement: Invalid highlights and older viewers are refused

`check`, `preview` and `render` MUST refuse, naming the shot: empty or unknown
parts, an assembly path the export does not contain, an unknown `others` value,
a colour that is not `#rrggbb`, times outside the shot, and overlapping
highlights of one view. Highlights SHALL require format
`machinome-video-draft/0.3` in an episode and Viewer API 28; an episode or
movie using them against an older viewer MUST be refused with the field, the
shot, the required and the declared API. Episodes without highlights keep
their viewer requirement, and a highlight changes only the frames on which it
is active: every other frame keeps the pixels it has without it.

#### Scenario: Bare path written as layers
- **WHEN** an author writes `parts: [Saw mechanism, Connecting rod]` without the
  inner list
- **THEN** `check` refuses two unknown layers rather than guessing a path.

#### Scenario: Highlighted episode, old viewer
- **WHEN** an episode with a highlight is rendered with a Viewer API 27 bundle
- **THEN** render refuses before capturing any frame and names Viewer API 28.

### Requirement: Preview lays out each highlight for a reviewer

For every highlight cue, `preview` SHALL keep the unlit and the lit capture
of the instant its proof compares (the cue's midpoint, posed without its
shot's transition) and SHALL write a difference image, the unlit frame in
grey with every pixel that differs in any channel marked in red, under
`preview/highlights/`, which holds only the current preview's images. The
difference SHALL mark where the named parts changed: for a highlight that
keeps the rest, against the lit capture; for one that dims or ghosts the
rest, against a capture of the same instant with the same highlight keeping
the rest, which `preview` SHALL keep too (`-parts-lit`) and the film never
draws. Each image SHALL be named by the shot, the cue and the parts the
highlight lights, and `-lit`, `-unlit`, `-parts-lit` or `-difference`. `preview/report.json` SHALL
list every highlight's images under each part it lights, a layer by its
name and an assembly path by its names joined with `/`, with the shot, the
cue, the element, the time, every assembly path lit, the number of pixels
that differ and the smallest box holding them; each highlight check SHALL
carry the same. `preview` SHALL print one line per highlight naming the
shot, the cue, the parts, the pixels changed with their box, and the
difference image. Whether the part lit is the part the author meant is the
reviewer's judgment: `preview` SHALL NOT take an expected region and SHALL
NOT refuse anything its highlight proof does not already refuse.

#### Scenario: The pinions beside the drum
- **WHEN** `preview` runs on *Addition*, whose shot `add-23` lights the
  stepped drum and the two input pinions beside it with the rest ghosted
- **THEN** `preview/highlights/` holds that highlight's lit, unlit, parts-lit
  and difference images, named by `add-23`, its cue and the three parts, the
  difference marking the drum and the pinions and not the ghosted rest, and
  the report lists them under `main_drive/stepped_drum` and under each
  pinion's path, with the pixels changed and their box.

#### Scenario: The wrong part, seen at once
- **WHEN** a highlight names the bevel tips at the top of the shafts where
  the author meant the input pinions
- **THEN** `preview` passes as it did, and the difference image listed under
  the bevel tips' path marks in red the pixels at the top of the shafts,
  where a reviewer sees the highlight landed.

#### Scenario: The double's highlight
- **WHEN** `preview` runs on an episode whose shot `pawls` highlights the
  layer `pawl` with the viewer double
- **THEN** the report lists under `pawl` the shot `pawls`, its images
  `highlight-0` lit, unlit, parts-lit (the highlight ghosts the rest) and
  difference, and a pixel count equal to the number of pixels in which the
  unlit and the parts-lit captures differ.

#### Scenario: Only this preview's images
- **WHEN** a highlight is removed from a film and `preview` runs again
- **THEN** `preview/highlights/` no longer holds its images.

