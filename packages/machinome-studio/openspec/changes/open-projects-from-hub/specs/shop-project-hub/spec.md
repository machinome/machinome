## ADDED Requirements

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

### Requirement: A project that cannot be opened says why
A listed project that the shop cannot open SHALL be presented as unopenable
together with the reason it cannot be opened, and the maker SHALL NOT be able to
attempt opening it. An unopenable project SHALL NOT prevent the hub from being
presented, prevent other projects from being listed, or prevent any other
project from being opened.

#### Scenario: A directory is not its own repository
- **WHEN** the working folder holds a directory that is not the root of its own Git repository
- **THEN** the hub lists it as unopenable and states that it is not a project repository, and every other project remains listable and openable

#### Scenario: A directory carries an unusable name
- **WHEN** the working folder holds a directory whose name is not a single lowercase kebab-case name
- **THEN** the hub lists it as unopenable and states that its name cannot identify a project

### Requirement: The maker creates a project from the hub
The maker SHALL be able to create a project from the hub by supplying a name and
choosing a runtime profile. The shop SHALL accept only a name that is a single
lowercase kebab-case directory name and that no entry of the working folder
already uses, and SHALL require a profile choice. It SHALL report a rejected
name or a missing profile choice before creating anything, and SHALL leave the
working folder unchanged when it rejects one.

On acceptance the shop SHALL create the project and SHALL open it, so creation
and opening are one action for the maker.

#### Scenario: The maker creates a project
- **WHEN** the maker supplies an unused valid name and chooses a profile
- **THEN** the shop creates that project under the working folder and opens it under the chosen profile

#### Scenario: The name is already taken
- **WHEN** the maker supplies a name that an entry of the working folder already uses, including an entry listed as unopenable
- **THEN** the shop refuses the name, says what it collides with, and creates nothing

#### Scenario: The name is not a usable project name
- **WHEN** the maker supplies a name containing a path separator, a dot component, an uppercase character, or whitespace
- **THEN** the shop refuses the name before creating anything and explains what a project name may be

### Requirement: The hub reports which agent backends are present
The hub SHALL report, for every agent backend the shop supports, whether that
backend was found on this machine and — when it was found — enough detail to
identify what would run: its executable, its version, and the model it is
configured to use. This report SHALL be observation only: the hub SHALL NOT
offer to enable, disable, install, or relocate a backend. The maker SHALL be
able to ask the shop to observe again without restarting it.

#### Scenario: Some backends are installed
- **WHEN** the maker views the hub on a machine where some supported backends are installed and others are not
- **THEN** each supported backend is listed as found or missing, and each found one shows its executable, version, and configured model

#### Scenario: The maker installs a backend while the shop runs
- **WHEN** the maker installs a supported backend and asks the hub to observe backends again
- **THEN** the hub reports that backend as found without the shop being restarted
