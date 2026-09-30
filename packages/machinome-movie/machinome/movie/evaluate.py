"""Evaluate a movie, once and purely, to the movie document.

The only files read are the export's `manifest.json` and
`source-revision.txt`. Every path in the document is relative to `root`,
the movie's directory as seen from where the document is written.
"""

import json
import math
import os

from .document import _paths, check_document
from .movie import Credits, Evidence, Format, Movie, Narrator, Release
from .names import MovieError, declaring_class, module_directory
from .stage import Style
from .take import Camera, Layer, Loop, Source, Still

FORMAT = 'machinome-movie/0.1'


def evaluate(movie, *, name, out=None):
    """The document of `movie`, declared under `name`, as it will be read
    from `out` (default `<movie dir>/_build/movie.json`)."""
    if not (isinstance(movie, type) and issubclass(movie, Movie) and hasattr(movie, '_movie')):
        raise MovieError(f'{movie!r} is not a Movie')
    where = f'Movie {movie.__name__}'
    if not isinstance(name, str) or not name or not all(c.isalnum() or c in '_-' for c in name) \
            or name != name.lower():
        raise MovieError(f"{where}: '{name}' is not a movie name; a name is lower-case "
                         f"letters, digits, underscores and hyphens")
    declared = movie._movie
    directory = module_directory(movie)
    out = os.path.abspath(out) if out else os.path.join(directory, '_build', 'movie.json')

    def relative(path):
        return os.path.relpath(path, directory).replace(os.sep, '/')

    chapters = [(chapter_id, klass._compiled) for chapter_id, klass in declared['chapters']]
    loop = _one_loop(where, chapters)
    export = loop.export_directory()
    manifest = _read_json(os.path.join(export, 'manifest.json'), where)
    seconds = (manifest.get('animation') or {}).get('loop')
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not seconds > 0:
        raise MovieError(f'{where}: the export {relative(export)} has no animation.loop; only a '
                         f'posed model with a normalized loop is filmable')
    revision = _read_revision(os.path.join(export, 'source-revision.txt'))
    paths = _paths(manifest.get('root') or {})
    for chapter_id, compiled in chapters:
        for here, written, names in compiled['parts']:
            _check_path(paths, here, written, names, relative(export))
    for layer_name, parts in loop._layer_paths.items():
        for written, names in parts:
            _check_path(paths, f'{loop.__name__}.{layer_name}', written, names, relative(export))

    found = declared['found']
    document = {'format': FORMAT, 'id': name.replace('_', '-'), **declared['text'],
                'root': os.path.relpath(directory, os.path.dirname(out)).replace(os.sep, '/'),
                'output': found[Format].document(),
                'model': {'manifest': relative(os.path.join(export, 'manifest.json')),
                          'expectedDurationSeconds': seconds,
                          'timeMode': 'normalized-loop',
                          'sourceRevision': revision,
                          'readiness': loop.readiness},
                'marks': dict(loop.marks),
                'audio': found[Narrator].document(),
                'cameras': {c.document_name(): c.document()
                            for c in loop.declarations(Camera).values()},
                'layers': {l.document_name(): [names for _, names in loop._layer_paths[attribute]]
                           for attribute, l in loop.declarations(Layer).items()},
                'sourceCode': {s.document_name(): {'file': relative(_declared_path(s)),
                                                   'lines': list(s.lines)}
                               for s in loop.declarations(Source).values()},
                'stills': {s.document_name(): _still(s, relative)
                           for s in loop.declarations(Still).values()},
                'clips': {},
                'evidence': {},
                'chapters': [{'id': chapter_id, 'narration': compiled['narration'],
                              'shots': compiled['shots']} for chapter_id, compiled in chapters]}
    style = found[Style]
    if style is not None:
        document['style'] = style.document()
    evidence = found[Evidence]
    if evidence is not None:
        base = module_directory(declaring_class(movie, _attribute_of(movie, evidence)))
        document['evidence'] = {key: relative(os.path.join(base, path))
                                for key, path in evidence.paths.items()}
    credits = found[Credits]
    if credits is not None:
        written = {key: value for key, value in credits.fields.items() if value is not None}
        if credits.license_file is not None:
            base = module_directory(declaring_class(movie, _attribute_of(movie, credits)))
            written['licenseFile'] = relative(os.path.join(base, credits.license_file))
        document['credits'] = written
    release = found[Release]
    if release is not None:
        base = module_directory(declaring_class(movie, _attribute_of(movie, release)))
        document['release'] = {'simulationUrl': release.simulation_url,
                               'sourceUrl': release.source_url,
                               'descriptionTemplate': relative(os.path.join(base, release.description))}
    document = _normal(document)
    check_document(document, manifest)
    return document


def dumps(document):
    """Canonical JSON: sorted keys, two-space indent, UTF-8, a trailing
    newline, integral floats written as integers."""
    return json.dumps(_normal(document), sort_keys=True, indent=2, ensure_ascii=False) + '\n'


def write(document, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as stream:
        stream.write(dumps(document))


def _normal(value):
    if isinstance(value, dict):
        return {key: _normal(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normal(item) for item in value]
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def _attribute_of(movie, value):
    for klass in movie.__mro__:
        for attribute, held in vars(klass).items():
            if held is value:
                return attribute
    raise MovieError(f'Movie {movie.__name__}: cannot find where {value!r} is declared')


def _declared_path(declaration):
    return os.path.normpath(os.path.join(module_directory(declaration.loop), declaration.file))


def _still(still, relative):
    written = {'file': relative(_declared_path(still)), 'credit': still.credit,
               'rights': still.rights}
    if still.upscale is not None:
        written['upscale'] = still.upscale
    return written


def _one_loop(where, chapters):
    seen = {}
    for chapter_id, compiled in chapters:
        for here, loop in compiled['loops']:
            seen.setdefault(loop, here)
    if len(seen) != 1:
        names = ', '.join(f'{loop.__name__} ({here})' for loop, here in seen.items())
        raise MovieError(f'{where}: a movie films one take, and this one uses {len(seen)}: {names}')
    loop = next(iter(seen))
    if not issubclass(loop, Loop):
        raise MovieError(f'{where}: {loop!r} is not a Loop')
    return loop


def _read_json(path, where):
    try:
        with open(path, encoding='utf-8') as stream:
            return json.load(stream)
    except FileNotFoundError:
        raise MovieError(f'{where}: there is no export manifest at {path}; export the model first')


def _read_revision(path):
    try:
        with open(path, encoding='utf-8') as stream:
            return stream.read().strip() or None
    except FileNotFoundError:
        return None


def _check_path(paths, where, written, names, export):
    if tuple(names) not in paths:
        raise MovieError(f"{where}: {written} resolves to {'/'.join(names)}, which the export "
                         f"{export} does not contain; re-export the model or correct the path")
