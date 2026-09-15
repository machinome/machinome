## Context

`workflow/docs/markings.md` is the design note this change implements, written
from the finding in `workflow/warts.md` ("# Calculators (2026-09-15, markings
applied after the part is made)") and from two projects that both hit the same
wall: `projects/Calculators/Curta-Type-I-3x` and
`projects/Calculators/Pascaline-module`. The note is not ratified and where it
and a baseline spec or an accepted ADR disagree the spec and the ADR are right;
this document settles what the note left open and records what the pilot
already decided.

The framework today has exactly three things a class body may declare that are
neither a method nor a plain attribute: a **parameter** (a `Declaration` in
`solid_node/parameters.py`, which enters `uniq_id`), a **child** (a
`ChildDeclaration` in `solid_node/node/declarative.py`, realized per parent
instance), and a **coordinate or control** (a port, a joint, a `controls`
table — validated by `NodeMeta.__new__` where it is written). A marking is a
fourth, and the interesting thing about it is what it is *not*: it is not a
node, it has no volume, and it does not identify the solid's artifacts.

Three existing mechanisms carry almost all of the weight, and this design is
mostly a matter of composing them rather than inventing anything:

1. **`_validate_controls` (`declarative.py:829-868`)** — how a reserved
   class-body name is recognized duck-typed and refused at the line that wrote
   it, without `solid_node/node/` importing anything it should not.
2. **`SheetLeafNode`'s DXF (`sheet_leaf.py:157-187`,
   `adapters/build123d_sheet.py:14-39`)** — how a node writes a **second**,
   non-solid artifact beside its STL: same basename, same atomic
   write-and-stamp, regenerated when stale, not rewritten when current. The
   sheet leaf additionally widens its skip predicates so a lost DXF comes
   back; that one part of the pattern a marking deliberately does **not**
   copy, for the reason D5 gives.
3. **`StlNode`'s source resolution (`adapters/stl.py:158-183`)** — how a
   declared file beside the wrapper module is resolved, refused when absent
   through `require_source_file`, and tracked for currency.

## Goals / Non-Goals

**Goals:**

- One honest way to say "this part carries this artwork, here, in this colour"
  that costs the model no solid, no part, no piece and no artifact identity.
- A per-marking build artifact with its **own** currency, so the artwork and
  the part rebuild independently in the direction that matters.
- The framework half of a two-repository contract, specified precisely enough
  that the viewer cycle can be written against it without reading this code.

**Non-Goals:** as listed in `proposal.md` under "Out of scope" — DXF artwork,
text from a font, general surface projection, `process` and its manufacturing
outputs, drawing the marking, and a marking driven independently of its part.

## Decisions

### D1. A marking is a declaration, not a node, and not a parameter

`Marking(artwork, placement, color=...)` is an ordinary class attribute
carrying a `__set_name__`. It is deliberately **not** a data descriptor and
**not** a `Declaration`:

- Not a `Declaration`, so `declared_parameters` never sees it, so it never
  reaches `resolve_parameters`, `identity_values` or `_build_uniq_id`. That is
  the whole mechanism behind invariant 3 for the solid: there is no code path
  by which a marking can change an artifact key, because the key is computed
  from a set it is not in (`base.py:509-538`, ADR-026/063).
- Not a descriptor, so `self.digits` on an instance returns the `Marking` —
  useful in a test and inert everywhere else. It cannot be mistaken for a
  child: automatic child naming snapshots `self.__dict__` (`base.py:1255`),
  the instance dict, and a class attribute is never in it.

**Alternative rejected:** a `markings = {...}` table in the class body, keyed
by display name, mirroring `controls`. It reads worse at the declaration site
(the Curta wants `digits = Marking(...)`, and a subclass wants to drop it by
name), and a table has no `__set_name__`, so the marking could not name itself
in an error raised while the body still runs. The attribute form also gets MRO
inheritance for free.

### D2. Collection and refusal happen in `NodeMeta.__new__`

