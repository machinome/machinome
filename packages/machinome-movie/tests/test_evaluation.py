"""Layer 1: a movie evaluates to the machinome-movie/0.2 document, twice
identically, opening nothing but the export's manifest and source revision
and the excerpts an emphasis lights.

The mapping assertions read the tour fixture movie, which uses every
construct the validation film uses; each assertion names the construct.
"""

import builtins
import io
import json
import random
import shutil
import socket
import time
from pathlib import Path

import pytest

from machinome_movie import (Action, Camera, Chapter, Cue, Element, Fade, Format, Frame, Loop,
                             Movie, MovieError, Narration, Narrator, Set, Shot, Slide, Slot,
                             Source, Split, View, dumps, evaluate)

from models.seesaw import Seesaw
from videos.minimal.movie import Minimal
from videos.takes import Playground
from videos.tour.movie import Tour

from conftest import PROJECT

EXPORT = PROJECT / 'export' / 'seesaw'
SOURCE = PROJECT / 'models' / 'seesaw.py'


@pytest.fixture(scope='module')
def tour():
    return evaluate(Tour, name='tour')


def chapter(document, chapter_id):
    return next(c for c in document['chapters'] if c['id'] == chapter_id)


def shot(document, shot_id):
    for candidate in (s for c in document['chapters'] for s in c['shots']):
        if candidate['id'] == shot_id:
            return candidate
    raise KeyError(shot_id)


def test_top_level(tour):
    assert tour['format'] == 'machinome-movie/0.2'
    assert tour['id'] == 'tour'
    assert tour['title'] == 'Tour'
    assert tour['series'] == 'VIDEOMAKER · FIXTURES'
    assert tour['status'] == 'rehearsal'
    assert tour['learningGoal'] == 'Exercise every construct the validation film uses.'
    assert tour['root'] == '..'
    assert tour['output'] == {'width': 1280, 'height': 720, 'fps': 30}
    assert [c['id'] for c in tour['chapters']] == ['opening', 'balance', 'tip']


def test_model_block_and_paths_relative_to_root(tour):
    revision = (EXPORT / 'source-revision.txt').read_text().strip()
    assert tour['model'] == {
        'manifest': '../../export/seesaw/manifest.json',
        'expectedDurationSeconds': 20,
        'timeMode': 'normalized-loop',
        'sourceRevision': revision,
        'readiness': 'Fixture export written by hand; nothing is simulated.'}
    assert tour['marks'] == {'rise': 5, 'top': 10, 'fall': 15}
    assert tour['sourceCode'] == {'declaration': {'file': '../../models/seesaw.py', 'lines': [22, 24]}}
    assert tour['stills'] == {'plate': {'file': '../../media/plate.png',
                                        'credit': 'Fixture drawing of a seesaw',
                                        'rights': 'Made for the Videomaker test suite',
                                        'upscale': 1.5}}
    assert tour['clips'] == {}
    assert tour['evidence'] == {'model': '../../models/seesaw.py'}


def test_cameras_layers_names_are_slugs(tour):
    assert tour['cameras']['far'] == {'position': [400, -600, 300], 'target': [0, 0, 50],
                                      'up': [0, 0, 1], 'fov': 37}
    assert tour['cameras']['rolled']['up'] == [0.15, 0, 1]
    assert set(tour['cameras']) == {'far', 'near', 'side', 'rolled'}
    assert tour['layers'] == {'ground': [['Base']], 'load': [['Beam', 'Plank'], ['Beam', 'Weight']]}


def test_production_blocks(tour):
    assert tour['audio'] == {'provider': 'elevenlabs', 'model': 'eleven_v3', 'voice': 'fixture-voice',
                             'voiceLabel': 'Fixture', 'outputFormat': 'pcm_24000',
                             'voiceSettings': {'stability': 0.5, 'similarity_boost': 0.75},
                             'direction': 'Plain and unhurried.'}
    assert tour['style'] == {'background': '#faf7ef', 'foreground': '#222222', 'accent': '#237c86',
                             'fontFamily': 'DejaVu Sans, sans-serif', 'safeInsetFraction': 0.08}
    assert tour['credits'] == {'project': 'Videomaker fixtures', 'creator': 'The Videomaker test suite',
                               'copyright': 'No copyright is claimed for this fixture',
                               'license': 'None', 'licenseFile': '../../NOTICE'}
    assert tour['release'] == {'simulationUrl': None, 'sourceUrl': None,
                               'descriptionTemplate': 'description.md'}


