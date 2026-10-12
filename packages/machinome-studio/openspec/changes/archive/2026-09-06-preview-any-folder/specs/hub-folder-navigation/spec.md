## MODIFIED Requirements

### Requirement: A multi-model project's folder card previews its models

Every folder card SHALL present up to three previews of what the folder holds,
laid out side by side within the card's preview area, in place of the folder
glyph. The shop SHALL choose them by one rule:

- when the folder's directory carries a manifest declaring models, the first
  three models it declares, in declaration order;
- otherwise the first three openable entries the folder holds, in the order the
  hub lists them, descending into the folders it holds when its own entries are
  folders.

A previewed entry that has no preview SHALL keep its place in that row and show
the same absent-preview treatment a project card shows, so the row states how
many entries it stands for. A folder holding no openable entry at all SHALL
show the folder glyph.

The shop SHALL name each previewed entry by its own hub entry path and SHALL
report the revision of its current preview, so that the browser requests it
from the same screenshot route that serves that entry's own project card. The
shop SHALL stop looking once it has the previews a card shows, so that listing
a folder costs no more for a folder holding many projects than for one holding
few.

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
- **THEN** that directory's folder card presents the previews of the first three openable entries it holds, in the order the hub lists them

#### Scenario: A catalogue folder holds its projects deeper down

- **WHEN** a catalogue folder's own entries are themselves folders holding projects
- **THEN** its card previews the first openable entries found by descending those folders in listing order

#### Scenario: A folder holds nothing openable

- **WHEN** a listed folder holds no openable entry
- **THEN** its card shows the folder glyph

## ADDED Requirements

### Requirement: Closing a project returns the maker to the folder that lists it

When the maker closes an open project, the shop SHALL return them to the
listing of the folder that holds that project's entry, and that folder SHALL be
what the browser location carries. For a model of a multi-model project this is
that project's folder of models; for a project held directly by the working
folder it remains the working folder.

#### Scenario: The maker closes a project held by a folder

- **WHEN** the maker closes a project whose entry is held by a folder below the working folder
- **THEN** the hub lists that folder

#### Scenario: The maker closes one model of a multi-model project

- **WHEN** the maker closes an open model of a project declaring several models
- **THEN** the hub lists that project's models

#### Scenario: The maker closes a project at the working folder

- **WHEN** the maker closes a project held directly by the working folder
- **THEN** the hub lists the working folder
