## MODIFIED Requirements

### Requirement: Source on screen is authentic

The author SHALL select real Python line ranges from the consuming project at
the model's pinned revision and show them in a source panel: in an episode, a
shot's `code`; in a movie document, a `source` element a chapter declares on an
excerpt of `sourceCode` and a shot places in a slot of its set. Production MUST
refuse changed bytes, missing files, out-of-repository paths and invalid line
ranges before rendering. Build records SHALL identify the file, lines, revision
and content hashes.

#### Scenario: Show the wheel connection
- **WHEN** a scene selects the sawmill's wheel-to-crankshaft declaration
- **THEN** the audience sees that source with Python highlighting beside the model.

#### Scenario: Refuse a fabricated or stale excerpt
- **WHEN** selected source differs from the pinned model revision
- **THEN** production refuses it rather than presenting it as that model's code.

#### Scenario: The source in the template's left-hand slot
- **WHEN** a shot of *Cut and Advance* places its chapter's source panel in
  `LeonardoSplit`'s `left`
- **THEN** the pinned excerpt is drawn inside that slot's box in the type the
  set gives it, and preview refuses a frame on which it does not fit.

### Requirement: Typing is reproducible and timed

The author SHALL time source reveals in shot-local seconds, including pauses:
in an episode by typing cues, in a movie document by `type` actions that type
through a line over a duration. In a movie document typing SHALL continue
across the shots of a chapter from where the chapter's previous typing
stopped, and a panel completed in an earlier shot of the chapter SHALL open
complete. Typing and highlighting MUST be derived from video time, preserve
source text, escape embedded markup and restore exactly after seeking. Invalid
or incomplete typing schedules MUST be refused. The whole excerpt SHALL remain
legible.

#### Scenario: Follow measured narration
- **WHEN** the narration reaches the wheel connection's authored cue
- **THEN** its actual line types into view while the model follows its own authored clock.

#### Scenario: Revisit an earlier instant
- **WHEN** capture seeks forward and returns
- **THEN** source, cursor, visibility and model pixels match the original instant.

#### Scenario: Typing resumes after a cut
- **WHEN** a chapter of *Cut and Advance* types its excerpt through line 414 in
  one shot and through line 415 in the next
- **THEN** the second shot opens with the text typed through line 414 and types
  on from there, with nothing typed twice.
