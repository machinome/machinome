## Context

`stage()` in `src/render.mjs` builds the map of URLs the session's asset
server answers: the viewer bundle, the film page, the stage bundle, the
export's `manifest.json` at `/model/manifest.json`, the pictures, and every
"model asset". It finds the model assets by walking every value of the
manifest and keeping each string that ends in `.stl`, `.png`, `.jpg`,
`.jpeg`, `.webp` or `.svg`, resolving it against the export directory,
refusing one that escapes it (`Model asset escapes export: …`), and hashing
each into `hashes`, whose non-picture entries enter the shot cache's
common key. A string that is not a file of the export reaches
`fileHash` and fails there with Node's bare `ENOENT`.

The framework's export specification (`openspec/specs/export/spec.md` of
the framework, read as the definition of the document) says what a
consumer reads from an export:

- the manifest's `root` tree: a rigid node emits one `model` reference
  "rooted beneath the export's `models/` directory with no parent
  traversal" that "SHALL resolve to a copied artifact"; a non-rigid node
  recurses into `children`; a flexible leaf emits a `flexible` object,
  which carries its shape inline and names no file;
- a rigid node declaring markings carries a `markings` list whose entries
  each carry "a `model` reference to its artifact under the same rules and
  the same portability guarantee as the node's own `model`";
- the `pieces` inventory beside `root`, whose `models` name the same copied
  artifacts (model deduplication is unchanged; the inventory is reported on
  top of it) and whose `sources` name the files a piece was built from,
  relative to the project. The widget renders the `root` tree; the
  inventory is a report.

The fixture project's exports agree: `export/seesaw/manifest.json` names
files only in `root…model` and `pieces[].models`; `export/counter/` adds
`root…markings[].model`. The Curta's `export/clocked_curta/manifest.json`
names 390 rigid `model` references (149 distinct files) and 28 marking
references (7 distinct files) under `root`; its 148 pieces name 149
`pieces[].models`, every one of them a `root` model too, and 148
`pieces[].sources`: 105 `.step`, 37 `.py` and 6 `.stl`. The six `.stl`
sources are the strings the old walk served and could not find.

## Goals / Non-Goals

Goals: serve exactly the files the viewer reads; refuse one that is missing
or escapes the export by its field in the manifest, with what to do; leave
everything else, the served set of an export without provenance file
strings included, as it was. Non-goals: those of the proposal.

## Decisions

### D1. The files are the `root` tree's model references and its markings'

A new module, `src/export.mjs`, holds what the viewer reads from an export.
`viewerFiles(manifest)` is pure: it walks the `root` tree, and for each node
takes, in the node's own key order, its `model` when it is a string, the
`model` of each entry of its `markings` list when that is a string, and the
nodes of its `children` list, depth first. It returns one entry per
distinct path, the first field that names it: `{path, field, node}`, with
`field` the JSON path in the manifest (`root.children[2].children[0].model`,
`root.children[1].markings[0].model`) and `node` the node's `name`.

Nothing outside `root` is read. `pieces[].models` name files the `root` tree
already names, and the widget does not read the inventory; `pieces[].sources`
and every other string are provenance or data.

Walking in each node's key order keeps the old walk's order for every
export: the old walk visited the same strings in the same depth-first key
order and met `pieces` after `root`, where every `models` entry was already
seen. So an export whose manifest holds no other matching string serves the
same URLs in the same order, and `hashes`, which `JSON.stringify` orders by
insertion, is byte-identical: those films keep their shot-cache common key.

Rejected: keeping the extension filter and skipping strings under `pieces`
(still guesses by extension, and serves any future provenance or data field
the framework adds); tolerating a missing file by skipping it (the viewer
would then fail on the missing model inside the browser, later and by URL,
and a provenance string and a lost model would be indistinguishable).

### D2. The refusal, before a browser opens

`exportFiles(manifestPath)` reads the manifest, takes `viewerFiles`, and
for each entry resolves the path against the export directory. It refuses,
naming the field, the node and the path the field gives:

- a path that resolves outside the export directory:
  `Export file outside the export: root.children[0].model (Base) names ../x.stl, which lies outside the export <dir>; export the model again so the manifest names only files inside it`
- a path that is not a file there:
  `Export file missing: root.children[2].children[0].model (Plank) names models/models/x.stl, which the export <dir> does not hold; export the model again so the export holds every file its manifest names`

It returns the map of URLs (`/model/<path>`) to files that `stage()` serves
and hashes as before. `stage()` runs before the session launches Chromium
or mounts the asset server, so `preview` and `render` refuse before a
browser opens. `Model asset escapes export` goes; its case is the first
refusal.

### D3. No change to the key beyond serving fewer files

The URL of a served file, its hash and the composition of the common key
are unchanged. The common key changes only for a film whose export's
manifest held a provenance or data string ending in one of the old
extensions; the Curta film's does (its six source STLs leave `hashes`), so
its 760 MB shot cache is recaptured once when it is next rendered. The
fixture exports and any export whose `pieces[].sources` name no `.stl` or
image keep their key.

### D4. No ADR

The change applies a boundary the repository already holds (the framework
is reached only through the documents it publishes, read by the fields that
document defines) and adds no structure but one pure module. ADR-013,
reserved for this cycle, is not used.

## Risks / Trade-offs

- A future export field the viewer reads (a texture, a second artifact kind)
  is not served until this module learns it; the viewer would then fail on
  that URL with a 404 that the session reports. That is the right failure:
  the framework's specification changes first, and this reading follows it.
- A manifest without `root` serves no model file; the movie checks already
  refuse a document whose parts are not in the export.
