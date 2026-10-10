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

The joints page's passage on a joint declared where a parent declares a
child SHALL say that the joint's values are read where the child finally
rests, after every rest operation the parent applies to it, so that when
one of those operations is conditional a plain value is right for one
branch only and the argument to write is a callable of the realized
parent.

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

#### Scenario: A site joint under a conditional rest placement

- **WHEN** a reader declares a joint where a parent declares a child, and
  the parent's rest placement of that child depends on a condition
- **THEN** the joints page's site passage tells them the values are read
  where the child finally rests, that a plain value is right for one
  branch only, and that a callable of the realized parent is what to write

### Requirement: The documentation build produces nothing

Building the manual SHALL require only what `docs/requirements.txt` lists:
Sphinx, its theme and the published `machinome-viewer` package, which
completes the committed exports with its widget. The Read the Docs
configuration and the CI docs job SHALL both install that file and run
Sphinx, and neither SHALL run `machinome export`, install a system package,
a Node tool or a package from a repository URL, or check out a submodule.
Every export a page embeds SHALL be committed under `docs/_exports/`.

Both builds SHALL treat warnings as errors, and the manual's Sphinx
configuration SHALL make every build nitpicky, so that a cross-reference
whose target the manual does not document, written in a page or in a
docstring the manual renders, fails the build that Read the Docs and the
CI docs job run.

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

#### Scenario: A reference names nothing the manual documents

- **WHEN** a page or a rendered docstring cross-references a target the
  manual does not document, such as a class named without its module
  where the current module does not hold it, or a docstring line napoleon
  reads as a type
- **THEN** the CI docs job's command, `python -m sphinx -b html -W docs
  <out>`, fails naming the reference, with no `-n` on its command line,
  and the suite fails if the manual's configuration stops being nitpicky
