## Context

The Curta Type I trial `simulation.positioning_ball_trial.RadialBallTrial` at `a2d0783` has a banked radial slide and two measured profiles: bell-turn `bell_limit(turn)` is a modulo/piecewise chart; carriage `collar_limit(lift)` is a piecewise chart. The bell-turn and register-lift coordinates are each determined by a direct affine law from their input. The ball has independent dynamic low/high `Bound`s over the same expressions. The current ADR-121 switch law moves the ball outward but pulls it back on bell retreat; a true `max(lower, min(retained, upper))` expression is correctly refused as a continuous self-read. `Play` is deliberately a single direct-source fixed-offset law (ADR-131), so it cannot encode these independent profiles.

The actual graphs compile today: bell has one modulo jump plan and a kinked skeleton, collar is kinked; the existing path compiler produces 30 certified affine bell pieces over 0→−90° and 21 collar pieces over 0→6 mm. The bell chart has a one-ULP difference between two piece endpoint evaluations at 6°; neither joining nor suppressing it under `_agree` is permissible. A full .1 s trial crank tick spans 18°, crossing many profile knots. An endpoint-only clamp would lose an interior peak.

## Goals / Non-Goals

**Goals:**

- Express this one scalar retained ball between two separately authored numeric envelopes; process every certified piece, retain a released contact, and stop a source at incompatible envelopes through its matched dynamic Bounds.
- Preserve all existing self-read, `Play`, Bound-search, source-timing, floating-operation, and snapshot/replay behavior for programs without the new law.
- Publish enough distinct program information for a version-aware browser consumer to reproduce the same mechanical decision.

**Non-Goals:**

- A force, rolling-contact, collision, or general complementarity solver; arbitrary curved or implicit source paths; inferred contact from meshes; changing timestep, the uniform Bound sample count, bisection rounds, or tolerance.
- Correcting project geometry or changing the trial's own source laws, profile tables, Bounds, or production assembly in this framework repository.

## Decisions

### Explicit relation, not a reinterpretation

`machinome.simulation.Follow(lower=, upper=)` is an immutable running-only law. The only accepted relation is `(lower_source & upper_source & retained).drives(retained, law=Follow(lower=callable, upper=callable))`, with two distinct scalar source coordinates and one banked scalar retained target named third. Each callable receives the two ordered source symbols and builds a numeric expression; it cannot read the retained coordinate. Both expressions are compiled through the existing checked graph and jump vocabulary. The compiler refuses a different shape, reversed direction, ambiguous writer, source cycle, invalid numeric graph, or missing rest value by relation identity. An ordinary callable self-read still follows ADR-121 unchanged; a `Play` still follows ADR-131 unchanged.

The project's two dynamic Bounds are mandatory, not merely examples. At compilation the retained coordinate must have a lower and an upper `Bound` whose compiled graph and declared reads structurally match the `Follow` lower/upper graphs and their source names. The bound expressions must not depend on the retained coordinate. An absent or mismatched Bound is refused rather than permitting an inverted interval to commit silently. At rest the retained value and both finite envelopes must be ordered and inside. This syntactic check intentionally does not infer semantic equivalence of differently written expressions.

### Certified path and ordered projection

The retained coordinate is terminal among program edges in this Curta-backed contract: a downstream edge would require its swept follower path, whereas this cycle certifies an absolute landing and Bound prefix replay only. Such an edge is refused at compile time rather than given an endpoint chord.

Source ancestry accepts inputs, held bank coordinates, and unbranched affine ordinary-law chains that the existing path executor represents as exact `Motion.line` values. Wiring/formula ancestry is refused: its one-piece numeric evaluator can differ by many ULPs from an endpoint chord, so a jump partition based on the chord would not certify the actual source path. Curta's bell-turn and lift sources are each direct ordinary affine laws and remain inside this boundary.

At runtime each accepted source must supply its original exact `Motion.line` delta; reconstructing `end-start` can change point arithmetic and move a branch cut. An unexpected non-linear path refuses the tick atomically. For each boundary expression, use the existing graph jump/kink path compiler over those exact source lines to partition the tick. Each boundary piece must be certified affine by the existing shape/trajectory machinery; a curved, unclassified, non-finite, or domain-unsafe piece refuses, not samples or approximates. Union all lower and upper piece cuts. At each piece, advance the retained value by the ordered projection `max(L, min(q, U))` through its source-path endpoints. Inspect both the left closure and right/exact value of every numeric join separately, including the authored modulo branch; never merge a one-ULP difference with `_agree`, snap to a chart knot, or interpolate across a jump. Since each boundary is affine within the piece, endpoint and one-sided closure checks cover its extrema; no hidden midpoint extremum is assumed away.

