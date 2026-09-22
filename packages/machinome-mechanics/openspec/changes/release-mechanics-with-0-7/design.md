## Context

The package exports 24 helpers in nine families, validated one cycle at a
time against real projects during the 2026-09-20 helper campaign. That
campaign wrote the consumers' names into the reference pages as evidence.
The framework manual was rebuilt for 0.7 with a new page layout
(`start/`, `concepts/`, `howto/`, `reference/`, `project/`); the mechanics
manual still links `driving.html`, `quickstart.html`, `declaring.html` and
`testing.html`, none of which exist there now. The viewer went through the
same release pass one day earlier and set the shape: a release stated on
the home, installation and compatibility surfaces, index installation
first, no development records or project credits in reader-facing pages,
a test that keeps it so.

## Goals / Non-Goals

**Goals:**

- A developer installing the 0.7 release set finds a manual that matches
  what they installed and every link they follow lands on a page.
- The reference reads as a formula reference: frame, zero, sign, domain,
  example, and the kind of machine a convention serves.
- The release narrative is single-sourced enough that a later release edits
  the changelog head, the release record and one test expectation.

**Non-Goals:**

- Renumbering the package. The framework manual names 0.1.0 and the pilot
  did not ask; the version identifies the distribution and 0.1.0 with
  Machinome 0.7.0 is an honest first release.
- Changing any helper, signature or formula. Doctests that assert values
  stay as they are.
- Uploading, tagging or pushing anything.

## Decisions

- **Machines by kind, not by name.** "A hexapod leg supplies its horizontal
  span" carries the same guidance as "Spiderbot supplies its horizontal
  span" and needs no repository the reader cannot see. Two of the named
  projects were withdrawn from the Foundry for licence reasons, so naming
  them as consumers of an Apache package would also be wrong. Alternative
  considered: linking each name to its Foundry repository. Rejected: the
  Foundry set is still being reviewed and the manual would carry links
  that rot.
- **Public spellings in examples.** The "Symbolic inputs" section and the
  indexed-advance page built a symbolic value with `solid2.get_animation_time`
  and checked its type against `OpenSCADConstant`. Neither is a Machinome
  API; the framework's spelling for the timeline value is `self.time` in
  `simulate()`. Those passages become short code blocks in the framework's
  spelling and the deferred face is proved by the package's own tests,
  which the reader is told about. Alternative: keep the doctests. Rejected:
  a manual that teaches a third library's internals to prove a claim the
  test suite already proves.
- **Index install first, source second.** As in the viewer manual, with the
  `machinome[mechanics]` and `machinome[viewer,mechanics]` forms both
  shown, and the two-checkout editable install kept under a "Build from
  source" heading for contributors.
- **Link targets.** `driving.html` becomes `concepts/relations.html` (laws
  and `law=`), `quickstart.html` becomes `start/install.html`,
  `declaring.html` becomes `concepts/values.html` (parameters, formulas,
  the `.value` escape), `testing.html` becomes `reference/assertions.html`,
  and the migration note points at `project/upgrading.html`. The test
  carries the allowed set so a renamed framework page fails here first.
- **Changelog shape.** One release section headed by the date and the
  framework release, grouped by what a project gets, followed by identity
  and provenance. The per-helper "Add X" bullets from the campaign fold
  into the family list; there is nothing worth archiving separately.
- **The release record stays `release-0.1.md`** and states the published
  set (framework 0.7.0, viewer 0.7.0, mechanics 0.1.0) and the pilot's
  remaining steps: upload after the framework, then a fresh-environment
  install of the set.

## Risks / Trade-offs

- [The framework's manual layout changes again] → the documentation test
  names every allowed target; a rename fails the mechanics suite instead
  of shipping a dead link.
- [Removing project names loses evidence] → the evidence stays in the
  archived per-helper changes and `workflow/helper-expansion.md`, which
  the reference never was the home of.
- [Fewer doctests] → the two removed doctests proved a type, not a value;
  `tests/test_motion.py` and the per-helper suites cover the deferred face.
