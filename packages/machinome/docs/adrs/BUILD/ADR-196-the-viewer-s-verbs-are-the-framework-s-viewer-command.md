# ADR-196: The Viewer's Verbs Are the Framework's `viewer` Command

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`viewer-command`](../../../openspec/changes/archive/2026-10-12-viewer-command/)
**Amends:**
- [ADR-188: The browser viewer is a product of the repository, numbered with the set](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md): its sentence "Its console script `machinome-viewer` and its entry point ... keep their names"; the console script is removed
- [ADR-194: Viewers are providers behind one seam, chosen by name](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md): its clause keeping `machinome-viewer describe|serve|capture` and `python -m machinome.viewer.web` working, printing what they printed; the seam's capture request gains the camera's parts
**Related to:**
- [ADR-189: A package contributes a command through the group `machinome.commands`](ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md): a framework name is never taken by a contributor, so the viewer's verbs grow under the framework's own `viewer`
- [ADR-024: Command-first CLI grammar and duck-typed command registry](ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md): the registry of the framework's commands, which `viewer` stays in, `needs_node` false
- [ADR-193: The studio is a product of the set, reached by `machinome studio`](ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md): the studio's console script was dropped the same way, with no alias

## Context and Problem Statement

The pilot's fourth decision for Machinome 0.9 (`workflow/ongoing/release-0.9.md`
at the repository root, 12 October 2026) makes `machinome` one command, to
which the packages contribute their subcommands, and gives the viewer's
command a cycle of its own before the bump: the framework's `viewer` command
grows the viewer's verbs and dispatches to the installed provider through the
seam, since a framework name is never taken by a contributor (ADR-189);
unifying anything beyond that is deferred. The first decision bounds it: no
module of a former name, no alias.

Before this record the set had two commands for one viewer. `machinome
viewer` printed the web viewer's report and took no verb; the viewer's
distribution installed a second executable, `machinome-viewer
describe|serve|capture`, and `python -m machinome.viewer.web` ran the same
program, with a parser and code paths of its own. ADR-194 gave the framework
typed operations on every viewer and left the verbs, the console script and
the module form to this cycle.

The change's probes (design.md) found:

- Through the seam the verbs give what the viewer's command gave: five
  captures of the tutorial's counter byte-identical to `machinome-viewer
  capture`'s, the same served page, document and socket greeting, the same
  report byte for byte (probes 3, 5, 6).
- The seam's capture request carried only the `--camera` notation, which
  fixes the field of view at 22.5 degrees and has no spelling for an up
  direction or a lone field of view: a request of the notation alone changes
  `--view`'s image in 1667868 of 2073600 pixels (probe 4).
- The OpenSCAD viewer offers `capture`, of a node it presented; handed a
  staging directory it would be asked to photograph a document it does not
  read.
- One reader outside the repository runs the console script, the site's
  viewer intake; no project and no studio module does (probes 12 and 14).

## Considered Options

1. **The verbs under `machinome viewer`, dispatched through the seam, the
   console script removed, the module form running the framework's
   command** (chosen)
2. The console script kept as an alias of `machinome viewer`: refused, one
   command and no alias (the pilot's first decision); its one reader moves
   in three files
3. The console script kept as a second program: refused, two parsers and two
   code paths for the same verbs
4. The verbs as separate framework commands (`machinome viewer-serve`):
   refused, a second naming scheme beside the contributed commands' verbs
5. The verb `capture` taking `--camera` in place of `--view`, `--up` and
   `--fov`: refused by probe 4, every `--view` image would change and `--up`
   would be lost

## Decision Outcome

**The command.** `machinome viewer` keeps `needs_node` false and gains an
optional verb:

```
machinome viewer
machinome viewer describe [--viewer NAME]
machinome viewer serve --build-dir DIR [--port N] [--viewer NAME]
machinome viewer capture STAGING -o PNG [--imgsize WxH] [--time T]
                         [--view EYE,TARGET] [--up X,Y,Z] [--fov DEG]
                         [--viewer NAME]
