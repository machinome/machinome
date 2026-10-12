## MODIFIED Requirements

### Requirement: `check` measures a document's set layouts

When a movie document shows a picture or comes in by a reframe, `check`
SHALL, after bundling the stage and before reading any take, measure the
layout of every set kind its shots use, once per kind, at the output size,
on the page the renderer serves, with the movie's bundle and no viewer
mounted: for each slot, its box, the box a picture element placed there
gets, and whether its box changes when the set's slots hold content. It
SHALL print one line per measured set giving each slot's box, or that the
slot is sized by what it holds. For each picture shown in a slot whose box
does not change with content, `check` SHALL print its peak enlargement and
its allowance, and MUST refuse, before any take is read, a raster picture
whose peak enlargement (the fit's scale in the measured box times the
largest zoom of its view keys) exceeds its allowance, naming the picture,
the shot, the enlargement, the source size, the slot's box and set, and the
allowance. For each reframe, `check` SHALL print the views it moves with
their outgoing and incoming slots' boxes, and MUST refuse, before any take
is read, a reframe whose outgoing or incoming slot is sized by what it
holds, naming the shot, the view, the set and the slot. Once the takes
resolve the times, `check` MUST refuse a still's view that, at any output
frame of its cue, shows the background beside a picture that overfills the
measured box or cuts off one that underfills it, naming the shot, the video
time, the element and the picture. A picture in a slot sized by what it
holds SHALL be reported as checked at preview and render, which judge it
against the box the stage reports. `check` MUST NOT open a browser for a
movie document that shows no picture and has no reframe, or for a YAML
episode, and MUST NOT need a viewer bundle to measure. Every browser
session of `preview` and `render` SHALL measure, on its own page before its
first frame, the slot boxes its reframes move views between.

#### Scenario: The tour's plate
- **WHEN** `check` runs on the fixture tour, whose still of 864×576 pixels
  is shown with `contain` in the `plate` slot of `Playbill` and keyed to a
  zoom of 1.4, in a 1280×720 film
- **THEN** it prints `Playbill`'s layout, with `plate` 870.4×576 and
  `headline` sized by what it holds, and `peak 1.40×; allowance 1.5×` for the
  still.

#### Scenario: The tour's reframe
- **WHEN** `check` runs on the fixture tour, whose `question` comes in by a
  reframe moving `opening.wide` from `Playbill`'s `stage` to
  `PlaybillSplit`'s `right`
- **THEN** it prints one `Reframe` line naming `question`, `opening.wide`
  and both slots with their measured boxes.

#### Scenario: A lowered allowance, before speech
- **WHEN** the tour's still is given an allowance of 1.2 and no take has
  been cached
- **THEN** `check` refuses it as enlarged 1.40× in shot `still`, naming the
  870.4×576 box of slot `plate` of set `playbill` and the allowance 1.2, and
  does not ask for the takes.

#### Scenario: A view that leaves the picture
- **WHEN** the tour's still's first view key is centred at (0.1, 0.5) at
  zoom 1
- **THEN** `check` refuses it naming the shot `still`, the time 16.67 s,
  the element `tip.plate` and the still `plate`.

#### Scenario: No picture, no browser
- **WHEN** `check` runs on a movie document whose shots show no picture and
  have no reframe
- **THEN** it launches no browser and prints no layout.
