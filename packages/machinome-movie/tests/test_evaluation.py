"""Layer 1: a movie evaluates to the movie document, twice identically,
reading nothing but the export's manifest and source revision.

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

from machinome_movie import (Camera, Chapter, Cue, Fade, Format, Loop, Movie, MovieError,
                             Narration, Narrator, Paper, PaperSplit, Shot, Slide,
                             Source, SourceOnly, View, dumps, evaluate)

from models.seesaw import Seesaw
from videos.minimal.movie import Minimal
from videos.takes import Playground
from videos.tour.movie import Tour

from conftest import PROJECT

EXPORT = PROJECT / 'export' / 'seesaw'


@pytest.fixture(scope='module')
def tour():
    return evaluate(Tour, name='tour')


def shot(document, shot_id):
    for chapter in document['chapters']:
        for candidate in chapter['shots']:
            if candidate['id'] == shot_id:
                return candidate
    raise KeyError(shot_id)


def test_top_level(tour):
    assert tour['format'] == 'machinome-movie/0.1'
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


def test_narration_is_the_chapters_and_whitespace_folds(tour):
    balance = tour['chapters'][1]
    assert balance['narration'] == ('A stand carries the plank. In the source, the beam rests '
                                    'on its pivot. The weight pushes one end down.')
    assert set(balance) == {'id', 'narration', 'shots'}


def test_shot_on_a_phrase_with_a_camera_move_and_fade_in(tour):
    hook = shot(tour, 'hook')
    assert hook['set'] == 'paper'
    assert hook['until'] == {'spoken': 'How'}
    assert hook['simulation'] == {'from': 0, 'to': 4}
    assert hook['camera'] == [{'at': 0, 'preset': 'far'},
                              {'at': {'spoken': 'How'}, 'preset': 'near', 'ease': 'out'}]
    assert hook['fadeIn'] == {'duration': 1}
    assert hook['hiddenLayers'] == [] and hook['overlays'] == [] and hook['evidence'] == []
    assert 'transition' not in hook and 'code' not in hook


def test_the_views_camera_persists_into_the_next_shot(tour):
    question = shot(tour, 'question')
    assert question['camera'] == [{'at': 0, 'preset': 'near'}]


def test_end_of_the_narration_is_its_unique_last_words(tour):
    question = shot(tour, 'question')
    assert question['until'] == {'spokenEnd': 'it', 'plus': 0.8}
    assert question['overlays'] == [{'from': 0, 'to': {'spokenEnd': 'it'}, 'text': 'SEESAW',
                                     'position': 'title', 'subtitle': 'One beam, one stand',
                                     'enter': {'kind': 'fade', 'duration': 0.6},
                                     'leave': {'kind': 'fade', 'duration': 0.6}}]


def test_split_shot_code_highlight_and_dissolve(tour):
    source = shot(tour, 'source')
    assert source['set'] == 'paper-split'
    assert source['transition'] == {'kind': 'dissolve', 'duration': 0.6}
    assert source['hiddenLayers'] == ['ground']
    assert source['camera'] == [{'at': 0, 'preset': 'side'}]
    assert source['code'] == {
        'snippet': 'declaration',
        'typing': [{'from': 0, 'to': 1.2, 'throughLine': 24}],
        'emphasis': [{'line': 24, 'phrase': 'the beam rests on its pivot',
                      'words': ['beam'], 'hold': 0}]}
    assert source['highlight'] == [
        {'from': {'spoken': 'beam'}, 'to': {'spoken': 'pivot'}, 'parts': [['Beam']], 'others': 'ghost'},
        {'from': {'spoken': 'pivot'}, 'to': {'spoken': 'The weight'},
         'parts': [['Beam', 'pivot']], 'others': 'ghost'}]


def test_wipe_move_after_a_hold_and_an_arrow(tour):
    push = shot(tour, 'push')
    assert push['transition'] == {'kind': 'wipe', 'duration': 0.6, 'direction': 'right'}
    assert push['camera'] == [{'at': 0, 'preset': 'side'},
                              {'at': {'spokenEnd': 'down'}, 'preset': 'near', 'ease': 'smooth'}]
    assert push['annotations'] == [
        {'from': {'spoken': 'The weight'}, 'to': {'spokenEnd': 'down', 'plus': 0.6},
         'kind': 'arrow', 'part': ['Beam', 'Weight'], 'text': 'Weight', 'place': [0.2, 0.25],
         'enter': {'kind': 'draw', 'duration': 0.8}, 'leave': {'kind': 'fade', 'duration': 0.4}}]


def test_model_keys_on_marks_rings_labels_titles(tour):
    rise = shot(tour, 'rise')
    assert rise['simulation'] == {
        'from': {'mark': 'rise'}, 'to': {'mark': 'fall'},
        'keyframes': [{'at': 0, 'seconds': {'mark': 'rise'}},
                      {'at': {'spoken': 'On the way down'}, 'seconds': {'mark': 'top'}, 'ease': 'out'},
                      {'at': {'spoken': 'Up.'}, 'seconds': {'mark': 'fall'}}]}
    assert rise['overlays'] == [
        {'from': 0, 'to': {'spoken': 'On the way down'}, 'text': 'Rise', 'position': 'top'},
        {'from': {'spoken': 'On the way down'}, 'to': {'spoken': 'Up.'}, 'text': 'Fall', 'position': 'top'}]
    assert rise['annotations'][0] == {
        'from': {'spoken': 'the plank'}, 'to': {'spoken': 'On the way down'}, 'kind': 'ring',
        'part': ['Beam', 'Plank'], 'enter': {'kind': 'draw', 'duration': 0.8},
        'leave': {'kind': 'fade', 'duration': 0.4}}
    assert rise['annotations'][1] == {
        'from': {'spoken': 'the plank'}, 'to': {'spoken': 'On the way down'}, 'kind': 'label',
        'part': ['Beam', 'Plank'], 'text': 'Plank', 'offset': [0.12, -0.08],
        'enter': {'kind': 'fade', 'duration': 0.4}, 'leave': {'kind': 'fade', 'duration': 0.4}}
    assert [a['kind'] for a in rise['annotations']] == ['ring', 'label', 'ring', 'label']
    assert rise['highlight'][1] == {'from': {'spoken': 'the stand'}, 'to': {'spoken': 'Up.'},
                                    'parts': [['Stand']], 'others': 'dim'}


def test_spoken_reveal_and_a_move_that_changes_the_lens(tour):
    rhythm = shot(tour, 'rhythm')
    assert rhythm['camera'] == [{'at': 0, 'preset': 'near'},
                                {'at': {'spoken': 'Explore'}, 'preset': 'rolled', 'ease': 'smooth'}]
    assert rhythm['overlays'] == [{'from': 0, 'to': {'spoken': 'Explore'}, 'text': 'Up. Down.',
                                   'position': 'top', 'reveal': {'timing': 'spoken'}}]


def test_still_with_keyed_view_on_an_anchor(tour):
    still = shot(tour, 'still')
    assert still['camera'] == [{'at': 0, 'preset': 'rolled'}]
    assert still['pictures'] == [{
        'from': 0, 'to': {'spoken': 'the model'}, 'still': 'plate', 'area': 'frame', 'fit': 'contain',
        'enter': {'kind': 'fade', 'duration': 0.5}, 'leave': {'kind': 'fade', 'duration': 0.5},
        'view': [{'at': 0, 'center': [0.5, 0.5], 'zoom': 1},
                 {'at': {'spoken': 'the model', 'plus': -0.2}, 'center': [0.5, 0.42], 'zoom': 1.4,
                  'ease': 'in-out'}]}]


def test_a_different_view_at_the_cut_and_fade_out(tour):
    invitation = shot(tour, 'invitation')
    assert invitation['camera'] == [{'at': 0, 'preset': 'far'}]
    assert invitation['hiddenLayers'] == ['ground', 'load']
    assert invitation['fadeOut'] == {'duration': 1.2}
    assert invitation['highlight'] == [{'from': 0, 'to': {'spokenEnd': 'model', 'plus': 1.2},
                                        'parts': [['Beam']], 'others': 'dim'}]


def test_minimal_document_has_no_optional_blocks():
    document = evaluate(Minimal, name='minimal')
    assert 'style' not in document and 'credits' not in document and 'release' not in document
    assert 'series' not in document
    assert document['evidence'] == {}
    assert document['chapters'][0]['shots'][0]['until'] == {'spokenEnd': 'seesaw', 'plus': 0.5}


def test_evaluating_twice_is_byte_identical():
    assert dumps(evaluate(Tour, name='tour')) == dumps(evaluate(Tour, name='tour'))


def test_canonical_json():
    text = dumps(evaluate(Minimal, name='minimal'))
    assert text.endswith('}\n') and not text.endswith('\n\n')
    assert '\n  "chapters": [' in text
    assert '"expectedDurationSeconds": 20,' in text
    keys = list(json.loads(text))
    assert keys == sorted(keys)


def test_root_follows_where_the_document_is_written(tmp_path):
    document = evaluate(Minimal, name='minimal', out=PROJECT / 'elsewhere' / 'deep' / 'movie.json')
    assert document['root'] == '../../videos/minimal'


def test_evaluation_reads_only_the_manifest_and_revision(monkeypatch):
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
    monkeypatch.undo()
    assert set(opened) <= {EXPORT / 'manifest.json', EXPORT / 'source-revision.txt'}
    assert EXPORT / 'manifest.json' in opened


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


def movie_on(directory):
    class Stale(Playground):
        # A copy of the fixture take whose export is elsewhere.
        export = str(directory)

    class Only(Chapter):
        lines = Narration("The weight tips the beam.")
        view = View(Stale, camera=Stale.far)
        whole = Shot(Paper, {Paper.stage: view}, until=lines.end(), model=Stale.run(0, 2),
                     cues=[Cue(0, view.highlight(Seesaw.beam.weight), until=lines.end())])

    class StaleMovie(Movie):
        title = "Stale"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        only = Only()
    return StaleMovie


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
        first = Shot(Paper, {Paper.stage: one}, until=lines.spoken("Then"), model=Playground.run(0, 1))
        second = Shot(Paper, {Paper.stage: two}, until=lines.end(), model=Elsewhere.run(1, 2))

    class Two(Movie):
        title = "Two"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        mixed = Mixed()
    with pytest.raises(MovieError) as refusal:
        evaluate(Two, name='two')
    assert 'Playground' in str(refusal.value) and 'Elsewhere' in str(refusal.value)


def test_source_only_shot_poses_the_chapters_view_and_other_joins():
    class Reading(Chapter):
        lines = Narration("Read the declaration. Then watch.")
        view = View(Playground, camera=Playground.side, hide=[Playground.ground])
        code = Source.panel(Playground.declaration)
        read = Shot(SourceOnly, {SourceOnly.source: code}, until=lines.spoken("Then"),
                    model=Playground.run(0, 1), cues=[Cue(0, code.type(through_line=24, over=1))])
        watch = Shot(Paper, {Paper.stage: view}, until=lines.end(), model=Playground.run(1, 3),
                     transition=Fade(0.8, color="#000000"))
        again = Shot(PaperSplit, {PaperSplit.left: code, PaperSplit.right: view}, until=lines.end(plus=1),
                     model=Playground.run(3, 4), transition=Slide(0.6, direction="left", ease="in-out"),
                     cues=[Cue(0, code.type(through_line=24, over=0.5))])

    class Read(Movie):
        title = "Read"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        reading = Reading()
    document = evaluate(Read, name='read')
    read, watch, again = document['chapters'][0]['shots']
    assert read['set'] == 'source-only'
    assert read['camera'] == [{'at': 0, 'preset': 'side'}] and read['hiddenLayers'] == ['ground']
    assert read['code'] == {'snippet': 'declaration', 'typing': [{'from': 0, 'to': 1, 'throughLine': 24}]}
    assert watch['transition'] == {'kind': 'fade', 'duration': 0.8, 'color': '#000000'}
    assert again['transition'] == {'kind': 'slide', 'duration': 0.6, 'direction': 'left', 'ease': 'in-out'}


def test_source_only_shot_with_several_views_is_refused():
    with pytest.raises(MovieError) as refusal:
        class Reading(Chapter):
            lines = Narration("Read the declaration.")
            one = View(Playground, camera=Playground.side)
            two = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            read = Shot(SourceOnly, {SourceOnly.source: code}, until=lines.end(),
                        model=Playground.run(0, 1), cues=[Cue(0, code.type(through_line=24, over=1))])
    assert 'read' in str(refusal.value) and 'one view' in str(refusal.value)
