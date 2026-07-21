# solid-node shop

An experimental agent harness for building 3D-printable mechanical CAD
projects with [solid-node](https://github.com/LibreSolid/solid-node) — the
framework that treats mechanical parts as software: parametric interfaces,
unit tests, and integration contracts verified on meshes. This checkout has a
Codex-native configuration for current trials. Claude Code packaging remains
experimental metadata; live orchestration is implemented and tested only for
Codex for now.

The plugin packages a small **shop** of specialist agents and the loop
that coordinates them, so you (the *pilot*) design and steer while the
agents do the token-heavy building and researching.

## The shop

| Role | What it does |
|---|---|
| **you (pilot)** | Establish intent, decide consequential choices, and judge the result by looking at it. |
| **orchestrator** | A non-model process that owns Codex app-server, routes broker events, and opens or closes the three role threads. |
| **foreman** | Manages shop-floor work and communicates directly with the maker through the shop-floor broker. |
| **designer** | Maintains the project design, releases the first executable drawing quickly, then plans one evidence-producing slice ahead (`docs/design.md`, `docs/specs/`). |
| **machinist** | Builds a committed released drawing while the designer plans ahead; owns code, tests, and implementation evidence. |
| **librarian** | Verifies a CAD-library API (cadquery, trimesh, cq_gears, OpenSCAD, three.js…) and files a recipe under `docs/notes/`. |

The foreman runs the shop, dispatching these agents concurrently after the
first drawing and bringing back only consequential decisions. The deterministic
orchestrator performs the routine lifecycle and delivery work. The
design lives in `docs/design.md` and immutable released drawings, so a fresh
session picks the project up from the repo, not from memory.

## Try with Codex

Start Codex from this checkout so it loads `.codex/config.toml` and the named
specialists under `.codex/agents/`, then describe the project you want to start
or resume. The Codex path is currently a checkout-based experimental harness,
not a published plugin.

To open the persistent event-driven floor for a workspace project:

    python -m floor.orchestrator v8-engine --port 9000

The orchestrator owns one app-server and the Foreman, Designer, and Machinist
threads. The required lowercase kebab-case name resolves only to
`projects/<name>`. A missing project is created with `solid new`, initialized
as its own Git repository, and given one scaffold commit. An existing project
must already be that exact repository root. In both cases, `solid build root`
must publish a complete viewer snapshot before the HTTP listener or any agent
starts, so a reported browser URL never opens on the no-build 404 state. Idle
role threads have no active model turn and consume no tokens.

## Claude Code packaging

    /plugin marketplace add LibreSolid/solid-node-shop
    /plugin install solid-node-shop@solid-node

(Or point the marketplace at wherever you host this repo.) This packaging is
retained for future work, but the persistent broker/app-server orchestration in
this version is Codex-only and makes no tested Claude support claim.

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

    scripts/dev-env <name> setup      # bench at solid-node/WTs/<name>
    scripts/dev-env <name> teardown

**One repository per project, and never the framework's.** Each CAD
project is its **own git repository**, at `projects/<name>` in the
workspace (untracked here — your projects are yours to host). The
boundary is repository membership, not directory nesting: a project's
files must answer to the project's own repo and to no enclosing one.
The framework clone and its benches (`solid-node/WTs/`) hold framework code
only. Top-level `WTs/` holds shop worktrees only. The shop's agents verify this
boundary before every commit and refuse to cross it.

Opening the shop is the normal creation and validation boundary. Pass the
project name to the launcher; do not pass an arbitrary project path. If
scaffolding, Git setup, or the initial build fails, the launcher preserves the
project evidence but starts no floor or role process.

## Use

Just describe what you want to build — "let's start a V8 engine
demonstrator", "build the windmill", "continue toward a working
gearbox" — and the foreman runs the pipeline:

1. The foreman has one focused conversation with you about the project.
2. A fresh **designer** first writes a minimal uncommitted draft
   checkpoint, then establishes the design spine and commits a small,
   executable first drawing.
3. The **machinist** builds and tests that released slice while the designer
   develops the higher-level design and drafts the next slice.
4. The foreman inspects the code, tests, and **snapshots**; implementation
   evidence is reconciled into the next released drawing.
5. The line continues toward the project goal, stopping only when a
   consequential decision needs you.

Released drawings do not move underneath the machinist. The designer owns design
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
| designer | `gpt-5.6-luna` | low |
| machinist | `gpt-5.6-luna` | low |
| librarian | `gpt-5.6-luna` | low |

The project config limits agent depth and concurrent threads so the two-lane
pipeline does not expand into uncontrolled token-heavy fan-out. These are
evaluation defaults, not settled performance claims.

### OpenSpec capability boundary

OpenSpec is an upstream open-source dependency. Its installed workflows own
change artifacts, their dependency and validation model, implementation
guidance, synchronization, and archival. The shop invokes those supported
interfaces and consumes their reported paths and results; it does not maintain
a parallel description or implementation of OpenSpec. These workflows support
shop and framework development outside the mechanical-project roles. Drawing
Designer, machinist, and librarian receive no OpenSpec skill.

Codex specialists keep persistent role threads, receive task-local broker
assignments, and load their role and skills locally once. During bootstrap,
the foreman expects the designer
draft checkpoint within 90 seconds. Silence beyond that boundary is interrupted
and reported; it is not poked or retried with inherited history.

When the framework itself gets in the way, that friction is a *wart* —
run `/file-a-wart` to propose the fix upstream.

## Contributing to the framework

Local framework development is a separate discipline from running the
mechanical shop and does not use a shop sprint. Every solid-node mutation is
routed through [`skills/framework-change/SKILL.md`](./skills/framework-change/SKILL.md):
it opens `solid-node/WTs/<change>`, uses OpenSpec to prepare a complete planning
record for pilot interaction, and waits for explicit ratification. The cycle
then has exactly two commits—one containing only the ratified planning state,
and one containing implementation, tests, synchronized and archived OpenSpec
records, plus any architecture updates and ADRs extracted after implementation
confirms the design. Integration and publication remain separate pilot
decisions.

Agent prompts and lifecycle orchestration live only in this shop. The framework
repository owns source, tests, OpenSpec records, `docs/architecture.md`, and
`docs/adrs/`; it must not be given an `AGENTS.md` or authoritative copies of
assistant workflows.

The public community-contribution and PR workflow is a separate intended lane,
not a claim about the currently private shop protocol or its portability. Its
experimental templates live in [`governance/`](./governance):

- `ISSUE_TEMPLATE.md` → the framework repo's
  `.github/ISSUE_TEMPLATE/framework-improvement.md`
- `CONTRIBUTING.md` → the framework repo root

They remain proposed source material until the public workflow is explicitly
published and activated.

### Protocol bootstrap

The protocol lands in two repository-local changes. First this shop capability
is implemented and integrated. Then the pilot starts a separate solid-node
cycle through it to remove tracked framework-local workflow copies and align
framework-owned OpenSpec and ADR guidance. Any untracked `solid-node/AGENTS.md`
is pilot-controlled local state: remove it as cleanup when explicitly directed,
and never commit it to the framework.

## Layout

    .claude-plugin/
      plugin.json            plugin manifest
      marketplace.json       marketplace listing (this repo == marketplace)
    .codex/
      config.toml            Codex model + concurrency defaults
      agents/                Codex foreman and specialist model adapters
    scripts/
      setup                  workspace bootstrap (tier 1 plain / tier 2 dev)
      dev-env                isolated worktree benches on the framework clone
    solid-node/              the framework working copy (untracked; setup dev)
      WTs/                   framework worktrees and their bench manifest
    WTs/                     shop worktrees only (untracked)
    projects/                your CAD projects — each its OWN git repo (untracked)
    skills/
      solid-node-api/        complete public framework contract
      solid-node/            the machinist's craft manual
      running-the-shop/      the orchestration loop (the foreman reads this)
      framework-change/      non-sprint solid-node change lifecycle
      file-a-wart/           /file-a-wart — open a framework-improvement issue
      openspec-*/            vendored OpenSpec workflow skills
    agents/
      designer.md            progressive design + released drawings
      machinist.md           build/test a stable released drawing
      librarian.md           CAD-library research
    governance/              contribution templates for the framework repo

## License

Apache-2.0
