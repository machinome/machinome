# solid-node shop

An experimental agent harness for building 3D-printable mechanical CAD
projects with [solid-node](https://github.com/LibreSolid/solid-node) — the
framework that treats mechanical parts as software: parametric interfaces,
unit tests, and integration contracts verified on meshes. This checkout has a
Codex-native configuration for current trials and also packages the existing
Claude Code plugin.

The plugin packages a small **shop** of specialist agents and the loop
that coordinates them, so you (the *pilot*) design and steer while the
agents do the token-heavy building and researching.

## The shop

| Role | What it does |
|---|---|
| **you (pilot)** | Establish intent, decide consequential choices, and judge the result by looking at it. |
| **drawing office** | Maintains the project design, releases the first executable drawing quickly, then plans one evidence-producing slice ahead (`docs/design.md`, `docs/specs/`). |
| **machinist** | Builds a committed released drawing while the office plans ahead; owns code, tests, and implementation evidence. |
| **librarian** | Verifies a CAD-library API (cadquery, trimesh, cq_gears, OpenSCAD, three.js…) and files a recipe under `docs/notes/`. |

You talk to the foreman assistant; it runs the shop, dispatching these agents
concurrently after the first drawing and bringing back only consequential
decisions. The design lives in `docs/design.md` and immutable released
drawings, so a fresh session picks the project up from the repo, not from
memory.

## Try with Codex

Start Codex from this checkout so it loads `.codex/config.toml` and the named
specialists under `.codex/agents/`, then describe the project you want to start
or resume. The Codex path is currently a checkout-based experimental harness,
not a published plugin.

## Install in Claude Code

    /plugin marketplace add LibreSolid/solid-node-shop
    /plugin install solid-node-shop@solid-node

(Or point the marketplace at wherever you host this repo.) Once
installed, the `running-the-shop` skill loads whenever you start a
mechanical project, and the three agents are available as
`solid-node-shop:<name>`.

## The workspace

The shop checkout is also your **workspace** — the rebuild of what used
to be a private development platform, now open. Clone it and bootstrap
in one of two tiers:

    scripts/setup             # tier 1 (plain): venv + pip install solid-node
    scripts/setup dev [ref]   # tier 2 (development): framework as a git
                              # working copy, editable install, frontend
                              # built from source

**Tier 1** is all you need to build projects: the wheel ships the
prebuilt viewer and widget (Python and OpenSCAD are the only system
requirements). **Tier 2** is the contributor bench: the framework is a
git clone at `solid-node/` (untracked — the shop does not pin a
framework commit, so the same shop version serves a user on the
latest release tag and a maintainer on `main`; pass a ref, or set
`SOLID_NODE_REPO` to your fork) installed editable, with the viewer
app and export widget built from source — so framework work,
including the whole frontend surface, is one branch away. `setup dev`
upgrades a tier-1 workspace in place; both tiers are idempotent.

On the dev bench, framework work happens in isolated git worktrees with
their own ports:

    scripts/dev-env <name> setup      # bench at WTs/<name>, branch <name>
    scripts/dev-env <name> teardown

**One repository per project, and never the framework's.** Each CAD
project is its **own git repository**, at `projects/<name>` in the
workspace (untracked here — your projects are yours to host). The
boundary is repository membership, not directory nesting: a project's
files must answer to the project's own repo and to no enclosing one.
The framework clone (`solid-node/`) and the benches (`WTs/`) hold
framework code only; the shop's agents verify this boundary before
every commit and refuse to cross it.

## Use

Just describe what you want to build — "let's start a V8 engine
demonstrator", "build the windmill", "continue toward a working
gearbox" — and the foreman runs the pipeline:

1. The foreman has one focused conversation with you about the project.
2. A fresh **drawing office** first writes a minimal uncommitted draft
   checkpoint, then establishes the design spine and commits a small,
   executable first drawing.
3. The **machinist** builds and tests that released slice while the office
   develops the higher-level design and drafts the next slice.
4. The foreman inspects the code, tests, and **snapshots**; implementation
   evidence is reconciled into the next released drawing.
5. The line continues toward the project goal, stopping only when a
   consequential decision needs you.

Released drawings do not move underneath the machinist. The office owns design
documents; the machinist owns project code and tests. While this workflow is
experimental, the product-side shop may not use another mechanical project as
a reference.

### Codex model defaults

The checkout includes project-scoped Codex agents under `.codex/agents/`.
The initial low-cost evaluation defaults step every role down one model tier so
the shop can establish whether its prompts are useful before spending heavily:

| Role | Model | Reasoning |
|---|---|---|
| foreman | `gpt-5.6-terra` | medium |
| drawing office | `gpt-5.6-luna` | low |
| machinist | `gpt-5.6-luna` | low |
| librarian | `gpt-5.6-luna` | low |

The project config limits agent depth and concurrent threads so the two-lane
pipeline does not expand into uncontrolled token-heavy fan-out. These are
evaluation defaults, not settled performance claims.

### OpenSpec capability boundary

The vendored OpenSpec skills support shop and framework development directly
from this repository, outside the mechanical-project shop roles. Drawing
office, machinist, and librarian receive no OpenSpec skill.

Codex specialists start with fresh task-local context and load their role and
skills locally once. During bootstrap, the foreman expects the drawing-office
draft checkpoint within 90 seconds. Silence beyond that boundary is interrupted
and reported; it is not poked or retried with inherited history.

When the framework itself gets in the way, that friction is a *wart* —
run `/file-a-wart` to propose the fix upstream.

## Contributing to the framework

Framework development is a separate discipline from running the mechanical
shop. It remains grounded in the framework repo's own records —
`openspec/specs/` (behavioral contracts), `docs/adrs/` (decisions), and
`docs/architecture.md` (synthesis). A wart can become an OpenSpec change whose
**delta specs** the maintainer ratifies; a contributor then implements
it as a PR, and the merged change is archived back into the specs
(and an ADR, when architectural). Conformance bugs — code violating
what the specs already promise — skip ratification and go straight to
a red-first PR. The templates that make this work live in
[`governance/`](./governance):

- `ISSUE_TEMPLATE.md` → the framework repo's
  `.github/ISSUE_TEMPLATE/framework-improvement.md`
- `CONTRIBUTING.md` → the framework repo root

They ship here as the canonical source; copy them into the solid-node
framework repo to activate the flow.

## Layout

    .claude-plugin/
      plugin.json            plugin manifest
      marketplace.json       marketplace listing (this repo == marketplace)
    .codex/
      config.toml            foreman model + concurrency defaults
      agents/                Codex specialist model adapters
    scripts/
      setup                  workspace bootstrap (tier 1 plain / tier 2 dev)
      dev-env                isolated worktree benches on the framework clone
    solid-node/              the framework working copy (untracked; setup dev)
    projects/                your CAD projects — each its OWN git repo (untracked)
    skills/
      solid-node-api/        complete public framework contract
      solid-node/            the machinist's craft manual
      running-the-shop/      the orchestration loop (the foreman reads this)
      file-a-wart/           /file-a-wart — open a framework-improvement issue
      openspec-*/            vendored OpenSpec workflow skills
    agents/
      drawing-office.md      progressive design + released drawings
      machinist.md           build/test a stable released drawing
      librarian.md           CAD-library research
    governance/              contribution templates for the framework repo

## License

Apache-2.0
