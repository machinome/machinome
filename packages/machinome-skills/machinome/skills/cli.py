# Machinome Skills - The machinome skills for assistants that read Agent Skills
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome skills`, the command this package contributes through the
entry-point group `machinome.commands` (ADR-189, change `join-skills`).

The module imports nothing at its import, so `machinome -h` pays for it
only the class; `handle` imports the installer.
"""


class Skills:
    """Install the machinome skills where your assistants read them"""

    needs_node = False

    def add_arguments(self, parser):
        verbs = parser.add_subparsers(dest='verb', required=True,
                                      metavar='{install,update,list}')
        self.parsers = {}
        install = verbs.add_parser(
            'install',
            help='copy the skills into the directories of the tools you '
                 'name, or choose them at a prompt')
        install.add_argument(
            'path', nargs='?', default='.',
            help='the project to install into (default: the current '
                 'directory); ignored with --personal')
        install.add_argument(
            '--tools', metavar='all|none|ID,ID...',
            help='the tools to install for, by id (machinome skills list '
                 'names them); without it, a prompt that pre-selects the '
                 'tools found in the project, or agents when there is no '
                 'terminal to ask')
        install.add_argument(
            '--personal', action='store_true',
            help="write each tool's directory under your home instead of "
                 "the project's")
        install.add_argument(
            '--force', action='store_true',
            help='replace a skill of the same name that machinome skills '
                 'did not write')
        self.parsers['install'] = install

        update = verbs.add_parser(
            'update',
            help='rewrite the copies older than the installed package')
        update.add_argument(
            'path', nargs='?', default='.',
            help='the project to look in (default: the current directory); '
                 'ignored with --personal')
        update.add_argument('--personal', action='store_true',
                            help='look under your home instead')
        update.add_argument(
            '--force', action='store_true',
            help='rewrite every copy machinome skills wrote, current or '
                 'newer too')
        self.parsers['update'] = update

        listing = verbs.add_parser(
            'list',
            help='print the tools and where each reads its skills, then the '
                 'copies under a path')
        listing.add_argument(
            'path', nargs='?', default='.',
            help='the project to look in (default: the current directory); '
                 'ignored with --personal')
        listing.add_argument('--personal', action='store_true',
                             help='look under your home instead')
        self.parsers['list'] = listing

    def handle(self, args):
        from machinome.skills import installer
        verbs = {'install': installer.install, 'update': installer.update,
                 'list': installer.listing}
        try:
            status = verbs[args.verb](args)
        except installer.UsageError as error:
            self.parsers[args.verb].error(str(error))
        raise SystemExit(status)
