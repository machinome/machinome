# production-assets Specification

## Purpose

Bind independent, nested production choices and attributed instructions to an
existing model, with lazy traceable BOM, stock, mass and findings plus portable
draft export. Unassigned components and unknown evidence remain explicit.

## Requirements

### Requirement: Independent typed bound productions

The bundled system SHALL expose Production from `machinome.production.profile`, Item from `.item`, typed processes from `.process` and values from their defining modules, with no root reexports or mandatory heavy dependency. Production SHALL bind a compatible supplied model without mutation or registration. Attribute names SHALL be arbitrary. Declaration errors SHALL fail at definition and wrong model types at binding. Production SHALL expose lazy bom, stock, steps, mass, findings and export directly, without evaluate or a second public plan.

#### Scenario: Two profiles share a model
- **WHEN** two productions bind the same parameterized model under different material/instruction choices
- **THEN** each has independent outputs while the model parameters, source, structure and simulation remain unaffected, and construction performs no geometry work

### Requirement: Public results are independently inspectable

The system SHALL return immutable typed records and tuples with the public members defined in the change design. BomLine SHALL expose status, quantity, occurrence_paths, declaration_paths, source_paths, finding_codes and its valid typed process/requirement/material/offer identities. Unassigned candidates SHALL each appear as quantity-one lines with process/geometry_id None, retained occurrence/source paths and unassigned status, without invented geometric/class grouping. Unsupported recipes SHALL yield invalid lines with no valid process/geometry identity and explicit requested_process/finding codes; absent targets SHALL yield quantity-zero diagnostic lines. A caller reading only bom SHALL see incomplete coverage. StockLine SHALL distinguish finished_count from optional purchased_quantity. ResolvedStep SHALL expose scope_path, subject_paths, instruction_text/path/digest. Bound Items SHALL expose target_paths, process, mass_basis and declaration_path. Finding.occurrences SHALL contain stable root-relative model paths with `.` for the root and `/` separators, and Finding.declarations SHALL identify owning production declaration paths. Independent project tests SHALL NOT require private dictionaries or node mutation to inspect these facts.

#### Scenario: Project validates a bought quantity through public records
- **WHEN** an independent Curta test selects the root BomLine with its DIN 934 M4x0.7 requirement
- **THEN** it can assert quantity seven and its seven occurrence_paths using only documented public members, with no private inventory access

#### Scenario: Partial tuple cannot resemble a complete BOM
- **WHEN** a profile covers one candidate, leaves another unassigned and declares Printed for an unsupported flexible candidate
- **THEN** bom contains the valid assigned line plus separate visible unassigned and invalid lines with stable occurrence/source paths, no invented geometry identity or valid process for either gap, and the invalid line retains the rejected recipe and finding code

### Requirement: Actual nested delegation and traceable quantity

Nested declarations SHALL bind actual compatible child instances, including repeated parameterized children, and SHALL retain hierarchy. Explicit references, repeats and tuples of references SHALL select actual active occurrences; no manual copied count SHALL replace model-derived quantity. A child subtotal or Step SHALL add no extra BOM item.

#### Scenario: Differently sized repeated children
- **WHEN** one profile delegates differently parameterized child occurrences to the same child production definition
- **THEN** each receives its actual bound values and each contributing item appears once in the consolidated root BOM with its occurrence path

### Requirement: Honest exclusive ownership

Each physical candidate SHALL have at most one ownership declaration. Sourcing a whole assembly SHALL cover its descendants as one obtained item. Delegation SHALL reserve its subtree. Overlaps SHALL produce deterministic findings naming all competitors and SHALL refuse ambiguous outputs with ProductionConflictError, while findings remains inspectable. Missing coverage and absent targets SHALL remain explicit nonfatal findings in partial outputs. Flexible candidates SHALL remain represented even when absent from the rigid inventory.

#### Scenario: Parent reaches inside a delegated subtree
- **WHEN** a parent Item selects an occurrence reserved to a child production
- **THEN** findings names both owners and ambiguous BOM/export are refused irrespective of declaration order

#### Scenario: Purchase replaces internal delegation
- **WHEN** a controlled profile selects a whole assembly with Sourced instead of delegating its internals
- **THEN** its purchased quantity counts each selected assembly once with no simultaneous internal part count

### Requirement: Complete process identity governs grouping

Manufactured lines SHALL consolidate only when canonical built content, material/stock/process, mass declaration and applicable finishing instructions agree. Sourced lines SHALL group by explicit Standard/Product and Offer, independent of visual mesh. All lines SHALL retain contributing occurrences. Manufactured bom access SHALL request required geometry; sourced-only bom, structure findings and steps SHALL avoid unnecessary geometry. BOM grouping SHALL NOT change according to earlier property reads.

