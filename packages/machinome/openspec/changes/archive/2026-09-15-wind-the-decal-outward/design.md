## Context

This is a follow-up to `carry-markings-on-a-part` (archived 2026-09-15,
ADR-120), and it settles one sentence that cycle left implicit: which way a
decal faces.

A marking artifact is the framework's only **open sheet**. Every other mesh it
writes — an STL, a faceted fusion mesh, the BREP behind them — is a closed
solid whose orientation the mesh engine owns and whose "outside" any consumer
can recover from the geometry itself. An open sheet has no recoverable
outside: the only thing that says which side of a decal is the air is the
winding of its triangles. ADR-120's D5 deliberately put the sheet on the
nominal surface with **no offset**, pushing any separation to the renderer —
and a renderer that must separate a sheet from a surface needs a direction.

The consumer that needs it exists. `solid-node-viewer`'s cycle
`draw-what-a-part-carries` (branch `draw-markings`) displaces each decal vertex
along its own vertex normal by `MARKING_LIFT = 0.15` mm, and its design's
"What the lift assumes of the producer" says in as many words that the
direction "relies on a property the framework's export spec does not yet
promise", records the property as **observed, not promised**, and names the
framework follow-up. This is that follow-up.

### What is actually true today, measured

Three facts, each verified in this worktree against the committed fixture
`tests/markings_project` and the venv's build123d 0.10.0 / ocpsvg 0.5.0:

1. **The framework's own placement maths already maps artwork `+Z` outward,
   by construction.** `Flat.__init__` (`markings.py:306-327`) sets
   `ŷ = n̂ × x̂`, so `x̂ × ŷ = n̂` — the declared plane normal.
   `Wrapped.place` (`markings.py:470-494`) maps artwork `(u, v)` to
   `at + v â + R(cos θ ê₀ + sin θ b̂)` with `b̂ = â × ê₀`; its tangents are
   `∂P/∂u = θ̂` and `∂P/∂v = â`, and `θ̂ × â = cos θ ê₀ + sin θ b̂` = the
   outward radial direction at that point. Neither is accidental and neither
   needs to change. **Half the promise is already kept and paid for.**
2. **`build123d.Face.tessellate` winds with the face's oriented normal.** It
   swaps indices 2 and 3 when `face.wrapped.Orientation()` is
   `TopAbs_REVERSED` (`build123d/topology/shape_core.py`), so the triangle
   winding follows `face.normal_at()`. Measured on a hand-built face:
   normal `+Z` → signed 2-D area `+48`; the same face complemented → normal
   `-Z`, signed area `-48`. So an artwork face with `normal_at().Z < 0` would
   produce a decal wound the wrong way, and the predicate to detect it is
   exactly `face.normal_at().Z < 0`.
3. **No SVG can currently produce such a face — but not for a reason the
   framework owns.** `ocpsvg.ensure_face_normal_up` (`ocpsvg/ocp.py:197-203`)
   measures each imported face's surface normal at its UV midpoint and calls
   `face.Reverse()` when `Z < 0`; `build123d.import_svg` yields exactly the
   faces that function returned. Probed against a deliberately clockwise path,
   a mirroring `matrix(-1 0 0 1 24 0)` group and an arc-built circle: every
   face came back `+Z`, some `TopAbs_FORWARD` and some `TopAbs_REVERSED`, all
   with positive signed 2-D area.

Fact 3 is the correction this cycle carries back to the finding, and it argues
*for* the change rather than against it. The viewer's design calls the property
"an accident of the pipeline"; it is not an accident, it is a **contract of an
undeclared transitive dependency**. `solid-node` declares `build123d`;
`build123d` pulls `ocpsvg`; `solid-node` pins neither, names neither, and has
no test that would notice `ensure_face_normal_up` changing, being removed, or
being bypassed by a future importer. Publishing a promise whose only
enforcement lives two packages away, unpinned and unnamed, is precisely the
kind of claim the shop's honesty rule exists to refuse. Four lines in
`markings.py` move the enforcement into the producer that makes the promise.

Measured consequence of that move, on all three fixture decals: **byte-for-byte
identical output** from correctly oriented artwork (`Dial.digits` 22 484 B
sha256 `bd3dacd344bd5050…`, `Plate.badge` 184 B `ff24e82d90c28677…`,
`Plate.band` 8 084 B `e492ab49a5dbb307…`) and **the same bytes again** from
artwork whose regions were deliberately reversed. The fix is a no-op on every
input the world can currently produce, and a repair on the one it cannot.

## Goals / Non-Goals

**Goals:**

- Promise, in the `export` and `markings` baseline specs, that a marking
  artifact's triangles wind away from the part, so a consumer may use a decal's
  own normals as an outward direction without inspecting the part.
