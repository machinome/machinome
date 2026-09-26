Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/vet-the-project`, with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once, because they share `tests/_build`.

Tests are `unittest` classes, one behaviour per test. Fixture projects
live under `tests/vet_projects/<name>/`, and each carries its own
`pyproject.toml` with `[tool.machinome]`. A fixture has to be complete
on disk before the test that uses it runs, but no vet fixture is ever
imported or built. Every test in sections 2–8 must be run and seen RED
for the reason it names before the code that turns it green is written.
Record each red run and each green run in `evidence.md`.

The finding kinds are exactly: `outside-universe`, `kernel-io`,
`framework-internal`, `file-write`, `dynamic-route`, `import-system`,
`denied-dunder`, `denied-builtin`, `shadowing`, `unparseable`,
`unresolved-import`, `escaped-module`, `unresolved-reference`,
`source-absolute`, `source-escapes`, `jscad-source`. A test pins that
set.

## 0. Opening evidence

- [ ] 0.1 Confirm that `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base commit (`d791eaa`) in
  `evidence.md`.
- [ ] 0.2 Run the full suite at the base and record the counts.
- [ ] 0.3 Record in `evidence.md` the catalogue survey of 2026-09-26 that
  the proposal's table comes from: the method (every `*.py` under a
  project's `simulation/`, excluding `/.git/`, `/_build`, `/WTs/`,
  `/tests/`, `/tools/`, `/scripts/`, `/.venv/`, `test_*.py` and
  `conftest.py`), the 1,131 files, and each row's count. The pilot's
  decisions of 2026-09-26 are recorded in `design.md`'s last section;
  none is open.

## 1. Planning record

- [ ] 1.1 `openspec validate vet-the-project --strict` passes. The
  planning commit holds the change folder and `workflow/ongoing/vet.md`,
  and nothing else. No ADR is written here: an ADR is extracted after
  implementation (task 9.4).

## 2. Red first: the manifest module (`tests/test_manifest_module.py`)

- [ ] 2.1 Importing `machinome.manifest` in a fresh interpreter imports
  no `machinome.core` or `machinome.node` module and none of `numpy`,
  `trimesh`, `cadquery` or `OCP`. It is red because the module does not
  exist.
- [ ] 2.2 `machinome.core.loader.ProjectManifestError`, `MODEL_NAME`,
  `project_root` and `_find_manifest` are the same objects as
  `machinome.manifest`'s, and an error raised by
  `manifest.read_declaration` is caught by `except
  loader.ProjectManifestError`.
- [ ] 2.3 `read_declaration` returns root, manifest, models as
  `(name, reference)` pairs in declaration order, default and `named`,
  for a single-model fixture and for a named-models fixture. Every
  refusal `read_project` makes today (bad name, missing `:`, directory
  collision, unknown default, empty table, `[tool.solid-node]`) is
  raised with the same message.
- [ ] 2.4 Implement `machinome/manifest.py` and rewrite
  `loader.read_project` on top of `read_declaration`. Run
  `tests/test_named_models.py`, `tests/test_loader_references.py`,
  `tests/test_lazy_test_framework.py` and `tests/test_cli.py` and
  confirm they are green and unchanged.

## 3. Red first: fixtures, the universe and its packaging (`tests/test_vet_universe.py`, `tests/vet_projects/`)

- [ ] 3.1 Add `vet_projects` to `tests/conftest.py`'s `collect_ignore`,
  so pytest never collects a fixture's companion tests.
