# Machinome Skills

Two assistant skills for building and reconstructing mechanical machines with
[machinome](https://github.com/machinome/machinome).

| Skill | Use it for |
| --- | --- |
| [machinome](skills/machinome/SKILL.md) | Creating and changing parts and assemblies, mechanical contracts, motion, and visual verification. |
| [machinome-simulate](skills/machinome-simulate/SKILL.md) | Adding a thin simulation layer to an existing design while preserving source geometry and recording reconstruction evidence. |

This is an instruction package using the [Agent Skills format](https://agentskills.io/specification).
It needs no Studio checkout, agent roster, vendor API key, or mandatory OpenSpec
workflow. Each skill includes its own references and can be installed separately.
Installing both provides the full workflow.

Status: initial local package, not published. Format, links, and distribution
contents can be checked locally; live behavior across assistant harnesses has
not yet been qualified. See [evaluation](docs/evaluation.md).

## Install

Copy the complete `skills/machinome/` and `skills/machinome-simulate/` directories
into a skill discovery directory for your assistant. Preserve their names,
references, licenses and notices. Check for existing installations before copying;
do not merge these with another skill of the same name.

| Assistant | Project installation | Personal installation |
| --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/` | `~/.agents/skills/` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/` | `~/.claude/skills/` |
| [OpenCode](https://opencode.ai/docs/skills/) | `.opencode/skills/` | `~/.config/opencode/skills/` |

These are documented discovery locations. Other Agent Skills hosts can use the
same folders through their own installer. The package does not depend on slash
commands, argument substitution, hooks, or particular tool names. No assistant
configuration is changed by building it.

For a project installation in Codex, for example, the resulting paths are:

```text
your-project/
  .agents/skills/
    machinome/SKILL.md
    machinome/references/mechanical-contracts.md
    machinome/LICENSE.txt
    machinome/NOTICE
    machinome-simulate/SKILL.md
    machinome-simulate/references/source-adaptation.md
    machinome-simulate/LICENSE.txt
    machinome-simulate/NOTICE
```

Ask the assistant to use the skill by name, or let its normal discovery choose
one. For example:

> Use machinome to add an adjustable shaft sleeve and prove its running clearance.

> Use machinome-simulate to assemble this printer's existing STL parts and expose
> its X, Y and Z motion. Start with the frame and X carriage.

## Runtime requirements and documentation

To implement and verify a machine, the assistant needs project file access,
command execution, and image inspection, with machinome and the appropriate CAD
tools installed in that project's environment. These skills do not install those
dependencies. An assistant without execution or image access can help plan work
but must identify the verification it could not perform.

The official documentation owns the API. The skills query Context7 when available
and use official documentation directly when it is absent or stale. They check
against the project's installed version and do not pin a Context7 library ID or
bundle an API manual. Network access is optional when matching official docs are
available locally. The skills' own version is independent of machinome's version;
the package does not promise support for an unverified runtime feature.

## Validate and build distributions

Maintainers need Python 3.10+ and the development dependency in
`requirements-dev.txt`. Skill consumers do not need the packaging tools.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check.py
.venv/bin/python scripts/check.py --build
```

On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

Validation checks metadata, names, local reference containment, license/notice
copies, and the package's two-skill layout. Building validates first and produces
three deterministic ZIP files under ignored `dist/`: the complete package and
one archive per skill. Each individual archive has a skill directory at its root,
including references and license files. Use the individual archives with hosts
that import one skill at a time. Nothing is uploaded, installed, or published.

The [evaluation cases](docs/evaluation.md) cover behavioral questions that static
validation cannot establish. Keep the entry points concise and route detailed
guidance through their references, following the
[skill authoring guidance](https://agentskills.io/skill-creation/best-practices).
When changing instructions, preserve the project's chosen scope and workflow.

## License and provenance

Copyright 2026 Luis Henrique Cassis Fagundes. Licensed under
[Apache-2.0](LICENSE); see [NOTICE](NOTICE).

The mechanical working practices were adapted from the machining and simulation
skills in Machinome Studio. This package removes Studio orchestration and local
workspace assumptions and leaves API definitions with official documentation.
Its license covers these instructions and packaging files; it does not change
the licenses of machinome, its optional tools, or a design being reconstructed.
