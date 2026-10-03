## MODIFIED Requirements

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

#### Scenario: A project declares no profile
- **WHEN** the maker views a hub whose working folder holds a project that declares no profile
- **THEN** that project is listed under `openspec`, the shop default it would open under

#### Scenario: The working folder holds a folder of projects
- **WHEN** the maker views a hub whose working folder holds a directory containing project repositories
- **THEN** that directory is listed as a folder showing how many projects it holds, and its contents are not listed alongside the working folder's own entries

#### Scenario: The working folder is empty
- **WHEN** the maker views a hub whose working folder holds no project
- **THEN** the hub says so and offers to create a project

#### Scenario: The working folder contains a regular file
- **WHEN** the working folder contains a regular file such as `README.md`
- **THEN** the hub omits that file because it is not a project directory

### Requirement: The maker creates a project from the hub
The maker SHALL be able to create a project from the hub by supplying a name and
choosing a runtime profile. The project SHALL be created inside the folder the
hub is listing. The shop SHALL accept any safe direct-child directory name that
no entry of that folder already uses, without imposing a stylistic naming
convention, and SHALL require a profile choice. It SHALL report an unsafe name
or a missing profile choice before creating anything, and SHALL leave the folder
unchanged when it rejects one.

The creation sheet SHALL offer the OpenSpec and Fordesmac profiles, each with
its label and a one-line description of what it is, and SHALL open with
OpenSpec, labelled `OpenSpec`, already chosen, so a maker who does not change
the choice creates an `openspec` project. Choosing Fordesmac SHALL remain one
action.

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

#### Scenario: The sheet opens with OpenSpec chosen
- **WHEN** the maker opens the "New project" sheet
- **THEN** OpenSpec is offered, labelled `OpenSpec` with a one-line description, and already chosen, and Fordesmac is offered beside it

#### Scenario: The maker keeps the preselected profile
- **WHEN** the maker supplies an unused valid name and creates the project without changing the profile choice
- **THEN** the provisional card shows the project as creating under `openspec`, and the created project's `pyproject.toml` declares `profile = "openspec"`

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