`_DeclaringNamespace.__setitem__` (`declarative.py:686-701`) is **not** a
general clash detector — it calls `_refuse_coordinate_clash`, which returns
immediately unless *both* the shadowed value and the new one are coordinates
and exactly one is a joint. A `digits = Length(...)` followed by
`digits = Marking(...)` is silently the second today. So the clash check is
this change's to write, and `NodeMeta.__new__` is where it belongs, for the
reason `_validate_controls` gives: the class exists now, so its own declared
parameters, children and coordinates can be enumerated and the clash refused at
the line that wrote it.

Four refusals, all at class creation, all naming the class and the attribute:

- **A marking on a non-rigid node.** `cls.rigid` is a class attribute fixed by
  type (`node-model`, "Rigid vs non-rigid distinction"), so an `AssemblyNode`
  or a `FlexibleNode` subclass is known here. An assembly has no artifact to
  carry a decal and no frame of its own to place one in; a flexible leaf's
  surface is a function of machine state, and a decal on it would have to
  deform with it, which is the projection problem this change does not solve.
- **A name clash** with a declared parameter, a declared child, a port, or a
  joint coordinate of the same class.
- **A name a node attribute already carries.** `color = Marking(...)` would
  make `self.color` a `Marking` and break `_colorize` (`base.py:1002-1010`);
  `files`, `model`, `mtime` and `stl_file` fail the same way. A parameter is
  already refused this twice over — the `_RESERVED` set of the attributes
  `__init__` assigns (`parameters.py:138-143`) and the MRO walk right after it
  in `Declaration.__set_name__` (`parameters.py:160-185`), which refuses any
  name a base class already carries as something other than a declaration. A
  marking is read as an attribute of its node in exactly the same way, so it
  is refused in exactly the same way, naming the class, the attribute and the
  node attribute it would shadow. (`_RESERVED` alone is not enough: `color`
  is not in it — it is caught by the MRO walk, because `AbstractBaseNode`
  carries `color = None` as a class attribute, `base.py:569`.)
- **A malformed marking** — an artwork that is not an artwork source, a
  placement that is not a placement, a missing or invalid `color`.

Recognition is duck-typed on a `marking_kind` attribute, exactly as a control
is recognized by `control_kind` (`declarative.py:839-848`), so
`declarative.py` imports nothing new and `solid_node/node/` keeps importing
nothing from the layers below it.

**Inheritance** follows `declared_children` (`declarative.py:878-890`): walk
`reversed(cls.__mro__)`, collect by attribute name, later classes winning. A
subclass assigning `digits = None` **removes** the entry — the one deliberate
difference from `declared_children`, and the reason it is worth having is a
variant part that is the same solid without its label. `None` is
unambiguous: `Marking` has no falsy state.

The walk is over `cls.__mro__`, not over node classes, so a marking written in
the body of a **plain mixin** — a class with no node base, which is exactly how
the Curta spells `class FittedDialType1(ClearingGearFit, ResultsDialType1)` —
is collected the moment a node class inherits it. Python calls `__set_name__`
on every object in a class body whatever the metaclass, so the mixin gets its
name and its declaring module captured there, and the artwork path therefore
resolves against the **mixin's** module, not the node's. Validation is the node
class's: `NodeMeta.__new__` never runs for a plain mixin, so a marking written
in one is refused when a non-rigid node inherits it and accepted when a rigid
one does — which is the right place for the refusal, since the mixin itself
says nothing about rigidity.

### D3. Artwork: SVG faces, open wires ignored and counted

`Svg(path, scale=None)`. `path` resolves against the directory of the module
that **declared** the marking — captured once in `__set_name__` from
`sys.modules[owner.__module__].__file__`, so a subclass inheriting the marking
still reads the file the declaring module meant, and a marking written in a
plain mixin (D2) resolves against the **mixin's** module — and is refused
through `require_source_file` (`sources.py:63-102`), the call every
source-bound leaf already makes.

The exceptions are that function's, named rather than alluded to, so a test
can pin them: a path that does not exist raises **`MissingSourceFile`**
(`sources.py:41-61`, a `FileNotFoundError` subclass built from the standard
`(errno, strerror, filename)` triple so `.filename` is the missing path while
`__str__` stays the one-sentence message), and a path that exists but is not a
regular file raises **`ValueError`** with `.filename` assigned after
construction. Either message names the class, the attribute, the declared
value and the resolved absolute path, because `require_source_file` composes
it from exactly those.

