"""python -m machinome_movie list <project-dir>
python -m machinome_movie evaluate <project-dir> <movie-name> [--out FILE]
python -m machinome_movie watch <project-dir> <movie-name> [--out FILE] [--interval SECONDS]"""

import argparse
import math
import os
import sys

from .evaluate import evaluate, write
from .names import MovieError, module_directory
from .project import load_movie, movies
from .watch import watch


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m machinome_movie',
                                     description='List and evaluate the movies a project declares.')
    commands = parser.add_subparsers(dest='command', required=True)
    listing = commands.add_parser('list', help="print the project's movies table")
    listing.add_argument('project')
    evaluating = commands.add_parser('evaluate', help='write a movie document')
    evaluating.add_argument('project')
    evaluating.add_argument('movie')
    evaluating.add_argument('--out', help='where to write it (default <movie dir>/_build/movie.json)')
    watching = commands.add_parser('watch', help='evaluate a movie, then again whenever a file of its project changes')
    watching.add_argument('project')
    watching.add_argument('movie')
    watching.add_argument('--out', help='where to write it (default <movie dir>/_build/movie.json)')
    watching.add_argument('--interval', default='0.5', help='seconds between two looks at the files (default 0.5)')
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == 'watch':
            # Each evaluation prints the path or the refusal; an interrupt ends it.
            interval = _interval(arguments.interval)
            try:
                watch(arguments.project, arguments.movie, out=arguments.out, interval=interval)
            except KeyboardInterrupt:
                pass
            return 0
        if arguments.command == 'list':
            for name, reference in movies(arguments.project).items():
                print(f'{name}\t{reference}')
            return 0
        movie = load_movie(arguments.project, arguments.movie)
        out = arguments.out or os.path.join(module_directory(movie), '_build', 'movie.json')
        write(evaluate(movie, name=arguments.movie, out=out), out)
        print(os.path.abspath(out))
        return 0
    except MovieError as refusal:
        print(f'machinome-movie: {refusal}', file=sys.stderr)
        return 1


def _interval(text):
    try:
        seconds = float(text)
    except ValueError:
        seconds = math.nan
    if not (math.isfinite(seconds) and seconds > 0):
        raise MovieError(f'--interval {text} is not a positive number of seconds')
    return seconds


if __name__ == '__main__':
    sys.exit(main())
