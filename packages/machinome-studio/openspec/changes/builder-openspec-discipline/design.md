## Context

The shop develops itself through OpenSpec cycles. Mechanical projects built by
Builder have no equivalent: the `builder` profile states a machining discipline
but names no durable design document, so a project's contracts between parts
survive only in chat.

Two constraints shape this design. First, the runtime agent reaches nothing
except the floor's MCP tool set — it has no shell, so an external CLI is
reachable only if the floor exposes it. Second, `scoped-agent-tools` ratified
that the shop requires no ambient `PATH` executable to start; OpenSpec is a
Node program, so this change reverses that boundary and must say so rather
than slip past it.

Empirical work preceded this design. In a scratch repository the OpenSpec
grammar carried a lid/body interface — a 0.3 mm flush tolerance, a 110° open
clearance, a 0.2 mm latch interference — through `validate --strict`, and the
full lifecycle (`init` → `new change` → artifacts → `validate` → `archive`)
completed offline. Nested roots behave: a project's own record shadows the
shop's. Two CLI behaviors did not hold up and are designed around below.

## Goals / Non-Goals

**Goals:**

- A Builder project accumulates a durable, machine-checkable record of the
  contracts between its parts.
- The discipline is Builder's own conduct: the Maker describes what they want
  and never handles a spec artifact.
- Each specified scenario becomes a fit or assembly test, driven by the
  profile's existing disassembled-leaf-first loop.
- Nothing the tool surface exposes can write outside the active project.

**Non-Goals:**

- Fordesmac. Its designer already owns `docs/design.md` and its own release
  protocol; folding both disciplines together is a separate question.
- Packaging the Node dependency. Node becomes a documented prerequisite; how
  the shop eventually ships or vendors it is deferred.
- Machinery for the Maker to browse, approve, or edit specs.
- Retrofitting existing projects. A project gains its record the first time
  Builder opens a change in it.

## Decisions

### The tool surface is one passthrough plus one setup operation

`openspec_run` takes an argument vector and invokes the CLI; `openspec_setup`
performs the whole first-time preparation in one call.

*Why not narrow per-command tools?* Wrapping `new change`, `status`,
`instructions`, `validate`, and `archive` individually would freeze one CLI
version's surface into the shop's ratified spec, and the Maker's benefit comes
from OpenSpec being fully available, not from a curated subset. The guardrails
that matter — root containment, the archive gate, no store or global
configuration — are enforced on the vector, so passthrough loses nothing.

*Why a separate setup operation?* Preparing a project is init, seeding house
rules, and committing. Making Builder do that as three tool calls plus written
config spends context on ceremony every time and produces a different result
per project. One idempotent call makes preparation uniform and near-free.

### Preparation is Builder's call, not the launcher's

The alternative was scaffolding the record during project preparation, which
guarantees it exists before the agent starts. It was rejected because it puts
an unexplained commit in every Builder project's history whether or not the
Maker ever does design work, and because preparation only runs on projects it
creates — existing projects would still need the agent path.

The containment check makes the deferred path safe: if Builder forgets to
prepare, `openspec_run` fails naming the ancestor root it would have used
instead of silently writing there. Without that check this decision would be
unsafe, since an unprepared project resolves to the shop repository itself —
verified.

### The archive gate is ours, because the CLI has none

Verified: `openspec archive <name> --yes` prints `Warning: 1 incomplete
task(s) found. Continuing due to --yes flag` and archives anyway. Without
`--yes` it prompts `Continue? (y/N)` and dies under a closed stdin with
`User force closed the prompt with 0 null`. A stdio subprocess must pass
`--yes`, so the CLI cannot gate.

`openspec_run` therefore reads the change's task state and refuses the archive
itself. No override argument: when listed work stops being relevant, the honest
repair is amending the change's own task record, which is bookkeeping Builder
should be doing regardless. An override flag would be reached for first.

### House rules live in the project, seeded once

Two CLI behaviors reliably corrupt a record: a `MODIFIED` requirement written
with partial content silently loses the omitted detail at archive, and a spec
file created by archiving is stamped `Purpose: TBD` until someone writes it.
Both are artifact-specific, and OpenSpec surfaces per-artifact rules at the
moment the agent asks how to write that artifact — the right place, and free
when irrelevant. The mechanical vocabulary (a capability is an interface, a
scenario is a fit test) is seeded the same way.

The alternative was carrying them in the profile prompt, which costs tokens on
every turn including the many with no spec work.

Seeding is once-only: once the project owns the file, the Maker owns it.
Improving the seed later does not reach into existing projects. Stale-but-
correct beats editing a repository the shop does not own; a genuine revision
becomes a visible migration.

### Nothing mechanically forces the discipline

With no Maker ratification and no commit gate, the discipline is the profile
prompt plus `validate --strict`. Gating commits on an open change was
considered and rejected: Builder commits for many reasons that are not design
changes, and forcing a ceremonial change around each one would both annoy and
hide the thing worth learning — whether Builder keeps the discipline when it
is not compelled to. `builder-spec-discipline` states the absence of that gate
explicitly so a later reader does not mistake it for an oversight.

### Startup fails closed on the missing CLI

Requiring `openspec` at startup contradicts `Runtime location independence`,
which is why that requirement is modified here rather than quietly bypassed.
The relaxation is bounded to exactly one named executable.

A degraded mode — open the shop, disable spec tooling — was considered. It
was rejected because half-working software is harder to explain than software
that states its prerequisite, and because a Builder session that cannot record
its design silently loses the discipline this change exists to establish.

### Spec-only commits do not render

`git_commit` unconditionally refreshes the screenshot. On a planning commit
that renders geometry nothing touched, and on a project that does not yet build
it attaches a build warning to a commit containing no geometry — training
Builder to disregard warnings. The commit path inspects staged paths and skips
the render when none can affect the model. Automatic, so there is no flag for
Builder to forget.

### Tests use the real CLI

A fake `openspec`, following the existing fake-CLI fixtures, was considered and
dropped: Node is now a prerequisite, so a stand-in would test our plumbing
against a fiction while adding a second surface to maintain.

## Risks / Trade-offs

- **The ambient-PATH relaxation is a precedent.** → Bounded in the spec to one
  named executable, with every other ambient dependency still forbidden, and
  recorded in an ADR so the next such request is argued rather than assumed.

- **Node becomes a hard prerequisite of the whole shop, including for makers
  who never do design work.** → Accepted deliberately; stated in the README and
  setup script and enforced at startup rather than discovered mid-session.

- **Builder may not keep a discipline nothing enforces.** → This is the
  experiment. Evidence arrives as project histories; teeth remain available if
  it drifts.

- **The seeded house rules go stale in old projects.** → Accepted. A revision
  that matters becomes an explicit migration rather than a silent edit to a
  repository the Maker owns.

- **The archive gate parses task state the CLI could restructure.** → It reads
  the CLI's own JSON status rather than the Markdown, and the real-CLI tests
  fail loudly if that contract moves.

- **Two commits per design change may feel heavy for small work.** → The
  discipline applies only to changes that establish or alter an interface;
  fixes and knob values stay direct.

## Open Questions

- Whether Fordesmac should adopt the same record, and how it would relate to
  the designer's `docs/design.md` and drawing-release protocol.
- Whether the Maker should eventually be able to read the project's record in
  the browser, and what that surface looks like.
