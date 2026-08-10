## ADDED Requirements

### Requirement: A project card shows its canonical model screenshot
The hub SHALL display the project's root `screenshot.png` within the model
preview region of its card when that path is an available regular non-symlink
PNG. The image SHALL fit within the existing 158-pixel preview allocation
without changing card dimensions and SHALL have an accessible description that
identifies it as that project's model preview. A missing, unsafe, unreadable, or
failed image SHALL leave the card usable and display the existing placeholder.

#### Scenario: A closed project has a screenshot
- **WHEN** the hub lists a closed valid project with a readable regular `screenshot.png`
- **THEN** its card displays that image in the reserved model-preview region

#### Scenario: A project has no screenshot
- **WHEN** the hub lists a project without a usable `screenshot.png`
- **THEN** its card displays the model-preview placeholder and remains openable according to its normal project state

#### Scenario: A screenshot cannot be decoded
- **WHEN** the browser cannot load or decode the screenshot named by hub state
- **THEN** that card falls back to the placeholder without affecting any other project card

### Requirement: The shop serves only the exact project screenshot
The shop SHALL provide a screenshot route for valid project repositories whether
they are open or closed. The route SHALL resolve the project as an exact direct
child and independent repository root, SHALL serve only its exact regular
non-symlink root `screenshot.png`, and SHALL accept no arbitrary project-relative
path.

#### Scenario: The hub requests a closed project's screenshot
- **WHEN** the browser requests the screenshot of a valid closed project that has one
- **THEN** the shop serves that exact PNG

#### Scenario: A screenshot request names an invalid project
- **WHEN** a screenshot request names a missing, nested, non-repository, or otherwise invalid project directory
- **THEN** the shop reports no screenshot and reads no file outside a verified project root

#### Scenario: The screenshot is a symlink
- **WHEN** a project's root `screenshot.png` is a symlink
- **THEN** the shop reports no screenshot and does not follow the link
