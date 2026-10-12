# Incremental path-piece evaluation Specification

## Purpose

Keep a running machine's repeated path-piece evaluation exact while avoiding expression work whose inputs have not changed between pieces.

## Requirements

### Requirement: Rebinding a followed quantity does no unchanged work

When a running step follows an expression over successive path pieces, the viewer SHALL reuse a previously evaluated node only when every input on which that node depends has the same value and presence as at its previous bind. Changed nodes and their dependents SHALL be evaluated in the same order, through the same operators and on the same operands as a whole bind. An `at` sample SHALL neither replace nor leak into the values retained for a bind. The resulting float SHALL be bit-identical to evaluating the whole expression for that piece; this optimization SHALL change no search points, tick duration, branch, admission, stop, committed bank or replay.

#### Scenario: Branch reading stays the same
- **WHEN** a path is rebound with a distinct values object whose relevant bank values and presence are unchanged
- **THEN** it returns the same value and resolves no expression node a second time

#### Scenario: A branch placeholder changes
- **WHEN** one branch placeholder changes between pieces and all other inputs stand
- **THEN** only nodes in that placeholder's dependent cone are resolved, and the result matches a whole expression evaluation bit for bit

#### Scenario: Point sampling cannot contaminate a later piece
- **WHEN** a moving coordinate is sampled at a later point, then the same path is rebound under another piece's branch reading
- **THEN** the new bind reads only its own supplied values and returns the same value as a whole expression evaluation

#### Scenario: Actual OperatingCurta export remains equivalent over a bounded crank window
- **WHEN** the viewer executes the first 48 ticks of a crank turn on the OperatingCurta's 213-coordinate document after setting selector 1
- **THEN** its admitted travel and every committed coordinate are unchanged while redundant expression resolutions fall
