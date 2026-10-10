## Context

Curta-Type-I-3x at project main `4aa04b51bf013aab01c43cec4ef4482e7f805c39` has eleven result dials and six counter dials. `simulation/registers.py` declares their turn joints at the child sites; `RetainedResultDials/RetainedTurnsDials.simulate` in `running_parts.py` initializes only an unbound dial.turn; `wheel_ends` and self-targeted `dial_motion` laws in `running.py` read and drive the same retained endpoints. The project record `simulation/docs/mates-refactor-2026-09-27.md` records the new finding separately from its completed crank adoption. The parent's two-dial probe reports rejection of a PathRef passed as the freedom. Implementation must create durable red fixtures for that failure and the caller invariants.

The ratified declaration is `ones_mount = ones.axle.on(ones_seat, ones.turn)`, with both frames defined; the full geometry-free executable class example is in the mates delta. The pilot rejected a joint_name string. Framework base is clean main `163afcc868155eba94dac16ab10345662d3ce5bc`, after the independently completed mechanical-contract cycle. ADR-147 creates a new joint and wired assembly port for a fresh freedom; ADR-153 follows that port to its generated physical joint only in mechanical contracts. Neither mechanism can be imposed on an existing dial joint without taking over its bindings or moving its Bound scope. ADR-088/098/105/121 and the ports, joints, couplings and simulation contracts establish the original slot, site frame, sole binder and retained-law meanings to preserve.

## Goals / Non-Goals

Goals: place two frames through an explicit existing scalar child-joint reference, preserve the original endpoint and all of its author/runtime semantics, and let the attachment handle name that same endpoint without new state. Cover class and site Revolute/Prismatic joints and the seventeen-dial caller shape.

Non-goals: joint-name strings, arbitrary joint kinds, implicit node-as-freedom selection, compound freedoms, expanded frame-end depth, sibling-following/loops, generalized coordinate aliases unrelated to this attachment, new viewer/schema fields, changes to fresh-freedom/rigid semantics, or project/Studio edits in this framework cycle.

## Decisions

### 1. An explicit reference selects a joint already belonging to the moving child

Recognize the written child-joint PathRef as a third attachment mode alongside fresh freedom and no freedom. Require the exact same ChildDeclaration as the moving FrameRef, no broadcast/list, exactly one terminal segment naming a scalar Revolute or Prismatic on that child, and identity/ownership checks before any effective inherited rewalk. A shared child class does not make another site's joint reference acceptable. A bare Dial.turn is not a place in this assembly and remains refused. Preserve the child declaration's existing specialized class for a site joint; do not specialize again, copy/redeclare the joint, or assign installed_by, mated_by or another shared provenance marker to it. If an inherited attachment's original child is replaced outside the currently supported restrictions, retain the existing named refusal rather than broaden inheritance.

The existing joint may share the mate handle's name if ordinary assembly name rules permit it: the fresh installation name-clash check has no purpose here, since nothing is installed under the mate name on the child. Frame placement remains the current whole-triad composition and rest-operation mark. A class joint stays child-local; a site joint remains parent-scoped and carried through the child rest placement by ADR-098. Frame axes/anchors cannot replace its arguments. Binding at zero preserves the original rest pose; frame attachment can change rest placement compared with a prior hand placement only as the project explicitly selects its frames.

Alternative rejected: reuse the fresh freedom installation and give its generated joint the old name. That still replaces scope, order or binding ownership and does not mean using the referenced declaration. Strings were explicitly rejected by the pilot. A rigid attachment plus a separate joint keeps the endpoint but does not expose the ratified existing-joint handle.

### 2. The reused-joint mate is a handle, not a second port

Preserve Mate's class-level named attachment and its moving/fixed/freedom reads; freedom is the exact written reference for this mode. Store attachment/reference metadata only on the mate. No assembly coordinate is owned, no identity wiring is added and no second _port_values slot is created. The existing child joint and its port alone remain in declared_joints/declared_ports of the child; declared_ports of the assembly omits this handle. Domain/unit lookup for a reference follows the original joint without mutating its coordinate name/owner. Do not present an empty coordinates mapping as meaning rigid: the new mode has a referenced coordinate while a rigid mate has none.

At runtime descriptor reads return the original joint's BoundPort on this realized child, and assignments dispatch through the original joint binding/placement path. A write through the handle has the same permissions and failures as child.turn: it is neither a privileged bypass nor a new writer. Preserve guarded default reads, original author wiring, binding phases and run ownership. The handle never gets fresh mate-exclusive wiring. This reconciles the ratified handle with Curta's existing child.turn consumers and avoids an unbound assembly port erasing a previously initialized dial.

The established get_coordinate/set_coordinate APIs operate on owned coordinate names and canonical child paths; do not add the assembly handle to ownership enumeration merely to make it another published address. Runtime attribute read/write and declaration references are the ratified handle surface. Any broader public name-address API change requires evidence and a separate decision.

Alternative rejected: an assembly port wired to the existing joint. It adds an extra value and binder, rejects existing dial defaults or silently overwrites them, and can alter the retained graph. An alias port enumerated at both owners would publish/bank one physical slot at two addresses.

### 3. Canonical endpoint identity applies in every context for this mode only

