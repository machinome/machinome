## Context

`README.rst` was 297 lines and 1752 words. Forty-eight lines described
the framework; then came "Version 0.8: a lean core" (with the install
line inside it), "Version 0.7 and the new name", "Learn it one machine at
a time", two licence paragraphs, and a hundred and seventy-five lines for
contributors: development environment, running tests, where things live,
the OpenSpec discipline and the ADR log. Each release and rename cycle had
added its section (the `release-0-8-0` tasks say "a 0.8 paragraph beside
the 0.7 lineage paragraph"), so the page read as the history of its own
amendments.

The manual already owns every release fact: `project/changelog.rst`,
`releases/release-0.7.rst` and `release-0.8.rst`, `project/status.rst`,
`project/upgrading.rst` and `HISTORY.rst`. The contributor briefing
(`docs/contributor-briefing.md`) owns the layout of the package and the
choice of evidence. `CONTRIBUTING.rst` was cookiecutter boilerplate that
said so of itself.

Every chapter of the tutorial, four to nine, places the drums in
`render()` with `translate` and restates each drum's axis in its class,
the shape frames and mates were made to remove; the chapter modules are
pinned by name (`c01` to `c09`), so no chapter could supply a mated
example.

Constraints the README was already under: it states the framework's
licence in `docs/conf.py`'s words and spells no other identifier but the
viewer's (`LicenceFactTest`); it spells no former kernel name or address
(`KernelExtrasTest`); it imports every node name from its module
(`tests/test_node_root_exports_nothing.py`); its installation section makes
the viewer's licence visible before the extra (user-documentation spec).
All of these hold after the rewrite.

## Goals / Non-Goals

**Goals:**

- A README that reads as the description of a thing: what it is, what its
  source looks like, what it does, how to get it, where to read more.
- One example, real and tested, showing parts placed by frames and mates.
- The contributor material kept, where contributors look for it.
- Pins that make the next addition a visible trade and refuse the
  accretion pattern, and the rule for a change stated where every agent
  working on the framework reads it.

**Non-Goals:**

- No manual page, release fact, version, changelog entry or briefing
  content changes. A project gets nothing new from this change, so the
  changelog gains no bullet.
- No words about the rename: the 0.7 changelog, release note and the
  upgrading page own that, as the specs say.
- Moving the tutorial onto mates: chapters four to nine, their pages,
  their committed exports and their companion tests would all change; a
  manual cycle of its own, for the pilot to call.
- Pinning prose quality mechanically beyond the structural pins: a rule
  against a word or a typographic mark would pin a symptom, not the
  defect.

## Decisions

**D1. The README's shape.** Title, tagline and the three badges; what
Machinome is (three paragraphs, in the manual's own framing); *A
machine's source* (the example of D2 and one paragraph naming what it
declares, one paragraph of pointers); *What the framework does* (builds,
tests, simulation, viewer, exports, in prose); *Install* (the one install
line, the extras named for their modules, the two packages and their two
licences, what works without the viewer, the platform); *Documentation*
(manual, tutorial, how-to guides, concepts, reference, changelog,
upgrading, machinome.org, the source); *Licence*; *Contributing* (the
guide, the briefing, `AI-USE.md`, issues). Keeping the version sections in
fewer words was rejected: it is the defect in smaller type. A reader who
wants to know what changed has the changelog one link away.

**D2. The example is a module of the tutorial project written for the
README,** `docs/tutorial/counter/readme.py`, declared as the model
`readme` in `docs/tutorial/pyproject.toml` beside `first`, the start
page's module, so `tests/test_tutorial_counter.py` builds it on every run.
It is self-contained: `Base`, `Crank` and `Drum`, each with the chapter's
geometry and its connector as a `Frame`, no joint; `Counter` with the
shared dimensions, the two seat frames, the driver, the four parts, three
mates with fresh `Revolute()` freedoms (the moving frame's `z` is the
axis, its origin the anchor), the relations on the mates' coordinates
(`crank.drives(turn)`, `turn.drives(units, ratio=0.1)`,
`units.drives(tens, ratio=0.1)`) and `check()`. The crank's fixed end is
`base.axle`, a frame of a child that does not move; the drums' fixed ends
are the assembly's seats, because the arbor they run on turns and a moving
child may not carry another. Built beside the chapter's `RatioCounter`,
the two viewer documents agree operation for operation and name the same
three meshes. Alternatives rejected: the chapter's `RatioCounter` (placed
by `translate`); rewriting the chapter (a non-goal); subclassing the
chapter's parts to add frames (their `turn` joints would sit idle beside
the mates' generated joints); a project outside the tutorial for the
README alone (a second project to keep green).

**D3. The block is `Drum` and `Counter`,** the shortest text that shows a
connector declared on a part and the mates that use it. `Base` and
`Crank` are omitted; the prose says so and links the module on GitHub,
since the sdist has never carried the tutorial's modules. The prose around
the block names each declaration in one clause, in the same voice for
every one, defines no term and states no mechanism; the joints page is
linked for frames and mates and the tutorial for the rest.

**D4. The README states no version of Machinome.** The test refuses a
heading containing a digit and any match of
`(?:Version|Machinome|machinome|solid-node)\s+\d+\.\d`. "Python 3.11" is
not a Machinome version and passes.

**D5. The sections and the size are pinned.** The exact heading list, the
way the structure test pins the manual's navigation captions; and a cap of
1500 words over the whole file, so that an addition is a trade for
something already there. The page is 1422 words.

**D6. The contributor material moves to `CONTRIBUTING.rst` with its text
kept.** *Development environment*, *Running tests* and *Development
discipline* replace the boilerplate; *Where things live* is dropped
because the briefing's *Layout* owns it, and the guide points there; the
Python claim is corrected to `pyproject.toml`'s `requires-python`; the
instruction to list features in the README goes; the Discord line and the
maintainers' deploying reminder stay; the Sphinx-only `.. highlight::`
directive, which plain docutils reports as an unknown directive, goes.

**D7. The tests live in `tests/test_docs_structure.py`,** the file that
already reads the README for its licence words and stale names, as a
`ReadmeTest` class: sections, size, no version, every Python block
verbatim from a module under `docs/tutorial/counter/`, a mate stated and
no `translate(`.

**D8. The distribution is checked.** `python -m build` into the scratch
directory and `twine check` on the wheel and the sdist prove the README
renders as the long description. Every manual URL in the README is
checked against the `docs/` tree.

**D9. No ADR.** A README is not architecture.

## Risks / Trade-offs

- [The example is a fragment and cannot be pasted and run] → the prose
  says what it omits and links the whole module; the substring pin keeps
  the fragment true to source the suite builds.
- [The cap is tight and a legitimate future fact does not fit] → the
  change trades it against a sentence that earns less, or brings the pilot
  the case for moving the cap by a change to the requirement, never
  silently.
- [A later cycle appends a release section again] → the section pin
  refuses it, naming the headings found.
- [A module in the tutorial package that no chapter teaches] → its
  docstring says what it serves, the manifest names it `readme`, and the
  README links it; when the tutorial moves onto mates, the chapter's module
  can replace it.
- [Moving text to `CONTRIBUTING.rst` loses a contributor who only reads the
  README] → the README's last section names the guide, the briefing and
  the issue tracker.
