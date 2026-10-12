# Evidence: `commands-contributed-by-packages`

A framework cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root): no import and no
merge. Worktree `machinome/WTs/v0.9-joins-command-seam`, branch
`v0.9-joins-command-seam`, cut from the line `v0.9-joins` at 484a528f (the
line's head after `join-mechanics`). Planning commit 766e78c1, ratified by
the orchestrator on 12 October 2026, every recommendation of design.md's Open
Questions accepted. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv, synced from the lock, 13
editable members), the OpenSpec CLI 1.6.0. Every command ran with `env -C
<dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-command-seam` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C4-apply/`.
The tests ran from `<bench>/packages/machinome` on the bench venv
(`PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p
no:cacheprovider ...`), one pytest process at a time. Logs are in
`<scratch>`, never in the bench. The fake distributions of the tests are
written under temporary directories, never under the bench; nothing of the
suite's environment is installed or uninstalled.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
766e78c1 Propose commands-contributed-by-packages: an installed package adds a command to machinome through an entry-point group
484a528f Implement join-mechanics: the mechanics helpers as the distribution machinome-mechanics, imported as machinome.mechanics
076b566d Join machinome-mechanics: its whole history at its final paths
$ git -C <bench> status --short | wc -l
0
$ <bench>/.venv/bin/python -c "import importlib.metadata as m; print(len(m.entry_points(group='machinome.commands')))"
0
```

### 1.2 The CLI modules' base (task 1.2)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_cli_lazy_imports.py tests/test_cli.py
SKIPPED [1] tests/test_cli_lazy_imports.py:172: machinome-viewer not installed
37 passed, 1 skipped, 31 subtests passed in 7.39s
```

As design.md probe 8 states. The suite's base, from `join-mechanics`'s
evidence and not rerun: 4838 passed, 24 skipped, 7505 subtests.

### 1.3 The lint base (task 1.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome/cli.py tests/test_cli_lazy_imports.py tests/test_cli.py | wc -l
6
```

Two in `machinome/cli.py` (E501 at lines 128 and 205, the reference help and
the directory refusal) and four in `tests/test_cli_lazy_imports.py` (E128 at
93 to 95, E501 at 118); none in `tests/test_cli.py`.

### 1.4 The timing base (task 1.4)

design.md probe 3's script copied to `<scratch>/probe_wall.py`, median of ten
whole invocations, the page cache warm:

```
$ env -C <scratch> <bench>/.venv/bin/python <scratch>/probe_wall.py <bench>/.venv/bin/machinome
python -c pass: median 34 ms, min 27, max 40
python -c "import machinome.cli": median 47 ms, min 39, max 57
python -c "import importlib.metadata as m; m.entry_points(group=...)": median 102 ms, min 90, max 120
machinome -h: median 902 ms, min 829, max 945
machinome viewer: median 121 ms, min 115, max 136
machinome build -h: median 262 ms, min 252, max 277
machinome vet -h: median 60 ms, min 50, max 69
machinome frobnicate: median 56 ms, min 50, max 70
```

