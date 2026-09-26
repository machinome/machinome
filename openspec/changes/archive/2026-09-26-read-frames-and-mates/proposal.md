## Why

Thor guards the frames it transcribed from its design with
`projects/Robotic-Arms/Thor/simulation/test_frames.py`, and to read what
its modules declare it had to restate the framework: it re-derives each
frame's resolved triad from the raw declaration `declared_frames(cls)`
yields — normalizing `z`, re-implementing the default-`x` rule through
its emitter's `default_x`, building `y` — because the resolved triad
lives only in the instance's private `_frame_arguments`; and it reads a
mate's ends through `Mate.described()` and its freedom through
`Mate.freedom.axis`, `.at`, `.anchor_written` and `.range`, none of them
documented, `at` misleading on its own (`evidence/finding.md` §2). A
project that must re-implement a framework rule to test its own
declarations is the shape the sixth `place-parts-by-mate` wart records
("No documented way to read a declared frame's numbers, or a mate's ends
and freedom, off the class", **Deferred**: "a project has now needed
one"). `place-parts-by-mate` chose no instance-level read because nothing
read a frame on an instance then (design decision 1, ADR-147's rejected
alternatives); Thor now does.

## What Changes

- **A resolved-frame read on an instance.** One new public function,
  `resolved_frames(node)` in `machinome.node.frames`: every frame the
  realized node's class declares, by name, in declaration order, as the
  `ResolvedFrame` the constructor already cached — the very objects a
  mate composes with, not re-resolved, so a callable argument is not
  called again. A node declaring no frame reads an empty mapping. A
  class, a class-body child declaration or anything else that is not a
  realized node is refused, naming what was passed and why (a frame may
  read the instance's parameters or call a function of it, so only an
  instance has numbers), as is a read made before the node's frames are
  resolved (from its `check()` or a joint argument's callable), which
  would otherwise be silently partial.
- **`ResolvedFrame` documented:** `at`, `x`, `y`, `z` as tuples of three
  plain numbers — `at` floats, the directions unit length with components
  within `1e-9` of `0`, `1` or `-1` exactly those integers — and
  `rotation()`, the 3×3 as rows whose columns are `x`, `y`, `z`. To be
  read, not assigned.
- **A mate's ends and freedom documented**, read off the class through the
  already documented `declared_mates(cls)`: `Mate.name`; `Mate.moving`, a
  frame reference whose `written` is `'<child>.<frame>'`; `Mate.fixed`,
  either such a reference or, for the assembly's own frame, that `Frame`
  itself, whose `name` is its attribute (the two ends as the class body
  wrote them); `Mate.freedom`, the `Revolute` written in the statement,
  with `axis` (`None`, or the three numbers as written), `at` together
  with `anchor_written` (`at` is the mate's anchor only when
  `anchor_written` is true; left out, the anchor is the moving frame's
  origin), `range` as written and `unit`.
- **Documentation only for everything that exists**: `Frame.name` and
  `FrameRef.written` gain docstrings; the manual's "Frames and mates"
  section gains the read with a runnable example; `docs/reference/api.rst`
  gains `resolved_frames`, `ResolvedFrame` and `Mate`; the
  changelog's Unreleased gains one bullet; `docs/architecture.md`'s frame
  paragraph gains one clause.
- **No behaviour changes.** Nothing a node, a mate, a document or an
  artifact does moves; every existing test stays green unedited. Reading
  a frame as an attribute of an instance still yields the declaration.

**Deliberately out**, with the reason: a per-name convenience
(`resolved_frame(node, 'hinge')` — `resolved_frames(node)['hinge']` reads
as well); documenting `Mate.described()` (a diagnostic string that elides
the freedom and feeds refusal messages; the attributes are the facts —
design decision 4); a documented read of the installed joint's resolved
line (`Joint.arguments`, which would widen the joints contract for a
choice Thor makes in one line over reads this change documents — design
decision 6); making `ResolvedFrame` immutable, a frame a descriptor, or
`at` read `None` when left out (behaviour changes nobody needs); a uniform
`written` on `Frame` (Thor distinguishes the two end kinds already);
`RESOLVED_KEY`, `_frame_arguments`, `Mate.joint`, `FrameRef.frame` /
`root` / `segments`, `Mate.owner` (stay undocumented).

## Scope questions for the pilot

The artifacts are written to each recommendation.

1. **`described()`: document it or not.** It exists and Thor reads it.
   *Recommendation: do not document it*; the ends are documented as
   attributes, `described()` stays as it is (no rename, no removal) and
   Thor stops reading it. Its form, `'<moving>.on(<fixed>, ...)'`, elides
   the freedom, so it is not a spelling of the mate, and it is the string
   every mate refusal is phrased with; pinning it would freeze those
   messages.
2. **A class, or a read before resolution: refuse or return empty.**
   *Recommendation: refuse, by name.* An empty mapping from a class would
   let a guard pass vacuously — exactly the guard this change serves. A
   node whose class declares no frame, realized, reads empty.
3. **ADR.** *Recommendation: none.* The change adds one read of state the
   constructor already computes and documents attributes that already
   exist; it takes no architectural decision and reverses none. ADR-147's
   decision that a frame is not a descriptor stands (reading one on an
   instance still yields the declaration); only its reason for the
   instance read's absence ("nothing reads a frame on an instance in
   this version") is overtaken, which this change's record and the
   wart's disposition say. No spec rule is added beyond the read itself.

## Ratified scope (2026-09-26)

Ratified by the orchestrator's adversarial review under the review gate
the pilot delegated on 7 September 2026, on the pilot's instruction of
26 September 2026 to work the `place-parts-by-mate` findings with Thor as
the validator, at each recommendation: `described()` stays undocumented
and unchanged, and Thor reads the attributes; a class, a declaration or
a read before resolution is refused by name; no ADR. The review's one
note for the implementer: task 2.3 may pin the identity of the read's
objects with the cache through `frames.RESOLVED_KEY` in a test, and the
public read must not depend on anything the test reads privately.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: two ADDED requirements — a realized node reads its resolved
  frames through `resolved_frames`, refused on a class, a declaration or
  before resolution; a mate's name, ends and freedom are documented reads
  off the class. No existing requirement's text changes.

## Impact

- `machinome/node/frames.py`: `resolved_frames(node)` added to `__all__`
  (a fresh `dict` over the cached mapping, with the three refusals, one
  local import); docstrings of the module, `ResolvedFrame` (attributes,
  types, read-only) and `Frame.name`. No other code changes.
- `machinome/motion/mates.py`: docstrings of `FrameRef` (`written`),
  `Mate` (`name`, `moving`, `fixed`, `freedom` and what each reads) and
  the module. No code changes.
- `machinome/motion/joints.py`: the `Revolute.anchor_written` docstring
  says what `at` means when it is false. No code changes.
- Tests: new classes in `tests/test_frames.py` and `tests/test_mates.py`
  (read, refusals, the triad a mate composes with, mate reads, the manual
  example and the reference entries); nothing existing edited.
- Documentation: `docs/concepts/joints.rst` "Frames and mates" (a third
  example, after the two existing ones), `docs/reference/api.rst`,
  `docs/project/changelog.rst` (Unreleased), `docs/architecture.md`
  (one clause); `workflow/warts.md`, the sixth `place-parts-by-mate`
  bullet's disposition (second commit).
- No document, serializer, export, viewer, mechanics or simulation change;
  no ADR.
- Studio (separate change in `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the read.
- Originating project: Thor's guard rewritten on the documented reads,
  later, by a separate agent, in Thor's own repository (tasks §7).
