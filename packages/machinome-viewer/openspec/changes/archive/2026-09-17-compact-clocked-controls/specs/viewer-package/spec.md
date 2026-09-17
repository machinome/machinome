## ADDED Requirements

### Requirement: On-screen machine controls leave the machine visible

The viewer's posed, running and clocked on-screen control panels SHALL occupy
a bounded rail at one side of the viewer rather than widening over most of the
model. On an ordinary wide pane the rail SHALL prefer approximately thirty
percent of the pane, SHALL have a finite maximum width, and SHALL leave the
rest of the pane directly visible and usable. On a pane too narrow for that
proportion to remain operable, the rail MAY use a larger proportion but SHALL
never exceed the pane.

A panel taller than the viewer SHALL scroll internally. Every input,
instruction, state readout, outcome and transport the applicable requirements
present SHALL remain reachable; compacting the panel SHALL NOT suppress an
operation or change the request it makes.

#### Scenario: A large clocked machine leaves room to use the model

- **WHEN** a clocked machine with dozens of handles and readouts is mounted in
  a normal desktop viewer
- **THEN** its chrome occupies a bounded side rail, the majority of the viewer
  remains available to see and manipulate the model, and controls beyond the
  rail's height are reached by scrolling the rail rather than the page

#### Scenario: A narrow host keeps the controls operable

- **WHEN** the same machine is mounted in a pane narrower than the rail's
  preferred desktop width
- **THEN** the rail stays within the pane and its controls wrap rather than
  being clipped or extending the page