Against design.md's 825, 53, 224 and 54 ms: `-h` 902, `vet -h` 60, `build
-h` 262 and `frobnicate` 56 ms on this run; the machine is slower by about 10
to 15 percent on the two long paths than when the proposer measured.

## 2. Red first

No edit to `machinome/cli.py` in this group.

### 2.1 The helper (task 2.1)

`tests/contributed_commands.py`: `write_distribution(root, dist, entries,
module_path, source)` writes `<dist>-0.0.0.dist-info` (the name's hyphens
made underscores) with `METADATA` and `entry_points.txt` under
`[machinome.commands]`, and the module's source; `FAKES` holds the nine
fakes of design.md Decision 8's table, each module a top-level
`machinome_fake_*` but the portion's, `machinome/fake_portion_command.py`
with no `__init__.py` above it; `distributions(*fakes)` gives a probe's
environment, `PYTHONPATH` with `REPO_DIR` first and one temporary directory
per fake; `installed(*fakes)` prepends the directories to `sys.path`, calls
`importlib.invalidate_caches()`, and on exit takes them off, forgets the fake
modules and invalidates again. Every directory is a `tempfile` directory,
removed on exit.

### 2.2 `tests/test_cli_contributed.py` on the base (task 2.2)

Thirteen tests, design.md Decision 8's 1 to 13, each naming its scenario in
its docstring:

| # | Test | Scenario |
| --- | --- | --- |
| 1 | `test_help_lists_contributed_commands_after_the_framework` | A contributed command is listed |
| 2 | `test_a_contributed_command_runs_with_its_own_verbs` (three subtests) | A contributed command runs; A later argument spells a framework command |
| 3 | `test_a_second_contributor_runs` | A contributed command runs |
| 4 | `test_a_command_shipped_as_a_namespace_portion_runs` | A contributed command runs |
| 5 | `test_a_contributed_command_operates_on_a_node` | A contributed command operates on a node |
| 6 | `test_a_framework_command_reads_no_entry_point` | A framework command reads no entry point (`cli-startup-cost`) |
| 7 | `test_an_unknown_name_names_the_contributed_commands` | the unknown name's error (`cli-startup-cost`) |
| 8 | `test_the_legacy_grammar_reads_the_contributed_names` | Legacy grammar with a contributed command |
| 9 | `test_a_framework_name_is_never_taken` | A contributed name is a framework command's |
| 10 | `test_a_name_two_packages_contribute_runs_neither` | Two packages contribute one name |
| 11 | `test_a_command_lacking_its_extra_is_answered_by_it` | A contributed command lacks its extra |
| 12 | `test_a_class_not_meeting_the_contract_is_refused` | A contributed class does not meet the contract |
| 13 | `test_a_module_that_cannot_be_imported` | A contributed module cannot be imported |

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rfEs --tb=line tests/test_cli_contributed.py
14 failed, 2 passed in 4.77s
```

Fourteen failures: eleven tests and test 2's three subtests. Each red's
reason, as the run printed it (`<scratch>/red_contributed.out`; the probe's
`prog` is `-c`):

- 1: `'{build,develop,test,snapshot,new,export,viewer,models,import-step,vet,movie,skills}' not found`: neither is listed.
- 2: `movie build film.yaml` exits 2 with "The CLI grammar changed in 0.4:
  commands come first. ..."; `movie list build` and `movie render film.yaml`
  exit 2 with "invalid choice: 'movie' (choose from 'build', ..., 'vet')".
- 3: exit 2, "invalid choice: 'skills'".
- 4: exit 2, "invalid choice: 'portioned'".
- 5: `SystemExit: 2`, "invalid choice: 'measure'", without the spellings.
- 7: `'movie' not found` in the error, which names the ten.
- 8: stderr is "invalid choice: 'film.yaml'", not the migration hint.
- 9: `'' != "Warning: fake-shadow contributes the command build ..."`: no
  warning on standard error.
- 10: `2 != 1`, "invalid choice: 'movie'".
- 11: `2 != 1`, "invalid choice: 'needy'".
- 12: `2 != 1`, "invalid choice: 'bare'".
- 13: `-h` does not hold "gone (unavailable: fake-gone
  (machinome_fake_gone:Gone) cannot be loaded: ModuleNotFoundError: ...".

Green, as expected: 6, the guard (`vet -h` with `fake-movie` installed
imports neither `importlib.metadata` nor the fake module; design.md probe 7).
The second "passed" is test 2's container, whose three subtests failed.

### 2.3 `tests/test_cli_lazy_imports.py` on the base (task 2.3)

