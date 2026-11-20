## MODIFIED Requirements

### Requirement: The viewer evaluates flexible geometry per frame

The package SHALL bundle the molejo JavaScript evaluator and render a
document's `flexible` nodes: each node's `params` expressions are
evaluated in the same scope as operation expressions (`$t` and the
nested driver map), and the resulting values are handed to the molejo
evaluator, which writes vertex data into buffers the viewer allocates
once per node and reuses — vertex count and ordering are declared by
the spec and never change at frame rate, so no reallocation occurs.

Re-evaluation SHALL be bounded the way operation re-evaluation already
is: a flexible node's geometry is recomputed only on frames where a
free variable of one of its `params` expressions changed, and driving
a driver named by no `params` expression SHALL NOT re-evaluate it.

On such a frame the node's geometry SHALL be recomputed only when at
least one of its parameter values differs from the value its present
geometry was computed from, two values being the same only when they
are the same value (`-0` and `0` differ; `NaN` is the same as `NaN`).
When no value differs, the node SHALL keep its vertex data, its bounds
and its buffers as they are: the molejo evaluator is not called and
nothing is uploaded. A node whose geometry is kept SHALL hold exactly
the vertex data the evaluator produces from its spec and its current
parameter values. A node's first evaluation, an evaluation after its
`params` expressions or the document's bindings were replaced, and an
evaluation after the evaluator refused the node SHALL always recompute
its geometry.

The loader SHALL accept documents declaring `version: 2` or
`version: 3`, and SHALL refuse — naming the node and the technology —
a `flexible` node whose `tech` the package cannot evaluate, rather
than rendering a wrong or missing shape.

The binding seam SHALL be pinned by the producer-generated parity
fixture: at least one case evaluates a real flexible document's
parameter expression client-side, feeds it to the bundled molejo
evaluator, and matches the producer's Python-side evaluation of the
same spec and binding within the fixture's tolerance. (Vertex-level
agreement between the two molejo evaluators is molejo's own parity
contract; what this package pins is the expression-to-parameter
binding in front of it.)

#### Scenario: A spring animates in the browser

- **WHEN** a document containing a molejo spring whose `height`
  expression references a declared driver is mounted and that driver
  is driven
- **THEN** the spring's geometry re-evaluates into its existing
  buffers on the frames where the driver changed the spring's
  `height`, with vertex count unchanged

#### Scenario: An unrelated driver does not touch the spring

- **WHEN** a driver named by no `params` expression of the spring
  changes
- **THEN** the spring's geometry is not re-evaluated that frame

#### Scenario: A changed input that leaves every value as it was

- **WHEN** an input a spring's `params` expressions read changes and
  every one of the spring's parameter values is the same as the one its
  present geometry was computed from
- **THEN** the spring's geometry is not re-evaluated that frame: the
  evaluator is not called, and its vertex data, bounds and buffers are
  left as they are

#### Scenario: One input reaches two springs and changes only one

- **WHEN** an input read by two springs' `params` expressions changes
  so that one spring's parameter values change and the other's do not
- **THEN** only the first spring's geometry is re-evaluated that frame

#### Scenario: An unknown technology is refused loudly

- **WHEN** a document carries a `flexible` node whose `tech` the
  package cannot evaluate
- **THEN** loading fails naming the node and the technology, and no
  wrong shape is rendered

#### Scenario: The binding parity case pins the seam

- **WHEN** the widget test suite runs the parity fixture's flexible
  binding case against the shipped evaluator and bundled molejo
- **THEN** the client-side parameter value and resulting evaluation
  agree with the producer-computed expectation within the declared
  tolerance
