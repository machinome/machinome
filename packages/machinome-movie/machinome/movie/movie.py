"""The movie tree: a movie orders chapters; a chapter owns its narration,
declares the elements its shots place, and orders its shots; a shot puts
elements in the slots of one set for a span of time, with cues.

Everything is found by type in declaration order and named by the
attribute that holds it. A chapter checks itself when its class is
created, where every class involved is known, and compiles its shots to
their document form there; evaluation adds only what needs the export.
"""

from .anchors import Anchor, Narration, is_zero, time_document, time_value
from .names import MovieError, number, slug
from .stage import (Emphasize, FadeIn, FadeOut, Highlight, Move, Picture, Placement,
                    Set, SourcePanel, Style, Title, Transition, Type, View,
                    _Annotation, _check_camera)
from .take import Simulation, part_path


class Cue:
    """At `anchor`, do these actions, optionally until another anchor."""

    def __init__(self, anchor, *actions, until=None):
        from .stage import Action

        if not actions or not all(isinstance(action, Action) for action in actions):
            raise MovieError(f'A Cue performs actions, not {actions!r}')
        self.anchor = time_value(anchor, 'Cue')
        self.actions, self.until = actions, None if until is None else time_value(until, 'Cue until')


class Shot:
    """One continuous composition on one set."""

    def __init__(self, set, placements, *, until, model=None, cues=(), transition=None,
                 fade_in=None, fade_out=None):
        self.set, self.placements, self.until, self.model = set, placements, until, model
        self.cues, self.transition = list(cues), transition
        self.fade_in, self.fade_out = fade_in, fade_out


def _scan(cls, base):
    """Every attribute of `cls`'s own and inherited bodies below `base`, in
    declaration order, later bodies overriding earlier ones."""
    found = {}
    for klass in reversed(cls.__mro__):
        if klass is base or not issubclass(klass, base):
            continue
        for name, value in vars(klass).items():
            if not name.startswith('_'):
                found[name] = value
    return found


