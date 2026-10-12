## Why

A multi-model project and a catalogue directory both reach the hub as folder
cards, and both draw the same word `folder` in the preview area. The maker
cannot tell `3DPrintedClocks`, a directory holding two clock repositories, from
a repository declaring two clock models: the two cards are identical apart from
their names.

They are not the same thing. A catalogue folder is an arbitrary grouping of
unrelated projects and has no picture of its own. A multi-model project is one
machine, and the shop already keeps a rendered preview of every model it
declares. Those pictures are the honest way to say what the card holds.

## What Changes

- A folder card standing for a project repository that declares several models
  shows the previews of its first three declared models, in the order the
  manifest declares them, laid side by side across the card's preview area.
- A model that has no preview yet keeps its slot in that row, showing the same
  placeholder a project card shows, so the row says how many models are being
  previewed rather than silently collapsing.
- A catalogue folder — a directory holding project repositories — keeps the
  folder glyph it has today. It owns no model and gains no picture.
- Hub state carries the entry path and current revision of each previewed
  model, so the browser fetches each picture from the screenshot route it
  already uses for that model's own card.

## Capabilities

### Modified Capabilities

- `hub-folder-navigation`: A folder card standing for a multi-model project
  previews its models rather than showing the folder glyph.
