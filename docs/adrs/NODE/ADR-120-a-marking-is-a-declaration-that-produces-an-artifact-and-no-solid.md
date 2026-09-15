# ADR-120: A Marking Is a Declaration on a Part That Produces an Artifact and No Solid

**Status:** Accepted
**Date:** 2026-09-15
**Depends on:**
- [ADR-026: Node identity, parameter-hashed artifact keys vs tree names](./ADR-026-node-identity-parameter-hashed-artifact-keys-vs-tree-names.md)
- [ADR-061: A call in a class body is a declaration](./ADR-061-a-call-in-a-class-body-is-a-declaration.md)
**Cites:**
- [ADR-043: Content-derived printed-piece identity](../EXPORT/ADR-043-content-derived-printed-piece-identity.md)
- [ADR-057: The flexible leaf, whose geometry travels as a spec](./ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — the rule that a producer emits the lowest version its content needs
- [ADR-060: Content-verified currency beneath the mtime rule](./ADR-060-content-verified-currency-beneath-the-mtime-rule.md)
- [ADR-071: Node-scoped content currency](./ADR-071-node-scoped-content-currency.md)
**OpenSpec change:** `carry-markings-on-a-part`

## Context and Problem Statement

A Curta is a calculator whose answer is the angular position of ten
printed number rolls. `projects/Calculators/Curta-Type-I-3x` models and
drives every one of them, so the register value is computed correctly
and is **unreadable**, because the digits are not on the part.
`projects/Calculators/Pascaline-module` has the same hole. Drive either
crank in the browser and the machine gives no answer, which for a
calculator is the one thing it is for.

The limit was one line wide: `color` is a single class attribute per
node, validated to one `#RRGGBB` and applied whole-node. Nothing in that
chain names a **region** of a part. A project that wanted digits on a
roll had two options, and both are wrong:

- declare each glyph as its own leaf — which invents parts no maker
  handles, gives them volume, puts phantom solids in front of every
  clearance, interference and disconnected-solid contract, and reports
  them in the bill of materials; or
- drop the markings, which is what both calculators did.

Upstream already states the concept the framework was missing: the Curta
ships its markings as cut artwork (eleven DXF, the same as SVG), or as a
co-printed multi-material variant, body STL plus one STL per glyph.
**One part, several colour bodies, one manufacturing unit** is what
those file names say, and solid-node could not say it.

## Decision Drivers

- The three things a class body could declare — a parameter, a child, a
  coordinate — are all things the machine is MADE of. What a part
  carries on its surface is none of them, and modelling it as one of
  them is what produces a phantom part.
- Every geometric verdict the framework offers must be untouched:
  volume, bounds, STL and BREP bytes, piece id, interference,
  connectivity, faceted and exact alike.
- Adding a decal to a part that is already built must not invalidate its
  artifacts, and editing the artwork must not re-derive a solid.
- The viewer is a separate repository on its own release cycle, so the
  framework's half has to be a written contract rather than an
  intention.

## Considered Options

1. **A `markings = {...}` table in the class body**, keyed by display
   name, mirroring `controls`.
2. **A marking as a node kind** — a zero-thickness leaf placed by its
   parent.
3. **A marking as an attribute declaration** carrying `__set_name__`,
   beside a parameter and a child, producing an artifact of its own and
   no solid.

## Decision

Option 3. A **marking** is a fourth kind of class-body declaration:

    digits = Marking(Svg('results_dial.svg'),
                     Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45)),
                     color='#FFFFFF')

It is deliberately **not** a `Declaration`, so `declared_parameters`
never sees it and there is no code path by which it can reach
`identity_values` or `_build_uniq_id` (ADR-026): adding a marking cannot
change an artifact key, because the key is computed from a set it is not
in. It is **not a descriptor**, so reading it off an instance returns
the declaration, and automatic child naming — which scans the instance
`__dict__` — can never mistake a class attribute for a child (ADR-061).

