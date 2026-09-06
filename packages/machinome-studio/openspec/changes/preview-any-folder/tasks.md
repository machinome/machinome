## 1. Every folder listing carries previews

- [ ] 1.1 Add red-first listing tests: a catalogue folder carries the previews
  of the first three openable entries it holds in listing order, a folder whose
  entries are folders carries entries found by descending them, a folder
  holding nothing openable carries none, and a multi-model project still
  carries its first three declared models.
- [ ] 1.2 Replace `_model_previews` with a manifest-or-entries rule fed by a
  lazy walk that stops at three, and use it for every folder `list_folder`
  emits.

## 2. The hub API reports them

- [ ] 2.1 Add a red-first API test that `GET /api/entries` reports a catalogue
  folder with the previews of the projects it holds, each fetchable from the
  screenshot route at the reported path.

## 3. Closing a project returns to its folder

- [ ] 3.1 Add a red-first end-to-end test that closing a project held by a
  folder lands the maker on that folder's listing.
- [ ] 3.2 Navigate to the entry's folder rather than the working folder when a
  project is closed.
- [ ] 3.3 Type-check and build the browser bundle.

## 4. Record

- [ ] 4.1 Run the full suite and record the result.
- [ ] 4.2 Update the architecture overview where it describes the hub listing.
- [ ] 4.3 Archive the change.
