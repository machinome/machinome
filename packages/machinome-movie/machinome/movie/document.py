"""Check a movie document: its schema, then the refusals Python can make
before speech exists.

Evaluation applies this to its own output; the shared invalid fixtures run
through it. Anchors are not resolved here: a fault that needs the seconds
of a spoken phrase is the renderer's to find.
"""

import json
from importlib import resources

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from .names import MovieError

# Read once, with the code: the schema is part of the package, not an input
# of an evaluation.
SCHEMA = json.loads(resources.files(__package__).joinpath('machinome-movie-0.1.json')
                    .read_text(encoding='utf-8'))
_VALIDATOR = Draft202012Validator(SCHEMA)


def check_document(document, manifest=None):
    """Refuse `document`, naming the chapter, the shot and the field, if it
    is not a valid movie document. `manifest`, the export's, lets part paths
    be checked too."""
    declared = document.get('format') if isinstance(document, dict) else None
    if declared != 'machinome-movie/0.1':
        raise MovieError(f'Unsupported movie format: {declared}; this package writes and checks '
                         f'machinome-movie/0.1')
    error = best_match(_VALIDATOR.iter_errors(document))
    if error is not None:
        raise MovieError(f'The movie document is invalid at {_where(document, error.absolute_path)}: '
                         f'{error.message}')
    _Semantics(document, manifest).check()


def _where(document, path):
    """A schema error's location in the words refusals use: the chapter and
    shot by id, then the field."""
    path, words, node = list(path), [], document
    while path:
        key = path.pop(0)
        if key in ('chapters', 'shots') and path and isinstance(path[0], int):
            index = path.pop(0)
            try:
                node = node[key][index]
                name = node.get('id', f'#{index}')
            except (KeyError, IndexError, TypeError, AttributeError):
                name = f'#{index}'
            words.append(f"{'chapter' if key == 'chapters' else 'shot'} {name}")
            continue
        field = str(key) if not isinstance(key, int) else f'[{key}]'
        rest = ''.join(f'[{p}]' if isinstance(p, int) else f'.{p}' for p in path)
        words.append(f'field {field}{rest}')
        break
    return ', '.join(words) or 'the top level'


def _count(text, phrase):
    found, start = 0, 0
    while True:
        start = text.find(phrase, start)
        if start < 0:
            return found
        found, start = found + 1, start + 1


