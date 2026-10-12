## ADDED Requirements

### Requirement: The movie package ships its Python and its Node side

The repository's distribution `machinome-movie`, at
`packages/machinome-movie/`, SHALL ship the package `machinome.movie`, a
portion of the `machinome` namespace: the declarations a project writes a
movie in, their evaluation to the movie document `machinome-movie/0.2`, its
schema, the command module `machinome.movie.cli`, and, as package data in
`machinome/movie/js/`, what the Node side's verbs run: `package.json`, its
own `package-lock.json`, `bin/videomaker.mjs`, `src/`, `stage/`, `player/`,
`transport/` and `schema/`, their tests excepted. Its wheel SHALL carry no
test, fixture, script, test configuration or `node_modules`. The package
SHALL declare `movie = "machinome.movie.cli:Movie"` in the entry-point group
`machinome.commands`, and its root SHALL read each name it exports from that
name's module on first use. No module named `machinome_movie` SHALL be
provided. The framework SHALL NOT import the package.

#### Scenario: The wheel carries what the verbs run

- **WHEN** the package's wheel is built
- **THEN** it holds `machinome/movie/` with its modules, `cli.py`, the schema
  as a regular file and `js/` with `package.json`, `package-lock.json`,
  `bin/videomaker.mjs` and the sources of `src/`, `stage/`, `player/`,
  `transport/` and `schema/`, and no file under `js/test/`, `js/fixtures/`
  or `js/scripts/`, no `*.test.*` and no `node_modules`

#### Scenario: A project declares a movie at the new address

- **WHEN** a project's movie module imports `from machinome.movie import
  Movie, Chapter, Shot`
- **THEN** the names are those the package exports, and `import
  machinome_movie` raises `ModuleNotFoundError`

### Requirement: The Node side runs on the user's Node

The verbs of `machinome movie` that run the Node side SHALL run
`machinome/movie/js/bin/videomaker.mjs` of the installed package with the Node
named by the environment variable `MACHINOME_NODE` when it is set, else the
`node` on the PATH, whose version SHALL be 22 or newer; the working
directory, the environment and the standard streams SHALL be the user's, and
the command SHALL exit with the Node process's status. When no Node is found,
when the one found cannot run, or when it is older than 22, the verb SHALL
write one line naming what it found and how to name another, and exit 1.
When the Node dependencies are not installed in `js/node_modules`, the verb
SHALL write one line naming `machinome movie setup`, or, where the directory
is a member of an npm workspace, `npm ci` in that workspace's root, and exit
1.

#### Scenario: Node is older than 22

- **WHEN** `MACHINOME_NODE` names a Node that reports v20 and a user runs
  `machinome movie setup` or a film verb
- **THEN** one line names that Node and its version and asks for Node 22 or
  `MACHINOME_NODE`, and the command exits 1

#### Scenario: The dependencies are not installed

- **WHEN** a user runs `machinome movie check film.yaml` before `machinome
  movie setup`
- **THEN** the command writes "the Node dependencies of machinome movie are
  not installed; run: machinome movie setup" and exits 1

### Requirement: Setup installs the Node dependencies into the package

`machinome movie setup` SHALL install the Node side's runtime dependencies
into `machinome/movie/js/node_modules/` of the installed package, with the
npm beside the Node it found or on the PATH, from the package's own
`package-lock.json` (`npm ci --omit=dev`), writing nothing outside that
directory and nothing into a cache of its own; it SHALL print where it
installs, then Playwright's command that installs Chromium, and say that
FFmpeg is the system's. `machinome movie setup --remove` SHALL delete that
`node_modules` directory. Both SHALL refuse, writing one line and exiting 1
before writing anything, when the JavaScript directory is a member of an npm
workspace (a source checkout, whose dependencies the workspace's `npm ci`
installs) and when a `node_modules` from that directory up to the filesystem
root is a symbolic link, naming it.

#### Scenario: Setup in an installed environment

- **WHEN** `machinome-movie` is installed from its wheel and a user runs
  `machinome movie setup`
- **THEN** the runtime dependencies are in
  `site-packages/machinome/movie/js/node_modules/`, the Chromium line is
  printed, and a film verb then reaches Node

#### Scenario: Setup in the repository's checkout

- **WHEN** `machinome movie setup` runs from an editable install whose
  JavaScript directory is a member of the repository's npm workspace
- **THEN** it writes that the dependencies are installed by `npm ci` at the
  workspace's root, names the root, installs nothing and exits 1

#### Scenario: Remove

- **WHEN** a user runs `machinome movie setup --remove` after `setup`
- **THEN** `js/node_modules/` no longer exists and the command exits 0

### Requirement: A source is an episode, a movie document, or a project and a movie

`machinome movie check`, `speech`, `preview`, `render`, `build` and `live`
SHALL take as their source a YAML episode, a JSON movie document, or a project
directory followed by a movie name; the options they take SHALL be those the
Node side's verbs take, `--viewer` excepted: `--width`, `--fps` and
`--silent`, and for `live` `--width`, `--port`, `--poll` and `--open`. A
project and a movie name SHALL be evaluated first, as `machinome movie
evaluate` evaluates them, the document written to the movie's `_build/
movie.json` and its path printed, and the Node side SHALL be given that
document. A directory without a movie name, or a movie name after a file,
SHALL be refused naming the form, and a movie whose project needs an absent
extra SHALL be refused naming the extra, exit 1. `machinome movie list`,
`evaluate` and `watch` SHALL take a project directory, and `evaluate` and
`watch` a movie name, and run in Python; `review` SHALL take a rendered
film's manifest.

#### Scenario: A project and a movie name

- **WHEN** a user runs `machinome movie check <project> addition`
- **THEN** the movie `addition` is evaluated to its `_build/movie.json`, its
  path is printed, and the Node side checks that document

#### Scenario: A movie whose model lacks its extra

- **WHEN** the project's model needs the `cadquery` extra, which is not
  installed, and a user runs `machinome movie preview <project> tour`
- **THEN** one line names the extra and the command exits 1, with no
  traceback

### Requirement: The films are drawn by the installed viewer

`machinome movie check`, `preview`, `render`, `build` and `live` SHALL give
the Node side the bundle of the browser viewer installed beside the framework,
the path the `machinome.viewer` entry point reports, as `machinome develop`
finds it; the command SHALL take no option naming a bundle. When no viewer is
installed, or the installed one reports no bundle, those verbs SHALL write one
line with the viewer's remedy and exit 1. `speech` and `review` SHALL run
without a viewer.

#### Scenario: No viewer installed

- **WHEN** `machinome-viewer` is not installed and a user runs `machinome
  movie check film.yaml`
- **THEN** standard error holds "Error: machinome movie check needs the
  browser viewer: " followed by the remedy naming `pip install
  "machinome[viewer]"`, and the command exits 1

#### Scenario: The installed viewer draws the film

- **WHEN** a user runs `machinome movie preview <project> <movie>` with the
  viewer installed
- **THEN** the Node side mounts the bundle the viewer's report names, and a
  film that needs a newer viewer API is refused naming the installed one and
  how to upgrade it
