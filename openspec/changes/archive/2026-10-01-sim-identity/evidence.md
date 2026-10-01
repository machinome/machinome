# Evidence — `sim-identity`

Cycle 2 of the curta-film-findings bench
(`workflow/ongoing/curta-film-findings/plan.md`). Worktree
`machinome/WTs/sim-identity`, branch `sim-identity`, cut from the bench
`curta-findings` at 4d1440a. Planning commit 664a406.

## The finding

Videomaker's archived change `2026-10-01-declare-a-take`, `evidence.md`,
finding 2: the framework's `Sim` keeps the clocked machine's identity only
on the private `sim._clocked.identity`. The take check therefore compares
the recorded bank's ids with the export's drivers and states, and a law
changed under the same ids is caught only where the viewer restores the
bank with the document's identity. Filed in `workflow/warts.md`, "Three
findings from filming the clocked Curta (1 October 2026)", finding 2.

## Red first

`tests/test_clocked_identity.py` was written before any code change and run
on the unchanged tree (`env -C <worktree> PYTHONPATH=<worktree>
.venv/bin/python -m pytest -q tests/test_clocked_identity.py`):

```
FFFFF                                                                    [100%]
...
>       self.assertEqual(Sim(Counter()).identity,
                         ^^^^^^^^^^^^^^^^^^^^^^^
                         manifest['clocked']['identity'])
E       AttributeError: 'Sim' object has no attribute 'identity'

tests/test_clocked_identity.py:49: AttributeError
...
>           sim.identity
E           AttributeError: 'Sim' object has no attribute 'identity'
...
FAILED tests/test_clocked_identity.py::IdentityTest::test_different_machines_have_different_identities
FAILED tests/test_clocked_identity.py::IdentityTest::test_the_identity_does_not_move_with_the_bank
FAILED tests/test_clocked_identity.py::IdentityTest::test_the_identity_is_the_one_the_export_carries
FAILED tests/test_clocked_identity.py::IdentityRefusalTest::test_a_running_simulation_refuses_the_identity_by_name
FAILED tests/test_clocked_identity.py::IdentityRefusalTest::test_an_untimed_simulation_refuses_the_identity_by_name
5 failed in 1.52s
```

The export test reached its assertion: `export_node(built(Counter()), …)`
wrote the manifest, and the failure is the missing member, not the
fixture. The two refusal tests fail because they expect `TypeError` and
get `AttributeError`.

## Green

| Run | Summary line |
|---|---|
| `tests/test_clocked_identity.py` | `5 passed in 1.35s` |
| `tests/test_clocked_sim.py tests/test_clocked_publication.py tests/test_clocked_time.py tests/test_clocked_identity.py` | `120 passed, 38 subtests passed in 3.15s` |
| `tests/test_docs_structure.py tests/test_tutorial_counter.py tests/test_release_records.py tests/test_profile_documentation.py tests/test_clocked_identity.py`, on the final content | `26 passed, 167 subtests passed in 82.64s (0:01:22)` |
| the whole suite, first run (with the withdrawn `HISTORY.rst` section) | `1 failed, 4180 passed, 4 skipped, 53 warnings, 3076 subtests passed in 844.32s (0:14:04)` |
| the whole suite, on the final content | `4181 passed, 4 skipped, 53 warnings, 3076 subtests passed in 686.25s (0:11:26)` |

The planning commit put the changelog entry in both `HISTORY.rst`, under a
new `Unreleased` section, and `docs/project/changelog.rst`, because the
cycle brief named `HISTORY.rst`. Two pins refused the new `HISTORY.rst`
section:
`tests/test_release_records.py::test_the_history_top_entry_is_the_released_version`
(`1 failed, 8 passed, 57 subtests passed in 0.13s`) and
`tests/test_profile_documentation.py::ProfileDocumentationTest::test_released_status_changelog_and_history`.
The second was the one failure of the first whole-suite run:

```
E       AssertionError: 'unreleased' unexpectedly found in "=======\nhistory\n=======\n\nunreleased\n----------\n\n* **a clocked simulation names its machine.** ..."
FAILED tests/test_profile_documentation.py::ProfileDocumentationTest::test_released_status_changelog_and_history
```