class _Semantics:
    def __init__(self, document, manifest):
        self.document = document
        self.paths = None if manifest is None else _paths(manifest.get('root') or {})

    def check(self):
        document = self.document
        chapters, shots = set(), {}
        film = [(chapter, shot) for chapter in document['chapters'] for shot in chapter['shots']]
        for chapter in document['chapters']:
            if chapter['id'] in chapters:
                raise MovieError(f"Chapter {chapter['id']} appears twice; chapter ids are unique")
            chapters.add(chapter['id'])
        for index, (chapter, shot) in enumerate(film):
            if shot['id'] in shots:
                raise MovieError(f"Shot {shot['id']} appears in chapters {shots[shot['id']]} and "
                                 f"{chapter['id']}; shot ids are unique across a movie")
            shots[shot['id']] = chapter['id']
            self.shot(chapter, shot, first=index == 0, last=index == len(film) - 1)
        for name, layer in document['layers'].items():
            for path in layer:
                self.path(path, f'layer {name}')

    def shot(self, chapter, shot, first=True, last=True):
        where = f"chapter {chapter['id']}, shot {shot['id']}"
        narration = chapter['narration']
        until = shot['until']
        if not isinstance(until, dict) and until <= 0:
            raise MovieError(f'{where}, until: the shot ends at or before its start (until {until})')
        if 'fadeIn' in shot and not first:
            raise MovieError(f"{where}: fadeIn is accepted only on the film's first shot")
        if 'fadeOut' in shot and not last:
            raise MovieError(f"{where}: fadeOut is accepted only on the film's last shot")
        for field, value in self.times(shot):
            if isinstance(value, dict) and ('spoken' in value or 'spokenEnd' in value):
                self.phrase(narration, value.get('spoken', value.get('spokenEnd')), where, field)
        for index, emphasis in enumerate(shot.get('code', {}).get('emphasis', [])):
            self.phrase(narration, emphasis['phrase'], where, f'code.emphasis[{index}].phrase')
        for index, overlay in enumerate(shot['overlays']):
            phrase = overlay.get('reveal', {}).get('phrase')
            if phrase is not None:
                self.phrase(narration, phrase, where, f'overlays[{index}].reveal.phrase')
        simulation = shot['simulation']
        marks = self.document.get('marks', {})
        for field, value in self.model_times(simulation):
            if isinstance(value, dict) and value['mark'] not in marks:
                declared = ', '.join(marks) or 'none'
                raise MovieError(f"{where}, {field}: unknown mark '{value['mark']}'; the "
                                 f"document's marks are {declared}")
        keys = simulation.get('keyframes')
        if keys is not None and not (keys[0]['at'] == 0 and keys[0]['seconds'] == simulation['from']
                                     and keys[-1]['at'] == shot['until']
                                     and keys[-1]['seconds'] == simulation['to']):
            raise MovieError(f"{where}: model keyframes must start at the shot's start (at 0, "
                             f"simulation.from) and end at its until (simulation.to)")
        for index, key in enumerate(shot['camera']):
            if key['preset'] not in self.document['cameras']:
                raise MovieError(f"{where}, camera[{index}]: unknown camera '{key['preset']}'")
        for name in shot['hiddenLayers']:
            if name not in self.document['layers']:
                raise MovieError(f"{where}, hiddenLayers: unknown layer '{name}'")
        for name in shot['evidence']:
            if name not in self.document['evidence']:
                raise MovieError(f"{where}, evidence: unknown evidence '{name}'")
        chosen = shot.get('set', 'paper-split' if 'code' in shot else 'paper')
        if chosen not in ('paper', 'paper-split', 'source-only'):
            raise MovieError(f"{where}: unknown set '{chosen}'; a set is paper, paper-split or "
                             f'source-only')
        if chosen == 'paper' and 'code' in shot:
            raise MovieError(f'{where}: the paper set shows the model alone, so it takes no code')
        if chosen != 'paper' and 'code' not in shot:
            raise MovieError(f'{where}: the {chosen} set shows source, so it needs code')
        if 'code' in shot and shot['code']['snippet'] not in self.document.get('sourceCode', {}):
            raise MovieError(f"{where}, code.snippet: unknown source excerpt '{shot['code']['snippet']}'")
        for index, picture in enumerate(shot.get('pictures', [])):
            for kind, table in (('still', 'stills'), ('clip', 'clips')):
                if kind in picture and picture[kind] not in self.document.get(table, {}):
                    raise MovieError(f"{where}, pictures[{index}]: unknown {kind} '{picture[kind]}'")
        for index, annotation in enumerate(shot.get('annotations', [])):
            if 'part' in annotation:
                self.part(annotation['part'], where, f'annotations[{index}].part')
        for index, cue in enumerate(shot.get('highlight', [])):
            for part in cue['parts']:
                self.part(part, where, f'highlight[{index}].parts')

    def phrase(self, narration, phrase, where, field):
        found = _count(narration, phrase)
        if found == 0:
            raise MovieError(f"{where}, {field}: the phrase '{phrase}' is absent from the "
                             f"chapter's narration")
        if found > 1:
            raise MovieError(f"{where}, {field}: the phrase '{phrase}' is ambiguous in the "
                             f"chapter's narration (it occurs {found} times)")

    def part(self, part, where, field):
        if isinstance(part, str):
            if part not in self.document['layers']:
                raise MovieError(f"{where}, {field}: unknown layer '{part}'")
        else:
            self.path(part, f'{where}, {field}')

    def path(self, path, where):
        if self.paths is not None and tuple(path) not in self.paths:
            raise MovieError(f"{where}: the export does not contain {'/'.join(path)}")

    @staticmethod
    def times(shot):
        yield 'until', shot['until']
        for index, key in enumerate(shot['camera']):
            yield f'camera[{index}].at', key['at']
        for index, key in enumerate(shot['simulation'].get('keyframes', [])):
            yield f'simulation.keyframes[{index}].at', key['at']
        for field in ('overlays', 'annotations', 'highlight', 'pictures'):
            for index, cue in enumerate(shot.get(field, [])):
                yield f'{field}[{index}].from', cue['from']
                yield f'{field}[{index}].to', cue['to']
                for number, key in enumerate(cue.get('view', [])):
                    yield f'{field}[{index}].view[{number}].at', key['at']
        for index, cue in enumerate(shot.get('code', {}).get('typing', [])):
            yield f'code.typing[{index}].from', cue['from']
            yield f'code.typing[{index}].to', cue['to']

    @staticmethod
    def model_times(simulation):
        yield 'simulation.from', simulation['from']
        yield 'simulation.to', simulation['to']
        for index, key in enumerate(simulation.get('keyframes', [])):
            yield f'simulation.keyframes[{index}].seconds', key['seconds']


def _paths(root):
    paths = set()

    def walk(node, path):
        paths.add(tuple(path))
        for child in node.get('children') or []:
            walk(child, path + [child.get('name')])
    walk(root, [])
    return paths
