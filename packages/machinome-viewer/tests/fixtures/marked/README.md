# The marked bench, as an export fixture

`manifest.json` is a widget-less `machinome export` of the framework's own
marked test project — `machinome`'s `tests/markings_project/assembly.py:Bench`
(the `carry-markings-on-a-part` change, ADR-120) — **verbatim**, beside the
five STLs it names. Nothing here edited it, and nothing here regenerates it.
It was written by

```
PYTHONPATH="$PWD" machinome export tests/markings_project/assembly.py:Bench \
    -o <dir> --no-widget
```

run from a machinome checkout at `8d29cf5` or later, and copied in whole:
59,220 bytes, of which the document is 2,700 and the meshes 56,520.

## What the document settles

Four facts this cycle needed and no prose had:

1. It declares **`version: 2`**. The `markings` list really is additive: a
   marked document may declare any version this viewer reads, and the
   capability is gated on none of them.
2. `plate` carries **two** markings — `badge` then `band`, in declaration
   order — with **different colours** (`#FFFFFF` and `#C0C0C0`).
3. `dial`'s own `color` is **`null`**, so the part renders through
   `MeshNormalMaterial` while its `digits` decal is `#FFFFFF`. A part's
   inherited colour and a marking's own colour are visibly independent, and
   inheritance never reaches a decal.
4. The `band` decal lies at radius **12.0** on a plate whose own bounding box
   is **±10.0**. A decal is not guaranteed to be inside its part's
   silhouette: the producer places it where the declaration says, which is why
   the camera fit box counts decals in.

## Why the part meshes are real

`pascaline`, `lock` and `touched` stand their documents' geometry in with unit
cubes, because those fixtures test a run and a gesture, where a cube shows
what a digit drum shows. This one tests **pixels on a surface** — the decal's
colour where the decal is and the part's where it is not — and that question
is meaningless unless the decal genuinely lies on the part it marks. The two
part meshes are 25,768 of the 59,220 bytes, and they are the cheapest honest
answer.

`dial-Dial-9f2c3557d753.stl` is the dial (R = 9.45 mm, meshed at its declared
`linear_deflection` of 0.05 mm) and `…marking-digits.stl` is its wrapped
decal: an open sheet of 448 facets lying on the nominal cylinder, with no
thickness and no offset. The anti-z-fighting bias that draws it over the
surface is the viewer's own rendering constant (`MARKING_LIFT` in `tree.ts`),
not anything this document states about where the part's surface is.

## The unmarked twin is not committed

Every "renders exactly as before" and "reads exactly as before" assertion
compares this document against the same document with its `markings` keys
stripped. That twin is written by the test into its own temporary staging
(`tests/support.py`'s `strip_markings`), never here.
