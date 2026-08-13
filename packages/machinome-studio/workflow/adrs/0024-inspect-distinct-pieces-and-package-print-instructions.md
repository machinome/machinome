# ADR 0024: Inspect distinct pieces and package deterministic print instructions

**Status:** Accepted

**Date:** 2026-08-13

**Deciders:** Pilot

**Origin:** OpenSpec change `add-build-inspection`

**Depends on:** [ADR 0004](./0004-static-build-artifact-boundary-for-functional-model-inspection.md)

## Context

The framework now publishes content-derived printed-piece identity, quantity,
provenance, extents, volume, and watertightness in the completed
`viewer.json`. Studio needs to turn that publication into a useful Build area
without claiming to be a slicer or inventing manufacturing conclusions the
framework did not publish.

The assembly viewer cannot show one representative piece against a
scale-related printer bed: it mounts a complete document, owns its scene, and
auto-frames the assembly. The maker also needs a portable download that says
which distinct STL files to print and how many copies, without exposing an
internal machine-readable manifest as the primary instruction.

## Decision

Build is an inspection-only fourth workspace area. It consumes the completed
published piece inventory and renders one canonical STL for the selected piece
in a dedicated Three.js scene. That scene contains a fixed 250 × 210 mm bed and
250 × 210 × 220 mm wireframe volume in the same millimetre coordinate system as
the STL. It centres the piece over the bed in its modelled orientation, offers
orbit, zoom, and reset, and keeps the required instance count prominent while
showing only one representative mesh.

Studio reports the published quantity, dimensions, volume, watertightness, and
provenance. Its only derived manufacturing result is an orthogonal
axis-permutation bounding-box comparison against the fixed volume, explicitly
labelled an envelope fit rather than a printability guarantee. It does not
derive orientation, supports, time, mass, material, slicer settings, or a
multi-copy layout.

The browser refreshes the inventory from atomic `viewer.json` publications and
reconnections carried by the existing session stream. Piece id preserves the
selection across publications. Build adds no polling or lifecycle connection.

A session-scoped download route generates a ZIP on demand from the same
verified artifact root. It includes exactly one canonical STL per distinct
piece and a deterministic `README.md` table naming each file and required copy
count. The archive orders pieces by content id and fixes entry timestamps,
permissions, compression, and names. It publishes neither a manifest nor a
persistent project artifact. Unsafe, missing, malformed, or non-STL model
references reject the whole package.

## Alternatives considered

- Add print time, material, supports, and orientation from the prototype.
  Rejected because those require printer, material, and slicer policy that the
  current publication does not provide.
- Arrange every required copy on the plate. Rejected for the first version
  because collision, spacing, rotation, and packing policy are separate from
  inspecting one distinct piece; quantity remains explicit instead.
- Reuse the functional-model widget with a CSS plate behind it. Rejected
  because its independent auto-framing would make the apparent size
  relationship false.
- Put `manifest.json` in the download. Rejected in favour of basic human-facing
  Markdown instructions that state the files and quantities directly.
- Assemble the ZIP in the browser or publish it into `_build`. Rejected because
  verified path handling belongs at the server boundary and inspection must
  not mutate the framework publication.

## Consequences

### Positive

- The maker sees a truthful, scale-aware representative piece and an
  unmistakable required count.
- Build remains useful without pretending that envelope fit proves
  printability.
- An unchanged publication and STL set produces byte-identical download
  contents.
- The package is immediately understandable without a dedicated manifest
  consumer.
- Existing Model, Code, Agents, conversation, and publication flows remain
  unchanged.

### Negative / trade-offs

- Three.js duplicates rendering machinery already embedded inside the
  framework viewer bundle and increases the browser bundle.
- A fixed build volume cannot represent another printer until a later profile
  capability exists.
- Bounding-box fit can reject no genuinely fitting orthogonal orientation, but
  says nothing about stability, supports, clearances, or slicer behaviour.
- Package generation reads and compresses every distinct STL on demand.

### Neutral

- Piece identity and measured facts remain framework-owned.
- The ZIP is ephemeral response data and never enters project Git state.
- Multiple placed instances and animation do not create additional package
  files because the published content id defines the distinct piece.
