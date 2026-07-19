# Shop history: drawing office and machinist

## Purpose of this record

This document preserves the reasoning behind the shop's planning and
implementation agents. It is context for changing `agents/drawing-office.md`,
`agents/machinist.md`, and their orchestration loop. It records experiments and
the lessons drawn from them; it is not a claim that the next workflow has
already been validated.

The present priority is to improve the relationship between the drawing office
and the machinist. The current sequential, specification-first loop can produce
excellent work, but it is too slow and expensive to be the general development
process.

## The objective that has remained constant

The shop should be able to take a mechanical idea, establish enough shared
intent with the pilot, and carry the project through to a useful result. It
should not optimize merely for producing something visible from any prompt, nor
should it spend hours proving details that do not yet matter.

The desired balance is:

- enough early conversation to understand the project and its important
  constraints;
- early construction and visual evidence;
- mechanical care proportional to the part being built;
- continuity of project context across the build;
- autonomy to continue toward the whole project, stopping only for decisions
  that genuinely require the pilot; and
- a parametric design that remains inexpensive to adjust as understanding
  improves.

## How the process evolved

### 1. The `solid` platform and fast builder agents

The work began in the private `../solid/` platform, which contained several
repositories and a team of builder agents. The surviving manifest is
`../solid/builder-agents.md` in the author's workspace.

The initial goal was speed: start from a prompt, put something on screen
quickly, let the pilot react, and adjust. Fast Haiku agents were used for the
first pass. A snowman was a useful simple visual test. Deliberately extreme
prompts, including a functional Boeing 747, tested whether the system could
find a tractable starting point and make *something* from almost any request.

That phase demonstrated the value of early visible output and iteration. It
also optimized for the wrong outcome. Mechanical development is expensive;
being able to emit a plausible object is not the same as spending that effort
on a coherent, functional project. A process that accepts any ambition without
enough attention can create activity without accumulating a good design.

### 2. Deliberate, step-by-step construction

The next experiment used the Fable model to design a gearbox incrementally.
After the first steps, implementation was delegated to a Sonnet subagent. That
work split naturally into planning and implementation responsibilities, and
the process was later packaged as two distinct agents: the drawing office and
the machinist.

The workflow became step-by-step because each step was being checked before
the next one began. This improved control, made errors easier to localize, and
kept the pilot close to the evolving mechanism. The current sequence—complete
a drawing, ratify it, machine one increment, inspect it, then repeat—grew out
of that experiment rather than from a prior belief that a waterfall process
was intrinsically desirable.

### 3. The V8 engine: precision at high cost

The two-agent process built a large part of a V8 engine with remarkable
precision. Planning captured measurements and component details extremely
well. This established that careful separation of mechanical design from
implementation can produce a complex, coherent result.

It also exposed two important weaknesses:

1. Dimensions were specified precisely but not organized into a genuinely
   parametric system. The design was accurate at one chosen point, yet hard to
   reshape as the project evolved.
2. Individual steps grew to roughly one or two hours and consumed a great many
   tokens. The level of analysis that helped a complex engine component was
   being paid for on every increment.

Precision is therefore evidence of capability, not by itself evidence that the
process is economical or adaptable.

### 4. The windmill: over-planning becomes obvious

The windmill exposed the scaling problem from the other direction. Even a
simple cylinder could cause the drawing office to analyze the entire framework
before planning the part. The cost of planning no longer matched the
complexity or uncertainty of the work.

The response was to forbid product agents from reading framework source. That
stopped unbounded framework excavation, but it was an overcorrection. The real
requirement is not ignorance of the framework; it is **proportionate access to
framework knowledge**. Planning a cylinder should use a small, reliable piece
of framework context. It should not trigger a repository-wide study. Equally,
an agent should not be forced to plan blindly when a narrow capability question
is material to the design.

This distinction matters when revising the current absolute prohibitions in
the drawing-office and machinist prompts. The problem to solve is uncontrolled
scope, not knowledge itself.

## Current diagnosis

The current shop encodes a batch handoff:

    drawing office finishes increment -> pilot ratifies -> machinist starts

That has several consequences:

- The machinist waits while the drawing office attempts to remove uncertainty
  from the whole increment.
- The drawing office must anticipate implementation findings before any part is
  built.
- Planning effort is determined more by the process gate than by the actual
  complexity of the part.
