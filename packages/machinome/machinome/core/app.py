# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model's own app: read from its root's declaration, bundled by the
viewer through the seam's operation `bundle`, beside the document that
names it (OpenSpec change `declare-a-models-app`).

A node class declares `app = 'app/index.tsx'`, a TypeScript or JavaScript
file relative to the file whose class body wrote it; `NodeMeta` checks the
form there. Only the declaration of the root a document is published for is
read. Here the entry is resolved, kept inside the project, and handed with
the project's root to the viewer that bundles, which writes the app's files
into the directory the document is published in and answers their names,
or refuses with its sentence.

Every refusal is a sentence naming the root's class and the declared path.
A build records it in the document, as the app's `refusal`, and publishes
the model as usual (`publish_app`); an export refuses (`AppRefused`).

A model with no app asks nothing of this module but `declared_app`, and
no viewer is resolved for it.
"""

import inspect
import logging
import os
from dataclasses import dataclass, field

from machinome import viewer as viewers
from machinome.manifest import ProjectManifestError
from machinome.node.declarative import APP_SUFFIXES

logger = logging.getLogger('core.app')

#: The files of an app's directory whose edit is an edit to the app, where
#: the bundle's own inputs are not known (design Decision 5a).
WATCHED_SUFFIXES = APP_SUFFIXES + ('.css',)


class AppRefused(Exception):
    """An app that cannot be bundled; the message is the sentence."""


@dataclass
class AppPublication:
    """What publishing a root's app gave: the document's `app` record, and
    what to watch for an edit to the app -- the files the bundle read, or,
    where it was refused before they were known, the directory of its
    declared file (None when no edit of the app's own files can repair it).
    """

    record: dict
    inputs: list = field(default_factory=list)
    directory: str = None


def declaring_class(klass, name):
    """The class of `klass`'s method resolution order whose own body
    assigned `name`, or None."""
    for each in klass.__mro__:
        if name in vars(each):
            return each
    return None


def declared_app(root):
    """The absolute path of the app `root`'s class declares, own or
    inherited, relative to the file of the class that declared it; None
    when it declares none. Only `root` is read, never its children."""
    owner = declaring_class(type(root), 'app')
    if owner is None:
        return None
    value = vars(owner)['app']
    if not isinstance(value, str):
        return None
    directory = os.path.dirname(os.path.realpath(inspect.getfile(owner)))
    return os.path.normpath(os.path.join(directory, value))


def _declared(root):
    owner = declaring_class(type(root), 'app')
    return f"{type(root).__name__}.app = '{vars(owner)['app']}'"


def _inside(path, root):
    try:
        return os.path.commonpath((path, root)) == root
    except ValueError:
        return False


def checked_entry(root):
    """The real path of `root`'s app, refused when it does not exist or
    lies outside the project; with the project's real root."""
    from machinome.manifest import project_root

    entry = declared_app(root)
    project = os.path.realpath(project_root(root.src))
    if not os.path.isfile(entry):
        raise AppRefused(f'{_declared(root)} names {entry}, which does not '
                         f'exist')
    real = os.path.realpath(entry)
    if not _inside(real, project):
        raise AppRefused(f"{_declared(root)} names {real}, which is outside "
                         f"the project at {project}; an app's files are the "
                         f"project's own")
    return real, project


def bundler(root, needed_by, explicit=None, origin=None):
    """The viewer that bundles, chosen as every operation's viewer is; its
    refusal, by the seam's own sentence, as `AppRefused`."""
    try:
        return viewers.resolve('bundle', needed_by, explicit, origin)
    except (ImportError, LookupError, RuntimeError,
            ProjectManifestError) as error:
        raise AppRefused(f'{_declared(root)} cannot be bundled: '
                         f'{error}') from None


def bundle(root, provider, entry, project, output_dir):
    """Bundle `root`'s app with `provider` into `output_dir`: the record
    and the files the bundle read, or `AppRefused` with the viewer's
    sentence."""
    try:
        answer = provider.bundle_app(entry, project, output_dir)
    except viewers.ViewerError as error:
        raise AppRefused(f'{_declared(root)} cannot be bundled: '
                         f'{error}') from None
    record = {'script': answer['script']}
    if answer.get('stylesheet'):
        record['stylesheet'] = answer['stylesheet']
    return record, list(answer.get('inputs') or ())


def publish_app(root, output_dir, needed_by, explicit=None, origin=None):
    """Bundle `root`'s app beside the document published in `output_dir`
    and answer its `AppPublication`; a refusal is the record's `refusal`,
    logged once as an error, and never raised."""
    stage = 'check'
    try:
        entry, project = checked_entry(root)
        provider = bundler(root, needed_by, explicit, origin)
        stage = 'bundle'
        record, inputs = bundle(root, provider, entry, project, output_dir)
    except AppRefused as refused:
        sentence = str(refused)
        logger.error(sentence)
        directory = None
        declared = declared_app(root)
        if stage == 'bundle' or not os.path.exists(declared):
            # Refused before the bundle's inputs were known, by something
            # an edit of the app's own files can repair: its file is
            # missing, or its sources did not build.
            directory = _existing_directory(declared)
        return AppPublication({'refusal': sentence}, [], directory)
    return AppPublication(record, inputs, None)


def _existing_directory(path):
    directory = os.path.dirname(path)
    while directory and not os.path.isdir(directory):
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return os.path.realpath(directory) if directory else None


def widgetless_refusal(root):
    """The sentence refusing a widget-less export of `root`, or None when
    it declares no app."""
    if declared_app(root) is None:
        return None
    owner = declaring_class(type(root), 'app')
    return (f"machinome export --no-widget does not carry a model's app, and "
            f"{type(root).__name__} declares app = '{vars(owner)['app']}'; "
            f"export it with its widget")
