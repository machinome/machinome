## ADDED Requirements

### Requirement: A multi-model project's folder card previews its models

A folder card standing for a project repository that declares several models
SHALL present the previews of the first three models the manifest declares, in
declaration order, laid out side by side within the card's model preview area.
A declared model that has no preview SHALL keep its place in that row and show
the same absent-preview treatment a project card shows, so the row states how
many models it stands for.

A folder card standing for a directory that holds project repositories SHALL
NOT present model previews, because such a directory declares no model of its
own.

The shop SHALL name each previewed model by its own hub entry path and SHALL
report the revision of its current preview, so that the browser requests it
from the same screenshot route that serves that model's own project card.

#### Scenario: A folder card stands for a multi-model project

- **WHEN** the maker views a folder listing a project repository whose manifest declares more than one model
- **THEN** that project's folder card presents the previews of its first three declared models side by side, in declaration order, instead of the folder glyph

#### Scenario: A multi-model project declares more than three models

- **WHEN** a listed project repository declares more than three models
- **THEN** its folder card presents exactly the first three the manifest declares

#### Scenario: A declared model has never been rendered

- **WHEN** one of the models a folder card previews has no valid preview
- **THEN** that model keeps its place in the row and shows the absent-preview treatment, and its siblings still show their pictures

#### Scenario: A folder card stands for a catalogue directory

- **WHEN** the maker views a folder holding a directory that is not a repository and contains project repositories
- **THEN** that directory's folder card shows the folder glyph and no model preview