#### Scenario: One mesh two materials
- **WHEN** two items share geometry but specify different materials or finishing instructions
- **THEN** they remain separate lines

#### Scenario: One product two meshes
- **WHEN** two sourced occurrences use different visual meshes but the same explicit product and offer
- **THEN** they consolidate while retaining both occurrence paths

### Requirement: Explicit stock and acquisition evidence

Printed SHALL allow unspecified material and retain that uncertainty. Cut SHALL require compatible sheet stock and the model's declared nominal-DXF capability with matching thickness, without changing the model or requiring an already-built file; lazy export SHALL ensure the required artifact through its established lifecycle. Stock SHALL distinguish finished-part count from unknown purchased-sheet quantity. Standard/Product SHALL be neutral component records; Offer SHALL name a distinct supplier listing and match its requirement by explicit catalogue assertion. No default procurement SHALL derive from STEP, color or class spelling.

#### Scenario: Curta polymer absent from evidence
- **WHEN** the author's printed-part instructions specify infill but no polymer
- **THEN** the production can report Printed with unknown material and does not invent PLA or a density

#### Scenario: Four panels lack a nesting layout
- **WHEN** four existing compatible sheet panels use Cut
- **THEN** stock reports four finished parts and unknown purchased-sheet quantity, and exports their nominal DXF without kerf compensation

### Requirement: Instructions remain local and ordered

Step subjects SHALL be declarations owned by the same profile. Markdown and mass evidence paths SHALL resolve within the declaring source directory, refusing canonical traversal/symlink escape. Nested output SHALL preserve subjects, local declaration order and child-before-parent assembly order. Referencing a subproduction SHALL mean its assembled boundary, not extra acquisition. Missing referenced files SHALL refuse requested steps/export contextually. Version 1 SHALL preserve plain Markdown, external http/https links and same-document fragments; local links/images, raw HTML dependencies, file/data URLs and unresolved referenced dependencies SHALL be refused rather than exported with broken paths. Exported project instructions SHALL retain source attribution without copying unlicensed complete manuals.

#### Scenario: A local image would break the bundle
- **WHEN** a Step Markdown contains a relative local image or reference-style local file link
- **THEN** steps/export refuses the unsupported dependency naming its declaration and source, without publishing a partial target or copying unrelated files

#### Scenario: Child and parent use the same filename
- **WHEN** two nested profiles each declare assembly.md from different source directories
- **THEN** each resolves its own file, both contents survive export and subjects retain their scopes

### Requirement: Mass retains its basis and unknown coverage

Mass SHALL default to unknown. MeasuredMass SHALL be per occurrence with local evidence. SolidMass SHALL explicitly state the homogeneous-solid basis and use positive watertight finite mm³ volume and declared density_kg_m3 to compute grams; missing density, invalid volume and unsupported flexible volume SHALL remain unknown with reasons. Infill SHALL NOT become an automatic volume multiplier. MassSummary SHALL cover the full queried subtree's candidate set, retaining unassigned/invalid candidates as unknown rather than restricting the denominator to assigned Items; a sourced assembly SHALL replace covered descendant weight with its one owner's basis. Absent targets SHALL also mark completeness false. MassSummary SHALL distinguish known subtotal from complete total and SHALL NOT mutate simulation/support behavior.

#### Scenario: Known and unknown items coexist
- **WHEN** one occurrence has measured mass and another has no valid basis
- **THEN** the summary retains the measured subtotal, marks complete false and names the unknown occurrence even if it has no Item assignment, rather than treating it as weightless

### Requirement: Deterministic lazy outputs and draft bundle

Bound assets SHALL share one coherent root/child input generation, reuse immutable valid facts and refuse changed sources/profile/instruction inputs with ProductionInputChangedError. Structural findings and unrequested check status SHALL be deterministic irrespective of access order; geometry-specific reasons SHALL belong to their requested result and the complete export checks. Export SHALL resolve required inputs automatically and publish a new portable directory atomically, refusing a nonempty destination and leaving no partial target on failure. The version-1 machinome-production manifest SHALL include identities, parameters, nested bindings, occurrence ownership, BOM, stock, steps, mass, input hashes and findings; CSV and Markdown views and explicitly consumed instruction/evidence/STL/DXF files SHALL remain traceable to it. Export SHALL state draft status and SHALL NOT claim fabrication readiness.

#### Scenario: Child-first and root-first agree
- **WHEN** callers read child properties before the root on one binding and in the opposite order on another equivalent binding
- **THEN** matching outputs and check statuses agree and neither requires explicit evaluation

#### Scenario: Curta root remains partial
- **WHEN** the Curta3x slice is exported with simulation-only mounting, unresolved retaining-spring physical boundary and made-wire recipe gaps
- **THEN** those limitations and unassigned occurrences survive in the draft bundle and no fabrication-ready whole-machine claim appears
