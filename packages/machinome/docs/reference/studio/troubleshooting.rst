===============
Troubleshooting
===============

Each entry names what you see, why, and what to do.

The hub does not start
======================

**An error naming openspec.** The ``openspec`` command is missing or will
not run. Install it, ``npm install -g @fission-ai/openspec``, or run
``scripts/setup``, which installs it when it is absent. There is no reduced
mode.

**The address is already in use.** Another process holds the port. Start
with ``--port`` or set ``FLOOR_PORT``; :doc:`reference/cli`.

**A blank page.** The browser surface has not been built:
``npm --prefix floor/frontend run build``, or ``scripts/setup``.

A project cannot be opened
==========================

The hub says why on the card.

**Not a project repository.** The directory is not the root of its own Git
repository. Make it one, ``git init`` in it, or create the project from the
hub. The studio never initialises, stages or commits an existing directory
on its own.

**A profile that does not resolve.** The project's ``pyproject.toml`` names
a profile the studio does not ship, or a value that is not a lowercase
kebab-case name. Fix the ``profile`` key; the studio does not fall back to
the default in place of a declared profile.

**A runtime selection is rejected.** An agent's value names an unknown or
retired backend, a Claude or Codex model or reasoning level the studio does not
accept, or has the wrong number of parts; or the table carries a key the
studio does not define, such as ``effort`` or ``tools``.
:doc:`reference/project-configuration` gives the grammar. A selection for
an agent the profile does not declare is ignored and reported, not
refused.

**The former studio table.** The project's ``pyproject.toml`` still carries
``[tool.libresolid-studio]``, and the message says so. Rename the table to
``[tool.machinome-studio]``; its contents are unchanged.

**No usable browser viewer.** The framework installed beside the studio
reports no viewer, or one older than API |required-viewer-api|. Install or
upgrade it in the studio's environment, ``pip install --upgrade
"machinome[viewer]"``, and check with ``machinome viewer``.

**An agent would not start.** The backend is not installed, not on
``PATH``, or not logged in. The hub's Backends panel reports Claude Code
and OpenCode; Codex qualification reports its reason on project opening or
in Agents. Use the appropriate login command and open the project again. The
studio never opens a project with part of its team.

**Project preparation failed during a named stage.** The framework's
scaffold, the repository initialisation, or the location of the model's
build directory failed; the message names the stage and the path. A build
directory outside the project fails the open.

The model does not update
=========================

The studio rebuilds when a Python file outside the build output changes.
When a rebuild fails, the failure record is shown beside the model and the
last complete model stays; fix the source and the next build clears it.
When the studio itself could not run a build, that is reported as such,
distinct from the model failing to build. A session opened on one model of
a multi-model project builds and shows that model only.

No preview on a card
====================

A project that has never been built has no preview. A preview is rendered
after a build that changed what is published, and only through the
viewer's headless capture: Playwright's Chromium must be installed in the
studio's environment, ``python -m playwright install chromium``, which
``scripts/setup`` does. A render that fails is logged and changes nothing.

An agent stopped answering
==========================

A notice in the conversation names the agent and the backend's reason: a
session limit, a lost login, a backend that exited. Restore access with the
backend's own command and send a new message; the studio resumes on the
retained session where it can, and otherwise opens one replacement session
when the backend permits it. Codex never silently replaces a used
conversation whose history cannot safely be recovered; it leaves that role
failed with the reason while other roles continue.
Closing the project ends its conversation; reopening starts afresh.

The librarian says it cannot research
=====================================

It is right. Under ``fordesmac`` the librarian is provisionally out of
service: none of the scoped backends gives it web, documentation or package access.
Foreman knows and does not depend on it.

OpenCode offers no models
=========================

The Agents area shows only providers OpenCode is connected to. Log in or
connect a provider in OpenCode itself, then open the project again for a
fresh agent, or change an idle agent's runtime.

Codex is unavailable
====================

Use the reason shown in Agents or on the failed project card. Studio
requires its qualified pinned installation (:doc:`installation`), not
just any executable named ``codex``. Do not enable dangerous permissions
or relax the tool policy to bypass qualification.

For a missing, expired or rejected Studio login, stop the hub and run
``python -m floor.codex_auth login`` in the studio's Python environment,
then reopen the project. An ownership error means another hub or login
command still holds the same store; close that owner before trying again.
An ordinary Codex CLI login does not provision Studio's separate login.
An unavailable model may also mean your account lacks access; the studio
does not silently substitute another model.
