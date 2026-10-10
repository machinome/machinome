## ADDED Requirements

### Requirement: Read the supplied effective model

The system SHALL expose `machinome.model.ModelSnapshot` and `Reference(model_type, path)` for reading the actual supplied node instance. It SHALL resolve declared references and public-attribute tuple paths, including inherited replacements, active legacy/build-created children, zero repetitions and omissions. Its explicit public reference adapters and scope/repetition predicates SHALL distinguish absent named targets from actual empty repetitions without exposing mutable nodes. Scoped selection SHALL stay within its actual occurrence subtree. It SHALL NOT construct replacement defaults, derive procurement from adapter provenance, or recognize node kinds by class-name strings.

#### Scenario: Fresh effective children are readable
- **WHEN** a fresh parameterized model has inherited replacements, omitted declarations and constructor-created children
- **THEN** structural selection returns only its actual active occurrences with resolved values and stable root-relative paths, without caller preparation or replacement construction

#### Scenario: Child alias points outside delegation
- **WHEN** an attribute of a delegated child aliases another root sibling
- **THEN** selection scoped to that child cannot return the sibling, and an actual zero/one-member repetition still retains its repeated selection shape

### Requirement: Preserve physical boundary uncertainty

The facade SHALL distinguish assembly hierarchy, topmost rigid candidate pieces, rigid features and flexible candidate pieces. Occurrence SHALL expose immutable path, parent_path, kind, model_type, resolved parameters, source_paths and declared sheet_thickness_mm/nominal_dxf compatibility facts without materializing geometry; GeometryFacts SHALL expose content_id, artifact_sha256, artifact_kind, size_mm, optional volume_mm3 and watertight. Rigid ingredients, markings and frames SHALL NOT become independent piece obligations. Candidate coverage SHALL NOT certify that an assembly of geometric patches represents separate handled parts.

#### Scenario: Fusion and flexible boundaries coexist
- **WHEN** an assembly contains a fusion of three rigid ingredients alongside a separate flexible wire
- **THEN** it supplies one rigid candidate and one flexible candidate, while retaining hierarchy and excluding the ingredients from independent piece counts

#### Scenario: Author BOM contradicts patch boundary
- **WHEN** the Curta RetainingSpring is one author-BOM item but represented by multiple rigid and flexible patches
- **THEN** the partial production retains that unresolved reconciliation explicitly and does not certify whole-machine completeness from terminal coverage

### Requirement: Structure reading preserves running state

Structural access SHALL use core-owned rest-only reading with normal result validation and linking, without simulation, geometry materialization, SCAD presentation or marking generation. It SHALL preserve public state, driver bindings and established motion semantics. Unsupported legacy stateful structure SHALL be refused contextually rather than simulated or assigned invented defaults. Native artifact reading SHALL be a separate demand and SHALL preserve current runtime banks or refuse an unsupported path.

#### Scenario: Read an advanced machine
- **WHEN** structure is read twice from a machine already advanced to a nondefault running state
- **THEN** its states, driver bindings and established operation values remain unchanged, no simulate/materialize hook is called, and both occurrence sets agree

### Requirement: Facts and artifact copies use a coherent generation

The facade SHALL verify consumed source identity and existing source currency, derive geometry identity/facts from coherent pinned artifacts, and pair copied bytes with those exact facts. Public input observation, validation, hashes and executed-code provenance SHALL let a consumer share its profile/evidence inputs with this same invalidation boundary. Changed loaded sources SHALL refuse further reads rather than combine old classes with new bytes. Same-size restored-mtime artifact replacement SHALL invalidate weaker caches. A source state whose executed bytes cannot be verified SHALL carry explicit unverified provenance, never a verification claim.

#### Scenario: Artifact replaced during copying
- **WHEN** an artifact is replaced between geometry observation and copying
- **THEN** the consumer receives a coherent fact/byte pair or a contextual retry/refusal, never mismatching content
