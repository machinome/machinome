## Purpose

Let Leonardo show its real, pinned source alone between views of the moving sawmill in an ordinary Videomaker episode, without promoting the disposable dark-source renderer or changing existing shot layouts.

## ADDED Requirements

### Requirement: A code shot may show source without a competing model view

In format `machinome-video-draft/0.4`, a shot with `code` SHALL accept `layout: source-only`. Its own picture SHALL show the pinned source panel in the main picture area and no visible model canvas. The film SHALL retain its current episode style, masthead, series label, progress rule, overlays, narration and external captions. Source text, syntax colour, typing cursor and measured identifier emphasis SHALL follow their existing rules; the source SHALL remain literal and safely escaped. Source-only presentation SHALL NOT change the shot's authored model time or camera, and SHALL NOT require a newer Viewer API than that shot otherwise requires.

#### Scenario: The current Leonardo drive line appears between moving model shots

- **WHEN** a format-0.4 film cuts from the moving sawmill to a source-only shot whose export-pinned excerpt contains `model.py` line 415, then returns to the moving model
- **THEN** the middle shot's own picture visibly shows `water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)` without a model alongside it, while the surrounding shots show the real model and the film's chrome remains in place

#### Scenario: Typed and lit source remains actual source

- **WHEN** a source-only shot types part of its pinned excerpt and has valid measured emphasis on identifiers already visible
- **THEN** the same source characters, syntax colours, cursor state and measured marks appear at the same video instants as in the existing split view, with no source character rewritten or lost

### Requirement: The opt-in leaves all default layouts unchanged

When `layout` is absent, a shot without `code` SHALL retain its model-only picture, and a shot with `code` SHALL retain its existing source/model split. The same unchanged episode at the same output settings and viewer/browser environment SHALL keep exact output-frame pixels in formats 0.2, 0.3 and 0.4. Source-only presentation SHALL be opt-in per shot, not inferred from the presence of code.

#### Scenario: An unchanged split-source film

- **WHEN** an existing 0.4 episode with a code shot is rendered without adding `layout`
- **THEN** its code and model stay side by side and every corresponding PNG equals the pre-change output byte for byte

#### Scenario: An unchanged model-only or older film

- **WHEN** an unchanged model-only 0.4 episode or 0.2/0.3 episode is rendered
- **THEN** it retains its previous visible picture and corresponding PNG bytes

### Requirement: A source-only declaration cannot hide an incompatible cue

`check`, `preview` and `render` SHALL refuse `layout: source-only` outside format 0.4, without `code`, or with a nonempty `annotations`, `highlight` or `pictures` list, naming the shot and conflicting field. Unknown layout values SHALL be refused rather than treated as split or model-only. These refusals SHALL apply only to the new opt-in; existing split and model-only cue combinations retain their rules.

#### Scenario: No source to show

- **WHEN** a shot declares `layout: source-only` but has no `code`
- **THEN** `check` refuses it by shot and asks for a pinned code excerpt

#### Scenario: A target or picture would be covered

- **WHEN** a source-only shot declares an annotation, highlight or picture cue
- **THEN** `check` refuses the cue by shot and field instead of omitting it or measuring a hidden model stage as visible

#### Scenario: Older format or misspelling

- **WHEN** a 0.3 shot declares `layout: source-only`, or a 0.4 shot declares `layout: souce-only`
- **THEN** `check` refuses the unsupported format or unknown value by shot; neither case silently falls back to its old layout

### Requirement: Source-only pictures remain visible, fitted and reproducible

At every posed source-only frame, including typing and emphasis instants, `preview` and `render` SHALL verify that the source panel is visible in the intended picture area, its displayed text equals the current pinned excerpt state, and its content does not clip or overflow. They SHALL NOT pass merely because a hidden viewer canvas exists; model-only and split frames SHALL keep their existing positive canvas-fill checks. A source-only frame revisited at the same video instant SHALL reproduce exact pixels.

Source-only shots SHALL retain their authored camera/up/FOV requests, model
timing, Viewer API requirements, and internal pose validation. Preview SHALL
NOT treat projection through their hidden canvas as evidence that a lens
change reached the visible picture. Model-only and split shots SHALL retain
their existing positive visible FOV/up projection checks.

#### Scenario: Source text does not fit

- **WHEN** the authored pinned excerpt overflows the source-only picture area at an output frame
- **THEN** preview or render refuses, naming the shot and frame time, rather than scrolling, shrinking or clipping it silently

#### Scenario: A blank source is not valid evidence

- **WHEN** a source-only frame has a mounted but hidden model canvas while its source panel is absent or outside its intended area
- **THEN** preview or render refuses it instead of passing a model-canvas check

#### Scenario: Return to a typed instant

- **WHEN** preview captures a source-only frame, seeks to another instant and returns
- **THEN** its source and chrome pixels match the first capture exactly

#### Scenario: Changed hidden lens beside a visible source

- **WHEN** a source-only shot changes camera up or FOV while showing the pinned
  excerpt
- **THEN** preview validates the resolved pose and the visible source panel
  without dereferencing a hidden canvas or reporting visible lens-change
  proof; the same FOV/up change on a model-only or split shot still requires
  the existing projected-picture proof

### Requirement: Each side of a join keeps its own shot layout

A source-only shot SHALL participate in existing hard cuts, fades, dissolves, wipes and slides without changing their duration, easing, outgoing continuation, narration or chrome behavior. During a join, each incoming and outgoing picture SHALL use its own shot's layout and existing time mapping, including source text continued from an outgoing shot under the existing code rule. A transition may visibly combine a source-only incoming picture with an outgoing model picture; it SHALL NOT add a model beside the source inside the source-only picture. A render reusing cached shots SHALL produce the same PNG bytes as a fresh render when a source-only layout or an outgoing layout changes.

#### Scenario: Model enters source and source exits to model

- **WHEN** a moving model shot joins a source-only shot, and that source-only shot later joins a model shot
- **THEN** each side of each transition has the picture its own shot and time specify; source never acquires the split-model pane, and the outgoing source uses the same continuation it would have had before this layout option

#### Scenario: A source-only edit reaches the next join

- **WHEN** a source shot changes from split to source-only and the following shot's incoming transition still shows that source shot as outgoing
- **THEN** both the changed source shot and the dependent incoming shot are recaptured as necessary, and every incremental output PNG matches the corresponding fresh-render PNG
