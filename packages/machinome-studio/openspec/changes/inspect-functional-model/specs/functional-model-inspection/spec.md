## ADDED Requirements

### Requirement: The shop floor builds the conventional functional model before opening
When opening a project shop floor, the system SHALL use a solid-node CLI
one-shot build of `<project-root>/__init__.py` before declaring the shop floor
open. The floor service SHALL NOT import the project model into its own process.

#### Scenario: A project has a conventional model
- **WHEN** the maker opens the shop for a project whose root contains `__init__.py`
- **THEN** the system completes one solid-node CLI build and presents the built functional model in the shop workspace

#### Scenario: A project has no conventional model
- **WHEN** the maker opens the shop for a project whose root has no `__init__.py`
- **THEN** the solid-node CLI exits cleanly with a message that the model does not exist and the system does not declare the shop open

### Requirement: The shop floor refreshes a changed functional model
The system SHALL start the machinist's solid-node development process with a
floor-broker callback location. After that process reports a successfully
updated build, the broker SHALL notify connected browsers and they SHALL load
the complete current functional-model state.

#### Scenario: The machinist changes the model
- **WHEN** the machinist's development process reports that a new model build is ready
- **THEN** the broker publishes a model-change event and the browser replaces its artifact view with the complete current model state

#### Scenario: A later build fails
- **WHEN** a development-time model build fails after the floor has a previously successful model
- **THEN** the browser retains the last successful model state and does not present a partial update