class Chapter:
    """An ordered part of a movie that owns its narration."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        body = _scan(cls, Chapter)
        narrations = [value for value in body.values() if isinstance(value, Narration)]
        if len(narrations) != 1:
            raise MovieError(f'Chapter {cls.__name__} needs exactly one Narration; it '
                             f'declares {len(narrations)}')
        elements = {name: value for name, value in body.items()
                    if isinstance(value, (View, SourcePanel))}
        shots = [(name, value) for name, value in body.items() if isinstance(value, Shot)]
        cls._compiled = _Compiler(cls, narrations[0], elements, shots).compile()

    def __init__(self):
        pass


class _Compiler:
    """Checks a chapter and writes its shots in document form."""

    def __init__(self, chapter, narration, elements, shots):
        self.chapter, self.narration = chapter, narration
        self.elements, self.shots = elements, shots
        self.names = {id(element): name for name, element in elements.items()}
        self.parts = []      # (where, written, names) for the export check
        self.loops = []      # (where, loop) for the one-take check

    def compile(self):
        cname = self.chapter.__name__
        views = [e for e in self.elements.values() if isinstance(e, View)]
        for name, element in self.elements.items():
            where = f'{cname}.{name}'
            if isinstance(element, View):
                element.check(where)
            self.loops.append((where, element.loop))
        cameras = {id(view): view.camera for view in views}
        written = []
        for name, shot in self.shots:
            written.append(self.shot(name, shot, views, cameras))
        return {'narration': self.narration.text, 'shots': written,
                'parts': self.parts, 'loops': self.loops}

    def anchor(self, value, where):
        if isinstance(value, Anchor):
            value.check(self.narration, where)
        return value

    def part(self, model, part, where):
        written, names = part_path(model, part, where)
        self.parts.append((where, written, names))
        return names

    def shot(self, name, shot, views, cameras):
        where = f'{self.chapter.__name__}.{name}'
        shot_id = slug(name, where, 'shot')
        chosen = shot.set
        if not (isinstance(chosen, type) and issubclass(chosen, Set) and chosen.kind):
            raise MovieError(f'{where}: {chosen!r} is not a set; use Paper, PaperSplit or SourceOnly')
        placed = self.placements(shot, chosen, where)
        until = self.anchor(time_value(shot.until, f'{where}: until'), f'{where}: until')
        if not isinstance(shot.model, Simulation):
            raise MovieError(f'{where}: the shot has no model time; give it '
                             f'model=<Loop>.run(start, end) or model=<Loop>.keys({{...}})')
        shot.model.check(until, self.narration, where)
        self.loops.append((f'{where}: model', shot.model.loop))

        view = next((e for e in placed.values() if isinstance(e, View)), None)
        posed = view
        if posed is None:
            if len(views) != 1:
                raise MovieError(f'{where}: the shot places no view and is still posed; it '
                                 f'poses the chapter\'s view, so the chapter must declare '
                                 f'exactly one view (it declares {len(views)})')
            posed = views[0]
        panel = next((e for e in placed.values() if isinstance(e, SourcePanel)), None)

        document = {'id': shot_id, 'set': chosen.kind, 'until': time_document(until),
                    'simulation': shot.model.document()}
        camera = cameras[id(posed)]
        keys = [{'at': 0, 'preset': camera.document_name()}]
        overlays, annotations, highlight, pictures = [], [], [], []
        typing, emphasis = [], []
        for index, cue in enumerate(shot.cues):
            here = f'{where}: cues[{index}]'
            if not isinstance(cue, Cue):
                raise MovieError(f'{here}: {cue!r} is not a Cue')
            start = self.anchor(cue.anchor, here)
            end = None if cue.until is None else self.anchor(cue.until, f'{here}.until')
            for action in cue.actions:
                if action.element is not None and not any(
                        action.element is element for element in placed.values()):
                    element = self.names.get(id(action.element), 'an element')
                    raise MovieError(f'{here}: {action.label} acts on {element}, which the '
                                     f'shot does not place')
                if action.spans and end is None:
                    raise MovieError(f'{here}: {action.label} shows something for a span '
                                     f'and needs the cue\'s until=')
                if isinstance(action, Move):
                    _check_camera(action.camera, view.loop, f'{here}: move')
                    target = action.camera.document_name()
                    finish = self.anchor(action.until, f'{here}: move until')
                    if not is_zero(start) and keys[-1]['at'] != time_document(start):
                        keys.append({'at': time_document(start), 'preset': keys[-1]['preset']})
                    key = {'at': time_document(finish), 'preset': target}
                    if action.ease is not None:
                        key['ease'] = action.ease
                    keys.append(key)
                    camera = action.camera
                elif isinstance(action, Highlight):
                    parts = [self.part(view.loop.model, part, f'{here}: highlight')
                             for part in action.parts]
                    written = {'from': time_document(start), 'to': time_document(end),
                               'parts': parts}
                    if action.others is not None:
                        written['others'] = action.others
                    highlight.append(written)
                elif isinstance(action, _Annotation):
                    if view is None:
                        raise MovieError(f'{here}: a {action.label} points at a part of the '
                                         f'model, and the shot places no view')
                    part = self.part(view.loop.model, action.part, f'{here}: {action.label}')
                    annotations.append(action.document(time_document(start),
                                                       time_document(end), part))
                elif isinstance(action, Title):
                    overlays.append(action.document(time_document(start), time_document(end)))
                elif isinstance(action, Type):
                    stop = start.shifted(action.over) if isinstance(start, Anchor) else start + action.over
                    typing.append({'from': time_document(start), 'to': time_document(stop),
                                   'throughLine': action.through_line})
                elif isinstance(action, Emphasize):
                    if not (isinstance(start, Anchor) and start.kind == 'spoken' and not start.plus):
                        raise MovieError(f'{here}: emphasize lights words where they are spoken, '
                                         f'so the cue\'s anchor must be a spoken phrase '
                                         f'(lines.spoken(...)) with no plus')
                    emphasis.append({'line': action.element.source.lines[1],
                                     'phrase': start.phrase, 'words': action.words,
                                     'hold': action.hold})
                elif isinstance(action, Picture):
                    self.loops.append((f'{here}: show', action.still.loop))
                    written = {'from': time_document(start), 'to': time_document(end),
                               'still': action.still.document_name()}
                    for key in ('area', 'fit', 'enter', 'leave'):
                        if getattr(action, key) is not None:
                            written[key] = getattr(action, key)
                    if action.view:
                        written['view'] = []
                        for number_, key in enumerate(action.view):
                            at = self.anchor(key['at'], f'{here}: show view[{number_}]')
                            written['view'].append({**key, 'at': time_document(at)})
                    pictures.append(written)
        cameras[id(posed)] = camera

        if panel is not None:
            if not typing:
                name = self.names[id(panel)]
                raise MovieError(f'{where}: the shot places the source panel {name} and no '
                                 f'cue types it; add Cue(0, {name}.type(through_line=..., over=...))')
            code = {'snippet': panel.source.document_name(), 'typing': typing}
            if emphasis:
                code['emphasis'] = emphasis
            document['code'] = code
        document['camera'] = keys
        document['hiddenLayers'] = [layer.document_name() for layer in posed.hide]
        document['overlays'] = overlays
        document['evidence'] = []
        for key, value in (('annotations', annotations), ('highlight', highlight),
                           ('pictures', pictures)):
            if value:
                document[key] = value
        for key, value, kind in (('transition', shot.transition, Transition),
                                 ('fadeIn', shot.fade_in, FadeIn),
                                 ('fadeOut', shot.fade_out, FadeOut)):
            if value is not None:
                if not isinstance(value, kind):
                    raise MovieError(f'{where}: {key} is a {kind.__name__}, not {value!r}')
                document[key] = value.document()
        return document

    def placements(self, shot, chosen, where):
        if not isinstance(shot.placements, dict):
            raise MovieError(f'{where}: place elements as {{{chosen.__name__}.<slot>: element}}')
        slots = chosen.slots()
        placed = {}
        for key, element in shot.placements.items():
            if not isinstance(key, Placement):
                raise MovieError(f'{where}: {key!r} is not a slot; write {chosen.__name__}.<slot>')
            slot = key.slot
            if slot.set is not chosen:
                raise MovieError(f'{where}: {slot.name} is a slot of {slot.set.__name__}, not of '
                                 f'{chosen.__name__}, whose slots are {", ".join(slots)}')
            if slot.name in placed:
                raise MovieError(f'{where}: slot {slot.name} of {chosen.__name__} is filled twice')
            if not any(element is declared for declared in self.elements.values()):
                raise MovieError(f'{where}: slot {slot.name} holds an element the chapter '
                                 f'{self.chapter.__name__} does not declare; declare it on the '
                                 f'chapter and place it by name')
            if element.slot_kind != slot.holds:
                wanted = {'view': 'view', 'panel': 'source panel'}
                raise MovieError(f'{where}: slot {slot.name} of {chosen.__name__} holds a '
                                 f'{wanted[slot.holds]}, not a {wanted[element.slot_kind]}')
            placed[slot.name] = element
        for name in slots:
            if name not in placed:
                raise MovieError(f'{where}: slot {name} of {chosen.__name__} is empty')
        return placed


##############################################
# The movie and what it declares once

class Format:
    """Output geometry and rate."""

    def __init__(self, width, height, *, fps):
        for name, value in (('width', width), ('height', height), ('fps', fps)):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise MovieError(f'Format: {name}={value!r} is not a positive whole number')
        self.width, self.height, self.fps = width, height, fps

    def document(self):
        return {'width': self.width, 'height': self.height, 'fps': self.fps}


class Narrator:
    """The voice every chapter's narration is spoken in."""

    def __init__(self, *, provider, model, voice, label=None, output=None, settings=None,
                 direction=None):
        for name, value in (('provider', provider), ('model', model), ('voice', voice)):
            if not isinstance(value, str) or not value:
                raise MovieError(f'Narrator: {name} is required, not {value!r}')
        if settings is not None and not isinstance(settings, dict):
            raise MovieError(f'Narrator: settings={settings!r} is not a mapping')
        self.fields = {'provider': provider, 'model': model, 'voice': voice,
                       'voiceLabel': label, 'outputFormat': output,
                       'voiceSettings': None if settings is None else dict(settings),
                       'direction': direction}

    def document(self):
        return {key: value for key, value in self.fields.items() if value is not None}


