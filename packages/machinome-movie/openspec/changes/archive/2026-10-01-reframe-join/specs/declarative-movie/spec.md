## ADDED Requirements

### Requirement: A shot can come in by a reframe

A shot SHALL accept `transition=Reframe(duration, ease=)` beside
`Dissolve`, `Fade`, `Wipe` and `Slide`, written `{"kind": "reframe",
"duration"}` with `ease` when given (smooth otherwise). A reframe whose shot
and the shot before it place no view element in both MUST be refused by
name, at class creation where both shots are known: by the chapter when
both shots are its own, by the movie when the shot is its chapter's first
(whose previous shot is the last of the chapter before, which never shares
a view). The refusal SHALL name the chapter or movie, both shots, the
transition and `no view element in both`. A direction or a colour on a
reframe MUST be refused.

#### Scenario: The tour's reframe
- **WHEN** the fixture tour's `question` places `wide` in
  `PlaybillSplit.right` with `transition=Reframe(0.8)` after `hook`, which
  places `wide` in `Playbill.stage`
- **THEN** it evaluates to `{"kind": "reframe", "duration": 0.8}` on
  `question`, twice identically.

#### Scenario: No view in both shots
- **WHEN** a chapter's shot placing only a source panel comes in by
  `Reframe(0.8)` from a shot placing only a view
- **THEN** the chapter's class is refused naming the chapter, both shots
  and `no view element in both`.

#### Scenario: A chapter that opens with a reframe
- **WHEN** a chapter's first shot comes in by `Reframe(0.8)`
- **THEN** the movie's class is refused naming the shot, the last shot of
  the chapter before and `no view element in both`.
