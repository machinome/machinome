## MODIFIED Requirements

### Requirement: Flexible faceted geometry has a bounded multi-binding working set

During a test run the system SHALL reuse a flexible leaf's evaluated base mesh, local bounds, and admitted Manifold for repeated faceted reads of the same geometry-definition/source identity, structural node identity, and binding. Several simultaneously useful bindings MAY coexist, but the working set SHALL have a finite internal entry limit and access-ordered eviction. Rebinding among a working set smaller than the limit SHALL reuse one construction per distinct key; a long sequence of unique bindings SHALL NOT grow retained entries beyond the limit.

The correctness key SHALL use full, non-truncated values: flexible technology; defining project source/module identity and full current source fingerprint/digest; the full canonical structural identity from which `uniq_id` is shortened; exact canonical sorted binding values from which `binding_hash` is shortened; and a full digest of the current serialized flexible shape/spec. Same-named or same-`uniq_id` classes from different source definitions, different values sharing a shortened hash, and different specs SHALL NOT share geometry. A source/spec identity change SHALL cause a miss and current-shape evaluation. An evicted binding MAY be evaluated again and SHALL produce the same geometry as uncached evaluation.

This cache SHALL contain reusable faceted geometry, not intersection verdicts. Verdicts involving a flexible node are memoized by the test framework, within a run and across runs, under the leaf's STATE identity (see the `test-framework` capability). That identity SHALL be taken from the same coherent snapshot this cache keys on. It uses the same full values, except that no absolute filesystem path and no filesystem metadata is part of it: the defining source is identified by its module and by the content of its tracked sources. A comparison involving a flexible node SHALL therefore execute the selected exact or faceted Boolean only when no verdict for that state and relative placement is already known. A flexible leaf whose class overrides the public evaluation seam a comparison reads (`base_mesh` for faceted geometry, `shape` for exact geometry) SHALL have no state identity, and its comparisons SHALL always run their Boolean. The existing `FlexibleNode` per-instance last-binding exact `(shape, tolerance)` memo SHALL remain separate and SHALL keep its behavior. It MAY carry, beside the solid it built, the state identity of the snapshot it built that solid from. This requirement SHALL NOT add cross-instance exact-shape reuse.

#### Scenario: Interleaved useful bindings build once each

- **WHEN** many identical flexible instances at one assembly instant alternate among three source-equal bindings and the working-set limit exceeds three
- **THEN** faceted geometry is constructed three times, later reads reuse the matching mesh/bounds/Manifold, and every returned volume and admission verdict equals uncached evaluation

#### Scenario: Same structural id from another source does not collide

- **WHEN** two flexible definitions have the same structural `uniq_id` and binding but different defining source/module identity
- **THEN** each evaluates and caches its own faceted geometry

#### Scenario: Short-hash collisions do not share geometry

- **WHEN** test-controlled structural or binding hash shortening makes two different full identities produce the same twelve-hex value
- **THEN** their flexible faceted geometry occupies distinct correctness keys and each returns its own mesh, bounds, and Manifold

#### Scenario: A source edit invalidates flexible geometry reuse

- **WHEN** a flexible definition's observable source identity changes while its structural id and binding remain equal
- **THEN** the next faceted read evaluates current geometry and cannot return the prior source generation's cached mesh or Manifold

#### Scenario: A long trajectory stays bounded

- **WHEN** a test reads more unique flexible bindings than the internal limit
- **THEN** retained faceted-geometry entries never exceed that limit, least-recently-used entries are disposed, and revisiting an evicted binding recomputes correct geometry

#### Scenario: Flexible verdicts are keyed on state

- **WHEN** a flexible pair is compared twice at one binding and relative placement, and then once at a different binding
- **THEN** the first comparison runs the selected Boolean, the second is served its verdict without a Boolean, and the third runs the Boolean and reaches its own verdict from the new geometry

#### Scenario: A moved flexible definition keeps its state identity

- **WHEN** a project containing a flexible definition is moved to another directory, with its sources unchanged
- **THEN** the flexible leaf's state identity at a given binding is the same as before the move

#### Scenario: A custom evaluation seam keeps flexible verdicts uncached

- **WHEN** a flexible pair whose leaf class overrides `base_mesh` or `shape` is compared twice at one binding
- **THEN** each comparison runs the selected Boolean

#### Scenario: Exact last-binding behavior is unchanged

- **WHEN** one flexible instance is asked twice for exact shape and tolerance at one binding and then at another
- **THEN** its first binding is evaluated once, the second binding replaces that instance's exact memo, and no other instance receives the exact result
