## Context

`BRepClass3d_SolidClassifier` decides inside and outside from the solid's
face orientations. A solid published inside out (Thor's `Art4BodyBot`,
signed volume −113,674.9 mm³; a unit box reversed, −1 mm³) has every face
pointing inward, and the classifier reads a point at (100, 100, 100) as
inside it (verified on OCP 7.8.1). The engine consults the classifier in
`_false_empty_witness` (ADR-142) and in `_classified_out` under
`mutually_outside` (ADR-092). The Boolean, fusion and volume are unaffected
by orientation in the sense Thor relies on: its record says the published
orientation booleans correctly and the reversed one does not.

## Goals / Non-Goals

**Goals:** no classifier verdict is ever taken on an inside-out solid; the
guard says which operand is inside out and why it cannot verify; Thor's
Booleans keep working.

**Non-Goals:** repairing an inside-out solid; refusing it at load, in the
Boolean, in fusion or in volume; any change to the witness's stencil or
budget (a separate finding).

## Decisions

1. **Detection is the signed volume, strictly negative.** `GProp` mass of
   an inside-out solid is negative; it is the same number `solid_volume`
   already sums, computed per solid and cached nowhere, since the test
   runs once per guard call on solids that are placed copies. A zero or
   positive volume is not inside out. Alternative: a classifier probe far
   outside the solid's box; rejected as it consults the instrument in
   question.
2. **The guard refuses, the containment tier declines.** The witness has no
   other instrument and the common cannot be verified, so the guard fails
   closed naming the operand, as it does for a failed section. The
   containment tier's existing answer for "cannot tell" is `False`, which
   sends the pair to the Boolean that is right for these parts; raising
   there would turn every face-box-settled pair of Thor's two parts into
   an error, which is the "everywhere" outcome the pilot did not choose.
3. **Named at the guard site, not inside the witness.** `intersect_shapes`
   has the operand names; it tests both operands before calling
   `_false_empty_witness` and raises `BrepCommonVerificationError`
   directly, so the message reads "B-rep common of A and B was empty and
   cannot be verified: B is inside out (signed volume −1.0 mm³), so its
   classifier reads every point as inside".
4. **ADR-142 is amended, not replaced:** one paragraph recording that the
   witness is never consulted on an inside-out operand.

## Risks / Trade-offs

- [A solid whose volume is negative for another reason] → OCCT's volume
  sign follows face orientation; no other cause is known. The refusal names
  the number so a reader can judge.
- [Thor's two tests fail with a different message] → they are red already,
  for the project's reasons; the new message names the real cause.
