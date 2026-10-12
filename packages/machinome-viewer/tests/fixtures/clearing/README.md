# The Curta's clearing interface, as a version 6 fixture

`viewer.json` is the framework's own test machine
`tests/clearing_project/machine.py:CurtaInterface`, exported **verbatim**
from a throwaway copy of machinome at main `8e15791` — 16,153 bytes, a
**version 6** document: one driver (`clearing`), six coordinates
(`result0.turn`, `result1.turn`, `result2.turn`, `counter0.turn`,
`counter1.turn`, `counter2.turn`), thirty bindings, one piece, and **six
law edges each of whose `needs` intersects its own `gives`**. That
intersection is the whole of what makes the document version 6: no key
was added for a law that reads the coordinate it drives.

Nothing here edited the document and nothing here regenerates it. It was
produced with

```
PYTHONPATH="$PWD" machinome export \
    tests/clearing_project/machine.py:CurtaInterface -o <dir> --no-widget
```

and the file `machinome export` wrote — `manifest.json` — is what sits here
under the name `viewer.json`, byte for byte (`md5
cd9a3de93d232f15185638f534c0c942`). The rename is the only thing done to
it: the loader reads either published document by the fields they share,
and every other running fixture in this repository is called
`viewer.json`.

## The machine

Clearing sweeps a ring carrying two nine-tooth racks past the register
dials — one row over the counter, one over the result, on opposite halves
of the ring. A rack turns a dial only while its teeth REACH it AND the
dial is not already standing at its missing-tooth zero. The gap is what
lets the ring go on sweeping past a dial that has finished while it still
clears the dials beyond it, and it is why the law that moves a dial has
to read where that dial stands.

The numbers are the originating project's own, source-backed: the racks
start at `9.75` and `10.5` ring degrees, their pitches are
`degrees(3.75 / 52)` and `degrees(3.75 / 49.55)` ring degrees per tooth,
a tooth turns a dial `36` wheel degrees, the stations are
`(130 if counter else 0) - 20 * place`, and the band's half-width is
`0.5`. The ring angle is the middle 80 % of the clearing control — a
`clamp01` window — so each law's SKELETON is **not** affine and every
self-read crossing of this shape falls to the sampled search rather than
to a solve. That is what makes this fixture the price list, and why the
corpus's own `Clearing` machine (whose skeleton IS affine) does not
replace it.

## What is a stand-in

The geometry is **not** the machine's. The one distinct model path the
document names — `models/running_project/parts-Arbor-ff269d604af9.stl`,
referenced by all six dials — holds a stand-in binary STL of a unit cube,
684 bytes, the same cube `tests/fixtures/pascaline` carries. This
repository tests a RUN, not a mesh: what the acceptance asks of that file
is that a mesh exists at the path, and an `Arbor`'s cylinder shows
exactly what a cube shows about where a dial stands.

## One thing the export needed, and what it did not change

`tests/clearing_project/machine.py` reaches its `Arbor` through the
relative import `from ..running_project.parts import Arbor`, which
resolves under pytest and not under `machinome export`: the framework's
loader takes `tests/pyproject.toml` as the project root, so the module
loads as `clearing_project.machine` and the relative import goes beyond
the top-level package. In the throwaway copy that one line was changed to
`from running_project.parts import Arbor` before exporting.

It changed nothing about the machine, and that was checked rather than
assumed: the framework's own `CurtaShapeTest` passes identically in both
copies (3 passed, 19 subtests), and the published program is
**byte-identical** between them apart from its `identity` hash, which
takes in the module path. Every dial clears to exactly `359.5` in both.

The `identity` in this document is therefore
`7425122fcfafee5a96152d79dd6a4ec4d66d1745a569abe7997ee9d00db4eecb`, where
the framework's own pytest run computes
`eb3404956f88c88b0652efe4b1da947ed43ad5d2c25fe8c1dc39e556aee82ead` for
the same machine. Nothing here depends on that string — it gates a run
state restore against the machine it came from, and both are one
document's own — but it is written down so nobody has to rediscover it.
