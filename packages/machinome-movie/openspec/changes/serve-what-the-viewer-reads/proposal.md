## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, filming the clocked model
`clocked_curta` through its export). Its finding is wart 1 of the section
"Addition (Curta, 1 October 2026)" of `workflow/warts.md`:

> `preview` and `render` serve every `.stl` or image string in the manifest
> as an export asset and fail with a bare `ENOENT`.

`stage()` in `src/render.mjs` walks the whole export manifest with a regular
expression on file extensions and serves every match as a file of the
export. The framework's export names each printed piece's source files in
`pieces[].sources`, paths relative to the project that are provenance, not
files the export holds and not files the viewer reads. The Curta's
imported pieces name six `.stl` files under `STLs/`, so `preview` stopped on
the first of them with `ENOENT … export/clocked_curta/STLs/…`, a refusal
that names neither the manifest field nor the cause. The film worked
around it with a symlink `export/clocked_curta/STLs -> ../../STLs` in its
untracked export, which its README documents as a workaround.

## What the film does with the result

The Curta project's export loses the symlink: `machinome export` alone makes
an export the film's `check`, `preview` and `render` accept, and the README's
`ln -s` step and its paragraph explaining the workaround go (the
orchestrator removes the workaround at the merge). Any later film whose
export names provenance files is filmed without one; a film whose export has
lost a model file is refused by `preview` and `render` naming the manifest
field, the file, and that the model must be exported again.

## What Changes

- **The stage serves the files the viewer reads, and only those.** Which
  files those are is read from the fields of the framework's export
  document, not from file extensions: every node of the `root` tree's
  `model` reference, and the `model` of each entry of a node's `markings`
  list. `pieces[]` (its `models` and its `sources`) and every other string
  in the manifest are not served and not read.
- **A missing or escaping file the viewer reads is refused by field.** The
  refusal names the field path in the manifest (`root.children[2].children[0].model`),
  the node it belongs to, the path the field gives and that the export does
  not hold it, and tells the reader to export the model again. It is made
  before a browser opens. A provenance string naming a file that does not
  exist changes nothing.
- **The served set is otherwise what it was.** The files are collected in
  the manifest's order, each once, so an export with no provenance file
  string serves the same URLs in the same order and its films keep their
  shot-cache common key; an export whose provenance strings were served
  before (the Curta's six source STLs) serves fewer files, so its common key
  changes once.
- **Proofs**: a pure test of the collection over the fixture project's real
  exports and edited copies (layer 2's neighbour, no browser); layer 8 runs
  the fixture movie `minimal` through `preview` and `render` with a
  provenance source that does not exist, and refuses both with a model file
  missing.
- **Records**: `README.md` (what the asset server exposes),
  `docs/architecture-overview.md` (the new module), `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `educational-video-production`: the renderer serves the export files the
  viewer reads, refusing one that is missing by its manifest field.

## Impact

Code: `src/export.mjs` (new: what the viewer reads from an export),
`src/render.mjs` (`stage()` calls it); tests `test/export.test.mjs` (new) and
`test/pipeline/movie-pipeline.test.mjs`. No change to the movie document,
its schema, the stage, the Python side, the viewer or the framework. The
shot-cache common key changes only for an export whose manifest held a
provenance string ending in a served extension.

## Non-goals

The framework's manifest, the viewer, the Curta film's source. No change to
how assets are hashed into the shot-cache key beyond serving fewer files.
`check` does not open the export's model files (it never served them; the
refusal is made by `preview` and `render` before a browser opens). No
publication, push or paid request.