- Context is repeatedly compressed into per-increment specifications instead of
  being carried forward as one evolving project understanding.
- Frequent mandatory stops make the pilot manage the process one small step at
  a time, even after the overall intent is clear.
- Exact dimensions can become frozen facts instead of derived relationships,
  making later visual and mechanical changes expensive.

The planning/implementation separation remains valuable. The assumption now
under question is that planning must finish before implementation can begin.

## Next experiment: progressive drawings and overlapping work

The next hypothesis is that the drawing office and machinist should work as an
overlapping pipeline.

1. **Establish project intent once.** Begin with a substantive conversation
   with the pilot. Capture purpose, functional ambition, important constraints,
   expected fidelity, manufacturing assumptions, and the few choices that
   shape the whole project.
2. **Publish an executable first draft.** The drawing office releases the
   smallest useful drawing that lets the machinist begin safely. It explicitly
   distinguishes stable decisions from provisional details and future work.
3. **Start machining.** The machinist implements the stable slice and returns
   concrete evidence: geometry, tests, snapshots, framework friction, and
   surprises.
4. **Refine ahead of the machinist.** While implementation proceeds, the
   drawing office improves later portions of the plan and incorporates evidence
   from completed work. It does not repeatedly redesign the slice currently
   under the machinist's hands without an explicit synchronization point.
5. **Continue toward the project, not merely the next step.** The agents keep
   building through ordinary local choices. They stop when a decision changes
   the project's purpose, major architecture, external interface, cost or
   safety envelope, or when conflicting evidence makes continued work likely
   to be wasted.

“Parallel” here means overlapping progress with controlled handoffs. It does
not mean both agents editing the same drawing or implementation files at the
same time. The protocol still needs a clear way to version drafts, declare a
slice ready, report implementation feedback, and prevent the machinist from
building against a moving contract.

## Parametric and agile design requirements

The project should be cheap to steer after the first visible result. To make
that possible:

- Keep only consequential degrees of freedom as named input parameters.
- Derive dependent dimensions and positions from those parameters instead of
  copying literals throughout the model.
- Separate adjustable defaults from fixed conventions and real manufacturing
  limits.
- Give parameters explicit useful ranges or guards.
- Test functional relationships across representative values in those ranges,
  not only at the current defaults.
- Let snapshots and implementation findings inform default values without
  treating every adjustment as a new design process.
- Add detail and verification in proportion to risk, mechanical importance,
  and evidence—not uniformly because another project once needed it.

This is the intended meaning of “agile” in the shop: construction produces
knowledge, that knowledge updates the plan, and parameterization keeps those
updates affordable. It does not mean skipping mechanical reasoning or tests.

## What should be preserved

The next iteration should retain the strengths established by earlier work:

- a distinct agent accountable for mechanical coherence and another
  accountable for implementation quality;
- durable project context rather than reliance on chat memory;
- functional tests and visual inspection;
- explicit reporting of framework friction;
- pilot authority over genuinely consequential decisions; and
- precise work where precision has mechanical value.

It should remove accidental costs:

- exhaustive planning before any implementation evidence exists;
- whole-framework analysis for routine geometry;
- full process ceremony for every small part;
- repeated pilot approval for reversible implementation choices; and
- fixed-value precision that makes the design brittle.

## Current experimental version

The repository now encodes the first pipelined version of this hypothesis:

- `docs/design.md` holds the evolving project-level design;
- committed, immutable drawings hold executable increment detail;
- the office releases a small first drawing before doing broad planning;
- the machinist builds that drawing while the office drafts one slice ahead;
- the office owns design files and the machinist owns code and tests;
- the office receives the complete public API without framework source;
- the machinist may inspect framework implementation narrowly for diagnosis;
  and
- consequential decisions stop for the pilot while reversible working
  assumptions do not.

During experimental evaluation, the product-side shop is also forbidden from
reading files from any other mechanical project for reference. This prevents
examples, archives, and previous generated work from tainting tests of whether
the current roles and skills are sufficient.

This version is encoded but not yet validated on a new end-to-end project. The
next experiments need to determine:

- whether the opening brief is sufficient without becoming another planning
  bottleneck;
- whether drawing commits, uncommitted planning-ahead drafts, and machinist
  commits coexist safely in the same working tree;
- whether one-slice-ahead planning produces timely drawings without outrunning
  implementation evidence;
