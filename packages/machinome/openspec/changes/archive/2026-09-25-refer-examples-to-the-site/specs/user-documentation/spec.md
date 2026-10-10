## MODIFIED Requirements

### Requirement: The public motion surface is documented

The documentation SHALL document the released motion and simulation surface:
driver declaration and attribute reads, `set_state` with instance-qualified
ids, ports and `connect()`, joints and relations, instruction declarations,
controls on parts, the fixed-`dt` simulation loop, running and clocked
simulations, and scenario tests that run under both plain pytest and
`machinome test`. Every name exported by `machinome.simulation` SHALL appear in
at least one published page. Every page that embeds a model SHALL use a
committed export, so the documentation build runs no CAD stack.

#### Scenario: Setting a driver from Python

- **WHEN** a reader looks up how to move a machine from code
- **THEN** the documentation shows `set_state` with a qualified dotted id,
  states that assignment to a driver attribute is rejected, and shows the
  driver being read back as an attribute

#### Scenario: Driving a published model in the browser

- **WHEN** a reader opens the tutorial chapter on instructions
- **THEN** an embedded committed export shows per-driver sliders and
  per-instruction buttons, and the page explains the layer-scoped controls
  and breadcrumb focus

#### Scenario: Deterministic stepping

- **WHEN** a reader needs to test a machine's behavior over time
- **THEN** the documentation shows a `ScenarioTest` building a `Sim` with a
  fixed `dt`, scheduling actions and assertions by tick, and running under
  pytest and `machinome test` unmodified

#### Scenario: Operating a machine with history or memory

- **WHEN** a reader needs a machine that accumulates or remembers
- **THEN** the tutorial shows `Time.running()` with moves, a ratchet stop and
  a control on the part, then `State` with a committing relation and a
  request, and a concept page states what each execution model owns,
  publishes and refuses

## REMOVED Requirements

### Requirement: Worked examples demonstrate the released capabilities

**Reason**: The three example machines were exported from Foundry submodules
during every documentation build, and the Read the Docs build of the 0.7.0
tag stopped at the service's time limit inside the third export. The same
machines are shown live on machinome.org, which owns their pages, credits and
licences.

**Migration**: The examples page sends the reader to the Foundry on
machinome.org; see "The examples page sends readers to machinome.org".

## ADDED Requirements

### Requirement: The examples page sends readers to machinome.org

The manual's examples section SHALL be one page that embeds no model, builds
no machine and pins no external repository. It SHALL send the reader to the
Foundry on machinome.org, where the simulated machines are shown live beside
their designs, and SHALL say what a reader finds there by kind of machine and
by execution model — a posed, a running and a clocked machine — rather than
by embedding or naming a project. The manual SHALL carry no example page of
its own and no Git submodule; a page that mentions a full machine the
tutorial does not build SHALL point at the site, not at a page of this
manual.

#### Scenario: Reaching the examples

- **WHEN** a reader opens the examples page
- **THEN** it links to the Foundry on machinome.org, embeds no live model,
  and names a posed, a running and a clocked machine as kinds the reader
  finds there

#### Scenario: A page that used to point at an example

- **WHEN** a how-to or concept page refers to a full machine the tutorial
  does not build
- **THEN** it points at the Foundry on machinome.org and not at a page of
  this manual

#### Scenario: No example is pinned

- **WHEN** the repository is cloned
- **THEN** it has no `.gitmodules` and no `docs/example-*.rst` page

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists:
Sphinx, its theme and the published `machinome-viewer` package, which
completes the committed exports with its widget. The Read the Docs
configuration and the CI docs job SHALL both install that file and run
Sphinx, and neither SHALL run `machinome export`, install a system package,
a Node tool or a package from a repository URL, or check out a submodule.
Every export a page embeds SHALL be committed under `docs/_exports/`.

#### Scenario: Read the Docs builds the manual

- **WHEN** Read the Docs builds any version of the manual
- **THEN** its configuration names no build job, no apt package and no Node
  tool, installs `docs/requirements.txt` alone, and the build takes the
  time Sphinx alone takes

#### Scenario: A page embeds an export nobody committed

- **WHEN** a `.. machinome::` directive names a directory outside
  `docs/_exports/`
- **THEN** the suite fails naming the page, before any documentation build

#### Scenario: A build configuration grows a build step

- **WHEN** the Read the Docs configuration or the CI docs job gains an
  export command, a repository install, an apt package, a Node tool or a
  submodule checkout
- **THEN** the suite fails naming the file and the step

#### Scenario: The manual builds from the requirements alone

- **WHEN** a fresh environment installs `docs/requirements.txt` and builds
  the manual with warnings as errors
- **THEN** the build succeeds and every tutorial page shows its committed
  export with the viewer's widget
