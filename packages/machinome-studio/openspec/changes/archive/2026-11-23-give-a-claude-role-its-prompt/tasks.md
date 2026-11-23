## 1. Prove the failure red first

Run from `packages/machinome-studio` on the bench's own venv. Record each
red run (test, failure line) in `evidence.md` in this change directory.

- [x] 1.1 `tests/test_orchestrator.py`, `test_role_contract_is_session_level_not_a_turn`: assert the session instructions contain the text of `profiles/fordesmac/machinist.md` and no longer assert its path.
- [x] 1.2 `tests/test_orchestrator.py`, a new test over every agent of both shipped profiles (`fordesmac`, `openspec-builder`): the instructions the Claude backend builds for the agent contain its prompt file's text, do not contain the prompt's path, and do not contain "read the following profile prompt".
- [x] 1.3 Run both and record them failing because the text is absent, not for an import or fixture error.

## 2. Deliver the prompt's text

- [x] 2.1 `machinome/studio/backends/claude.py`, `_role_contract`: replace the read instruction and its path with "The following profile prompt is authoritative:" followed by `agent.prompt_path.read_text()`.
- [x] 2.2 Run the two tests green, then the whole of `tests/test_orchestrator.py` and `tests/test_role_contracts.py`.

## 3. Prove it in a real session

- [x] 3.1 Open one real `claude` session with the argv the bench's backend builds for `openspec-builder`'s Builder on a scratch project outside every repository, ask it to quote the first sentence of its profile prompt, and record the question and the answer in `evidence.md`. Record the same question against the unchanged backend beside it.

## 4. Records

- [x] 4.1 `CHANGELOG.md`, under `Unreleased`: one correction, a Claude role now holds its profile prompt.
- [x] 4.2 Read `workflow/architecture-overview.md` for a sentence that describes the Claude role reading its prompt from a path, and correct it in place if there is one. There is none: the overview's Claude paragraphs describe the process, the tool grants and the skill catalogue, and say nothing of how the prompt arrives.
- [x] 4.3 `workflow/warts.md`: record the intermittent readiness test met while running the suite.
- [x] 4.4 `tests/test_documentation.py`, `test_the_changelog_records_the_join`: find the join in the section of the package's version, so an `Unreleased` section above it does not hide it.

## 5. Validate and close the cycle

- [x] 5.1 Run the studio's Python suite from the bench; report environmental failures honestly.
- [x] 5.2 `openspec validate give-a-claude-role-its-prompt --strict`; sync the delta into `openspec/specs/`, archive the change, and create the implementation commit. Integration and push are the pilot's.
