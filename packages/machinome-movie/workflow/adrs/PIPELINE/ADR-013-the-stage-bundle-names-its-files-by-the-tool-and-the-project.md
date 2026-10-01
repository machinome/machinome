# ADR-013: The stage bundle names its files by the tool and the project, never by the machine

Status: Accepted (OpenSpec change `stable-stage-bundle`, 1 October 2026).

## Context

Each movie's stage is bundled by esbuild (`src/stage-build.mjs`) into
`<build>/stage/stage.js` and `stage.css`, with the output directory as
esbuild's working directory. esbuild names every file it bundles by its
real path relative to that directory and prints the name in the outputs:
a `// <name>` line before each module, the property name of each CommonJS
or lazily initialised module's wrapper (`"<name>"(exports, module) {`, a
string literal it escapes), and a `/* <name> */` line before each
stylesheet. The tool's runtime and React lie in the Videomaker checkout,
outside the project, so their names run from the project's `_build/` up
through the machine's directories and down into the checkout
(`../../../../../../../../../home/…/videomaker/WTs/<name>/stage/runtime.tsx`).
The bundle's key hashed `{path, sha256}` of its inputs with absolute paths.

The Curta film *Addition* got three `stageSha256` values from three
checkouts for bundles byte-identical once the prefix was masked; since
`/stage.js` is a common input of every cached shot, a render from another
checkout of the same Videomaker would recapture every frame, an hour for
that film, and `check`, the manifest and the review pack named a
different stage when nothing drawn had changed.

## Decision

1. **A bundled file is named by the first root it lies in**, each root by
   its real path: a file of the output directory keeps esbuild's name
   (`entry.tsx`); the tool's `stage/` gives `videomaker/stage/<file>`; the
   tool's `node_modules/` gives `videomaker/node_modules/<file>`; the
   project repository gives `project/<path in the repository>`; any other
   file keeps esbuild's name, relative to the output directory. The tool
   is tried before the project, so a project that contains the tool still
   names the runtime as the runtime.
2. **The outputs are rewritten where esbuild prints a name, before they
   are written.** The bundle is built with `write: false`; in the script a
   line that is only `// <name>`, or only a string literal naming a
   bundled file followed by `(…) {`, and in the stylesheet a line that is
   only `/* <name> */`, where `<name>` is one of the metafile's inputs, get
   the D1 name. A literal is decoded as esbuild writes it (either quote,
   `\xHH`, `\uHHHH`, `\u{…}`) and the new one is double-quoted with every
   character beyond ASCII escaped. A wrapper's property name is read only
   as the object's one own property, so renaming it changes no behaviour;
   no code, order or rule is touched, and no source map is written.
3. **The key is over names and content.** The runtime's sources, each
   module and every file the previous build read are hashed under their
   D1 names, without the generated entry; `inputs.json` records them by
   name, and reuse maps each name back to the building checkout's files
   and hashes them there. A checkout reuses a bundle another checkout of
   the same content built.
4. **A file with no root keeps a machine-dependent name**, and is not
   refused: the bundle is correct, only not location-independent. No film
   imports such a file.

## Options considered

- **Minify.** Removes the comments but keeps the wrappers' names, and
  changes every byte of the code.
- **An esbuild plugin that loads every file from its own namespace**, so
  esbuild prints the plugin's names itself. It takes over resolution and
  loading, and with them how esbuild decides a file's module kind from
  `package.json`, which changes the code, not only the names: built
  without the tool's `package.json` above it (a first draft of this
  change's test), the runtime's imports of React became `__toESM(…)`
  instead of `__toESM(…, 1)`. Not built.
- **Links in the output directory** to the tool, its packages and the
  project, with `preserveSymlinks`, so esbuild's own names are stable. A
  link from a project's `_build/` back to the project is a loop in the
  project's tree, and `preserveSymlinks` changes resolution for every
  package.
- **Mask the checkout prefix when hashing** in `check` and the renderer.
  The bytes served would still differ while the records claimed them
  equal, and the shot cache's key composition is not this decision's.

## Consequences

- Two checkouts of the same tool content, building the same project
  content wherever either lies, write the same `stage.js` and
  `stage.css`; `check`'s `Stage:` line, the manifest's `stageSha256` and
  `stageCssSha256` and the shot cache's common key no longer depend on the
  checkout, so a render from another checkout reuses verified shots.
- The bundle's comments read as names (`// videomaker/stage/runtime.tsx`,
  `// project/videos/addition/stage.tsx`) rather than paths; the
  `metafile.json` beside the bundle still records esbuild's paths on the
  machine that built it.
- Every film's `stage.js` changes bytes once with this change, so each
  film's next render recaptures once, as for any change of the runtime.
- If a later esbuild prints a name in another place or form, the layer 4
  proof that two checkouts write the same bytes fails; the esbuild version
  is in the key and pinned in `package.json`.
