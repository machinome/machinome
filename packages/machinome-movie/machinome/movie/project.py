"""A project's movies: the `[tool.machinome.movies]` table of its
`pyproject.toml`, `name = "module:Class"`, imported with the project on
`sys.path` as its models are."""

import importlib
import os
import re
import sys
import tomllib

from .movie import Movie
from .names import MovieError

_NAME = re.compile(r'[A-Za-z0-9_-]+')


def movies(project):
    """The movies table, name -> reference, in table order."""
    pyproject = os.path.join(os.path.abspath(project), 'pyproject.toml')
    try:
        with open(pyproject, 'rb') as stream:
            config = tomllib.load(stream)
    except FileNotFoundError:
        raise MovieError(f'There is no pyproject.toml in {project}')
    table = config.get('tool', {}).get('machinome', {}).get('movies')
    if not isinstance(table, dict) or not table:
        raise MovieError(f'{pyproject} has no [tool.machinome.movies] table; declare a movie '
                         f'there as name = "package.module:Class"')
    for name, reference in table.items():
        if not _NAME.fullmatch(name):
            raise MovieError(f'{pyproject} declares the movie name {name!r}; a name is one word '
                             f'of letters, digits, underscores and hyphens')
        if not isinstance(reference, str) or reference.count(':') != 1:
            raise MovieError(f'{pyproject} declares movie {name!r} as {reference!r}; a movie is a '
                             f'reference of the form package.module:Class')
    return dict(table)


def load_movie(project, name):
    """Import the Movie class declared under `name`."""
    table = movies(project)
    if name not in table:
        raise MovieError(f"The project {project} declares no movie '{name}'; it declares: "
                         f"{', '.join(table)}")
    module_name, class_name = table[name].split(':')
    root = os.path.abspath(project)
    if root not in sys.path:
        sys.path.insert(0, root)
    module = importlib.import_module(module_name)
    movie = getattr(module, class_name, None)
    if not (isinstance(movie, type) and issubclass(movie, Movie)):
        raise MovieError(f"{table[name]}, declared as movie '{name}', is not a Movie class")
    return movie
