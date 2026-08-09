# shop-project-hub Specification

## Purpose

Present the shop's working folder as a project hub where the maker can inspect,
create, and open projects while seeing project and backend readiness.

## Requirements

### Requirement: The shop opens on the project hub
The shop SHALL start without a project and SHALL present the maker with a
project hub as the first thing they see. The hub SHALL be reachable for as long
as the shop is running, whether or not any project is open, and SHALL identify
the working folder that holds the shop's projects. The maker SHALL NOT be
required to name a project, a profile, or any other project choice before the
shop is usable.

#### Scenario: The maker starts the shop
- **WHEN** the maker starts the shop
- **THEN** the shop becomes available and presents the project hub, naming the working folder it will list projects from

#### Scenario: The maker returns to the hub with projects open
- **WHEN** the maker reaches the hub while one or more projects are open
- **THEN** the hub is presented with those projects shown as open

### Requirement: The hub lists everything in the working folder
The hub SHALL list every project directory the working folder contains,
whether or not it can be opened, and SHALL identify each one by name. For each
listed project the hub SHALL show whether it is currently open, the profile it
would open under, and enough recorded history for the maker to tell projects
apart. The hub SHALL NOT omit a directory the maker put in the working folder.

#### Scenario: The working folder holds projects
- **WHEN** the maker views a hub whose working folder holds several projects
- **THEN** every one of them is listed with its name, its open state, and the profile it would open under

#### Scenario: The working folder is empty
- **WHEN** the maker views a hub whose working folder holds no project
- **THEN** the hub says so and offers to create a project

#### Scenario: The working folder contains a regular file
- **WHEN** the working folder contains a regular file such as `README.md`
- **THEN** the hub omits that file because it is not a project directory

### Requirement: A project that cannot be opened says why
A listed project that the shop cannot open SHALL be presented as unopenable
together with the reason it cannot be opened, and the maker SHALL NOT be able to
attempt opening it. An unopenable project SHALL NOT prevent the hub from being
presented, prevent other projects from being listed, or prevent any other
project from being opened.

#### Scenario: A directory is not its own repository
- **WHEN** the working folder holds a directory that is not the root of its own Git repository
- **THEN** the hub lists it as unopenable and states that it is not a project repository, and every other project remains listable and openable

### Requirement: The maker creates a project from the hub
The maker SHALL be able to create a project from the hub by supplying a name and
choosing a runtime profile. The shop SHALL accept any safe direct-child
directory name that no entry of the working folder already uses, without
imposing a stylistic naming convention, and SHALL require a profile choice. It
SHALL report an unsafe name or a missing profile choice before creating
anything, and SHALL leave the working folder unchanged when it rejects one.

On acceptance the shop SHALL create the project and SHALL open it, so creation
and opening are one action for the maker. As soon as creation is accepted, the
sheet SHALL close and the hub SHALL show a provisional card saying that the
project is being created. That card SHALL remain visible until the project opens
or creation fails, including to a hub browser that connects while creation is in
progress.

#### Scenario: The maker creates a project
- **WHEN** the maker supplies an unused valid name and chooses a profile
- **THEN** the sheet closes, a provisional card shows the project as creating, and the shop creates that project under the working folder and opens it under the chosen profile

#### Scenario: Another browser reaches the hub during creation
- **WHEN** project creation has been accepted but its directory and session are not ready yet
- **THEN** that browser's initial hub state includes the provisional project with its chosen profile and `creating` state

#### Scenario: The name is already taken
- **WHEN** the maker supplies a name that an entry of the working folder already uses, including an entry listed as unopenable
- **THEN** the shop refuses the name, says what it collides with, and creates nothing

#### Scenario: The name is not a usable project name
- **WHEN** the maker supplies an empty name, a dot component, or a name containing a path separator
- **THEN** the shop refuses the name before creating anything and explains what a project name may be

#### Scenario: The name does not follow the shop author's convention
- **WHEN** the maker supplies a safe name containing an underscore, uppercase character, or whitespace
- **THEN** the shop accepts the name without presenting a naming-convention warning

### Requirement: The hub reports which agent backends are present
The hub SHALL report, for every agent backend the shop supports, whether that
backend was found on this machine and — when it was found — enough detail to
identify what would run: its executable, its version, and the model it is
configured to use. This report SHALL be observation only: the hub SHALL NOT
offer to enable, disable, install, relocate, or manually re-detect a backend.

#### Scenario: Some backends are installed
- **WHEN** the maker views the hub on a machine where some supported backends are installed and others are not
- **THEN** each supported backend is listed as found or missing, and each found one shows its executable, version, and configured model

### Requirement: The hub lays out project cards for the available width
The hub SHALL present project cards at a useful density without making them
too wide on a full-HD display. It SHALL use four columns at viewport widths of
1500 pixels and above, three columns at ordinary desktop widths, two columns at
900 pixels and below, and one column at 700 pixels and below. Project cards and
the new-project tile SHALL have a minimum height of 252 pixels, and project
cards SHALL reserve 158 pixels for the model preview.

#### Scenario: The maker views the hub on a full-HD display
- **WHEN** the hub viewport is at least 1500 pixels wide
- **THEN** the project grid presents four equal-width columns with cards at least 252 pixels tall and 158-pixel model previews

#### Scenario: The hub narrows
- **WHEN** the hub viewport crosses the 900-pixel or 700-pixel responsive boundary
- **THEN** the grid reduces to two or one column respectively without changing the card height or preview allocation
