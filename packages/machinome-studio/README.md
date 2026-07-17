# solid-node shop

A Claude Code plugin for building 3D-printable mechanical CAD projects
with [solid-node](https://github.com/lhfagundes/solid-node) — the
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
| **toolmaker** | Implements a *ratified* framework improvement as a pull request to solid-node itself. |

You talk to Claude; Claude runs the shop, dispatching these agents and
bringing decisions back to you for ratification. The design lives in
`docs/design.md` so a fresh session picks the project up from the repo,
not from memory.

## Install

    /plugin marketplace add lhfagundes/solid-node
    /plugin install solid-node-shop@solid-node

(Or point the marketplace at wherever you host this repo.) Once
installed, the `running-the-shop` skill loads whenever you start a
mechanical project, and the four agents are available as
`solid-node-shop:<name>`.

Your project still needs the solid-node framework itself installed in
its virtualenv, plus `rtree` and `scipy` for the mesh assertions.

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

The framework improves through a **ratify-then-build** loop: you file a
wart (an issue proposing an interface change), the maintainer ratifies
the interface, then anyone — including your coding agent, via the
toolmaker — implements it as a PR. The templates that make this work
live in [`governance/`](./governance):

- `ISSUE_TEMPLATE.md` → the framework repo's
  `.github/ISSUE_TEMPLATE/framework-improvement.md`
- `CONTRIBUTING.md` → the framework repo root

They ship here as the canonical source; copy them into the solid-node
framework repo to activate the flow.

## Layout

    .claude-plugin/
      plugin.json            plugin manifest
      marketplace.json       marketplace listing (this repo == marketplace)
    skills/
      solid-node/            the machinist's craft manual (shared)
      running-the-shop/      the orchestration loop (the foreman reads this)
      file-a-wart/           /file-a-wart — open a framework-improvement issue
    agents/
      drawing-office.md      design + spec
      machinist.md           build to spec
      librarian.md           CAD-library research
      toolmaker.md           framework PRs
    governance/              contribution templates for the framework repo

## License

Apache-2.0
