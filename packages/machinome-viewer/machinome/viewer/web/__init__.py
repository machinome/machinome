# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The browser viewer for machinome models: the web provider of the
framework's seam of viewers, `machinome.viewer`.

The package carries the built ``machinome-viewer.js`` bundle, the standalone
export page, the development page and the development server that serves a
published build to it, and the headless browser capture behind ``machinome
snapshot --viewer web``. The framework reaches all of it through this
module, as the viewer named ``web``, in its own process: it declares the
contract version it implements and the operations it offers, and each
operation imports its machinery only when it is called, so resolving the
viewer, asking its identity or whether it reads a document version imports
no web framework and no browser driver. The ``machinome-viewer`` console
script and ``python -m machinome.viewer.web`` describe, serve and capture
from the command line as before.
"""

__version__ = "0.8.1"

#: The viewer contract version this provider implements (the seam's
#: `machinome.viewer.CONTRACT`).
CONTRACT = 1

#: The name the seam knows this viewer by.
NAME = 'web'

#: Everything the contract names: a still, an interactive session and the
#: files an export or a page embeds.
OPERATIONS = frozenset({'present', 'capture', 'serve', 'embed'})

#: The snapshot options this viewer honours beyond the common ones: the
#: browser frames the whole model by default, which is what they ask.
CAPTURE_OPTIONS = frozenset({'autocenter', 'viewall'})


def identity():
    """`('machinome-viewer', <version>)`, the installed distribution."""
    from machinome.viewer.web.bundle import version
    return ('machinome-viewer', version())


def document_versions():
    """The node-tree document versions this build's widget renders."""
    from machinome.viewer.web.bundle import document_versions as declared
    return declared()


def readable(version):
    """Whether this viewer renders document `version`."""
    return version in document_versions()


def describe():
    """The report of the installed viewer: its bundle, its export page, its
    API, the document versions it renders and its version. Raises the
    bundle's own refusal when it is not built or cannot be made current."""
    from machinome.viewer.web.bundle import describe as report
    return report()


def files():
    """What an export or a documentation page embeds: the standalone page
    and the bundle."""
    from machinome.viewer.web.bundle import bundle_path, index_path
    return {'index.html': index_path(), 'machinome-viewer.js': bundle_path()}


def present(node, build_dir):
    """Bring the posed node's artifacts up to date and stage it beside
    `build_dir`; called inside the project build lock. Returns the staging
    directory, which `capture` photographs and `withdraw` removes."""
    from machinome.viewer.web.stage import stage
    node.build_stls()
    return stage(node, build_dir)


def withdraw(staging):
    """Remove a staging directory `present` made."""
    from machinome.viewer.web.stage import remove_stage
    remove_stage(staging)


def capture(staging, request, output):
    """Photograph `staging` into the PNG `output` in a headless browser, in
    this process, at the request's image size and animation time, framed by
    its camera notation as the core resolves it (`machinome.core.camera`)."""
    from machinome.core.camera import parse_camera
    from machinome.viewer import ViewerError
    from machinome.viewer.web.capture import (
        Capture, CaptureError, mount_options,
    )

    view = up = fov = None
    if request.camera:
        camera = parse_camera(request.camera)
        view = (tuple(camera.eye), tuple(camera.target))
        up, fov = tuple(camera.up), camera.fov
    width, height = (int(value) for value in request.imgsize.lower().split('x'))
    options = mount_options(time=request.time, view=view, up=up, fov=fov)
    try:
        Capture(staging).render(output, (width, height), options)
    except CaptureError as error:
        raise ViewerError(str(error)) from error


def serve(build_dir, port=None):
    """Serve `build_dir` to the development page in a thread this package
    owns; returns the session once the server listens."""
    from machinome.viewer.web.session import Session
    return Session(build_dir, port=port).start()


# Importing a submodule binds it as an attribute of its package, and
# `capture.py`, the machinery of the photograph, has the name of the
# operation `capture`: its first import would replace the operation by the
# module, and the seam would find a module where it calls a function. This
# package therefore keeps its operations: a submodule named as one is not
# bound over it, and stays where every import finds it, in `sys.modules`
# (`importlib.import_module('machinome.viewer.web.capture')`).
import sys as _sys  # noqa: E402
import types as _types  # noqa: E402


class _Provider(_types.ModuleType):

    def __setattr__(self, name, value):
        if name in OPERATIONS and isinstance(value, _types.ModuleType):
            return
        super().__setattr__(name, value)


_sys.modules[__name__].__class__ = _Provider
