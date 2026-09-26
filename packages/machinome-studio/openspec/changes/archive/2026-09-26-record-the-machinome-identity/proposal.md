## Why

On 26 September 2026 the pilot asked for the Machinome visual identity to
be applied to the studio empirically: make the change first, assess it
live, then see what the records must say. The identity was applied
(`b90747a`), assessed and corrected in two steps the same day: the
identity orange as the interface accent read harsh on the studio's cool
dark surfaces and the amber came back (`47657e3`); the studio got a white
favicon on a black plate so a studio tab tells apart from a machinome.org
tab (`e43ec03`). The pilot merged all three into `main`. The reference
design and the `product-identity` spec still describe the studio before
that: an amber square mark and a typed name in the title bar, IBM Plex
Sans, a 38px title bar and no assets. This change makes the records say
what the studio now does, so the next interface change starts from the
truth. Nothing about the interface changes.

## What Changes

- `product-identity` gains a requirement that the browser surface wears
  the Machinome identity: the wordmark lockup with a `Studio` qualifier in
  every title bar, the interface and technical faces, the intact identity
  release, the studio's own favicon, and the boundary that the identity's
  orange is not an interface colour.
- `docs/design/README.md`, the reference design, is corrected where the
  identity superseded it: the title bar's contents and height, the
  typography, the colour note on the accent, and the assets the product
  ships.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `product-identity`: the customer-facing identity is now also visual, and
  the requirement states what a maker sees and what the studio may not do
  with the identity's assets.

## Impact

- Records only: `openspec/specs/product-identity/spec.md` after archive,
  `docs/design/README.md`. No source, test, manual or asset changes; the
  behaviour being recorded is already on `main` with its tests
  (`tests/test_product_identity.py`, the hub identity scenario in
  `tests/test_shop_lifecycle_e2e.py`).
- The identity repository's decision history records the same application
  from its side (its commit `779d727`); this change does not touch that
  repository.
- No ADR: the decision is a product design one, held by the reference
  design and the spec, not an architectural boundary.
