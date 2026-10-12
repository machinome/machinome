"""python -m machinome.movie VERB ...: the command `machinome movie`, run by
this interpreter with the same parser.

    python -m machinome.movie list <project-dir>
    python -m machinome.movie evaluate <project-dir> <movie-name> [--out FILE]
    python -m machinome.movie watch <project-dir> <movie-name> [--out FILE] [--interval SECONDS]
"""

import argparse

from .cli import Movie


def main(argv=None):
    parser = argparse.ArgumentParser(prog='machinome movie')
    command = Movie()
    command.add_arguments(parser)
    command.handle(parser.parse_args(argv))


if __name__ == '__main__':
    main()