def test_the_stage_block(tour):
    assert tour['stage'] == {
        'modules': ['stage.tsx'],
        'sets': {
            'playbill': {'module': 'stage.tsx', 'slots': ['stage', 'plate', 'headline', 'aside'],
                         'props': {'series': 'VIDEOMAKER · FIXTURES'}},
            'playbill-split': {'module': 'stage.tsx', 'base': 'playbill',
                               'slots': ['left', 'right', 'headline'], 'props': {'series': 'VIDEOMAKER · FIXTURES'}},
            'frame': {'slots': ['stage']},
            'split': {'slots': ['left', 'right']}},
        'elements': {
            'tally': {'module': 'stage.tsx', 'props': {'items': 'list'},
                      'actions': {'light': {'item': 'string'}}}}}


def test_a_chapter_declares_its_elements(tour):
    opening = chapter(tour, 'opening')
    assert set(opening) == {'id', 'narration', 'elements', 'shots'}
    assert opening['elements'] == {
        'wide': {'kind': 'view', 'camera': 'far'},
        'card': {'kind': 'tally', 'props': {'items': ['Balance', 'Tip']}},
        'title': {'kind': 'title', 'text': 'SEESAW', 'subtitle': 'One beam, one stand'}}
    assert chapter(tour, 'balance')['elements'] == {
        'mill': {'kind': 'view', 'camera': 'side', 'hide': ['ground']},
        'code': {'kind': 'source', 'source': 'declaration'}}
    assert chapter(tour, 'tip')['elements'] == {
        'close': {'kind': 'view', 'camera': 'near', 'hide': ['ground']},
        'wide': {'kind': 'view', 'camera': 'far', 'hide': ['ground', 'load']},
        'heading': {'kind': 'title', 'text': 'Rise and fall'},
        'beat': {'kind': 'title', 'text': 'Up. Down.'},
        'plate': {'kind': 'picture', 'still': 'plate', 'fit': 'contain'}}


def test_narration_is_the_chapters_and_whitespace_folds(tour):
    assert chapter(tour, 'balance')['narration'] == (
        'A stand carries the plank. In the source, the stand holds the beam. '
        'The weight pushes one end down.')


def test_a_shot_on_a_project_set_with_a_move_a_project_action_and_fade_in(tour):
    assert shot(tour, 'hook') == {
        'id': 'hook', 'set': 'playbill', 'places': {'stage': 'wide', 'aside': 'card'},
        'until': {'spoken': 'How'}, 'model': {'from': 0, 'to': 4},
        'fadeIn': {'duration': 1},
        'cues': [{'at': 0, 'actions': [{'element': 'wide', 'action': 'move', 'camera': 'near',
                                        'until': {'spoken': 'How'}, 'ease': 'out'}]},
                 {'at': {'spoken': 'balances'}, 'until': {'spoken': 'How'},
                  'actions': [{'element': 'card', 'action': 'light', 'params': {'item': 'Balance'}}]}]}


def test_a_title_in_a_slot_and_the_end_of_the_narration(tour):
    question = shot(tour, 'question')
    assert question['places'] == {'stage': 'wide', 'aside': 'card', 'headline': 'title'}
    assert question['until'] == {'spokenEnd': 'it', 'plus': 0.8}
    assert question['cues'][1] == {
        'at': 0, 'until': {'spokenEnd': 'it'},
        'actions': [{'element': 'title', 'action': 'show',
                     'enter': {'kind': 'fade', 'duration': 0.6},
                     'leave': {'kind': 'fade', 'duration': 0.6}}]}


