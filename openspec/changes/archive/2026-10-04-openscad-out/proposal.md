## Why

The pilot's finding of 4 October 2026 (`workflow/ongoing/lean-core.md`,
"Locked at the session's close", "A proper OpenSCAD removal cycle"): cycles 5
and 6 (`expression-type`, ADR-170, 171; `scad-presentation`, ADR-172, 173) were
described as taking OpenSCAD out of the core, yet they only put SCAD *writing*
behind the seam `machinome.scad_engine`. The core still presents, names,
sweeps, snapshots and coalesces SCAD: on the unmodified bench (a16d45a) the
word occurs in 41 of the core's Python modules by `grep -il` (37 by this
change's scan rule, 453 occurrences; design.md, "The gate"). Under the ruling
"Every node type is a package" (same day) a project's dependencies must say at
once what mix it makes, so the OpenSCAD family is a node package like the
others, `Solid2Node` is a second package over it, and the core mentions SCAD
nowhere but in one table of supported node types. The phase "The next phase:
the architecture ready for the split" makes this its first cycle and fixes its
gate: one acceptance test, written red first, a token and AST scan finding no
`scad` in the core outside the family and the table. Two rulings of that
phase bind it: the leaf's capability flags become one declared set on the leaf
base, and the renderer architecture is the pilot's to revisit, so this cycle
does the least that gets SCAD out.

## What Changes

- **The acceptance gate**, a permanent test: a scan of every Python module
  under `machinome/` (templates included) by token (identifiers, attribute
  names, strings, docstrings, comments) and by module path finds no `scad`,
  in any case, outside the package `machinome/node/openscad/`, the module
  `machinome/node/solid2.py`, the OpenSCAD viewer's module
  `machinome/viewers/openscad.py` and the table `machinome/node/supported.py`;
  JSCAD's own name passes, `scad` inside any other word fails. Red on the
  unmodified tree: 37 modules, 453 occurrences (design.md, "The gate").
