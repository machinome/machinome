## Why

A Builder project has no durable design record. The profile's disassembled-leaf
workflow governs how a part is built, but nothing states what the parts must be
to each other, so every contract between two parts lives only in the
conversation that produced it. When the Maker returns weeks later, or when a
part is changed, the reason a clearance is 0.3 mm is gone.

The shop already develops itself spec-first with OpenSpec, and OpenSpec's
grammar carries mechanical contracts unchanged: a capability is an interface
between parts, a requirement is what that interface must guarantee, and a
scenario is a fit or assembly test. Giving Builder the same discipline turns
each project's interfaces into a record that outlives the chat, and turns each
scenario into a test the existing red-first loop already knows how to drive.

## What Changes

- Builder develops every design change through a two-commit OpenSpec cycle:
  the plan is proposed and committed first, then the parts are built red-first,
  the specs synced, the change archived, and the result committed.
- The discipline is internal to Builder. The Maker never ratifies a plan and
  never sees OpenSpec vocabulary unless they ask; they describe what they want
  and Builder keeps the record.
- A project owns its own `openspec/` root. Builder creates it through a single
  tool call that scaffolds, seeds the project's mechanical house rules, and
  commits, and is a no-op once the root exists.
- A new floor tool surface exposes OpenSpec to Builder, refusing any invocation
  whose resolved OpenSpec root is not the active project, and refusing to
  archive a change whose tasks are not complete.
- A new `OpenSpec` profile tool capability carries that surface, declared only
  by the `builder` profile. Fordesmac roles are unchanged.
- The shop refuses to start without the `openspec` CLI, the way it refuses any
  other missing prerequisite. **BREAKING** for an installation that has no
  Node.
- A floor-mediated commit carrying only spec text does not rebuild the model or
  refresh the project screenshot.

## Capabilities

### New Capabilities
- `builder-spec-discipline`: how Builder plans, records, and closes a design
  change — the two-commit cycle, interfaces as capabilities, scenarios as fit
  tests, one change at a time, and what happens when the Maker changes course
  mid-change.

### Modified Capabilities
- `scoped-agent-tools`: adds the project-scoped OpenSpec tool surface, its root
  containment refusal, and its archive gate; relaxes `Runtime location
  independence` to permit the one declared external CLI this change introduces.
- `shop-runtime-profile`: adds the `OpenSpec` tool capability to the profile
  vocabulary and declares it for `builder` only.
- `shop-floor-lifecycle`: adds the `openspec` CLI to fail-closed startup
  preflight.
- `project-model-screenshot`: a commit carrying no model content does not
  trigger a render.

## Impact

- `profiles/builder/builder.md` — the OpenSpec cycle joins the standing
  discipline beside the red-first loop.
- `profiles/builder/profile.toml` — declares the `OpenSpec` capability.
- `floor/profiles.py` — the closed capability vocabulary gains one name.
- `floor/mcp_server.py` — OpenSpec tools, containment check, archive gate, and
  the spec-only commit path.
- `floor/orchestrator.py` — startup preflight for the `openspec` CLI.
- `README.md`, `scripts/setup` — Node and `@fission-ai/openspec` become
  documented prerequisites.
- Tests run against the real `openspec` CLI; no stand-in is introduced.
- Existing Builder projects gain their `openspec/` root the first time Builder
  opens a change in them, not through a migration.
