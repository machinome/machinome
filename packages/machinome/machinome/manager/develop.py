# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import sys
import logging
from machinome import viewer as viewers
from machinome.core.builder import Builder, BuildOutcome, get_build_dir
from machinome.core.loader import ProjectManifestError, select_model
from machinome.core.processes import Process
from machinome.manifest import reference_origin


logger = logging.getLogger('manager.develop')

#: What `--web-dev` does since the development page is served directly: it
#: is accepted, and says so.
WEB_DEV_NOTICE = ('--web-dev no longer does anything: the development page '
                  'is served directly, with no separate frontend process.')


# Every subprocess target is a module-level function taking plain values.
# The subprocesses a develop session runs do not inherit this process's
# memory; each is handed its target and arguments to reconstruct in a fresh
# interpreter, and the command object -- which holds an unpicklable
# ArgumentParser -- stays here. See `machinome.core.processes`.
#
# The viewer is not one of these targets at all: it serves in this process,
# in a session it owns, reached through the seam `machinome.viewer`.


def run_builder(path, overrides, is_reload=False, callback=None,
                viewer=None):
    Builder(
        path,
        is_reload=is_reload,
        callback=callback,
        lifecycle=True,
        overrides=overrides,
        viewer=viewer,
    ).start()


class Develop:
    """Runs all processes required for developing with machinome.
    Monitors filesystem and executes transpilations and compilations on background,
    and serves the project through the viewer chosen by `--viewer`, the
    project's viewer or the browser viewer, unless the viewerless watch loop
    was explicitly requested.
    """

    needs_node = True

    def add_arguments(self, parser):
        self.parser = parser
        parser.add_argument('--viewer', metavar='NAME', default=None,
                            help='The viewer that serves the project (default: '
                                 "the project's viewer, else "
                                 f"{viewers.DEFAULTS['serve']})")
        parser.add_argument('--web', action='store_true',
                            help='View the project in the browser through the installed '
                                 'machinome-viewer (the default)')
        parser.add_argument('--web-dev', action='store_true',
                            help='Accepted and ignored: the development page is served '
                                 'directly')
        parser.add_argument('--no-web', action='store_true',
                            help='Run the builder watch loop with no viewer, for a host '
                                 'that publishes its own view of the build directory')
        parser.add_argument('--debug-builder', action='store_true',
                            help='Debug mode supports breakpoints, but reload is not automatic')
        parser.add_argument('--callback', metavar='URL',
                            help='POST URL notified after each complete build')

    def web(self):
        """The chosen viewer's session on this project's build directory."""
        return self.provider.serve(get_build_dir(self.path))

    def handle(self, args):
        # A declared model name, or the default, selects what to load and
        # the build directory to serve; the builders this loop starts and
        # the viewer it serves inherit that selection.
        try:
            selection = select_model(args.path)
        except ProjectManifestError as error:
            sys.stderr.write(f'Error: {error}\n')
            raise SystemExit(1)
        selection.anchor()
        self.path = selection.reference
        # Every builder this loop starts, first run and each reload,
        # loads the root with the same parameters the session asked for.
        self.overrides = list(getattr(args, 'set', None) or [])
        callback = getattr(args, 'callback', None)
        no_web = getattr(args, 'no_web', False)
        self.web_dev = getattr(args, 'web_dev', False)
        explicit = getattr(args, 'viewer', None)
        wants_web = args.web or self.web_dev

        if no_web and wants_web:
            self.parser.error(
                '--no-web cannot be combined with --web or --web-dev')
        if no_web and explicit is not None:
            self.parser.error(
                '--no-web runs no viewer and cannot be combined with '
                '--viewer')
        if callback and self.web_dev:
            self.parser.error(
                '--callback is not available with --web-dev')
        if wants_web:
            if explicit not in (None, 'web'):
                self.parser.error(
                    f'--web names the web viewer and --viewer {explicit} '
                    f'another; name one')
            explicit = 'web'
        if self.web_dev:
            logger.warning(WEB_DEV_NOTICE)

        # Interactive development has one viewer. Resolve it, and its
        # report, before starting either child so a missing or incapable
        # viewer never leaves a watch loop running without the requested
        # surface. `--no-web` deliberately resolves none, for an external
        # host or a builder-only session.
        self.provider = None
        name = None
        if not no_web:
            try:
                self.provider = viewers.resolve(
                    'serve', 'machinome develop', explicit,
                    reference_origin(args.path))
                name = self.provider.NAME
                self.provider.describe()
            except (ImportError, LookupError, RuntimeError, OSError,
                    ProjectManifestError) as error:
                sys.stderr.write(f'Error: {error}\n')
                raise SystemExit(1)

        session = None
        if self.provider is not None:
            try:
                session = self.web()
            except viewers.ViewerError as error:
                sys.stderr.write(f'Error: {error}\n')
                raise SystemExit(1)

        if args.debug_builder:
            return run_builder(self.path, self.overrides, callback=callback,
                               viewer=name)

        builder_proc = None

        # Only the very first builder attempt is "startup": a project
        # that is already broken at launch exits cleanly instead of
        # looping. Every attempt after that is a WATCH-LOOP reload,
        # which must survive an import error raised while re-loading
        # edited source (see Builder.is_reload / _on_reload_exception).
        first_run = True

        while True:
                if session is not None and builder_proc:
                    # The builder that went before published a build: tell
                    # every open page, on the socket it keeps open.
                    logger.info('Reloading the viewer')
                    session.reload()

                builder_proc = Process(target=run_builder,
                                       args=(self.path, self.overrides,
                                             not first_run, callback, name))
                builder_proc.start()

                try:
                    builder_proc.join()
                except KeyboardInterrupt:
                    if session is not None:
                        session.stop()
                    sys.exit(0)

                exitcode = builder_proc.exitcode
                if exitcode == BuildOutcome.RENDERED.value:
                    first_run = False
                    continue
                if exitcode == BuildOutcome.SOURCE_CHANGED.value:
                    first_run = False
                    continue
                if first_run and exitcode:
                    logger.error('Initial build failed, exiting')
                    if session is not None:
                        session.stop()
                    sys.exit(exitcode)
                first_run = False
