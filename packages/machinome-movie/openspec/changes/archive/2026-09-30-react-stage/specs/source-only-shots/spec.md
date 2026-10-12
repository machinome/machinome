## MODIFIED Requirements

### Requirement: A code shot may show source without a competing model view

In format `machinome-video-draft/0.4`, a shot with `code` SHALL accept `layout: source-only`, and SHALL be drawn in the shipped set `source-only`. Its own picture SHALL show the pinned source panel in the main picture area and no model: the shot places no view. The film SHALL retain its current episode style, masthead, series label, overlays, narration and external captions. Source text, syntax colour, typing cursor and measured identifier emphasis SHALL follow their existing rules; the source SHALL remain literal and safely escaped. Source-only presentation SHALL NOT change the shot's authored model time or camera, and SHALL NOT require a newer Viewer API than that shot otherwise requires.

#### Scenario: The current Leonardo drive line appears between moving model shots

- **WHEN** a format-0.4 film cuts from the moving sawmill to a source-only shot whose export-pinned excerpt contains `model.py` line 415, then returns to the moving model
- **THEN** the middle shot's own picture visibly shows `water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)` without a model alongside it, while the surrounding shots show the real model and the film's masthead remains in place

#### Scenario: Typed and lit source remains actual source

- **WHEN** a source-only shot types part of its pinned excerpt and has valid measured emphasis on identifiers already visible
- **THEN** the same source characters, syntax colours, cursor state and measured marks appear at the same video instants as in the existing split view, with no source character rewritten or lost

### Requirement: The opt-in leaves all default layouts unchanged

When `layout` is absent, a shot without `code` SHALL retain its model-only picture in the set `paper`, and a shot with `code` SHALL retain its source/model split in the set `paper-split`. Adding or leaving out `layout: source-only` on one shot SHALL change only that shot's picture: every other shot of the same episode, at the same output settings and viewer/browser environment, SHALL keep exact output-frame pixels in formats 0.2, 0.3 and 0.4. Source-only presentation SHALL be opt-in per shot, not inferred from the presence of code.

#### Scenario: An unchanged split-source film

- **WHEN** an existing 0.4 episode with a code shot is rendered without adding `layout`
- **THEN** its code and model stay side by side in the paper split, drawn as the paper sets draw them

#### Scenario: One shot opts in

- **WHEN** one code shot of a 0.4 episode gains `layout: source-only` and the episode is rendered again with the same viewer, browser and output settings
- **THEN** that shot shows the source alone, and every PNG of every shot that neither is it nor shows it in a transition equals the PNG of the render without the opt-in byte for byte

#### Scenario: An unchanged model-only or older film

- **WHEN** an unchanged model-only 0.4 episode or 0.2/0.3 episode is rendered
- **THEN** it keeps its model-only and split pictures in the paper sets, and no shot is drawn source-only

### Requirement: Source-only pictures remain visible, fitted and reproducible

At every posed source-only frame, including typing and emphasis instants, `preview` and `render` SHALL verify that the source panel is visible in its slot, its displayed text equals the current pinned excerpt state, and its content does not clip or overflow. They SHALL NOT pass merely because a viewer canvas exists; model-only and split frames SHALL keep their positive checks that the canvas fills the view's box. A source-only frame revisited at the same video instant SHALL reproduce exact pixels.

Source-only shots SHALL retain their authored camera/up/FOV requests, model
timing, and their validation, and those requests SHALL still count toward the
Viewer API the episode needs. Because a source-only shot places no view, no
hidden canvas SHALL be posed or projected for it, and preview SHALL NOT report
a lens change on it as reaching the picture. Model-only and split shots SHALL
retain their existing positive visible FOV/up projection checks.

#### Scenario: Source text does not fit

- **WHEN** the authored pinned excerpt overflows the source-only picture area at an output frame
- **THEN** preview or render refuses, naming the shot and frame time, rather than scrolling, shrinking or clipping it silently

#### Scenario: A blank source is not valid evidence

- **WHEN** a source-only frame's source panel is absent or outside its slot
- **THEN** preview or render refuses it, whatever viewer canvas exists elsewhere in the page

#### Scenario: Return to a typed instant

- **WHEN** preview captures a source-only frame, seeks to another instant and returns
- **THEN** its source and chrome pixels match the first capture exactly

#### Scenario: Changed hidden lens beside a visible source

- **WHEN** a source-only shot changes camera up or FOV while showing the pinned
  excerpt
- **THEN** the change is validated as authored and counts toward the Viewer API
  the episode needs, no view is posed for it and no lens-change proof is
  reported for it; the same FOV/up change on a model-only or split shot still
  requires the existing projected-picture proof
