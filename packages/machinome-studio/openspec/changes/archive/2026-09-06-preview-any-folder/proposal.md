## Why

A multi-model project's folder card now stands on the pictures of its models,
and beside it a catalogue folder still draws the word `folder`. That is the
wrong way round for the maker who is trying to organise a growing catalogue:
the folders they make to group printers, clocks, and fixtures are exactly the
cards they most need to recognise, and a grey glyph says nothing about what is
inside.

The pictures already exist. Every project repository below such a folder keeps
a committed preview of its own, reachable at its own hub entry path. A folder
card can stand on the first few of them the same way a multi-model project's
card stands on its models, and the two kinds of folder become one card shape
with one rule for filling it.

The second half is what happens on the way back. A maker who opens a model of
`3DPrintedClocks`, or a project inside a `printers` folder, and then closes it
is returned to the working folder root, losing the place they were working in
and having to walk back down. Closing a project should return them to the
folder they opened it from.

## What Changes

- Every folder card previews what it holds. A folder whose directory carries a
  manifest declaring models previews the first three the manifest declares, as
  it does today; any other folder previews the first three openable entries it
  holds, in listing order, descending into the folders it holds when its own
  entries are folders.
- An entry with no preview yet keeps its place in the row and shows the same
  absent-preview treatment a project card shows.
- A folder that holds no previewable entry at all keeps the folder glyph.
- Closing a project returns the maker to the folder that lists it rather than
  to the working folder, whether that is a catalogue folder or the folder of
  models a multi-model project presents.

## Capabilities

### Modified Capabilities

- `hub-folder-navigation`: Every folder card previews what it holds, and
  closing a project returns the maker to the folder that lists it.
