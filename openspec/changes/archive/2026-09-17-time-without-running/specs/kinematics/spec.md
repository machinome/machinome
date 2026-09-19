## MODIFIED Requirements

### Requirement: Declared time base

A root assembly MAY declare its time base as a class attribute named `time`
holding one of THREE declarations exported from `solid_node.motion.ports` —
the module that answers what moves, alongside the port kinds — and no
longer from `solid_node.node`: `Time(loop=<seconds>)`, the LOOPING base,
`Time.running()`, the RUNNING base, or `Time.elapsed()`, the ELAPSED base.
Under the looping base `loop` SHALL
be a positive finite number of seconds: the span of machine time one turn
of the animation timeline covers. Under the running base and the elapsed
base `loop` SHALL be `None`, because elapsed simulation seconds never
wrap. `Time()` with none of them SHALL be refused naming all three
spellings. The declaration SHALL be
frozen class metadata readable off the class (`Root.time.loop`, and
`Root.time.mode` reading `'loop'`, `'running'` or `'elapsed'`); assigning
`self.time` SHALL fail naming `set_keyframe`. Two declarations SHALL be
equal, and SHALL hash alike, exactly when they declare the same base with
the same `loop`: `Time.running()` and `Time.elapsed()` are NOT equal,
though both carry `loop` `None`.

A `Time` declaration of ANY base SHALL be refused at class-definition
time when it is bound to any attribute name other than `time`, or when the
declaring class is not an `AssemblyNode`, each with an error naming the
rule. A declaration below the root SHALL be refused at the read, naming the
descendant and the root, for every base alike.

Under the RUNNING base `self.time` SHALL read elapsed simulation seconds
when bound — by a running simulation, which binds `k*dt` as the
`simulation` capability states, or by `set_keyframe`/`set_state(time=)`,
which callers state in seconds — and, unbound, bare `$t` exactly as an
undeclared root reads, because elapsed seconds have no symbolic form until
a compiled program is published. Every producer that reads the declaration
SHALL treat a `loop` of `None` as no loop: the document's `animation`
object SHALL carry no `loop` key, a snapshot at a fraction of the timeline
SHALL keyframe the fraction as it does for an undeclared root, and a
running root's document SHALL therefore be the document an undeclared root
publishes. What the running base changes is what a simulation over the
root owns and integrates, stated by the `simulation` capability; nothing
else about the tree changes.

Under the ELAPSED base `self.time` SHALL mean exactly what it means under
the running base — elapsed simulation seconds that never wrap, the bound
number when a simulation, `set_keyframe` or `set_state(time=)` bound one,
and bare `$t` unbound — and every producer SHALL read its `loop` of `None`
as no loop by the same sentence above, so an elapsed root's document SHALL
also be the document an undeclared root publishes, byte for byte. What the
elapsed base CHANGES is stated by the `simulation` capability and is
confined to a CLOCKED root: there, and only there, `time` is a banked value
of the simulation that a request may move. A root declaring the elapsed
base whose tree declares no `State` SHALL be ADMITTED and SHALL be
unchanged in every observable particular — the same fixed-`dt` stepping
simulation, the same reads, the same published bytes — because the time
base states what `time` MEANS and the state discipline alone selects which
simulation runs over the tree.

The elapsed base SHALL NOT be a route into the running mechanics: it SHALL
NOT make a simulation own or integrate any coordinate, SHALL NOT compile a
program, and SHALL NOT change anything about `Time.running()`.

Under the LOOPING base `self.time` SHALL read machine time in seconds on
every path:

- unbound, it SHALL be the symbolic expression `$t * loop`, so the normalized
  0..1 `$t` timeline is unchanged and published expressions carry the
  multiplication verbatim (`(360 * ($t * 43200))` rather than a constant);
- bound by `set_keyframe(t)` or `set_state(time=t)`, it SHALL be exactly the
  bound number, which callers state in seconds;
- under a stepped simulation, it SHALL be the simulation clock in seconds
  exactly as the `simulation` capability already states.

The time base is a property of the root: every assembly below it SHALL read
the root's time base, whether or not it declares one itself. Reading `time`
on a linked descendant whose own class declares a `Time` SHALL fail naming
the descendant and the root, so a stray declaration can never silently scale
one subtree differently. An assembly that is itself the root of the tree it
is read in — including a sub-assembly loaded on its own — uses its own
declaration.

A root that declares no time base SHALL keep the normalized 0..1 behaviour
of the "Normalized animation time" requirement unchanged.

#### Scenario: Symbolic time carries the loop

- **WHEN** a root declares `time = Time(loop=43200)` and a nested assembly
  rotates a child by `360 * self.time / 3600`
- **THEN** the nested assembly reads the same `$t * 43200` expression as the
  root, and the serialized operation names `$t` with the loop inside the
  expression rather than a constant

#### Scenario: Keyframes bind seconds

