# Mechanical contracts

Use this guide to choose what to prove. Look up the available assertions and
their exact semantics in the documentation for the installed machinome version.
These checks establish modeled geometry and kinematics; they do not establish
strength, wear, manufacturing suitability, or physical safety.

## Connectivity and clearance answer different questions

Check that every modeled manufactured piece is one connected body. Watertightness
does not imply connectivity: several closed shells can make a valid STL that
looks like one part. A tangential contact between ingredients does not establish
a printable junction. Where features join, give their union a dimensioned overlap
consistent with the design and check the resulting solid.

Separately, check for unintended overlap between distinct rigid pieces. Apply
this at the physical-piece level: the ingredients intentionally fused into one
piece are not interfering assembly members. Flexible parts need checks appropriate
to their changing geometry rather than being treated as printed rigid pieces.

Keep both connectivity and assembly-interference checks at the model root when
supported. An interference check over one piece passes without testing any pair;
describe that limit. For moving assemblies, repeat it through relevant motion.

Use clearances from the drawing or an explicit modeling assumption. Do not
silence a failure with an arbitrary volume threshold. For intentionally
overlapping upstream representations, preserve an explicit inventory of the
known pairs and measured overlap, with any measurement tolerance justified by
the method. New or changed overlaps must still fail. Distinguish those source
approximations from a design asserted to have clear rigid parts.

## Engagement is positive evidence

Two distant gears satisfy a non-interference test and can be animated at a
perfect ratio. Neither fact proves they mesh. Test that the driven piece is free
within the intended play and blocked by its mate just beyond it. Use both
directions for a two-sided fit and the intended direction for a one-sided stop.
Verify the tooth phase as well as the ratio and direction.

The same pattern applies to a pin in a bore, a captive nut, a sleeve on a shaft,
and an axial retaining lip. Derive play from the design's dimensions; select
the perturbation in the documented local frame. Rotated or mirrored placements
must exercise the same mechanical meaning.

Clear pieces can also float. Where the design says an assembly stands, hangs,
or is bolted down, check its supports using the framework's documented scope.
Make assumed fasteners, glue, or fixed mounting explicit. A geometric support
test is not a load-capacity analysis.

## Independent expectations

Tests may share the design's input dimensions. Compute expected results from
those inputs independently of the implementation's derived values. Reading a
node's own computed clearance back into an assertion cannot catch a wrong
clearance formula. Measurement axes can hide the same mistake: derive them from
the intended frame, rather than following a possibly miswired live placement.

Measure independent gaps independently. Taking the minimum distance across two
gaps can leave a failure in one invisible because the other still wins the
minimum. Check lower and upper bounds where both too tight and too loose fail.

Test parameter relationships at more than the default setting, including a
useful boundary configuration. Check that invalid inputs are refused where the
documented parameter mechanism supports that contract.

## Measurement traps

- A bounding box is not a diameter for a gear or another uneven radial shape.
  Measure distances from the intended axis using the appropriate surface region.
- Cylinder mesh vertices may exist only on the end rims. Vertex-to-vertex
  distance can miss the closest surfaces; use a suitable surface measurement.
- A bore intersecting another feature can lose part of its rim. An average of
  the remaining vertices is a biased center. Measure an intact region or use
  exact geometry when available.
- Two features meeting in one plane cannot always be separated by filtering
  that coordinate. Identify their own axes and geometric regions.
- Imported STL files may already share an assembly frame. Moving every part's
  bounding-box minimum to zero destroys that evidence. Establish units and
  source origins before inferring placement.

Record measurement method, units, frame, and justified precision. Do not make
mesh approximation uncertainty disappear by calling a measurement exact.

## Motion coverage

Sample where the geometry changes fastest. For gears, sweep a tooth pitch in
detail and cover the whole machine cycle more coarsely. A few evenly spaced
whole-cycle poses can repeatedly miss the same collision. Sample transition
paths between instructions, not only their endpoints.

For independent controls, include meaningful combinations. For machines with
history, check repeated actions, reversal where admitted, interrupted motion,
and interleaved operations on the same instance. A rejected command should leave
the state unchanged where the public contract promises that behavior.

For event-driven state, calculate expected outcomes from the mechanism rather
than calling the implementation's update law. Compare at mechanically meaningful
event boundaries and inspect intermediate geometry separately. A posed model
and an operated model need different evidence even when their rest images agree.

## Make a mutation informative

Change code that uses a parameter: remove a clearance term, reverse a rotation,
alter tooth phase, or displace a seat. Changing an input dimension alone is often
inert as a mutation because correct tests intentionally follow design inputs.
Changing a child's default also does nothing if the parent supplies its value.

Choose an error larger than the gap or play the contract is meant to bound.
Confirm the relevant mechanical assertion fails, not merely that the file has
a syntax error. If the mutation survives, investigate the measurement and report
the blind spot. For example, a ratio assertion using absolute values cannot
catch reversed rotation.
