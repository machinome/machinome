"""Layer 1: a clocked take, declared and recorded.

A `Take` names the steps a clocked machine is asked to make and the marks
its shots cut on; its class refuses by name what it cannot film; evaluation
records the take once through the framework's simulation, twice
identically, and the document check holds a take document to its export
and to the replay of its steps. The fixture is the framework tutorial's
clocked counter (`models/counter.py`), its take `Turns` and the movie
`count`.
"""

import builtins
import copy
import io
import json
import random
import shutil
import socket
import time
from pathlib import Path

import pytest

from machinome.simulation import Driver, Instruction
from machinome_movie import (Camera, Chapter, Format, Frame, Loop, Mark, Move, Movie, MovieError,
                             Narration, Narrator, Shot, Take, Trigger, View, check_document, dumps,
                             evaluate)

from models.counter import Counter
from models.seesaw import Seesaw
from videos.count.movie import Count
from videos.takes import Turns

from conftest import PROJECT

EXPORT = PROJECT / 'export' / 'counter'
MANIFEST = json.loads((EXPORT / 'manifest.json').read_text())
IDENTITY = MANIFEST['clocked']['identity']
RELATION = '(crank, units, tens) commits (units, tens)'


def refused(*names):
    """Assert the block raises MovieError naming every one of `names`."""
    class Check:
        def __enter__(self):
            self.raised = pytest.raises(MovieError)
            self.info = self.raised.__enter__()
            return self.info

        def __exit__(self, *exc):
            handled = self.raised.__exit__(*exc)
            message = str(self.info.value)
            for name in names:
                assert name in message, f'{name!r} not named in: {message}'
            return handled
    return Check()


def take(*steps, model=Counter, export='fixtures/project/export/counter', **body):
    """A take on the fixture counter whose body is `steps` and `body`."""
    namespace = {'model': model, 'export': export, 'readiness': 'A test take.',
                 'steps': list(steps), **body}
    return type('Trial', (Take,), namespace)


##############################################
# Declarations

def test_the_counters_take():
    assert [(p.id, p.at, p.duration, p.input, p.instruction) for p in Turns.schedule] == [
        ('step-1', 0, 2.0, None, 'Turn once'),
        ('step-2', 2.0, 4, 'crank', None),
        ('step-3', 6.0, 2.0, None, 'Turn once')]
    assert Turns.length == 8
    assert Turns.marks == {'one': 2, 'nine': 6, 'ten': 8}
    assert Turns.schedule[1].to == 3240 and Turns.schedule[1].by is None


def decimal_steps():
    """Three moves of 1.2 s with a mark after each: summed as floats, the
    third mark is 3.5999999999999996 (finding 7 of the Curta film)."""
    return take(Move(Counter.crank, by=360, over=1.2), Mark('first'),
                Move(Counter.crank, by=360, over=1.2), Mark('second'),
                Move(Counter.crank, by=360, over=1.2), Mark('third'), front=camera())


def test_take_time_is_the_exact_sum_of_the_written_durations():
    trial = decimal_steps()
    assert [repr(p.at) for p in trial.schedule] == ['0', '1.2', '2.4']
    assert {name: repr(at) for name, at in trial.marks.items()} == {
        'first': '1.2', 'second': '2.4', 'third': '3.6'}
    assert repr(trial.length) == '3.6'


def test_an_instructions_duration_is_summed_exactly_with_the_moves():
    trial = take(Move(Counter.crank, by=360, over=0.1), Move(Counter.crank, by=360, over=0.2),
                 Mark('moved'), Trigger('Turn once'), Mark('turned'), front=camera())
    assert {name: repr(at) for name, at in trial.marks.items()} == {'moved': '0.3',
                                                                      'turned': '2.3'}


def test_an_input_is_the_models_driver_or_the_frameworks_id():
    by_name = take(Move('crank', by=360, over=1))
    assert by_name.schedule[0].input == 'crank' and by_name.schedule[0].by == 360
    by_declaration = take(Move(Counter.crank, by=360, over=1))
    assert by_declaration.schedule[0].input == 'crank'


def test_an_instruction_is_named_or_the_one_the_table_holds():
    held = take(Trigger(Counter.instructions['Turn once']))
    assert held.schedule[0].instruction == 'Turn once'
    assert held.schedule[0].duration == 2.0


