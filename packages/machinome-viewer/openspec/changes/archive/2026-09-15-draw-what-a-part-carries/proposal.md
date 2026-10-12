## Why

A Curta's answer is the angular position of ten printed number rolls, and a
Pascaline's is the digit each drum shows through its window. Both machines are
modelled, driven and run in this viewer today, and both are **unreadable**: the
digits are not on the parts, so the maker turns the crank and the machine gives
no answer — which for a calculator is the one thing it is for.

The framework has just closed its half. solid-node's `carry-markings-on-a-part`
(ADR-120, merged at `8d29cf5`) lets a rigid part declare what it **carries** on
its surface without declaring a solid, builds one surface-mesh artifact per
marking, and publishes it in the document. Nothing draws it yet. This is the
second of the three cycles `solid-node/workflow/docs/markings.md` §8 stages —
"Viewer: draw it" — and it is what makes those machines readable in a browser.

## What Changes

- **The viewer draws what a part carries.** Every entry of a rigid node's
  `markings` list is loaded through the same path the node's own `model` takes
  and drawn inside that node's own group, in the marking's own colour.
- **The contract consumed**, from solid-node's `export` capability, requirement
  **"Manifest contract"**: a rigid node's entry MAY carry `markings`, one entry
  per declared marking in declaration order, each with `name`, a `model`
  reference under the same rules and portability guarantee as the node's own,
  `color` in `#RRGGBB`, and its own `mtime` — the marking artifact's, not the
  node's. The key is absent when the node declares none. No placement is
  published: the artifact already holds the artwork's surface in the part's own
  frame. No `piece`. The list is **additive** and moves no document version, so
  a marked document may declare any version this viewer reads, 1 to 5.
  Requirement **"Export artifact contents"** guarantees the artifacts are
  copied under `models/` in an export, so a marked export stays self-contained.
- **The decal is drawn over the surface it lies on.** The artifact carries no
  offset — solid-node's design D5 states the anti-z-fighting offset is the
  *viewer's* rendering constant, not a claim about where the part's surface is
  — so the viewer supplies it as a polygon-offset bias and never as geometry.
- **A marking is not a part.** It is not a navigator row, not a focus or a
  visibility target of its own, not in a host's assembly readback, not in the
  piece inventory, and in no measurement this viewer reports. It is a region of
  a part's surface, and it goes wherever the part goes.
- **A decal reloads on its own currency.** A marking artifact has its own
  `mtime`, so a targeted update refetches a decal whose `mtime` moved without
  refetching the part it is on, drops one whose entry disappeared, and routes
  an artifact-changed path to the marking that owns it.
- **A marked document is refused rather than half-drawn** when its `markings`
  cannot be read, on the same surface an unreadable `bindings` table, an
  inexecutable program and an unresolvable `controls` table already stand on.
- **A capture shows markings.** The framework already stages marking artifacts
  beside the models it copies, so `solid snapshot --renderer web` photographs
  them once the widget draws them; this cycle proves it with a marked staging.
- **The declared API version rises to 14**, this being a capability a host may
  require. `solidNodeDocumentVersions` stays `[1, 2, 3, 4, 5]`.
- **Documentation**: a README section, the Versions table row, a CHANGELOG
  entry under 0.2.0, and an ADR extracted after implementation.

### Non-Goals

- **No texture or UV mapping.** Rasterising the artwork and UV-mapping it is
  the better answer eventually (`markings.md` §7) and is not this answer: the
  pipeline produces no UV coordinates, and the decal mesh reuses the whole
  existing rigid-mesh path for nothing.
- **No placement arithmetic in the viewer.** The mesh is already in the part's
  frame. Reproducing solid-node design D4's wrap maths in TypeScript would
  grow the producer-parity problem ADR-022 exists to contain a new limb, for a
  second description of a fact the document already states once.
- **No markings in the OpenSCAD path.** That renderer is the framework's, and
  its own spec already states it draws none.
- **No version floor on the framework's `viewer` extra.** Raising what
  solid-node requires of an installed viewer is a framework change, later, and
  needs a viewer release first.
- **No DXF, process or 3MF output.** That is `markings.md` §8 cycle 3, in the
  framework, with or after 0.8.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a new requirement for drawing the markings a document's
  parts carry and for refusing a `markings` list this viewer cannot read;
  geometry currency extended to a marking's own artifact and `mtime`; the
  colour-inheritance rule stated not to reach a marking; the declared API
  version raised to 14.
- `viewer-assembly-navigation`: a marking is not a node — it appears in no
  assembly readback, is no navigator row, and is no focus or visibility target
  of its own.
- `snapshot-capture`: a staged document whose parts carry markings is
  photographed with them.

## Impact

The widget's tree (`solid_node_viewer/widget/src/tree.ts`), its document
validation (`viewer.ts`'s `assertRenderable`), its published types
(`types.ts`), `package.json`'s `solidNodeViewerApi`, the vitest suites beside
them, the Python e2e and capture suites, one new committed fixture under
`tests/fixtures/`, the README, and `CHANGELOG.md`.

`solid_node_viewer/capture.py` is expected to need **no change**: it serves the
whole staging directory, so a decal staged beside the models is already
reachable. The cycle proves that with a test rather than asserting it.

This viewer-owned change starts at main
`4cfa2513` and consumes the merged framework change `carry-markings-on-a-part`
(solid-node ADR-120, `8d29cf5`). Fixtures are exported data: this AGPL-3.0-only
package still imports nothing of the Apache-2.0 framework, and the framework
still imports nothing of it. The mechanical run, its worker engine and its
conformance corpus are untouched.

The in-flight cycle `slide-and-turn-parts` claims API 13 and modifies the same
"The viewer declares its API version" requirement and the same `package.json`
line. That is a known, expected, one-line conflict at integration, not a
dependency: neither cycle needs the other's code. No push or publication is
implied by this change.
