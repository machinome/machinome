## MODIFIED Requirements

### Requirement: Unchanged shots reuse verified frames

`render` SHALL reuse the complete output-frame set of a shot only when its effective visual inputs and global output-frame positions are unchanged and its cached frame set is complete and verified. It SHALL capture invalidated shot sets again. The cache unit is the **whole shot**, including its incoming transition; no promise is made to reuse only a transition's unaffected suffix. A local edit SHALL NOT invalidate an unrelated shot merely because both shots share the episode or movie or because unused picture/media metadata changed. Changes to common viewer/model/renderer/stage/chrome inputs SHALL invalidate every affected shot, even if that means the whole film. The stage bundle a film is drawn with, the runtime and the project's stage modules together, SHALL be a common input.

#### Scenario: Correct one shot with a following join
- **WHEN** Leonardo's `demo-incremental-rendering` changes only the camera or title of its middle shot, followed by a shot with an incoming transition
- **THEN** the edited middle shot and the complete following shot are captured again, other independently unchanged shots reuse their verified frames, and the manifest reports those counts by shot.

#### Scenario: Change an unused or unrelated picture
- **WHEN** the bytes of a picture used only by one shot change, or an unused picture declaration changes
- **THEN** only shots whose own or outgoing-transition pictures reach those bytes recapture; a wholly unused picture declaration causes no PNG recapture, though current validation and release metadata still update.

#### Scenario: Change a common film input
- **WHEN** the viewer bundle, model export asset, renderer/page behavior, stage bundle, effective film-wide chrome, output geometry/FPS, or film duration changes
- **THEN** no shot is reused under an old common input. Film duration remains a common input even though no film-wide drawn element now depends on it: this is a deliberately conservative choice, and a duration change recaptures every shot.

#### Scenario: Change the template
- **WHEN** only Leonardo's `stage.tsx` changes between two renders of *Cut and Advance*
- **THEN** every shot is captured again, and the manifest records the new stage bundle's hash.
