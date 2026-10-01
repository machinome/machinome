## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`). Two cycles of the
addition-warts campaign that checked and previewed it from their own
worktrees met the same finding (`workflow/warts.md`, "Findings met by the
campaign's cycles", 15; `serve-what-the-viewer-reads`, evidence finding 2;
`honest-provenance`, evidence finding 3):

15. **The stage bundle's hash depends on the checkout that built it.**
    esbuild writes, before each module it bundles, a comment naming the
    module by its path relative to the build directory, and names each
    CommonJS module's wrapper by the same path. For the tool's runtime and
    React those paths run up out of the project and down into the
    Videomaker checkout (`../../../../../../../../../home/…/videomaker/WTs/<name>/stage/runtime.tsx`).
    The Curta film therefore has three `stageSha256` values,
    `e5c7bccec003`, `c82a3718550a` and `6298cd57909a`, from three
    checkouts, for bundles that are byte-identical once the checkout
    prefix is masked. The stage build's own key (`src/stage-build.mjs`,
    `computeKey`) hashes `{path, sha256}` with absolute paths, so a second
    checkout rebuilds the bundle rather than reusing it even when the bytes
    would be the same.

It matters because `/stage.js`, as served, is a common input of every
cached shot (`src/render.mjs`, `commonKey`): the Curta film rendered from
another checkout of the same Videomaker recaptures all 3 787 frames, an
hour of capture, for a bundle that differs only in comments. `check`'s
`Stage:` line, the render manifest's `stageSha256` and, through the
manifest, the review pack all say "a different stage" when nothing the
viewer draws has changed.

## What the film does with the result

The Curta film's stage is built from two checkouts of the same Videomaker
content and gets one `stageSha256`, so `check` from any checkout prints
the same `Stage:` line and a render from a second checkout reuses the
shots the first captured instead of recapturing them for a comment. The
next render of *Addition* (from whichever checkout the pilot uses) pays
the stage change once, because the bundle's bytes change with this
change, and never again for the checkout.

## What Changes

- **The bundle names its modules, not the machine's paths.** Every path
  the bundle embeds (esbuild's comment before each module and stylesheet,
  and the key of each CommonJS or lazily initialised module's wrapper) is
  rewritten to a name relative to a root the content defines: the tool's
  runtime as `videomaker/stage/<file>`, the tool's packages as
  `videomaker/node_modules/<file>`, a file of the project repository as
  `project/<path in the repository>`, and the generated entry as
  `entry.tsx`. Two checkouts of the same tool building the same project
  content, wherever either lies, write the same `stage.js` and
  `stage.css`.
- **The bundle's key hashes content and those names**, not absolute paths:
  the runtime's sources, each module, every file the previous build read
  and the stage block, each under its name, and the versions as before.
  `inputs.json` records the inputs by name, and reuse re-reads them by name
  from the checkout that is building, so a second checkout reuses a bundle
  the first built when the content is the same, and reports `reused`.
- **Nothing the browser runs changes.** Only comments and the wrappers'
  property names (which the runtime never reads by value) are rewritten;
  no source map is written, as before. The fixture films' frames are the
  same bytes before and after.
- **Proofs**: layer 4 (`test/stage-types.test.mjs`): the tour's stage
  built from two copies of the fixture project at different depths, by
  this checkout and by a copy of the tool's `src/` and `stage/` elsewhere,
  is the same bytes and names no machine path; the copy reuses the
  bundle this checkout built. The suites whole, the fixture films'
  frame hashes before and after, and `check` of the Curta film from two
  checkouts.
- **Records**: ADR-013 (PIPELINE); `docs/stage.md` ("Rebuilt by
  content"), `docs/architecture-overview.md`, `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `react-stage`: the stage bundle is the same bytes, and its key the same,
  from any checkout of the tool and any location of the project.

## Impact

Code: `src/stage-build.mjs` only; test `test/stage-types.test.mjs`. No
schema, contract page, Python, stage runtime, renderer or viewer change.
The shot cache's key composition is unchanged. Every film's `stage.js`
changes bytes once (its comments now carry names), so every film's next
render recaptures once, as for any change of the runtime; after that, the
checkout no longer enters it.

## Non-goals

Which inputs the shot cache's common key hashes (out, by the brief). The
viewer bundle (another repository). A file a stage module imports from
outside the project repository and outside the tool keeps the path
esbuild gives it, relative to the build directory, since there is no root
to name it by; no film does this, and it is recorded, not refused. No
minification, no source maps, no change of the film. No publication, push
or paid request.
