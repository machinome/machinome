## Why

`solid-node` is easily confused with Tim Berners-Lee's Solid project and its
existing node clients. The framework needs the distinct Machinome identity for
its 0.7 release while preserving the complete history and explicitly narrating
the transition from solid-node 0.6.

## What Changes

- Rename the framework repository to `machinome-framework` under the
  `machinome` GitHub organization and the Python distribution to `machinome`.
- Define the framework as the source-code framework for a machine and Machinome
  as the wider body and organization of machine source code and resources.
- Release the next framework line as `machinome` 0.7.0 with migration notes,
  changelog and release documentation that identify solid-node 0.6.0 as its
  direct predecessor and preserve the repository's full history.
- **BREAKING**: rename the Python package `solid_node` to `machinome`, the
  `solid` command to `machinome`, `SOLID_NODE_*` environment/configuration
  names to `MACHINOME_*`, and `[tool.solid-node]` project configuration to
  `[tool.machinome]`. Do not ship a parallel legacy import package or legacy
  CLI alias in 0.7.
- Rename the emitted export identity to `machinome-export`; readers accept the
  legacy `solid-node-export` identity so committed 0.6 exports remain usable.
- Provide `viewer`, `mechanics`, and `studio` extras selecting
  `machinome-viewer`, `machinome-mechanics`, and `machinome-studio`. State that
  the studio extra cannot install from an index until the still-experimental
  studio is published.
- Rename the viewer entry-point/process contract to `machinome.viewer` and
  `machinome-viewer describe|serve|capture`, retaining the process boundary and
  licensing separation.
- Update source paths, tests, fixtures, examples, current specs, docs, status,
  release material, URLs and automation. Preserve archived OpenSpec changes,
  accepted ADR wording, and earlier release notes as historical evidence, with
  a new ADR and current synthesis explaining the rename.

## Capabilities

### New Capabilities

- `framework-identity`: Define the canonical distribution, import, command,
  configuration, repository, version-transition, extras, and legacy-artifact
  identities of the Machinome framework.

### Modified Capabilities

- `cli`: Rename the executable and its environment/project configuration
  surface.
- `viewer-distribution`: Rename the optional viewer distribution, entry point,
  process command and installation remedies.
- `build-viewer-artifacts`: Emit the Machinome export identity while retaining
  readable 0.6 artifacts through the coordinated viewer.
- `sphinx-embedding`: Rename the embedding directive and copied-resource
  identity.
- `user-documentation`: Narrate the 0.6 to 0.7 rename and publish only current
  Machinome installation, import, command, repository, and extras guidance.

## Impact

Every framework source import, console invocation, environment key, project
manifest, package path, test, fixture, documentation page, current spec and CI
configuration is affected. Downstream projects must migrate imports and
commands. The viewer, mechanics, studio and package-name-holder repositories
are coordinated dependencies. No remote push, index upload, tag, or release is
authorized by this change.
