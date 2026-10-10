## ADDED Requirements

### Requirement: Explicit frame direction precision is documented narrowly

Public Frame and ResolvedFrame docstrings and the frame/readout explanation in
`docs/concepts/joints.rst` SHALL state that explicitly supplying BOTH x and z
retains full normalized/projected/cross-product direction precision without
component snap. They SHALL distinguish explicit default z from omitted z,
state that omitted x (including None) and explicit x with omitted z retain
existing snapped/default behavior, and retain principal inference and named
degeneracy refusals. They SHALL state that resolved_frames returns the same
cached basis mates use, not a separately altered display basis, and SHALL NOT
imply that final mate rotation/axis snap or Joint axis snapping changes.

`docs/project/changelog.rst` SHALL record the new numeric contract under
Unreleased without changing the released section or release substitutions.
Reader-facing explanations SHALL use mechanical kinds rather than originating
project names, and SHALL introduce no precision flag or new signature.

#### Scenario: A reader supplies an exact attachment triad

- **WHEN** a reader consults Frame help and the frame/readout manual passage
- **THEN** they learn the both-explicit precision rule, unchanged projection
  and refusal behavior, same actual resolved basis and unchanged final snap

#### Scenario: A reader omits the default z

- **WHEN** a reader compares Frame(x=...) with Frame(z=(0,0,1), x=...)
- **THEN** the documentation explains that only the latter supplies both
  directions explicitly and that the former keeps the old snapped path

#### Scenario: A reader checks the change's publication state

- **WHEN** a reader reads the changelog
- **THEN** the precision change is under Unreleased and the released record
  remains untouched without presenting the new contract as already published
