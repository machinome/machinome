# Foundation validation

Date: 2026-09-11. Environment: Linux, Python 3.12.

- The five formula family files compare byte-for-byte equal to solid-node
  2bdc50b37be920e79202d1c9e9c5700e43f525e0. Package import paths and ownership
  docs changed; the equations did not.
- Against the extracted framework wheel: 28 tests and 24 subtests passed.
  This includes numeric reference values, inverse identities, geometric closure,
  numeric/symbolic parity, declarative integration and a helper driving a
  Prismatic joint through a motion relation.
- Against the math source exported from the released v0.6.0 tag: 24 tests and
  24 subtests passed; two modules covering unreleased declarative/motion APIs
  skipped. This verifies the required released math surface, not a fresh install
  of the full released CAD dependency stack.
- scripts/check-dist built wheel and sdist with setuptools 84.0.0, passed
  twine's strict metadata checks, installed each into separate temporary
  directories and passed numeric/symbolic smoke checks outside the checkout.
  Both artifacts carry Apache-2.0 metadata, LICENSE, NOTICE and the solid-node
  dependency, and neither bundles solid_node.
- The refactored framework separately passed 440 tests and 565 subtests, and
  its installed wheel ran math/motion with mechanics unavailable and the old
  solid_node.mechanisms import absent.

The workspace registers an editable solid-node checkout. Checks using released
source or the framework wheel ran with Python -S and explicit dependency paths
to prevent that editable finder from supplying missing modules from main.
Distribution smoke checks verify that helpers load from the installed target.

No mechanical project was changed or revalidated. No CAD geometry or poses were
changed, so no new snapshots were generated. No Python 3.11 run, new dependency
resolution of the full CAD stack, publication or remote integration is claimed.

The corresponding framework extraction and its documentation-build limitations
are recorded under that repository's archived extract-mechanics change.
