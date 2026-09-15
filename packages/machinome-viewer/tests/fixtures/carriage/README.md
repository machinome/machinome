# The Curta's carriage, as a version 7 fixture

`viewer.json` is the framework's own test machine
`tests/carriage_project/machine.py:CurtaCarriage`, exported **verbatim**
from a throwaway copy of solid-node at branch `select-the-source`, commit
`0b0f02a` — 32,791 bytes, `md5 1598d57e18f772315183a7e466123a39`, a
**version 7** document.

It declares five drivers (`clearing`, `crank`, `lift`, `position`,
`reset`), fourteen coordinates all resting at `0.0`, thirty-five
bindings, no intermediates, a `seat` span **both of whose sides are
expressions** reading another coordinate (solid-node ADR-113), and
**nine law edges of which seven — edges 2 to 8, the three levers and the
four dials — form ONE BLOCK**, each carrying a self-read and each
published `affine: [true]`.

That block is the whole of what makes the document version 7: no key was
added for it. A consumer re-derives the block from the published edges'
own `needs` and `gives`, and each member's SELECTORS from the `level`
expressions its plan publishes. **The published order of a block's
members is a LISTING, not an execution order**, which is why a viewer
that executed it as published would commit a different machine in
silence.

Nothing here edited the document and nothing here regenerates it. It was
produced with

```
PYTHONPATH="$PWD" solid export \
    tests/carriage_project/machine.py:CurtaCarriage -o <dir> --no-widget
```

which warned, correctly, that the installed viewer could not read it:

```text
WARNING - core.export - this model needs document version 7, and the
  installed browser viewer renders 1, 2, 3, 4, 5, 6 (solid-node-viewer
  0.1.0). The export is written anyway: an export is an artifact a LATER
  viewer may open, and a viewer that cannot read it refuses it by name
  rather than rendering part of a machine it does not understand.
```

The file `solid export` wrote — `manifest.json` — is what sits here under
the name `viewer.json`, byte for byte. The rename is the only thing done
to it: the loader reads either published document by the fields they
share, and every other running fixture in this repository is called
`viewer.json`.

## The machine

Four number dials ride on the CARRIAGE; three carry levers belong to the
FIXED frame. The carriage's `position` sets `seat`, twenty degrees per
station, and `lift` raises `hoist`. With the carriage DOWN
(`hoist < 0.5`) each lever is tripped by whichever dial its station
brings under it and advances the dial one place up — so the same lever is
tripped by dial `s` and advances dial `s + 1`, where `s` is the position
the maker chose. At any one position the active dependencies are a chain
and acyclic; their UNION over the working positions is CYCLIC, and the
union is what the compiled program orders.

Each lever reads its own travel (`lever_n.travel < 1.0`), so it trips
once and holds; with the carriage UP, `reset` runs the levers back to
zero. Each dial reads its own angle through a `floor` window, so
`clearing` advances it only while it stands off its own zero. `seat`
declares a span whose two sides are expressions over `seat` and `hoist`:
with the carriage DOWN the span pins it to its own station — the
INTERLOCK — and with it UP the span opens by four stations either way.

## What is a stand-in

The geometry is the machine's own: `solid export` wrote both meshes the
document names, a dial (`parts-Arbor-ff269d604af9.stl`, 5,884 bytes) and
a carriage plate (`parts-Carriage-047f12d8000c.stl`, 684 bytes). This
repository tests a RUN, not a mesh; what the acceptance asks of those
files is that a mesh exists at every path the document names.

## One thing the export needed, and what it did not change

`tests/carriage_project/machine.py` reaches its parts through the
relative import `from ..running_project.parts import Arbor, Block,
Carriage as Slide`, which resolves under pytest and not under
`solid export`: the framework's loader takes `tests/pyproject.toml` as
the project root, so the module loads as `carriage_project.machine` and
the relative import goes beyond the top-level package. In the throwaway
copy that one line was changed to `from running_project.parts import
Arbor, Block, Carriage as Slide` before exporting.

It changed nothing about the machine, and that was checked rather than
assumed, exactly as the clearing fixture's was:

- the framework's own `tests/test_running_selection.py` passes in the
  read-only worktree (39 passed, 4 subtests) and
  `tests/test_running_selection.py` with `tests/test_running_stops.py`
  passes in the throwaway copy (107 passed, 32 subtests);
- the published program is **byte-identical** between the two copies
  apart from its `identity` hash, which takes in the module path.

The `identity` in this document is therefore
`917094ae7e0629ed26e139086cca7c55f4777258e80f8b003f8cf0c4afa89572`, where
the framework's own pytest run computes
`d69d52118f007a91f8a658a391759098e513cdbd4513126d98ec5f648bfbbba4` for
the same machine. Nothing here depends on that string — it gates a run
state restore against the machine it came from, and both are one
document's own — but it is written down so nobody has to rediscover it.
