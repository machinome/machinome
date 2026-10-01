"""The movie tree: a movie orders chapters; a chapter owns its narration,
declares the elements its shots place, and orders its shots; a shot places
elements in the slots of one set for a span of time, with cues of actions.

Everything is found by type in declaration order and named by the
attribute that holds it. A chapter checks itself when its class is
created, where every class involved is known, and compiles its shots to
their document form there; evaluation adds only what needs a file: the
export's part paths, the excerpts an emphasis lights, the stage modules.
"""

from .anchors import Anchor, Narration, time_document, time_value
from .names import MovieError, no_view_in_both, prop_kind, shared_views, slug
from .stage import (Cued, Element, FadeIn, FadeOut, Placement, Reframe, Set, SourcePanel,
                    Style, Title, Transition, View, check_camera)
from .take import Simulation, part_path
from .text import count_phrase, count_words


class Cue:
    """At `anchor`, do these actions, optionally until another anchor."""

    def __init__(self, anchor, *actions, until=None):
        if not actions or not all(isinstance(action, Cued) for action in actions):
            raise MovieError(f'A Cue performs actions of elements, as view.highlight(...), '
                             f'not {actions!r}')
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
        elements = {name: value for name, value in body.items() if isinstance(value, Element)}
        shots = [(name, value) for name, value in body.items() if isinstance(value, Shot)]
        cls._compiled = _Compiler(cls, narrations[0], elements, shots).compile()

    def __init__(self):
        pass


