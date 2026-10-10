## Why

Videomaker's curta-video campaign films the clocked Curta
(`projects/Calculators/Curta-Type-I-3x`, model `clocked_curta` =
`simulation.clocked:ClockedCurta`) by recording a take through the public
`Sim`. In the workspace, `projects/` is a symbolic link to
`/mnt/data/machinome-projects`. Run from the symlinked project path, with
that path on `PYTHONPATH`, `Sim(ClockedCurta())` fails:

    PermissionError: [Errno 13] Permission denied: '/mnt/home'

raised in `machinome/node/base.py` `_make_build_dirs`. Run from the real
path it works. Recorded in Videomaker's spike note
(`videomaker/workflow/ongoing/curta-video-campaign/spike.md`, section 2
"The scenario in Python" and "What the cycles must know", item 4) and
filed in the
framework's `workflow/warts.md`, "Three findings from filming the clocked
Curta (1 October 2026)", finding 1.

The cause is a path measured between a resolved path and an unresolved
one. The node's build directory is
`normpath(join(<build root>, relpath(<node source dir>, <project root>)))`.
The project root is discovered through `os.path.realpath`
(`machinome/manifest.py` `_find_manifest`), so it is
`/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`. The node's
source directory is `inspect.getfile(type(node))`, the module's `__file__`
as Python imported it, so through the symlinked `PYTHONPATH` it is
`/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/simulation`.
Their relative path climbs four levels out of the build root and back down
the symlinked spelling; normalised, the build directory becomes
`/mnt/home/asa/devel/machinome/projects/…/simulation`. On this machine
`/mnt` is not writable and the constructor raises; on a machine where the
climb lands somewhere writable, the node quietly builds outside its
project.

The build-pipeline contract already says a command resolves "the same
artifact paths from any directory", anchored on the discovered root. A
project reached through a symbolic link is the same project; the contract
did not say so, and one input of the build directory did not honour it.

What the Curta film does with the result: its evaluation records the take
through `Sim` from whichever path the project is reached by, the
workspace's symlinked `projects/` included, and stops having to run from
the real path.

## What Changes

- **A node's source file is taken as a resolved path.** The one input of
  a node's artifact paths that was not resolved, its own source file, is
  resolved where it enters the node (`AbstractBaseNode.__init__`), so the
  project root, the source directory its artifacts mirror and its source
  closure are all resolved paths, and no artifact path is computed between
  a resolved path and an unresolved one.
- **One build directory per node, whichever path reached it.** A node
  imported through a symlinked path builds in the same directory as the
  same node imported through the real path, under the project's own build
  root, so a build warmed through one spelling is current through the
  other.
- The build-pipeline requirement "Project root discovery and model
  reference" says so, with a scenario for a project reached through a
  symbolic link.

Nothing about what a build directory is called or where a project's build
root is changes; a project reached by its real path builds exactly where
it built before.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `build-pipeline`: "Project root discovery and model reference". The
  discovered root and every source path measured against it are resolved
  paths, so a project reached through a symbolic link has the same root,
  source closure and artifact paths as through its real path.

## Impact

**Framework code.** `machinome/node/base.py`, `AbstractBaseNode.__init__`:
`self.src` is the resolved source file. Every adapter that overrides
`get_source_file` (`StlNode`, `StepNode`, `OpenScadNode`, `JScadNode`)
already returns a resolved path, so they are unchanged.

**The CLI.** `machinome export`, `test`, `build` and `develop` construct
their nodes through the same constructor, so they are covered by the same
change. The spike found `machinome export` unaffected from the symlinked
path, because the loader puts the resolved project root first on
`sys.path` and the modules it imports carry resolved `__file__` paths; the
build directory no longer depends on that.

**Tests.** A new test file builds a temporary project and a symbolic link
to it, imports a node class through the link with the working directory on
it, constructs the node and a `Sim` over it, and asserts the build
directory is under the project's build root and equal to the one reached
through the real path.

**Docs.** The changelog's `Unreleased` section
(`docs/project/changelog.rst`); the reference sentence in
`docs/concepts/node-tree.rst` that a command behaves the same from any
directory gains "and through any symbolic link to the project";
`docs/architecture.md`'s build-pipeline paragraph states the resolved
anchor.

**Not changed.** The viewer, Videomaker, the Curta project, the document,
the names of build directories and the location of a project's build root.
No ADR: this restores what the contract already promises with the anchor
every other path of the build already uses.

**Downstream.** The studio's `shop-skills/machinome-api/SKILL.md`
sentence "so every command behaves identically from any directory" gains
the same clause, in the studio repository, after the merge.