def test_source_beside_the_model_with_emphasis_pairs_on_two_lines(tour):
    source = shot(tour, 'source')
    assert source['set'] == 'playbill-split'
    assert source['places'] == {'left': 'code', 'right': 'mill'}
    assert source['transition'] == {'kind': 'dissolve', 'duration': 0.6}
    assert source['cues'][0] == {'at': 0, 'actions': [{'element': 'code', 'action': 'type',
                                                       'throughLine': 24, 'over': 0.8}]}
    assert source['cues'][1] == {'at': {'spoken': 'the stand holds'}, 'until': {'spoken': 'the beam'},
                                 'actions': [{'element': 'mill', 'action': 'highlight',
                                              'parts': [['Stand']], 'others': 'ghost'}]}
    assert source['cues'][3] == {
        'at': {'spoken': 'the stand holds the beam'},
        'actions': [{'element': 'code', 'action': 'emphasize', 'hold': 0.6,
                     'words': [{'spoken': 'stand', 'token': 'Stand'},
                               {'spoken': 'beam', 'token': 'beam'}]}]}


def test_a_completed_panel_on_the_shipped_split_and_an_arrow(tour):
    push = shot(tour, 'push')
    assert push['set'] == 'split' and push['places'] == {'left': 'code', 'right': 'mill'}
    assert push['transition'] == {'kind': 'wipe', 'duration': 0.6, 'direction': 'right'}
    assert [a['action'] for c in push['cues'] for a in c['actions']] == ['move', 'emphasize', 'arrow']
    # An emphasis on a completed panel, its token chosen on one line of the excerpt.
    assert push['cues'][1] == {'at': {'spoken': 'pushes one end down'},
                               'actions': [{'element': 'code', 'action': 'emphasize', 'hold': 0.4, 'line': 22,
                                            'words': [{'spoken': 'one end', 'token': 'Block'}]}]}
    assert push['cues'][2] == {
        'at': {'spoken': 'The weight'}, 'until': {'spokenEnd': 'down', 'plus': 0.6},
        'actions': [{'element': 'mill', 'action': 'arrow', 'part': ['Beam', 'Weight'],
                     'text': 'Weight', 'place': [0.2, 0.25],
                     'enter': {'kind': 'draw', 'duration': 0.8},
                     'leave': {'kind': 'fade', 'duration': 0.4}}]}


def test_model_keys_on_marks_and_marks_bound_to_the_view(tour):
    rise = shot(tour, 'rise')
    assert rise['model'] == {'keys': [
        {'at': 0, 'seconds': {'mark': 'rise'}},
        {'at': {'spoken': 'On the way down'}, 'seconds': {'mark': 'top'}, 'ease': 'out'},
        {'at': {'spoken': 'Up.'}, 'seconds': {'mark': 'fall'}}]}
    assert rise['cues'][1]['actions'] == [
        {'element': 'close', 'action': 'ring', 'part': ['Beam', 'Plank'],
         'enter': {'kind': 'draw', 'duration': 0.8}, 'leave': {'kind': 'fade', 'duration': 0.4}},
        {'element': 'close', 'action': 'label', 'part': ['Beam', 'Plank'], 'text': 'Plank',
         'offset': [0.12, -0.08], 'enter': {'kind': 'fade', 'duration': 0.4},
         'leave': {'kind': 'fade', 'duration': 0.4}},
        {'element': 'close', 'action': 'highlight', 'parts': [['Beam', 'Plank'], ['Beam', 'Weight']],
         'others': 'ghost'}]
    assert rise['cues'][2]['actions'][2] == {'element': 'close', 'action': 'highlight',
                                             'parts': [['Stand']], 'others': 'dim'}


def test_a_spoken_reveal_and_a_move_that_changes_the_lens(tour):
    rhythm = shot(tour, 'rhythm')
    assert rhythm['places'] == {'stage': 'close', 'headline': 'beat'}
    assert rhythm['cues'] == [
        {'at': 0, 'actions': [{'element': 'close', 'action': 'move', 'camera': 'rolled',
                               'until': {'spoken': 'Explore'}, 'ease': 'smooth'}]},
        {'at': 0, 'until': {'spoken': 'Explore'},
         'actions': [{'element': 'beat', 'action': 'show', 'reveal': {'timing': 'spoken'}}]}]


