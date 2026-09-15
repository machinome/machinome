## MODIFIED Requirements

### Requirement: STEP source declaration and freshness

A `StepNode` subclass SHALL declare its part with a `step_source` class
attribute naming a STEP file, resolved relative to the directory of the
Python module defining the subclass; an absolute path SHALL resolve to
itself. The resolved file SHALL be the node's source file for freshness:
its modification time drives artifact currency exactly as an `StlNode`'s
`.stl` and a `JScadNode`'s `.js` do. The wrapper Python module itself SHALL
also be part of the node's tracked file set, transitively with the
project-local modules it imports, because it carries geometry-affecting
code — the `part` selection and the `adjust` hook — so editing the wrapper
SHALL invalidate the node's artifacts. A subclass without `step_source`
SHALL fail at construction with an error naming the class.

A subclass whose `step_source` names a file that does not exist SHALL also
fail at construction, with an error naming the class, `step_source` and the
value declared on it, and the absolute path the declaration resolved to; a
`step_source` resolving to something that exists but is not a regular file
SHALL fail the same way, saying so. Neither failure SHALL substitute a
placeholder solid, and neither SHALL be deferred to the moment the document
is read — a vendor document that has not been fetched is a declaration to
correct or a file to obtain, never geometry to invent.

#### Scenario: The declared file resolves beside the wrapper module

- **WHEN** a `StepNode` subclass in `parts/gearbox.py` declares
  `step_source = 'gearbox.step'`
- **THEN** the node reads `parts/gearbox.step`, and its build artifacts
  mirror that source location

#### Scenario: Editing the STEP file invalidates the artifacts

- **WHEN** the declared STEP file is modified after a build
- **THEN** the node's artifacts report not-up-to-date and are regenerated
  on the next build

#### Scenario: Editing the wrapper module invalidates the artifacts

- **WHEN** the wrapper `.py` defining the subclass is modified after a
  build — for example its `part` selection or its `adjust` hook changes
- **THEN** the node's artifacts report not-up-to-date and are regenerated
  on the next build

#### Scenario: A missing declaration fails at construction

- **WHEN** a `StepNode` subclass declaring no `step_source` is instantiated
- **THEN** an error is raised naming the class and the missing attribute

#### Scenario: A declared document that is not there fails at construction

- **WHEN** a `StepNode` subclass whose `step_source` names a file that does
  not exist — a vendor document not yet fetched or extracted — is
  instantiated
- **THEN** an error is raised naming the class, `step_source` and its
  declared value, and the absolute path resolved from it, and no document is
  read and no artifact is written

#### Scenario: A step_source naming a directory fails at construction

- **WHEN** a `StepNode` subclass whose `step_source` resolves to a directory
  is instantiated
- **THEN** an error is raised saying the path is not a file, naming the class
  and `step_source`, rather than the STEP reader failing on it later
