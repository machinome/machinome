## Context

solid-node 0.6.0 is released. Its main branch has continued through substantial
unreleased work, while separate viewer and mechanics repositories have been
founded. A one-commit `machinome` name-holder exists locally for the PyPI name.
The rename is maintainer release work: the current framework itself is the
originating product, and avoiding collision with the unrelated Solid ecosystem
is the concrete need.

The desired 0.7 surface is a full product rename, not only a PyPI alias. It must
also keep published 0.6 artifacts intelligible and preserve the framework's
complete Git and architectural history.

## Goals / Non-Goals

**Goals:**

- Establish `machinome` as distribution, import package, CLI and configuration
  identity for version 0.7.0.
- Keep framework behavior unchanged except where a public identifier must move.
- Coordinate optional viewer, mechanics and future studio installations.
- Narrate the rename and migration completely and retain historical evidence.

**Non-Goals:**

- Publishing, tagging, pushing, deleting the old GitHub repository, or deciding
  registry redirects.
- A long-lived `solid_node` compatibility layer or `solid` command alias.
- Rewriting pre-0.7 ADRs, archived changes or release notes.
- Changing the node document schema merely to encode the product name.

## Decisions

### One clean runtime namespace begins at 0.7

The source tree moves from `solid_node/` to `machinome/`; imports, module
strings, templates and tests move with it. The console script becomes
`machinome`. The old distribution remains available at its last published
version but 0.7 ships no duplicate package or command. An alias was rejected
because it would double the public import surface indefinitely and keep the
conflicting identity visible in new code.

### Configuration migration is explicit

`[tool.solid-node]` becomes `[tool.machinome]` and `SOLID_NODE_*` becomes
`MACHINOME_*`. Where the framework parses these surfaces it detects former
names and emits an actionable migration error. Silently accepting both was
rejected because current configuration and docs would remain ambiguous;
silently ignoring the old table was rejected because builds could target the
wrong model.

### Product identity does not consume a schema version

New documents say `machinome-export`, but their numerical `version` continues
to describe document capabilities only. The renamed viewer accepts the legacy
format string for committed 0.6 exports. This preserves artifacts without
making new producers continue to publish the old brand.

### Extras name independent products

The framework declares:

- `viewer = ["machinome-viewer"]`
- `web-snapshot = ["machinome-viewer[snapshot]"]`
- `mechanics = ["machinome-mechanics"]`
- `studio = ["machinome-studio"]`

Viewer and mechanics remain one-way dependencies selected by extras. Studio is
also optional and current docs clearly mark it unpublished; declaring the name
now reserves the eventual installation syntax without claiming availability.

### History is linked, not rewritten

A new accepted ADR records the rename and clean-break namespace. The
architecture synthesis and current ADR/spec indexes use Machinome and explain
that older records retain solid-node terminology. Archived changes, old ADR
bodies and release notes remain byte-for-byte historical unless a current link
must be repaired. The v0.7 release note provides the narrative bridge.

### The package holder is provenance, not the product repository

The full solid-node repository is renamed to `machinome-framework` so its
history remains linear. The separate one-commit name-holder repository is moved
under the workspace's `name-holders/` collection and retained. Its code is not
merged as an unrelated history; relevant registry provenance is narrated in
the 0.7 release material.

## Risks / Trade-offs

- **Thousands of import and command references create omission risk** → use
  mechanical path-aware replacement, compile/import scans, tracked-file audits,
  the full suite and installed-wheel tests.
- **Naive replacement corrupts history** → exclude archive/ADR/release history
  from replacement and classify all remaining old-name hits.
- **Fresh installs can pass while sdists omit renamed packages** → build wheel
  and sdist, inspect them, install each in isolated environments and run a real
  import/CLI/build smoke test.
- **Downstream projects break immediately** → provide a complete migration map
  and actionable old-config errors; the clean break is deliberate and versioned
  at 0.7.
- **The unpublished studio dependency cannot resolve** → never install the
  studio extra in ordinary validation and state its unavailable status wherever
  the spelling is introduced.
- **Viewer compatibility drifts** → validate framework and viewer together
  against both `machinome-export` and committed `solid-node-export` fixtures.

## Migration Plan

1. Commit this ratified planning state alone.
2. Add red tests for package/CLI/config/export/viewer names, then rename the
   source tree and current runtime surfaces.
3. Update current specs, documentation, templates, fixtures, tooling and CI;
   add the rename ADR and v0.7 narrative.
4. Validate source, wheel and sdist, the full suite, docs, and paired viewer,
   mechanics and studio callers.
5. Sync specs, archive the change, commit the complete result, and fast-forward
   only with pilot authority.
6. After clean worktree removal, move the primary directory to
   `machinome-framework` and set the new remote without pushing.

## Open Questions

None after ratification of the clean-break namespace and the explicit
unpublished status of the studio extra.
