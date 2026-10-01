## ADDED Requirements

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
