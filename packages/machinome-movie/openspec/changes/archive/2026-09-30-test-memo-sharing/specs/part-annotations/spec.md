## MODIFIED Requirements

### Requirement: Older episodes and older viewers are handled explicitly

Episodes in format `machinome-video-draft/0.2` SHALL parse and render with any
Viewer API 21 or later. Annotations SHALL require format
`machinome-video-draft/0.3` and Viewer API 28, and a movie document's marks
SHALL require Viewer API 28. `check`, `preview` and `render` MUST refuse an
episode or movie using annotations against a viewer declaring an older API,
with a message naming the source as a movie or an episode, the field, the
shot, the required and the declared API.

#### Scenario: Old episode, old viewer
- **WHEN** the unchanged sawmill or *Revolutions* episode is checked and previewed
  with the Viewer API 27 bundle
- **THEN** it passes as it did before this change.

#### Scenario: Annotated episode, old viewer
- **WHEN** an episode with annotations is previewed with a Viewer API 27 bundle
- **THEN** preview refuses before capturing, saying that this episode's
  annotations in that shot need Viewer API 28 and the bundle declares 27.

#### Scenario: Marked movie, old viewer
- **WHEN** a movie document whose view carries a mark is checked with a
  Viewer API 27 bundle
- **THEN** `check` refuses, saying that this movie needs Viewer API 28 for
  the marks in that shot and the bundle declares 27, and does not call the
  movie an episode.

#### Scenario: Annotations in a 0.2 episode
- **WHEN** an episode still declaring format 0.2 carries `annotations`
- **THEN** `check` refuses it and asks for format 0.3, rather than ignoring the field.
