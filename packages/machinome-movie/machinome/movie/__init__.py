"""Declare a movie of a machinome model in Python and evaluate it, once and
purely, to the machinome-movie/0.2 document the stage draws.

A class body declares; a chapter finds its narration, elements and shots
by type in declaration order; a movie finds its chapters the same way; the
attribute holding a declaration is its name. A project declares its own
sets and elements, drawn by the stage module each names.
"""

from .anchors import Anchor, Narration
from .document import check_document
from .evaluate import dumps, evaluate, write
from .movie import (Chapter, Credits, Cue, Evidence, Format, Movie, Narrator, Release,
                    Shot)
from .names import MovieError
from .project import load_movie, movies
from .stage import (Action, Dissolve, Element, Fade, FadeIn, FadeOut, Frame, Picture, Reveal,
                    Set, Slide, Slot, Split, Style, Title, View, Wipe)
from .take import Camera, Layer, Loop, Source, Still

__all__ = [
    'Action', 'Anchor', 'Camera', 'Chapter', 'Credits', 'Cue', 'Dissolve', 'Element',
    'Evidence', 'Fade', 'FadeIn', 'FadeOut', 'Format', 'Frame', 'Layer', 'Loop', 'Movie',
    'MovieError', 'Narration', 'Narrator', 'Picture', 'Release', 'Reveal', 'Set', 'Shot', 'Slide',
    'Slot', 'Source', 'Split', 'Still', 'Style', 'Title', 'View', 'Wipe',
    'check_document', 'dumps', 'evaluate', 'load_movie', 'movies', 'write',
]
