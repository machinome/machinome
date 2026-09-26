# `workflow/` — the studio's pre-spec working record

This directory holds the working material of Machinome Studio development
that is real and worth keeping but is not yet, or is no longer, an OpenSpec
record, and is not written for a reader of the manual. It follows the
convention the framework established in its own `workflow/` directory and
the viewer adopted.

The intended chain of a studio change is:

    finding -> plan -> OpenSpec change + ADRs -> baseline specs

`openspec/` owns the middle and the end of that chain: proposals under
ratification, and the ratified behaviour of the studio as it stands. It has
no place for the two ends — the finding before anyone has decided there is a
change, the plan a change is later cut from, and the evidence of a finished
campaign once its change is archived. Those used to live only in a
conversation, which meant they died with it. They live here.

Nothing in this directory is ratified, and nothing in it is a promise to a
maker. When a document here and an OpenSpec spec or an accepted ADR
disagree, the spec or the ADR is right and the document is stale. Say so in
the document rather than quietly editing the record.

## What is here

### `ongoing/` — provisional plans and design notes

The document a plan is worked out in before it is broken into an OpenSpec
change and its ADRs: an assessment the pilot asked for, a roadmap, a design
note recording a direction settled in discussion. Each states its status,
its date, and what it does *not* claim, in its own opening lines. Follow
that convention; a note without a status line will be read as settled and
it is not.

These documents are revised as the thinking moves, and superseded rather
than deleted; a note that supersedes an earlier one says what it keeps of
it. When a plan is taken up, the OpenSpec change becomes the authority and
the note stays as the context the change was cut from. Once everything the
note plans is implemented and its changes are archived, the note leaves
`ongoing/` for `archive/`; a note only partly taken up stays here.

- `reconstructions-in-the-studio.md` — the tools and process the floor
  lacks for a historical reconstruction, assessed 26 September 2026 against
  the reconstructions made directly from the workspace, with a proposed
  order. Provisional; nothing cut from it yet.

### `archive/` — finished campaigns and their evidence

One directory per completed campaign, named `<campaign>-<YYYY-MM-DD>`, for
work too large to be one OpenSpec change — an audit, a due diligence, a
remediation programme — and for a note from `ongoing/` whose work is done,
dated by the archive of the change that finished it. Each holds its own
report, a `PROGRESS.md` execution index naming the worktree, the measured
commits and the OpenSpec changes it produced, and the raw evidence.

Archived records are historical. A later fix does not rewrite the finding
that motivated it: the report keeps its original evidence and gains a
resolution note.

Two records predate this layout and stay as flat files where the
documentation tests expect them:

- `archive/shop-history.md` — the development narrative of the shop's
  planning and implementation agents before the studio had profiles: the
  reasoning the current profiles grew from.
- `archive/codex-hub-list-fix.md` — the 26 September 2026 hub discovery
  correction, a direct conformance fix and its local test.

### Implementation notes

Flat notes on how a part of the studio is built, kept beside the plans:

- `documentation.md` — how the manual under `docs/` is built and checked,
  and how it would be hosted.
- `foreman-listener.md` — how the user-facing agent receives delivery.

### Findings

The framework keeps `warts.md`, a running log of friction met while
building real machines, grouped by the project that produced it and
carrying the pilot's triage in place. The studio has no such log yet. When
floor work on a real project produces findings worth keeping before anyone
decides there is a change, they go in a `warts.md` here, in that shape.

## Where this fits

`workflow/` belongs to the studio repository and is committed with it. It is
studio material: what the floor was found to lack and what is planned for
it. It is not agent instructions — a document here is never read as
authority over `AGENTS.md`, a profile prompt or a runtime skill — and it is
not the manual. The reader-facing manual is `docs/` (its `.rst` pages),
`README.md`, `CHANGELOG.md` and the `floor` package's docstrings; the
architecture overview, ADRs, design reference and product records stay under
`docs/` where `AGENTS.md` names them; the ratified behaviour is under
`openspec/`.
