## ADDED Requirements

### Requirement: Repeated path samples reuse immutable numeric operations

After a path has been bound successfully, repeated samples of the same immutable moving cone SHALL reuse its operation classification and operand positions. Each sample SHALL still read its current moving inputs and the current piece's standing values, evaluate the same nodes in the same postorder with the same numeric operators and operand order, and report the same first error. Binding a new piece SHALL refresh standing values; a failed binding SHALL NOT publish partial values or structure. This optimization SHALL NOT retain discarded paths or change the number of evaluated path points.

#### Scenario: A changing input crosses several arithmetic operators

- **WHEN** a bound path with shared arithmetic, unary operations and numeric extrema is sampled at several moving input values
- **THEN** every result has the same float bits as whole-graph evaluation at the current inputs, including signed zero and NaN operand selection

#### Scenario: A later sample fails

- **WHEN** a moving input makes an earlier operation fail before another node in the path
- **THEN** that sample reports the original earlier error at the same operation, without returning a cached prior value

#### Scenario: A new piece changes standing values

- **WHEN** a path is rebound with different standing inputs or branch placeholders
- **THEN** its later samples use the new standing values and the path's original node order

#### Scenario: The path is released

- **WHEN** the path and its owner are discarded after repeated samples
- **THEN** operation bookkeeping retains no reference to its expression graph
