## MODIFIED Requirements

### Requirement: Superseded and redundant builds do not publish

Having acquired the build lock, a builder SHALL re-evaluate whether its work is still needed before rendering or publishing, using the complete per-contributor source-generation observation together with the mtime-equality and source-fingerprint rules already governing artifact currency.

- When any source identity on disk differs from the source generation represented by the builder's loaded classes, the builder SHALL publish nothing and SHALL report the same source-changed outcome an ordinary edit produces, so its lifecycle loop rebuilds from current source. Equality of the aggregate maximum mtime SHALL NOT override a contributor disagreement.
- Nor SHALL a difference of the aggregate maximum mtime stand a builder down while every contributor agrees with its own observation. A contributor that joins the source generation during assembly — a mesh, STEP, SCAD or JavaScript file a part reads, or a module a part imports — SHALL be compared with the observation taken when it joined, never with the maximum mtime of the sources the classes were loaded from, nor with the time the build started. Its timestamp relative to the loaded sources, to the build's start or to the present SHALL NOT by itself be a source change.
- When the published artifact set is already current for the loaded node, the builder SHALL publish nothing. A one-shot build SHALL report the model current; a watching builder SHALL go on waiting for the next source change rather than ending.

Currency SHALL be judged where a consumer reads artifacts — the build directory itself, which is now the only place a builder writes. Persistent artifact currency SHALL remain derived from source/artifact timestamps, the source fingerprint, and the node-scoped content fallback; the system SHALL NOT record a generation counter or source identity inside a published viewer document. The source-generation observation is process-local and certifies only whether the live classes may continue working.

#### Scenario: The newest source wins

- **WHEN** a build against older source finishes after a build against newer source has published the same project
- **THEN** the older build publishes nothing and the published model matches the newer source

#### Scenario: A contributor changes beneath the same maximum

- **WHEN** a retained builder's contributor changes while the source set's maximum mtime remains equal
- **THEN** the changed contributor's metadata identity invalidates that process-local generation and the builder publishes nothing from the old classes

#### Scenario: A contributor newer than the loaded sources joins during assembly

- **WHEN** a part's mesh file, unchanged while the build runs, is dated later than every module the builder loaded — one millisecond, one second, or later than the build's own start
- **THEN** the builder that assembles it builds and publishes in that one generation, without reporting a source change

#### Scenario: A contributor edited after it joined stands the build down

- **WHEN** a contributor that joined the source generation during assembly is replaced before the assembly phase's closing check
- **THEN** the builder publishes nothing from that generation and reports the source-changed outcome

#### Scenario: A redundant build publishes nothing

- **WHEN** a builder acquires the lock and the published artifact set is already current for its sources
- **THEN** no artifact is rendered, no publication occurs, and the outcome reports the model current

#### Scenario: A watching builder finds nothing to do

- **WHEN** a builder that watches for source changes acquires the lock and the published set is already current
- **THEN** it publishes nothing and keeps watching, and the development loop does not respawn it

#### Scenario: An ordinary change still builds

- **WHEN** a builder acquires the lock, its complete source generation is the newest on disk, and the published set is not current for it
- **THEN** it renders and publishes exactly as it does without contention
