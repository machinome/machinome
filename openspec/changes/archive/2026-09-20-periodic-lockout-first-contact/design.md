## Context

The empirical and source-level diagnosis is recorded in
`workflow/docs/curta-periodic-lockout-first-contact.md`. The complete Curta
source-backed reproduction at `c76f230` fails against framework `8d2bd71`.
`Run._searched_constraint` correctly finds an interior obstruction, but
`Run._constraint_group` compares a candidate's level only at fractions 0 and
1. For the two-turn crank request those levels are both approximately -5.22;
the early positive level is ignored and the selected group is empty.

ADR-113 explicitly describes this pushing test as net over the stretch. Its
limitation conflicts with this real periodic caller, although its interior
contact search already finds the event. ADR-108's atomicity and no-backlog
rules, ADR-109's own-coordinate freezing, ADR-111's producer corpus,
ADR-133's independent time admissions and ADR-134's ancestor declarations
remain relevant and must be preserved.

### Cycle identity

- Shop: `/home/asa/devel/machinome-studio`.
- Framework primary: `/home/asa/devel/machinome-studio/machinome`, clean
  branch `main` at `8d2bd71171be81f13ba5dd492851ed8b3a9ababb` when opened.
- Standalone cycle branch: `periodic-lockout-first-contact`.
- Worktree: primary framework's `WTs/periodic-lockout-first-contact`.
- Integration target: framework `main`, only on separate pilot authority
  after final validation and only if still at the recorded base.
- Existing unrelated worktrees and obsolete external worktree registrations
  are preserved, not inspected outside the workspace or repaired.
- Status: ratified by the pilot's “go on” on 2026-09-20 after presentation
  of the complete plan; implementation follows the planning-only commit.

## Goals / Non-Goals

Goals:

- Stop the originating long request at the same measured first contact as
  its short and timed equivalents, without fictional travel caps.
- Identify pushing admissions using evidence at the contact already found.
- Preserve correct relief, idle retention, independent motion, command
  retirement, deterministic replay, own-coordinate freezing and atomicity.
- Publish producer conformance evidence usable by the independent viewer.

Non-goals:

- No new public API, expression primitive, wire field or document version.
- No replacement collision engine, CAD changes, production Curta restraint
  adoption or claim that all operating Curta work is complete.
- No hidden request subdivision, one-turn restriction or suppressed invariant.
- No general solution for effects that require multiple admissions together
  while no single admission pushes alone; existing transactional refusal stays.
- No stronger detection guarantee for contact intervals wholly between search
  samples, and no new tolerance. No performance redesign or clocked-run change.
- No implementation, integration or publication in the viewer repository.

## Decisions

### 1. Keep the located contact's two-sided evidence

Retain both inside and outside fractions of the final bisection bracket for
moving-read constraints instead of discarding the outside side. Carry this
private localization evidence through event selection to the group decision.
The committed segment still ends at the inside fraction. Simultaneous events
keep their own bracket while sharing the existing earliest-event commit rule.
Nothing new is persisted or serialized.

The existing 64 subdivisions, bisection limit, crossing tolerance, sampling
limitations and no-snap invariant remain. Static reads still take the numeric
bound path. An idle constraint still does no path search.

Alternative: recompute a small offset after contact. Rejected because an
arbitrary epsilon might cross another branch and would duplicate information
the locator already computed. Alternative: detect periodic syntax and treat it
specially. Rejected because endpoint cancellation is about the path, not the
spelling of its bound.

### 2. Test each candidate over the contact bracket

For each nonzero candidate admission, evaluate its constraint level alone at
the bracket's inside and outside fractions, using the original stretch state
and original admission scaled to each fraction. Every other admission is zero
for this candidate test. Preserve the tick-start own-coordinate argument and
the full compiled determining sub-program for the coordinate and reads.
Select the candidate when its level increases across that bracket. The same
procedure applies to independent time-drive admissions, not only commands.

