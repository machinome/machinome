# `workflow/` — studio development records

This directory holds working material of Machinome Studio development that
is real and worth keeping but is not, or is not yet, an OpenSpec record,
and is not written for a reader of the manual. It follows the convention
the framework and the viewer established in their own `workflow/`
directories.

Working notes here are not ratified promises. When a note and an OpenSpec
spec or an accepted ADR disagree, the spec or ADR is right and the note is
stale; say so in the note rather than quietly editing the record.

- `documentation.md` — how the manual under `docs/` is built and checked,
  and how it would be hosted.
- `foreman-listener.md` — how the user-facing agent receives delivery; an
  implementation note.
- `archive/shop-history.md` — the development narrative of the shop's
  planning and implementation agents before the studio had profiles: the
  reasoning the current profiles grew from.

The reader-facing manual is `docs/` (its `.rst` pages), `README.md`,
`CHANGELOG.md` and the `floor` package's docstrings. The architecture
overview, ADRs, design reference and product records stay under `docs/`
where `AGENTS.md` names them; the manual's build does not read them. The
ratified behaviour is under `openspec/`.
