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
invalidate the node's artifacts. A subclass without `stl_source`, or
declaring it as an empty string, SHALL fail at construction with
`ValueError` naming the class, `stl_source` and the module defining the
class, in the shape every source-bound leaf refuses an undeclared source
under the `node-model` capability.

A subclass whose `stl_source` names a file that does not exist SHALL also
fail at construction, with an error naming the class, `stl_source` and the
value declared on it, and the absolute path the declaration resolved to; a
`stl_source` resolving to something that exists but is not a regular file
SHALL fail the same way, saying so. Neither failure SHALL substitute a
placeholder mesh, and neither SHALL be deferred to the moment the mesh is
read.

A subclass whose `stl_source` resolves, after symbolic links, to a path
outside the project root of the module that declares the subclass SHALL
fail at construction with `ValueError`, whether or not the file exists,
naming the class, `stl_source` and its declared value, the resolved path
and the project root. The project root is the one the manifest module
finds above the declaring module's file; a module that lies in no project
is not judged. Construction SHALL NOT read the mesh before this check.

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
- **THEN** `ValueError` is raised naming the class, the missing
  attribute and the module defining the class, and no mesh is read

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

#### Scenario: A mesh outside the project is refused

- **WHEN** an `StlNode` subclass declares `stl_source` as a `../` path
  that resolves to an existing file above its project root
- **THEN** construction raises `ValueError` naming the class,
  `stl_source`, the resolved path and the project root, and no mesh is
  read

#### Scenario: A mesh reached through a symbolic link is refused

- **WHEN** an `StlNode` subclass declares `stl_source = 'link/part.stl'`
  and `link` is a symbolic link to a directory outside the project root
- **THEN** construction raises `ValueError` saying the source lies
  outside the project