def test_a_picture_in_the_plate_with_a_keyed_view(tour):
    still = shot(tour, 'still')
    assert still['places'] == {'stage': 'close', 'plate': 'plate'}
    assert still['cues'] == [{
        'at': 0, 'until': {'spoken': 'the model'},
        'actions': [{'element': 'plate', 'action': 'show',
                     'enter': {'kind': 'fade', 'duration': 0.5},
                     'leave': {'kind': 'fade', 'duration': 0.5},
                     'view': [{'at': 0, 'center': [0.5, 0.5], 'zoom': 1},
                              {'at': {'spoken': 'the model', 'plus': -0.2}, 'center': [0.5, 0.42],
                               'zoom': 1.4, 'ease': 'in-out'}]}]}]


def test_a_second_view_on_the_shipped_frame_and_fade_out(tour):
    invitation = shot(tour, 'invitation')
    assert invitation['set'] == 'frame' and invitation['places'] == {'stage': 'wide'}
    assert invitation['fadeOut'] == {'duration': 1.2}
    assert invitation['cues'] == [{'at': 0, 'until': {'spokenEnd': 'model', 'plus': 1.2},
                                   'actions': [{'element': 'wide', 'action': 'highlight',
                                                'parts': [['Beam']], 'others': 'dim'}]}]


def test_minimal_document_has_no_optional_blocks():
    document = evaluate(Minimal, name='minimal')
    assert 'style' not in document and 'credits' not in document and 'release' not in document
    assert 'series' not in document
    assert document['evidence'] == {}
    assert document['stage'] == {'modules': [], 'sets': {'frame': {'slots': ['stage']}},
                                 'elements': {}}
    assert document['chapters'][0]['shots'][0] == {
        'id': 'whole', 'set': 'frame', 'places': {'stage': 'view'},
        'until': {'spokenEnd': 'seesaw', 'plus': 0.5}, 'model': {'from': 0, 'to': 2}, 'cues': []}


def test_evaluating_twice_is_byte_identical():
    assert dumps(evaluate(Tour, name='tour')) == dumps(evaluate(Tour, name='tour'))


def test_canonical_json():
    text = dumps(evaluate(Minimal, name='minimal'))
    assert text.endswith('}\n') and not text.endswith('\n\n')
    assert '\n  "chapters": [' in text
    assert '"expectedDurationSeconds": 20,' in text
    keys = list(json.loads(text))
    assert keys == sorted(keys)


def test_root_follows_where_the_document_is_written():
    document = evaluate(Tour, name='tour', out=PROJECT / 'elsewhere' / 'deep' / 'movie.json')
    assert document['root'] == '../../videos/tour'
    assert document['stage']['modules'] == ['stage.tsx']