- **The OpenSCAD family is one package, `machinome.node.openscad`**: the node
  `OpenScadNode` (defined in the package's `__init__`, its address unchanged),
  the family's leaf base with `scad_file`, `scad_code`, `generate_scad()`,
  `fn` and the STL runner, the SCAD writer (`writer`) and the binary contract
  (`binary`). `machinome/openscad/` and `machinome/scad_engine.py` are removed;
  nothing re-exports or aliases them (ADR-169). The OpenSCAD snapshot renderer
  stays at `machinome/viewers/openscad.py` and imports the package directly:
  viewers become providers behind a seam `machinome.viewer` in the phase's last
  cycle, after the root cleanup (the pilot's ruling of 4 October 2026). The writer keeps SolidPython, on evidence (design.md,
  Decision 2): SolidPython's text depends on its process-global `use`
  registry, and `OpenScadNode`'s module call needs SolidPython's SCAD parser.
- **`Solid2Node` is `machinome.node.solid2` over the package**, with
  `as_number` and the adoption of SolidPython values, which it registers with
  the expression graph as a hook when it is imported.
- **What the core keeps is nameless.** A leaf declares the artifacts it keeps
  (`kept_artifacts()`), and the build sweep keeps by that declaration, not by
  suffix (`scad_only` goes); the OpenSCAD snapshot's on-demand root `.scad` is
  published as transient in its currency record, and every build removes
  transient artifacts, so a killed snapshot leaves nothing behind. A node's presentation is the core's description
  (`present`, `presentation()`, `assemble()`), which an installed package may
  write; the core writes none. `math`, `expression_graph` and
  `core.expressions` are documented as machinome's expression language;
  `scad_expression` is renamed `closed_expression` in place (it is the core's
  `str()` of a symbolic value; design.md, Decision 7). ADR-086's assembly-phase
  coalescing goes; the generation census stays, its reuse record renamed. The
  `machinome new` template scaffolds the leaf kind the installed extras
  provide (`solid2`, else `cadquery`), and refuses naming both extras when
  neither is installed.
- **The capability flags become one declared set on the leaf base**
  (`rigid`, `flexible`, `exact`, `optimize`, `present`, `kept_artifacts`,
  `generate_stl`, the artifact paths, `base_mesh`); every `getattr` probe of
  a leaf capability with a default in the core is replaced by a direct read
  (fourteen sites, design.md, Decision 5). The leaf contract goes to
  **`CONTRACT = 2`**.
- **The core reaches a package's renderer and command through one table of
  supported node types**, `machinome.node.supported` (provisional; its
  renderer column goes with the viewer cycle): `machinome snapshot --renderer
  openscad` resolves the renderer from the table's `openscad` entry and refuses naming
  `machinome[openscad]`; the default renderer stays `openscad`; the
  `import-step` command reaches `machinome.node.step` through the table; the
  node root's export table takes its node-type rows from it.
- **A rigid leaf whose STL is not current after its materialization is
  refused, naming the node**, instead of falling through to an OpenSCAD
  launch (the base no longer launches OpenSCAD; fixes the `backend-switch`
  wart "A self-materializing leaf that publishes nothing falls through to the
  OpenSCAD path").
- **`--renderer web` and `Sim(meshes=True)` no longer call `assemble()`**:
  they prepare and build STLs only, so the per-binding snapshot STL of a
  flexible leaf is written only when a presentation is composed (the loose
  end of the plan's "State of the campaign").
- **BREAKING:** `solidpython2` leaves the required dependencies; the extras
  `openscad` (SolidPython) and `solid2` (`machinome[openscad]`) are new, `all`
  and `dev` take both. A plain install carries no SolidPython and writes no
  SCAD; `Solid2Node` needs `machinome[solid2]`, `OpenScadNode` and an OpenSCAD
  snapshot need `machinome[openscad]`; `machinome snapshot` with its default
  renderer is refused without it, naming the extra and `--renderer web`.
- **BREAKING (framework API):** `as_scad`, `scad_file`, `generate_scad`,
  `scad_code`, `fn`, `scad_authored` and the OpenSCAD runner leave the node
  and leaf bases for the family; `as_scad` is `present`; a project leaf that
  overrides `as_scad` is no longer handed to OpenSCAD (subclass `Solid2Node`
  instead). No project names any of these (grep of 4 October 2026, the
  plan's "ready for the split").

Not in this change: `jscad` and `stl` as packages, the `brep`/`mesh` rename,
the root cleanup, renderer discovery or a renderer contract, the licence,
watchdog, the package split itself (no distribution is cut).

## Capabilities

### New Capabilities

- `openscad-node`: the OpenSCAD node family as the package
  `machinome.node.openscad`, `Solid2Node` over it, the SCAD writer, the family
  leaf's own `.scad` and STL runner, SolidPython as the family's kernel
  refused at three doors, and the adoption of SolidPython values through a
  registered hook. It takes the content of `openscad-engine` and
  `scad-engine-dependency`, which this change removes (design.md, "Specs").

### Modified Capabilities

- `openscad-dependency`: the requiring paths are the family's; no SCAD-only
  project leaf path.
- `kernel-extras`: the `openscad` and `solid2` extras; SolidPython is no longer
  required; the kernel modules and the core's namers of node modules.
- `leaf-contract`: the declared capability set, `present` and `kept_artifacts`,
  no SCAD member, `CONTRACT = 2`.
- `node-model`: the render lifecycle, the adapters and the tree naming without
  `as_scad`; the family as a package at its address; the refusal of a leaf
  that produced no STL.
- `backend-neutral-materialization`: the presentation is the core's; SCAD is
  the OpenSCAD package's output; no legacy SCAD-only override.
- `build-pipeline`: the artifact layout, the sweep by declaration, the STL
  render protocol's owner, the end of assembly-phase coalescing, the
  generated imports written by the package.
- `cli`: the snapshot command's renderer through the table, the `new`
  template by installed extras, the `import-step` entry through the table.
- `web-snapshot`: the OpenSCAD renderer is the package's, refused by its
  extra; the web renderer composes no presentation.
- `stl-import`, `flexible-parts`: `present` in place of `as_scad`.
- `motion-expression-sharing`: SolidPython operands are adopted through the
  hook `machinome.node.solid2` registers.
- `kinematics`: an operation's presentation consumer is `presented(child)`.
- `vet`: `machinome.openscad` is gone from the contract members that pass.
- `viewer-distribution`: an OpenSCAD snapshot in a plain install needs the
  `openscad` extra.

Removed (by the archive task, design.md "Specs"): `openscad-engine`,
`scad-engine-dependency`.

## Impact

- **Code.** New: `machinome/node/openscad/{__init__,leaf,writer,binary}.py`,
  `machinome/node/supported.py`, `machinome/manager/templates/project/root/{solid2,cadquery}.py`.
  Removed: `machinome/openscad/`, `machinome/scad_engine.py`,
  `machinome/node/openscad.py`,
  `machinome/manager/templates/project/root/__init__.py`. Changed: the 37
  modules of design.md's red count, `machinome/viewers/openscad.py`, `pyproject.toml`, `requirements.txt`,
  `setup.cfg`. `machinome/vet/universe.toml` is unchanged: its contract is
  `machinome` whole, and `machinome.viewers` stays denied.
- **Public interface.** Projects: none of the moved names is used (grep of
  `projects/`, 4 October 2026); a project using `Solid2Node` or
  `OpenScadNode` installs `machinome[solid2]` or `machinome[openscad]`.
  `moved-names.toml` lists every moved or removed importable name and member.
- **Artifacts and documents.** No document byte and no document version
  moves; every `.scad` a family leaf writes, every node's SCAD text and the
  OpenSCAD snapshot's root text are byte-identical (design.md, Decision 2).
- **Sibling packages.** machinome-mechanics' twelve test files that pass
  SolidPython's `get_animation_time()` to machinome math meet an
  unadopted value unless `machinome.node.solid2` is imported (design.md,
  Open Questions); machinome-freecad's validation branch declares
  `leaf_contract = 1` and is refused under 2, as ADR-165 intends.
- **Docs.** `docs/architecture.md`, the install, node-type, snapshot, CLI and
  API reference pages, the changelog's Unreleased section, the campaign plan.

Originating evidence: `workflow/ongoing/lean-core.md`, sections "Every node
type is a package", "Locked at the session's close", "The next phase: the
architecture ready for the split" (the counts and the two rulings) and "State
of the campaign" (the loose ends); the pilot's rulings of 4 October 2026.
