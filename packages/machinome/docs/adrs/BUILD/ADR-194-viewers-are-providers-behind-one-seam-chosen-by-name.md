# ADR-194: Viewers Are Providers Behind One Seam, Chosen by Name

**Status:** Accepted; its clause keeping `machinome-viewer` and the module form printing what they printed, amended 2026-10-12 by [ADR-196](ADR-196-the-viewer-s-verbs-are-the-framework-s-viewer-command.md): the viewer's verbs are `machinome viewer`'s, and the capture request carries the camera's parts
**Date:** 2026-10-12
**Change:** [`viewer-seam`](../../../openspec/changes/archive/2026-10-12-viewer-seam/)
**Supersedes:**
- [ADR-068: Optional viewer package behind a process boundary](../EXPORT/ADR-068-optional-viewer-package-behind-a-process-boundary.md), in what [ADR-188](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md) left of it: the lookup through the entry point `machinome.viewer` and the process boundary
- [ADR-188](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md), its paragraph "The seam is unchanged" and its sentence on `machinome vet`
**Amends:**
- [ADR-179: The core reaches a node package's renderer and command through the table of supported node types](ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md): the renderer column is removed; the table states classes and commands
- [ADR-183: An extension package is a namespace portion in its own distribution](ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): an extension package may be a portion of `machinome.viewer`
- [ADR-191: The videomaker is a product of the set](ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md): the films take the viewer's bundle through the seam
**Related to:**
- [ADR-103: The browser is the only interactive development viewer](ADR-103-the-browser-is-the-only-interactive-development-viewer.md): unchanged; the OpenSCAD viewer takes stills and serves nothing
- [ADR-176](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md) and [ADR-162](../NODE/ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md): the engines' seams, a provider at a known address declaring its contract version, which this seam is modelled on
- The viewer's own decision log, `packages/machinome-viewer/workflow/adrs/`, whose decisions stand

## Context and Problem Statement

The pilot's eighth decision for Machinome 0.9 (`workflow/ongoing/release-0.9.md`
at the repository root, 12 October 2026) puts the viewer seam inside 0.9, on
the outline of 4 October 2026 ("The last cycle of the phase: `viewer-seam`",
`packages/machinome/workflow/ongoing/lean-core.md`): the word is viewer, never
renderer; viewers coexist and are chosen by name behind one seam with
Protocols and an integer contract version; an absent viewer is refused by its
extra, a wrong contract as incompatible, an operation a viewer lacks by name,
and nothing is substituted; the web viewer's staging moves into its provider;
the renderer column of the table of node types and the core's
`machinome/viewers/` go; the commands take `--viewer <name>`.

The core reached its two viewers in two unrelated ways. The OpenSCAD one was a
row of the table of node types (`machinome.node.openscad.renderer`, ADR-179's
provisional column). The web one was found through the entry-point group
`machinome.viewer` and run as a subprocess, `python -m machinome.viewer.web
serve|capture` (ADR-068, kept by ADR-188), a process boundary that existed for
a licence difference the one licence removed. `machinome snapshot` compared
the string `'web'` in four places and called different methods on each. The
viewer joined the repository on 12 October 2026 at `machinome.viewer.web`, the
address the outline gives its provider.

The change's probes (design.md) found that the seam resolves both providers
editable and from the wheels when its `__init__.py` extends its path; that the
manual's snapshot example draws the same pixels through the seam as before,
through each viewer; that the web viewer serves and captures in the
framework's process, a rebuild reaching the open page as a message on its
socket instead of a server restart; and that removing the entry point breaks
the manual's build, which found the published viewer only through it.

## Considered Options

1. The seam at `machinome.viewer`, both viewers its providers, the web viewer
   in the framework's process (chosen)
2. A seam module beside an empty `__init__` (`machinome.viewer.seam`);
   refused: the outline names the `__init__`, as the engines' seams are
3. Discovery by entry points; refused: a provider is found at a known
   address, and the group is what this change removes
4. The OpenSCAD viewer as a second portion of `machinome-node-openscad`;
   refused: a node distribution would ship an address outside
   `machinome.node`, and the outline gives the viewer its own distribution
5. The web viewer serving in a child process the provider owns, restarted as
   before; refused: a second interpreter and a dropped socket per rebuild for
   nothing the thread does not give

## Decision Outcome