- **WHEN** `set_keyframe(2700)` is called on a root declaring
  `Time(loop=43200)` containing a nested assembly
- **THEN** both assemblies read `time == 2700` as a float and their meshes
  resolve at the pose 2700 seconds into the loop

#### Scenario: Clearing restores the loop expression

- **WHEN** a root declaring a time base is keyframed and then cleared
- **THEN** `time` reads the symbolic `$t * loop` expression again and the
  nested child's operations serialize to the same strings a never-keyframed
  render produces

#### Scenario: A misnamed declaration is refused

- **WHEN** a class body binds `clock = Time(loop=60)`
- **THEN** class definition fails with an error naming `time` as the only
  name a time base may be bound to

#### Scenario: A declaration below the root is refused

- **WHEN** a root without a declaration links a child assembly whose class
  declares `time = Time(loop=60)` and that child's `simulate()` reads
  `self.time`
- **THEN** the read fails naming the child and the root

#### Scenario: A sub-assembly loaded alone uses its own declaration

- **WHEN** an assembly declaring `Time(loop=60)` is loaded as the root
- **THEN** its `time` reads `$t * 60`

#### Scenario: The declaration is readable off the class

- **WHEN** a producer reads `type(root).time` on a root declaring
  `Time(loop=43200)`
- **THEN** it gets the declaration and `loop == 43200.0`, without
  constructing the node

#### Scenario: An undeclared root is unchanged

- **WHEN** a root declares no time base
- **THEN** `self.time` is bare `$t` unbound and the keyframed fraction when
  bound, exactly as before

#### Scenario: The time base is imported from the motion package

- **WHEN** a root's module writes
  `from solid_node.motion.ports import Time` and declares
  `time = Time(loop=43200)`
- **THEN** the declaration behaves exactly as it did when `Time` came from
  `solid_node.node`, and `from solid_node.node import Time` raises
  `ImportError` naming `solid_node.motion.ports`

#### Scenario: The running base is declared and readable off the class

- **WHEN** a root declares `time = Time.running()`
- **THEN** `type(root).time.mode` reads `'running'`, `type(root).time.loop`
  reads `None`, `declared_time(type(root))` returns that declaration, and
  `Time()` with no argument raises naming `Time(loop=...)`,
  `Time.running()` and `Time.elapsed()`

#### Scenario: Under the running base unbound time reads bare $t

- **WHEN** a root declaring `Time.running()` is rendered with nothing bound
- **THEN** `self.time` on the root and on a nested assembly reads `$t`,
  `set_keyframe(2.5)` makes both read `2.5`, and clearing restores `$t`

#### Scenario: The running base obeys the declaration rules

- **WHEN** a leaf class declares `time = Time.running()`, a class body binds
  `clock = Time.running()`, or a linked child assembly declares it under a
  root and its `simulate()` reads `self.time`
- **THEN** the first two fail at class definition naming the rule and the
  third fails at the read naming the child and the root, exactly as
  `Time(loop=...)` does

#### Scenario: A running root publishes no loop

- **WHEN** a root declaring `Time.running()` is exported and snapshotted at
  a fraction of the timeline
- **THEN** the document's `animation` object carries no `loop` key and is
  byte-identical to an undeclared root's, and the snapshot keyframes the
  fraction

#### Scenario: The elapsed base is declared and readable off the class

- **WHEN** a root declares `time = Time.elapsed()`
- **THEN** `type(root).time.mode` reads `'elapsed'`, `type(root).time.loop`
  reads `None`, and `declared_time(type(root))` returns that declaration
  without constructing the node

#### Scenario: Under the elapsed base unbound time reads bare $t

- **WHEN** a root declaring `Time.elapsed()` is rendered with nothing bound
- **THEN** `self.time` on the root and on a nested assembly reads `$t`,
  `set_keyframe(2.5)` makes both read `2.5`, and clearing restores `$t`

#### Scenario: The elapsed base obeys the declaration rules

- **WHEN** a leaf class declares `time = Time.elapsed()`, a class body binds
  `clock = Time.elapsed()`, or a linked child assembly declares it under a
  root and its `simulate()` reads `self.time`
- **THEN** the first two fail at class definition naming the rule and the
  third fails at the read naming the child and the root, exactly as
  `Time(loop=...)` does

#### Scenario: An elapsed root that declares no state is unchanged

- **WHEN** a root declaring `Time.elapsed()` and no `State` is simulated
  with `Sim(node, dt)`, stepped, exported and snapshotted at a fraction of
  the timeline
- **THEN** the simulation is the ordinary fixed-`dt` stepping loop, `sim.time`
  reads `tick * dt` seconds, each step binds exactly that number of seconds
  as the tree's `time` — what a stepped simulation binds under every base
  today, an undeclared root included — the document's `animation` object
  carries no `loop` key and is byte-identical to the same tree declaring no
  base at all, and the snapshot keyframes the fraction
