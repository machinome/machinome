# Relicensing of 5 October 2026: Apache-2.0 to GPL-2.0-or-later OR CERN-OHL-S-2.0+

Status: done on 5 October 2026 in the framework's `main`, not pushed. This
directory is the record of a history rewrite, not of a campaign: one
operation, its script, its commit map and its verification.

## What was done

Machinome is licensed **GPL-2.0-or-later OR CERN-OHL-S-2.0+** at the
recipient's choice, with the consent of all contributors. Every release up to
0.7.1 stays Apache-2.0. The pilot decided the licence on 4 October 2026
(workspace `workflow/ongoing/machinome-license.md`) and directed that the
licence commit sit right after `origin/main` (`bf24687`, the pushed 0.7.1),
with every unpushed commit following it, so that no commit after the licence
commit carries the old grant. The release handoff
(`workflow/ongoing/release-0.8.0.md`) had listed the instruments this commit
would change and expected it to be injected into the history.

The licence commit is **f5556a61c2a583da04c648bb46d8b6c596bbf3eb**, parent
`bf24687`. The 75 commits that followed `bf24687` (8 merges among them) and
the one extra commit on each of three side branches were rewritten to carry
the same instruments, authors, dates, messages and topology unchanged. The
tip of `main` moved from `dc8067c` to **e87cf52e8fff6f18b7c5a4437bbbc25a3df86400**;
`commit-map.txt` pairs every old commit with its rewrite. `main` is a
fast-forward of `origin/main`.

## The instruments

- `LICENSE`: the dual statement; `LICENSES/GPL-2.0-or-later.txt` and
  `LICENSES/CERN-OHL-S-2.0.txt`: the full texts; `NOTICE` removed.
- `pyproject.toml`: `license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"`,
  `license-files = ["LICENSE", "LICENSES/*.txt"]`, build floor
  `setuptools>=77` (the PEP 639 form the viewer, mechanics and studio already
  use). `MANIFEST.in` includes `LICENSES/*.txt` instead of `NOTICE`.
- Every `# SPDX-License-Identifier` header (667 at the tip: 666 `.py` and
  `machinome/vet/universe.toml`), including the nine archived
  `moved-names.toml` files that had been mislabelled `AGPL-3.0-or-later`.
- `CREDITS.md` (project licence section; the per-dependency compatibility
  bullets dropped), `AI-USE.md`, the two adjectives in
  `openspec/specs/framework-identity/spec.md`.
- In the trees before the 0.8.0 release commit: the README sentence, the two
  sentences of `docs/architecture.md`, the sentences of `docs/why.rst`,
  `docs/project/status.rst` and `docs/start/install.rst` that named the grant,
  and an `Unreleased` entry in `HISTORY.rst`. From the release commit on, the
  manual states the licence through `|framework_licence|` and the 0.8.0 entry
  of HISTORY states it, so those files were left as written.

Not touched, as records: the ADRs, the archived OpenSpec changes, the release
notes of 0.7 and older, the 0.7.x-and-older entries of HISTORY and of the
changelog page, the mechanics package's own licence in `docs/reference/manuals.rst`,
and the lean-core plan's dependency table (a dated note was added to the plan).

## How

`relicense.py` is one deterministic, idempotent transform of a checkout.
Applied to the tree of `bf24687` it produced the licence commit; applied by
`git filter-branch --tree-filter` to every later tree it produced the rewrite.
A rebase was not used because 25 header-bearing files were deleted or renamed
inside the range and every one would have stopped a replay on a modify/delete
conflict; a tree rewrite has no conflicts.

    git worktree add -b relicense WTs/relicense bf24687
    (in it)  RELICENSE_ASSETS=<assets> python3 relicense.py; git add -A
             GIT_AUTHOR_DATE=2026-10-05T10:20:26+00:00 GIT_COMMITTER_DATE=<same> \
               git commit -F licence-commit-msg.txt            # -> f5556a6
    git replace --graft 6e6c0b28afead86f41b8ec7410b779bbc2468b6d f5556a6…
    FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -d <tmp> \
        --tree-filter 'RELICENSE_ASSETS=<assets> python3 relicense.py' \
        -- ^f5556a6… <the 25 branches containing 6e6c0b2>
    git replace -d 6e6c0b28afead86f41b8ec7410b779bbc2468b6d

The whole procedure ran first in a throwaway clone and then in the
repository. The licence commit's fixed date and identity make both runs
reproduce the same hashes, and they did: the tip of the rehearsal and of the
real run are both `e87cf52e…`. A `git bundle` of every ref was taken before
the real run. The five linked worktrees whose branches were rewritten were
reset to them. `refs/original/refs/heads/*` (25 refs) still hold the old
commits for inspection; `git for-each-ref refs/original` lists them and
`git update-ref -d` on each removes them when the pilot says.

## Verification

`verify.txt` is the output of `verify.sh` against the real run, every check
`ok`: licence commit parented on `bf24687`; 75 commits and 8 merges after it;
each side branch one commit beyond `main`; author, committer, dates, subjects
and graph identical between `refs/original/*` and the rewrite; every rewritten
commit free of Apache and AGPL headers and carrying `LICENSE`, both texts, no
`NOTICE` and the new pyproject expression; old `main` to new `main` differs
only in the instruments and headers, README, HISTORY and
`docs/architecture.md` untouched at the tip.

At the tip, `python -m build --no-isolation` produced `machinome-0.8.0` sdist
and wheel with `Metadata-Version: 2.4`,
`License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+` and `License-File`
entries for `LICENSE`, `LICENSES/CERN-OHL-S-2.0.txt` and
`LICENSES/GPL-2.0-or-later.txt`; `twine check` passed; the five record test
modules the handoff lists (`test_docs_structure`, `test_release_records`,
`test_machinome_identity`, `test_production_documentation`,
`test_profile_documentation`) passed: 27 tests, 810 subtests.

## Files

- `relicense.py`: the transform.
- `licence-commit-msg.txt`: the licence commit's message.
- `commit-map.txt`: old commit, new commit, subject, for all 78 rewritten
  commits.
- `verify.sh` and `verify.txt`: the checks and their output on the real run.

## Text sources

GPL-2.0: <https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt> as fetched on
5 October 2026 (338 lines; the FSF's current text, with URLs where older
copies carry the postal address). CERN-OHL-S-2.0: the SPDX license-list-data
text, which `reuse download` installs; CERN's own hosts returned 404 that day.
It differs from the copy in the 3DPrintedClocks repository only in one
heading's capitalisation and one "license/licence".

## What remains

The pilot's steps from the release handoff: the `v0.8.0` tag at a commit that
carries both the release state and the instruments, the push, the upload from
distributions built at the tagged commit, Read the Docs, Context7, the viewer.
Outside this repository: the other packages' own relicensing decisions, and
the workspace contract's sentences that still call machinome Apache-2.0.
