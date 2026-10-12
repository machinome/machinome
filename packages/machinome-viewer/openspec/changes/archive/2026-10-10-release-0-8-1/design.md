## Context

The viewer was renumbered once before: 0.7.1 was the published 0.7.0
renumbered with Machinome 0.7.1 (archived `2026-09-27-release-0-7-1`).
This change repeats that shape for 0.8.1.

## Goals / Non-Goals

**Goals:** every version statement says 0.8.1, released with Machinome
0.8.1 on 10 October 2026; the changelog says nothing in the widget, the
server or the capture changed; the built distributions report 0.8.1, API
29, document versions 1 to 13.

**Non-Goals:** no source change, no API or document-version move; the
push, the upload, Read the Docs and Context7.

## Decisions

1. **Renumber, as 0.7.1 did.** The framework's extras require the viewer
   its manual declares, 0.8.1. Keeping the viewer at 0.8.0 would break the
   numbering both repositories state and the framework's floor test.
2. **API 28 and 29 stay "the 0.8.0 release".** They arrived in 0.8.0; the
   compatibility page's first list names the current release, 0.8.1, and
   its history sentence keeps 0.8.0.
3. **The removed root `openscad.py` and the corpus test are not
   changelog entries.** Neither was in a distribution (the wheel packages
   `machinome_viewer` only); a reader can use neither.

## Risks / Trade-offs

- [Order of uploads] → `machinome[viewer]` 0.8.1 does not resolve until
  this package is on the index; the release record says to upload it
  first.