- [ ] 3.2 Write the fixture projects:
  - `pure_project`: a model importing `machinome`, `cadquery`, `math`,
    `fractions`, `xml.etree.ElementTree`, `os.path` and `pathlib.Path`
    and its own package, through a relative import, a dotted import and
    a package `__init__`. It includes a literal
    `stl_source = '../meshes/part.stl'` under the root, `re.compile`,
    `json.load` bound by import, a read-mode `open(path)`, and a
    companion `test_<model>.py` that imports only `machinome` and
    `unittest`.
  - One project per finding kind or rule: `outside_stdlib`
    (`subprocess`), `outside_thirdparty` (`yaml`), `kernel_io_dotted`
    (`np.load`, `cq.importers.importStep`,
    `from build123d import import_step`), `kernel_io_method`
    (`.export(...)` on a call result), `framework_internal`
    (`from machinome.core.loader import load_node`, and
    `machinome.core.builder` reached through `import
    machinome.core.expressions`), `file_write` (a write-mode literal
    `open(p, 'w')`, a `mode='a'` keyword, a non-literal mode,
    `Path.write_text` and `.mkdir`), `os_restricted` (`os.path.join` and
    `os.path.exists` and `os.listdir` pass; `os.makedirs` fails), `pathlib_allowed`
    (`Path(__file__).parent / 'x'` passes), `dynamic_eval`,
    `dynamic_importlib`, `sys_path`, `sys_modules`, `dunder_attribute`
    (`__mro__`), `dunder_literal` (`'__globals__'`), `dunder_path` (a
    package `__init__.py` running `__path__.append(...)`),
    `denied_builtin` (`input`), `bound_builtin` (a pure project whose
    file binds the built-in names itself: a class-body child
    `input = InputArbor()` used as `input.turn.drives(...)`,
    `from re import compile` then `compile(p)`, and
    `def f(help): return help`), `shadowing` (a root `json.py`),
    `unparseable`, `unresolved_import`, `escaped_module` (a symlink
    leaving the root, created by the test in a temporary copy),
    `unresolved_reference`, `source_absolute`, `source_escapes` (by `../`
    and by a symlinked directory), `computed_source_passes`
    (`step_source = os.path.join(HERE, 'x.step')` raises nothing),
    `jscad_source`, `init_on_path` (a pure model whose package
    `__init__.py` imports `subprocess`), `function_local`
    (`import tempfile` inside a function), `guarded` (`socket` inside
    `try/except ImportError`), `star_import`, `tests_scope` (a pure model
    whose companion imports `subprocess`, a package with `test.py`, and a
    `tools/fetch.py` importing `urllib` that nothing imports),
    `tests_tier` (a pure model whose companion imports `unittest`,
    `pytest` and `logging`, and a second model module that imports
    `unittest`),
    `two_models` (`clock_a` pure, `clock_b` importing `socket`, no
    default), and `side_effect` (a model that would write a marker file
    if imported).
- [ ] 3.3 Universe tests: the declaration loads, names `machinome` and
  equals `machinome.__version__`. The three member lists, the tests
  tier, the `os` restriction (`os` → `["os.path", "os.listdir", "os.scandir", "os.walk"]`), the contract
  denylist, the dynamic routes, the eleven dunders (with `__path__`),
  `denied_builtins` (`breakpoint`, `help`, `input`, and not `open`), the
  `[writes]` table and the source attributes equal design.md D3 exactly
  (spelled out in the test). `xml.etree.ElementTree` is a member and
  `xml`/`xml.sax` are not; `os.path.join` and `os.listdir` are members
  and `os.makedirs` is not. The file ships in the built wheel (checked through
  `MANIFEST.in`/package-data). Red: no package.
- [ ] 3.4 A packaging test reads `setup.cfg` and asserts a
  `[bumpversion:file:machinome/vet/universe.toml]` section whose search
  and replace are exactly `version = "{current_version}"` and
  `version = "{new_version}"`, and that the search string occurs exactly
  once in `universe.toml`. The same test reads `pyproject.toml` and
  asserts `shapely==2.1.*` among `[project] dependencies`. Red: neither
  is there.
- [ ] 3.5 Write `machinome/vet/universe.toml` and a loader for it. Add
  the bumpversion section to `setup.cfg`, and `"shapely==2.1.*"` to
  `[project] dependencies` in `pyproject.toml` (installed: 2.1.2),
  commented as a universe member the framework must install.

