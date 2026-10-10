## MODIFIED Requirements

### Requirement: STL source declaration and freshness

An `StlNode` subclass SHALL declare its part with a `stl_source` class
attribute naming an STL file, resolved relative to the directory of the
Python module defining the subclass. The resolved file SHALL be the
node's source file for freshness: its mtime drives artifact currency
exactly as a `JScadNode`'s `.js` does. In addition — and unlike the
other external-file adapters — the wrapper Python module itself SHALL
be part of the node's tracked file set, because it carries
geometry-affecting code (`adjust`, `body`); editing the wrapper SHALL
invalidate the node's artifacts. A subclass without `stl_source` SHALL
fail at construction with an error naming the class.

A subclass whose `stl_source` names a file that does not exist SHALL also
fail at construction, with an error naming the class, `stl_source` and the
value declared on it, and the absolute path the declaration resolved to; a
`stl_source` resolving to something that exists but is not a regular file
SHALL fail the same way, saying so. Neither failure SHALL substitute a
placeholder mesh, and neither SHALL be deferred to the moment the mesh is
read.

#### Scenario: The declared file resolves relative to the wrapper module

- **WHEN** an `StlNode` subclass in `parts/bracket.py` declares
  `stl_source = 'bracket.stl'`
- **THEN** the node reads `parts/bracket.stl`, and its build artifacts
  mirror that source location

#### Scenario: Editing the STL invalidates the artifact

- **WHEN** the declared `.stl` file is modified after a build
- **THEN** the node's artifact reports not-up-to-date and is
  regenerated on the next build

#### Scenario: Editing the wrapper module invalidates the artifact

- **WHEN** the wrapper `.py` defining the `StlNode` subclass is
  modified after a build — for example its `adjust` hook or `body`
  selection changes
- **THEN** the node's artifact reports not-up-to-date and is
  regenerated on the next build

#### Scenario: A missing declaration fails at construction

- **WHEN** an `StlNode` subclass declaring no `stl_source` is
  instantiated
- **THEN** an error is raised naming the class and the missing
  attribute

#### Scenario: A declared mesh that is not there fails at construction

- **WHEN** an `StlNode` subclass whose `stl_source` names a file that does
  not exist is instantiated
- **THEN** an error is raised naming the class, `stl_source` and its
  declared value, and the absolute path resolved from it, and no mesh is
  read and no artifact is written

#### Scenario: A stl_source naming a directory fails at construction

- **WHEN** an `StlNode` subclass whose `stl_source` resolves to a directory
  is instantiated
- **THEN** an error is raised saying the path is not a file, naming the class
  and `stl_source`, rather than the mesh loader failing on it later
