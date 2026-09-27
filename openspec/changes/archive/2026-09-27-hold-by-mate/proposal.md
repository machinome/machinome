## Why

AlbertPro is a quadruped reconstructed from its MuJoCo file and its print
plate. Its printed chain migrates onto revolute mates read from
`RL/dog.xml`, as SO-ARM100's did from its URDF; its 48 bought parts do
not move of their own -- each servo, horn, screw and nut sits connector
onto connector on the part that holds it, at a seat the project measured
off the print (`evidence/finding.md` §2-3) -- and a mate must state a
freedom (ADR-147: "no freedom at all (the rigid mate) [is] refused naming
this version's scope"). So today the bought parts live in a parallel
tree of hand placements, `sourced.py`, tied to the printed tree by eight
relations and one wrapper class that exists only to order a quarter turn
before a joint angle. A mate with no freedom -- `servo.ears.on(servo_seat)`,
stated in the class of the printed part that holds the servo -- places
the part from the two frames and gives it nothing else.

This is the wart recorded in `workflow/warts.md`, "A bought part cannot
be held by mate: no rigid mate (2026-09-26, AlbertPro)", bullet "A mate
must have a freedom; a part that is simply held has none". The
originating project is `projects/Robots/AlbertPro`; its follow-up
declares every bought part in the printed part that holds it and deletes
the parallel tree (tasks §6). It also answers Thor's recorded question
("whether a fixed end on a moving sibling should follow it, or whether a
part's fasteners belong in its own class"): by the project's shape, not
a rule (`evidence/finding.md` §5).

## What Changes

- **A mate may leave its freedom out: the rigid mate.**
  `servo_bolted = servo.ears.on(servo_seat)` places the moving child at
  rest exactly as any mate does -- `P_owner · F_fixed · F_moving⁻¹`,
  whole triad onto whole triad, one rotation then one translation, the
  `1e-9` snap, after `render()` -- and compiles to nothing else: no
  joint on the child (its class is not specialized; `type(child)` is the
  declared class), no coordinate on the assembly, no wiring, nothing
  published but the operations.
- **What it is not:** a rigid mate is not a coordinate. `declared_ports`
  does not report it; reading it on an instance yields the declaration,
  as reading a frame does; assigning to it, naming it as a relation's
  end, as a wiring source or by path from above is refused, naming the
  mate. `declared_mates` reports it with `freedom` `None`.
- **Rules unchanged:** the frames' rules; the ends' depth; a fixed end
  that does not move -- a rigidly held part rides with the part that
  holds it because it is declared in that part's class; a second mate on
  one child (the rigid one included) refused as a loop; a `render()`
  placing a mated child refused; a freedom that is not a `Revolute` or
  a `Prismatic` refused; every mate named. A fixed end on a child
  another mate places stays refused, the rigid mate included, its
  message no longer saying the child "moves".
- **A held child may carry its own joints, children and mates:** the
  rest placement composes outside them, as every mate's does.
- **Words that change with it:** the `mates` spec; the manual's "Frames
  and mates" (a sixth example, appended, and the refusal paragraph);
  `docs/reference/api.rst`'s sentence on the mate's spelling; the
  changelog's Unreleased; the `mates.py` module, `Mate`, `_check_freedom`,
  `_install` docstrings and three messages; `docs/architecture.md`'s mate
  paragraph; ADR-147 and ADR-151, amended by a new ADR-152 at archive;
  the working note; the wart's disposition.

**Deliberately out**, with the reason:

- a fixed end on a moving sibling (Thor's question), a fixed end on a
  rigidly held sibling and the dependency order it would bring (the
  place-parts-by-mate design's §9 (b)), and a rigid mate on an inherited
  child: AlbertPro needs none of them (`evidence/finding.md` §5);
- an unassigned rigid mate: every mate keeps a name (scope question 2);
- loops, `Orbit` and `Free`, ends deeper than one child, world-placement
  reads (Thor's first finding), the viewer, the studio skill (a separate
  change in `machinome-studio`, recorded as a follow-up);
- AlbertPro's "show me only what I print" view (its D12): not a
  framework matter; the project decides it in its own record (tasks §6).

## Scope questions for the pilot

The artifacts are written to each recommendation.

1. **The spelling.** *Recommendation: the freedom left out,
   `moving.on(fixed)`* -- the default `on()` already has, and the working
   note's §5 spelling ("Rigid is the default ... needs no class") --
   rather than a `Rigid()` freedom class (design decision 1). A class
   would be a fourth joint-like kind that installs no joint, owns no
   coordinate and has no arguments; nothing in AlbertPro's seats needs an
   argument. `None` written explicitly is the same statement (the
   signature's default) and is neither documented nor refused.
2. **Must a rigid mate be named?** *Recommendation: yes, as every mate
   is* (decision 3). `declared_mates` is keyed by name, the refusals name
   the mate, and a bare statement has no name to report. The wart writes
   the statement bare; naming it costs a word. The refusal of a bare
   mate stays, its reason reworded for a mate with no coordinate.
3. **Reading and binding a rigid mate on an instance.**
   *Recommendation: reading yields the declaration, as reading a frame
   on an instance does (the working note: "reading `arm.lid` yields the
   declaration"); assigning raises `AttributeError` naming the mate and
   saying it states no freedom and owns no coordinate* (decision 4). A
   crash on a `None` coordinate is not a message, and a plain "has no
   attribute" would be false: the class has one.
4. **The ADR.** *Recommendation: a new ADR-152 (NODE), "a mate may
   leave its freedom out", amending ADR-147* ("a mate compiles to a rest
   placement, a joint and a coordinate"; "no freedom at all (the rigid
   mate) [is] refused"; the deferral in its Consequences) *and ADR-151*
   ("`Orbit`, `Free` and the rigid mate stay refused"), written after
   implementation confirms the design. A MODIFIED spec block alone would
   leave both ADRs' decision texts contradicting the code.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: a mate may leave its freedom out; such a rigid mate places
  the moving child at rest from the two frames and gives the child no
  joint and the assembly no coordinate; it is not a coordinate anywhere a
  coordinate is named; it is read off the class with `freedom` `None`;
  it publishes only the operations; every other mate rule holds for it.

## Impact

- `machinome/motion/mates.py`: `_check_freedom` accepts no freedom;
  `declare_mates`' bare-mate refusal reworded; `Mate.__init__`,
  `__set_name__`, `__get__`, `__set__` for a mate with no coordinate;
  `_install` installs nothing for it; `_check_child_name` skipped for it;
  the messages of `_check_fixed` and `_check_moving` true for it; the
  refusal of a rigid mate named as a coordinate (at `coordinate_ref` in
  `machinome/motion/couplings.py`, where a frame is already refused, and
  at the wiring check in `machinome/node/declarative.py`); docstrings.
- Tests: `tests/test_mates.py` (the two rigid-refusal tests turned into
  acceptance tests, a new `HeldPartTest` and its twin and document tests,
  the manual example), a new fixture module `tests/mate_project/hold.py`.
- Documentation: `docs/concepts/joints.rst` "Frames and mates",
  `docs/reference/api.rst` "Frames and mates", `docs/project/changelog.rst`
  (Unreleased), `docs/architecture.md`, new ADR-152, ADR-147's and
  ADR-151's headers, `docs/adrs/README.md`,
  `workflow/ongoing/mates-and-sketches.md`, `workflow/warts.md`.
- Studio (separate change in `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the rigid mate.
- Originating project: AlbertPro's migration, later, by a separate
  agent, in its own repository (tasks §6).
