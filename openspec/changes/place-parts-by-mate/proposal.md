## Why

Thor's elbow is one joint stated in three files. `art3.py` declares
`elbow = Revolute(axis=(0, 1, 0), at=(0, 0, 81.5))` under a thirteen-line
docstring that derives the anchor by hand through a 90-degree turn;
`art2.py`'s `render()` places the forearm with `rotate(90, X)` and
`translate(0, 160 + 81.5, 68)`; three module constants (`ELBOW_ALONG_ARM`,
`ELBOW_ACROSS_ARM`, `ELBOW_ACROSS_FOREARM`) are shared between the two
files only so that the numbers agree; and the machine's driver reaches
the freedom through `shoulder.art2.art3.elbow`. The same shape repeats at
the shoulder (Art1 places Art2 with a 180-degree turn about
`(0, .7071, .7071)` and Art2 restates the line), at the forearm yaw and at
the wrist: every link of Thor's root chain is a rest placement in the
parent and a joint in the child that describe one physical pin twice.

Thor's own design does not have this problem. Every FreeCAD Assembly4
link records the connector it is attached by, the parent connector it is
attached to, and an offset; the placement Thor transcribes into
`layout.py` is that solver's output. Spike evidence
(`evidence/spike.md`) re-derives 142 of Thor's 145 transcribed
placements from those connectors under one rule, and a 60-line resolver
reproduces the elbow's and the shoulder's hand-written placements and
the elbow's hand-written joint exactly from two frames each.

This is section 5.1 + 5.2 of the framework's working note
`workflow/ongoing/mates-and-sketches.md`: parts name their connectors,
and an assembly relates two connectors in one sentence that both places
the part and declares its freedom. It is cut now because a named
project, Thor, needs it now, and it is cut to what Thor needs.

## What Changes

- **A frame, a new class-body declaration.** `Frame(at=(0, 0, 0),
  z=(0, 0, 1), x=None)` in `machinome.node.frames` (also resolving from
  `machinome.node`): an origin and a right-handed triad in the
  declarer's own rest frame, declared on any node kind — a leaf, a
  fusion or an assembly — in the mould of a marking (ADR-120). It is not
  identity, not a child, not a port and builds nothing. Components follow
  the joint rule; a frame is resolved per instance at realization.
- **A mate, a new class-body statement on an assembly.**
  `elbow = art3.hinge.on(elbow_pin, Revolute(range=..., unit='deg'))`:
  the moving end is a frame declared by a directly declared child; the
  fixed end is a frame of the declaring assembly itself or of another
  directly declared child that does not move. The freedom is a
  `Revolute` written with no `axis` and no `at`.
- **What a mate compiles to, at realization, and nothing else:** (1) the
  moving child's rest placement, as ordinary rotate and translate
  operations applied after the author's `render()` returns;
  (2) a revolute joint on the moving child whose axis and anchor are the
  moving frame's `z` and `at`, occupying a slot after the child's own
  joints; (3) a rotational coordinate on the assembly under the mate's
  name, which relations, drivers and bindings see as an ordinary
  coordinate and which moves the child's joint.
- **One signature change in `joints`:** `Revolute`'s `axis` becomes
  optional. A `Revolute` without an axis anywhere except as a mate's
  freedom is refused at class definition, naming the mate as the only
  place it is allowed. No existing declaration changes meaning.
- **Refusals**, each naming what it refuses: a frame on a clashing name;
  a frame that does not resolve, whose `z` has no direction, whose `x`
  is parallel to `z`, or whose `z` is not along a principal axis and
  states no `x`; a mate on a non-assembly; a moving end that is not a
  frame declared by a directly declared child; a fixed end reached
  through more than one child, or on a child that moves; a list-held or
  repeated child at either end; a second mate on one child; a
  coordinate-owning mate left unnamed; a freedom other than `Revolute`, a
  freedom stating its own `axis` or `at`, a freedom whose range reads
  another coordinate or is not a plain pair; a mate with no freedom (the
  rigid mate, deferred); a child both mated and placed by `render()`.
- **Untouched:** the published document (the compiled placement is
  already expressible as `operations`, the coordinate as a binding;
  document version stays 13, and a document with no frame or mate is
  byte-identical), the simulation package, the build pipeline, export,
  the viewer and the mechanics package. No existing project changes.

**Deliberately out**, with the reason: loops and a second mate on one
child (§5.3; no named project); publishing frames and mates in the
document for the viewer (§5.5; a later pair of changes); repeated frames
and broadcast mates (Thor has neither); mates in list-held or repeated
children; a moving frame on a grandchild; a fixed frame reached through
more than one child. `Prismatic`, `Free` and the rigid mate are put to
the pilot below rather than built by default.

