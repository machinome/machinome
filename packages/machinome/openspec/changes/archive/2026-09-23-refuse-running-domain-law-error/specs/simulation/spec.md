## ADDED Requirements

### Requirement: A running law's non-finite evaluation refuses its tick

When a compiled running law's evaluation at a point the tick already visits raises a numeric domain error or returns `NaN` or either infinity, the simulation SHALL report an `UnsupportedLaw` refusal naming the relation as authored, its declarer, and the driven coordinate. The failing tick SHALL commit no bank, tick-count, record, or posed-tree change, and every command that moved an input in that tick SHALL retire `refused` with only travel admitted in earlier successful ticks. It SHALL NOT evaluate the law at new points merely to find an error.

#### Scenario: An immediate command leaves no active owner after a domain error

- **WHEN** a running machine starts with `feed=0` and `shaft.turn=sqrt(0.1)`, its law is `shaft.turn=sqrt(0.1-feed)`, and an immediate command asks `feed` to reach `0.2`
- **THEN** the command is refused as `UnsupportedLaw` naming the relation, declarer and `shaft.turn`; bank, tick zero, records and pose stand at rest, and `feed` has no active command owner

#### Scenario: A failed later tick preserves earlier admitted travel

- **WHEN** a two-tick move of that machine to `feed=0.2` successfully commits its first tick at `feed=0.1` but the second evaluates the law outside its domain
- **THEN** the second tick is refused, the first tick's bank, record and pose remain, and the command retires `refused` reporting only the first tick's admitted travel

#### Scenario: A finite source does not overflow a running law into the bank

- **WHEN** a running machine starts with `feed=1` and `shaft.turn=1` under the law `shaft.turn=feed*feed`, and an immediate command asks `feed` to reach `1e308`
- **THEN** the law's infinity is refused as `UnsupportedLaw` naming the relation, declarer and `shaft.turn`; the bank remains finite at its rest values, no record is appended, and the command has no active owner

#### Scenario: A finite boundary remains valid

- **WHEN** the machine moves from `feed=0` to its finite law boundary at `feed=0.1`
- **THEN** the tick retains the law's ordinary finite result and the command completes without a domain refusal