- Make that promise true by construction in the producer, independent of the
  drawing tool and of any library that reads the drawing.
- Keep the promise total: close the one remaining way a project's own class
  body could defeat it.
- Change nothing else — not the placement maths, not the artifact's path,
  bytes, sources, currency or producer recipe, not the published document.

**Non-Goals:**

- Offsetting or lifting the decal in the producer. ADR-120 D5 stands: the
  sheet is on the nominal surface and any separation is the renderer's.
- Publishing the decal's tessellation tolerance. That is the viewer's
  *magnitude* residual; this change is about *direction*. Independent.
- Any viewer change. The viewer already tests the direction by name; after
  this it is testing a promise rather than an observation.
- A winding rule for closed meshes. An STL's orientation is the mesh engine's.
- Pinning `build123d` or `ocpsvg`. This change removes the reason to.

## Decisions

### D1. The promise is stated on the ARTIFACT, in both specs

The `markings` spec owns what a marking artifact *is*, and the `export` spec
owns what a consumer of the document may *rely on*. The finding was filed
against `export`, and the viewer — the consumer that needs it — reads the
document, so `export` must carry it. But a promise a consumer relies on and
the producer's spec does not state is a promise with no home: a future
`markings` cycle could change the producer without ever reading the `export`
spec. So both, phrased for their own reader: `markings` says the producer
winds the artifact outward whatever the artwork gave it; `export` says a
consumer may treat a decal's own normals as outward and need not inspect the
part.

Both are MODIFIED requirements reproducing their existing text and every
existing scenario unchanged, per the delta rule.

**Alternative rejected:** `export` alone, per the literal finding. It leaves
the producer free to drift out from under the consumer's promise, which is the
failure mode this cycle exists to remove.

### D2. The orientation happens in `Svg.tessellate()`, not `Svg.regions()`

Both were candidates. `tessellate()` wins, on two independent grounds.

**The seam.** The red path has to be reachable. Fact 3 above says a reversed
face **cannot be authored in SVG** — `ensure_face_normal_up` intercepts every
one — so no committed fixture drawing can produce the failure, and the only
way to reach it is to substitute the faces. The natural seam is `Svg.regions()`,
which is the module's own "what the drawing holds" boundary and is already
exercised directly by `ArtworkReductionTest`. If the orientation lived *in*
`regions()`, a test that patches `regions()` would patch away the fix and stay
red forever. Putting the orientation one layer out, in its only caller, makes
`regions()` a usable seam: the test supplies reversed regions, `tessellate()`
orients them, and the test goes green on the real production path.

**The meaning.** `regions()` is documented as "the drawing's CLOSED regions" —
a faithful reading of the file, and a reader who asks it what the file holds
should get what the file holds. `tessellate()` is documented as "the artwork as
flat triangles" — the geometry that is actually placed. The winding promise is
about triangles, so it belongs where the triangles are made.

The step itself is four lines at the top of `tessellate()`'s loop:

    for face in self.regions():
        if face.normal_at().Z < 0:
            face = b3d.Face(face.wrapped.Complemented())
        points, facets = face.tessellate(tolerance)

`Complemented()` returns a new `TopoDS_Face` and does not mutate the original
(verified), preserves the face's holes (verified on a face with an inner wire:
8 triangles before and after), and flips the tessellation's winding exactly
(signed 2-D area `+84` → `-84`, and back). `normal_at()` with no argument
evaluates at the face's UV centre and is the same quantity `ensure_face_normal_up`
tests, so the two agree and the step is a no-op wherever ocpsvg already ran.
`build123d` is already imported inside `Svg.regions()`; `tessellate()` needs
the same import, which costs nothing it was not already paying.

The strict `< 0` comparison matters: a face whose normal is exactly `+Z` is
left alone, byte for byte, which is what makes the no-op measurable rather than
merely argued.

**Alternative rejected:** flipping triangle winding in 2-D after tessellation,
by signed area. It is per-triangle, so a sliver of near-zero area gets an
arbitrary answer, and it would have to run over every triangle of every decal
instead of once per region — 4 508 triangles for the Curta's results dial
against 10 regions.

**Alternative rejected:** orienting in `Marking.surface()`, after `tessellate()`
returns. By then the faces are gone and only 2-D points remain, which is the
per-triangle problem above.

### D3. `scale` must be positive, or the promise is not total

`Svg.tessellate()` multiplies its 2-D vertices by `scale` **after** meshing
(`markings.py:225-227`), and `scale` is not validated anywhere. A negative
`scale` mirrors the artwork plane, which reverses the effective winding of
every triangle after the faces were oriented — defeating D2 from a project's
own class body, silently, and with no error.

