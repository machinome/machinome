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
The hub SHALL list every entry of the folder it is listing, whether or not it
can be opened, and SHALL identify each one by name. An entry SHALL be one of
three things: a folder the maker can enter, an openable project, or a directory
that cannot be opened. For each openable project the hub SHALL show whether it
is currently open, the profile it would open under, and enough recorded history
for the maker to tell projects apart. For each folder the hub SHALL show how
many openable projects it holds. The hub SHALL NOT omit a directory the maker
put in the folder it is listing.

#### Scenario: The working folder holds projects
- **WHEN** the maker views a hub whose working folder holds several projects
- **THEN** every one of them is listed with its name, its open state, and the profile it would open under

#### Scenario: The working folder holds a folder of projects
- **WHEN** the maker views a hub whose working folder holds a directory containing project repositories
- **THEN** that directory is listed as a folder showing how many projects it holds, and its contents are not listed alongside the working folder's own entries

#### Scenario: The working folder is empty
- **WHEN** the maker views a hub whose working folder holds no project
- **THEN** the hub says so and offers to create a project

#### Scenario: The working folder contains a regular file
- **WHEN** the working folder contains a regular file such as `README.md`
- **THEN** the hub omits that file because it is not a project directory

### Requirement: A project that cannot be opened says why
A listed entry that the shop can neither open nor enter SHALL be presented as
unopenable together with the reason, and the maker SHALL NOT be able to attempt
opening it. An unopenable entry SHALL NOT prevent the hub from being presented,
prevent other entries from being listed, or prevent any other project from being
opened.

#### Scenario: A directory is not its own repository
- **WHEN** the folder being listed holds a directory that is not the root of its own Git repository and holds no project repository anywhere below it
- **THEN** the hub lists it as unopenable and states that it is not a project repository, and every other entry remains listable and openable

#### Scenario: A directory holds projects but is not one
- **WHEN** the folder being listed holds a directory that is not the root of its own Git repository but holds project repositories below it
- **THEN** the hub lists it as a folder the maker can enter rather than as unopenable

### Requirement: The maker creates a project from the hub
The maker SHALL be able to create a project from the hub by supplying a name and
choosing a runtime profile. The project SHALL be created inside the folder the
hub is listing. The shop SHALL accept any safe direct-child directory name that
no entry of that folder already uses, without imposing a stylistic naming
convention, and SHALL require a profile choice. It SHALL report an unsafe name
or a missing profile choice before creating anything, and SHALL leave the folder
unchanged when it rejects one.

While the hub is listing a multi-model project, whose entries are declared
models rather than directories, the shop SHALL NOT offer to create a project
there.

On acceptance the shop SHALL create the project and SHALL open it, so creation
and opening are one action for the maker. As soon as creation is accepted, the
sheet SHALL close and the hub SHALL show a provisional card saying that the
project is being created. That card SHALL remain visible until the project opens
or creation fails, including to a hub browser that connects while creation is in
progress and is listing the folder the project is being created in.

#### Scenario: The maker creates a project
- **WHEN** the maker supplies an unused valid name and chooses a profile
- **THEN** the sheet closes, a provisional card shows the project as creating, and the shop creates that project inside the folder being listed and opens it under the chosen profile

#### Scenario: The maker creates a project inside a folder
- **WHEN** the maker has entered a folder and creates a project there
- **THEN** the project is created as a direct child of that folder and is listed in it

#### Scenario: Another browser reaches the hub during creation
- **WHEN** project creation has been accepted but its directory and session are not ready yet
- **THEN** a browser listing that project's folder receives initial hub state including the provisional project with its chosen profile and `creating` state

#### Scenario: The name is already taken
- **WHEN** the maker supplies a name that an entry of the folder being listed already uses, including an entry listed as unopenable
- **THEN** the shop refuses the name, says what it collides with, and creates nothing

#### Scenario: The name is not a usable project name
- **WHEN** the maker supplies an empty name, a dot component, or a name containing a path separator
- **THEN** the shop refuses the name before creating anything and explains what a project name may be

#### Scenario: The name does not follow the shop author's convention
- **WHEN** the maker supplies a safe name containing an underscore, uppercase character, or whitespace
- **THEN** the shop accepts the name without presenting a naming-convention warning

#### Scenario: The maker is listing a multi-model project
- **WHEN** the hub is listing the declared models of a multi-model project
- **THEN** no project creation is offered there

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
900 pixels and below, and one column at 700 pixels and below. Project cards,
folder cards, and the new-project tile SHALL have a minimum height of 252
pixels, and project cards SHALL reserve 158 pixels for the model preview. A
folder card SHALL occupy one grid cell of the same size as a project card.

#### Scenario: The maker views the hub on a full-HD display
- **WHEN** the hub viewport is at least 1500 pixels wide
- **THEN** the project grid presents four equal-width columns with cards at least 252 pixels tall and 158-pixel model previews

#### Scenario: The hub narrows
- **WHEN** the hub viewport crosses the 900-pixel or 700-pixel responsive boundary
- **THEN** the grid reduces to two or one column respectively without changing the card height or preview allocation

#### Scenario: A folder is listed beside projects
- **WHEN** the folder being listed holds both folders and projects
- **THEN** folder cards and project cards share the same grid and card size

