## 1. Hub listing carries model previews

- [ ] 1.1 Add red-first listing tests: a multi-model project's folder listing
  carries its first three declared models as entry paths with their revisions
  in manifest order, a model without a screenshot carries a null revision, a
  project declaring more than three carries exactly three, and a catalogue
  folder carries none.
- [ ] 1.2 Give `FolderListing` its `previews` field, populate it in
  `list_folder` for a multi-model project only, and emit it from
  `browser_value()`.

## 2. The hub API and stream report them

- [ ] 2.1 Add a red-first API test that `GET /api/entries` reports a
  multi-model project's folder entry with the previews of its declared models,
  each fetchable from the screenshot route at the reported path.
- [ ] 2.2 Confirm the hub snapshot carries the same listing the entries route
  does, so a browser opening the stream sees the previews without a second
  request.

## 3. The folder card draws them

- [ ] 3.1 Render up to three model previews side by side in a folder card's
  preview area when the entry carries previews, keeping the placeholder for a
  model whose revision is null, and keep the folder glyph when it carries none.
- [ ] 3.2 Style the row so each tile takes a third of the preview width, and
  keep the card height and preview allocation the hub grid already specifies.
- [ ] 3.3 Type-check and build the browser bundle.

## 4. Record

- [ ] 4.1 Run the full suite and record the result.
- [ ] 4.2 Update the architecture overview where it describes the hub listing.
- [ ] 4.3 Archive the change.
