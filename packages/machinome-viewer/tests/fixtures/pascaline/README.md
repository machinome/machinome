# The Pascaline module, as a running fixture

`viewer.json` is the Pascaline module's own published build, **verbatim**
— `projects/Calculators/Pascaline-module`'s `_build/viewer.json`, a
version 5 document of 32,994 bytes carrying three inputs, nine joint
coordinates, six intermediates, nine edges and three `floor` jump plans.
Nothing here edited it, and nothing here regenerates it.

The geometry beside it is **not** the module's. Each of the fifteen model
paths the document names holds a stand-in binary STL of a unit cube, 684
bytes, so the whole fixture is about 43 kB instead of 1.5 MB. This
repository tests a run, not a mesh: what the acceptance asks of these
files is that a mesh exists at each path and that its world matrix moves
when the bank behind it moves. A cube shows that as well as a digit drum
does, and costs a thousandth of the bytes.