- whether complete API access gives the office feasibility knowledge without
  causing exhaustive analysis;
- whether targeted source access helps the machinist without leaking private
  APIs or unrelated project patterns;
- whether the decision threshold prevents unnecessary pilot stops;
- how verification depth should scale with part risk and complexity; and
- whether elapsed time, token cost, rework, visual quality, functional
  correctness, and later parameter changes improve in practice.

These remain active hypotheses. Update this record when experiments invalidate
an assumption or establish a better workflow; do not rewrite the history to
make the current design look inevitable.

## First Codex bootstrap experiment: classroom polder mill

The first attempt to run the pipelined shop through Codex targeted
`projects/classroom-polder-mill`. The pilot brief was substantial: a Dutch-style
drainage windmill that recirculates real water; hand-turned sails; an enlarged,
exposed educational mechanism; an Archimedes screw as the proposed pump;
approximately 400 mm default height; small-car portability and
teacher-sensitive cost; parametric scale, printer envelope, process limits,
segmentation, clearances, and container interface; no motor or electronics;
and provisional FDM and water-tolerance assumptions. Visibility had to be
balanced against pinch and entanglement hazards.

The project was scaffolded and committed correctly. Its confirmed final state
was:

- HEAD `25b8568` (`Scaffold classroom polder mill project`);
- a clean working tree and a reflog containing only that commit;
- only `.gitignore` and `root/__init__.py` in the project; and
- no design record, increment drawing, CAD implementation, test, snapshot, or
  export.

No machinist or librarian was dispatched. No push, publication, or external
contact occurred. All drawing-office contexts were ultimately interrupted.

### Dispatches and observable result

| Attempt | Context | Instruction | Observed result |
|---|---|---|---|
| 1 | `drawing_office_bootstrap`, `fork_turns="all"` | Initial design record and small released increment | No message, file, or commit after roughly 5.5 minutes of completed waits and a status prompt; interrupted |
| 2 | Follow-up in the same accumulated context | Narrow “execute now” retry | No message, file, or commit after roughly 90 more seconds; interrupted |
| 3 | `drawing_office_release`, new agent with `fork_turns="all"` | Same release in a fresh agent but inherited failed history | No message, file, or commit after roughly 3 minutes of completed waits; interrupted |
| 4 | `drawing_office_fresh`, `fork_turns="none"` | Minimal fresh-context retry, reading instructions locally | No message, file, or commit before the pilot stopped the experiment; interrupted |

The registry reported `last_task_message: null` for every specialist context.
Across the experiment there were about eleven minutes of fully completed wait
windows, plus partial waits and orchestration overhead. The earlier shorthand
description of “about 15 minutes” included that overhead; the more precise
evidence is the attempt-by-attempt timing above.

The collaboration surface did not expose hidden reasoning, live tool calls,
partial unreturned prose, exact input/output token counts, requested versus
actual subagent model, or a checkpoint recoverable after interruption. It is
therefore not possible to distinguish a model reasoning continuously from a
queued, stalled, or otherwise blocked runtime. The only supported conclusion is
**no observable progress before interruption**. Excessive context, scheduling
failure, and generation that never reached an action remain hypotheses, not
findings.

### Context construction

The first agent inherited the complete conversation and repository contract
through `fork_turns="all"`. Its dispatch also pasted the full drawing-office
role and `solid-node-api` skill, as prescribed by the checkout fallback. Those
two sources contained 2,525 words and 18,434 bytes. Because they had already
appeared in inherited tool output, the dispatch effectively supplied them
twice.

The report estimated roughly 7,000–10,000 tokens of duplicated role/API
material alone, before the running-shop skill, repository contract,
conversation, pilot brief, platform instructions, and generated tokens. That
range is a context-size estimate, not billing evidence.

The second fresh `fork_turns="all"` agent compounded the worst parts of the
first attempt: it inherited the oversized dispatch, loaded instructions, wait
events, commentary, and failed retry history. The final `fork_turns="none"`
attempt was much smaller and referred to local instructions, but this departed
from `CLAUDE.md`'s verbatim direct-checkout fallback. That exposed a portability
mistake in the shop documentation: a Claude-specific fallback had been treated
as if it were the correct Codex transport protocol.

### Orchestration failures

The foreman correctly reported its own mistakes:

