## Why

The Curta Type I 3× project's `CounterOperatingFixtureTest` reproducibly fails while building an exact fusion: an exact leaf's stale BREP is read after its SCAD presentation has been assembled, and `shape()` hands a SolidPython `_ArtifactImport` to OCCT instead of an OCCT shape. The installed counter candidate cannot be verified against its measured parts until this existing exact-geometry promise holds.

## What Changes

- Make an exact leaf's `shape()` recover native geometry when its BREP is stale, regardless of whether the leaf has already assembled its SCAD presentation.
- Preserve current-BREP reuse and the existing exact fusion and artifact behavior.
- Add a red-first lifecycle regression and verify the originating Curta fixture.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `exact-geometry`: an exact leaf returns native local geometry after SCAD assembly when its BREP needs regeneration.

## Impact

Internal exact-leaf shape resolution, the exact-geometry conformance suite, and the Curta counter operating fixture. No public API, document format, or viewer change.