Both pins had been corrected to allow one `Unreleased` heading. The
orchestrator then corrected the brief: the entry belongs in
`docs/project/changelog.rst` alone. The `HISTORY.rst` section and both pin
corrections were reverted to the bench's bytes, and the whole suite was run
again on the final content (design.md decision 6).

The suite memoizes verdicts across runs (ADR-156), so a memoized pass is
reported as a pass.

The strict manual build (`python -m sphinx -b html -n -W --keep-going docs
docs/_build/html`) ends `build finished with problems, 5 warnings (with
warnings treated as errors).` None of the five is this change's: they are
`api.rst` lines 23, 35 and 76 (`AssemblyNode.simulate`,
`AssemblyNode.time`, `name keyword`) and the `Sim.initial` and `Sim.state`
docstrings, all untouched by this diff. The first draft of `Sim.identity`'s
docstring added a sixth warning (napoleon read "The clocked machine's
identity: …" as a type), and the docstring was reworded until the build
was back to the five warnings it already had. The rendered `Sim.identity`
entry and the new sentence of "Clocked simulation" were read once in
`docs/_build/html/reference/api.html`.

## The caller

A five-line script in the session scratchpad
(`Sim(ClockedCurta()).identity` beside the `clocked.identity` of
`export/clocked_curta/manifest.json`). It was run from the Curta's real
path with the worktree first on `PYTHONPATH`:
`env -C /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x
PYTHONPATH=<worktree>:<project> .venv/bin/python caller.py`. The project
is at 23c9e6f, and its export is the untracked `export/clocked_curta/`,
version 8.

```
/home/asa/devel/machinome/machinome/WTs/sim-identity/machinome/__init__.py
18f8b447b410de79b8f161e0a95a02e2bdbca28207cc9b08a8679dddf84d63c7
18f8b447b410de79b8f161e0a95a02e2bdbca28207cc9b08a8679dddf84d63c7
True
```

The first line shows that the worktree's package answered. `git status
--short` of the project was identical before and after the run.

## Findings

1. **The viewer's clocked snapshot carries the identity, and the
   framework's does not.** `ClockedSnapshot` holds `model`, the root
   class's bare name and its sorted bank ids (`Counter(crank,tens,units)`),
   and `values`. `Clocked.restore` compares `model`, not `identity`. The
   export spec says the identity exists "so a bank taken against one
   machine is refused against another", and the viewer's
   `restore({identity, bank})` does refuse by it. The framework's `restore`
   accepts a snapshot from a machine whose law or range changed under the
   same class name and ids, and a snapshot from a different class of the
   same name in another module. A running `RunSnapshot` does carry
   `program.identity` and is refused by it. Left as the cut decided: the
   snapshot's shape is unchanged.
2. **Two pins forbid an `Unreleased` section in `HISTORY.rst`.**
   `test_release_records.py::test_the_history_top_entry_is_the_released_version`
   and `test_profile_documentation.py::test_released_status_changelog_and_history`
   each refuse any `unreleased` text above the released section of
   `HISTORY.rst`. Their changelog twins were relaxed by
   `persistent-verdict-memo`. Under the orchestrator's ruling, work after a
   release is recorded in the manual's changelog and not in the history, so
   these pins hold that rule. They are left unchanged.
3. **`docs/architecture.md`'s known gap "A clocked model is published but
   not yet VIEWED" is stale.** The released viewer 0.7.0 declares
   document versions 1 to 13. The gap was left as written, because it is
   not this change's subject.
4. **The strict manual build does not pass on the base.** It fails with
   five pre-existing warnings (above), so `-W` cannot be the gate it is
   meant to be until they are fixed.

## What was not done, and why

- **The snapshot's shape and `restore`'s comparison.** Out by the
  orchestrator's cut. Finding 1 records the gap.
- **An identity for untimed or running roots under this name.** No
  project asks for one. The running value is already public as
  `sim.program.identity`, and the refusal points at it.
- **No ADR.** `design.md` decision 5: what the identity is, and that a bank
  is refused against another machine by it, is ADR-128's. This change
  exposes an existing value on the public API in an existing refusal
  shape. ADR-157 is unused.
- **The viewer, Videomaker's use of the member, and the studio's
  `shop-skills/machinome-api/SKILL.md`.** These belong to other
  repositories and other hands.
- **`workflow/warts.md`.** It is the orchestrator's to triage at merge.