## 4. Red first: the resolver (`tests/test_vet_closure.py`)

- [ ] 4.1 `pure_project`: the vetted files are exactly the model, the
  modules it reaches and each package `__init__.py` on their paths, and
  the companion test is not among them.
- [ ] 4.2 One test per scenario of "Vet resolves the model closure
  statically": the package init on the path, the function-local import,
  the guarded import, the relative import followed, and the missing
  module (`unresolved-import`). Add the star import vetting every module
  in the package.
- [ ] 4.3 `outside-universe` (stdlib and third-party), `shadowing`,
  `unparseable` (with the parser's line, and a latin-1 coding cookie
  that still parses), `escaped-module` and `unresolved-reference`, each
  with its path, line, kind and name.
- [ ] 4.4 Implement `machinome/vet/resolve.py` (D4). Cite
  `browser-engine/scripts/walk-imports.py` as the ancestor in its
  docstring, and note that its scope rule is deliberately reversed.

## 5. Red first: the static assertions (`tests/test_vet_assertions.py`)

- [ ] 5.1 `kernel-io` through an alias, through `from ... import`, through
  a module prefix (`cadquery.importers`), and through a method on an
  unbound receiver. No finding for `json.load`, for a project module's
  `load`, for `np.linspace` or for `trimesh.creation.cylinder`.
- [ ] 5.2 `framework-internal` for `machinome.core.loader` by import and
  for `machinome.core.builder` through an import-bound chain, naming the
  denied module. No finding for `machinome.node`, `machinome.simulation`,
  `machinome.motion`, `machinome.exact`, `machinome.openscad` or
  `machinome.core.expressions`.
- [ ] 5.3 `file-write` for `open(p, 'w')`, `open(p, mode='a+')`,
  `open(p, mode)` with a variable mode, `opener = open`,
  `Path(p).write_text(...)` and `.mkdir()`, naming `open`, `write_text`
  and `mkdir`. No finding for `open(p)`, `open(p, 'rb')` or
  `archive.open('rb')`, and no finding for `text.replace(...)`.
- [ ] 5.4 The `os` restriction: `import os`, `from os import path`,
  `from os.path import join`, `os.path.join`, `os.path.exists`,
  `os.listdir` and `os.walk` pass; `os.makedirs`, `os.environ.get`,
  `os.system` and `from os import system` are `outside-universe` named
  `os.makedirs`, `os.environ`, `os.system`;
  `from os import *` is `os.*`. `pathlib` passes whole outside its
  mutating methods.
- [ ] 5.5 `dynamic-route` for `eval` (called and aliased), `exec`,
  `compile` and `__import__`. No finding for `re.compile`. `importlib`
  and `runpy` are reported as `dynamic-route` and not as
  `outside-universe`.
- [ ] 5.6 `import-system` for `sys.path.insert`, `sys.modules[...] = `
  and `from sys import path`, each alongside `outside-universe` for
  `sys`.
- [ ] 5.7 `denied-dunder` as an attribute, as a bare name and as a
  string literal (including inside an f-string), for each of the eleven
  names; `__path__.append(...)` in a package `__init__.py` is reported.
- [ ] 5.8 `denied-builtin` for `breakpoint`, `help` and `input`, and no
  `denied-builtin` for `open`.
- [ ] 5.9 Sources: a literal under the root passes, and so does
  `computed_source_passes`. `source-absolute`, `source-escapes` (by
  `../` and by a symlink) and `jscad-source` each raise their finding.
  `None` passes. The source file is never opened; assert this with a
  nonexistent literal that passes.
- [ ] 5.10 The tests tier: with `--tests`, `tests_tier`'s companion
  importing `unittest`, `pytest` and `logging` raises nothing; its model module
  importing `unittest` is `outside-universe` under both scopes.
- [ ] 5.11 The set of kinds any vet can emit equals the sixteen listed
  above, checked against the module's declared kind constants.
