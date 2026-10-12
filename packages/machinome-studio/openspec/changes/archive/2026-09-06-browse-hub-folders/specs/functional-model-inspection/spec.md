## MODIFIED Requirements

### Requirement: The shop floor builds the selected functional model before opening
When opening a shop floor for a hub entry, the system SHALL use a solid-node CLI
one-shot build of the model that entry names before starting the Floor service
or agent runtime. For an entry naming a declared model, that is the named model;
for a project listed as a single openable project, it is the project's default
model. The build SHALL produce a complete viewer snapshot and all referenced
model files in that model's own build directory before Floor can be declared
open. The Model area SHALL consume only that completed snapshot and its
referenced model files. Floor MAY list, read, and atomically replace verified
project source as inert text for the Code area, but it SHALL NOT import,
execute, reload, or interpret that source.

#### Scenario: A named project has a buildable default model
- **WHEN** the maker opens the shop for a project listed as one openable project whose default model builds successfully
- **THEN** the system completes one solid-node CLI build and makes that model's complete build artifacts available before starting Floor

#### Scenario: The entry names one model of several
- **WHEN** the maker opens an entry naming one of a project's declared models
- **THEN** the system builds that model and serves that model's build directory, and does not build or serve the project's other models

#### Scenario: The build command succeeds without a complete publication
- **WHEN** the initial build does not leave a readable viewer snapshot and every referenced model artifact
- **THEN** the system treats preparation as failed and does not start Floor or its agents

#### Scenario: The maker first opens the reported browser location
- **WHEN** the system has reported a shop as open for an entry
- **THEN** the browser can retrieve the already-validated initial viewer snapshot rather than receiving a no-build response

#### Scenario: The maker opens project source
- **WHEN** the maker reads a verified text file through Code
- **THEN** Floor returns inert text without using it as functional-model input or executing it
