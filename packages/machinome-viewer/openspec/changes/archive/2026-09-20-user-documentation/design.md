## Context

Base: viewer main `4d575f3768587c515cdcaac426c84d507187b600`.
Worktree: `WTs/viewer-user-docs`, branch `user-documentation`.
Integration target (not authorized): viewer main.
The README contains substantial public material but no navigable manual exists.
The widget declares API 22 and document readers 1–9; package 0.2.0 is unreleased.
The package's own interfaces, CLI and committed fixtures are the source for
examples. Existing accepted ADRs remain accepted when relocated.

## Goals / Non-Goals

**Goals:** Make the viewer understandable and usable by makers and host authors;
provide complete current reference coverage and a verifiable, self-contained
Read the Docs site matching the approved mechanics/framework manuals.

**Non-Goals:** Runtime changes, new interfaces or example machines, framework
imports, a new design system, legal advice, publication or Git integration.

## Decisions

1. Use reStructuredText, Sphinx and sphinx-rtd-theme with the same pins as the
   approved mechanics manual. Curated explanations accompany explicit JS
   reference entries; coverage tests compare them to the TypeScript interfaces.
   Generated source dumps alone would not explain the distinct operating modes.
2. Split maker guides, embedding, and reference pages. Clearly distinguish native
   driver values, design-unit requests, normalized animation time, and elapsed
   machine seconds. Document the four mounts and every supported handle/options
   member, not internal exported test seams.
3. Build the actual viewer bundle with the existing npm lockfile and reuse the
   committed spinner export for the interactive manual example. Sphinx copies
   self-contained assets; no framework, CAD build or external CDN is needed.
   Node is a documentation-build prerequisite, not a reader or wheel prerequisite.
4. Move `docs/adrs/` and `docs/release-0.2.md` into `workflow/`, retain their
   contents, and fix current references. Clarify accepted ADR authority in the
   workflow index. README becomes a concise entry point to the manual.
5. Keep the intended RTD URL configurable. Document the one-time project import;
   a checked-in configuration cannot create a hosted project. Local preview and
   browser evidence precede pilot approval and spec sync/archive.

## Risks / Trade-offs

- [Reference drift] → Compare documented API entries/options with source and
  package/CLI metadata; test executable embedding snippets in Chromium.
- [WebGL and narrow viewports] → Inspect desktop/mobile screenshots and browser
  errors; load the interactive example on demand to avoid idle render loops.
- [Heavy docs build] → Only documentation Python dependencies and the existing
  widget frontend are needed; no package/CAD installation.
- [Record relocation breaks current links] → Check repository links and retain
  relative structure of all ADR files. Historical records remain historical.

## Migration Plan

No runtime migration. Users find current guidance through README and package
metadata. Framework links are a separate standalone cycle. Rollback is a Git
revert after authorized integration; no deployed service is changed here.

## Open Questions

The pilot must approve the rendered site before sync/archive. Read the Docs
project creation and publication remain the pilot's actions.