def test_evaluation_opens_only_the_manifest_revision_and_emphasised_excerpts(monkeypatch):
    opened = []
    real_open = builtins.open

    def recording_open(file, *args, **kwargs):
        opened.append(Path(file).resolve())
        return real_open(file, *args, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError('evaluation reached for a clock, randomness or the network')

    monkeypatch.setattr(builtins, 'open', recording_open)
    monkeypatch.setattr(io, 'open', recording_open)
    monkeypatch.setattr(socket, 'socket', forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(time, 'time', forbidden)
    monkeypatch.setattr(time, 'time_ns', forbidden)
    monkeypatch.setattr(random, 'random', forbidden)
    evaluate(Tour, name='tour')
    evaluate(Minimal, name='minimal')
    monkeypatch.undo()
    assert set(opened) == {EXPORT / 'manifest.json', EXPORT / 'source-revision.txt', SOURCE}


def stale_export(tmp_path, drop=None, revision=True, loop=20.0):
    target = tmp_path / 'export'
    shutil.copytree(EXPORT, target)
    manifest = json.loads((target / 'manifest.json').read_text())
    if drop:
        beam = next(c for c in manifest['root']['children'] if c['name'] == 'Beam')
        beam['children'] = [c for c in beam['children'] if c['name'] != drop]
    if loop is None:
        del manifest['animation']['loop']
    (target / 'manifest.json').write_text(json.dumps(manifest))
    if not revision:
        (target / 'source-revision.txt').unlink()
    return target


def one_chapter_movie(chapter_class):
    class Untitled(Movie):
        title = "Untitled"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        only = chapter_class()
    return Untitled


def movie_on(directory):
    class Stale(Playground):
        # A copy of the fixture take whose export is elsewhere.
        export = str(directory)

    class Only(Chapter):
        lines = Narration("The weight tips the beam.")
        view = View(Stale, camera=Stale.far)
        whole = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Stale.run(0, 2),
                     cues=[Cue(0, view.highlight(Seesaw.beam.weight), until=lines.end())])
    return one_chapter_movie(Only)


def test_part_path_the_export_lacks(tmp_path):
    with pytest.raises(MovieError) as refusal:
        evaluate(movie_on(stale_export(tmp_path, drop='Weight')), name='stale')
    message = str(refusal.value)
    for name in ('Seesaw.beam.weight', 'Beam/Weight', 'whole'):
        assert name in message, message


def test_export_without_a_revision_is_unpinned(tmp_path):
    document = evaluate(movie_on(stale_export(tmp_path, revision=False)), name='stale')
    assert document['model']['sourceRevision'] is None


def test_export_that_is_not_a_posed_loop(tmp_path):
    with pytest.raises(MovieError, match='animation.loop'):
        evaluate(movie_on(stale_export(tmp_path, loop=None)), name='stale')


class Elsewhere(Loop):
    model = Seesaw
    export = "fixtures/project/export/seesaw"
    marks = {}
    readiness = "A second take."
    far = Camera(position=(1, 2, 3), target=(0, 0, 0), fov=30)


def test_one_movie_films_one_take():
    class Mixed(Chapter):
        lines = Narration("One take. Then another.")
        one = View(Playground, camera=Playground.far)
        two = View(Elsewhere, camera=Elsewhere.far)
        first = Shot(Frame, {Frame.stage: one}, until=lines.spoken("Then"), model=Playground.run(0, 1))
        second = Shot(Frame, {Frame.stage: two}, until=lines.end(), model=Elsewhere.run(1, 2))
    with pytest.raises(MovieError) as refusal:
        evaluate(one_chapter_movie(Mixed), name='two')
    assert 'Playground' in str(refusal.value) and 'Elsewhere' in str(refusal.value)


def emphasising(*words):
    class Drive(Chapter):
        lines = Narration("The stand holds the beam.")
        view = View(Playground, camera=Playground.far)
        code = Source.panel(Playground.declaration)
        coupling = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(),
                        model=Playground.run(0, 2),
                        cues=[Cue(0, code.type(through_line=24, over=1)),
                              Cue(lines.spoken("The stand holds the beam"), code.emphasize(*words))])
    return one_chapter_movie(Drive)


def test_a_token_absent_from_its_excerpt():
    with pytest.raises(MovieError) as refusal:
        evaluate(emphasising(("beam", "plonk")), name='drive')
    for name in ('Drive', 'coupling', 'cues[1]', "'plonk'", 'absent', 'declaration'):
        assert name in str(refusal.value), str(refusal.value)


def test_a_token_repeated_in_its_excerpt():
    with pytest.raises(MovieError) as refusal:
        evaluate(emphasising(("stand", "Block")), name='drive')
    for name in ('Drive', 'coupling', "'Block'", 'ambiguous', 'declaration'):
        assert name in str(refusal.value), str(refusal.value)


def test_a_token_on_any_line_of_the_excerpt():
    document = evaluate(emphasising(("stand", "Stand"), ("The", "base")), name='drive')
    words = document['chapters'][0]['shots'][0]['cues'][1]['actions'][0]['words']
    assert [w['token'] for w in words] == ['Stand', 'base']


class Sheet(Set):
    module = "fixtures/project/videos/tour/nowhere.tsx"
    stage = Slot()


class Outside(Set):
    module = "../../stage.tsx"
    stage = Slot()


@pytest.mark.parametrize('chosen, words', [
    (Sheet, ('Sheet', 'nowhere.tsx', 'does not exist')),
    (Outside, ('Outside', 'stage.tsx', 'outside the project')),
], ids=['missing', 'outside'])
def test_a_stage_module_exists_inside_the_project(chosen, words):
    class Only(Chapter):
        lines = Narration("A seesaw.")
        view = View(Playground, camera=Playground.far)
        whole = Shot(chosen, {chosen.stage: view}, until=lines.end(), model=Playground.run(0, 1))
    with pytest.raises(MovieError) as refusal:
        evaluate(one_chapter_movie(Only), name='sheet')
    for word in words:
        assert word in str(refusal.value), str(refusal.value)


