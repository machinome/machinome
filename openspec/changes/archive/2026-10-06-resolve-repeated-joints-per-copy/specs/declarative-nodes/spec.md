## ADDED Requirements

### Requirement: A repeated copy carries its position throughout its own construction

Every child a `.repeat()` realizes SHALL carry its `index`, its 0-based
position in the repeat, from the start of its own construction, and not
only once that construction has returned. Everything the copy's
construction runs SHALL read the copy's own `index`, as SHALL every
function that construction calls with the copy. That includes:

- its `check()`;
- a function given as the whole `axis`, `at`, `range` or `carries` of a
  joint its class declares;
- a function given as a frame argument its class declares.

Each copy SHALL therefore resolve its class-declared joint and frame
arguments against its own position, and a binding of the joint SHALL
place each copy by the arguments that copy resolved. Those arguments
SHALL still resolve at the same moment, after the copy's parameters and
its `check()` and before any of its children is realized. The copies SHALL
still share one identity whatever arguments each resolves. A copy SHALL
end its realization carrying its position as `index`, even when its own
constructor assigned an `index` of its own.

What a function sees otherwise SHALL NOT change:

- a node that is not a repeat's copy SHALL carry no `index` during its
  construction;
- a function given at a site, or as a mate's freedom, SHALL be handed
  the declaring parent or the assembly and never the copy;
- a function that fails for any other reason SHALL be refused at
  realization as before, naming the class, the joint or frame, the
  argument and the underlying error, including the attribute it could
  not read.

#### Scenario: Each copy resolves and places its own joint

- **WHEN** a leaf class declares
  `turn = Revolute(axis=lambda node: (0, 0, 1 if node.index == 0 else -1), at=lambda node: (10.0 * node.index, 0, 0), range=lambda node: (0, 90 + node.index), unit='deg')`,
  an assembly declares `guides = Guide().repeat(2)`, and the assembly
  is realized and each copy's `turn` is bound to `30`
- **THEN** copy 0 resolves axis `(0, 0, 1)`, anchor `(0, 0, 0)` and range
  `(0, 90)`, copy 1 resolves axis `(0, 0, -1)`, anchor `(10, 0, 0)` and
  range `(0, 91)`, each copy is rotated by 30 degrees about its own line,
  and the two copies share one `uniq_id`

#### Scenario: An orbit's carried point reads the copy's position

- **WHEN** a leaf class declares
  `spin = Orbit(axis=(0, 0, 1), carries=lambda node: (5.0 + node.index, 0, 0), unit='deg')`
  and is repeated twice
- **THEN** the copies' resolved carried points are `(5, 0, 0)` and
  `(6, 0, 0)`

#### Scenario: A frame argument and a check read the copy's position

- **WHEN** one repeated class declares `seat = Frame(at=lambda node: (0, 0, 3.0 * node.index))`,
  and a repeated declarative class's `check()` records `self.index`
- **THEN** the copies' resolved `seat` frames are at `(0, 0, 0)` and
  `(0, 0, 3)`, and the checks recorded `0` and `1`

#### Scenario: A function failing for another reason is refused as before

- **WHEN** a repeated class declares
  `turn = Revolute(axis=lambda node: node.no_such_thing, unit='deg')`,
  or the class whose `axis` reads `node.index` is realized as a single
  declared child rather than through a repeat
- **THEN** realization raises a `ParameterError` naming the class, `turn`,
  `axis`, `AttributeError` and the attribute it could not read,
  `no_such_thing` or `index`

#### Scenario: What other functions are handed is unchanged

- **WHEN** a site-declared joint on a `.repeat()` declaration has an
  `axis` function that reads `index` off what it is handed, and a legacy
  repeated class's constructor assigns `self.index = -1` before
  constructing its base
- **THEN** the site's function is handed the declaring parent, which has
  no `index`, and is refused naming `AttributeError` as before, and each
  legacy copy reads its position, `0` and `1`, once realized
