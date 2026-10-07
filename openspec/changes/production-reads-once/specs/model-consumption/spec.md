## MODIFIED Requirements

### Requirement: Structure reading preserves running state

Structural access SHALL use core-owned rest-only reading with normal result validation and linking, without simulation, geometry materialization, SCAD presentation or marking generation. It SHALL preserve public state, driver bindings and established motion semantics. Unsupported legacy stateful structure SHALL be refused contextually rather than simulated or assigned invented defaults. Native artifact reading SHALL be a separate demand and SHALL preserve current runtime banks or refuse an unsupported path. A rigid internal node whose children the native lifecycle already rendered SHALL be read from that render, so its author's `render()` runs at most once per instance whether the lifecycle or structural reading comes first, and the placements it applied are never applied again.

#### Scenario: Read an advanced machine
- **WHEN** structure is read twice from a machine already advanced to a nondefault running state
- **THEN** its states, driver bindings and established operation values remain unchanged, no simulate/materialize hook is called, and both occurrence sets agree

#### Scenario: Read a machine the lifecycle already built
- **WHEN** a fusion whose `render()` translates one of its two children has been built, alone or inside an assembly, before its structure is read
- **THEN** that child keeps exactly the one operation the build applied, a later `render()` returns the same children with the same operations, and the fused artifact made again from the read structure has the content identity the build produced

### Requirement: Facts and artifact copies use a coherent generation

The facade SHALL verify consumed source identity and existing source currency, derive geometry identity/facts from coherent pinned artifacts, and pair copied bytes with those exact facts. Public input observation, validation, hashes and executed-code provenance SHALL let a consumer share its profile/evidence inputs with this same invalidation boundary. Changed loaded sources SHALL refuse further reads rather than combine old classes with new bytes. Same-size restored-mtime artifact replacement SHALL invalidate weaker caches. A source state whose executed bytes cannot be verified SHALL carry explicit unverified provenance, never a verification claim. A source an existing node names that does not exist when the snapshot is constructed SHALL be refused with `FileNotFoundError` naming the node and the path, never reported as a changed input; a source that was observed and later changes or disappears SHALL still invalidate the generation with `ModelInputChangedError`.

#### Scenario: Artifact replaced during copying
- **WHEN** an artifact is replaced between geometry observation and copying
- **THEN** the consumer receives a coherent fact/byte pair or a contextual retry/refusal, never mismatching content

#### Scenario: Bind a model naming a missing file
- **WHEN** a snapshot is constructed over a model one of whose nodes names, among its files, a path that does not exist
- **THEN** construction raises `FileNotFoundError` whose message names the node's class and name and whose filename is the path, and no `ModelInputChangedError` is raised; a file that existed when the snapshot was constructed and is deleted afterwards is refused at the next read with `ModelInputChangedError`