1. It waited too long without a heartbeat, message, or repository change.
2. It poked and restarted a silent accumulated context without evidence that
   the context could respond.
3. It created another `fork_turns="all"` agent and enlarged an already failed
   context.
4. It combined inherited context with verbatim instruction inclusion, paying
   for the same material twice.
5. It made a fresh-context retry that reduced cost but violated the documented
   fallback instead of first recognizing the fallback as wrong for Codex.
6. It continued retrying without any changed evidence or runtime condition.
7. An early repository search excluded `projects/**` but still exposed
   filenames under `old/polder-mill/`. The files were not opened or passed to a
   specialist, but even discovering those paths violated the provisional
   project-isolation experiment.

### What the experiment tested

This run did **not** test drawing-office design quality, the windmill
architecture, solid-node CAD capability, the machinist, red-to-green testing,
snapshot judgment, or the concurrent pipeline. It tested only the Codex
dispatch/bootstrap boundary, and that boundary failed before the first released
drawing.

The result therefore does not justify simplifying the windmill brief or
concluding that the drawing-office role is incapable. It does justify treating
silent delegation, context construction, interruption, and artifact latency as
first-class parts of the shop design.

### Requirements before another Codex attempt

The next Codex bootstrap experiment should:

- use one `fork_turns="none"` specialist dispatch;
- supply the role and API exactly once, preferably through locally loaded
  Codex instructions rather than pasted inherited content;
- make the first actions repository verification followed by a minimal durable
  `DRAFT` artifact, before extended design reasoning;
- require an observable heartbeat or filesystem change within 60–90 seconds;
- interrupt after that threshold and report delegation failure rather than
  poke or retry the same context;
- make at most one fresh retry, and only when a concrete dispatch or runtime
  condition has changed;
- never inherit failed-agent history into a retry;
- anchor every filesystem search at the active project so other project names
  are not exposed;
- record requested model, actual model when available, fork mode, dispatch
  time, time to first artifact, last observable action, result, and usage when
  the runtime exposes it; and
- leave the existing clean scaffold untouched unless the pilot explicitly
  chooses to resume or remove it.

### Model allocation after the failed run

The first Codex-native allocation requested Sol for the foreman, drawing
office, and framework roles, and Terra for the machinist and librarian. The
runtime report could not establish which model any spawned context actually
used, so role-specific model selection remains unverified on this collaboration
surface.

For the next cost experiment, every configured role was stepped down one model
tier without changing reasoning effort: the foreman uses Terra at medium; the
drawing office uses Terra at high; the machinist uses Luna at high; the
librarian uses Luna at medium; and both framework roles use Terra at high.
Project configuration still caps agent depth and concurrency.

This lower allocation is an evaluation baseline, not a diagnosis or sufficient
fix. Change it from observed time, usage, artifact latency, revisions, retries,
mutation failures, and completed-slice quality. In particular, time and usage
until the first durable drawing are primary metrics: reasoning that produces no
recoverable artifact is a failed shop run regardless of its hidden theoretical
quality.

## Bootstrap revision after the first Codex experiment

The next shop version changes the Codex transport and startup contract without
yet changing the progressive-drawing or concurrent-machining hypothesis.

- Every Codex specialist receives a fresh `fork_turns="none"` task-local
  context. Its named-agent adapter loads the role and skills locally once; the
  foreman no longer pastes them or sends its conversation history.
- An initial drawing office loads its role, verifies the project repository,
  and immediately writes minimal uncommitted drafts of `docs/design.md` and
  `docs/specs/increment-1.md`. Only after this durable checkpoint does it load
  the complete public API and begin mechanical planning.
- The foreman checks for a message or filesystem change at 60 seconds. Ninety
  seconds of silent startup ends in interruption and a factual failure report,
  not a poke, accumulated-context retry, or automatic replacement agent.
- A fresh retry is permitted only after a concrete transport, path, packaging,
  or runtime condition changes. Partial drafts are preserved as evidence.
- Claude's direct-checkout verbatim-prompt fallback is now explicitly scoped
  to Claude and must also supply each instruction exactly once. It is no longer
  presented as a Codex fallback.

This revision deliberately separates **dispatch liveness** from **design
quality**. A quick draft proves only that the agent reached the project and can
externalize work. A committed released drawing remains the first evidence that
the drawing office can produce an executable design slice. The revision is
ready for another experiment but is not yet validated.
