======
Studio
======

.. needs:: studio

Machinome Studio is the project hub and workspace in which a maker builds
a mechanical CAD project with Machinome by talking to agents in the
browser. It opens a project hub over a folder of projects. Opening a
project starts a session of its own: the agents the project's profile
declares, a conversation with the one agent who speaks for the team, a live
view of the model that follows every change to its source, the project's
files, each agent's work as it happens, and the printable pieces of the
last complete build.

The maker describes the machine in ordinary words. The agents design it,
write it in the framework's declarative source, test it, inspect it and
commit it, inside that project's own Git repository and nowhere else. The
maker remains the authority for the decisions that matter, and the project
holds the record of every one that was made.

The studio is the package ``machinome-studio``, installed by
``machinome[studio]`` and numbered with the framework; ``machinome studio``
starts it.

The how-to guides take a maker through it:
:doc:`/howto/open-a-studio-project`, :doc:`/howto/studio-workspace` and
:doc:`/howto/studio-agents`. The pages below are its reference.

What it runs against
====================

Machinome |release| with its browser viewer, which must declare API
|studio_viewer_api| or later; the studio checks the installed viewer once
when it starts and refuses to open a project without one. ``pip install
"machinome[studio]"`` installs both beside it, with the viewer's capture,
through which the hub photographs each project.

Linux is the only validated platform. The agent backends are Claude Code,
OpenCode and qualified Codex, chosen per agent by the project. Codex is
limited to |studio_codex_version| on Linux x86_64, with the models and
reasoning levels in :doc:`project-configuration`. Other versions and
tool-affecting configurations are refused.

Limits
======

* The studio needs, beside the package, Git, OpenSCAD, the OpenSpec CLI,
  Playwright's Chromium and a logged-in backend, each installed by hand as
  :doc:`/howto/open-a-studio-project` says.
* The ``fordesmac`` librarian is out of service until the studio gives it
  a bounded research surface.
* A session keeps nothing: the project's repository is the record, and the
  agents commit but never push. Codex's separate authentication persists,
  but its ended project conversations do not.
* Tool scoping does not OS-sandbox code executed by project builds or
  tests. Codex cannot honor required signed commits. Its native refresh
  path and login persistence were exercised, not multi-day expiry behavior.
* The Build area's envelope fit is a bounding-box comparison, not a
  printability judgement. The studio does not slice and does not assess
  strength, tolerance or safety; nor does the framework.

.. toctree::
   :maxdepth: 1

   command
   project-configuration
   profiles
   troubleshooting