Added: `CONTRIBUTED_GROUP`, `no_contributed_commands` (the patch of test 17)
and its probed form `NO_CONTRIBUTED_COMMANDS`, the module-level
`contract_failures(entry, group)` written without `machinome.cli`; in
`RegistryConformanceTest`, `test_the_group_is_named_machinome_commands` (14),
`test_every_contributed_entry_resolves_and_honours_the_contract` (15) and
`test_the_contract_walk_reads_a_fake_distribution` (16); in
`CommandImportIsolationTest.test_importing_the_cli_loads_no_command_module`,
the assertion that `importlib.metadata` is not imported; `HelpFidelityTest`
gains a `setUp` patching `importlib.metadata.entry_points` with
`no_contributed_commands` for all its tests, and
`CommandNeedsTest.test_help_lists_import_step_without_its_extra` prefixes its
probed snippet with `NO_CONTRIBUTED_COMMANDS` (17).

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rfEs --tb=line tests/test_cli_lazy_imports.py
E   AttributeError: module 'machinome.cli' has no attribute 'COMMAND_GROUP'
FAILED tests/test_cli_lazy_imports.py::RegistryConformanceTest::test_the_group_is_named_machinome_commands
SKIPPED [1] tests/test_cli_lazy_imports.py:243: machinome-viewer not installed
1 failed, 21 passed, 1 skipped, 21 subtests passed in 6.59s
```

Red: 14, `AttributeError: COMMAND_GROUP`. Green, as expected: 15 (it walks
no entry: `entry_points(group='machinome.commands')` has 0 entries in the
bench venv), 16 (the helper was written at 2.1, so its import succeeds; it
proves the walk, not the seam), the `importlib.metadata` assertion (a guard)
and every existing test, 19 passed and 1 skipped as at 1.2.

## 3. The seam

### 3.1 `machinome/cli.py` (task 3.1)

Added: `COMMAND_GROUP = 'machinome.commands'`; `instantiate(module,
class_name)`, the one construction `resolve_command` and the contributed
resolver share; `contributed_commands()`, which imports
`importlib.metadata` in its body, sorts the group's entries by name,
distribution and value, drops an entry taking a registry name with Decision
6's warning line and keeps a name's entries together; `located(entry)`;
`unmet_term(command)`, the first unmet term in Decision 2's order;
`CommandUnavailable`, whose `str()` is the line an invocation writes and
whose `reason` the help's; `resolve_contributed(name, entries)`, refusing a
name of two distributions, an absent extra and an unmet contract, and
letting any other failure propagate; `Unlisted` and `list_contributed`, the
help path's form of the resolver, listing every failure as `(unavailable:
<reason>)`. `manage()` selects `first`, the first argument not beginning with
`-`; reads the group only when `first` is not a registry name; runs the guard
over the union; resolves a registry command as before, a contributed one
through `resolve_contributed` (its refusal written on standard error, exit 1,
before parsing), every command of both on the help path, and none otherwise;
registers the contributed names after the registry's. The `COMMANDS` comment
gains its sentence naming the group and ADR-189; the selection comment is
rewritten for the position rule. No other module of the framework changes.

The four message lines, as the tests read them:

```
Warning: fake-shadow contributes the command build (machinome_fake_shadow:Build), which is machinome's own; it is not used
Error: machinome movie is contributed by more than one package: fake-movie (machinome_fake_movie:Movie), fake-movie-two (machinome_fake_movie_two:Movie)
Error: machinome needy needs the step extra: the needy fake command needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'
Error: machinome bare: fake-bare (machinome_fake_bare:Bare) does not meet the command contract: no docstring
```

The distributions of a contested name are named in the order of their
names, so the line reads the same whatever order they were installed in.

`machinome -h` with seven fakes installed (`<scratch>/show.py`,
`<scratch>/show.out`), exit 0, its command list after `vet`:

```
    bare                (unavailable: fake-bare (machinome_fake_bare:Bare)
                        does not meet the command contract: no docstring)
    gone                (unavailable: fake-gone (machinome_fake_gone:Gone)
                        cannot be loaded: ModuleNotFoundError: No module named
                        'machinome_fake_gone')
    movie               (unavailable: contributed by more than one package:
                        fake-movie (machinome_fake_movie:Movie), fake-movie-
                        two (machinome_fake_movie_two:Movie))
    needy               (unavailable: needs the step extra: the needy fake
                        command needs cadquery, which is not installed;
                        install it with 'pip install "machinome[step]"')
    skills              Install the agent skills (a fake contributed command).
```

and the one warning line for `fake-shadow` on standard error.

### 3.2 Green (task 3.2)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rfEs --tb=short tests/test_cli_contributed.py tests/test_cli_lazy_imports.py
SKIPPED [1] tests/test_cli_lazy_imports.py:243: machinome-viewer not installed
35 passed, 1 skipped, 24 subtests passed in 14.34s
```

### 3.3 The guards' reds (task 3.3)

`machinome/cli.py` and `tests/test_cli_lazy_imports.py` were copied to
`<scratch>/guards/` before each temporary edit and copied back after it;
`git -C <bench> diff packages/machinome/machinome/cli.py | sha256sum` was
`cb4c845b...a8c` before the first edit and after each restoration, and
`cmp` confirmed the test module restored.

