## ADDED Requirements

### Requirement: Reused large placed profiles avoid exhaustive disjoint-pair scans

Within one integration attempt, an eligible repeated pointwise contact over large finite profiles SHALL be able to prune polygon pairs whose placed AABBs are strictly disjoint without evaluating each pair's AABB individually. The pruning SHALL be conservative: it SHALL preserve complete left-then-right placement validation, the original polygon-order visitation of remaining SAT candidates, every returned positive `0.0` or `1.0` and first refusal, and the existing success-only bounded cache lifetime. It SHALL introduce no epsilon, omitted polygon, or caller-visible eligibility limit. Calls outside the eligible repeated-work path SHALL retain the ordinary evaluator's behavior and error order.

#### Scenario: Curta-sized repeated separated covers
- **WHEN** a 591-polygon profile is repeatedly tested against a successfully placed 159-polygon profile during one running integration attempt and their placed AABBs are strictly separated
- **THEN** contact remains positive `0.0`, and the repeated calls avoid an exhaustive 591-by-159 individual pair-AABB scan

#### Scenario: A late contact retains authored order
- **WHEN** a conservative index leaves several possible polygon pairs and the first contact occurs in a later authored pair
- **THEN** the result is positive `1.0` after visiting surviving candidates in the same left-then-right order as the ordinary predicate

#### Scenario: Earlier invalid placement or projection is never hidden
- **WHEN** a later polygon has invalid finite-placement geometry, or an earlier surviving pair's SAT projection becomes nonfinite before a later contact
- **THEN** the original first refusal occurs before any numerical result, and no failed or partial index is published for reuse

#### Scenario: Direct and uncertain evaluations remain ordinary
- **WHEN** a contact is called without an integration cache or with uncertain/custom placement keys
- **THEN** its conversions, validation, result and refusal order are unchanged, and no persistent spatial index is registered

#### Scenario: Skewed calls cannot force index construction
- **WHEN** a successfully cached right placement has many polygons but the left placement has only one or two polygons
- **THEN** repeated contact retains the ordinary evaluator's result and error order without building a spatial tree merely because the polygon-pair product is large
