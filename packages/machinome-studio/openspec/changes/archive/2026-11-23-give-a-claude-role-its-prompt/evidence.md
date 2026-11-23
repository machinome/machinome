# Evidence

Run from `packages/machinome-studio` on the bench's own venv, 23 November
2026, base `777631e6`.

## Red, against the unchanged backend

`python -m pytest tests/test_orchestrator.py -k "role_contract_is_session_level or every_shipped_role_holds"`:
6 failed, 1 passed.

- `test_role_contract_is_session_level_not_a_turn`: `AssertionError`, the
  text of `profiles/fordesmac/machinist.md` not found in the session
  instructions, which read "Before taking any task action, read the
  following profile prompt in full and follow it as authoritative:
  <path>/profiles/fordesmac/machinist.md".
- `test_every_shipped_role_holds_its_profile_prompt_when_it_opens`: five
  subtests failed, `foreman`, `designer`, `machinist`, `librarian` and
  `builder`, each because its prompt's text was absent.

## Green, after the change

The same selection: 2 passed, 5 subtests passed.

The studio's Python suite without the browser tests
(`python -m pytest tests --deselect tests/test_shop_lifecycle_e2e.py`):
492 passed, 1 skipped, 420 subtests passed, on its cleanest run; the one test
described below failed in two of the four whole runs.
`tests/test_shop_lifecycle_e2e.py` was not run.

One test of that suite is intermittent and was so before this change:
`test_first_delivery_reports_last_pending_status_on_readiness_timeout`
run alone sixteen times on each side, failed 6 times on the unchanged main
and 3 times on the bench. It is recorded in `workflow/warts.md`.

`tests/test_documentation.py`, `test_the_changelog_records_the_join`, went
red when the changelog gained its `Unreleased` section: it looked for the
join in the first section of the file. It now looks in the section of the
package's version, and passes with and without the new section.

## A real session

One real `claude` session per side, opened by `ClaudeBackend.open_role`
for `openspec-builder`'s Builder (model `sonnet`, effort `medium`) on a
scratch Git repository outside every repository, with the floor's tool
server attached. The delivery:

    Shop broker message:
    kind: direction
    sender: maker
    recipient: builder

    Do you hold your profile prompt? If you do, quote its first sentence
    exactly. If you do not, say why. Call no tool. One short paragraph.

Unchanged backend (framework main `777631e6`):

> No, I don't hold it yet. I was told to read the profile prompt at
> `profiles/openspec-builder/builder.md` in full before taking any task
> action. This direction said to call no tool, so I haven't read it, and I
> can't quote its first sentence without making something up.

Bench:

> Yes, I hold it. The first sentence reads: "You are OpenSpec Builder, the
> sole standing agent for the active project."

That is the first sentence of `profiles/openspec-builder/builder.md`.

The question forbade tools, so the unchanged session did not attempt the
read. What happens when it does is the originating report: in the pilot's
session on SO-ARM100 the agent answered "The profile file is outside the
project, so I can't read it with these tools."
