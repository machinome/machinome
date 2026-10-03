# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Whether a module's kernels are installed, and the one refusal when not.

The CAD kernels are extras, not required dependencies (OpenSpec change
`lean-install`, capability `kernel-extras`): a bare `pip install machinome`
carries none, and each is installed by the extra named by the last
component of the address of the module that needs it -- `machinome[step]`
for `machinome.node.step`, `machinome[occt]` for the exact engine's
package. Each such module calls `require_extra` first, before it imports
any kernel, so an install without the extra fails at the module's import
with the line that installs it.

The check asks the import system whether each kernel can be found and
imports none of them: importing CadQuery to learn it is there would cost
seconds where the module deliberately imports none. A kernel that is found
and fails to import is not absent; it reports its own error where the
module really imports it.

This module imports nothing but `importlib.util`, so every module of the
core may use it, the exact engine included. No table here maps a module to
its extra: each module states its own.
"""

import importlib.util


class ExtraUnavailable(ModuleNotFoundError):
    """A module needs a kernel its extra installs, and it is not installed.

    A `ModuleNotFoundError`, whose `name` is the kernel that is in fact
    missing, so code catching the import system's errors keeps working; the
    extra is data on it (`extra`), so a caller answering by it -- the CLI,
    the markings seam -- needs no second copy.
    """

    def __init__(self, extra, needed_by, missing):
        super().__init__(
            f'{needed_by} needs {missing}, which is not installed; install '
            f'it with \'pip install "machinome[{extra}]"\'', name=missing)
        self.extra = extra
        self.needed_by = needed_by


def _found(module):
    """Whether the import system can find `module`, without importing it.

    A finder that answers by raising `ModuleNotFoundError` counts as not
    found; a module already loaded without a spec (`ValueError`) counts as
    found.
    """
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False
    except ValueError:
        return True


def require_extra(extra, needed_by, *modules):
    """Refuse, with `ExtraUnavailable`, the first of `modules` that cannot
    be found: `needed_by` names what needs it, `extra` the extra that
    installs it."""
    for module in modules:
        if not _found(module):
            raise ExtraUnavailable(extra, needed_by, module)
