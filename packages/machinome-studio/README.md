# solid-node shop

A Claude Code plugin for building 3D-printable mechanical CAD projects
with [solid-node](https://github.com/LibreSolid/solid-node) — the
framework that treats mechanical parts as software: parametric
interfaces, unit tests, and integration contracts verified on meshes.

The plugin packages a small **shop** of specialist agents and the loop
that coordinates them, so you (the *pilot*) design and steer while the
agents do the token-heavy building, researching, and contributing.

## The shop

| Role | What it does |
|---|---|
| **you (pilot)** | Design authority. State intent, ratify decisions, judge the result by looking at it. |
| **drawing office** | Designs the mechanism and writes the machinist's spec (`docs/design.md`, `docs/specs/`). |
| **machinist** | Builds one component from a spec, test-first, one commit through the full definition of done. |
| **librarian** | Verifies a CAD-library API (cadquery, trimesh, cq_gears, OpenSCAD, three.js…) and files a recipe under `docs/notes/`. |
| **tool-design office** | The toolroom's drawing office: turns framework friction into a ratifiable OpenSpec change (proposal + delta specs + tasks) in the framework repo. |
| **toolmaker** | Implements a *ratified* OpenSpec change as a pull request to solid-node itself, one commit per task. |

You talk to Claude; Claude runs the shop, dispatching these agents and
bringing decisions back to you for ratification. The design lives in
`docs/design.md` so a fresh session picks the project up from the repo,
not from memory.

## Install

    /plugin marketplace add LibreSolid/solid-node-shop
    /plugin install solid-node-shop@solid-node

(Or point the marketplace at wherever you host this repo.) Once
installed, the `running-the-shop` skill loads whenever you start a
mechanical project, and the five agents are available as
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
git clone (latest release tag by default; pass a ref, or set
`SOLID_NODE_REPO` to your fork) installed editable, with the viewer app
and export widget built from source — so framework work, including the
whole frontend surface, is one branch away. `setup dev` upgrades a
tier-1 workspace in place; both tiers are idempotent.

On the dev bench, framework work happens in isolated git worktrees with
their own ports:

    scripts/dev-env <name> setup      # bench at WTs/<name>, branch <name>
    scripts/dev-env <name> teardown

## Use

Just describe what you want to build — "let's start a V8 engine
demonstrator", "add the next increment", "build the bearing frame" —
and Claude runs the loop:

1. **drawing office** designs the increment and writes its spec.
2. You **ratify** the design decisions (asked in plain language).
3. **machinist** builds it, test-first, one commit.
4. Claude shows you the **snapshots**; you judge the result.
5. The increment is **banked** in `docs/design.md`; on to the next.

When the framework itself gets in the way, that friction is a *wart* —
run `/file-a-wart` to propose the fix upstream.

## Contributing to the framework

The framework improves through a **ratify-then-build** loop grounded
in the framework repo's own records — `openspec/specs/` (behavioral
contracts), `docs/adrs/` (decisions), `docs/architecture.md`
(synthesis). You file a wart; the tool-design office turns it into an
OpenSpec change whose **delta specs** the maintainer ratifies; then
anyone — including your coding agent, via the toolmaker — implements
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
    scripts/
      setup                  workspace bootstrap (tier 1 plain / tier 2 dev)
      dev-env                isolated worktree benches on the framework clone
    skills/
      solid-node/            the machinist's craft manual (shared)
      running-the-shop/      the orchestration loop (the foreman reads this)
      file-a-wart/           /file-a-wart — open a framework-improvement issue
    agents/
      drawing-office.md      design + spec (product)
      machinist.md           build to spec
      librarian.md           CAD-library research
      tool-design-office.md  design + delta specs (framework)
      toolmaker.md           framework PRs
    governance/              contribution templates for the framework repo

## License

Apache-2.0
