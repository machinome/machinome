## 1. Lock correctness before optimization

- [x] 1.1 Add red-first tests in `tests/test_convex_profile_contact.py` and `tests/test_profile_integration_cache.py` for eligible repeated large separated profiles, skewed 1-by-N/2-by-N bypass, late-pair contact and strict clearance, first-error order (later collapsed edge and earlier nonfinite SAT projection), signed zero/extreme finite operands, uncertain-key bypass, cache eviction, attempt exit, and no cached-index mutation when a later SAT error occurs.
- [x] 1.2 Record the red failure and baseline exact outputs, cache-entry counts, CPU and memory on the frozen Curta version-13 one-tick probe; keep temporary/project evidence outside the framework repository.

## 2. Implement private bounded index

- [x] 2.1 Add a comparison-only conservative 2D AABB tree for validated right-placement polygon boxes, storing any successful tree only with that placement in the existing per-attempt cache.
- [x] 2.2 Gate tree use to a cached right placement with at least 32 left and 16 right polygons and at least 512 possible pairs; query with strict separation, restore authored right-polygon order before the unchanged pair AABB/SAT path, and leave direct, uncertain-key, first-use, small and skewed calls ordinary.
- [x] 2.3 Stage each newly built tree locally and publish it only after the entire predicate succeeds; prove failed placement, tree preparation or SAT leaves no partial index on a previously cached value.

## 3. Validate originating need and scope

- [x] 3.1 Run focused profile, running-bound and cache suites plus the relevant full framework tests; require exact existing result/error behavior and document/serialization parity.
- [x] 3.2 Repeat paired pinned CPU10 Curta old-document one-tick measurements against base `8d0fd156787f5136174fb752be78451ce172bce8`; compare ordered contact digest, all 214 bank bits, tick and predicate CPU, direct/cold and 1-by-N/2-by-N crossovers, bounded cache entries, retained and peak index memory. Return to review if the private gate lacks material benefit; do not claim this proves the current unadopted revised covers.
- [x] 3.3 Record the measured outcome, risks and any accepted architectural consequence in framework-owned completion records; do not modify viewer code without a separate measured viewer cycle.
