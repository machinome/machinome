## MODIFIED Requirements

### Requirement: One stage bundle per movie, typed from the document and rebuilt by content

The tool SHALL bundle, for each movie, its own stage runtime with the stage
modules the document names into one script and one stylesheet under
`<root>/_build/stage/`, and SHALL generate from the document's stage block
the types of each project set's props and slots and each project element's
props and actions' parameters. When a module is TypeScript, the modules
SHALL be checked against those types, and a mismatch MUST be refused by
`check`, naming the module and what the check found, whether or not the
chapters' takes are cached, so it is found before `speech` is run. The
bundle SHALL be rebuilt only when the content of one of its inputs changes
(the runtime, a module or a file it reads, the stage block, the versions of
the bundler, the type checker and React), never because of a modification
time. The bundle SHALL NOT depend on where the tool's checkout or the
project lies: every file it embeds a name of SHALL be named relative to the
tool (its runtime and its packages) or to the project repository, so the
same tool content and the same project content bundle to the same bytes,
and the bundle's key SHALL be computed over those names and the files'
content, so a checkout reuses a bundle another checkout of the same content
built. A YAML episode SHALL be drawn by a bundle of the runtime alone.
`check` SHALL report the bundle it built or reused, with the SHA-256 of its
script and the SHA-256 of its stylesheet, so a change to either shows in the
line.

#### Scenario: A prop of the wrong type
- **WHEN** `stage.tsx` reads the `Jobs` prop `jobs` as a string while the
  document declares it a `list`
- **THEN** `check` refuses, naming `stage.tsx` and the prop, and nothing is
  requested from the speech provider.

#### Scenario: A touched module
- **WHEN** only the modification time of `stage.tsx` changes between two runs
  of `check`
- **THEN** the second run reuses the bundle and reports it as reused.

#### Scenario: A changed stylesheet
- **WHEN** a stylesheet `stage.tsx` imports changes, and nothing else
- **THEN** the next `check` rebuilds the bundle and its `Stage:` line
  reports the stylesheet's new hash beside the script's unchanged one.

#### Scenario: Two checkouts, two copies of the project
- **WHEN** a movie's stage is bundled by one checkout of the tool from one
  copy of the project, and by another checkout of the same tool content,
  elsewhere, from another copy of the same project content, elsewhere
- **THEN** the two scripts are the same bytes, the two stylesheets are the
  same bytes, and no name in either is a path of the machine.

#### Scenario: A second checkout reuses the bundle
- **WHEN** a second checkout of the same tool content bundles the stage of a
  movie whose bundle the first checkout built, unchanged since
- **THEN** it reuses that bundle and reports it as reused, with the same
  hashes.