Resolve a reused-joint mate reference, bare or reached from an ancestor, through its original child-joint reference to the same ResolvedEnd as the child spelling. A fresh mate reference remains its assembly port for ordinary relation/binding/derived/wiring contexts and follows ADR-153 only in mechanical contracts. Rigid mates retain their no-coordinate refusal. Use one mode-aware endpoint mapping, retaining written references for diagnostics and ownership validation.

Canonicalize before relation duplicate/shared-coordinate checks and derived term identity where necessary, not only at final compilation. Handle and explicit child path (and existing supported single-joint inferred-node spelling) identify one physical coordinate. Two distinct relations that write it still conflict; duplicated aliases in one grouped side still fail; equivalent derived linear terms use normal existing arithmetic over one value. A law using the coordinate on both sides preserves ADR-121's supported retained self-read interpretation even when its spellings differ. A Bound remains different: its implicit own argument forbids that coordinate as an additional read. Check foreign ownership before alias expansion so matching names cannot redirect another assembly's declaration here.

Downward author wiring sourced from a reused handle follows the child slot under the same ordinary unbound/order rules; this adds no writer to the referenced child. Existing wiring into that child remains untouched and remains its sole binder. Binding/placement and freshness clearing operate on the actual child slot, so the handle needs no independent clear/restore pass. Canonicalization is scoped to this new handle mode; unrelated references and old fresh mates keep their paths and errors.

Alternative rejected: a new relay relation between handle and joint. It obscures same-coordinate self-read semantics, adds a causal edge and a writer, and can create a cycle from existing self-targeting dial laws.

### 4. Mechanical scope, compilation and publication follow the original endpoint

Generalize ADR-153's physical resolution to select the reused joint's original name, not the mate's name. Preserve the original joint's argument factory receiver and timing and class/site Bound declarer; the mate is not installed_by for it. Additional constraints through the handle retain the contributor's own ancestor scope and ordinary intersection with the original range. Explicit controls use the original posing node, kind, bank id, axis/anchor and placement block, with ancestry, domain and input-reachability checks unchanged.

The run banks each original child joint once. Retained value, guarded initialization, laws, clocked reachability, untimed fixpoint, stops and replay continue through the existing machinery. Publish frame placement as ordinary rest operations and the original joint binding/id only. The handle has no wire representation; no version/field/viewer change. A equivalent hand-placed witness need not have identical rest operation encoding, but composed poses and original coordinate ids/history must agree. Old-mode fixtures must retain pinned document bytes.

### 5. Proof and follow-through stay repository-owned

Red fixtures first: the complete class example and a two-site-dial fixture currently reject PathRef freedom. Witnesses must include nontrivial frame rotation/translation and noncommuting additional joint placement to expose frame/order drift, child-local Bounds with same-named parent traps, parent/site Bounds and argument factories, guarded defaults and pre-existing wiring. Reuse the joint declaration in other attachment sites and an unattached instance to detect shared metadata leakage.

A seventeen-dial representative caller reads child.turn, retains its defaults, integrates self-targeted clearing, pauses/resumes and restores a snapshot with unchanged original ids. Mixed child/handle sources and targets exercise canonical self reads and duplicate writers; derived expressions and wiring source tests exercise the ordinary reference path. Root may separately migrate and test Curta in its project repository, using the already committed crank-adoption state as the baseline. No Curta source edits or whole-machine acceptance claim belong to this proposal.

After implementation proves the design, extract the focused ADR amending ADR-147's fresh-only interface and extending ADR-153 resolution for existing endpoints, update architecture and affected manual examples after reading write-the-manual, and hand the public contract to root for separately owned Studio API documentation. A separate Sol implements; root adversarial review precedes supported sync/archive and completion commit.

## Risks / Trade-offs

- Handle metadata may be mistaken for port ownership or rigid absence → explicitly separate modes and pin assembly/child enumeration, descriptor identity and serialized bindings.
- Existing mechanical resolver assumes the generated joint has the mate name → use the written existing-joint endpoint and test distinct names and site scopes.
- Alias spellings may hide a writer or retained self read → canonicalize before duplicate/shared checks and prove mixed spelling in both directions.
- A site joint depends on the attachment's rest transform → test its unchanged parent frame/carry through nontrivial rotation/translation against an ordinary site-joint witness.
- Shared declaration mutation can leak across sites → forbid marker/name/scope mutation and test multiple attached and unattached instances with factory call counts.
- Wiring source order remains the author's existing responsibility → retain unbound/order refusals rather than invent a scheduling mechanism.

## Migration Plan

This is additive and needs no existing-caller migration. Projects may replace their hand rest placements with explicit frames and references while keeping child joint paths. Frame agreement and project acceptance remain project-owned. Rollback before integration discards the isolated framework cycle; no schema, persistent state or public release is migrated here. Integration/push/publication remain separately authorized decisions.

## Open Questions

The parent confirmed that the ratified form is a reference handle with no assembly port/wiring and canonical physical endpoint identity in all contexts for this mode. No unresolved author-semantic choice remains. If implementation needs to replace a joint, change its original scope, introduce another port/edge, take over its existing wiring or permit duplicate writers, stop and return the contradiction before broadening the design.