- [ ] 5.12 Implement `machinome/vet/assertions.py` (D5, D7).
- [x] 5.13 Review closure (2026-09-26), the bound-name rule of D5:
  `bound_builtin` raises no finding and is pure, red first because the
  first rule reported `denied-builtin` for `input` and `help`. Collect the
  file's bound names in one `ast.walk` pass beside `import_bindings` and
  consult them where `visit_Name` and `visit_Call` judge the built-ins.
  Re-run `tests/test_vet_command.py` and `tests/test_vet_closure.py`.

## 6. Red first: the adapters contain their sources (`tests/test_missing_source_file.py`)

- [ ] 6.1 Fixtures: in `tests/stl_project/parts.py` and
  `tests/step_project/parts.py`, an `Escaping*` leaf whose source is a
  `../` literal resolving to an existing regular file above `tests/`
  (the fixtures' project root, by `tests/pyproject.toml`), and a
  `Linked*` leaf whose source goes through a symbolic link that
  `setUpModule` creates beside it, pointing to a file in a temporary
  directory, and `tearDownModule` removes. The OpenSCAD and JSCAD cases
  write scratch projects, as the file's existing tests do, whose source
  points above the scratch root through `../` and through a symlink.
  The marking case declares `Svg` artwork above its project root.
- [ ] 6.2 Constructing each escaping leaf raises `ValueError` naming
  the class, the attribute, the declared value, the resolved path and
  the project root, whether the target exists or not, and before any
  mesh or document is read and before OpenSCAD or node is started.
  Creating the marking's class raises the same way. Red: construction
  succeeds today (or fails later, in the reader).
- [ ] 6.3 A computed source under the root
  (`os.path.join(HERE, 'part.stl')`) constructs as before, and an
  absolute `step_source` under the root is admitted.
- [ ] 6.4 A source-bound leaf declared in a module with no
  `[tool.machinome]` manifest above it, whose file exists, constructs
  as before.
- [ ] 6.5 Implement the check in `require_source_file`
  (`machinome/node/sources.py`, D10), finding the root through
  `machinome.manifest.project_root` and memoizing it per declaring
  module's real path. The four adapters and `Svg.resolve` are not
  edited.
- [ ] 6.6 Run `tests/test_missing_source_file.py`,
  `tests/test_stl_node.py`, `tests/test_step_node.py`,
  `tests/test_meta.py`, `tests/test_builder_reload_resilience.py`,
  `tests/test_markings.py` and `tests/test_build_lock.py`, and confirm every test
  that constructs a source-bound leaf is green and unchanged. A test
  that declares a source outside its root is reported to the pilot, not
  rewritten silently.

- [x] 6.7 Review closure (2026-09-26), D11: `machinome import-step`
  refuses a document outside the project its `--into` directory lies in,
  before creating or writing anything, naming the document, the root and
  the remedy, and exits 1; with `--into` in no project nothing is judged.
  Red first in `tests/test_import_step.py`
  (`ImportStepContainmentTest`). `GeneratedModelFaithfulnessTest` and the
  manifest-printing test generate against a copy of the document under
  their scratch project root. The whole file runs green.

## 7. Red first: the command and the report (`tests/test_vet_command.py`)

- [ ] 7.1 `machinome vet` in `pure_project` exits 0. The text output
  starts with the preamble naming the universe and its version, and it
  ends with the project line `pure`.
- [ ] 7.2 `--json` prints exactly one object with the specification's
  keys, and a finding appears as
  `{"path", "line", "kind", "name"}`. Two runs are byte-identical.
- [ ] 7.3 `two_models`: with no reference, both models are vetted
  despite there being no default. `clock_a` is pure, `clock_b` is not,
  and the project is not. With the reference `clock_a`, only it is
  reported. The exit statuses are 1 and 0.
- [ ] 7.4 `tests_scope`: the model is pure without `--tests` and not
  pure with it, `test.py` is vetted under `--tests`, and `tools/fetch.py`
  is never among the files.
- [ ] 7.5 Exit 2, with stderr only, for no manifest, a malformed
  manifest and a directory reference.
- [ ] 7.6 `machinome vet -h` lists `reference`, `--tests` and `--json`,
  and no `--set`. `machinome -h` lists `vet` after `import-step`. Update
  `COMMAND_ORDER` and the help oracle in `tests/test_cli_lazy_imports.py`
  deliberately, and record that the top-level help changed by exactly
  one entry.
- [ ] 7.7 Implement `machinome/manager/vet.py` and the report rendering
  in `machinome/vet/__init__.py`, and register `vet` in `COMMANDS`.

## 8. Red first: cost and isolation (`tests/test_vet_isolation.py`)

- [ ] 8.1 In a fresh interpreter, `machinome vet` over `pure_project`,
  whose model imports `cadquery`, leaves `OCP`, `cadquery`, `numpy`,
  `trimesh`, every `machinome.node` module, `machinome.core.loader` and
  every other command module absent from `sys.modules`.
- [ ] 8.2 `side_effect`: after a vet, no marker file exists and no
  module of the fixture is in `sys.modules`.
- [ ] 8.3 Vet reads no environment variable: it gives the same JSON with
  `SOLID_BUILD_DIR` set and with it unset, and with the `.env` fixture
  present and absent.

## 9. Documentation, records and completion

- [ ] 9.1 `docs/architecture.md` CLI section: one synthesis line naming
  `vet`, its universe declaration, its kernel-free manifest module and
  its limit (static, not a sandbox; reads bounded by the runtime and
  declared sources by the adapters). Add `vet` to the Map row's code and
  spec columns (`vet`), and leave the ADR number to 9.4.
- [ ] 9.2 The manual (`docs/reference/cli.rst`, a `machinome vet`
  section after `machinome import-step`), written under
  `skills/write-the-manual/SKILL.md`. It gives the synopsis, what pure
  means (reads inside the project; no write, process, network or
  dynamic import), the tiers described without restating the member
  lists (the page points at the shipped declaration), the scopes, the
  JSON shape, the exit statuses, and the limit, stated once. The pages
  that document `stl_source`, `step_source`, `scad_source`,
  `jscad_source` and `Svg` artwork state that a source outside the
  project is refused at construction. It carries no release fact other
  than through the existing substitutions, and no publication caveat.
  Its example runs on the public command only. Run
  `tests/test_docs_structure.py` green.
- [ ] 9.3 `workflow/warts.md`: add the finding that three printers
  (Metamaquina2, snappy-reprap, hangprinter) run OpenSCAD through
  `subprocess` to echo parameter values, a gap the SCAD import could
  close. Include the evidence and date it 2026-09-26. The note's other
  findings, the fetch and preparation tooling inside `simulation/` and
  fender-bender's `sys.path`, are
  project fixes and are not filed as framework warts.
- [ ] 9.4 Extract the ADR (the next free number after 147, in the BUILD
  area) once the tests confirm the final design: the universe as a
  versioned declaration, the reads decision, static closure without
  import, the three assertions with their soundness limits, the
  adapters' containment at construction, and `machinome.manifest`.
  Update `docs/adrs/README.md`.
- [ ] 9.5 Run the full suite and record the counts beside 0.2's.
- [ ] 9.6 Run `machinome vet --json` over the catalogue projects named in
  the proposal's survey, read only, and record each verdict and finding
  count in `evidence.md` against the proposal's table.
- [ ] 9.7 Sync the delta specs (`vet`, `cli`, `cli-startup-cost`,
  `stl-import`, `step-import`, `node-model`, `markings`) into
  `openspec/specs/` and archive the change. `workflow/ongoing/vet.md`
  moves to `workflow/archive/` with a pointer to the archived change.
- [ ] 9.8 The studio's `shop-skills/machinome-api/SKILL.md` gains
  `machinome vet` and the source containment in the studio repository,
  as a separate change. Nothing is done here beyond naming it in the
  completion report.
