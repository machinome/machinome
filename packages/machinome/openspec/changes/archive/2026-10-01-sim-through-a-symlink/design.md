## Context

A node's artifact paths are fixed in `AbstractBaseNode.__init__`:

    self.src = self.get_source_file()            # inspect.getfile(cls)
    self.basedir = os.path.dirname(self.src)
    root = project_root(self.src)                # realpath'd in _find_manifest
    self.build_dir = normpath(join(get_build_dir(self.src),
                                   relpath(self.basedir, root)))

Every path but one in that computation is resolved:

- `manifest._find_manifest` resolves its origin before walking up, so the
  project root is always a resolved path;
- `project_build_root` joins the build root onto that resolved root;
- `source_closure` and `source_scope` (`machinome/node/sources.py`) key
  every file by its resolved path, and `currency.source_digest` measures
  each against the resolved root;
- the loader resolves every path it imports and checks containment by
  resolved paths (`loader._within`, `import_module_from_path`);
- the adapters resolve their own sources (`StlNode.stl_source`,
  `StepNode.step_source`, `OpenScadNode.openscad_source`,
  `JScadNode.jscad_source`).

The exception is the plain Python node's source file,
`inspect.getfile(cls)`: the module's `__file__` exactly as the import
system found it, which is unresolved when the module was imported through
a `sys.path` entry that contains a symbolic link (a symlinked
`PYTHONPATH`, or a script run by a symlinked path). Then
`relpath(basedir, root)` is measured from an unresolved directory to a
resolved one, climbs out of the build root and lands wherever the climb
happens to end: `/mnt/home/…` for the Curta, which cannot be created.

The CLI does not usually meet this, because the loader inserts the
resolved project root at the front of `sys.path` before it imports a
project module; the modules then carry resolved `__file__` paths. A Python
caller such as Videomaker's take recorder imports the project itself.

## Goals / Non-Goals

**Goals.**
- A node's build directory lies under its project's build root whichever
  path the project was reached by.
- The same node reached through a symbolic link and through its real path
  has the same build directory, so a cache warmed through one is current
  through the other.

**Non-goals.**
- What a build directory is called, where a project's build root is, and
  how an absolute `SOLID_BUILD_DIR` is used: all unchanged.
- A project whose own source tree contains symbolic links pointing outside
  it. The loader's and `vet`'s existing rules about sources leaving the
  root are unchanged.
- The viewer and Videomaker.

## Decisions

### 1. The anchor is the resolved path

Every side of an artifact path is a resolved path. The project root is
already resolved by discovery, and every tracked source by the closure;
the node's own source file is resolved where it enters the node, in one
place:

    self.src = os.path.realpath(self.get_source_file())

so `basedir`, the `relpath` against the root, the `files` and `scope`
seeds, `self.root` (the directory an assembly's generated SCAD imports
are measured from), and every later `get_build_dir(self.src)` all agree.

Why resolved rather than written:

- **It is the one the framework already uses.** Discovery, the source
  closure, the content digest, the loader's containment check and every
  adapter resolve. Resolving the one remaining input changes one line;
  anchoring on the written path would mean un-resolving all of them.
- **It is unique.** A project has one resolved path and any number of
  written ones (two symbolic links, a bind mount, a relative
  `PYTHONPATH`). The build-pipeline contract gives a project one build
  root and, derived from it, one build lock per model; anchored on the
  written path, each spelling would get a private build tree and a
  private lock, the very failure the "never the working directory" rule
  exists to prevent.
- **It shares the cache.** With both sides resolved, the build directory
  reached through the symlink is byte for byte the one reached through
  the real path, so an artifact built through either is current through
  the other.

The entry point is `__init__`, not `get_source_file`, because subclasses
override `get_source_file` (the four adapters do); resolving at the single
call site covers every override, and costs the adapters nothing since
their paths are already resolved.

### 2. The CLI is covered by the same line

`machinome build`, `test`, `export` and `develop` construct their nodes
through the same constructor, so whatever path a module was imported by,
they now compute the same build directory. They were not observed to
fail, because the loader seeds the resolved root first on `sys.path`; the
build directory no longer depends on that ordering.

### 3. No new refusal

The change adds no error and changes no message. A node whose source
genuinely lies outside its project (a symbolic link inside the project
pointing elsewhere) is decided by the rules that already decide it.

## Alternatives rejected

- **Anchor on the written path** (un-resolve the root): see decision 1;
  it multiplies build roots and locks per spelling and contradicts every
  other resolved path of the build.
- **Resolve only `basedir` in the one `relpath`.** Smaller, but leaves
  `self.src` unresolved while `files`, `scope` and the root are resolved,
  and leaves `self.root` unresolved for an assembly's SCAD imports, so a
  parent and a child imported through different spellings would still
  measure relative imports across the mix. One anchor where the path
  enters is the coherent fix.
- **Refuse a source reached through a symbolic link.** The workspace
  layout that produced the finding is ordinary; refusing it would turn a
  bug into a rule.
- **Catch the failure in `_make_build_dirs`.** It would hide the wrong
  path, and on a writable filesystem there is no failure to catch: the
  node silently builds outside its project.

## Risks / Trade-offs

- `node.src` now reads as the resolved path where it used to read as the
  imported spelling. Nothing in the framework compares it against an
  unresolved path (the one other reader, `flexible.py`, resolves it
  itself); a project test that compared `node.src` with a symlinked
  spelling would see the resolved one. The suite is the check.
- `os.path.realpath` is one more `lstat` walk per node construction, on a
  path whose prefixes the OS caches; negligible beside the source closure,
  which already resolves the same file.
