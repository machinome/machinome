"""Declare a movie of a machinome model in Python and evaluate it, once and
purely, to the machinome-movie/0.2 document the stage draws.

A class body declares; a chapter finds its narration, elements and shots
by type in declaration order; a movie finds its chapters the same way; the
attribute holding a declaration is its name. A project declares its own
sets and elements, drawn by the stage module each names. The take a movie
films is a posed `Loop` or a clocked machine's `Take`, whose steps
evaluation records through the framework's simulation.
"""

import importlib
import sys
import types

#: Each name the package exports, by the module it is read from on first use
#: (PEP 562): `machinome -h` and `machinome movie -h` import the command's
#: module, and none of the evaluation (change `join-movie`).
_MODULES = {
    **dict.fromkeys(('Anchor', 'Narration'), 'anchors'),
    'check_document': 'document',
    **dict.fromkeys(('dumps', 'evaluate', 'write'), 'evaluate'),
    **dict.fromkeys(('Chapter', 'Credits', 'Cue', 'Evidence', 'Format', 'Movie',
                     'Narrator', 'Release', 'Shot'), 'movie'),
    'MovieError': 'names',
    **dict.fromkeys(('load_movie', 'movies'), 'project'),
    **dict.fromkeys(('Action', 'Dissolve', 'Element', 'Fade', 'FadeIn', 'FadeOut',
                     'Frame', 'Picture', 'Reframe', 'Reveal', 'Set', 'Slide', 'Slot',
                     'Split', 'Style', 'Title', 'View', 'Wipe'), 'stage'),
    **dict.fromkeys(('Camera', 'Layer', 'Loop', 'Mark', 'Move', 'Source', 'Still',
                     'Take', 'Trigger'), 'take'),
}

__all__ = [
    'Action', 'Anchor', 'Camera', 'Chapter', 'Credits', 'Cue', 'Dissolve', 'Element',
    'Evidence', 'Fade', 'FadeIn', 'FadeOut', 'Format', 'Frame', 'Layer', 'Loop', 'Mark', 'Move',
    'Movie', 'MovieError', 'Narration', 'Narrator', 'Picture', 'Reframe', 'Release', 'Reveal',
    'Set', 'Shot', 'Slide', 'Slot', 'Source', 'Split', 'Still', 'Style', 'Take', 'Title',
    'Trigger', 'View', 'Wipe',
    'check_document', 'dumps', 'evaluate', 'load_movie', 'movies', 'write',
]


def __getattr__(name):
    module = _MODULES.get(name)
    if module is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    loaded = importlib.import_module(f'.{module}', __name__)
    globals().update({exported: getattr(loaded, exported)
                      for exported, place in _MODULES.items() if place == module})
    return globals()[name]


class _Package(types.ModuleType):
    """The package's module: the import system binds a submodule to the
    package's attribute of its name, and the function `evaluate` keeps that
    name, as when the root imported its names at its own import."""

    def __setattr__(self, name, value):
        if isinstance(value, types.ModuleType) and _MODULES.get(name) == name:
            value = getattr(value, name)
        super().__setattr__(name, value)


sys.modules[__name__].__class__ = _Package
