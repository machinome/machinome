# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The web viewer's staging of a still: what it reads at one instant.

`machinome snapshot --viewer web` asks the web viewer, through the seam
`machinome.viewer`, to present the posed node inside the project build lock.
This module does that from what the core offers: the assembled node, the
document serializer (`machinome.core.serializer`) and the artifact inventory
(`machinome.core.pieces`). It serializes the photographed node into a staging
directory of its own beside the build and copies the models and markings it
names there, so the capture reads one directory and the project's published
build is never touched. The core's modules are imported inside the functions
that use them, so resolving the viewer costs none of them.
"""

import json
import os
import shutil
import tempfile

from machinome.viewer import EXTRAS, ViewerError, unreadable
from machinome.viewer.web import bundle


def stage(node, build_dir):
    """Describe `node` in a private directory beside the build.

    The document is serialized here rather than republished into the
    build, because the build's own document and artifacts belong to
    whatever produced them -- usually a running `machinome develop` serving
    the project's root. Writing this node's tree there would replace
    that model, sweep the artifacts it still references, and discard any
    recorded build error. A snapshot only reads.
    """
    from machinome._artifact import ArtifactChanged

    for attempt in range(3):
        try:
            return _stage(node, build_dir)
        except ArtifactChanged:
            if attempt == 2:
                raise


def _stage(node, build_dir):
    """Perform one coherent read-only staging attempt."""
    from machinome.core.pieces import PieceInventory
    from machinome.core.serializer import (
        compiled_clocked, compiled_program, document_body, drivers_table,
        serialize_node,
    )

    if not bundle.has_bundle():
        raise ViewerError(bundle.missing_bundle_remedy())

    artifacts = {}
    # A marking is staged beside the models it belongs to, by the
    # same build-relative path: the capture reads one directory.
    markings = {}
    # A capture BAKES one instant: the node arrives keyframed and
    # posed at whatever `--drive` asked for, and its operations hold
    # the numbers that pose produced. So this document is not the
    # machine's own -- there is nothing symbolic in it to bind -- and
    # the drivers table it carries under a running root is the
    # declaration beside the program, not a scope for expressions.
    program, initial = compiled_program(node)
    # And the CLOCKED machine beside it. A capture of a clocked
    # model is refused below -- version 8 is not a version the
    # installed viewer reports until its own cycle adds it -- but
    # the refusal is the VERSION COMPARISON's and not a refusal of
    # its own, so the document is assembled exactly as any other
    # producer assembles it (OpenSpec change
    # ``publish-the-clocked-machine``, design section 15).
    clocked, bank = compiled_clocked(node)
    with PieceInventory(publish_facts=False) as inventory:
        root = serialize_node(
            node,
            lambda rigid_node: artifacts.setdefault(
                rigid_node.stl_file,
                artifact_path(rigid_node.stl_file, build_dir),
            ),
            inventory.register,
            graph_values=True,
            marking_path=lambda rigid_node, artifact: markings.setdefault(
                artifact, artifact_path(artifact, build_dir),
            ),
        )
        if program is not None:
            drivers = drivers_table(dict(program.inputs))
        elif clocked is not None:
            drivers = drivers_table(clocked.drivers)
        else:
            drivers = {}
        document = document_body(node, root, drivers, {}, program,
                                 initial if program is not None else bank,
                                 clocked=clocked)
        refuse_unreadable(document['version'])
        document["root"] = root
        document["pieces"] = inventory.pieces()

        staging = tempfile.mkdtemp(
            prefix=f"{os.path.basename(build_dir)}.web-snapshot.",
            dir=os.path.dirname(build_dir),
        )
        try:
            for source, relative in artifacts.items():
                if not os.path.isfile(source):
                    raise ViewerError(
                        f"Build artifact is missing: {relative}")
                target = os.path.join(staging, relative)
                inventory.copy_artifact(source, target)
            for source, relative in markings.items():
                if not os.path.isfile(source):
                    raise ViewerError(
                        f"Marking artifact is missing: {relative}")
                target = os.path.join(staging, relative)
                os.makedirs(os.path.dirname(target) or '.', exist_ok=True)
                # Not `inventory.copy_artifact`: that serves only
                # paths registered as pieces, and a marking is
                # deliberately not one.
                shutil.copy2(source, target)
            inventory.validate()
            # Document last: a successful staged directory never names a
            # missing or incoherent model.
            with open(os.path.join(staging, "viewer.json"), "w") as output:
                json.dump(document, output)
            return staging
        except Exception:
            remove_stage(staging)
            raise


def refuse_unreadable(version):
    """Refuse a document the installed web viewer cannot read, BEFORE the
    browser starts and before a staging directory exists.

    A capture is a one-shot: the viewer's own refusal would reach the
    caller as an opaque failure of a headless page, and the standing rule
    is to fail with what is missing rather than substitute. It never falls
    back to another viewer, which is the same rule stated for a missing
    viewer package and a missing browser.
    """
    message = unreadable(version, 'web')
    if message is not None:
        others = ' or '.join(f'--viewer {name}' for name in sorted(EXTRAS)
                             if name != 'web')
        raise ViewerError(
            f'{message}. A capture is a one-shot, so it is refused '
            f'here rather than failing inside a headless page: no '
            f'browser was started and no image was written. Install a '
            f'viewer that renders it, or photograph the model with '
            f'{others}.')


def artifact_path(stl_file, build_dir):
    """The staged, build-relative location of one artifact."""
    source = os.path.abspath(stl_file)
    if os.path.commonpath((source, build_dir)) != build_dir:
        raise ViewerError(f"Node artifact lies outside the build: {stl_file}")
    return os.path.relpath(source, build_dir)


def remove_stage(staging):
    shutil.rmtree(staging, ignore_errors=True)