An inverted interval is not an arithmetic error during a request. Keep the same ordered projection provisionally: it yields `q=L` when `L>U`, so the matched upper Bound has a positive level and can stop the request at the first incompatible contact. The final committed state must satisfy both Bounds; otherwise the run's existing invariant refusal applies. A source that retreats while the ball is inside the interval does not pull it back. Report an exact absolute landing for the retained coordinate, including in prefix replay, so `old + (new-old)` rounding does not erase contact or change restore/replay.

### First-contact evidence and existing Bound localization

Mark Follow as untraced and replay its complete certified prefix for a dynamic Bound; do not invent a chord for a retained path. Keep the uniform Bound fractions and existing outward-level test, bisection rounds, crossing tolerance, group attribution, and stop records. Supplement only a Bound on this follower with the union of its certified piece cut fractions, their representable left neighbors, and the exact/right cut. This exposes a positive interval narrower than one uniform step: an affine `L−U` reaches its maximum at one of these one-sided endpoints. The follower checks each one-sided closure's matched-Bound level directly. If a closure is positive but no representable neighboring fraction gives a positive level to bracket with the unchanged search, refuse the tick atomically as unsupported precision; do not silently pass or invent a contact. Duplicate fractions are ordered/deduplicated without changing the uniform sequence's values.

The full and every prefix propagation must use the same Follow sweep; a Bound replay that lacks the original piece cuts is invalid. With two sources moving, the matched Bound's existing contact-group rule determines which input(s) carry its level outward. No separate physics ownership rule is introduced.

### Program and consumer contract

The edge also carries `lower_plan` and `upper_plan`, each a nullable running law-plan object (`skeleton` plus ordered `jumps` with name, primitive, level and affine flag). The actual bell modulo requires its producer-compiled jump plan; the viewer cannot reconstruct identical cut and branch order from expression text alone. Placeholder names are minted across both plans in edge order and their expression slots join the ordinary document binding pass.

The new edge is `kind: "follow"`, `needs: [lower_source, upper_source, retained]`, `gives: [retained]`, `lower` and `upper` graph expressions in the same serialized expression format as running laws, plus ordinary `description` and `stated_by`. The matching dynamic Bounds remain in the existing span table. The producer raises a document carrying Follow to version 12 (and the paired viewer capability/API gate accordingly); every document without it remains at its prior version and unchanged fields. The program identity includes both expressions and ordered ends, so snapshot restore cannot silently cross a changed envelope. The viewer companion must validate the same structural Bounds, refuse malformed or unsupported paths, and prove Python/JS numeric and stop/replay parity on the Curta trial before adoption.

## Risks / Trade-offs

- **One-sided chart arithmetic differs by a ULP** → Treat each value as a distinct numeric side; test the actual 6° Curta join and a synthetic closure-only violation. No agreement-window continuity waiver.
- **A narrow inverted interval lies between uniform samples** → Add only certified piece-side candidates; prove a sub-grid transient inversion red/green without reducing existing samples or tolerances.
- **An authored path has an unsupported jump, curve, or source dependency the certificate does not cover** → Refuse explicitly and atomically; do not extend Follow into a general solver by guesswork. The Curta modulo jump is supported by its published jump plan and exact one-sided evaluation.
- **Prefix replay and full propagation disagree at a cut** → Keep absolute landing and exact side convention in both, test long coarse ticks, opposite-direction sources, stop/relief, snapshot/restore, and document replay against the actual Curta graph.
- **A Follow edge with no matching Bound could commit an impossible interval** → Compiler and consumer reject such a program before execution.

## Migration Plan

Add the producer and consumer as separate repository changes. Older documents retain version 11 or lower and their existing executor. A version-11 consumer refuses a Follow document at version 12 rather than interpreting it as a law. No persisted bank or project source migration is needed; the Curta trial may adopt the new explicit law only after Python, browser, and independent geometry gates pass.

## Open Questions

None are intentionally deferred. If red-first implementation shows the Curta boundary graph cannot be certified or a one-sided positive contact cannot be localized with the stated fractions, stop this cycle and revise the design under the pilot's authority rather than broadening the solver or weakening the contract.
