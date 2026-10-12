# machinome-studio

The studio of [Machinome](https://github.com/machinome/machinome): the
package `machinome.studio` and the command `machinome studio`. It opens a
project hub in the browser over a folder of projects; opening a project
starts a session of its own, with the agents its profile declares, the
conversation with the one who speaks for them, the model in the browser
viewer following every change to its source, the project's files and the
printable pieces of its last build. The agents work inside the project's own
Git repository through Claude Code, OpenCode or Codex.

## Install

    pip install "machinome[studio]"
    playwright install chromium
    machinome studio --projects-dir PATH

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