- **The group read on every path**: `contributed = {} if first in COMMANDS
  else contributed_commands()` made `contributed = contributed_commands()`.
  `-k test_a_framework_command_reads_no_entry_point`: 1 failed,
  `tests/test_cli_contributed.py:139: self.assertFalse(result.imported('importlib.metadata'))`,
  `AssertionError: True is not false` (`<scratch>/guards/a.out`).
- **`from importlib.metadata import entry_points` at the module's scope**
  (with `# noqa: F401`): both modules, 2 failed, 33 passed, 1 skipped:
  `test_cli_lazy_imports.py:232` (the new assertion of
  `test_importing_the_cli_loads_no_command_module`) and
  `test_cli_contributed.py:139`, each `AssertionError: True is not false`
  (`<scratch>/guards/b.out`).
- **Test 17's patch removed**: `test_top_level_help_is_byte_identical`
  given `patch.stopall()` and its comparison run inside
  `installed('fake-movie')`: 1 failed, `"usag[100 chars]p,vet,movie}\n ..."
  != "usag[100 chars]p,vet}\n ..."`: `movie` listed (`<scratch>/guards/c.out`).
  With the patch kept and `fake-movie` installed the same test passes (1
  passed, `<scratch>/guards/c2.out`): the patch is what holds the oracle.

### 3.4 The CLI's neighbours (task 3.4)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_cli.py tests/test_vet_isolation.py tests/test_named_models.py tests/test_supported_node_types.py tests/test_import_step.py tests/test_viewer_bundle.py
122 passed, 108 subtests passed in 11.23s
```

The same six modules with the base's `cli.py` (`git show
HEAD:packages/machinome/machinome/cli.py` written in place for the run, then
the change's copied back, the diff's checksum as above): 122 passed, 108
subtests (`<scratch>/run_34_base.out`). No test that patches `sys.argv`
changed its answer.

design.md probe 8's five (`test_cli_lazy_imports.py`, `test_cli.py`,
`test_vet_isolation.py`, `test_named_models.py`,
`test_supported_node_types.py`): 93 passed, 1 skipped, 117 subtests, the
base's 90 passed and 117 subtests and the three tests 14 to 16 this change
adds.

### 3.5 The lint (task 3.5)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome/cli.py tests/test_cli_lazy_imports.py tests/test_cli.py tests/test_cli_contributed.py tests/contributed_commands.py | wc -l
6
```

The base's six lines, moved by the insertions (`cli.py` 255 and 350,
`test_cli_lazy_imports.py` 161 to 163 and 186); none in the two new modules.

## 4. The records

### 4.1 ADR-189 (task 4.1)

`docs/adrs/BUILD/ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md`,
as design.md Decision 9 outlines it: Status Proposed (promoted to Accepted
at task 6.1, as the orchestrator directed), Date 2026-10-12, Change
`commands-contributed-by-packages` (linked at its live path until the
archive), Amends ADR-024 and ADR-168, Related to ADR-179, ADR-059 and
ADR-184; the five considered options; Decisions 1 to 7 a paragraph each with
the four message lines verbatim; the measurements of probes 2, 3 and 6; the
consequences of Decision 9. Every relative link of ADR-189, ADR-024 and
ADR-168 resolves (each link target tested with `[ -e ]`).

### 4.2 The amended ADRs and the index (task 4.2)

ADR-024 and ADR-168 each gain an "Amendment (2026-10-12)" of one paragraph,
and their status lines name ADR-189. `docs/adrs/README.md`: ADR-024's line
"amended by 119, 168, 189", ADR-168's "amended by 179, 189", and ADR-189's
line after ADR-187's, Decision 9's text with the status **Proposed** until
6.1.

### 4.3 to 4.5 The manual, the architecture and the changelogs