## Scope questions for the pilot

The workspace's evidence rule builds only what a named project needs
now. Three decisions are the pilot's; each carries a recommendation, and
the planning artifacts are written to the recommendation.

1. **`Prismatic` and `Free` as mate freedoms.** Thor's five root-chain
   attachments are all revolute; no project in the catalogue has been
   read for a sliding or floating mate. *Recommendation: `Revolute`
   only.* `Prismatic` is the same one-coordinate path and would cost one
   refusal's deletion and a test when a project needs it; `Free` owns six
   coordinates and needs its own design for the mate's coordinate. Both
   are refused naming this cycle's scope.
2. **The rigid mate now.** Thor's 142 in-assembly attachments are
   exactly rigid mates, so the Thor migration could exercise one for one
   sub-assembly's internals. But none of them is restated anywhere: each
   is transcribed once from the design by `emit_layout.py` and checked
   entry for entry by `test_layout.py`, so the rigid mate would replace
   a working, single-statement mechanism rather than fix a finding. It
   would also bring back what the revolute-only cycle does not need: a
   mate placing a child another mate's fixed end sits on, and therefore
   a dependency order and a loop refusal among sibling mates.
   *Recommendation: defer.* `on()` with no freedom is refused naming
   the deferral. If the pilot wants it now, the design's §9 lists the
   three additions it brings.
3. **Thor's validation scope.** *Recommendation: the whole five-mate
   root chain* (base → housing → upper arm → forearm root → forearm →
   wrist). The finding is that the shape repeats at every link; migrating
   two of five would leave Thor with two placement styles for one kind
   of connection, and the first link (the housing on the base) is the
   only one whose fixed end is a sibling's frame rather than the
   assembly's own — the one case that exercises a fixed end on a child.
   If the pilot chooses elbow and shoulder only, that case has no
   originating evidence and is struck from the cycle with it.

## Ratified scope (2026-09-26)

Ratified by the orchestrator's adversarial review under the review gate
the pilot delegated on 2026-09-07, with the three scope questions taken
at their recommendations: `Revolute` only; the rigid mate deferred;
Thor's validation over the whole five-mate root chain. The pilot may
widen any of the three; a widening reopens the planning artifacts
before any test is written (tasks 0.3).

## Capabilities

### New Capabilities
- `mates`: named frames on parts; the `on()` statement relating two
  frames in an assembly; what a mate compiles to (rest placement,
  joint, coordinate); its refusals; and that it publishes nothing new.

### Modified Capabilities
- `joints`: `Revolute`'s `axis` becomes optional, and a joint written
  without one is refused everywhere but as a mate's freedom.
- `declarative-nodes`: reading a frame off a child declaration in a
  class body yields a reference to that frame (a place, like a port
  path), where today it would be refused as a sideways read.
- `couplings`: a mate's coordinate is an end of a relation exactly as a
  joint's coordinate is — named bare in the declaring body, by path from
  above — and the joint a mate installs on the child is bound only
  through it.

## Impact

- New modules `machinome/node/frames.py` (`Frame`, `declared_frames`)
  and `machinome/motion/mates.py` (the frame reference, `Mate`,
  `declared_mates`, the resolver).
- `machinome/node/declarative.py`: `NodeMeta.__new__` collects frames
  and mates (through the declaring-namespace channel relations already
  use) and installs each mate's joint on the child declaration;
  `ChildDeclaration.__getattr__` yields a frame reference.
- `machinome/motion/couplings.py`: `read_through` admits a frame;
  `OwnRef.check_declared_on` admits a mate; a mate's wiring is exempt
  from the unbound-source refusal.
- `machinome/motion/joints.py`: `Revolute(axis=None, ...)` and its
  refusal.
- `machinome/node/assembly.py`: `_rest` applies the compiled placements
  after the author's `render()` and refuses a mated child placed by hand.
- `machinome/node/base.py`: frames resolved per instance beside joints.
- New ADR-147 (NODE): a mate compiles at realization to a rest
  placement, a joint and a coordinate. Extends ADR-061, 066, 088, 089,
  093, 097, 098, 114, 120.
- Documentation: the user manual's driving/joints page gains the frame
  and the mate (under `skills/write-the-manual`); the studio's
  `shop-skills/machinome-api/SKILL.md` gains them in the studio
  repository, as a separate change there.
- Originating project: Thor migrates in its own repository afterwards,
  by a separate agent, with a pose comparison at maximum deviation 0.
- The working note `workflow/ongoing/mates-and-sketches.md` is corrected
  in this cycle's second commit (see `evidence/spike.md`, "Corrections to
  the note").
