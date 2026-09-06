## Context

`FolderListing` is one dataclass serving two different things: a catalogue
directory holding project repositories, and a project repository declaring
several models. Both reach the browser as `{"kind": "folder", path, name,
projects}` and both draw the placeholder word `folder`. The maker has no way to
tell them apart, which is the problem this change fixes.

Every previewed model already has an openable hub entry of its own — the path
`<project>/<model>` — and the screenshot route already serves that entry's
picture at `GET /api/screenshot?path=<entry>&revision=<revision>`. Nothing new
has to be served; the folder card only needs to know which entries to ask for.

## Goals / Non-Goals

Goals:

- Distinguish the two kinds of folder card at a glance, using pictures the shop
  already renders and commits.
- Keep the browser's picture fetching on the one screenshot route.

Non-Goals:

- Composing a single collage image server-side. Three `<img>` elements cost one
  cached request each and stay correct when one model is re-rendered.
- Previewing a catalogue folder by reaching into the projects below it. Such a
  directory owns no model, and walking an arbitrary depth to find one would
  make listing a large catalogue expensive.
- Live-updating a folder card when a model inside it is re-rendered. Hub events
  are scoped to the folder that lists the entry, so a model's screenshot event
  reaches browsers listing that project's own folder. The card refreshes on the
  next listing of its parent.

## Decisions

### Decision: A folder listing carries the entry paths and revisions it previews

`FolderListing` gains `previews`: a tuple of `(entry path, revision or None)`
pairs, empty for a catalogue folder and holding up to three entries for a
multi-model project. `browser_value()` emits them as a `previews` array.

The alternative was to let the browser derive the model entry paths by entering
the folder — a second request per card — or to have it guess them from the
project path, which would require it to know the manifest. Carrying the paths
is one field on a listing the hub already builds.

Revisions are read with the same `screenshot_revision` the project cards use,
so a card and the collage tile of the same model always agree, and the revision
in the URL keeps the browser cache honest when a model is re-rendered.

### Decision: Three, in manifest order, with placeholders kept

Three fits the preview area at a third of its width each without shrinking a
640x360 thumbnail past recognition, and the pilot asked for three. The order is
the manifest's declaration order, which is the order the folder's own listing
uses, so the card and the folder behind it read the same way.

A model without a preview keeps its slot rather than being skipped: skipping
would make a two-model project and a three-model project with one unrendered
model draw the same card. The slot shows the project card's placeholder.

### Decision: The catalogue folder keeps its glyph

A directory holding repositories has no model of its own, and its projects'
previews would be a picture of something one level further away than the card
stands for. The glyph continues to say "this is a place, not a machine", and
now says it only about places.