Nothing in `solid_node/core/builder.py` handles that family **by name** —
`MissingSourceFile` is referenced nowhere outside `sources.py`. What applies
unchanged is generic and worth stating so no reader infers more: on the
develop-mode reload path `_on_reload_exception` (`builder.py:505-533`) reads
`.filename` off whatever exception reached it and adds that path to the set it
watches broadly, so a develop session pointed at a missing SVG watches the SVG
and retries when it appears. That is the same recovery a missing STL source
gets today, and this change adds no handling of its own.

Reduction: `build123d.import_svg(path, align=None)`, keeping the returned
`Face` objects and ignoring the `Wire` objects. Measured in this venv
(build123d's signature is `import_svg(svg_file, *, flip_y=True,
align=Align.MIN, ...)`):

| file | faces | open wires | face extent (mm) | full extent (mm) |
|---|---|---|---|---|
| `results_dial.svg` | 10 | 4 | 56.438 × 6.000 | 59.376 × 10.500 |
| `reversing_lever_arrows.svg` | 3 | 0 | 3.494 × 24.000 | same |
| `upper_housing_numbers.svg` | 14 | 1 | 155.354 × 160.035 | 224.860 × 180.529 |

- `align=None` keeps the file's own origin at (0, 0) rather than moving the
  drawing's minimum corner there. That is what makes `origin=` meaningful and
  what makes two artworks authored on one sheet register with each other.
- `flip_y=True` is build123d's default and is kept: SVG's Y grows downward,
  the model's does not, and every one of these files is authored in a drawing
  program. This is why the measured faces sit at negative Y.
- A `Face` already carries its holes as inner wires, so a digit's counters
  come out as holes with no rule of our own. This is exactly the reduction
  `SheetLeafNode` performs on an authored profile, minus the one-face
  restriction: a marking is legitimately many disjoint faces.
- **Open wires are ignored, and their count is logged at build.** *Reported*
  means logged at **INFO** on the marking module's own logger, in one line
  naming the artwork file and how many open paths were ignored; a test pins it
  with `assertLogs`. INFO is the level the build already uses for an artifact
  notice (`base.py:87`, `'%s generated with %s!'`), and neither `sheet_leaf.py`
  nor `adapters/stl.py` logs anything of its own, so there is no quieter
  convention to follow. They are not a defect: `results_dial.svg`'s four open lines are its sheet border, and
  that border measures 59.376 mm wide against a 9.45 mm roll radius, whose
  circumference is 2π × 9.45 = 59.376 mm. **The border is the unwrapped
  circumference** — a registration mark, not a glyph. Dropping it silently
  would leave a modeller wondering why the digits do not sit where the drawing
  says; reporting the count says what was dropped without refusing a file that
  is perfectly correct. `upper_housing_numbers.svg`'s single wire is the same
  thing, and its 224.860 mm full width is the 224.8 mm the warts note records
  upstream sizing that artwork by.
- Artwork yielding **no** face is refused, naming the file: a decal with
  nothing in it is a mistake, not an empty decal.
- **Units.** build123d reads SVG user units as millimetres. `scale`, when
  given, multiplies every artwork coordinate, for a file authored in something
  else. It is not a placement parameter and does not belong on `Wrapped` or
  `Flat`: it is a property of the file.

### D4. Placement, and the angular zero

Both placements map an artwork point `(x, y)` — first shifted so that the
declared `origin` lands at the placement origin, `u = x - origin_x`,
`v = y - origin_y` — into the part's **adjusted** frame: the frame the node's
own artifact is written in, after `adjust()`. Nothing about an assembly's
operations, a joint or an instant enters here, which is invariant 4 and is why
the marking moves with the part for free.

**`Flat(at, normal, x_axis, origin=(0, 0))`**

    x̂ = normalize(x_axis - (x_axis · n̂) n̂)      n̂ = normalize(normal)
    ŷ = n̂ × x̂
    P(u, v) = at + u x̂ + v ŷ

An `x_axis` parallel to `normal` leaves nothing to orthogonalize and is
refused naming both. Vectors need not be unit.

**`Wrapped(axis, radius, at, start=0, origin=(0, 0), pitch=None, zero=None)`**

    â = normalize(axis)
    θ(u) = start + degrees(u / radius)
    P(u, v) = at + v â + radius (cos θ ê₀ + sin θ (â × ê₀))

Artwork X is arc length around `axis`, artwork Y is height along it from `at`,
positive angle is right-handed about `axis`. `radius` must be positive.

The zero direction ê₀ is the decision the note left open. The rule:

    σ(a₁, a₂, a₃) = (a₃, a₁, a₂)
    ê₀ = normalize(σ(â) - (σ(â) · â) â)

σ is the cyclic shift, which is a 120° rotation about (1, 1, 1). For a
principal axis it lands exactly on **the next principal axis in right-hand
order** — verified numerically: Z → +X, X → +Y, Y → +Z, and −Z → −X. For a
general axis it is deterministic, continuous away from the degeneracy, and
needs no table. It is undefined for exactly one direction, â parallel to
(1, 1, 1), where σ(â) = â (measured residual 1.9e-16); that case is **refused**
naming the axis and `zero=` as the remedy, rather than silently choosing.

`zero=`, when given, wins: it is projected perpendicular to `axis`,
normalized, and used as ê₀; parallel to `axis` it is refused. It exists for
the degenerate axis and for a modeller who wants the zero written down rather
than derived. Both spellings are specified and tested, so the convention is
never something a reader has to infer from geometry.

**Alternative rejected:** deriving ê₀ from "the principal axis least parallel
to `axis`". It has a tie at 45° whose resolution is an arbitrary iteration
order, and it does not reduce to the principal table without a special case.

**`pitch`**, in degrees, stamps the whole artwork at θ + k·pitch for
k = 0 … N−1. `pitch` must be positive and 360/pitch must be a whole number
within 1e-9, N being that number; anything else is refused naming the value
and the nearest whole count, because a pitch that does not divide the circle
leaves the last copy overlapping the first and no honest answer about which
wins. The artwork is stamped as authored; a file wider than one pitch arc
overlaps itself, and that is the author's business.

Note what `pitch` is *not* for: `results_dial.svg` already carries all ten
digits across exactly one circumference, so the Curta's roll needs no pitch.
It is for an artwork that is one repeated unit.

### D5. The marking artifact and its own currency

Per marking, one **surface mesh** — an open sheet of triangles lying on the
nominal cylinder or plane, with no thickness and **no offset**. Any
anti-z-fighting offset is a rendering constant belonging to the viewer, not a
claim about where the part's surface is, so no offset is baked here
(`markings.md` §7).

Path: `<basepath>.marking-<name>.stl`, beside the part's `.stl` and under the
same `<script>-<uniq_id>` basename, extending the `build-pipeline` "Build
artifact layout" requirement the way the sheet leaf's `.dxf` did. The
attribute name is in the path, so two markings on one part never collide and
the file says which declaration wrote it.

Construction (measured end to end on `results_dial.svg`, R = 9.45 mm):

1. Tessellate each `Face` in the artwork plane through OCCT's incremental
   mesher — 4 508 vertices, 4 499 triangles for the ten digits.
2. For a `Wrapped` placement, subdivide so that no edge spans more than the
   chord the tolerance allows: `max_edge = 2 √(2 R t − t²)`, t being the
   part's own declared `linear_deflection` where it declares one and the
   framework's historical 0.1 mm where it does not (an `StlNode` declares
   none). `trimesh.remesh.subdivide_to_size` (trimesh 4.4.9, present) does it;
   at R = 9.45 and t = 0.1 the limit is 2.742 mm and the glyph mesh is already
   finer, so it cost 12 triangles. A flat face's two triangles wrapped by
   their vertices alone would be a chord, not an arc; this is what makes the
   decal follow the surface it is on.
3. Map every vertex by D4 and write a binary STL. Measured: every vertex at
   radius 9.45 to within 3e-15 mm, 69.48 mm² of artwork, 226 kB.

The mesh is deliberately **not** watertight (measured `is_watertight` False,
`volume` meaningless). Nothing gates it: the watertight gate is `StlNode`'s
*import* admission, not an output check, and this artifact is never imported
as a part, never fused, never measured.

**Its own currency.** Its tracked source set is the node's `files` **plus the
artwork file**; its mtime stamp is the maximum over that set, and its digest
and fingerprint are `currency.source_digest` / `currency.source_fingerprint`
over it, recorded in the ordinary sidecar by `_atomic_write_bytes`. Because
the artwork file is in the marking's set and not in `node.files`:

- editing the **artwork** changes only the marking's stamp and digest, so the
  decal is rebuilt and the STL and BREP stay current — invariant 3's operative
  half, and the reason the currency split is a requirement rather than an
  optimization;
- a stale or missing decal never re-derives a solid, because nothing in the
  solid's currency reads the marking's;
- a **current** decal is never rewritten, because the marking build is guarded
  by the same `_up_to_date`-shaped predicate every other artifact uses.

The artwork file is deliberately **not** added to `node.files`. Adding it would
be the one-line version of this feature and would break invariant 3 outright:
`node.files` is what `mtime_ns`, `source_digest` and `source_fingerprint` are
computed over, so an artwork edit would invalidate the STL, the BREP, the
`.scad` and, through the parent's union (ADR-033), every ancestor.

**Its producer recipe.** The marking artifact records one. The machinery is
already there: `_atomic_write_bytes` takes a `recipe` through to
`currency.publish` (`base.py:130-151`), and `_artifact_recipe(path)` — `None`
for every artifact today (`base.py:1413-1415`) — is the hook currency checks
first (`base.py:1363-1367`), under the `build-pipeline` requirement "Producer
recipe identity qualifies artifact currency". For a marking path it returns
`marking-svg-v1:<effective tolerance>`, in the shape `FusionNode` already uses
for its faceted mesh (`fusion.py:44-47`), and defers to `super()` for every
other path, so the STL, the BREP and the `.scad` are untouched by it.

The tolerance has to be in the recipe because it is not always in the sources.
A part that declares `linear_deflection` puts that number in its own class
body and the scoped source digest catches an edit (ADR-071); a part that
declares none — an `StlNode` — is meshed at the framework's default, which
lives in the framework and in no project file. Without a recipe, changing that
default, or the meshing rule itself, would leave every existing decal certified
current and go on serving chords where the new rule wants arcs. The marking's
own currency predicate consults the same `_artifact_recipe` hook, so the check
is written once and both the solid's `_up_to_date` and the marking's answer it
the same way.

**The accepted consequence, recorded rather than engineered around.** Editing
the declaration **line** — the placement numbers, the colour, the artwork path
— rebuilds the part's solid. The class body is in the node's scoped source
digest (ADR-071, `currency._scoped_digest`), which is scoped per node class but
not per statement, and making it finer would mean parsing a class body into
"statements that affect geometry" and "statements that do not" — exactly the
kind of cleverness ADR-060's "the fallback is strictly stricter than the rule
it stands behind" exists to avoid. The cost is one rebuild of one part when a
decal moves. The pilot has it in writing.

**Where it is built.** `AbstractBaseNode._prepare` already runs for every node
on the build path — `assemble` calls it unconditionally, before it consults any
skip predicate of its own (`base.py:848-856`) — and it is the only place both a
leaf adapter and a `FusionNode` pass through (`base.py:884-905`; `_prepare` is
defined exactly once in the node tree, so neither `FusionNode` nor
`InternalNode` overrides it). Stale markings are built there, **after and
independently of the solid's skip decision**: the marking pass sits outside
`_prepare`'s `if not self._prepare_can_be_skipped():` block, so every rigid
node's markings are visited on every build whether or not its STL is current,
each guarded by its own `_up_to_date`-shaped predicate over its own artifact
and its own tracked source set. It sits after `_prepare`'s `if self._prepared`
early return (`base.py:890-891`), so the pass runs once per node per process,
which is the same once-per-process guarantee the solid's own materialization
has.

`LeafNode._render_can_be_skipped` and `_prepare_can_be_skipped`
(`leaf.py:41-65`) are therefore left **untouched**, and this is the one place
the sheet leaf is not the model. `SheetLeafNode` widens both
(`sheet_leaf.py:157-170`) because its DXF is derived FROM the rendered profile
— `materialize` writes it out of `validated_profile()` — so a lost DXF
genuinely needs the render back. A marking is derived from the artwork and the
declaration and never from the render. Widening the predicate would make a
stale or missing decal re-enter `_prepare`'s body and call `self.render()`
(`base.py:893`) — for a `StepNode` that is the STEP load plus `adjust()`, the
expensive derivation — only for `materialize` to leave the current STL bytes
alone. The sheet leaf's analogy holds for the artifact **lifecycle** (atomic
write, stamp, digest, fingerprint, regenerate when stale, never rewrite when
current) and not for the skip predicate.

A node's markings depend on its render not at all, so the marking build needs
no rendered geometry and cannot be made to wait on one. It follows that a
marking is written by whatever process runs `_prepare` for that node — the
assembling process, not the STL render subprocess — which is exactly where the
sheet leaf's DXF is written today.

### D6. The document: an additive `markings` list, and no placement in it

A rigid node's entry gains:

    "markings": [
      {"name": "digits", "model": "…/dial-….marking-digits.stl",
       "color": "#FFFFFF", "mtime": 1757900000.123456789}
    ]

absent when the node declares none.

- **Additive, no version bump.** ADR-057's rule is that a producer emits the
  lowest version its content needs, and ADR-043's `piece` is the precedent: a
  consumer that ignores `markings` renders exactly the picture it renders
  today, because a marking adds nothing the existing fields describe wrongly.
  Byte-identity is proved the way the last two additive growths proved it, and
  in particular it is **not** proved by recapturing anything: the seven
  documents `ByteIdentityTest` compares against
  (`tests/base_documents/*.json`, `tests/test_running_document.py:234-280`)
  were captured at earlier cycles' bases and stay exactly as they are, so the
  assertion keeps comparing post-change output against pre-marking bytes. A
  capture regenerated with this cycle's code would assert nothing at all. The
  new marking fixture did not exist at any base and therefore gets no capture;
  its marking-free tree is asserted structurally instead — no `markings` key on
  any node, the version its content already needed, the same node fields.
  Contrast `bindings` (version 4) and `program` (version 5), both non-additive
  precisely because ignoring them puts the machine in a **wrong pose**. A
  marking cannot: it is not in any operation, any binding or any program.
- **Placement is not published.** The decal mesh is already in the part's
  adjusted frame, so a consumer applies the part's own operations to it and is
  done. Publishing the placement as well would be a second, redundant
  description of the same fact and a second thing to keep in agreement; the
  viewer would have to reproduce D4's maths in TypeScript, and the parity
  problem ADR-022 exists to contain would grow a new limb for nothing.
- **No `piece`, and the inventory excludes markings.** A piece is a thing to
  print (ADR-043/085); a decal is not one, its bytes are not a solid, and a
  piece id over them would be a lie about the bill of materials — which is the
  exact failure the split-into-leaves workaround commits.
- **Its own `mtime`** is the marking artifact's, not the node's, so a consumer
  that reloads on change sees the decal change without the part appearing to.
- **`color` is required** on a marking, unlike a node's, which may be `None`.
  A part with no colour has a sensible default appearance; a decal with no
  colour is invisible, which means the declaration did nothing.

Mechanically, `serialize_node` gains one keyword-only `marking_path=None`
callback, resolved by the producer exactly as `model_path` and `piece_id`
already are (`serializer.py:627-673`), so every existing caller — the tools,
the parity generator, the corpus generator and a dozen tests passing
`lambda rigid: rigid.name` — keeps the document it has. The three real
producers pass it: `core/builder.py` (build-root-relative), `core/export.py`
(under `models/`, with the same containment guard `_model_path` applies, so an
artifact outside the build directory fails export before anything is written)
and `viewers/browser.py` (staged beside the models). Export copies the file
with an ordinary atomic copy rather than `PieceInventory.copy_artifact`, which
only serves paths registered as pieces (`core/pieces.py:273-276`) and a
marking is deliberately not one.

The build's sweep (`core/builder.py:727-790`) collects a marking's `model`
into `referenced` alongside the node's, so a marking artifact is spared **by
reference, not by kind**. That is the honest arrangement: unlike `.brep` and
`.scad`, which no document names, a marking IS named, so a marking whose
declaration was deleted is swept on the next successful build exactly as a
renamed node's artifact is.

### D7. The public module

`solid_node.node.markings` defines and exports `Marking`, `Wrapped`, `Flat`
and `Svg`, and all four are added to `_EXPORTS` in
`solid_node/node/__init__.py` so they resolve lazily from `solid_node.node`
like every other public node name. This is consistent with ADR-087's "one
module answers one question": `solid_node.node` answers *what has shape*, and
what a part carries on its surface is an answer to that question, not to *what
moves* (`solid_node.motion`) or *what is a knob* (`solid_node.parameters`).
The `_MOVED` warning in that module's docstring is about a name whose home is
another **question's** module; a submodule of the node package re-exported
from the node package is the established pattern (`StlNode`,
`Build123dSheetNode`, every adapter).

The module imports only the standard library at import time. build123d is
reached inside the artwork reduction and trimesh inside the mesh build, for
the reason `Build123dSheetNode`'s docstring gives: `solid_node.node` is on
every `solid` invocation's path and build123d costs about 1.6 s.

### D8. What the pilot already decided (`markings.md` §9)

Recorded here so the settled decisions do not live only in a conversation:

- **A co-printed marking still declares no solid in the model.** It affects
  only the export, which is cycle 3's business. This is what makes "a marking
  can never collide with anything" true without qualification, and it is the
  premise every invariant in this change rests on. An `engraved` marking would
  be a cut — it changes the solid and belongs in the part's own render, not
  here.
- **The document growth is additive** (D6).
- **Text from a font is not a source**, in this cycle or by default; if it ever
  is, it gets its own cycle and an explicit answer on font provenance.
- **A marking is not driven independently of its part.** Nothing in the
  catalogue needs it.
- **A marking may be declared on any rigid node — a leaf adapter or a
  fusion** (pilot, 2026-09-15). Both calculators declare theirs on leaves, but
  the rule falls out of `rigid` being a type property and costs no extra code,
  so a fusion carries a marking on the same terms a leaf does: one artifact
  beside the fusion's own STL, in the fusion's adjusted frame. This is settled,
  not open.

## Risks / Trade-offs

- **Editing a marking's declaration line rebuilds the part's solid** (D5) →
  Accepted and recorded, not mitigated. The alternative is statement-level
  digest scoping, which is more cleverness in the one place the cache cannot
  afford to be clever. Cost is one part's rebuild.
- **A build123d dependency arrives through a file, not a backend** → A project
  whose leaves are all `StlNode` and which declares one `Svg` marking now needs
  build123d at build time. This is the same bargain `Build123dSheetNode`
  already offers and it is paid only by a project that declares a marking; the
  import stays inside the build, so no `solid` invocation that touches no
  marking pays for it.
- **The wrap tolerance for a faceted part is a framework default, not a
  declaration** → An `StlNode` declares no `linear_deflection`, so its decals
  are meshed at 0.1 mm. That is the same number every exact node defaults to,
  and a marking is a surface decal where 0.1 mm of chord error is invisible. If
  it ever matters, the knob is a follow-up, declared where the other two are.
- **A marking artifact is an STL that is not a solid** → Nothing in the
  framework reads it as one (D5), but a person browsing `_build/` will find a
  non-watertight `.stl`. The filename says `marking` and the document says
  which node it belongs to; a distinct extension was considered and rejected,
  because the viewer already knows how to load an STL and inventing a format
  to make a directory listing self-explanatory is the wrong trade.
- **The viewer does not draw markings until its own cycle lands** → A model
  that declares one publishes it and looks exactly as it does today. That is
  the point of the growth being additive, and it is why this cycle is worth
  landing before the viewer's: the document is the contract, and the viewer
  cycle is written against a specification rather than against an intention.
- **Two markings could overlap on one part** → Not refused. They are colour on
  a surface, not solids; overlap is a rendering order question and nothing in
  the model is wrong.

## Open Questions

- **ADR number.** ADR-119 is the highest on `docs/adrs/` at this base —
  `main` at 710d86f, onto which the cycle branch was fast-forwarded on
  2026-09-15: ADR-118 is the archived `honour-skip-and-xfail` record and
  ADR-119 the named-project-models decision renumbered from 073. This cycle
  plans on **ADR-120** and re-checks at extraction time.