It is refused instead of compensated for, because a negative scale is a
mistake on its own terms and not a unit conversion: it mirrors every glyph, so
the decal reads backwards. Zero is refused with it — it collapses the artwork
to a point. The refusal goes in `Svg.__init__`, where `Wrapped`'s `radius` and
`pitch` refusals already live, and names the value the way they do; it cannot
name the class, because `__init__` runs while the class body is still
executing, which is equally true of `Wrapped(radius=0)` today.

This is the one decision beyond the finding, and it is **severable**: it has
its own requirement paragraph, its own scenario and its own task. Cutting it
leaves D1 and D2 intact and the promise true for every artwork the framework
itself produces — but then the spec's SHALL is defeasible from a class body,
which is why it is proposed rather than merely noted.

**Alternative rejected:** flipping the winding when `scale < 0`. It makes a
mirrored, backwards-reading decal *correct* in the spec's terms, which is
worse than refusing it.

### D4. The producer recipe stays `marking-svg-v1`

`AbstractBaseNode._artifact_recipe` returns `marking-svg-v1:<tolerance>` for a
marking path, and a changed recipe re-derives every decal on disk. It does not
change here, for a reason stronger than "the bytes probably match":

- **No decal on disk can be wrong.** A wrong decal would need a reversed
  artwork face, and fact 3 says `import_svg` has never returned one. There is
  nothing out there to repair.
- **The bytes are measurably identical.** All three fixture decals hash the
  same before and after, both from upright and from reversed regions. The
  orientation step is not "probably" a no-op on correct input; it is one.

Bumping to `v2` would therefore re-derive every decal in every project cache
to produce identical bytes. The recipe exists to catch a producer whose
*output* changed; this producer's output did not.

### D5. No ADR

ADR-120 already decided what a marking artifact is, that it is an open sheet,
that it sits on the nominal surface with no offset, and that any separation is
the renderer's constant. This change states a **conformance property** of that
artifact — which side of the sheet is the air — and crosses no boundary, adds
no interface, and chooses between no architectural options. The one thing it
changes about the system's structure is negative: it stops the framework
depending on a transitive dependency's behaviour for something it publishes,
which is the removal of an undocumented coupling, not the creation of one.

Recorded here rather than left silent, because "no ADR" is itself a judgment
the reviewer should be able to check.

## Risks / Trade-offs

- **`normal_at()` costs a `BRepGProp` evaluation per region.** → Ten regions
  for the Curta's largest artwork, fourteen for `upper_housing_numbers.svg`,
  against a tessellation that already produces thousands of triangles. Below
  noise, and paid only inside a build that is meshing an artwork anyway.
- **`normal_at()` on a non-planar face is ill-defined.** → Every face reaching
  here comes from `import_svg`, which produces planar faces in `z = 0`; a
  non-planar artwork face is not a thing SVG can express. The evaluation is at
  the UV centre, which is the same point `ensure_face_normal_up` uses, so the
  two cannot disagree about a face they both see.
- **The red test patches a production seam.** → It patches `Svg.regions()`,
  which is a documented public method with its own tests, to return
  `Face(f.wrapped.Complemented())` for each real region — real artwork
  geometry, really reversed, through the real `tessellate()`, `place()` and
  `mesh_bytes()`. The alternative is no red at all, since SVG cannot express
  the input. Recorded as a structural blind spot in the honest sense: the test
  proves the producer repairs a reversed region, not that `import_svg` will
  ever hand it one.
- **A future artwork kind (`Dxf`, text from a font) must keep the promise
  too.** → The promise is stated on the **artifact**, not on `Svg`, so a
  future artwork class inherits the obligation and the `markings` spec's
  scenarios are already written against "the drawing tool" generically. Noted
  for the `Dxf` cycle, which ADR-120's proposal already defers.
- **The viewer's residual is untouched.** → A part declaring
  `linear_deflection` above 0.15 mm may still show punch-through. That is a
  magnitude question and explicitly out of scope; this change guarantees only
  that the lift goes the right way.

## Migration Plan

None. No artifact is invalidated, no recipe moves, no document field changes,
no public signature changes except that `Svg(scale=…)` refuses a value it
previously accepted and silently mis-built. Rollback is reverting the commit;
decals rebuilt under either version are byte-identical.

## Open Questions

- **Should the finding be recorded in `workflow/warts.md`?** It is not there:
  the `# Calculators (2026-09-15, markings applied after the part is made)`
  entry does not mention winding, and the viewer's design says the reviewer
  filed it without saying where. Promoting it straight to a ratified spec
  promise arguably makes the wart entry moot. Left to the pilot; this cycle
  writes no `workflow/` note.
- **Should `solid-node` pin `build123d`, now that it has stopped depending on
  `ocpsvg`'s fix-up?** Out of scope here and unaffected by this change either
  way, but the dependency audit it suggests is real.