This deliberately replaces ADR-113's net-over-the-whole-stretch test. The
later end of a request no longer cancels its pushing motion at the encountered
contact. No blanket fallback that stops all candidates is permitted. Inputs
that are unrelated, disengaged or relieving remain free; the remaining segment
is re-evaluated normally. If no candidate pushes, the transactional invariant
continues to refuse the tick rather than guessing a group.

Alternative: only shorten the whole-stretch comparison to the contact prefix.
Rejected because it still asks for net motion from the original state rather
than motion at the obstruction, and misses a changing direction near contact.
Alternative: catch the exception and retry smaller requests. Rejected because
it changes command history and hides the executor defect in its callers.

### 3. Validate progressively, red first

Before runtime edits, add a cheap framework fixture with the same periodic
moving-read geometry-independent arithmetic. Prove the long immediate case
fails while fixed, short and timed controls work. Cover equal and lower final
clearance levels, lower and mirrored upper bounds, later revolutions, zero
travel retry, backward relief, independent and relieving admissions,
time-drive candidates, simultaneous constraints and snapshot replay. Keep the
existing lock, pawl, retained-coordinate, play and time-drive suites green.

Add a producer-generated corpus scenario and coverage refusal test, including
snapshot replay and a mutation restoring the old pushing comparison. Existing
unaffected published program shapes and identities must not change. Retain
the framework's complete regression suite as final acceptance.

Then run the existing actual Curta four-case reproduction against the isolated
framework. All four must pass. Validate the measured five-flat candidate:
its long request, each flat and later revolutions, five withdrawal phases,
retry/relief/idle/replay, and already legal 1080° requests. Check the complete
printed pair at admitted stop poses with both native and faceted geometry and
inspect rendered snapshots. Never replace this with only synthetic fixtures.
Use the project-owned tests and temporary diagnostic commands; any additional
project edits remain project-owned and are reported separately.

### 4. Keep runtime and repository boundaries honest

This is a producer correction without a document-schema change. Generate the
fixture from the corrected framework, never hand-author expected banks.
The viewer executes its own run and may retain the same defect; the corpus is
the handoff, not proof that it passes. Browser acceptance and any viewer fix
are a separate repository gate before adopting Curta's general operating law.
Do not drive the pilot's current live Studio session during this cycle.

After implementation proves the design, extract one accepted decision amending
ADR-113's pushing-test choice, update its index and the architecture synthesis,
sync baseline specs and archive the cycle. No accepted ADR is written during
proposal. The two-commit cycle and separate integration authority remain.

## Risks / Trade-offs

- Very close bracket endpoints can expose floating-point cancellation → use
  the locator's actual endpoints and existing tolerances; test small and large
  requests, and stop for plan revision if robust attribution needs a different
  rule. Do not silently add an epsilon or all-input fallback.
- Candidate-alone paths can differ from a jointly moving path → preserve the
  existing individual-push scope and explicitly test established multi-input
  lock scenarios. A contradiction returns to the pilot for re-ratification.
- Changing an accepted attribution rule can alter old outcomes → run the full
  corpus and regression suite; explain any difference before accepting it.
- Sampling can miss an entire narrow forbidden interval → document that
  existing limitation; the originating contact is detected already and is not
  such a miss. Do not claim arbitrary unlimited-frequency contact completeness.
- Python and viewer runtimes may disagree until a viewer cycle follows → record
  the unverified consumer status and do not claim browser completion.
- Full source-backed Curta checks are costly → run CAD checks sequentially with
  the existing resource cap; use small pure-motion fixtures for iteration.

## Migration Plan

No model migration is intended. After explicit ratification, validate and
commit planning alone, implement red-first, validate the framework and Curta,
then commit implementation with synchronized specs and archive. Integration is
separately authorized and fast-forward-only from the recorded base. Until then
main and the production Curta restraint remain unchanged.

## Open Questions

Numerical robustness and compatibility of the
local-bracket attribution are implementation acceptance gates, not assumed
results. Any change to that rule or widening to compound multi-input effects
requires renewed pilot agreement. Viewer correction, if needed, is separate.
