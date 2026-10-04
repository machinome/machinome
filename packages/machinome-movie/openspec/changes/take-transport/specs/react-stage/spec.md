## MODIFIED Requirements

### Requirement: A view on a take is posed by restoring its bank

For a view element whose frame state carries `bank`, the stage SHALL mount
its viewer instance without a loop time, attach the take transport's
machine transport to it once, with the take's identity, and keep it with
the instance; and on every frame SHALL pose the view through that
transport, which restores the whole bank on the viewer's machine handle,
`machine().restore({identity, bank})`, and then sets the camera: one
restore and one camera call per frame, as before. It MUST NOT set a loop
time for that view. The view's report SHALL carry the bank the machine
holds after the pose. `window.film.transport(key)` SHALL return the
machine transport of the instance the view element `key` holds, or `null`
for a view on a loop. At mount, the stage MUST refuse, naming the view and
the shot: a viewer that gives no machine handle for the clocked document,
and a machine whose identity differs from the take's, naming both
identities and `take.identity`. A movie on a take SHALL need Viewer API 29,
for the reason `clocked take`, and the stage's refusal of an older viewer
SHALL name it.

#### Scenario: A pose by bank
- **WHEN** the stage draws a frame of the counter whose view carries a bank
  with crank 1800 and units 5
- **THEN** the viewer's machine is restored to that bank with the
  counter's identity, the camera is set after it, no loop time is set, and
  the view reports that bank.

#### Scenario: The transport reported
- **WHEN** the stage has drawn frames of the counter at the take's start,
  inside a step and at the mark `one`
- **THEN** `window.film.transport` of the view reports, after each, the
  bank the frame carried and the take's identity, at `one` the recorded
  bank; and for a view of the fixture tour, which is on a loop, it is
  `null`.

#### Scenario: A viewer without a machine
- **WHEN** the viewer mounted for a view on a take gives no machine handle
- **THEN** the stage refuses at mount naming the view, the shot and the
  machine it lacks.

#### Scenario: Another machine
- **WHEN** the machine's identity differs from the take's
- **THEN** the stage refuses at mount naming the view, both identities and
  `take.identity`.

#### Scenario: The requirement named
- **WHEN** the movie films a take and also highlights a part
- **THEN** it needs Viewer API 29, and the refusal of a viewer declaring 28
  names `clocked take` among its reasons.

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
(the runtime and the take transport, a module or a file it reads, the
stage block, the versions of the bundler, the type checker and React),
never because of a modification time. The bundle SHALL NOT depend on where
the tool's checkout or the project lies: every file it embeds a name of
SHALL be named relative to the tool (its runtime, the take transport and
the pose rule it imports, and its packages) or to the project
repository, so the same tool content and the same project content bundle
to the same bytes, and the bundle's key SHALL be computed over those names
and the files' content, so a checkout reuses a bundle another checkout of
the same content built. A YAML episode SHALL be drawn by a bundle of the
runtime alone. `check` SHALL report the bundle it built or reused, with the
SHA-256 of its script and the SHA-256 of its stylesheet, so a change to
either shows in the line.

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
  same bytes, no name in either is a path of the machine, the script names
  the take transport `videomaker/transport/take.ts`, and the record the
  bundle's key is computed over names it and the pose rule it imports
  `videomaker/transport/take.ts` and `videomaker/src/take.mjs`.

#### Scenario: A second checkout reuses the bundle
- **WHEN** a second checkout of the same tool content bundles the stage of a
  movie whose bundle the first checkout built, unchanged since
- **THEN** it reuses that bundle and reports it as reused, with the same
  hashes.
