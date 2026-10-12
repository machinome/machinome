## ADDED Requirements

### Requirement: The inspector does not repeat its navigator in machine chrome

The inspector's assembly navigator SHALL be its on-screen way to focus a child
assembly. Within the inspector, posed, running and clocked machine chrome SHALL
retain the focused node's ancestor breadcrumb but SHALL NOT repeat the focused
node's children as a field of descendant-focus buttons. A plain viewer mounted
without the inspector SHALL retain those buttons so its focused controls stay
reachable without a navigator.

The inspector's default clocked-machine presentation SHALL omit the on-screen
Reset button. The viewer handle's machine reset operation SHALL remain
available and unchanged, and a plain viewer SHALL retain its existing Reset
control.

#### Scenario: The Curta root does not become seventeen focus buttons

- **WHEN** the inspector opens a clocked Curta whose root has result and turns
  register children
- **THEN** those children appear in the assembly navigator and not as buttons
  across the machine-control rail, while its ancestor breadcrumb and operating
  controls remain visible

#### Scenario: A host retains reset without an inspector button

- **WHEN** a clocked machine is mounted in the inspector
- **THEN** no Reset button is presented in its control rail and the host can
  still return the machine to its initial bank through the viewer handle

#### Scenario: A plain viewer remains self-navigable

- **WHEN** the same document is mounted with the plain viewer rather than the
  inspector
- **THEN** its descendant-focus buttons and clocked Reset button remain
  available exactly as before