def test_a_mark_before_every_step_is_the_initial_instant():
    # The contract: "a mark at 0 is the initial bank".
    assert take(Mark('rest'), Trigger('Turn once')).marks == {'rest': 0}


def test_a_step_that_is_neither_a_move_a_trigger_nor_a_mark():
    with refused('Take Trial', 'steps[1]', "'Turn once'", 'Move', 'Trigger', 'Mark'):
        take(Trigger('Turn once'), 'Turn once')


@pytest.mark.parametrize('to, by', [(3, 4), (None, None)])
def test_a_move_says_where_or_how_far(to, by):
    with refused('Take Trial', 'steps[0]', 'Move(Counter.crank', 'to=', 'by='):
        take(Move(Counter.crank, to=to, by=by, over=1))


@pytest.mark.parametrize('over', [None, 0, -1, True, 'slow', float('inf')])
def test_a_move_is_drawn_over_a_positive_number_of_seconds(over):
    with refused('Take Trial', 'steps[0]', 'over'):
        take(Move(Counter.crank, by=360, over=over))


@pytest.mark.parametrize('to', [True, 'far', float('nan')])
def test_a_move_goes_to_a_number(to):
    with refused('Take Trial', 'steps[0]', 'to'):
        take(Move(Counter.crank, to=to, over=1))


def test_an_input_the_model_does_not_declare():
    stray = Driver(default=0.0, range=(0.0, 1.0))
    with refused('Take Trial', 'steps[0]', 'Counter', 'driver'):
        take(Move(stray, by=1, over=1))
    with refused('Take Trial', 'steps[0]', 'units', 'State', 'driver'):
        take(Move(Counter.units, to=1, over=1))
    with refused('Take Trial', 'steps[0]', '42'):
        take(Move(42, by=1, over=1))


def test_an_instruction_the_model_does_not_declare():
    with refused('Take Trial', 'steps[0]', 'Turn twice', 'Turn once', 'instructions'):
        take(Trigger('Turn twice'))
    with refused('Take Trial', 'steps[0]', 'instructions'):
        take(Trigger(Instruction(by={'crank': 360.0}, duration=2.0)))


class Snapping(Counter):
    instructions = {'Snap': Instruction(by={'crank': 360.0}, duration=0.0)}


def test_an_instruction_drawn_over_no_time():
    with refused('Take Trial', 'steps[0]', 'Snap', 'duration'):
        take(Trigger('Snap'), model=Snapping)


@pytest.mark.parametrize('name', ['nine turns', '9th', '', None])
def test_a_mark_is_a_name(name):
    with refused('Take Trial', 'steps[1]', 'mark'):
        take(Trigger('Turn once'), Mark(name))


def test_a_mark_named_twice():
    with refused('Take Trial', 'steps[3]', "'one'", 'twice'):
        take(Trigger('Turn once'), Mark('one'), Trigger('Turn once'), Mark('one'))


def test_two_marks_at_one_instant():
    with refused('Take Trial', 'steps[2]', "'once'", "'single'", 'instant'):
        take(Trigger('Turn once'), Mark('once'), Mark('single'))


@pytest.mark.parametrize('steps', [[], [Mark('rest')]])
def test_a_take_with_no_steps(steps):
    with refused('Take Trial', 'no steps', 'Move', 'Trigger'):
        take(*steps)


def test_a_take_writes_no_marks():
    with refused('Take Trial', 'marks', 'Mark('):
        take(Trigger('Turn once'), marks={'one': 2})


@pytest.mark.parametrize('attribute', ['model', 'export', 'readiness', 'steps'])
def test_a_take_needs_its_declarations(attribute):
    namespace = {'model': Counter, 'export': 'x', 'readiness': 'r', 'steps': [Trigger('Turn once')]}
    del namespace[attribute]
    with refused('Take Trial', attribute):
        type('Trial', (Take,), namespace)


def test_steps_are_a_list():
    with refused('Take Trial', 'steps'):
        type('Trial', (Take,), {'model': Counter, 'export': 'x', 'readiness': 'r',
                                'steps': Trigger('Turn once')})


def one_shot(model):
    class Only(Chapter):
        lines = Narration("The counter turns.")
        view = View(Turns, camera=Turns.front)
        whole = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=model)
    return Only


@pytest.mark.parametrize('model, field', [
    (lambda: Turns.run('nine', 9), '9'),
    (lambda: Turns.run(8.5, 'one'), '8.5'),
    (lambda: Turns.keys({0: 'one', 2: 8.25}), '8.25'),
])
def test_model_time_outside_the_take(model, field):
    with refused('Only.whole', 'outside the take', 'Turns', field):
        one_shot(model())


