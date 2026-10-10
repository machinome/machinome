## Why

The Curta Type I installed-reverser contact trial exposes a large, repeated finite-profile query that is needlessly scanning polygon pairs after the successful-placement cache has already done its work. In the pinned version-13 one-tick reproduction, 1,560 numeric calls perform 45,445,536 pairwise AABB checks, taking 1.52–1.57 CPU seconds of an 8.40–8.64 CPU-second tick in `profile_overlap`; the project's current revised contact covers are separate, unadopted work, so this change claims only the pinned trial.

## What Changes

- Make repeated eligible numeric contacts avoid most disjoint polygon-pair AABB checks using a conservative private spatial index of an already validated placed profile. A conservative internal gate excludes skewed calls with too few left-polygon queries to justify building a tree.
- Keep the public call, result bits, error and SAT visitation order, complete placement validation, bounded per-attempt success-only cache lifetime, and all existing running Bound semantics unchanged. Direct, uncertain-key, and small calls continue through the ordinary evaluator.
- Add red-first order/error, cache-lifetime, memory, and originating-project regression proofs. No new document field, viewer behavior, tolerance, polygon limit, or external dependency is introduced.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `convex-profile-contact`: Repeated eligible pointwise contacts with large authored profiles may prune provably disjoint polygon pairs without altering the finite ordered predicate or its success-only integration cache contract.

## Impact

The change is confined to the framework's private numeric path in `machinome/simulation/profile.py` and its tests, with a delta to the existing convex-profile-contact specification. The originating evidence is `projects/Calculators/Curta-Type-I-3x/_build_checks/reverser-installed-profile-reference-a428dea.jsonl` (SHA-256 `d41e1b46ee7f4c92b61d2ddae586f01242574213942d7dd93f0e9c4aefad01a3`) and the frozen old-trial document `/tmp/curta-installed-profile-v13.json` (SHA-256 `2d62786b64c4f8f113fbd6224a1dca49b12bbfad0e37c8130c2b0840d208eb34`). The 214-key one-tick oracle is `/tmp/curta-installed-profile-one-tick-bank.json` (SHA-256 `1872b5a9ca242df97d5f86f0050f7e1b94144b9f55c019a3db58ed1a7c50cc2e`). These `/tmp` probes are local evidence, not a promised repository fixture; implementation tests must contain their own durable small cases.

The measured candidate retains 130 trees in the 136-placement crank cache: +1,614,277 deep bytes including tuple-subclass attribute dictionaries, and +1,661,069 bytes paired `tracemalloc` peak (235,962,453 versus 234,301,384). This bounded per-attempt memory cost buys the measured CPU reduction; it is not a universal byte cap.
