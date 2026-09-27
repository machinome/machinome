## Context

Curta's running crank has a pawl-dependent range plus independent lift, ancestor-installed locking obstacles, and explicit turn/lift controls. A simple running mate already compiles through an assembly port wired to one generated child joint; the missing forms are mechanical contracts naming that mate. The existing contracts are in mates, joints and simulation specs, architecture Kinematics/Motion/Simulation, and ADRs 113, 117, 134, 147, 148, 150, 151 and 152. ADR-147 deliberately keeps Mate a Coordinate rather than a Joint; ADR-150 calls whole argument functions with the declaring assembly while preserving the child's geometric frame. Those distinctions remain.

The parent reported a probe showing a simple running mate succeeds while freedom Bound reads and coordinate=mate fail. Its temporary probe file is no longer present, so implementation must recreate durable red-first fixtures rather than cite an unavailable file as reproducible evidence. Curta source at fb5505d is read-only originating evidence; no completed Curta mate migration is claimed.

## Goals / Non-Goals

Goals: carry the existing Bound, additive range constraint and explicit control contracts through a moving mate using the existing generated child joint. Preserve the public mate binding surface and identity wiring, coordinate banking, solver semantics and export schema.

Non-goals: compound mate freedoms, broader frame-end reach, moving fixed ends, new range syntax, implicit control inference changes, coordinate aliases in the bank, a new viewer format, unrelated documentation cleanup, and modifying the originating project in this cycle.

## Decisions

### 1. Normalize mechanical endpoints without changing ordinary mate binding

Provide a shared internal resolution for the mechanical-contract contexts (Bound reads, constraint targets and explicit controls): a bare moving mate resolves through its declaring assembly to its moving child and generated joint; a path to a mate first resolves the declaring assembly then follows that same mapping. Preserve ordinary relation ends, derived coordinates, public assignment and the existing mate wiring. Do not globally rewrite every coordinate_ref result or change Mate to subclass Joint: either would change ownership, enumeration or binding paths that already work. The generated joint is the run's existing bank entry; the assembly port remains a wired source, not another retained value.

Canonical physical endpoint comparison must happen wherever both written and effective references are known. Self reads, including a read of the generated joint while targeting its mate, and duplicate mate/child-joint alias reads are refused. Path shape checks remain at declaration time; effective tree rechecks remain at realization/compile. Keep ordinary references on their current path and avoid broad solver changes. Control resolution returns the actual posing child and generated joint, then reuses the existing ancestry, domain, banking and operation_span code.

### 2. Separate Bound read scope from geometric argument frame

Accept Bound range sides in mate validation and preserve their expressions until ordinary evaluation. Check statically written reads on the declaring assembly after mate installation, not on the specialized child class. The generated joint retains explicit provenance to the declaring mate/assembly for its Bound read resolver. Its axis and anchor still resolve in the child's own rest frame; do not reuse a site-joint flag if that would carry the axis through the rest placement.

The parent link and complete child tree must exist when read values are resolved; reading a later sibling during construction is forbidden. Existing whole-range functions still run once before child construction with the assembly; returned Bounds must get the same declarer scope, self/duplicate and path checks when that returned pair exists. The joint's per-instance resolved span may differ from its class declaration, so validate returned Bounds and use the resolved span for evaluation rather than only declared_bounds(). Cache resolved reads per instance, never in shared mate or joint declarations.

Inherited declarations are checked against the effective class/tree and may retain only supported compatible replacements; no general weakening of current mate inheritance restrictions. Missing or incompatible paths fail, and two instances cannot share a resolved read.

### 3. Extend additive targets to own moving mates deliberately

Current constrain() is on CoordinateRef/PathRef and constraints require scalar descendant Joint targets. Add the existing verb to a moving Mate so turn.constrain(range=...) in its declaring assembly records a target reference; ancestor paths to mates use the same recording operation. Canonicalize to the generated child joint for installation, while keeping the constraint's own declaring ancestor as read/parameter scope. Retain intersection, written order, additive inheritance, nonempty numeric intersection, and original range. A bare ordinary own Joint remains outside the existing descendant-only target contract; this exception serves a mate whose physical joint is on its child. Rigid mates receive a named no-coordinate refusal before access to an absent joint.

### 4. Keep existing execution and publication

Reuse untimed enumeration and running/clocked span compilation. A Bound's implicit own argument is the generated physical joint; reads and added contributions use canonical ids. Explicit controls publish that same joint's existing coordinate, axis, anchor and operation_span. There is no extra edge, bank slot, field or document version attributable to these contract references. Changed effective bounds may change existing program identity as they do for ordinary joints; selection itself cannot change it. Pin untouched non-mate and old simple-mate documents against baseline bytes.

### 5. Evidence and records follow ownership

First reproduce each refused declaration with focused durable tests and Curta-shaped twins. Cover moving read stops and relief, additive ancestor stops, explicit controls on a body with existing lift, nested mate paths, inherited declarations, distinct instances, returned Bounds and late sibling reads. Compare bank cardinality, read ids and control ids with the actual generated joint; compare admitted travel/pose/replay with an ordinary-joint twin. Exercise supported clocked and untimed cases with their existing limitations. Root's baseline Curta tests provide regression evidence; a compact Curta-shaped fixture provides new acceptance without pretending the entire project was migrated.

After implementation proves this design, extract the consequential endpoint/scope decision as an ADR amending the pertinent ADR-147/150 restrictions and extending ADR-113/117/134. Update architecture and only the affected manual sections after reading write-the-manual. Studio API instructions are a separately owned root-agent follow-through, not a framework file edit. Root must perform adversarial review before supported spec sync/archive.

## Risks / Trade-offs

- Mate and child-joint references have different written keys → compare canonical endpoint identity and test both alias orders for self/duplicate refusal.
- Parent scope is unavailable during specialized child construction → defer coordinate value resolution; validate static scope only once the assembly class and mate mapping exist.
- Whole-range functions hide Bound declarations until realization → validate their resolved returned spans per instance without recalling the factory.
- Changing global coordinate resolution could affect relations, identities or legacy documents → limit normalization to mechanical contracts and compare untouched documents and existing mate wiring.
- Clocked expression support is narrower than running support → preserve supported-level refusals and use existing supported clocked fixtures.
- Full Curta costs substantial memory → run baseline regressions sequentially and report environmental failures separately from feature acceptance.

## Migration Plan

This is additive. Existing callers need no migration. A project may later replace a hand placement/site joint with its frame and mate, using the mate name for mechanical contracts; project migration is separately owned. Rollback is removal of this isolated change before integration; no persisted schema or published artifact is migrated here. Framework integration, pushing and publication remain the pilot's decisions.

## Open Questions

No new interface choice is required by the ratified scope. If implementation cannot preserve the single physical bank coordinate, existing binding surface or geometric frame while resolving these contracts, return that concrete contradiction to the pilot before expanding scope. Do not introduce a compound freedom or viewer change to complete this proposal.
