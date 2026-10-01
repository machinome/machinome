## Context

`buildStage` (`src/stage-build.mjs`) writes `<build>/stage/entry.tsx`, which
imports the runtime (`<tool>/stage/runtime.tsx`) and each stage module by
absolute path, and bundles it with esbuild into `stage.js` (IIFE, not
minified, no source map, `legalComments: 'none'`) and `stage.css`, with
`absWorkingDir` the output directory. esbuild names every bundled file by
its path relative to `absWorkingDir`, after resolving symlinks, and prints
that name in three places:

- a line comment before each module's code in the script,
  `  // ../../../../../../../../../home/…/videomaker/WTs/x/stage/runtime.tsx`;
- the property name of each CommonJS module's wrapper,
  `__commonJS({ "../../…/node_modules/react/index.js"(exports, module) {`,
  and of a lazily initialised ES module's (`__esm({ "…"() {`), as a string
  literal: double-quoted, with non-ASCII characters escaped (`\xE7`,
  `ł`, `\u{1F600}`), single-quoted when the path holds a double quote;
- a block comment before each stylesheet in `stage.css`,
  `/* ../../stage.css */`.

The project's own modules are named relative to the build directory, which
lies in the project, so they are stable; the tool's runtime and its
packages are named through the machine's directories to the checkout. The
key is `hash({inputs: [{path, sha256}], modules, stageBlock, versions})`
with absolute paths, the previous inputs read back from esbuild's
`metafile.json` by resolving its relative names against the output
directory.

The renderer serves `stage.js` and `stage.css` and puts their content hashes
in the shot cache's common key; `check` prints the hashes; the manifest
records them.

## Goals / Non-Goals

Goals: the same tool content and the same project content bundle to the
same bytes, wherever either lies; the bundle's key is the same, so a
second checkout reuses a bundle the first built. Non-goals: those of the
proposal.

## Decisions

### D1. Name every bundled file by a root the content defines

Each file esbuild read is named by the first root it lies in, in this
order, each root taken by its real path (esbuild resolves symlinks, and a
worktree's `node_modules` is a link to the primary checkout's):

1. the output directory: the name esbuild gives it (`entry.tsx`);
2. the tool's `stage/`: `videomaker/stage/<path below it>`;
3. the tool's `node_modules/`: `videomaker/node_modules/<path below it>`;
4. the project repository (`project`, which every module already must lie
   in): `project/<path below it>`;
5. anything else: the name esbuild gave it, unchanged.

The tool is named before the project so that a project containing the tool
(or the tool's own fixture project, inside the checkout) still names the
runtime as the runtime. The names are injective: distinct files have
distinct names, since the roots are tried in one order and each name
carries its root's prefix, and esbuild's own names in the output directory
hold no `/` prefix of those words. `project/` names the repository, not the
movie's directory: the module paths a document lists are relative to its
root, but the repository is what `checkModules` already holds every module
inside, and a module's own imports may reach elsewhere in it.

The fifth case is a file a stage module imports from outside its
repository and outside the tool. It has no root but the machine's; its
name stays machine-dependent and is not refused, because the bundle is
still correct. No film imports one.

### D2. Rename what esbuild printed, in the places it prints names

esbuild has no option to print a name of the caller's choosing for a file
it reads from disk; a plugin that loads every file from its own namespace
would print `namespace:name`, but would take over resolution and loading,
and with them how esbuild decides a file is CommonJS or an ES module (the
`package.json` `type` field) and its side effects, which change the
bundle's code, not only its names. So the bundle is built as before with
`write: false`, and its two outputs are rewritten before they are written,
line by line, only where esbuild prints a module's name:

- in the script, a line that is only `// <name>` where `<name>` is a key of
  the metafile's inputs, and a line that is only a string literal naming
  such a key followed by `(…) {` (a wrapper's method). The literal is
  decoded (both quotes, `\\`, `\'`, `\"`, `\xHH`, `\uHHHH`, `\u{H…}`), so a
  name esbuild escaped is still found; the new name is written as a
  double-quoted literal with every character beyond ASCII escaped as
  `\uHHHH`;
- in the stylesheet, a line that is only `/* <name> */`.

The metafile's inputs are exactly the files esbuild bundled, so no other
line can be taken for a name except a comment of identical text, which
only changes a comment. A wrapper's property name is read by the runtime
helper only as "the object's one own property" (`__getOwnPropNames(cb)[0]`),
never by value, so renaming it changes no behaviour. `metafile.json` is
written as esbuild produced it: it is the build's record of what it read
on this machine, not part of the bundle.

### D3. The key over names and content

`computeKey` hashes `{inputs: [{path: <name>, sha256}], modules, stageBlock,
versions}`: the runtime's sources, each module and every file the previous
build read, each under its D1 name, without duplicates, the entry left out
(it is generated from the runtime's location and the modules list, both
already in the key, and it holds the checkout's absolute paths).
`inputs.json` records the inputs by name. Reuse re-reads the previous
build's inputs from `inputs.json`, mapping each name back to a file of the
checkout that is building (`videomaker/stage/x` to its own `stage/x`, and
so on; an unchanged esbuild name against the output directory), and
re-hashes them there. A second checkout of the same content therefore
computes the same key over the same names and the same bytes, finds the
outputs as recorded, and reuses the bundle the first one wrote; a second
checkout whose runtime differs in a byte rebuilds. The metafile is no
longer needed for reuse.

### D4. Nothing the browser runs changes

The rewrite touches comments and the wrapper's property names only; the
order of modules, the code and the stylesheet's rules are esbuild's. The
fixture films' frames are the proof: the slow suite's renders keep their
shot caches' frame hashes before and after the change.

### D5. Tests

Layer 4, in `test/stage-types.test.mjs`, which already builds the tour's
stage in a temporary directory: two copies of the fixture tour at
different depths, one built by this checkout and one by a copy of the
tool's `src/` and `stage/` in the temporary directory (its `node_modules` a
link to this checkout's), give the same `stage.js` and `stage.css` bytes
and hashes, and every module comment in the script is a D1 name (no
`../`, no temporary directory, no checkout path). Then the copy of the tool
builds the first project into the first build directory and reports
`reused` with the same hashes. These are pure tests; no memo is involved.

## Alternatives rejected

- **Minify the bundle.** It drops the comments but keeps the wrappers'
  path names, and changes every byte of the code.
- **A namespace plugin** that names each file itself (D2): it changes how
  esbuild classifies modules, so the code changes, not only the names.
- **Symlinks in the output directory** (`link/stage`, `link/node_modules`,
  `link/project`) with `preserveSymlinks`, so esbuild's own names are
  stable: a link from a project's `_build/` back to the project is a loop
  in the project's tree, and `preserveSymlinks` changes resolution for
  every package.
- **Mask the checkout prefix when hashing** in `check` and the renderer:
  the served bytes would still differ while the records said they were the
  same, and the shot cache's key composition is out of scope.
- **Hash only the runtime's relative paths in the key and leave the
  bundle's names alone**: the key would reuse a bundle whose bytes the
  other checkout would not have written.