class _Paths:
    """A declaration of named files, relative to the movie's file."""

    def __init__(self, **paths):
        for name, path in paths.items():
            if path is not None and (not isinstance(path, str) or not path):
                raise MovieError(f'{type(self).__name__}: {name}={path!r} is not a path')
        self.paths = paths


class Evidence(_Paths):
    """Readable names for the project files that support the film's claims."""


class Credits:
    """Who made what, for the upload description; never drawn in the film."""

    def __init__(self, *, project=None, creator=None, copyright=None, license=None,
                 license_file=None):
        self.fields = {'project': project, 'creator': creator, 'copyright': copyright,
                       'license': license}
        self.license_file = license_file


class Release:
    """The public addresses and the description template of a release.
    `None` addresses are unresolved and block a release, never invented."""

    def __init__(self, *, simulation_url=None, source_url=None, description):
        if not isinstance(description, str) or not description:
            raise MovieError(f'Release: description is the template path, not {description!r}')
        self.simulation_url, self.source_url, self.description = simulation_url, source_url, description


class Movie:
    """The work: ordered chapters, one format, one narrator."""

    _TEXT = (('title', 'title', True), ('series', 'series', False),
             ('status', 'status', True), ('learning_goal', 'learningGoal', True))

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        where = f'Movie {cls.__name__}'
        body = _scan(cls, Movie)
        chapters = [(name, value) for name, value in body.items() if isinstance(value, Chapter)]
        if not chapters:
            raise MovieError(f'{where} declares no Chapter; hold each as an attribute, '
                             f'name = MyChapter()')
        found = {}
        for kind, label in ((Format, 'Format(width, height, fps=...)'), (Narrator, 'Narrator(...)'),
                            (Style, 'Paper.style(...)'), (Evidence, 'Evidence(...)'),
                            (Credits, 'Credits(...)'), (Release, 'Release(...)')):
            held = [value for value in body.values() if isinstance(value, kind)]
            if len(held) > 1:
                raise MovieError(f'{where} declares {len(held)} of {label}; it takes one')
            found[kind] = held[0] if held else None
        for kind, label in ((Format, 'a Format(width, height, fps=...)'), (Narrator, 'a Narrator(...)')):
            if found[kind] is None:
                raise MovieError(f'{where} needs {label}')
        text = {}
        for attribute, field, required in cls._TEXT:
            value = getattr(cls, attribute, None)
            if value is None and not required:
                continue
            if not isinstance(value, str) or not value.strip():
                raise MovieError(f'{where} needs {attribute} as text')
            text[field] = value
        seen = {}
        ordered = []
        for name, chapter in chapters:
            chapter_id = slug(name, f'{where}.{name}', 'chapter')
            for shot in type(chapter)._compiled['shots']:
                if shot['id'] in seen:
                    raise MovieError(f"{where}: shot {shot['id']} appears in chapters "
                                     f"{seen[shot['id']]} and {chapter_id}; shot ids are unique "
                                     f"across a movie")
                seen[shot['id']] = chapter_id
            ordered.append((chapter_id, type(chapter)))
        cls._movie = {'chapters': ordered, 'text': text, 'found': found}