def test_model_time_to_the_end_of_the_take():
    one_shot(Turns.run(0, 8))
    one_shot(Turns.run('nine', 'ten'))


def test_a_view_on_a_take_and_a_camera_of_another():
    class Other(Take):
        model = Counter
        export = '../export/counter'
        readiness = 'Another take.'
        steps = [Trigger('Turn once')]
        side = Camera(position=(1, 2, 3), target=(0, 0, 0), fov=30)

    with refused('camera side', 'Other', 'Turns'):
        class Wrong(Chapter):
            lines = Narration("The counter turns.")
            view = View(Turns, camera=Other.side)
            whole = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Turns.run(0, 2))


##############################################
# Evaluation

@pytest.fixture(scope='module')
def count():
    return evaluate(Count, name='count')


def test_the_model_block_and_the_marks(count):
    assert count['model'] == {
        'manifest': '../../export/counter/manifest.json',
        'expectedDurationSeconds': 8,
        'timeMode': 'take',
        'sourceRevision': (EXPORT / 'source-revision.txt').read_text().strip(),
        'readiness': "Exported by machinome export; the drums count the crank's turns and carry."}
    assert count['marks'] == {'one': 2, 'nine': 6, 'ten': 8}


def test_the_take_is_the_frameworks_requests_verbatim(count):
    recorded = count['take']
    assert recorded['kind'] == 'clocked'
    assert recorded['identity'] == IDENTITY
    assert recorded['initial'] == {'crank': 0, 'tens': 0, 'units': 0}
    first, move, carry = recorded['steps']
    assert first == {'id': 'step-1', 'at': 0, 'duration': 2, 'input': 'crank', 'by': 360,
                     'origin': 0, 'end': 360, 'admitted': 360,
                     'commits': [{'fraction': 1, 'value': 360, 'targets': {'tens': 0, 'units': 1},
                                  'relations': [RELATION]}],
                     'stops': []}
    assert {key: move[key] for key in ('id', 'at', 'duration', 'input', 'to', 'origin', 'end',
                                       'admitted', 'stops')} == {
        'id': 'step-2', 'at': 2, 'duration': 4, 'input': 'crank', 'to': 3240, 'origin': 360,
        'end': 3240, 'admitted': 2880, 'stops': []}
    assert 'by' not in move
    assert [c['fraction'] for c in move['commits']] == [k / 8 for k in range(1, 9)]
    assert [c['value'] for c in move['commits']] == [360 * k for k in range(2, 10)]
    assert [c['targets'] for c in move['commits']] == [{'tens': 0, 'units': u} for u in range(2, 10)]
    assert carry['commits'] == [{'fraction': 1, 'value': 3600, 'targets': {'tens': 1, 'units': 0},
                                 'relations': [RELATION]}]
    assert recorded['banks'] == {'one': {'crank': 360, 'tens': 0, 'units': 1},
                                 'nine': {'crank': 3240, 'tens': 0, 'units': 9},
                                 'ten': {'crank': 3600, 'tens': 1, 'units': 0}}


def test_the_shots_run_take_time_between_marks(count):
    shots = count['chapters'][0]['shots']
    assert [s['model'] for s in shots] == [{'from': 0, 'to': {'mark': 'one'}},
                                           {'from': {'mark': 'one'}, 'to': {'mark': 'nine'}},
                                           {'from': {'mark': 'nine'}, 'to': {'mark': 'ten'}}]
    assert count['chapters'][0]['elements']['view'] == {'kind': 'view', 'camera': 'front'}
    assert count['sourceCode'] == {'relations': {'file': '../../models/counter.py',
                                                 'lines': [150, 153]}}


def test_evaluating_a_take_twice_is_byte_identical():
    assert dumps(evaluate(Count, name='count')) == dumps(evaluate(Count, name='count'))