class _Compiler:
    """Checks a chapter and writes it in document form."""

    def __init__(self, chapter, narration, elements, shots):
        self.chapter, self.narration = chapter, narration
        self.elements, self.shots = elements, shots
        self.keys = {}
        self.parts = []      # (where, written, names) for the export check
        self.loops = []      # (where, loop) for the one-take check
        self.tokens = []     # (where, source, token) for the excerpt check
        self.sets = []       # the set classes the shots use, in order
        self.completed = set()   # the source panels typed through their last line
        self.written = []    # the shots compiled so far, in document form
        self.views = set()   # the keys of the chapter's view elements

    def compile(self):
        cname = self.chapter.__name__
        declared = {}
        for name, element in self.elements.items():
            where = f'{cname}.{name}'
            key = slug(name, where, 'element')
            element.check(where)
            if element.loop is not None:
                self.loops.append((where, element.loop))
            self.keys[id(element)] = key
            declared[key] = element.document()
            if isinstance(element, View):
                self.views.add(key)
        for name, shot in self.shots:
            self.written.append(self.shot(name, shot))
        written = self.written
        project = [(self.keys[id(e)], e) for e in self.elements.values() if e.project()]
        return {'narration': self.narration.text, 'elements': declared, 'shots': written,
                'parts': self.parts, 'loops': self.loops, 'tokens': self.tokens,
                'sets': self.sets, 'project': project}

    def anchor(self, value, where):
        if isinstance(value, Anchor):
            value.check(self.narration, where)
        return value

    def part(self, model, part, where):
        written, names = part_path(model, part, where)
        self.parts.append((where, written, names))
        return names

    def shot(self, name, shot):
        where = f'{self.chapter.__name__}.{name}'
        shot_id = slug(name, where, 'shot')
        chosen = shot.set
        if not (isinstance(chosen, type) and issubclass(chosen, Set) and chosen is not Set):
            raise MovieError(f'{where}: {chosen!r} is not a set; a shot is on Frame, Split or a '
                             f'Set the project declares')
        if chosen not in self.sets:
            self.sets.append(chosen)
        placed = self.placements(shot, chosen, where)
        until = self.anchor(time_value(shot.until, f'{where}: until'), f'{where}: until')
        if not isinstance(shot.model, Simulation):
            raise MovieError(f'{where}: the shot has no model time; give it '
                             f'model=<take>.run(start, end) or model=<take>.keys({{...}}), on '
                             f'its Loop or Take')
        shot.model.check(until, self.narration, where)
        self.loops.append((f'{where}: model', shot.model.loop))

        cues = []
        typed = {}
        for index, cue in enumerate(shot.cues):
            here = f'{where}: cues[{index}]'
            if not isinstance(cue, Cue):
                raise MovieError(f'{here}: {cue!r} is not a Cue')
            start = self.anchor(cue.anchor, f'{here}.at')
            end = None if cue.until is None else self.anchor(cue.until, f'{here}.until')
            actions = [self.action(action, placed, start, end, here, typed)
                       for action in cue.actions]
            written = {'at': time_document(start), 'actions': actions}
            if end is not None:
                written['until'] = time_document(end)
            cues.append(written)
        for slot, element in placed.items():
            if isinstance(element, SourcePanel) and id(element) not in self.completed:
                name = self.keys[id(element)]
                last = element.source.lines[1]
                raise MovieError(f'{where}: the shot places the source panel {name} in {slot} and '
                                 f'does not complete it: no earlier shot of the chapter typed it '
                                 f'through its last line, {last}; add '
                                 f'Cue(0, {name}.type(through_line={last}, over=...))')

        document = {'id': shot_id, 'set': chosen.kind,
                    'places': {slot: self.keys[id(element)] for slot, element in placed.items()},
                    'until': time_document(until), 'model': shot.model.document(), 'cues': cues}
        for key, value, kind in (('transition', shot.transition, Transition),
                                 ('fadeIn', shot.fade_in, FadeIn),
                                 ('fadeOut', shot.fade_out, FadeOut)):
            if value is not None:
                if not isinstance(value, kind):
                    raise MovieError(f'{where}: {key} is a {kind.__name__}, not {value!r}')
                document[key] = value.document()
        # A reframe moves a view element both shots place; the shot before
        # this one is known here when it is the chapter's own (a chapter's
        # first shot is the movie's to check).
        if isinstance(shot.transition, Reframe) and self.written:
            prior = self.written[-1]
            if not shared_views(prior, document, self.views):
                raise MovieError(f"{where}: transition: {no_view_in_both(prior['id'], shot_id)}")
        return document

    def action(self, action, placed, start, end, here, typed):
        element = action.element
        if not any(element is candidate for candidate in placed.values()):
            name = self.keys.get(id(element), f'a {element.kind} the chapter does not declare')
            raise MovieError(f'{here}: {action.name} acts on {name}, which the shot does not place')
        key = self.keys[id(element)]
        if action.spans and end is None:
            raise MovieError(f"{here}: {action.name} shows something for a span and needs the "
                             f"cue's until=")
        written = {'element': key, 'action': action.name}
        if action.params is not None:
            written['params'] = dict(action.params)
            return written
        fields = dict(action.fields)
        if action.name == 'move':
            check_camera(fields['camera'], element.loop, f'{here}: move')
            fields['camera'] = fields['camera'].document_name()
            fields['until'] = time_document(self.anchor(fields['until'], f'{here}: move until'))
        elif action.name == 'highlight':
            fields['parts'] = [self.part(element.loop.model, part, f'{here}: highlight')
                               for part in fields['parts']]
        elif action.name in ('ring', 'label', 'arrow'):
            fields['part'] = self.part(element.loop.model, fields['part'], f'{here}: {action.name}')
        elif action.name == 'type':
            self.type(element, fields['throughLine'], key, here, typed)
        elif action.name == 'emphasize':
            self.emphasize(element, fields['words'], start, here, fields.get('line'))
        elif action.name == 'show' and isinstance(element, Title) and 'reveal' in fields:
            found = count_phrase(self.narration.text, element.text)
            if found != 1:
                state = 'absent from' if found == 0 else 'ambiguous in'
                raise MovieError(f"{here}: show: the title's text '{element.text}' is {state} the "
                                 f"chapter's narration (found {found} times); a spoken reveal shows "
                                 f"each word as it is spoken, so the narration says the title once")
        elif action.name == 'show' and 'view' in fields:
            fields['view'] = [{**view, 'at': time_document(self.anchor(view['at'],
                                                                       f'{here}: show view[{n}]'))}
                              for n, view in enumerate(fields['view'])]
        written.update(fields)
        return written

    def type(self, panel, through, name, here, typed):
        first, last = panel.source.lines
        if id(panel) in self.completed and id(panel) not in typed:
            raise MovieError(f'{here}: type: the source panel {name} is already typed through its '
                             f'last line by an earlier shot of the chapter; it keeps its text')
        if not first <= through <= last:
            raise MovieError(f'{here}: type: through_line={through} is outside the excerpt, lines '
                             f'{first} to {last}')
        before = typed.get(id(panel))
        if before is not None and through <= before:
            raise MovieError(f'{here}: type: through_line={through}, and the panel {name} is '
                             f'already typed through line {before}; typing runs forward')
        typed[id(panel)] = through
        if through == last:
            self.completed.add(id(panel))

    def emphasize(self, panel, words, start, here, line=None):
        if not (isinstance(start, Anchor) and start.kind == 'spoken' and not start.plus):
            raise MovieError(f"{here}: emphasize lights words where they are spoken, so the cue's "
                             f"anchor must be a spoken phrase, lines.spoken(...), with no plus")
        for word in words:
            found = count_words(start.phrase, word['spoken'])
            if found != 1:
                state = 'absent from' if found == 0 else 'ambiguous in'
                raise MovieError(f"{here}: emphasize: the spoken words '{word['spoken']}' are "
                                 f"{state} the cue's phrase '{start.phrase}' (found {found} times "
                                 f"as whole words)")
            self.tokens.append((here, panel.source, word['token'], line))

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
                declared = ', '.join(slots) or 'none'
                raise MovieError(f'{where}: {slot.name} is a slot of {slot.set.__name__}, not of '
                                 f'{chosen.__name__}, whose slots are {declared}')
            if slot.name in placed:
                raise MovieError(f'{where}: slot {slot.name} of {chosen.__name__} is filled twice')
            if not any(element is declared for declared in self.elements.values()):
                raise MovieError(f'{where}: slot {slot.name} holds an element the chapter '
                                 f'{self.chapter.__name__} does not declare; declare it on the '
                                 f'chapter and place it by name')
            for other, held in placed.items():
                if held is element:
                    raise MovieError(f'{where}: the element {self.keys[id(element)]} is placed in '
                                     f'two slots, {other} and {slot.name}; an element is in one '
                                     f'place at a time')
            placed[slot.name] = element
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
                            (Style, 'Style(...)'), (Evidence, 'Evidence(...)'),
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
        _check_props(where, ordered)
        _check_reframes(where, ordered)
        cls._movie = {'chapters': ordered, 'text': text, 'found': found}