`docs/reference/cli.rst`: the section `contributed-commands`, "Commands from
other packages", verbatim, before "Several models in one project".
`docs/architecture.md`: in "CLI", the paragraph of Decision 9 after "every
command is listed with or without its extra."; ", the contributed ones
included" after "so it loads them all"; the Map's CLI row gains 168, 179,
189. `HISTORY.rst` (the root's, which `packages/machinome/HISTORY.rst` links
to) and `docs/project/changelog.rst`: the two bullets of Decision 9,
verbatim, after `join-mechanics`'s.

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_release_records.py tests/test_profile_documentation.py tests/test_docs_structure.py
36 passed, 1294 subtests passed in 0.76s
```

## 5. Validation

### 5.1 The manual (task 5.1)

A fresh venv, `<scratch>/seam-docvenv` (uv 0.11.8, CPython 3.12), with
`packages/machinome/docs/requirements.txt` alone (Sphinx 9.1.0,
machinome-viewer 0.8.0 from PyPI):

```
$ env -C <bench>/packages/machinome <scratch>/seam-docvenv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/seam-html
build succeeded.
$ grep -c 'id="contributed-commands"' <scratch>/seam-html/reference/cli.html
1
$ grep -o 'href="[^"]*#contributed-commands"' <scratch>/seam-html/project/changelog.html
href="../reference/cli.html#contributed-commands"
```

### 5.2 The timings (task 5.2)

`<scratch>/probe_wall.py` again on the implemented tree, then
`<scratch>/seam_wall.py` with `fake-movie` written by the helper into
`<scratch>/seam-fakes/fake-movie` and on `PYTHONPATH`, median of ten
(`<scratch>/timing_after.out`):

```
machinome -h: median 975 ms, min 900, max 1022
machinome viewer: median 115 ms, min 106, max 127
machinome build -h: median 262 ms, min 251, max 298
machinome vet -h: median 54 ms, min 49, max 88
machinome frobnicate: median 121 ms, min 105, max 129
fake-movie installed: machinome -h (exit 0): median 922 ms, min 858, max 1039
fake-movie installed: machinome vet -h (exit 0): median 58 ms, min 52, max 70
fake-movie installed: machinome build -h (exit 0): median 269 ms, min 231, max 1904
fake-movie installed: machinome frobnicate (exit 2): median 131 ms, min 111, max 280
fake-movie installed: machinome movie build film.yaml (exit 0): median 194 ms, min 123, max 473
```

Against 1.4 (902, 60, 262 and 56 ms), `-h` read 975 ms. To tell the change
from the machine's drift, the base's `cli.py` (`git show HEAD:...` written to
`<scratch>/seam-base/base_cli.py`) and the change's were run alternately in
the same loop, twenty runs each, `python -c "from <module> import manage;
manage()"` (`<scratch>/seam_interleaved.py`,
`<scratch>/timing_interleaved.out`):

```
no contributor: machinome -h: base median 918 ms, change median 991 ms
no contributor: machinome vet -h: base median 56 ms, change median 58 ms
no contributor: machinome build -h: base median 231 ms, change median 244 ms
no contributor: machinome frobnicate: base median 47 ms, change median 114 ms
fake-movie: machinome -h: base median 822 ms, change median 885 ms
fake-movie: machinome vet -h: base median 58 ms, change median 58 ms
fake-movie: machinome build -h: base median 254 ms, change median 251 ms
fake-movie: machinome frobnicate: base median 45 ms, change median 113 ms
fake-movie: machinome movie build film.yaml: base median 41 ms, change median 112 ms
```

and `-h` alone, thirty runs each, alternating which runs first
(`<scratch>/seam_help_only.out`): base median 807 ms, change 874 ms.

- `vet -h` and `build -h`: within noise (56 and 58, 231 and 244, 58 and 58,
  254 and 251 ms), as design.md probe 6 found.
- `frobnicate`: 67 and 68 ms slower, about the 57 ms the design expected.
- `movie build film.yaml`: 112 ms against the hint's 41 ms, the 122 ms of
  probe 6.
- **`-h` is not within noise on this machine: 63 to 73 ms slower** in all
  three comparisons, where probe 6 measured 848 and 838 ms. The help's module
  set is unchanged (`<scratch>/seam_help_modules.out`: 1023 modules on both
  sides, the only difference the CLI module's own name, and the same
  standard output), so the cost is the read of the group itself; measured
  in-process after every command module is imported
  (`<scratch>/seam_read_cost.out`, five interpreters), the first read costs
  25.1 to 31.5 ms and a second 20.4 to 22.9 ms, which accounts for about
  half of it. The rest is not explained by these measurements.

