"""Evaluate a movie, once and purely, to the machinome-movie/0.2 document.

The only files opened are the export's `manifest.json` and
`source-revision.txt` and the source files of the excerpts an emphasis
lights; the stage modules are checked to exist, not read. Every path in the
document is relative to `root`, the movie's directory as seen from where the
document is written.
"""

import json
import math
import os

from .document import FORMAT, _paths, check_document
from .movie import Credits, Evidence, Format, Movie, Narrator, Release
from .names import MovieError, declaring_class, module_directory, prop_kind
from .stage import Style
from .take import Camera, Layer, Loop, Source, Still
from .text import count_token, excerpt_line


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
    excerpts = _check_tokens(chapters)

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
                'stage': _stage(movie, chapters, directory, relative),
                'chapters': [{'id': chapter_id, 'narration': compiled['narration'],
                              'elements': compiled['elements'], 'shots': compiled['shots']}
                             for chapter_id, compiled in chapters]}
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
    check_document(document, manifest,
                   sources={source.document_name(): text for source, text in excerpts.items()})
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


##############################################
# The stage block

def _stage(movie, chapters, directory, relative):
    """The stage block: every set kind a shot uses and the project sets they
    derive from, every project element kind a chapter declares, and their
    modules."""
    where = f'Movie {movie.__name__}'
    project = _project_directory(directory)
    used = []
    for _, compiled in chapters:
        for chosen in compiled['sets']:
            # A project set's base is listed too, so `base` always names a
            # kind of this table or one the tool ships.
            while chosen is not None and chosen not in used:
                used.append(chosen)
                base = chosen.base() if chosen.project() else None
                chosen = base if base is not None and base.project() else None
    modules = set()

    def module(declaration, what):
        path = os.path.normpath(os.path.join(module_directory(declaration.module_owner()),
                                             declaration.module))
        _check_module(path, f'{where}: {what} {declaration.__name__}', declaration.module, project)
        written = relative(path)
        modules.add(written)
        return written

    sets = {}
    for chosen in used:
        if chosen.kind in sets:
            other = next(c for c in used if c.kind == chosen.kind and c is not chosen)
            raise MovieError(f'{where}: the sets {other.__qualname__} and {chosen.__qualname__} '
                             f'both have the kind {chosen.kind}; a kind names one set')
        entry = {'slots': list(chosen.slots())}
        if chosen.project():
            entry['module'] = module(chosen, 'set')
            entry['props'] = chosen.props()
            base = chosen.base()
            if base is not None:
                entry['base'] = base.kind
        sets[chosen.kind] = entry
    elements, classes = {}, {}
    for _, compiled in chapters:
        for key, element in compiled['project']:
            kind = type(element)
            if kind.kind in elements:
                if classes[kind.kind] is not kind:
                    raise MovieError(f'{where}: the elements {classes[kind.kind].__qualname__} and '
                                     f'{kind.__qualname__} both have the kind {kind.kind}; a kind '
                                     f'names one element')
                continue
            classes[kind.kind] = kind
            elements[kind.kind] = {'module': module(kind, 'element'),
                                   'props': {name: prop_kind(value) for name, value in element.props.items()},
                                   'actions': kind.actions()}
    return {'modules': sorted(modules), 'sets': sets, 'elements': elements}


def _project_directory(directory):
    """The project a movie belongs to: the nearest directory at or above the
    movie's that holds a pyproject.toml, or None."""
    here = directory
    while True:
        if os.path.isfile(os.path.join(here, 'pyproject.toml')):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def _check_module(path, where, written, project):
    if project is not None and os.path.commonpath([project, path]) != project:
        raise MovieError(f'{where}: its module {written} resolves to {path}, outside the project '
                         f'{project}; a stage module is the project\'s own file')
    if not os.path.isfile(path):
        raise MovieError(f'{where}: its module {written} does not exist (looked for {path})')


##############################################
# Tokens

def _check_tokens(chapters):
    """Refuse a token absent from or repeated in its excerpt. Returns the
    excerpts read, source -> text."""
    excerpts = {}
    for _, compiled in chapters:
        for here, source, token, line in compiled['tokens']:
            if source not in excerpts:
                excerpts[source] = _excerpt(source, here)
            first, last = source.lines
            text = excerpts[source] if line is None else excerpt_line(excerpts[source], first, line)
            found = count_token(text, token)
            if found != 1:
                state = 'absent from' if found == 0 else 'ambiguous in'
                where = (f'the excerpt {source.document_name()} ({source.file}, lines {first} to {last})'
                         if line is None else f'line {line} of the excerpt {source.document_name()} ({source.file})')
                raise MovieError(f"{here}: emphasize: the token '{token}' is {state} {where}; found "
                                 f"{found} times; a token is an identifier or a dotted path, bounded "
                                 f"by anything but a letter, a digit or an underscore, and occurs "
                                 f"once{'' if line is not None else ' (name line= to choose a line)'}")
    return excerpts


def _excerpt(source, where):
    path = _declared_path(source)
    first, last = source.lines
    try:
        with open(path, encoding='utf-8') as stream:
            lines = stream.read().splitlines(True)
    except FileNotFoundError:
        raise MovieError(f'{where}: the excerpt {source.document_name()} names {source.file}, '
                         f'which does not exist (looked for {path})')
    if last > len(lines):
        raise MovieError(f'{where}: the excerpt {source.document_name()} names lines {first} to '
                         f'{last} of {source.file}, which has {len(lines)}')
    return ''.join(lines[first - 1:last])


##############################################
# The rest

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