def test_recording_reads_no_clock_randomness_network_or_cad(monkeypatch):
    import cadquery

    opened = []
    real_open = builtins.open

    def recording_open(file, *args, **kwargs):
        opened.append(Path(file).resolve())
        return real_open(file, *args, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError('evaluation reached for a clock, randomness, the network or CAD')

    monkeypatch.setattr(builtins, 'open', recording_open)
    monkeypatch.setattr(io, 'open', recording_open)
    monkeypatch.setattr(socket, 'socket', forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(time, 'time', forbidden)
    monkeypatch.setattr(time, 'time_ns', forbidden)
    monkeypatch.setattr(random, 'random', forbidden)
    monkeypatch.setattr(cadquery.Workplane, '__init__', forbidden)
    evaluate(Count, name='count')
    monkeypatch.undo()
    # The evaluation's own reads, and the model's project files the
    # framework's simulation reads; nothing else.
    allowed = {EXPORT / 'manifest.json', EXPORT / 'source-revision.txt',
               PROJECT / 'models' / 'counter.py', PROJECT / 'pyproject.toml',
               PROJECT / 'models' / 'pyproject.toml'}
    assert set(opened) <= allowed, set(opened) - allowed
    assert EXPORT / 'manifest.json' in opened


def movie_of(chosen, model=None):
    class Only(Chapter):
        lines = Narration("The counter turns.")
        view = View(chosen, camera=chosen.front)
        whole = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                     model=model or chosen.run(0, chosen.length))

    class Trial(Movie):
        title = "Trial"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        only = Only()
    return Trial


def camera():
    return Camera(position=(160, -260, 140), target=(0, 0, 20), fov=37)


def test_a_request_the_framework_refuses():
    trial = take(Trigger('Turn once'), Move('cranky', by=360, over=1), front=camera())
    with refused('Take Trial', 'step-2', "Move('cranky', by=360, over=1)", 'cranky',
                 'names no declared driver', 'declared: crank'):
        evaluate(movie_of(trial), name='trial')


def test_a_step_the_machine_stops_before_it_travels():
    trial = take(Trigger('Turn once'), Move(Counter.crank, by=-100, over=1), front=camera())
    with refused('Take Trial', 'step-2', 'Move(Counter.crank, by=-100, over=1)', 'handle.turn',
                 'stop'):
        evaluate(movie_of(trial), name='trial')


def test_a_step_stopped_part_way_is_recorded_with_its_stop():
    trial = take(Move(Counter.crank, to=50, over=1), Move(Counter.crank, by=-30, over=1),
                 front=camera())
    step = evaluate(movie_of(trial), name='trial')['take']['steps'][1]
    assert (step['origin'], step['end'], step['admitted']) == (50, 36, -14)
    assert step['stops'] == [{'coordinate': 'handle.turn', 'side': 'low', 'bound': 36,
                              'value': 36, 'input': 36, 'fraction': pytest.approx(14 / 30)}]


def test_the_document_carries_the_exact_sums():
    document = evaluate(movie_of(decimal_steps()), name='trial')
    written = json.loads(dumps(document))
    assert [step['at'] for step in written['take']['steps']] == [0, 1.2, 2.4]
    assert [step['duration'] for step in written['take']['steps']] == [1.2, 1.2, 1.2]
    assert written['marks'] == {'first': 1.2, 'second': 2.4, 'third': 3.6}
    assert written['model']['expectedDurationSeconds'] == 3.6
    assert '3.5999999999999996' not in dumps(document)
    check_document(document, manifest=MANIFEST)


def test_a_take_on_an_export_with_no_clocked_machine():
    trial = take(Trigger('Turn once'), export='fixtures/project/export/seesaw', front=camera())
    with refused('Take Trial', 'clocked', 'export'):
        evaluate(movie_of(trial), name='trial')


def test_a_take_on_a_model_the_framework_does_not_clock():
    trial = take(Move('crank', by=1, over=1), model=Seesaw, front=camera())
    with refused('Take Trial', 'Seesaw', 'clocked'):
        evaluate(movie_of(trial), name='trial')


def test_a_loop_on_a_clocked_export_is_refused():
    class Wrong(Loop):
        model = Counter
        export = 'fixtures/project/export/counter'
        readiness = 'A loop that is not one.'
        front = camera()

    class Only(Chapter):
        lines = Narration("The counter turns.")
        view = View(Wrong, camera=Wrong.front)
        whole = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Wrong.run(0, 1))

    class Trial(Movie):
        title = "Trial"
        status = "rehearsal"
        learning_goal = "None."
        format = Format(640, 360, fps=10)
        narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
        only = Only()

    with refused('animation.loop', 'Take'):
        evaluate(Trial, name='trial')


