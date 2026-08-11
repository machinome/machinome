## ADDED Requirements

### Requirement: The Code navigator presents an operable source hierarchy
The Code navigator SHALL present the project root as expanded, SHALL initially collapse every directory beneath it, and SHALL let the maker independently expand and collapse those directories. It SHALL distinguish folders, Markdown documents, PNG images, Python files, and other files with recognizable icons drawn in one monochrome visual style rather than file-type colors.

#### Scenario: The maker first opens Code
- **WHEN** the project contains files at the root and within one or more directories
- **THEN** root files and the collapsed top-level directories are visible, while no descendant of a collapsed directory is visible

#### Scenario: The maker expands and collapses a folder
- **WHEN** the maker activates a folder disclosure control twice
- **THEN** its immediate visible descendants first appear and then disappear without changing the active file

#### Scenario: The maker scans common source types
- **WHEN** the visible tree contains a directory, a Markdown file, a PNG file, a Python file, and another file type
- **THEN** each entry has its corresponding monochrome icon and no entry uses the former colored source chip

### Requirement: The Code workspace previews Git-visible PNG images safely
The shop SHALL expose a bounded, session-scoped, read-only preview for a Git-visible regular non-symlink `.png` file whose resolved path remains beneath the verified project root. The Code workspace SHALL display that image at its intrinsic aspect ratio within the available area and SHALL keep PNG previews outside the editable text buffer and save flow.

#### Scenario: The maker opens a PNG source file
- **WHEN** the maker selects a valid Git-visible `.png` file from the Code navigator
- **THEN** the Code workspace displays the image without attempting to decode it as UTF-8 text or opening it in Monaco

#### Scenario: A PNG is larger than the preview boundary
- **WHEN** the maker requests a Git-visible `.png` file whose bytes exceed the configured source preview limit
- **THEN** the shop rejects the preview without returning any file content

#### Scenario: A claimed PNG has the wrong signature
- **WHEN** a Git-visible `.png` path does not contain the PNG signature
- **THEN** the shop rejects the preview rather than serving arbitrary bytes as an image

#### Scenario: The maker selects another file after a PNG
- **WHEN** the maker opens an editable text file after viewing a PNG preview
- **THEN** the existing Monaco editing, revision, conflict, reload, and save behavior remains available for that text file
