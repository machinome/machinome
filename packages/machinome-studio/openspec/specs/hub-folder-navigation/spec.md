# hub-folder-navigation Specification

## Purpose
TBD - created by archiving change browse-hub-folders. Update Purpose after archive.
## Requirements
### Requirement: The hub lists the contents of one folder

The hub SHALL list the contents of exactly one folder at a time and SHALL open
on the working folder. Everything the hub says about its listing — the count of
what it holds, the entries it lays out, and the project it offers to create —
SHALL be about the folder being listed and SHALL NOT include the contents of a
folder below it.

#### Scenario: The maker reaches the hub

- **WHEN** the maker reaches the hub without asking for a particular folder
- **THEN** the hub lists the working folder's own entries and identifies the working folder as the one being listed

#### Scenario: The maker lists a folder

- **WHEN** the maker enters a folder listed in the hub
- **THEN** the hub lists that folder's entries, and an entry held only by a folder deeper inside it is not listed

### Requirement: A directory that holds projects is a folder

A directory beneath the working folder that is not itself a project repository
SHALL be listed as a folder when at least one project repository exists
somewhere below it, and the maker SHALL be able to enter it. A directory that is
neither a project repository nor holds one anywhere below it SHALL remain listed
as an entry that cannot be opened, with the reason it cannot.

The hub SHALL NOT require the projects inside a folder to be its direct
children, and a folder MAY hold further folders to any depth.

#### Scenario: A grouping directory holds projects

- **WHEN** the working folder holds a directory that is not a repository and contains project repositories
- **THEN** the hub lists it as a folder the maker can enter, rather than as a project that cannot be opened

#### Scenario: A folder holds another folder

- **WHEN** a listed folder holds a directory that itself only holds project repositories deeper down
- **THEN** that directory is listed as a folder the maker can enter

#### Scenario: A directory holds no project at all

- **WHEN** the working folder holds a directory that is not a repository and holds no project repository at any depth
- **THEN** the hub lists it as unopenable and says that it is not a project repository

### Requirement: A project declaring several models is a folder

A project repository whose manifest declares more than one named model SHALL be
listed as a folder, and entering it SHALL list one openable project entry per
declared model, named by the name the manifest gives that model. A project
repository declaring one model, or none, SHALL be listed as a single openable
project as it is today.

A multi-model project's folder SHALL list its models and nothing else: a
directory inside such a repository SHALL NOT be listed as an entry of it.

#### Scenario: A repository declares two models

- **WHEN** the maker views a folder holding a project repository whose manifest declares two models
- **THEN** that project is listed as a folder, and entering it lists one openable entry per declared model

#### Scenario: A repository declares one model

- **WHEN** a project repository declares a single model, whether named or as the manifest's default
- **THEN** the hub lists it as one openable project card and does not present a folder

#### Scenario: A multi-model repository holds directories

- **WHEN** the maker enters a multi-model project whose repository also holds source and build directories
- **THEN** only its declared models are listed

### Requirement: Every hub entry is named by its path under the working folder

The shop SHALL identify every hub entry — folder, openable project, or
unopenable directory — by its path relative to the working folder, using the
model's declared name as the final segment of a multi-model project's entry.
That path SHALL be what the maker's browser location carries, what the shop
accepts to open an entry, and what hub state uses to name an entry.

The shop SHALL reject a path that escapes the working folder, and SHALL do so
before touching anything outside it.

#### Scenario: A nested project is opened

- **WHEN** the maker opens a project held by a folder
- **THEN** the shop opens the project at that path under the working folder, and the browser location carries the same path

#### Scenario: One model of a multi-model project is opened

- **WHEN** the maker opens a model listed inside a multi-model project
- **THEN** the shop opens that project's repository for that named model, identified by the project path followed by the model name

#### Scenario: A path leaves the working folder

- **WHEN** a request names an entry path containing a dot component or an absolute location
- **THEN** the shop refuses it without reading anything outside the working folder, and the hub remains available

### Requirement: The maker returns from a folder through the breadcrumb

While listing anything other than the working folder, the hub SHALL show a trail
naming the working folder and each folder between it and the one being listed,
in order. Each named ancestor SHALL return the maker to that folder's listing.
The folder being listed SHALL be identified in the trail and SHALL NOT act as a
link to itself.

#### Scenario: The maker lists a nested folder

- **WHEN** the maker has entered a folder two levels below the working folder
- **THEN** the trail names the working folder, the folder between, and the one being listed, in that order

#### Scenario: The maker goes back up

- **WHEN** the maker chooses an ancestor from the trail
- **THEN** the hub lists that folder

#### Scenario: The maker lists the working folder

- **WHEN** the hub is listing the working folder itself
- **THEN** the trail names the working folder alone and offers nothing to go back to

