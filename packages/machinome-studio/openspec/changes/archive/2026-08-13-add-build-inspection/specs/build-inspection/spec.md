## ADDED Requirements

### Requirement: The Build area presents the published distinct-piece inventory
The shop SHALL provide an interactive Build workspace area that reads the current framework-published `pieces` inventory from the project's completed `viewer.json`. It SHALL list each distinct piece once, identify it by its published id, show its published name, required instance count, size, volume, watertightness, sources, and models, and SHALL NOT infer replacement identity or geometry facts. The required count SHALL be visually explicit even when it is one.

#### Scenario: Repeated geometry appears once with its quantity
- **WHEN** a completed publication reports one piece whose count is sixteen
- **THEN** Build lists one distinct piece, selects one representative STL for inspection, and prominently tells the maker to print sixteen copies

#### Scenario: A legacy publication has no inventory
- **WHEN** the completed `viewer.json` contains no published `pieces` list
- **THEN** Build explains that no piece inventory is available while the other workspace areas remain usable

### Requirement: A maker inspects one representative piece on a fixed build volume
The Build viewport SHALL render one representative STL for the selected distinct piece against a scale-accurate 250 × 210 mm virtual bed and 250 × 210 × 220 mm build volume. It SHALL provide orbit, zoom, and reset interaction and SHALL label the fixed build volume. The viewport SHALL show one representative mesh regardless of required quantity.

#### Scenario: A maker selects a repeated piece
- **WHEN** the maker selects a piece with a required count greater than one
- **THEN** the viewport shows one representative mesh at truthful scale on the fixed bed and the surrounding Build facts continue to show the full required count

#### Scenario: A maker changes the selected piece
- **WHEN** the maker selects another published piece
- **THEN** the viewport loads that piece's canonical published STL and resets framing to include the bed and piece

### Requirement: Build reports only supported manufacturing facts
The Build area SHALL report the published size, volume, watertightness, count, and provenance. It SHALL report whether the size bounding box can fit within the fixed 250 × 210 × 220 mm envelope under an orthogonal axis permutation. It SHALL describe this as envelope fit and SHALL NOT present the result as a printability guarantee. It SHALL NOT report print time, material mass, support requirements, recommended orientation, slicer settings, or automatic layout.

#### Scenario: A piece fits under an axis permutation
- **WHEN** a piece's published extents fit within 250 × 210 × 220 mm under at least one permutation
- **THEN** Build reports that the piece fits the fixed build envelope without recommending a print orientation

#### Scenario: A mesh is not watertight
- **WHEN** the framework publishes `watertight` as false for a piece
- **THEN** Build displays that fact independently of the envelope-fit result

### Requirement: Build follows atomic model publications
Build SHALL load the current piece inventory on entry and SHALL reconcile it after a `viewer.json` publication or live-state reconnection through the workspace's existing lifecycle connection. It SHALL retain selection by stable piece id when that id remains published and otherwise select the first published piece. A failed rebuild SHALL leave the last completed inventory and representative STL inspectable while displaying the rebuild error.

#### Scenario: The selected piece survives a rebuild
- **WHEN** a new atomic publication still contains the selected piece id
- **THEN** Build refreshes its facts and model reference while retaining that selection without opening another lifecycle connection

#### Scenario: A rebuild fails after a completed inventory
- **WHEN** the project watcher reports a rebuild failure after Build has loaded a completed publication
- **THEN** Build keeps the prior completed pieces inspectable and displays the rebuild failure

### Requirement: A maker downloads deterministic print instructions and distinct STLs
The shop SHALL provide a session-scoped Build download whose ZIP contains `README.md` and exactly one canonical STL for every distinct published piece. The README SHALL deterministically list each STL filename and the required number of copies to print, SHALL identify the fixed 250 × 210 × 220 mm inspection envelope, and SHALL contain no timestamps, machine-local paths, slicer instructions, or unsupported manufacturing estimates. Archive entry names, order, metadata, and README content SHALL be deterministic for an unchanged publication and unchanged STL bytes.

#### Scenario: A maker downloads a repeated-piece package
- **WHEN** the current publication contains one piece used sixteen times and another used once
- **THEN** the ZIP contains two STL files plus `README.md`, and the README tells the maker to print sixteen copies of the first file and one copy of the second

#### Scenario: The published package is unchanged
- **WHEN** the maker downloads twice without a changed publication or changed referenced STL
- **THEN** both downloads have byte-identical ZIP contents

#### Scenario: A published model reference is unsafe or unavailable
- **WHEN** a piece's canonical model reference escapes the artifact root, is not an STL, or does not name a readable file
- **THEN** the shop rejects package creation and does not substitute another identity or artifact
