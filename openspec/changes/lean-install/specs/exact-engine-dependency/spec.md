## MODIFIED Requirements

### Requirement: An unavailable exact engine fails actionably at the point of use

When a path that needs the exact engine is reached and its provider module
cannot be found, or is found but refuses because the kernel its `occt` extra
installs cannot be found (the `kernel-extras` capability), the system SHALL
raise one error that names the exact engine, the operation that needed it, why
that operation needs it, and the install line `pip install "machinome[occt]"`,
before any geometry work is attempted. It SHALL be raised at the requiring
operation, not at import, and SHALL NOT surface as a bare
`ModuleNotFoundError` from framework internals.

`exact_engine()` SHALL answer `None` in both cases, without raising, so a
caller may ask whether exact geometry is available.

A provider module that is found but fails to import for another reason, such
as its kernel being found and failing to load, SHALL NOT be reported as
absent: the underlying import error SHALL be raised at the point of use, as
the `cli-startup-cost` capability requires of every deferred import.

The system SHALL NOT substitute the mesh engine, degrade an exact question to
a faceted one, or skip an operation when the exact engine is unavailable.

The framework SHALL declare the `occt` extra, so the install line it names
installs the engine's kernel.

#### Scenario: A missing engine names the install

- **WHEN** `require_exact_engine('exact fusion Bracket', 'fusing its exact
  children')` is called in an interpreter where the engine's provider module
  cannot be imported
- **THEN** it raises an error whose message names the exact engine, `exact
  fusion Bracket`, `fusing its exact children` and `pip install
  "machinome[occt]"`

#### Scenario: An absent OCCT binding is an absent engine

- **WHEN** `require_exact_engine('exact fusion Bracket', 'fusing its exact
  children')` is called in an interpreter where the provider module exists
  and `OCP` cannot be found
- **THEN** it raises the same error naming `pip install "machinome[occt]"`,
  and `exact_engine()` answers `None`

#### Scenario: Asking about availability does not raise

- **WHEN** `exact_engine()` is called in an interpreter where the provider
  module cannot be imported
- **THEN** it returns `None`

#### Scenario: A broken engine reports its own failure

- **WHEN** the provider module is present but importing it raises an import
  error from inside, its kernel having been found
- **THEN** that import error is raised at the point of use, rather than the
  engine being reported as not installed

#### Scenario: The extra the refusal names exists

- **WHEN** the framework's package metadata is read
- **THEN** it declares an `occt` extra
