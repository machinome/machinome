## ADDED Requirements

### Requirement: A part read from a model file is drawn from its positions alone

A part read from a model file SHALL be held, in the page and in the viewer's graphics context, as its vertex positions without any normal: the viewer SHALL keep neither the normals the file carries nor normals of its own for it. Each of its facets SHALL be drawn flat, lit by the normal of the facet's own plane on the side that faces the viewer, whichever way the facet's triangle is wound, in every look a part takes: plain, hovered, highlighted, dimmed or ghosted, with or without a colour.

At a pixel reached by a facet seen within about one pixel of edge-on, or by a triangle of nearly zero area, that facet's or triangle's share of the pixel MAY be lit as from another direction, as a flexible part's already is; every other pixel of a part SHALL show its facet lit by its own plane.

A marking SHALL be drawn as before, with its own smoothed normals, its lift and its material, whether or not it names the file its part names, and a flexible part SHALL be drawn as before. Holding no normals SHALL NOT change what a press, a hover or a part control reaches, a part's bounds or position on screen, the order of drawing, the requests a page makes, or which parts share one geometry.

#### Scenario: Parts hold their positions alone

- **WHEN** a document whose parts name model files is mounted, reloaded, updated in place or mounted by a second viewer in the page
- **THEN** every geometry its parts are drawn from holds no normals, and the graphics buffers the viewer uploads for it hold none: for a file without per-facet colours, its positions alone, twelve bytes a vertex

#### Scenario: A facet is lit by its own plane

- **WHEN** a part whose triangles are wound outward, a part whose triangles are wound inside out and a part with no colour are drawn
- **THEN** each facet seen is drawn flat, lit by one normal over its whole face, from the side facing the viewer: none is black, and the faces' brightnesses follow their directions to the lights

#### Scenario: Every look keeps the shading

- **WHEN** a part is hovered, highlighted with the others kept, dimmed or ghosted, or hidden and shown again
- **THEN** it is drawn flat and lit from the side facing the viewer as in its plain look, in that look's colours

#### Scenario: A facet seen edge-on or a triangle of no area

- **WHEN** a part has a facet seen within about one pixel of edge-on, or a triangle of nearly zero area that the browser still draws
- **THEN** only the pixels that facet or triangle reaches may be lit as from another direction, and every other facet of the part is lit by its own plane

#### Scenario: Markings and flexible parts are drawn as before

- **WHEN** a document whose parts carry markings, one of them naming its part's own file, and whose tree holds flexible parts is mounted
- **THEN** each marking is drawn lifted over its surface with its own smoothed normals, from the same geometry and material as before, and each flexible part is drawn as before

## MODIFIED Requirements

### Requirement: The viewer draws the markings a part carries

The viewer SHALL draw every marking a rigid node of the published document
carries, one per entry of that node's markings list, each from the artifact the
entry names and in the colour the entry declares. A marking SHALL be drawn in
its part's own place, moving with the part under every pose, animation instant
and committed mechanical state the part moves under, with no placement supplied
by the viewer: the artifact holds the artwork's surface in the part's own frame,
and the part's own operations place it.

A marking SHALL be drawn OVER the surface it lies on, from every viewing
distance and angle at which the part itself is drawn, and SHALL NOT be broken
up by the surface it marks. The bias that achieves this is the viewer's own
rendering constant and SHALL NOT be presented as, or derived from, anything the
document states about where the part's surface is. A marking whose artwork is
open on both sides SHALL be drawn from either side.

A node that carries no markings SHALL be drawn exactly as it is drawn when its
document carries no marking at all: the same geometry, the same material and
the same scene contents, nothing being added to it for markings. A document
whose nodes carry no markings SHALL be rendered, read back and photographed
identically to the same document published before markings existed.

The viewer SHALL draw markings on a document of any schema version it renders:
the markings list is additive to the document and is gated on no version.

#### Scenario: A part's markings are drawn in their own colours

- **WHEN** a document is mounted whose part carries two markings declaring
  different colours
- **THEN** both are drawn on that part, each in the colour its own entry
  declares, and the part is drawn in the colour it declares

#### Scenario: A marking goes where its part goes

- **WHEN** a driver, an animation instant or a mechanical command moves a part
  that carries a marking
- **THEN** the marking moves with it, arriving in the same place on the part's
  surface it started on, without the viewer computing any placement for it

#### Scenario: A marking is visible over the surface it marks

- **WHEN** a marked part is photographed from a viewpoint that sees the marked
  surface
- **THEN** the marking's colour is what is seen where the marking is, and the
  part's is what is seen where it is not

#### Scenario: A marking on a colourless part

- **WHEN** a document is mounted whose marked part inherits no colour
- **THEN** the part renders with the normal-based material and its marking
  renders in its own declared colour

#### Scenario: A marked document below the running version

- **WHEN** a document that declares an early schema version carries markings on
  its parts
- **THEN** its markings are drawn, exactly as a later version's are

#### Scenario: An unmarked document is untouched

- **WHEN** a document whose parts carry no markings is mounted
- **THEN** it renders exactly the picture this viewer renders of the same
  document published before markings existed, and its scene contains nothing
  a marking would have added
