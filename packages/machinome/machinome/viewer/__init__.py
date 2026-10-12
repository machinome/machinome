# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The seam of viewers: the contract the core speaks to the programs that
show a machine, and their resolution by name.

A viewer shows a machine: it takes a still of one assembled instant, serves
a build directory to a page that follows it as it is rebuilt, or gives the
files an export or a documentation page embeds. Each viewer is a provider,
one known module beneath this package, `machinome.viewer.<name>`, shipped by
a distribution of its own: the web viewer `machinome.viewer.web`
(`machinome-viewer`) and the OpenSCAD viewer `machinome.viewer.openscad`
(`machinome-viewer-openscad`). `EXTRAS` and `DEFAULTS` below are the only
place the core names a viewer's technology.

A provider declares the contract version it implements as its own
`CONTRACT`, its name as `NAME`, and the operations it offers as
`OPERATIONS`, a subset of this module's `OPERATIONS`; every viewer answers
its identity and the node-tree document versions it reads. The Protocols
below state what each operation asks. The seam resolves a viewer by
importing its address and nothing else, and refuses rather than replaces: a
viewer the core knows that is not installed by the extra that installs it,
an unknown name by the names the core knows, a provider of another contract
as incompatible, an operation the viewer does not offer by name. A command
chooses its viewer by its `--viewer` option, else by the project's
`[tool.machinome] viewer`, else by the default of the operation it needs
(`chosen`), and nothing consults which viewers are installed.

Only the standard library and `machinome.extras` are imported here, so
resolving a viewer, asking its identity or whether it reads a document
version costs no web framework, no browser driver and no CAD library (OpenSpec
change `viewer-seam`, ADR-194).
"""

import importlib
from dataclasses import dataclass
from typing import Any, Protocol

from machinome import _namespace_portions
from machinome.extras import ExtraUnavailable

#: The viewer contract version this core speaks. A provider declares the
#: version it implements as its own `CONTRACT`; they must be equal.
CONTRACT = 1

#: The viewers the core knows, by name, and the extra that installs each.
EXTRAS = {'openscad': 'viewer-openscad', 'web': 'viewer'}

#: The operations a viewer may offer beyond what every viewer answers.
OPERATIONS = ('present', 'capture', 'serve', 'embed')

#: The viewer each operation uses when neither the command nor the project
#: names one: a still is OpenSCAD's, serving and embedding the browser's.
DEFAULTS = {'capture': 'openscad', 'serve': 'web', 'embed': 'web'}

#: The manifest key a project names its viewer with.
KEY = '[tool.machinome] viewer'


class Viewer(Protocol):
    """What every viewer answers."""

    NAME: str
    CONTRACT: int
    OPERATIONS: frozenset

    def identity(self) -> tuple:
        """`(distribution, version)` of the installed provider."""

    def document_versions(self) -> Any:
        """The node-tree document versions the viewer reads, a list, or
        None for a viewer that reads no document."""

    def readable(self, version: int) -> bool:
        """Whether the viewer reads document `version`."""


class Presenter(Protocol):
    """`present`: prepare what the viewer reads at one assembled instant."""

    def present(self, node: Any, build_dir: str) -> Any:
        """Called by the command inside the project build lock with the
        posed root; returns the provider's own value, which `capture` and
        `withdraw` are handed."""

    def withdraw(self, presented: Any) -> None:
        """Remove what `present` prepared, after the capture, whether it
        succeeded or failed."""


class Capturer(Protocol):
    """`capture`: an image of what was presented."""

    #: The snapshot options the viewer honours beyond the common output,
    #: image size, time and camera.
    CAPTURE_OPTIONS: frozenset

    def capture(self, presented: Any, request: 'CaptureRequest',
                output: str) -> None:
        """Write the image of `presented` to `output`, or raise
        `ViewerError` writing none."""


class Session(Protocol):
    """An interactive session a viewer serves."""

    def reload(self) -> None:
        """Tell every open page that a build was published."""

    def stop(self) -> None:
        """Stop the server; returns when it has stopped."""


class Server(Protocol):
    """`serve`: an interactive session on a build directory."""

    def serve(self, build_dir: str, port: Any = None) -> Session:
        """Start serving `build_dir`; returns once the server listens, or
        raises `ViewerError`."""


class Embedder(Protocol):
    """`embed`: the files an export or a documentation page carries."""

    def files(self) -> dict:
        """`{'index.html': Path, 'machinome-viewer.js': Path}`."""

    def describe(self) -> dict:
        """The report of the installed viewer, `machinome viewer`'s."""


@dataclass(frozen=True)
class CaptureRequest:
    """The options of one still, as `machinome snapshot` was given them, so
    a provider reads no argument parser's namespace."""

    imgsize: str = '1920x1080'
    time: float = 0.0
    camera: Any = None
    autocenter: bool = False
    viewall: bool = False
    projection: Any = None
    colorscheme: Any = None
    view: Any = None
    render: bool = False
    preview: bool = False


