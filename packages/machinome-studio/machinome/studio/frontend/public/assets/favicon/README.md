# The studio's favicon

The identity's white linkage symbol on a black rounded plate: the reverse
treatment of the Machinome identity (white on a black ground, the dots
showing the ground) given its own ground, so that it reads on light browser
chrome as a black chip and on dark chrome as a white symbol. It is
deliberately not the identity release's orange favicon, which machinome.org
wears, so a studio tab and a site tab tell apart.

`scripts/build-favicon` writes this directory from the intact
`../brand/v1/mark-white.svg`: the symbol's path is copied verbatim, the plate
and the placement (radius 24 on the 100-unit canvas, symbol at 78%) are the
studio's. Rebuild here rather than editing a file by hand, and bump the
`?v=` on the links in `floor/frontend/index.html` when the icon changes,
because browsers cache favicons hard.