class Gauge(Element):
    module = "fixtures/project/videos/tour/stage.tsx"
    point = Action(at=float)


def test_a_project_element_used_by_one_chapter_is_listed_once():
    class Only(Chapter):
        lines = Narration("A seesaw tips.")
        gauge = Gauge(scale=2, labels=True, marks={"low": 0})
        whole = Shot(Split, {Split.left: gauge}, until=lines.end(), model=Playground.run(0, 1),
                     cues=[Cue(0, gauge.point(at=1), until=lines.end())])
    document = evaluate(one_chapter_movie(Only), name='gauge')
    assert document['stage']['modules'] == ['fixtures/project/videos/tour/stage.tsx']
    assert document['stage']['elements'] == {
        'gauge': {'module': 'fixtures/project/videos/tour/stage.tsx',
                  'props': {'scale': 'number', 'labels': 'boolean', 'marks': 'object'},
                  'actions': {'point': {'at': 'number'}}}}
    assert document['stage']['sets'] == {'split': {'slots': ['left', 'right']}}


def test_other_joins():
    class Reading(Chapter):
        lines = Narration("Read the declaration. Then watch.")
        view = View(Playground, camera=Playground.side, hide=[Playground.ground])
        code = Source.panel(Playground.declaration)
        read = Shot(Frame, {Frame.stage: code}, until=lines.spoken("Then"),
                    model=Playground.run(0, 1), cues=[Cue(0, code.type(through_line=24, over=1))])
        watch = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Playground.run(1, 3),
                     transition=Fade(0.8, color="#000000"))
        again = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(plus=1),
                     model=Playground.run(3, 4), transition=Slide(0.6, direction="left", ease="in-out"))
    document = evaluate(one_chapter_movie(Reading), name='read')
    read, watch, again = document['chapters'][0]['shots']
    assert read['places'] == {'stage': 'code'} and 'view' not in read['places'].values()
    assert watch['transition'] == {'kind': 'fade', 'duration': 0.8, 'color': '#000000'}
    assert again['transition'] == {'kind': 'slide', 'duration': 0.6, 'direction': 'left', 'ease': 'in-out'}


class Sheet2(Set):
    module = "fixtures/project/videos/tour/stage.tsx"
    title = "Sheet"
    stage = Slot()


class SheetSplit(Sheet2):
    left = Slot()
    right = Slot()


def test_a_derived_sets_base_is_listed_though_no_shot_uses_it():
    class Only(Chapter):
        lines = Narration("A seesaw.")
        view = View(Playground, camera=Playground.far)
        whole = Shot(SheetSplit, {SheetSplit.right: view}, until=lines.end(), model=Playground.run(0, 1))
    sets = evaluate(one_chapter_movie(Only), name='sheet')['stage']['sets']
    assert sets == {
        'sheet-split': {'module': 'fixtures/project/videos/tour/stage.tsx', 'base': 'sheet2',
                        'slots': ['left', 'right'], 'props': {'title': 'Sheet'}},
        'sheet2': {'module': 'fixtures/project/videos/tour/stage.tsx', 'slots': ['stage'],
                   'props': {'title': 'Sheet'}}}


def test_two_sets_of_one_kind_are_refused():
    class Twin(Set):
        module = "fixtures/project/videos/tour/stage.tsx"
        kind = "sheet2"
        stage = Slot()

    class Only(Chapter):
        lines = Narration("A seesaw. Twice.")
        view = View(Playground, camera=Playground.far)
        one = Shot(Sheet2, {Sheet2.stage: view}, until=lines.spoken("Twice"), model=Playground.run(0, 1))
        two = Shot(Twin, {Twin.stage: view}, until=lines.end(), model=Playground.run(1, 2))
    with pytest.raises(MovieError) as refusal:
        evaluate(one_chapter_movie(Only), name='sheet')
    for word in ('Sheet2', 'Twin', 'sheet2'):
        assert word in str(refusal.value), str(refusal.value)
