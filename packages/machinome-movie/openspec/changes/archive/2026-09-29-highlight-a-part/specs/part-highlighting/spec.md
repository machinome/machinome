## ADDED Requirements

### Requirement: A named part stands out while the rest is kept, dimmed or ghosted

The author SHALL add timed `highlight` cues to a shot, each naming the parts to
lift (production layer names or assembly paths), what happens to every other
part (`keep`, `dim` or `ghost`, default `keep`) and optionally a tint colour
(default the production accent). While a cue is active the audience SHALL see
the named parts tinted and the others unchanged, dimmed, or ghosted: still
drawn, translucent, so parts behind them show through. Highlighting MUST NOT
change the model's pose, the camera, or which parts are hidden.

#### Scenario: See the pawls through the frame
- **WHEN** the *Revolutions* pawls shot highlights the driving pawl and ratchet
  with `others: ghost` instead of hiding the timber structure
- **THEN** the pawl and ratchet stand out in the accent tint while the frame
  around them remains visible as a translucent context.

#### Scenario: Cue ends or the shot cuts
- **WHEN** video time reaches a cue's `to`, or the next shot begins
- **THEN** every part's appearance is restored exactly as it was before the cue.

### Requirement: Hidden layers keep their meaning

Parts a shot hides with `hiddenLayers` SHALL stay hidden during a highlight,
whatever happens to the other parts. Production MUST refuse a highlight naming a
part the same shot hides.

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
a colour that is not `#rrggbb`, times outside the shot, and overlapping cues.
Highlights SHALL require format `machinome-video-draft/0.3` and Viewer API 28;
an episode using them against an older viewer MUST be refused with the field,
the shot, the required and the declared API. Episodes without highlights keep
their previous behaviour and viewer requirement.

#### Scenario: Bare path written as layers
- **WHEN** an author writes `parts: [Saw mechanism, Connecting rod]` without the
  inner list
- **THEN** `check` refuses two unknown layers rather than guessing a path.

#### Scenario: Highlighted episode, old viewer
- **WHEN** an episode with a highlight is rendered with a Viewer API 27 bundle
- **THEN** render refuses before capturing any frame and names Viewer API 28.