def _check_reframes(where, chapters):
    """A chapter's first shot comes in from the last shot of the chapter
    before; a view element belongs to its chapter, so the two never place
    one in both and a reframe between them is refused. (A reframe between
    two shots of one chapter was checked when the chapter was created.)"""
    previous = None
    for chapter_id, klass in chapters:
        shots = klass._compiled['shots']
        first = shots[0] if shots else None
        if previous is not None and first and first.get('transition', {}).get('kind') == 'reframe':
            raise MovieError(f"{where}: chapter {chapter_id}, shot {first['id']}, transition: "
                             f"{no_view_in_both(previous[1], first['id'])}: shot {previous[1]} "
                             f"is chapter {previous[0]}'s, and a view element belongs to its "
                             f"chapter")
        if shots:
            previous = (chapter_id, shots[-1]['id'])


def _check_props(where, chapters):
    """Every element of one project kind gives the same props, of the same
    kinds, so the kind's generated types are one."""
    first = {}
    for chapter_id, klass in chapters:
        for key, element in klass._compiled['project']:
            kinds = {name: prop_kind(value) for name, value in element.props.items()}
            if element.kind not in first:
                first[element.kind] = (chapter_id, key, kinds)
                continue
            there, other, known = first[element.kind]
            for name in sorted(set(kinds) | set(known)):
                if kinds.get(name) != known.get(name):
                    def said(chapter, element_key, kind):
                        how = f'as a {kind}' if kind else 'not at all'
                        return f'{element_key} in chapter {chapter} gives {name} {how}'
                    raise MovieError(
                        f"{where}: the {element.kind} elements disagree on their props: "
                        f"{said(there, other, known.get(name))}, {said(chapter_id, key, kinds.get(name))}; "
                        f"every {element.kind} of a movie gives the same props, of the same kinds")
