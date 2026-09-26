=====================
The project workspace
=====================

An open project fills the browser. A title bar names the studio and the
project. An activity rail on the left offers four areas, **Model**,
**Code**, **Agents** and **Build**; a panel beside it holds that area's
context, the area itself fills the centre, and the conversation stands on
the right. Switching areas keeps everything where it was: the viewer's
camera, the open files and their unsaved text, the agent you were
inspecting, the transcript and your unsent draft.

The conversation
================

The conversation is with one agent: the one the project's profile puts in
front of you, **Builder** under ``builder`` and **Foreman** under
``fordesmac``. Write what you want in ordinary words; Enter sends, and
Ctrl+Enter starts a new line. The transcript holds your messages and that
agent's replies, attributed with the labels the profile gives you both. The
other agents of the team do not write here; what they are doing is in the
Agents area.

You can write while the team works. Direction reaches the agent during its
turn without interrupting a specialist's assignment; what it does with the
direction is its judgement, stated in its reply. When an agent's backend
fails, at a session limit or a lost login, a notice in the conversation
names the agent by its label and gives the backend's reason, and stays
until the agent recovers. The composer remains available: once access is
restored, a new message resumes the work.

The transcript survives a page reload and a lost connection for as long as
the session lasts, and ends with it.

Model
=====

Model shows the project's model in the framework's browser viewer, updated
in place as the source changes: a rebuilt part appears while the rest of
the model and your camera stay where they are, whoever made the change, an
agent, the Code area, or an editor outside the studio. The panel beside it
is the viewer's own assembly navigator, named **Assembly**: expand the
tree, hide and show parts, focus a subassembly and return to the full
assembly. How to orbit the camera, operate the controls a model declares
and read a running or clocked machine is the viewer's manual: `Using the
viewer <https://machinome-viewer.readthedocs.io/en/latest/using-the-viewer.html>`_.
Below the assembly, the panel lists the profile's agents with their live
state.

The studio watches the project's Python source and rebuilds the model with
``machinome build`` whenever it changes, then reports each published
artifact to the browser. When a build fails, the failure is shown beside
the model; the last complete model stays inspectable, and whatever a
partial build did publish is shown as it is. When the project has no
complete model at all, because its first build failed, the area says so
and the rest of the workspace remains usable.

Code
====

Code lists the project as Git sees it: tracked files and untracked files
that are not ignored, with ``.git``, ignored paths and the build output
left out. The root starts open and every directory below it starts
collapsed. The file the session's model is declared in opens first.

Open a file to edit it; each file keeps its own tab, undo history and view
state, and Ctrl+S (Cmd+S on a Mac) saves. A save is checked against the
revision you opened: if an agent changed the file meanwhile, the save is
refused, your text is kept, the file is marked as in conflict and you may
reload the external version. A file an agent changes while you have it
open and unedited is refreshed in place. A PNG opens as a read-only image.
Code offers no create, rename, delete, Git or terminal control; those
actions are the agents'. Saving a Python file rebuilds the model exactly as
an agent's write does.

Agents
======

Agents lists the session's roster. Select an agent to see its runtime,
backend, provider, model and reasoning level, its state, and its activity
in order: messages, tool calls with their results, file changes with their
diffs, and errors, with a filter for each kind and a way to open a changed
file in Code. The feed is what the session retains: bounded, and gone when
the session closes.

While an agent is idle, its model and reasoning level can be changed for
the rest of the session. Before an agent has done anything at all, its
backend and provider can be replaced too; after its first message,
assignment or action they are fixed for the session. Claude's provider is
Anthropic; Codex's is OpenAI, with only its qualified models available.
An unavailable Codex choice includes the qualification or login remedy.
OpenCode offers the providers it is connected to and the models
of the one you select; with none connected, it offers nothing. **Apply**
takes effect at once and, unless you untick it, records the selection in
the project's ``pyproject.toml`` for later sessions;
:doc:`reference/project-configuration` gives the grammar. A Claude agent
that has already worked keeps its model: the runtime is shown, read-only.

Build
=====

Build reads the distinct printed pieces the framework published with the
last complete model: each piece once, with the number of copies required,
its size, its volume, whether its mesh is watertight, and where in the
source it comes from. The selected piece is shown at true scale on a fixed
virtual bed of |build-volume|, with orbit, zoom and reset, and the facts say
whether its bounding box fits that volume in some orientation, labelled as
an envelope fit and nothing more. The studio does not slice, orient,
support, arrange, or estimate time or material.

**Download** packs one STL per distinct piece with a ``README.md`` listing
each file and how many copies to print. The archive is deterministic: an
unchanged publication gives the same bytes.
