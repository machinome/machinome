## ADDED Requirements

### Requirement: Certified swept two-envelope following

A running Follow SHALL keep one banked scalar retained coordinate within the two matched authored envelopes by applying the ordered projection `max(lower, min(retained, upper))` through every certified affine piece and both numeric sides of each path join. It SHALL retain its exact landed value when a surface retreats and SHALL use the existing authored source and expression arithmetic without endpoint-only projection, changed timestep, changed uniform Bound sample count, or a new tolerance. It SHALL admit only affine source ancestry and piecewise-affine envelope paths; an unsupported or non-finite path SHALL refuse the entire tick atomically.

Only run inputs, held banked sources, and unbranched affine ordinary-law chains whose executor supplies exact linear source paths qualify as source ancestry. A wiring or formula endpoint chord SHALL NOT be substituted for its different point arithmetic.

#### Scenario: Push, release, and opposite surface
- **WHEN** a lower envelope rises past a free retained coordinate, later retreats, and an independently driven upper envelope moves inward
- **THEN** the lower pushes it out, retreat does not pull it back, and the upper pushes it inward from the retained position

#### Scenario: Interior peak survives a coarse tick
- **WHEN** a certified piecewise-affine lower envelope rises to a knot maximum and falls before a single requested tick ends
- **THEN** the retained coordinate holds the interior maximum instead of returning to the endpoint envelope value

#### Scenario: Uncertified motion refuses atomically
- **WHEN** a source path or an envelope piece is curved, unclassified, non-finite, domain-invalid, or outside the supported affine-source ancestry
- **THEN** the request refuses without changing the bank, tick, command admission, or snapshot

### Requirement: Matched Bounds stop incompatible Follow envelopes

When Follow envelopes become incompatible, its ordered projection SHALL expose a positive level to the matching dynamic Bound, and the run SHALL use the existing first-outward contact bracket, bisection tolerance, source-group attribution, absolute landing, and atomic commit rules. The Bound search SHALL retain every existing uniform probe and additionally inspect certified envelope piece boundaries and their representable cut sides. A positive one-sided closure without a representable positive probe SHALL refuse atomically instead of passing contact or inventing a stop.

#### Scenario: Curta raised carriage blocks after positive crank travel
- **WHEN** the collar holds the ball inward at 6 mm and the bell lower envelope rises through it during a coarse crank request
- **THEN** the crank stops at a positive admitted angle below one degree, the ball and sources remain within their Bounds, and lowering the carriage relieves the stop

#### Scenario: Sub-grid transient inversion
- **WHEN** two certified affine envelope paths become inverted and feasible again entirely between adjacent uniform Bound probes
- **THEN** the additional certified cut-side evidence finds the first representable outward contact and blocks the connected source rather than missing the interval

#### Scenario: Closure-only precision cannot be bracketed
- **WHEN** a one-sided affine piece closure is outside its matched Bound but the neighboring representable fractions do not expose a positive level
- **THEN** the tick refuses atomically as unsupported precision rather than waiving the violation

#### Scenario: Relief and replay are deterministic
- **WHEN** a Follow request is stopped, the run is snapshotted, restored, and the same request is replayed
- **THEN** the source admissions, stops, exact retained landing, and bank are reproduced; a later retreating or relieving request does not pull a free follower