```

With no verb it prints the web viewer's report, asked through the seam as
ADR-194 left it, and takes no option, so nothing changes its bytes. Each verb
asks the seam for the viewer `--viewer` names, else `web`, requiring the
operation it needs: `describe` the operation `embed` and prints the same
report; `serve` the operation `serve`, waits in the main thread, stops the
session and exits 0 on an interrupt, and on a termination signal stops it
and ends the process by that signal; `capture` the operation `capture` of a
viewer that reads published documents, refusing one whose
`document_versions()` is `None` with the seam's sentence and the viewers
that can. A `--time` outside [0, 1] exits 2 before a viewer is asked; a
server that cannot listen and a capture the viewer cannot make are one
`Error:` line and exit 1; the staging directory is the caller's and is never
withdrawn. Every refusal is the seam's sentence on standard error, nothing on
standard output, exit 1, and nothing is substituted.

**The address.** The web viewer's session binds the port before uvicorn
runs, and uvicorn announces its address only on a socket it binds itself,
so the session prints `Serving at http://0.0.0.0:PORT (Ctrl+C to stop)` on
standard output once the server listens, and nothing when it cannot listen;
`machinome viewer serve` and `machinome develop` both show it.

**No manifest.** The command takes no node path and acts on the installation
and on the directories it is given; it reads no project's `[tool.machinome]
viewer`, so its answer does not depend on the directory a host runs it from.

**The request.** `CaptureRequest` gains `eye`, `target`, `up` and `fov`, each
`None` when absent, beside the notation `camera`; a request naming both forms
is refused with `ValueError`. The web viewer resolves the notation into the
parts as the snapshot always has, takes parts as given, and leaves an absent
part to its own default (the whole model framed, Z up, 50 degrees).
`machinome snapshot` keeps passing the notation alone.

**The console script.** The viewer's manifest declares no `[project.scripts]`;
no alias is provided. Serve's three ignored frontend flags (`--dev`,
`--frontend-port`, `--start-frontend`) are not carried into the verb.

**The module form.** `python -m machinome.viewer.web` stays, its
`__main__.py` code unchanged; `cli.py` is reduced to a `main(argv)` that runs
the framework's command class with its own parser, as `python -m
machinome.movie` runs the movie's. One parser serves both spellings. With no
verb the module form prints the report, where it printed its help. The
provider imports the framework's command module only inside `main`.

### Consequences

- Good: one command for the viewer, one parser, every verb through the seam
  and its refusals.
- Good: `capture` reproduces the former command's images, the camera's parts
  reaching the viewer as given.
- Bad: a host that ran `machinome-viewer` stops working until it runs
  `machinome viewer`; the site's intake is one (three files of its
  repository).
- Bad: the serve verb runs the server in a thread of the command, not in the
  main thread; the served bytes, the log lines and the exit statuses are the
  same (probe 6).
- Neutral: `python -m machinome.viewer.web` with no verb prints the report
  rather than its help; `-h` prints the help.

## References

- OpenSpec change `viewer-command`: proposal, design (Decisions 1 to 15,
  probes 1 to 14), the modified capabilities `cli`, `cli-startup-cost`,
  `viewer-distribution`, `viewer-seam`, `framework-identity` and
  `user-documentation`
- `machinome/manager/viewer.py`, `machinome/viewer/__init__.py`
  (`CaptureRequest`); `packages/machinome-viewer/machinome/viewer/web/`
  (`__init__.py`'s `capture`, `cli.py`); `packages/machinome-viewer/pyproject.toml`
- `tests/test_manager_viewer.py`, `tests/test_viewer_seam.py`,
  `tests/test_cli_lazy_imports.py`, `tests/test_machinome_identity.py`,
  `tests/test_docs_structure.py`; the viewer's `tests/test_cli.py` and
  `tests/test_machinome_identity.py`; `scripts/check-dist`
