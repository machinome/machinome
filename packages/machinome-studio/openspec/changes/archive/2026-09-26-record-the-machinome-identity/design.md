## Context

The Machinome visual identity (application guide 1.0, adopted 20 September
2026) is the whole ecosystem's. It prescribes, for a product: the master
signature (the rounded linkage M with Anta's `achinome`) with a plain-text
qualifier such as `Studio` outside its clear space and in the same colour;
Space Grotesk for interface and editorial text and IBM Plex Mono for
technical text; the logo-only font never as a text face; the identity's
orange for the lockup, with body copy, code and ordinary navigation left to
the interface's own colours. Its favicon rule is orange with solid white
dots.

The studio's reference design (`docs/design/README.md`) predates the
identity: a dark desktop shell with an amber accent it calls themeable,
IBM Plex Sans and IBM Plex Mono, a 38px title bar with an amber square mark
and the typed name, and no assets. The `product-identity` spec fixes the
name `Machinome Studio` and its machine-readable form, nothing visual.

The pilot's direction was empirical: apply, assess live, then record. The
three commits on `main` are the outcome; this change records it.

## Decisions

**D1. The lockup, not the typed name.** Both title bars show the identity's
outlined white wordmark at 180 CSS px (the guide's working minimum) with
`Studio` in Space Grotesk 17px/500 beside it, 16px away, in the same
white; the bar is 50px so half an M stays clear above and below. The link
is named `Machinome Studio` for assistive technology, so the existing
requirement that the title bar identifies the product still holds. The
wordmark is an `<img>` of the release's SVG, not the logo font, as the
guide prefers for fixed logos. White is the guide's treatment on a dark
ground.

**D2. The faces.** Space Grotesk (variable, 300–700) and IBM Plex Mono
(regular only) are bundled unchanged with their OFL notices and served
from the floor's assets route; `font-synthesis: none` keeps a missing bold
from being faked. The editor uses the same mono face and re-measures once
the font is in. The logo font ships inside the intact release and is
named by no stylesheet, and a test keeps it so.

**D3. The accent stays amber.** The identity orange was applied as the
accent, assessed by the pilot and rejected as harsh against the studio's
cool dark surfaces. The guide leaves interface colour to the product, so
the reference design's amber stands; the identity's colours are declared
as tokens on `:root` and used by nothing but a future lockup.

**D4. The favicon is a product variant.** The pilot wants a studio tab to
tell apart from a machinome.org tab, which wears the release's orange
favicon. A white symbol on a transparent canvas vanishes on light browser
chrome, so the studio's favicon is the reverse treatment given its own
ground: the white symbol, its path verbatim from the release, on a black
plate. `scripts/build-favicon` derives the pack; the release's own favicon
files stay in the intact directory unused. The identity's decision history
records the variant from its side.

**D5. Asset ownership.** `brand/v1` is copied intact and pinned to its
manifest by a test; a revised identity arrives as a new versioned
directory. The favicon pack and the fonts live beside it, each directory
with its README and notices. The identity's artwork carries no public
licence; NOTICE says the marks are not under the AGPL grant.

**D6. What goes where.** The spec states what a maker sees and the two
boundaries a later change must respect (the release intact, the logo font
never text); the reference design carries the values (sizes, faces,
colours, assets). Neither restates the guide.

## Risks

- The reference design is a handoff document with the prototype's own
  values; correcting only what the identity superseded leaves it partly
  historical, which it already was. A fresh design reference is a separate
  decision.
- `docs/design/shop-desktop.html` still draws the amber mark and Plex Sans;
  it is the prototype, kept as history, not edited.