The proposal's measurements, made by the proposer on the bench at 484a528f
on 12 October 2026 with a scratch prototype of the seam and one contributor
installed (design.md, probe 6), were: `-h` 848 and 838 ms, `vet -h` 62 and
62 ms, `frobnicate` 55 and 112 ms, `movie build film.yaml` 50 (the hint) and
122 ms. These, measured on the implemented tree on 12 October 2026, agree
with them for every path but the help; ADR-189 states these, not the
proposal's.

### 5.5 OpenSpec (task 5.5)

```
$ env -C <bench>/packages/machinome openspec validate commands-contributed-by-packages --strict
Change 'commands-contributed-by-packages' is valid
```

### 5.3 The whole suite (task 5.3)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4854 passed, 24 skipped, 55 warnings, 7508 subtests passed in 899.32s (0:14:59)
```

(`<scratch>/seam-suite.out`.) No failure. The orchestrator's own run of the
suite on the bench, from the same directory on the same venv
(`scratchpad/runs/C4-suite.log`, ended 2026-10-12T11:51:42Z):

```
4854 passed, 24 skipped, 55 warnings, 7508 subtests passed in 889.21s (0:14:49)
```

Both runs agree. Against `join-mechanics`'s 4838
passed, 24 skipped and 7505 subtests: sixteen tests more, the thirteen of
`tests/test_cli_contributed.py` and the three of `tests/test_cli_lazy_imports.py`
(`test_the_group_is_named_machinome_commands`,
`test_every_contributed_entry_resolves_and_honours_the_contract`,
`test_the_contract_walk_reads_a_fake_distribution`), and three subtests more,
those of `test_a_contributed_command_runs_with_its_own_verbs`. The 24 skips
are the base's: 4 FreeCAD runtime not set (`tests/freecad_support.py:21`), 16
machinome-viewer not installed (14 in `tests/test_browser_renderer.py`, 1 in
`tests/test_cli_lazy_imports.py`, 1 in `tests/test_scad_presentation.py`), 1
networkx not installed (`tests/test_connectivity.py:314`), 1 jscad CLI not
installed (`tests/test_jscad_integration.py:25`), 2 vendor STEP not present
(`tests/test_step_assembly.py:426` and `:546`).

### 5.4 The tree (task 5.4)

```
$ git -C <bench> status --short
 M HISTORY.rst
 M packages/machinome/docs/adrs/BUILD/ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md
 M packages/machinome/docs/adrs/BUILD/ADR-168-the-command-table-names-the-module-a-command-needs.md
 M packages/machinome/docs/adrs/README.md
 M packages/machinome/docs/architecture.md
 M packages/machinome/docs/project/changelog.rst
 M packages/machinome/docs/reference/cli.rst
 M packages/machinome/machinome/cli.py
 M packages/machinome/tests/test_cli_lazy_imports.py
?? packages/machinome/docs/adrs/BUILD/ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md
?? packages/machinome/openspec/changes/commands-contributed-by-packages/evidence.md
?? packages/machinome/tests/contributed_commands.py
?? packages/machinome/tests/test_cli_contributed.py
```

`HISTORY.rst` is the root's, which `packages/machinome/HISTORY.rst` links
to. No `.dist-info`, no `machinome_fake_*` module and no
`fake_portion_command` outside `.venv` (`find <bench> ...`: none); the
ignored files are the suite's usual build leavings (`tests/_build*`, the
generated STEP and STL fixtures).

### 5.6 The checkpoint (task 5.6)

Reported to the orchestrator before any records closing; reviewed and
accepted on 12 October 2026 with the departures recorded above (the help's
cost; ADR-189's index line at Proposed until 6.1; a contested name's
distributions in the order of their names; `contract_failures(entry,
group)`; the `.dist-info` named with underscores). The orchestrator directed
that ADR-189 state the help's cost as measured here.

## 6. Records closing

### 6.1 The ADRs re-read (task 6.1)

ADR-189 re-read against `machinome/cli.py`: the group's name, the contract's
terms in their order, the read off the table's path, the position rule, the
union read by the guard and the choices, the listing by name, the four
message lines, the order of a contested name's distributions and the help's
`(unavailable: <reason>)` match the implementation. Its Measurements and
Consequences now state the costs measured at 5.2 (the help about 70 ms
slower, 25 to 31 ms of it the group's read, the rest unexplained, the same
1023 modules and output; a framework command within noise; an unknown name
about 67 ms slower; the contributed command 112 ms), and none of the
proposal's probe 6 numbers. Status promoted to **Accepted**; its Change link
now names the archive, `archive/2026-10-12-commands-contributed-by-packages/`;
its index line in `docs/adrs/README.md` **Accepted**. Every relative link of
ADR-189 resolves (each target tested with `[ -e ]` after the archive). The
amendments of ADR-024 and ADR-168 re-read: each holds for the
implementation as it is. `docs/architecture.md`'s CLI paragraph, help
sentence and Map row agree with the three.

### 6.2 The archive (task 6.2)

```
$ env -C <bench>/packages/machinome openspec archive commands-contributed-by-packages -y
Task status: 23/28 tasks
Warning: 5 incomplete task(s) found. Continuing due to --yes flag.
Specs to update:
  cli: update
  cli-startup-cost: update
