## ADDED Requirements

### Requirement: `check` reports a continuation that crosses a mark

In a take document, a shot that a dissolve, a wipe, a slide or the first
half of a fade still shows past its end keeps running its take time at the
rate it ended with. Resolution SHALL follow each such shot through the
output frames on which its outgoing join shows it, by the frame's own
model-time rule, and SHALL record a **crossing** when the take time posed
on the last of those frames lies past a mark that the shot's take time at
its end reached or had not yet reached (a mark `m` with `end ≤ m <
reached`). The crossing SHALL name the first such mark and the step the
take runs into there, the step whose `at` is the mark. A step boundary
that is not a mark MUST NOT be reported, nor a continuation that only
reaches a mark, nor a shot whose model stands still at its end (held, or
eased to rest). A reframe shows no outgoing shot and crosses nothing; a
posed loop's document records no crossing.

The resolved document SHALL carry each crossing on the outgoing shot's
`model` as `crossing`: the join's `kind` as `join` and its `duration`, the
incoming shot's id as `into`, the `mark`, the `step`'s id, the take time
`reaches` posed on the join's last frame of the shot, how far `past` the
mark it is, and the `report`, the sentence `check` prints; a shot that
crosses no mark SHALL be resolved as before. For each crossing, in film
order, `check` SHALL print the report after the take's line: the shot, the
join and its length, the incoming shot, the mark, the take time reached
and how far past the mark, the step with its input and its `to` or `by`,
and what to do: hold the shot at the mark before it ends, or ease its
model to rest there. A crossing is a report: `check` MUST still pass. A
continuation that would pass the take's last second MUST still be refused
as before, naming the outgoing shot, the take time it would reach and the
export's length.

#### Scenario: The counter's nine dissolves past its mark
- **WHEN** `check` passes on the fixture movie `count`, whose shot `nine`
  ends on the mark `nine` at 6 s still moving and dissolves for 0.5 s into
  `carry` at 10 fps
- **THEN** it prints, after the take's line, `Continuation: shot nine runs
  on through the 0.5 s dissolve into shot carry and crosses the mark nine:
  its last frame there poses take time 6.76 s, 0.76 s past the mark, inside
  step-3, which moves crank by 360; hold the shot at the mark before it
  ends, or ease its model to rest there`, and the resolved `nine` carries
  the same crossing on its `model`, with `mark` `nine` and `step`
  `step-3`.

#### Scenario: The Curta's read-23 before its hold
- **WHEN** the Curta film's `read-23` runs its take time from 5.2 s to the
  mark `added_23` and dissolves into `set-145`
- **THEN** `check` names `read-23`, the dissolve into `set-145`, the mark
  `added_23` and the step after it, which moves the units slide to 5.

#### Scenario: Held at the mark
- **WHEN** a shot's model keys reach the mark before its end and hold it
  there, as the Curta's `read-23` does since its hold
- **THEN** nothing is reported for it, and its resolved model carries no
  crossing.

#### Scenario: A step boundary that is not a mark
- **WHEN** a continuation runs past the end of a step at which no mark is
  declared
- **THEN** nothing is reported.

#### Scenario: Ending before a mark and running past it
- **WHEN** a shot ends its take time before a mark, still moving, and the
  frames of its join pose take times past the mark
- **THEN** `check` reports the crossing of that mark.

#### Scenario: A fade shows the outgoing shot for half its length
- **WHEN** the join is a fade
- **THEN** only the frames of its first half are followed, and a mark the
  shot would pass only in the second half is not reported.

#### Scenario: Past the take's end
- **WHEN** a continuation would run past the take's last second
- **THEN** the document is refused with the words of the existing refusal,
  and no crossing is reported.