def test_an_export_older_than_the_model(tmp_path):
    stale = tmp_path / 'counter'
    shutil.copytree(EXPORT, stale)
    manifest = json.loads((stale / 'manifest.json').read_text())
    del manifest['states']['tens']
    (stale / 'manifest.json').write_text(json.dumps(manifest))
    trial = take(Trigger('Turn once'), export=str(stale), front=camera())
    with refused('take.initial', 'tens'):
        evaluate(movie_of(trial), name='trial')


##############################################
# The document check on take documents

def checked(document, manifest=MANIFEST):
    check_document(document, manifest=manifest)


def mutated(count, change):
    document = copy.deepcopy(count)
    change(document)
    return document


def test_the_evaluated_take_document_is_accepted(count):
    checked(count)
    checked(count, manifest=None)


@pytest.mark.parametrize('change, names', [
    (lambda d: d['model'].update(timeMode='clocked'), ['model.timeMode', "'clocked'"]),
    (lambda d: d.pop('take'), ['model.timeMode', 'take', 'missing']),
    (lambda d: d['take'].update(identity='0' * 64), ['take.identity', 'clocked.identity']),
    (lambda d: d['take']['steps'][0].update(input='cranky'),
     ['take.steps[0]', 'step-1', 'input', 'cranky']),
    (lambda d: d['take']['initial'].pop('tens'), ['take.initial', 'tens']),
    (lambda d: d['take']['initial'].update(time=0), ['take.initial', 'time']),
    (lambda d: d['take']['steps'][1].update(at=2.5), ['take.steps[1]', 'step-2', 'at']),
    (lambda d: d['take']['steps'][0].update(at=1), ['take.steps[0]', 'step-1', 'at']),
    (lambda d: d['take']['steps'][1].update(by=1), ['take.steps[1]', 'step-2', 'to', 'by']),
    (lambda d: d['take']['steps'][0].pop('by'), ['take.steps[0]', 'step-1', 'to', 'by']),
    (lambda d: d['take']['steps'][2].update(id='step-1'), ['take.steps[2]', 'step-1', 'twice']),
    (lambda d: d['model'].update(expectedDurationSeconds=9),
     ['model.expectedDurationSeconds', 'take']),
    (lambda d: d['marks'].update(nine=5), ['marks.nine', 'step']),
    # The sums are exact: a hair off is off (finding 7 of the Curta film).
    (lambda d: d['take']['steps'][1].update(at=2.0000000000000004),
     ['take.steps[1]', 'step-2', 'at']),
    (lambda d: d['model'].update(expectedDurationSeconds=7.999999999999999),
     ['model.expectedDurationSeconds', 'take']),
    (lambda d: d['marks'].update(nine=6.000000000000001), ['marks.nine', 'end of a step']),
    (lambda d: d['take']['banks'].pop('nine'), ['take.banks', 'nine', 'missing']),
    (lambda d: d['take']['banks'].update(eleven={}), ['take.banks', 'eleven', 'marks']),
    (lambda d: d['take']['banks']['ten'].update(units=1), ['take.banks.ten', 'ten', 'units']),
    (lambda d: d['take']['steps'][2]['commits'][0]['targets'].update(tens=2),
     ['take.banks.ten', 'ten', 'tens']),
    (lambda d: d['take']['steps'][1].update(end=3250), ['take.banks.nine', 'nine', 'crank']),
    (lambda d: d['chapters'][0]['shots'][2]['model'].update(to=9),
     ['chapter counting', 'shot carry', 'model.to', 'outside the take']),
    (lambda d: d['chapters'][0]['shots'][0]['model'].update(**{'from': {'mark': 'ten', 'plus': 0.5}}),
     ['chapter counting', 'shot once', 'model.from', 'outside the take']),
])
def test_a_take_document_is_refused_naming_its_fault(count, change, names):
    with refused(*names):
        checked(mutated(count, change))


def test_a_take_block_on_a_loop_document(count):
    document = json.loads((Path(__file__).resolve().parents[2] / 'fixtures' / 'documents'
                           / 'minimal.json').read_text())
    document['take'] = copy.deepcopy(count['take'])
    with refused('take', 'normalized-loop'):
        check_document(document)


def test_a_take_document_on_an_export_with_no_clocked_machine(count):
    seesaw = json.loads((PROJECT / 'export' / 'seesaw' / 'manifest.json').read_text())
    with refused('clocked', 'export'):
        checked(count, manifest=seesaw)