Collection and refusal happen in `NodeMeta.__new__`, duck-typed on a
`marking_kind` attribute exactly as a control is recognized by
`control_kind`, so the declaration layer imports nothing new.
Inheritance is the MRO's, which means a marking may be written in a
**plain mixin that is not a node** — the shape a project already uses
for a family of fitted parts — and is collected, and refused if the node
is not rigid, on the node class that wears it. The artwork path resolves
against the module that DECLARED the marking, captured in
`__set_name__`, which Python calls whatever the owner's metaclass.

A marking is refused on a non-rigid node, on a name that clashes with a
parameter, a child, a port or a joint coordinate, on a name a node
attribute already carries (`color` first among them), and when it is
malformed — each at class creation, naming the class and the attribute.

The build writes **one surface mesh per marking** beside the part's
`.stl`, under the same basename with the attribute name in the path, in
the part's own adjusted frame, on the nominal surface with no offset. It
is not watertight and is never read as a solid. A wrapped decal is
subdivided so no edge spans more chord than the part's own tessellation
precision allows.

Its currency is **its own**: the tracked set is the node's `files`
together with the artwork file, and the artwork is deliberately NOT in
`node.files`. Editing the artwork therefore rebuilds only the decal and
leaves the STL, the BREP, the `.scad` and every ancestor current; a
stale or missing decal never re-derives a solid. The pass runs in
`_prepare`, AFTER and OUTSIDE the solid's skip decision, so a lost decal
always comes back and costs no render — which is the one place the sheet
leaf's DXF is not the model: it widens its skip predicates because its
cut file is derived FROM the rendered profile, and a marking never is.
The artifact records a producer recipe (`marking-svg-v1:<tolerance>`),
because a part that declares no `linear_deflection` is meshed at a
framework default that lives in no project file.

A rigid node's published entry gains an optional `markings` list —
`name`, `model`, `color` and the marking's own `mtime`, no placement and
no `piece` — ADDITIVE, moving no version (ADR-057, the `piece`
precedent of ADR-043). Placement is not published because the artifact
is already in the part's frame: a consumer applies the part's own
operations to it, and no consumer reproduces the placement arithmetic.

## Consequences

**Good.**

- A calculator can be read. A dial face, an index mark, a scale, a
  warning label and a part number are now sayable, at no cost to any
  geometric contract: the four invariants — no solid, not a child, not
  the solid's identity, in the part's own frame — are each enforced by
  construction rather than by care.
- The framework's half of the two-repository contract is specified
  precisely enough that the viewer's cycle can be written against a
  document rather than against an intention, and a model that declares a
  marking today publishes it and renders exactly as it does now.
- The currency split makes the direction that matters cheap: an artwork
  edit costs one decal, not a part and every ancestor.

**Bad, and accepted.**

- **Editing the declaration LINE rebuilds the part's solid.** The class
  body is in the node's scoped source digest (ADR-071), which is scoped
  per class and not per statement, and making it finer would mean
  parsing a class body into "statements that affect geometry" and
  "statements that do not" — exactly the cleverness ADR-060 exists to
  avoid. The cost is one rebuild of one part when a decal moves.
- A project whose leaves are all `StlNode` and which declares one `Svg`
  marking now needs build123d at build time. It is the bargain
  `Build123dSheetNode` already offers, paid only by a project that
  declares a marking: the import stays inside the build.
- A marking artifact is an `.stl` that is not a solid. The filename says
  `marking` and the document says which node it belongs to; inventing a
  format so a directory listing explains itself would cost the viewer a
  loader it already has.
- The wrap tolerance for a faceted part is a framework default rather
  than a declaration. A marking is a surface decal, where 0.1 mm of
  chord error is invisible; if it ever matters the knob is a follow-up.

**Rejected options.**

- A `markings = {...}` table reads worse at the declaration site, gives
  a subclass no way to drop one by name, and has no `__set_name__` — so
  a marking could not name itself in an error raised while the body
  still runs, and MRO inheritance would have to be written by hand.
- A marking as a node kind is the workaround this ADR exists to
  replace: it puts a part in the tree, in the piece inventory and in
  front of every interference sweep.
