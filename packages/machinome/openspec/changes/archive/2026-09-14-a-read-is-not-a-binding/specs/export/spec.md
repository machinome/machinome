## MODIFIED Requirements

### Requirement: A committed bank poses the geometry

Under a running root the producer SHALL serialize the tree with every JOINT
COORDINATE of the linked tree bound to a symbolic token of its own qualified
id, beside every declared driver's token, through the same internal binding
path the symbolic driver mode uses and never through the numeric snapshot
door. The document's ordinary pose expressions SHALL therefore name bank
ids: a joint's own placement operation SHALL be that coordinate's id, or an
expression over the ids of a joint owning several; a plain port, a derived
coordinate and a flexible leaf's `params` SHALL be expressions over whatever
bank ids drive them; and a driver that poses geometry without passing
through a joint SHALL keep publishing its driver id.

A consumer therefore evaluates, per frame, exactly the expressions it
evaluates for any other document, from a scope holding the whole bank rather
than the driver values alone. No second table of poses SHALL be published,
and flexible parts SHALL follow this rule unchanged.

The producer SHALL restore every coordinate it bound — its value, its
binder and its freshness marks — and SHALL re-place the joints from what
their coordinates then hold, so a caller that held a posed tree still holds
one. A declared range SHALL NOT judge a symbolic binding.

The restore SHALL leave the tree able to be POSED again, not only read: a
tree whose coordinates an enumeration bound before the publication SHALL,
after the publication, clear and re-solve exactly as it would have if
nothing had been published. Whatever record the framework keeps of which
coordinates an enumeration bound — the record the next pass reads to decide
what is stale — SHALL therefore be restored beside the coordinates
themselves, because the publication's own enumeration replaces it while
binding none of those coordinates itself.

PUBLISHING SHALL REFUSE NO DECLARATION a pose accepts. In particular, a
relation a CHILD assembly declares into its own coordinate, whose value a
relation the ROOT declares then READS to drive another coordinate, is a
legal shape under a running root: the tree poses, a simulation runs it, and
its document publishes, naming that coordinate's id wherever it poses
geometry. A relation's SOURCE SHALL NEVER be reported as one of its
binders.

#### Scenario: A joint's placement is its coordinate's name

- **WHEN** a running root drives a register wheel through a carry law and
  its document is published
- **THEN** that wheel's rotation operation is the single name of its joint
  coordinate, and the carry law appears only inside `program`

#### Scenario: A plain port follows the bank

- **WHEN** a running root's readout port is driven from a joint coordinate
  at ratio −1
- **THEN** that port's pose expression is an expression over the joint
  coordinate's qualified id

#### Scenario: A flexible part follows the bank

- **WHEN** a running root holds a flexible leaf whose shape parameter is
  driven from a joint coordinate
- **THEN** its `params` expression names that coordinate's qualified id and
  its `spec` is unchanged

#### Scenario: Every name the document reads is declared

- **WHEN** a version 5 document is published
- **THEN** every free name its operation and `params` expressions read, after
  the bindings table is resolved, is the clock name, a key of the `drivers`
  table, a key of `program.coordinates`, or a `program.intermediates` entry

#### Scenario: The tree is left as it was found

- **WHEN** a posed running tree is serialized and the producer returns
- **THEN** every joint coordinate holds the value, binder and placement it
  held before, and rendering it again reproduces the same pose

#### Scenario: A child states the relation and the root reads it

- **WHEN** a running root whose child assembly declares
  `key.insert.drives(p1.lift, …)` and whose own body declares
  `plug.p1.lift.drives(d1.lift, ratio=-1)` is posed and its document is
  published
- **THEN** the document is published, `d1`'s placement names `d1.lift`, and
  nothing is refused — with the root's law reading forward only, as well as
  with one that inverts

#### Scenario: A posed tree re-solves after publication

- **WHEN** a running tree posed by `set_state` is published and then posed
  again
- **THEN** every coordinate holds the value that pose computes, each bound
  by the relation that states it, and no coordinate is reported as bound by
  two statements
