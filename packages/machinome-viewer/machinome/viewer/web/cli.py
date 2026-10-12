# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""``python -m machinome.viewer.web``: the framework's ``machinome viewer``.

The viewer's verbs ``describe``, ``serve`` and ``capture`` are the
framework's command, which asks this package through the seam of viewers
(change ``viewer-command``). Run through an interpreter, the module form
uses the viewer installed beside it, with the framework's parser, so the two
spellings cannot drift. The framework's command module is imported only when
``main`` runs: resolving this provider through the seam imports nothing of
it.
"""


def main(argv=None):
    """`python -m machinome.viewer.web`: the framework's `machinome
    viewer`, run by this interpreter with the same parser."""
    import argparse

    from machinome.manager.viewer import Viewer

    parser = argparse.ArgumentParser(prog='machinome viewer')
    command = Viewer()
    command.add_arguments(parser)
    command.handle(parser.parse_args(argv))
    return 0
