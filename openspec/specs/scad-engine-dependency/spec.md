# scad-engine-dependency Specification

## Purpose

The OpenSCAD engine as a conditional, versioned provider of the core, resolved through the seam `machinome.scad_engine`: its one provider, the contract version check and its refusal, what an absent engine means for a value SolidPython built, that a plain number never consults it, and that the seam is the one core module naming the provider (ADR-171).
## Requirements
### Requirement: The OpenSCAD engine is resolved through one seam

The system SHALL resolve the OpenSCAD engine through one module of the core,
`machinome.scad_engine`, which names one provider, `machinome.openscad.engine`,
in its constant `PROVIDER`, and SHALL NOT name that provider in any other core
module. `scad_engine()` SHALL return the provider module when it is
importable, and SHALL return `None` when the import fails with a
`ModuleNotFoundError` whose missing module is `machinome.openscad`, the
provider itself, or `solid2`, the provider's kernel. Any other error raised
while importing the provider SHALL propagate unchanged. The resolution SHALL
happen at most once per process for a provider that resolves or is absent.

Importing `machinome.scad_engine` SHALL NOT import the provider or `solid2`.

#### Scenario: The provider is installed

- **WHEN** `scad_engine()` is called in an installation carrying
  `machinome.openscad.engine`
- **THEN** it returns that module, and a second call returns the same module
  without importing again

#### Scenario: The provider is absent

- **WHEN** `machinome.openscad` cannot be found, or `solid2` cannot be found
  when the provider imports it
- **THEN** `scad_engine()` returns `None`

#### Scenario: The provider is broken

- **WHEN** importing the provider raises an error other than a missing
  `machinome.openscad`, provider or `solid2` module
- **THEN** that error propagates from `scad_engine()` unchanged

### Requirement: The OpenSCAD engine's contract version is checked when it resolves

The seam SHALL declare the OpenSCAD engine contract version the core speaks as
`machinome.scad_engine.CONTRACT`, which is `1`. A resolved provider whose own
`CONTRACT` is absent or differs SHALL be refused with
`ScadEngineIncompatible`, whose message names the provider module, the version
the provider declares (or that it declares none) and the version the core
speaks. The refusal SHALL NOT be cached: every resolution of a mismatched
provider raises it.

#### Scenario: A provider declaring another version

- **WHEN** the provider declares `CONTRACT = 2`
- **THEN** `scad_engine()` raises `ScadEngineIncompatible` naming
  `machinome.openscad.engine`, `2` and `1`

#### Scenario: A provider declaring no version

- **WHEN** the provider declares no `CONTRACT`
- **THEN** `scad_engine()` raises `ScadEngineIncompatible` saying the provider
  declares none and naming `1`

### Requirement: A SolidPython value is an expression only through the engine

The core SHALL recognise a value as symbolic when it is the framework's own
symbolic value, an expression graph node, or a value the resolved OpenSCAD
engine adopts; it SHALL consult the engine only for a value that is none of
the first two and not a plain number. When the engine is absent, no other
value is symbolic: a SolidPython value reaching `machinome.math`, a law, a
bound, a chain or a profile contact SHALL be treated as a non-number,
non-expression value and SHALL meet the refusal that path already gives such a
value, with its existing wording. No path SHALL require the engine to be
present, and the seam SHALL raise no install refusal.

#### Scenario: Native values need no engine

- **WHEN** the engine is absent and a project composes time, drivers and
  `machinome.math` functions, compiles its laws and publishes its document
- **THEN** every result, every refusal and every published byte is the one an
  installation with the engine produces

#### Scenario: A SolidPython value without the engine

- **WHEN** the engine is absent and a running law returns a value SolidPython
  built
- **THEN** simulation construction refuses it as "neither a number nor an
  expression over its sources", as it refuses any other non-expression value

#### Scenario: Numbers never consult the engine

- **WHEN** a `machinome.math` function or an operator receives a plain `int`
  or `float`
- **THEN** the OpenSCAD engine is not consulted

