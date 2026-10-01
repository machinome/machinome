"""Check a machinome-movie/0.2 document: its schema, then every refusal
Python can make before speech exists.

Evaluation applies this to its own output; the shared invalid fixtures run
through it. Anchors are not resolved here: a fault that needs the seconds of
a spoken phrase (an anchor before its shot, a token typed too late) is the
renderer's to find. Given the export's manifest, part paths are checked;
given the text of the source excerpts, emphasised tokens are.
"""

import json
from importlib import resources

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from .names import (EASES, MODULE_SUFFIXES, MovieError, exact_seconds, no_view_in_both,
                    prop_kind, seconds_written, shared_views)
from .text import TOKEN, count_phrase, count_token, count_words, excerpt_line

FORMAT = 'machinome-movie/0.2'

# Read once, with the code: the schema is part of the package, not an input
# of an evaluation.
SCHEMA = json.loads(resources.files(__package__).joinpath('machinome-movie-0.2.json')
                    .read_text(encoding='utf-8'))
_VALIDATOR = Draft202012Validator(SCHEMA)

#: The sets the tool ships for movies, with their slots.
SHIPPED_SETS = {'frame': ['stage'], 'split': ['left', 'right']}
#: The sets the stage runtime keeps for YAML episodes only.
EPISODE_SETS = ('paper', 'paper-split', 'source-only')
#: The element kinds the tool ships: the fields a declaration requires and
#: the fields it takes, `kind` aside.
SHIPPED_ELEMENTS = {
    'view': ({'camera'}, {'camera', 'hide'}),
    'source': ({'source'}, {'source'}),
    'title': ({'text'}, {'text', 'subtitle'}),
    'picture': (set(), {'still', 'clip', 'fit', 'inPoint'}),
}
#: Each shipped element's actions: required and accepted fields, besides
#: `element` and `action`.
ACTIONS = {
    'view': {'move': ({'camera', 'until'}, {'camera', 'until', 'ease'}),
             'highlight': ({'parts'}, {'parts', 'others', 'color'}),
             'ring': ({'part'}, {'part', 'padding', 'enter', 'leave'}),
             'label': ({'part', 'text'}, {'part', 'text', 'offset', 'enter', 'leave'}),
             'arrow': ({'place'}, {'part', 'point', 'text', 'place', 'enter', 'leave'})},
    'source': {'type': ({'throughLine', 'over'}, {'throughLine', 'over'}),
               'emphasize': ({'words'}, {'words', 'hold', 'line'})},
    'title': {'show': (set(), {'enter', 'leave', 'reveal'})},
    'picture': {'show': (set(), {'enter', 'leave', 'view'})},
}
#: Actions that end on their own; every other action spans its cue.
UNSPANNED = ('move', 'type', 'emphasize')
#: How a document's model time runs: a posed loop, or a clocked take.
TIME_MODES = ('normalized-loop', 'take')
#: Seconds within which a model time the reader adds itself, a mark plus its
#: `plus`, is still inside the take. The take's own sums (each step's at, the
#: length, the marks) are exact and held with no tolerance (ADR-016).
TOLERANCE = 1e-9
DRAWN = ('ring', 'arrow')
TRANSITIONS = ('dissolve', 'fade', 'wipe', 'slide', 'reframe')


def check_document(document, manifest=None, sources=None):
    """Refuse `document`, naming the chapter, the shot and the field, if it
    is not a valid movie document. `manifest`, the export's, lets part paths
    be checked; `sources`, excerpt name -> the excerpt's text, lets
    emphasised tokens be."""
    declared = document.get('format') if isinstance(document, dict) else None
    if declared != FORMAT:
        raise MovieError(f'Unsupported movie format: {declared}; this package writes and checks '
                         f'{FORMAT}')
    error = best_match(_VALIDATOR.iter_errors(document))
    if error is not None:
        raise MovieError(f'The movie document is invalid at {_where(document, error.absolute_path)}: '
                         f'{error.message}')
    _Semantics(document, manifest, sources or {}).check()


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


