# The pin tumbler lock, as a running fixture

`viewer.json` is the lock's own published build, **verbatim** —
`projects/Locks/Pin_tumbler_lock`'s `_build/viewer.json`, a version 5
document of 26,278 bytes carrying two inputs (`insertion` in mm over
`[-60, 0]` and `rotation` in deg over `[-90, 90]`), six declared
instructions, sixteen coordinates, five published computed values,
fourteen edges, twenty-three bindings and eleven flexible pieces.
Nothing here edited it, and nothing here regenerates it.

Three of its spans are bounds that READ OTHER COORDINATES: `plug.turn`'s
low and high sides each reach `plug.p1.lift … plug.p5.lift` through the
bindings `_b10`, `_b13`, `_b16`, `_b19` and `_b22` — the expression
itself names no coordinate at all — and `plug.key.insert`'s low side
names `plug.turn` directly. That is the mechanism: the plug turns only
while five pins stand at the shear line, and the key is captured while
the plug stands turned.

The geometry beside it is **not** the lock's. Each of the eleven distinct
model paths the document names (fifteen references, five of them the one
driver pin) holds a stand-in binary STL of a unit cube, 684 bytes — the
same cube `tests/fixtures/pascaline` uses — so the whole fixture is about
80 kB instead of 3.2 MB. This repository tests a run, not a mesh: what
the acceptance asks of these files is that a mesh exists at each path.
