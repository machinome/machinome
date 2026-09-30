"""Declare a movie of a machinome model in Python and evaluate it, once and
purely, to the movie document the renderer reads.

A class body declares; a chapter finds its narration, elements and shots
by type in declaration order; a movie finds its chapters the same way; the
attribute holding a declaration is its name.
"""

from .anchors import Anchor, Narration
from .document import check_document
from .evaluate import dumps, evaluate, write
from .movie import (Chapter, Credits, Cue, Evidence, Format, Movie, Narrator, Release,
                    Shot)
from .names import MovieError
from .project import load_movie, movies
from .stage import (Arrow, Dissolve, Element, Fade, FadeIn, FadeOut, Label, Paper,
                    PaperSplit, Reveal, Ring, Set, Slide, Slot, SourceOnly, Title, View,
                    Wipe)
from .take import Camera, Layer, Loop, Source, Still

__all__ = [
    'Anchor', 'Arrow', 'Camera', 'Chapter', 'Credits', 'Cue', 'Dissolve', 'Element',
    'Evidence', 'Fade', 'FadeIn', 'FadeOut', 'Format', 'Label', 'Layer', 'Loop', 'Movie',
    'MovieError', 'Narration', 'Narrator', 'Paper', 'PaperSplit', 'Release', 'Reveal', 'Ring',
    'Set', 'Shot', 'Slide', 'Slot', 'Source', 'SourceOnly', 'Still', 'Title', 'View', 'Wipe',
    'check_document', 'dumps', 'evaluate', 'load_movie', 'movies', 'write',
]