**The seam.** `machinome/viewer/__init__.py` of the core declares the
contract: `CONTRACT = 1`; the operations a viewer may offer, `present`,
`capture`, `serve` and `embed`, with what each asks as Protocols (`Viewer`:
its name, contract, operations, identity, the document versions it reads and
whether a version is readable; `Presenter`; `Capturer` with the snapshot
options it honours; `Server` and `Session`, reload and stop; `Embedder`, its
files and its report); `CaptureRequest`, the snapshot's options; the viewers
the core knows with the extra that installs each (`EXTRAS`) and each
operation's default viewer (`DEFAULTS`), the only place the core names a
viewer's technology. It imports the standard library and `machinome.extras`
alone, and its path is extended with the portions other distributions ship
(`machinome._namespace_portions`).

**Resolution and refusals.** `viewer(name)` imports `machinome.viewer.<name>`
and nothing else. A viewer the core knows that cannot be found is refused by
its extra (`ExtraUnavailable`, naming the install line); an unknown name names
the viewers; a provider whose `CONTRACT` differs, or that declares none, is
incompatible; `require(name, operation, needed_by)` refuses an operation the
viewer does not offer, naming what needs it and the viewers that offer it. A
refusal a provider's own import raises (the OpenSCAD node package or
SolidPython absent) passes unmodified. A provider's operational failure is a
`ViewerError`, its message the sentence a command writes. A viewer is never
replaced by another.

**The default rule.** A command chooses by its `--viewer`, else the project's
`[tool.machinome] viewer`, else its operation's default: `snapshot` the
OpenSCAD viewer, `develop` and `export` the web viewer. No availability is
consulted. A project's viewer that lacks the command's operation is refused
naming the key and the flag. The manual's build and the films read no
manifest and ask the web viewer.

**The web viewer.** `machinome.viewer.web` of `machinome-viewer` offers the
four operations; resolving it, asking its identity or whether it reads a
document version imports no web framework or browser driver. Its `present`
builds the STLs and stages the posed node (`stage.py`, the core's former
`machinome/viewers/browser.py`); its `capture` photographs the staging
directory in the caller's process; its `serve` runs the development server in
a thread the provider owns, on a port bound before the thread starts, and
returns a session whose `reload` sends `reload` on every open page's socket
and whose `stop` returns when the server has stopped. The entry point is
removed; `machinome-viewer describe|serve|capture` and `python -m
machinome.viewer.web` keep working.

**The OpenSCAD viewer.** `machinome.viewer.openscad`, the distribution
`machinome-viewer-openscad` at `packages/machinome-viewer-openscad/`, the
former `machinome.node.openscad.renderer`, offers `present` and `capture`,
reads no document and honours every snapshot option; it requires the core and
`machinome-node-openscad` with the set's pins. The extra `viewer-openscad`
installs it, and so do `openscad` and `solid2`.

**The commands.** `machinome snapshot`, `develop` and `export` take
`--viewer <name>`; `snapshot` refuses `--renderer`, exit status 2, naming
`--viewer`, and reaches no table of node types; `develop` serves through the
session and reloads the page in place; `export` embeds the files the chosen
viewer gives. `machinome viewer` prints the web viewer's report, unchanged.
`machinome vet` denies `machinome.viewer` whole.

**What goes.** `machinome/viewers/`, the table's renderer column with
`DEFAULT_RENDERER` and `renderer()`, the entry-point group
`machinome.viewer`, every run of `python -m machinome.viewer.web` by the
framework, the classes `OpenScadRenderer` and `BrowserRenderer`, the logger
`viewers.openscad` (now `viewer.openscad`). No module of a former name is
kept.

### Consequences

- Good: one seam, one contract version, one set of refusals for every caller
  of the set; the snapshot names no viewer; a third viewer is a provider at
  an address and a row of `EXTRAS`.
- Good: the web viewer is one process with the command; a rebuild reaches the
  open page without the offline banner a restart showed.
- Bad: the manual builds the repository's viewer, its bundle built by npm
  first, in Read the Docs, CI and `make docs`; the published viewer is hidden
  behind the source core.
- Bad: one more distribution of the set to version, build and smoke.
- Neutral: the web stack shares the develop process; a server that cannot
  listen is refused before any builder starts.

## References

- OpenSpec change `viewer-seam`: proposal, design (Decisions 1 to 16, probes
  1 to 17), the capability `viewer-seam` and the modified capabilities
  `web-snapshot`, `cli`, `viewer-distribution`, `kernel-extras`,
  `framework-identity`, `openscad-node`, `vet`, `user-documentation` and
  `release-tooling`
- `packages/machinome/workflow/ongoing/lean-core.md`, "The last cycle of the
  phase: `viewer-seam`"