class _Semantics:
    def __init__(self, document, manifest, sources):
        self.document, self.sources, self.manifest = document, sources, manifest
        self.paths = None if manifest is None else _paths(manifest.get('root') or {})
        self.stage = document['stage']
        #: The take's length in take seconds, for a take document.
        self.length = None

    def check(self):
        document = self.document
        self.check_stage()
        self.check_take()
        chapters, shots = set(), {}
        film = [(chapter, shot) for chapter in document['chapters'] for shot in chapter['shots']]
        for chapter in document['chapters']:
            if chapter['id'] in chapters:
                raise MovieError(f"Chapter {chapter['id']} appears twice; chapter ids are unique")
            chapters.add(chapter['id'])
        for chapter, shot in film:
            if shot['id'] in shots:
                raise MovieError(f"Shot {shot['id']} appears in chapters {shots[shot['id']]} and "
                                 f"{chapter['id']}; shot ids are unique across a movie")
            shots[shot['id']] = chapter['id']
        for name, layer in document['layers'].items():
            for path in layer:
                self.path(path, f'layer {name}')
        index, previous = 0, None
        for chapter in document['chapters']:
            self.chapter(chapter)
            completed = set()
            for shot in chapter['shots']:
                self.shot(chapter, shot, completed, first=index == 0, last=index == len(film) - 1)
                self.reframe(previous, chapter, shot)
                previous = (chapter, shot)
                index += 1

    def reframe(self, previous, chapter, shot):
        """A reframe moves a view element the shot and the one before it both
        place; a view element belongs to its chapter. (A reframe on the film's
        first shot is refused with every join's, once the shots are timed.)"""
        if shot.get('transition', {}).get('kind') != 'reframe' or previous is None:
            return
        outgoing_chapter, outgoing = previous
        views = ({key for key, element in chapter['elements'].items() if element['kind'] == 'view'}
                 if outgoing_chapter is chapter else set())
        if not shared_views(outgoing, shot, views):
            raise MovieError(f"chapter {chapter['id']}, shot {shot['id']}, transition: "
                             f"{no_view_in_both(outgoing['id'], shot['id'])}")

    ##########################################
    # The stage block

    def check_stage(self):
        stage = self.stage
        seen = set()
        for module in stage['modules']:
            if module in seen:
                raise MovieError(f'stage.modules lists {module} twice')
            seen.add(module)
            if module.startswith('/') or not module.endswith(MODULE_SUFFIXES):
                raise MovieError(f'stage.modules: {module} is not a stage module; a module is a '
                                 f'TypeScript or JavaScript file (.ts, .tsx, .js or .jsx) relative '
                                 f'to root')
        for kind, entry in stage['sets'].items():
            where = f'stage.sets.{kind}'
            if len(set(entry['slots'])) != len(entry['slots']):
                raise MovieError(f'{where}: slots lists a slot twice')
            if 'module' not in entry:
                if kind not in SHIPPED_SETS:
                    raise MovieError(f'{where}: {kind} has no module and is not a set the tool ships '
                                     f'for movies (frame, split)')
                if entry['slots'] != SHIPPED_SETS[kind]:
                    raise MovieError(f"{where}: the shipped set {kind} has the slots "
                                     f"{', '.join(SHIPPED_SETS[kind])}, not {', '.join(entry['slots']) or 'none'}")
                if 'base' in entry:
                    raise MovieError(f'{where}: a set the tool ships has no base')
                continue
            if kind in SHIPPED_SETS or kind in EPISODE_SETS:
                raise MovieError(f'{where}: {kind} is a set the tool ships; a project set takes '
                                 f'another kind')
            self.module(entry['module'], where)
            base, chain = entry.get('base'), [kind]
            while base is not None:
                if base in chain:
                    raise MovieError(f"{where}: its base {base} derives from it "
                                     f"({' -> '.join(chain + [base])})")
                if base in SHIPPED_SETS and base not in stage['sets']:
                    break
                if base not in stage['sets']:
                    raise MovieError(f'{where}: its base {base} is neither a set of stage.sets nor '
                                     f'one the tool ships')
                chain.append(base)
                base = stage['sets'][base].get('base')
        for kind, entry in stage['elements'].items():
            where = f'stage.elements.{kind}'
            if kind in SHIPPED_ELEMENTS:
                raise MovieError(f'{where}: {kind} is an element the tool ships; a project element '
                                 f'takes another kind')
            self.module(entry['module'], where)

    def module(self, module, where):
        if module not in self.stage['modules']:
            raise MovieError(f'{where}: its module {module} is not listed in stage.modules')

    ##########################################
    # A clocked take (docs/movie-document.md, "The take")

    def check_take(self):
        document = self.document
        mode, take = document['model']['timeMode'], document.get('take')
        if mode not in TIME_MODES:
            raise MovieError(f"model.timeMode '{mode}' is not a time mode; a document films a "
                             f"normalized-loop or a take")
        if mode == 'normalized-loop':
            if take is not None:
                raise MovieError('take: a normalized-loop document carries no take block; a take '
                                 'block belongs to a document whose model.timeMode is take')
            return
        if take is None:
            raise MovieError('model.timeMode is take, and the take block is missing; a take '
                             'document carries the steps it films and what the machine did')
        drivers = known = None
        if self.manifest is not None:
            clocked = self.manifest.get('clocked')
            if not isinstance(clocked, dict):
                raise MovieError('model.timeMode is take, and the export publishes no clocked '
                                 'machine (its manifest has no clocked block)')
            if take['identity'] != clocked.get('identity'):
                raise MovieError(f"take.identity {take['identity']} differs from the machine the "
                                 f"export publishes, clocked.identity {clocked.get('identity')}; "
                                 f"the document was recorded against another machine")
            drivers = set(self.manifest.get('drivers') or {})
            if clocked.get('clock'):
                drivers.add(clocked['clock'])
            known = drivers | set(self.manifest.get('states') or {})
        # Take time is the exact sum of the written durations (ADR-016): each
        # step's at, the length and every mark are held to it with no
        # tolerance.
        seen, ends, total = {}, [], exact_seconds(0)
        for index, step in enumerate(take['steps']):
            here = f"take.steps[{index}] ({step['id']})"
            if step['id'] in seen:
                raise MovieError(f"{here}: the step id {step['id']} is used twice, by "
                                 f"take.steps[{seen[step['id']]}] and take.steps[{index}]")
            seen[step['id']] = index
            if ('to' in step) == ('by' in step):
                raise MovieError(f'{here}: a step has exactly one of to and by')
            if step['at'] != seconds_written(total):
                raise MovieError(f"{here}: at is {step['at']} s, and the steps before it end at "
                                 f"{seconds_written(total)} s; steps play end to end from 0")
            if drivers is not None and step['input'] not in drivers:
                raise MovieError(f"{here}: input '{step['input']}' is not a driver the export "
                                 f"declares ({', '.join(sorted(drivers)) or 'none'})")
            total += exact_seconds(step['duration'])
            ends.append(seconds_written(total))
        end = seconds_written(total)
        declared = document['model']['expectedDurationSeconds']
        if declared != end:
            raise MovieError(f"model.expectedDurationSeconds is {declared} s, and the take's steps "
                             f"end at {end} s; a take document lasts its take")
        initial = take['initial']
        if known is not None:
            # The identity is checked above, so a bank that is not the
            # machine's drivers and states is a damaged record, not another
            # machine's (ADR-011, amended).
            for name in sorted(known - set(initial)):
                raise MovieError(f"take.initial lacks '{name}', a driver or state of the machine "
                                 f"the export publishes; a take's bank holds every driver and state "
                                 f"of its machine and nothing else")
            for name in sorted(set(initial) - known):
                raise MovieError(f"take.initial holds '{name}', which is not a driver or state of "
                                 f"the machine the export publishes; a take's bank holds every "
                                 f"driver and state of its machine and nothing else")
        # The step each mark follows: -1 for the initial bank, at 0.
        follows = {}
        for name, seconds in document.get('marks', {}).items():
            if seconds == 0:
                follows[name] = -1
                continue
            index = next((i for i, at in enumerate(ends) if at == seconds), None)
            if index is None:
                raise MovieError(f'marks.{name}: {seconds} s is neither 0 nor the end of a step; a '
                                 f'mark of a take is the instant after the step before it')
            follows[name] = index
        banks = take['banks']
        for name in follows:
            if name not in banks:
                raise MovieError(f'take.banks: the bank of the mark {name} is missing; every mark '
                                 f'of a take has its recorded bank')
        for name in banks:
            if name not in follows:
                raise MovieError(f"take.banks: {name} is not one of the marks "
                                 f"({', '.join(follows) or 'none'})")
        # The replay: the bank before a step is the one the step before it
        # ended with; a step ends with its input at `end` and every commit's
        # targets written.
        bank, replayed = dict(initial), {-1: dict(initial)}
        for index, step in enumerate(take['steps']):
            bank[step['input']] = step['end']
            for commit in step['commits']:
                bank.update(commit['targets'])
            replayed[index] = dict(bank)
        missing = object()
        for name, index in follows.items():
            expected, recorded = replayed[index], banks[name]
            for key in sorted(set(expected) | set(recorded)):
                if expected.get(key, missing) != recorded.get(key, missing):
                    def shown(value):
                        return 'nothing' if value is missing else value
                    raise MovieError(f'take.banks.{name}: the bank recorded at the mark {name} '
                                     f'differs from the replay of the steps at {key}: recorded '
                                     f'{shown(recorded.get(key, missing))}, replayed '
                                     f'{shown(expected.get(key, missing))}')
        self.length = end

    ##########################################
    # Chapters and their elements

    def chapter(self, chapter):
        for key, element in chapter['elements'].items():
            self.element(chapter, key, element)

    def element(self, chapter, key, element):
        where = f"chapter {chapter['id']}, elements.{key}"
        kind = element['kind']
        fields = set(element) - {'kind'}
        if kind in SHIPPED_ELEMENTS:
            required, accepted = SHIPPED_ELEMENTS[kind]
        elif kind in self.stage['elements']:
            required, accepted = {'props'}, {'props'}
        else:
            raise MovieError(f"{where}: unknown element kind '{kind}'; a kind is view, source, "
                             f"title, picture or one of stage.elements")
        self.fields(where, f'a {kind} element', fields, required, accepted)
        if kind == 'view':
            self.known(element['camera'], 'cameras', where, 'camera')
            for layer in element.get('hide', []):
                self.known(layer, 'layers', where, 'layer')
        elif kind == 'source':
            self.known(element['source'], 'sourceCode', where, 'source excerpt')
        elif kind == 'picture':
            if ('still' in element) == ('clip' in element):
                raise MovieError(f'{where}: a picture shows one still or one clip')
            if 'still' in element:
                self.known(element['still'], 'stills', where, 'still')
                if 'inPoint' in element:
                    raise MovieError(f'{where}: inPoint belongs to a clip, not a still')
            else:
                self.known(element['clip'], 'clips', where, 'clip')
            if element.get('fit', 'contain') not in ('contain', 'cover'):
                raise MovieError(f"{where}: fit '{element['fit']}' must be contain or cover")
        elif kind not in SHIPPED_ELEMENTS:
            declared = self.stage['elements'][kind]['props']
            given = element['props']
            for name in sorted(set(declared) | set(given)):
                if name not in given:
                    raise MovieError(f'{where}: props: the {kind} element declares the prop {name}, '
                                     f'and it is missing')
                if name not in declared:
                    raise MovieError(f'{where}: props: {name} is not a prop the {kind} element '
                                     f'declares ({", ".join(declared) or "none"})')
                if prop_kind(given[name]) != declared[name]:
                    raise MovieError(f'{where}: props: {name} is a {prop_kind(given[name])}, and the '
                                     f'{kind} element declares it a {declared[name]}')

    def fields(self, where, what, fields, required, accepted):
        for field in sorted(fields - accepted):
            raise MovieError(f"{where}: {what} takes {', '.join(sorted(accepted)) or 'nothing'}, "
                             f"not {field}")
        for field in sorted(required - fields):
            raise MovieError(f'{where}: {what} needs {field}')

    def known(self, name, table, where, what):
        if name not in self.document.get(table, {}):
            raise MovieError(f"{where}: unknown {what} '{name}'")

    ##########################################
    # Shots

    def shot(self, chapter, shot, completed, first=True, last=True):
        where = f"chapter {chapter['id']}, shot {shot['id']}"
        narration = chapter['narration']
        sets = self.stage['sets']
        if shot['set'] not in sets:
            raise MovieError(f"{where}: unknown set '{shot['set']}'; the stage block declares the "
                             f"sets {', '.join(sets) or 'none'}")
        slots = sets[shot['set']]['slots']
        placed = {}
        for slot, key in shot['places'].items():
            if slot not in slots:
                raise MovieError(f"{where}, places.{slot}: the set {shot['set']} has no slot {slot}; "
                                 f"its slots are {', '.join(slots)}")
            if key not in chapter['elements']:
                raise MovieError(f"{where}, places.{slot}: the chapter does not declare the "
                                 f"element {key}")
            if key in placed.values():
                other = next(s for s, k in placed.items() if k == key)
                raise MovieError(f'{where}: the element {key} is placed in two slots, {other} and '
                                 f'{slot}; an element is in one place at a time')
            placed[slot] = key
        until = shot['until']
        if not isinstance(until, dict) and until <= 0:
            raise MovieError(f'{where}, until: the shot ends at or before its start (until {until})')
        if 'fadeIn' in shot and not first:
            raise MovieError(f"{where}: fadeIn is accepted only on the film's first shot")
        if 'fadeOut' in shot and not last:
            raise MovieError(f"{where}: fadeOut is accepted only on the film's last shot")
        self.joins(shot, where)
        for field, value in self.times(shot):
            # The end of the narration names no phrase to look for.
            if isinstance(value, dict) and 'narrationEnd' not in value:
                self.phrase(narration, value.get('spoken', value.get('spokenEnd')), where, field)
        self.model(shot, where)
        typed = {}
        for index, cue in enumerate(shot['cues']):
            self.cue(chapter, shot, placed, cue, f'{where}, cues[{index}]', typed, completed)
        for slot, key in placed.items():
            element = chapter['elements'][key]
            if element['kind'] == 'source' and key not in completed:
                last_line = self.document['sourceCode'][element['source']]['lines'][1]
                raise MovieError(f'{where}, places.{slot}: the source panel {key} is placed and not '
                                 f'complete: no typing of this shot or an earlier one of the '
                                 f'chapter reaches its last line, {last_line}')

    def joins(self, shot, where):
        for field in ('transition', 'fadeIn', 'fadeOut'):
            join = shot.get(field)
            if join is None:
                continue
            kind = join.get('kind')
            if field == 'transition' and kind not in TRANSITIONS:
                raise MovieError(f"{where}, transition.kind: '{kind}' is not a transition; use "
                                 f"dissolve, fade, wipe, slide or reframe")
            if field != 'transition' and kind not in (None, 'fade'):
                raise MovieError(f"{where}, {field}.kind: '{kind}' is not a fade")
            if 'direction' in join and (kind not in ('wipe', 'slide')
                                        or join['direction'] not in ('left', 'right')):
                raise MovieError(f"{where}, {field}.direction: a direction is left or right, on a "
                                 f"wipe or a slide")
            if 'color' in join and kind not in (None, 'fade'):
                raise MovieError(f'{where}, {field}.color: a colour belongs to a fade')
            self.ease(join.get('ease'), where, f'{field}.ease')

    def model(self, shot, where):
        model, marks = shot['model'], self.document.get('marks', {})
        for field, value in self.model_times(model):
            if isinstance(value, dict) and value['mark'] not in marks:
                declared = ', '.join(marks) or 'none'
                raise MovieError(f"{where}, {field}: unknown mark '{value['mark']}'; the "
                                 f"document's marks are {declared}")
            if self.length is not None:
                seconds = (marks[value['mark']] + value.get('plus', 0) if isinstance(value, dict)
                           else value)
                if not -TOLERANCE <= seconds <= self.length + TOLERANCE:
                    raise MovieError(f'{where}, {field}: take time {seconds} s is outside the take, '
                                     f'0 to {self.length} s')
        keys = model.get('keys')
        if keys is None:
            return
        if keys[0]['at'] != 0:
            raise MovieError(f"{where}, model.keys[0].at: model keys must start at the shot's "
                             f"start, with a first key at 0")
        if keys[-1]['at'] != shot['until']:
            raise MovieError(f"{where}, model.keys[{len(keys) - 1}].at: model keys must end at the "
                             f"shot's until, with a last key at the same time")
        for index, key in enumerate(keys):
            self.ease(key.get('ease'), where, f'model.keys[{index}].ease')

    ##########################################
    # Cues and actions

    def cue(self, chapter, shot, placed, cue, where, typed, completed):
        narration = chapter['narration']
        for number, action in enumerate(cue['actions']):
            here = f'{where}.actions[{number}]'
            key, name = action['element'], action['action']
            if key not in placed.values():
                raise MovieError(f'{here}: {name} acts on {key}, which the shot does not place')
            element = chapter['elements'][key]
            kind = element['kind']
            fields = set(action) - {'element', 'action'}
            if kind in ACTIONS:
                if name not in ACTIONS[kind]:
                    raise MovieError(f"{here}: the {kind} element has no action {name}; it has "
                                     f"{', '.join(ACTIONS[kind])}")
                required, accepted = ACTIONS[kind][name]
                self.fields(here, f'the action {name}', fields, required, accepted)
            else:
                declared = self.stage['elements'][kind]['actions']
                if name not in declared:
                    raise MovieError(f"{here}: the {kind} element has no action {name}; it declares "
                                     f"{', '.join(declared) or 'none'}")
                self.fields(here, f'the action {name}', fields, {'params'}, {'params'})
                self.params(here, kind, name, declared[name], action['params'])
            if name not in UNSPANNED and 'until' not in cue:
                raise MovieError(f"{where}: {name} shows something for a span and needs the cue's "
                                 f"until")
            if kind == 'view':
                self.view_action(action, here)
            elif kind == 'source' and name == 'type':
                self.typing(element, key, action, here, typed, completed)
            elif kind == 'source' and name == 'emphasize':
                self.emphasis(narration, element, cue, action, where, here)
            elif kind == 'title':
                self.entrances(action, here, name)
                self.reveal(narration, element, action.get('reveal'), here)
            elif kind == 'picture':
                self.entrances(action, here, name)
                for index, view in enumerate(action.get('view', [])):
                    self.ease(view.get('ease'), here, f'view[{index}].ease')

    def params(self, where, kind, name, declared, given):
        for param in sorted(set(declared) | set(given)):
            if param not in given:
                raise MovieError(f'{where}: params: the {kind} action {name} declares the '
                                 f'parameter {param}, and it is missing')
            if param not in declared:
                raise MovieError(f'{where}: params: {param} is not a parameter the {kind} action '
                                 f'{name} declares ({", ".join(declared) or "none"})')
            actual = prop_kind(given[param])
            if actual != declared[param]:
                raise MovieError(f'{where}: params: {param} is a {actual}, and the {kind} action '
                                 f'{name} declares it a {declared[param]}')

    def view_action(self, action, where):
        name = action['action']
        if name == 'move':
            self.known(action['camera'], 'cameras', where, 'camera')
            self.ease(action.get('ease'), where, 'ease')
            return
        if name == 'highlight':
            for part in action['parts']:
                self.part(part, where, 'parts')
            if action.get('others', 'keep') not in ('keep', 'dim', 'ghost'):
                raise MovieError(f"{where}: others '{action['others']}' must be keep, dim or ghost")
            return
        if name == 'arrow' and ('part' in action) == ('point' in action):
            raise MovieError(f'{where}: an arrow points at one part or one point')
        if 'part' in action:
            self.part(action['part'], where, 'part')
        self.entrances(action, where, name)

    def entrances(self, action, where, name):
        for field in ('enter', 'leave'):
            entrance = action.get(field)
            if entrance is None:
                continue
            kinds = ('fade', 'draw') if name in DRAWN and field == 'enter' else ('fade',)
            if entrance['kind'] not in kinds:
                raise MovieError(f"{where}, {field}.kind: '{entrance['kind']}' is not an "
                                 f"{'entrance' if field == 'enter' else 'exit'} of a {name}; use "
                                 f"{' or '.join(kinds)} (draw only on the entrance of a ring or an "
                                 f"arrow)")
            self.ease(entrance.get('ease'), where, f'{field}.ease')

    def typing(self, element, key, action, where, typed, completed):
        first, last = self.document['sourceCode'][element['source']]['lines']
        through = action['throughLine']
        if key in completed and key not in typed:
            raise MovieError(f'{where}: type: the source panel {key} was completed by an earlier '
                             f'shot of the chapter and is already typed; it keeps its text')
        if not first <= through <= last:
            raise MovieError(f'{where}: throughLine {through} is outside the excerpt '
                             f"{element['source']}, lines {first} to {last}")
        if key in typed and through <= typed[key]:
            raise MovieError(f'{where}: throughLine {through}: the panel {key} is already typed '
                             f'through line {typed[key]}; typing runs forward')
        typed[key] = through
        if through == last:
            completed.add(key)

    def emphasis(self, narration, element, cue, action, cue_where, where):
        at = cue['at']
        if not (isinstance(at, dict) and 'spoken' in at and 'plus' not in at):
            raise MovieError(f"{cue_where}.at: emphasize lights words where they are spoken, so "
                             f"the cue's at is a spoken phrase with no plus")
        phrase = at['spoken']
        excerpt = element['source']
        first, last = self.document['sourceCode'][excerpt]['lines']
        line = action.get('line')
        if line is not None and not first <= line <= last:
            raise MovieError(f'{where}, line: line {line} is outside the excerpt {excerpt}, '
                             f'lines {first} to {last}')
        for index, word in enumerate(action['words']):
            found = count_words(phrase, word['spoken'])
            if found != 1:
                state = 'absent from' if found == 0 else 'ambiguous in'
                raise MovieError(f"{where}, words[{index}].spoken: the spoken words "
                                 f"'{word['spoken']}' are {state} the cue's phrase '{phrase}' "
                                 f"(found {found} times as whole words)")
            token = word['token']
            if not TOKEN.fullmatch(token):
                raise MovieError(f"{where}, words[{index}].token: '{token}' is not a source token; "
                                 f"a token is an identifier or a dotted path")
            if excerpt in self.sources:
                text = (self.sources[excerpt] if line is None
                        else excerpt_line(self.sources[excerpt], first, line))
                found = count_token(text, token)
                if found != 1:
                    state = 'absent from' if found == 0 else 'ambiguous in'
                    place = f'the excerpt {excerpt}' if line is None else f'line {line} of the excerpt {excerpt}'
                    raise MovieError(f"{where}, words[{index}].token: the token '{token}' is "
                                     f"{state} {place} (found {found} times, bounded by anything "
                                     f"but a letter, a digit or an underscore)")

    def reveal(self, narration, element, reveal, where):
        if reveal is None:
            return
        if reveal['timing'] == 'spoken':
            phrase = reveal.get('phrase', element['text'])
            if phrase.split() != element['text'].split():
                raise MovieError(f"{where}, reveal.phrase: '{phrase}' does not match the title's "
                                 f"text '{element['text']}' word for word")
            self.phrase(narration, phrase, where, 'reveal.phrase')
            if 'duration' in reveal or 'ease' in reveal:
                raise MovieError(f'{where}, reveal: a spoken reveal takes no duration or ease')
        elif reveal['timing'] == 'even':
            if not reveal.get('duration', 0) > 0:
                raise MovieError(f'{where}, reveal.duration: an even reveal needs a duration')
            if 'phrase' in reveal:
                raise MovieError(f'{where}, reveal.phrase: an even reveal is not spoken')
            self.ease(reveal.get('ease'), where, 'reveal.ease')
        else:
            raise MovieError(f"{where}, reveal.timing: '{reveal['timing']}' must be spoken or even")

    ##########################################
    # Shared rules

    def ease(self, name, where, field):
        if name is not None and name not in EASES:
            raise MovieError(f"{where}, {field}: unknown easing '{name}'; use linear, smooth, in, "
                             f"out or in-out")

    def phrase(self, narration, phrase, where, field):
        found = count_phrase(narration, phrase)
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
        """Every time of the shot that may be an anchor, by its field."""
        yield 'until', shot['until']
        for index, key in enumerate(shot['model'].get('keys', [])):
            yield f'model.keys[{index}].at', key['at']
        for index, cue in enumerate(shot['cues']):
            yield f'cues[{index}].at', cue['at']
            if 'until' in cue:
                yield f'cues[{index}].until', cue['until']
            for number, action in enumerate(cue['actions']):
                if 'until' in action:
                    yield f'cues[{index}].actions[{number}].until', action['until']
                for key_index, key in enumerate(action.get('view', [])):
                    yield f'cues[{index}].actions[{number}].view[{key_index}].at', key['at']

    @staticmethod
    def model_times(model):
        if 'keys' in model:
            for index, key in enumerate(model['keys']):
                yield f'model.keys[{index}].seconds', key['seconds']
        else:
            yield 'model.from', model['from']
            yield 'model.to', model['to']


def _paths(root):
    paths = set()

    def walk(node, path):
        paths.add(tuple(path))
        for child in node.get('children') or []:
            walk(child, path + [child.get('name')])
    walk(root, [])
    return paths
