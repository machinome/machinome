# machinome-movie

The Python half of Videomaker: the declarations a project writes a movie in,
and their evaluation to the movie document the renderer reads. See
[Declaring a movie](../docs/declaring-a-movie.md) for how to write one and
[the movie document](../docs/movie-document.md) for what it evaluates to.

Private, unversioned (0.0.0), unpublished; its licence is not selected.

    python -m machinome_movie list <project-dir>
    python -m machinome_movie evaluate <project-dir> <movie-name> [--out FILE]

Tests: `python -m pytest` from this directory.
