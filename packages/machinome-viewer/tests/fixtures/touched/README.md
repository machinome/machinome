# The Pascaline module with its dials declared, as a touchable fixture

`viewer.json` is the framework's own published build of that module's
classes with a `controls` table, **verbatim** — a version 5 document of
31,972 bytes, root `Touched`, carrying three inputs, four instructions,
nine joint coordinates and six controls: three `button` on `Add one` /
`Add ten` / `Add hundred`, and three `turn` at `per_unit` `-36.0`, each
naming the joint `[<column>, "input"]`, the coordinate
`<column>.input.turn`, the axis `[1, 0, 0]` and the origin `[0, 0, 0]`.
It is a probe build rather than the module's own: it imports the
module's `simulation.module` and `simulation.pascaline` unchanged and
only its root class differs, to declare the table the module itself does
not carry until its own later cycle. Nothing here edited it, and nothing
here regenerates it.

The geometry beside it is **not** the module's. Each of the fifteen
model paths the document names holds a stand-in binary STL of a unit
cube, 684 bytes — the same cube `tests/fixtures/pascaline` uses. Three
of those fifteen paths differ from that fixture's, so this one carries
its own `vendor/` tree rather than borrowing it. This repository tests a
run and a gesture, not a mesh: what the acceptance asks of these files is
that a mesh exists at each path, that a pick reaches it, and that its
world matrix moves when the bank behind it moves. A cube shows that as
well as a digit drum does, and costs a thousandth of the bytes.
