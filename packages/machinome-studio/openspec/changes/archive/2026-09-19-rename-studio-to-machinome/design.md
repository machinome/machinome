## Context

The studio is still private and experimental, but its package metadata,
project configuration, UI, setup scripts, profiles, skills and documentation
already expose the LibreSolid identity. The workspace also coordinates three
independent full-history repositories plus two one-commit package-name holders.
The rename must preserve repository boundaries and historical evidence and may
not imply that the studio has been published.

The canonical names are:

| Product | Repository | Distribution / package | Command / integration |
| --- | --- | --- | --- |
| Studio | `machinome/machinome-studio` | `machinome-studio` | `[tool.machinome-studio]` |
| Framework | `machinome/machinome-framework` | `machinome` / `machinome` | `machinome` |
| Mechanics | `machinome/machinome-mechanics` | `machinome-mechanics` / `machinome_mechanics` | `machinome[mechanics]` |
| Viewer | `machinome/machinome-viewer` | `machinome-viewer` / `machinome_viewer` | `machinome[viewer]` |

## Goals / Non-Goals

**Goals:**

- Give all current studio surfaces one Machinome identity.
- Keep each independent repository's full history and make every primary branch
  ready for the pilot to push to its new remote.
- Update executable references and paired validation to use the renamed
  framework and viewer.
- Keep current status claims honest: studio remains unpublished and
  experimental; viewer and mechanics remain unreleased.

**Non-Goals:**

- Publishing, pushing, tagging, opening pull requests, or deleting old remote
  repositories.
- Rewriting old ADRs, archived changes, or past release records as if the new
  name existed then.
- Renaming shop-domain concepts such as floor, shop, foreman, or machinist.

## Decisions

### Canonical spellings use Machinome everywhere

The two `machinode-*` spellings in the initiating message are treated as
typographical errors. The explicit GitHub URL, the term definition, and the
viewer's already-configured remote all use `machinome`. Alternatives—keeping a
Machinode repository brand or mixing the two spellings—would recreate the
identity ambiguity this migration removes.

### Current surfaces move; historical records remain

Current source, tests, configuration, baseline specs, architecture synthesis,
indexes, README material, skills, profiles and operational scripts move to the
new names. Archived OpenSpec changes, accepted ADR bodies, old release notes
and commit history retain the old names. Current indexes may annotate their
historical context, and new rename records link the eras.

### Full-history repositories replace the holder directories

The full framework, viewer and mechanics histories become the canonical
repositories. Before the final directory move, the one-commit `machinome/`
PyPI holder and `machinome-viewer/` npm holder move intact under
`name-holders/`; they are not deleted, merged as unrelated histories, or
mistaken for the product repositories. The full repositories then move to
`machinome-framework/`, `machinome-viewer/`, and `machinome-mechanics/`.

### Remotes change only after content commits are integrated

Each rename is implemented and validated in its owning repository. Completed
change commits are fast-forwarded to the clean primary branch. Only then are
worktrees removed, directories moved, and `origin` configured to the exact
`git@github.com:machinome/<repository>.git` destination. No network write is
performed.

### The studio extra is described honestly

The framework may declare `machinome-studio` behind its `studio` extra so the
eventual installation spelling is stable. Current studio documentation and
0.7 release material explicitly state that the extra cannot install from an
index until Machinome Studio is published.

## Risks / Trade-offs

- **Broad mechanical replacement can rewrite historical evidence** → scope
  replacement to current files and add searches that classify every remaining
  old name as history, compatibility input, or a defect.
- **Directory collisions with the holder repositories** → move holders intact
  to `name-holders/` before moving the full-history repositories.
- **Renamed config silently stops selecting a profile** → add red-first tests
  for `[tool.machinome-studio]` and explicit rejection/migration messaging for
  the former table.
- **Setup tests accidentally resolve old checkouts or commands** → validate a
  fresh temporary workspace using only canonical paths and the `machinome`
  executable.
- **The migration could overstate publication** → retain explicit unpublished
  status in studio, viewer and mechanics docs and test package metadata rather
  than attempting an upload.

## Migration Plan

1. Land and integrate the framework, viewer and mechanics repository changes.
2. Update the studio against those exact integrated commits and run unit,
   frontend, E2E where available, packaging, setup and cross-repository checks.
3. Fast-forward the studio primary branch.
4. Remove clean migration worktrees, move name holders and canonical repository
   directories, update all local remotes, and verify every repository root,
   branch, clean status and outgoing commits.
5. Hand the pilot exact push commands and any external GitHub/PyPI/npm rename
   steps; perform none of them.

## Open Questions

None after ratification of the clean-break surface and the `machinome`
spellings above.