class ViewerError(RuntimeError):
    """An operation of a viewer failed; the message is the sentence a
    command writes after `Error: `."""


class UnknownViewer(LookupError):
    """No viewer the core knows has this name."""

    def __init__(self, name):
        super().__init__(f'no viewer is named {name!r}; the viewers are '
                         f'{", ".join(sorted(EXTRAS))}')


class ViewerIncompatible(RuntimeError):
    """A provider of another contract version, or of none."""

    def __init__(self, name, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The {name} viewer machinome.viewer.{name} {stated}, but this '
            f'machinome speaks viewer contract version {CONTRACT}; install '
            f'the viewer released with this machinome')


class ViewerLacks(RuntimeError):
    """The chosen viewer does not offer the operation a command needs."""

    def __init__(self, name, operation, needed_by, declared=False):
        able = ', '.join(_able(operation)) or 'none is installed'
        named = (f"the {name} viewer, this project's viewer (`{KEY}`),"
                 if declared else f'the {name} viewer')
        message = (f'{needed_by} needs a viewer that can {operation}, and '
                   f'{named} cannot; the viewers that can: {able}')
        if declared:
            message += '; name one with --viewer'
        super().__init__(message)


def absent(name):
    """The refusal of viewer `name` when no installed distribution ships its
    module: it names the viewer, its module and the line that installs its
    extra."""
    return ExtraUnavailable(EXTRAS[name], f'the {name} viewer',
                            f'machinome.viewer.{name}')


def viewer(name):
    """The provider of viewer `name`, imported at its address.

    A provider whose own import is refused because a package its extra
    installs is absent passes that refusal unmodified; a provider that
    cannot be found at all is refused by `absent`, or as `UnknownViewer`
    for a name the core does not know; a provider of another contract is
    `ViewerIncompatible`. Nothing is cached here but by the import system.
    """
    address = f'machinome.viewer.{name}'
    try:
        provider = importlib.import_module(address)
    except ExtraUnavailable:
        raise
    except ModuleNotFoundError as error:
        if error.name != address:
            raise
        if name in EXTRAS:
            raise absent(name) from None
        raise UnknownViewer(name) from None
    declared = getattr(provider, 'CONTRACT', None)
    if declared != CONTRACT:
        raise ViewerIncompatible(name, declared)
    return provider


def require(name, operation, needed_by, declared=False):
    """The provider of viewer `name`, refused by name, naming what needs it,
    when it does not offer `operation`. `declared` says the name is the
    project's, so the refusal names the manifest key and the flag."""
    provider = viewer(name)
    if operation not in provider.OPERATIONS:
        raise ViewerLacks(name, operation, needed_by, declared)
    return provider


def _choice(operation, explicit=None, origin=None):
    """`(name, declared)`: the viewer `operation` uses, and whether the
    project's manifest named it."""
    if explicit is not None:
        return explicit, False
    from machinome.manifest import declared_viewer
    named = declared_viewer(origin)
    if named is not None:
        return named, True
    return DEFAULTS[operation], False


def chosen(operation, explicit=None, origin=None):
    """The name of the viewer `operation` uses: `explicit`, a command's
    `--viewer`, else the viewer the project above `origin` declares under
    `[tool.machinome]`, else the operation's default. No availability is
    consulted and nothing falls back."""
    return _choice(operation, explicit, origin)[0]


def resolve(operation, needed_by, explicit=None, origin=None):
    """The provider `chosen` names, required to offer `operation`."""
    name, declared = _choice(operation, explicit, origin)
    return require(name, operation, needed_by, declared)


def _able(operation):
    """The installed viewers that offer `operation`, by name."""
    able = []
    for name in sorted(EXTRAS):
        try:
            provider = viewer(name)
        except (ImportError, LookupError, ViewerIncompatible):
            continue
        if operation in provider.OPERATIONS:
            able.append(name)
    return able


def unreadable(version, name):
    """The one sentence a producer writes about a document version viewer
    `name` cannot read: the version, the versions it reads and its
    distribution's version. None when it reads the version, reads no
    document, or is not installed, which is not a document problem."""
    try:
        provider = viewer(name)
        versions = provider.document_versions()
    except (ImportError, LookupError, ViewerIncompatible, OSError):
        return None
    if versions is None or version in versions:
        return None
    distribution, installed = provider.identity()
    return (f'this model needs document version {version}, and the '
            f'installed {name} viewer renders '
            f'{", ".join(str(one) for one in versions)} '
            f'({distribution} {installed})')


# A provider is shipped by a distribution of its own, which installs its
# module here without this package's `__init__.py`; it is found as a portion
# of this package's path, and a second copy of the core never is (see
# `_namespace_portions`).
__path__ = _namespace_portions(__path__, __name__)
