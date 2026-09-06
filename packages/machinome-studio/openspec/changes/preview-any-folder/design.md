## Context

`preview-multi-model-projects` gave `FolderListing` a `previews` tuple of
`(entry path, revision)` pairs and taught the folder card to draw them. It
filled that tuple for one kind of folder only, and recorded as a non-goal
"previewing a catalogue folder by reaching into the projects below it",
because walking an arbitrary depth to find a picture would make listing a
large catalogue expensive.

The pilot has since asked for exactly that, to organise the catalogue into
folders whose cards are recognisable. The cost objection is real but it was
answered too broadly: a card shows three pictures, so the walk that finds them
can stop after three. That is a bounded walk, not a full traversal, and it is
cheaper than the `holds_project` walk the same listing already performs for
every catalogue directory.

The return-to-folder half is a separate, smaller correction: the browser knows
the entry path of the project it has open and already derives the listing
folder from it in three other places; only the close path navigates to `/`.

## Goals / Non-Goals

Goals:

- One rule for filling a folder card, applied to every folder.
- Keep the browser's picture fetching on the one screenshot route, at the
  previewed entry's own path.
- Keep listing a folder proportional to what it shows, not to what it holds.

Non-Goals:

- Composing a collage server-side, or serving a folder-level picture. Each
  tile stays the previewed entry's own committed screenshot.
- Live-updating a folder card when an entry inside it is re-rendered. Hub
  events remain scoped to the folder that lists the entry; the card refreshes
  on the next listing of its parent.
- Choosing which entries a folder features. The rule is declaration order for
  a manifest and listing order otherwise; a way to pin a favourite would be a
  separate change.

## Decisions

### Decision: Previews come from the manifest when there is one, and from the folder's own entries otherwise

`_folder_previews(directory, path)` answers both kinds of folder:

- If the directory's manifest declares models, the previews are its first
  three declared models, `<path>/<model>`, in declaration order — today's
  behaviour, unchanged.
- Otherwise the previews are the first three openable entries found by
  descending the folder in listing order, each named by its own hub entry
  path.

The manifest is consulted with the existing `declared_models`, which reads
`pyproject.toml` directly and costs no subprocess. A directory that is not a
repository but carries a manifest declaring models is treated the same way as
one that is: the rule is about the manifest, not about Git.

### Decision: The walk yields entries lazily and stops at three

`_previewable_entries(directory, path)` is a generator yielding one
`(entry path, project root, model)` leaf at a time, in the order `list_folder`
would list them: multi-model repositories give their declared models, single
projects give themselves, and a directory that is neither is descended into.
`_folder_previews` takes three and abandons the generator, so a folder holding
two hundred projects reads three screenshots and stops.

A directory that turns out to hold nothing openable yields nothing, and its
card keeps the folder glyph. That is the same fallback the card already has
for an empty `previews`.

### Decision: Closing a project navigates to the folder that lists it

`closeProject` navigates to `folderUrl(folderOf(entryPath))` instead of `/`.
For `printers/kossel` that is `/folders/printers`; for
`3DPrintedClocks/wall_clock_02` it is `/folders/3DPrintedClocks`, the folder of
models; for a project at the root it is `/`, unchanged. This is the same
derivation the workspace already uses when a session turns out not to be open.

## Risks / Trade-offs

- A catalogue folder's card now depends on the screenshots of projects it
  holds, which are committed by those projects and may be missing. The card
  then shows placeholder tiles rather than a glyph. That is the same honesty
  the multi-model card already offers, and it makes an unrendered corner of
  the catalogue visible rather than hiding it behind a folder icon.
- Reading three PNGs to hash their revisions costs more than reading none. It
  is bounded per card and the pictures are small; the listing already reads one
  per project card.
