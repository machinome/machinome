# `workflow/` — the framework's pre-spec working record

This directory holds the working material of machinome development that is
real and worth keeping but is not yet, or is no longer, an OpenSpec record.

The intended chain of a framework change is:

    empirical finding -> plan -> OpenSpec change + ADRs -> baseline specs

`openspec/` owns the middle and the end of that chain. It holds proposals
under ratification, and the ratified behaviour of the framework as it stands.
It has no place for the two ends: the finding before anyone has decided there
is a change, the plan a change is later cut from, and the evidence of a
finished campaign once its change is archived. Those used to live only in a
conversation, which meant they died with it. They live here.

Nothing in this directory is ratified, and nothing in it is a public API
promise. When a document here and an OpenSpec spec or an accepted ADR
disagree, the spec or the ADR is right and the document is stale. Say so in
the document rather than quietly editing the record.

## What is here

### `warts.md` — findings, in the order they were met

The running log of framework friction met while building real machines:
a workaround a project had to learn, a contract the framework cannot express,
a promise that failed, a gap a project routed around. Entries are grouped by
the project that produced them and say plainly whether they were filed,
deferred, or judged not a framework fix at all. Triage decisions the pilot
has ratified are recorded in place, so the file also reads as the queue.
It holds open findings only: a resolved entry leaves it for a dated
archive that keeps the text and says what closed it, as
`archive/warts-hygiene-2026-10-04/` did for everything fixed up to then.

An entry is evidence, not a requirement. It becomes a requirement only when
it is taken up as a framework change under
`machinome-studio/skills/framework-change/SKILL.md`.

### `ongoing/` — provisional plans and design notes

The document a plan is worked out in before it is broken into an OpenSpec
change and its ADRs: research proposals, surveys of what the project
catalogue actually contains, design notes recording a direction the pilot
settled in discussion. Each states its status, its date, and what it does
*not* claim, in its own opening lines. Follow that convention; a note without
a status line will be read as settled and it is not.

These documents are revised as the thinking moves, and superseded rather than
deleted. A note that supersedes an earlier one says what it keeps of it — as
`joints-and-couplings.md` did for `mechanics-ontology.md` (both now under
`archive/motion-layer-2026-09-09/`), keeping the survey as a coverage
checklist while setting its class catalogue aside. When
a plan is taken up, the OpenSpec change becomes the authority and the note
stays as the context the change was cut from. Once everything the note plans
is implemented and its changes are archived, the note leaves `ongoing/` for
`archive/`, as below; a note only partly taken up stays here.

### `archive/` — finished campaigns and their evidence

One directory per completed campaign, named `<campaign>-<YYYY-MM-DD>`. A
campaign is work too large to be one OpenSpec change: an audit, a due
diligence, a remediation programme. A plan or design note from `ongoing/`
whose work has been implemented is archived the same way, in a directory
named after the note and dated by the archive of the change that finished
it. Each campaign holds its own report, a `PROGRESS.md`
execution index naming the worktree, the measured commits, the OpenSpec
changes it produced, and the raw evidence — probes, logs, JSON measurements,
checksums.

Archived records are historical. A later fix does not rewrite the finding
that motivated it: the report keeps its original evidence and gains a
resolution note. Measurements describe the commit they were taken at, and a
report that has been rebased says so rather than implying it was remeasured.

## Where this fits

`workflow/` belongs to the machinome repository and is committed with it.
It is framework material, not shop material: it records what the framework
found and what it plans, while the shop keeps the process for doing the work.
It is not agent instructions — the framework repository holds no agent
prompts, and a document here is never read as authority over
`machinome-studio/AGENTS.md` or its skills.
