# `workflow/` — Videomaker's pre-spec working record

This directory holds the working material of Videomaker development that is
real and worth keeping but is not yet, or is no longer, an OpenSpec record.
It follows the same pattern as the machinome framework's `workflow/`.

The intended chain of a Videomaker change is:

    empirical finding (an episode) -> plan -> OpenSpec change -> baseline specs

`openspec/` owns the middle and the end of that chain: proposals under
ratification and the ratified behaviour of the tool. It has no place for the
two ends: the finding before anyone has decided there is a change, the plan a
change is later cut from, and the evidence of a finished campaign once its
change is archived. Those live here so they do not die with a conversation.

Nothing in this directory is ratified, and nothing in it is a promise about
the episode format. When a document here and an OpenSpec spec disagree, the
spec is right and the document is stale. Say so in the document rather than
quietly editing the record.

## What is here

### `warts.md` — findings, in the order they were met

The running log of friction met while producing real episodes: a workaround
an episode had to learn, a look the format cannot express, a promise that
failed. Entries are grouped by the episode that produced them and say plainly
whether they were filed, deferred, or judged not a Videomaker fix at all
(a viewer finding belongs to the viewer repository). Triage decisions the
pilot has ratified are recorded in place, so the file also reads as the queue.

An entry is evidence, not a requirement. It becomes a requirement only when
it is taken up as an OpenSpec change under this repository's `AGENTS.md`.

### `ongoing/` — provisional plans and design notes

The document a plan is worked out in before it is broken into an OpenSpec
change: surveys, design notes recording a direction the pilot settled in
discussion, the roadmap. Each states its status, its date, and what it does
*not* claim, in its own opening lines. Follow that convention; a note without
a status line will be read as settled and it is not.

These documents are revised as the thinking moves, and superseded rather than
deleted. When a plan is taken up, the OpenSpec change becomes the authority
and the note stays as the context the change was cut from. Once everything
the note plans is implemented and its changes are archived, the note leaves
`ongoing/` for `archive/`; a note only partly taken up stays here.

### `archive/` — finished campaigns and their evidence

One directory per completed campaign, named `<campaign>-<YYYY-MM-DD>`,
created when the first campaign finishes. A campaign is work too large to be
one OpenSpec change. Each holds its own report, a `PROGRESS.md` execution
index naming the commits and the OpenSpec changes it produced, and the raw
evidence. Archived records are historical: a later fix does not rewrite the
finding that motivated it; the report keeps its evidence and gains a
resolution note.

Disposable visual experiments are not campaigns. They live under
`experiments/` while they run and are recorded by the consuming project's
episode; what they prove is written up here or in `warts.md` when it becomes
a finding.

## Where this fits

`workflow/` belongs to the Videomaker repository and is committed with it.
It is not agent instructions: `AGENTS.md` is the working agreement, and a
document here is never read as authority over it, over `README.md` or over
`docs/FORMAT.md`.