Applying changes to openspec/specs/cli/spec.md:
  + 1 added
  ~ 2 modified
Applying changes to openspec/specs/cli-startup-cost/spec.md:
  ~ 2 modified
Totals: + 1, ~ 4, - 0, → 0
Specs updated successfully.
Change 'commands-contributed-by-packages' archived as '2026-10-12-commands-contributed-by-packages'.
```

The five incomplete tasks were 5.6 and group 6, ticked in the archived
`tasks.md` as each closed. Every scenario title of the two baseline specs
before the archive is still present after it (the scenario headings of
`git show HEAD:...spec.md` against the synced file: only additions, ten in
`cli`, two in `cli-startup-cost`). Then:

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 46 passed, 0 failed (46 items)
```

### 6.3 The plan's record (task 6.3)

The line's head holds the campaign's record at the root's
`workflow/ongoing/release-0.9.md` (3ccbb05a), which this bench, at
484a528f, does not have; the orchestrator carries the paragraph below into
its Progress section at integration.

For release-0.9.md, Progress:

> Beside the joins (12 October 2026): the framework cycle
> `commands-contributed-by-packages`, by the pilot's decision of 12 October
> 2026 ("one single machinome cli with packages contributing subcommands").
> Branch `v0.9-joins-command-seam`, planning commit 766e78c1 on 484a528f,
> ratified by the orchestrator's review with every recommendation of its
> Open Questions accepted. ADR-189, a package contributes a command through
> the group `machinome.commands`, accepted; ADR-024 and ADR-168 amended. An
> installed distribution declares `name = "package.module:Class"` in the
> entry-point group `machinome.commands`, its class meeting the framework
> commands' contract with `needs_node` declared; the command is the first
> argument that is not an option, and the group is read only when it is not
> a framework command, so a framework command's dispatch reads no entry
> point; the guard and argparse's choices read the union; `machinome -h`
> lists the contributed commands after the framework's, by name; a
> framework name is never taken (one warning line), a name two packages
> declare runs neither (exit 1 naming both), an absent extra is answered by
> it, an unmet contract refused, other failures propagate, and the help
> lists each as unavailable and exits 0. `machinome/cli.py` alone changes;
> no package declares a command yet: the videomaker (`machinome movie`), the
> skills package (`machinome skills`) and the studio (`machinome studio`)
> register at their joins. Proved by fake distributions written into
> temporary directories (`tests/contributed_commands.py`,
> `tests/test_cli_contributed.py`, thirteen tests; three more in
> `tests/test_cli_lazy_imports.py`, whose help oracle reads the group
> empty). The specs modified are `cli` (one requirement added, two
> modified) and `cli-startup-cost` (two modified). The suite green on the
> bench's uv venv (4854 passed, 24 skipped, the base's, 7508 subtests; the
> orchestrator's run the same); the manual built with warnings as errors.
> Timings against the base, alternating runs: a framework command within
> noise (`vet -h` 56 and 58 ms, `build -h` 231 and 244 ms); an unknown name
> 47 and 114 ms; `machinome -h` about 70 ms slower (807 and 874 ms), 25 to
> 31 ms of it the group's read and the rest unexplained; the fake movie
> command 112 ms. Evidence:
> `packages/machinome/openspec/changes/archive/2026-10-12-commands-contributed-by-packages/evidence.md`.

### 6.4 This record (task 6.4)

`evidence.md` is complete. The implementation commit is the
orchestrator's; the planning commit 766e78c1 is not amended; nothing is
committed by the applier and nothing is pushed.
