## MODIFIED Requirements

### Requirement: Parameter-hashed artifact identity

The system SHALL give each node instance a `uniq_id` of the form
`<readable-prefix>-<12-hex-sha256>`, hashed over a canonical serialization of
the class `__qualname__` and the node's parameters. For an external-file
wrapper (`StlNode`, `StepNode`, `JScadNode` or `OpenScadNode`), the class
identity SHALL additionally include its defining Python source's normalized
real path relative to the project root owning the resolved external source.
It SHALL NOT depend on an absolute checkout path, module import alias,
source contents or timestamp. Ordinary Python nodes SHALL retain their
existing canonical serialization byte for byte.

For a class that declares no parameters and no children under the
`declarative-nodes` capability, the parameters are the positional args in
order and the kwargs sorted by key that reach `AbstractBaseNode.__init__`,
exactly as before. For a declarative class, the parameters are the resolved,
coerced values of its declared parameters sorted by name, derived by the
framework and never forwarded by hand. The readable prefix is sanitized and
truncated to 60 characters; the hash is computed over the full untruncated
serialization. Build artifact basenames are always `<script-name>-<uniq_id>`.
The `name=` kwarg SHALL never influence `uniq_id`.

Generated declaration-site joint and fresh-mate specializations SHALL retain
the original author class's defining source and qualname for artifact identity.
Origin qualification SHALL NOT change constructor acceptance/refusal or
source-containment behavior. When an otherwise constructible wrapper is
defined outside a project, its defining source SHALL be expressed relative to
the artifact-owning project root, including parent-directory components when
needed; it SHALL NOT be newly refused for lacking its own manifest.

#### Scenario: Parameter change invalidates artifact key

- **WHEN** the same node class is instantiated with any differing parameter
  value
- **THEN** the two instances have different `uniq_id`s and separate build
  artifacts

#### Scenario: Identical instances share artifacts

- **WHEN** the same class is instantiated twice with identical args
- **THEN** both instances share one `uniq_id` and one cached artifact set

#### Scenario: Distinct no-arg classes never collide

- **WHEN** two no-arg node classes with different qualnames are built, or two
  same-qualname external wrappers defined in different Python files are built
- **THEN** their `uniq_id`s differ because their class identities differ

#### Scenario: A declarative class cannot forget a parameter

- **WHEN** a class declares six parameters and is realized twice with one
  value differing
- **THEN** the two `uniq_id`s differ without the class forwarding anything
  to `super().__init__()`

#### Scenario: A migrated class keeps its key

- **WHEN** a class that forwarded all of its kwargs to `super().__init__()`
  with float defaults is rewritten to declare exactly those parameters with
  the same defaults
- **THEN** an instance realized with defaults has the same `uniq_id` as
  before the rewrite

#### Scenario: Local wrapper identity survives project relocation and aliases

- **WHEN** the same project, external asset and project-local defining wrapper
  move together to a different absolute directory, or that class is imported
  through a different module alias, with its qualname and parameters unchanged
- **THEN** its `uniq_id` and project-relative artifact path are unchanged

#### Scenario: A specialization keeps the author's geometry key

- **WHEN** a source-bound author class is realized with declaration-site joints
  or with a fresh freedom mate's generated specialization
- **THEN** its `uniq_id` equals the author class's for the same parameters and
  no generated implementation source or joint declaration enters the key

#### Scenario: Ordinary Python nodes keep existing identity bytes

- **WHEN** an ordinary Python node is realized with unchanged class and
  parameters after external-wrapper origin qualification is introduced
- **THEN** its canonical serialization and `uniq_id` remain unchanged

#### Scenario: A nonproject defining wrapper remains constructible

- **WHEN** a wrapper defined in a module with no manifest is already
  constructible using an external file inside a discoverable project
- **THEN** identity includes its defining Python path relative to that project
  and construction remains accepted without requiring a new manifest
