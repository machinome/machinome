=========================
Profiles and their agents
=========================

A profile is the team a project opens with: which agents stand ready,
which one speaks with you, who assigns work to whom, what each may do, the
prompt each follows and the skills it may load. The studio ships two. The
choice is made when a project is created, recorded in its
``pyproject.toml`` and read every time the project opens; a project that
records none opens under ``fordesmac``. :doc:`reference/profiles` lists
what each declares.

Builder
=======

``builder`` is one agent, **Builder**, working directly with you. You
describe what you want; Builder designs, builds, tests and commits, and
reports back, asking only when a choice is yours to make. It never pushes.

Builder keeps the project's design in the project's own OpenSpec record,
which it creates on the first design change. A design change is one that
establishes or alters an interface between parts; Builder plans it and
commits the plan, then builds it, syncs the record and commits the parts,
their tests and the record together. A knob value, a build repair or a
snapshot is not a design change and is done directly. You never write,
read or approve a spec artifact to get work done: the record is there so
that "why is this part like this?" can be answered from it months later,
and Builder answers such questions from it.

For every new part Builder first wires the part into the model in a
deliberately disassembled position, then writes the fit or assembly test
that fails because the relationship is wrong, then assembles the part
until the test passes; builds, range checks and snapshots follow.

Fordesmac
=========

``fordesmac`` is a delegated team of four standing agents.

**Foreman** speaks with you and runs the work. It establishes enough intent
from the opening conversation for a first assignment rather than waiting
for complete requirements, assigns the specialists one increment at a
time, keeps design at most one released increment ahead of machining, and
keeps increments small: one evidence-producing slice, never a whole
mechanism in one drawing. It asks you only consequential questions.

**Designer** owns the project's design record, ``docs/design.md``, and its
increment drawings under ``docs/specs/``. A drawing states parameters,
mechanical formulas, interfaces, ranges and functional contracts, names
every separately manufactured item and the number of printed bodies it
resolves to, states which features fuse into one body and the weld at each
junction, and for a pair that transmits motion states the pitch geometry,
the tooth phase and the backlash window. A released drawing is immutable
while it is machined; Designer works ahead on the next.

**Machinist** builds the released slice, test first, from the drawing's
commit: it owns the project's code and tests, checks parameters across
their useful ranges, renders and inspects an isometric and an interface
view, and lands one coherent commit. It works from the framework's public
contract only, and reports a gap in that contract to Foreman rather than
guessing.

**Librarian** researches external CAD libraries and files a distilled,
verified note under the project's ``docs/notes/``. It is provisionally out
of service: the two backends give it no web, documentation or package
access, so it reports that it cannot take the assignment. Foreman knows.

What an agent can do
====================

Every agent works inside the active project's repository and nowhere else.
The studio gives each a bounded set of operations rooted there: reading,
searching, writing and editing files; Git status, diff, log, staging and
commit, and never push, reset, checkout, branch or rebase; the framework's
build, test and snapshot; messages to the other agents of its team; and,
for Builder alone, the project's OpenSpec record. There is no shell, no
web and no other network. Which of these an agent holds is declared by its
profile and cannot be widened by a project or a prompt, and no agent runs
with permission checking disabled.

An agent may also load the skills its profile allows: ``machinome-api``,
the framework's complete public contract, and ``machinome``, the craft of
building a part that is one connected body, meshes that are proven to
drive, and contracts that measure geometry rather than trust it. Agents
never read the framework's source and never look into another project.

Where the work is recorded
==========================

In the project, and only there: the source and its tests; under
``fordesmac``, ``docs/design.md``, ``docs/specs/`` and ``docs/notes/``;
under ``builder``, the ``openspec/`` record; the commits, one per coherent
slice; and the model's preview picture, committed with the model. Agents
commit and never push. What you see in a session, its conversation and its
activity, is not kept; the repository is the record.

Backends
========

An agent runs on one of two backends, chosen per agent by the project:
**Claude Code**, the default for every agent the project does not name,
with the model and effort its profile declares; and **OpenCode**, which a
project selects by naming a connected provider and a model, and which
otherwise inherits the model the OpenCode installation is logged in with.
On both, the agent's native file, shell and network tools are replaced by
the studio's bounded operations above, and the profile's prompt and skill
list travel with every session. Under OpenCode, a regular ``AGENTS.md`` at
the project root is appended to the prompt as subordinate guidance: it may
describe the project, and it cannot change an agent's model, tools, role or
boundaries. A backend that cannot enforce the profile's tool policy is not
selectable.
