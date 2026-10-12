"""Layer 1: the declarations refuse by name when the class is created.

Each test declares a set, an element, a chapter or a movie inline and
asserts that the refusal names what is wrong: the chapter, the shot, the
field, the slot, the element, the action, the parameter, the phrase, the
mark, the camera.
"""

import pytest

from machinome.movie import (Action, Camera, Chapter, Cue, Element, Format, Frame, Loop,
                             Movie, MovieError, Narration, Narrator, Picture, Reframe, Reveal,
                             Set, Shot, Slot, Source, Split, Style, Title, View)
from machinome.movie.text import excerpt_line, count_token, count_words

from models.seesaw import Seesaw
from videos.takes import Playground

MODULE = "fixtures/project/videos/tour/stage.tsx"


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


class Bill(Set):
    module = MODULE
    series = "FIXTURE SERIES"
    stage = Slot()
    headline = Slot()
    aside = Slot()


class BillSplit(Bill):
    left = Slot()
    right = Slot()
    headline = Slot()


class Card(Element):
    module = MODULE
    light = Action(item=str)
    weigh = Action(kilograms=float, count=int, loud=bool)


##############################################
# Sets

def test_a_project_sets_kind_is_its_class_names_slug():
    assert Bill.kind == 'bill' and BillSplit.kind == 'bill-split'

    class HTMLCard(Set):
        module = MODULE
    assert HTMLCard.kind == 'html-card'


def test_a_set_may_write_its_kind():
    class Wide(Set):
        module = MODULE
        kind = "wide-screen"
    assert Wide.kind == 'wide-screen'


def test_a_derived_set_has_its_own_slots_its_base_and_its_bases_module():
    assert list(BillSplit.slots()) == ['left', 'right', 'headline']
    assert list(Bill.slots()) == ['stage', 'headline', 'aside']
    assert BillSplit.base() is Bill and Bill.base() is None
    # A derived set inherits its base's props, so the chrome it inherits reads them.
    assert BillSplit.props() == {'series': 'FIXTURE SERIES'} == Bill.props()


def test_the_shipped_sets():
    assert Frame.kind == 'frame' and list(Frame.slots()) == ['stage']
    assert Split.kind == 'split' and list(Split.slots()) == ['left', 'right']


def test_a_slot_does_not_know_what_it_holds():
    with refused('Stage', 'main', 'what it holds'):
        class Stage(Set):
            module = MODULE
            main = Slot("view")


def test_a_project_set_needs_its_module():
    with refused('Stage', 'module'):
        class Stage(Set):
            main = Slot()


def test_a_stage_module_is_typescript_or_javascript():
    with refused('Stage', 'stage.py', '.tsx'):
        class Stage(Set):
            module = "stage.py"
            main = Slot()


def test_a_set_prop_is_json():
    with refused('Stage', 'camera', 'JSON'):
        class Stage(Set):
            module = MODULE
            camera = Playground.far
            main = Slot()


def test_a_set_prop_is_json_all_the_way_down():
    with refused('Stage', 'colours', 'JSON'):
        class Stage(Set):
            module = MODULE
            colours = ["#fff", ("a", "tuple")]


def test_a_project_set_cannot_take_a_shipped_kind():
    with refused('Frame', 'frame', 'ships'):
        class Frame(Set):  # noqa: F811 - the project's own, refused
            module = MODULE


def test_a_written_kind_is_a_slug():
    with refused('Stage', 'Wide Screen', 'kind'):
        class Stage(Set):
            module = MODULE
            kind = "Wide Screen"


##############################################
# Elements and actions

def test_a_project_elements_kind_and_actions():
    assert Card.kind == 'card'
    assert Card.actions() == {'light': {'item': 'string'},
                              'weigh': {'kilograms': 'number', 'count': 'number', 'loud': 'boolean'}}


def test_an_action_parameter_of_an_unsupported_type():
    with refused('Jobs', 'light', 'job', 'str, int, float or bool'):
        class Jobs(Element):
            module = MODULE
            light = Action(job=list)


def test_a_project_element_needs_its_module():
    with refused('Jobs', 'module'):
        class Jobs(Element):
            light = Action(job=str)


def test_an_element_declares_no_plain_attributes():
    with refused('Jobs', 'colour', 'props'):
        class Jobs(Element):
            module = MODULE
            colour = "#237c86"


def test_a_project_element_does_not_derive_from_a_shipped_one():
    with refused('Wide', 'View'):
        class Wide(View):
            module = MODULE


def test_element_props_are_keyword_json():
    with refused('Card', 'positional'):
        Card(["Balance"])
    with refused('Card', 'items', 'JSON'):
        Card(items={"a", "set"})
    with refused('Card', 'items', 'no kind'):
        Card(items=None)


def test_an_action_call_checks_its_parameters_by_name():
    card = Card(items=["Balance"])
    assert card.light(item="Balance").params == {'item': 'Balance'}
    assert card.weigh(kilograms=2, count=3, loud=False).params == {'kilograms': 2, 'count': 3,
                                                                    'loud': False}
    with refused('Card', 'light', 'item', 'string'):
        card.light(item=2)
    with refused('Card', 'light', 'item', 'missing'):
        card.light()
    with refused('Card', 'light', 'colour', 'does not declare'):
        card.light(item="Balance", colour="red")
    with refused('Card', 'weigh', 'kilograms', 'number'):
        card.weigh(kilograms=True, count=3, loud=False)
    with refused('Card', 'weigh', 'count', 'whole number'):
        card.weigh(kilograms=1.0, count=2.5, loud=False)
    with refused('Card', 'light', 'keyword'):
        card.light("Balance")


def test_a_bare_element_is_refused():
    with refused('Element', 'subclass'):
        Element()


##############################################
# Chapters: placements

def test_a_well_formed_chapter_is_accepted():
    class Fine(Chapter):
        lines = Narration("A seesaw. But it tips.")
        view = View(Playground, camera=Playground.far)
        hook = Shot(Frame, {Frame.stage: view}, until=lines.spoken("But"),
                    model=Playground.run(0, 2))
    assert issubclass(Fine, Chapter)


def test_slots_may_stay_empty():
    class Sparse(Chapter):
        lines = Narration("A seesaw.")
        view = View(Playground, camera=Playground.far)
        hook = Shot(BillSplit, {BillSplit.right: view}, until=lines.end(),
                    model=Playground.run(0, 2))
    assert Sparse._compiled['shots'][0]['places'] == {'right': 'view'}


def test_unknown_slot_of_the_shots_set():
    with refused('Question', 'hook', 'stage', 'Split', 'left', 'right'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Split, {Frame.stage: view}, until=lines.end(), model=Playground.run(0, 2))


def test_a_derived_set_does_not_inherit_its_bases_slots():
    with refused('Question', 'hook', 'stage', 'BillSplit', 'left, right, headline'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(BillSplit, {BillSplit.stage: view}, until=lines.end(),
                        model=Playground.run(0, 2))


def test_slot_filled_twice():
    with refused('Question', 'hook', 'stage', 'twice'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            one = View(Playground, camera=Playground.far)
            two = View(Playground, camera=Playground.near)
            hook = Shot(Frame, {Frame.stage: one, Frame.stage: two},  # noqa: F601
                        until=lines.end(), model=Playground.run(0, 2))


def test_element_the_chapter_does_not_declare():
    with refused('Question', 'hook', 'stage', 'does not declare'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            hook = Shot(Frame, {Frame.stage: View(Playground, camera=Playground.far)},
                        until=lines.end(), model=Playground.run(0, 2))


def test_element_placed_in_two_slots():
    with refused('Question', 'hook', 'view', 'two slots', 'left', 'right'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Split, {Split.left: view, Split.right: view}, until=lines.end(),
                        model=Playground.run(0, 2))


def test_a_shot_names_a_set():
    with refused('Question', 'hook', 'set'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot("frame", {}, until=lines.end(), model=Playground.run(0, 2))


##############################################
# Chapters: anchors, marks, cameras

def test_phrase_absent_from_the_narration():
    with refused('Question', 'hook', 'until', 'Buut', 'absent'):
        class Question(Chapter):
            lines = Narration("A seesaw can tip. But how?")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Frame, {Frame.stage: view}, until=lines.spoken("Buut"),
                        model=Playground.run(0, 2))


def test_phrase_repeated_in_the_narration():
    with refused('Drive', 'wheel', 'cues[0]', "'wheel'", 'ambiguous'):
        class Drive(Chapter):
            lines = Narration("The wheel turns the waterwheel.")
            view = View(Playground, camera=Playground.far)
            wheel = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2),
                         cues=[Cue(lines.spoken("wheel"), view.highlight(Seesaw.beam),
                                   until=lines.end())])


def test_anchor_from_another_chapters_narration():
    other = Narration("Another narration entirely.")
    with refused('Question', 'hook', 'until', 'another'):
        class Question(Chapter):
            lines = Narration("A seesaw. Another narration entirely.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Frame, {Frame.stage: view}, until=other.spoken("Another"),
                        model=Playground.run(0, 2))


def test_unknown_mark():
    with refused('Feed', 'pawls', 'rize', 'rise'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                         model=Playground.keys({0: "rize", lines.end(): "top"}))


def test_model_keys_without_the_shots_start():
    with refused('Feed', 'pawls', 'start'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                         model=Playground.keys({lines.spoken("Watch"): "rise", lines.end(): "top"}))


def test_model_keys_without_the_shots_end():
    with refused('Feed', 'pawls', 'end', 'until'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Frame, {Frame.stage: view}, until=lines.end(plus=0.8),
                         model=Playground.keys({0: "rise", lines.end(): "top"}))


class Elsewhere(Loop):
    model = Seesaw
    export = "../export/seesaw"
    marks = {}
    readiness = "A second take, for the refusals."
    faraway = Camera(position=(1, 2, 3), target=(0, 0, 0), fov=30)


def test_view_on_a_camera_of_another_take():
    with refused('Question', 'view', 'faraway', 'Elsewhere', 'Playground'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Elsewhere.faraway)


def test_move_to_a_camera_of_another_take():
    with refused('Question', 'hook', 'faraway', 'Playground'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                        model=Playground.run(0, 2),
                        cues=[Cue(0, view.move(Elsewhere.faraway, until=lines.end()))])


def test_a_mark_name_is_an_identifier():
    with refused('Marked', 'pull-start'):
        class Marked(Loop):
            model = Seesaw
            export = "../export/seesaw"
            marks = {"pull-start": 1}
            readiness = "Marks with hyphens."


##############################################
# Cues and actions

def test_cue_on_an_element_the_shot_does_not_place():
    with refused('Drive', 'wheel', 'code', 'does not place'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            wheel = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2),
                         cues=[Cue(0, code.type(through_line=24, over=1))])


@pytest.mark.parametrize('make', [
    lambda view, card, title: view.highlight(Seesaw.beam),
    lambda view, card, title: view.ring(Seesaw.beam),
    lambda view, card, title: view.label(Seesaw.beam, "Beam"),
    lambda view, card, title: view.arrow(Seesaw.beam, "Beam", place=(0.1, 0.1)),
    lambda view, card, title: title.show(),
    lambda view, card, title: card.light(item="x"),
], ids=['highlight', 'ring', 'label', 'arrow', 'show', 'light'])
def test_a_spanning_action_needs_the_cues_until(make):
    view = View(Playground, camera=Playground.far)
    card = Card(items=["x"])
    title = Title("Beam")
    action = make(view, card, title)
    with refused('Drive', 'wheel', 'cues[0]', action.name, 'until'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            mill = view
            tally = card
            heading = title
            wheel = Shot(Bill, {Bill.stage: view, Bill.aside: card, Bill.headline: title},
                         until=lines.end(), model=Playground.run(0, 2), cues=[Cue(0, action)])


def test_actions_that_finish_on_their_own_need_no_until():
    class Drive(Chapter):
        lines = Narration("The beam rests on its pivot.")
        view = View(Playground, camera=Playground.far)
        code = Source.panel(Playground.declaration)
        wheel = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(),
                     model=Playground.run(0, 2),
                     cues=[Cue(0, code.type(through_line=24, over=1)),
                           Cue(0, view.move(Playground.near, until=lines.end()))])
    cues = Drive._compiled['shots'][0]['cues']
    assert cues == [{'at': 0, 'actions': [{'element': 'code', 'action': 'type',
                                           'throughLine': 24, 'over': 1}]},
                    {'at': 0, 'actions': [{'element': 'view', 'action': 'move', 'camera': 'near',
                                           'until': {'narrationEnd': True}}]}]


def test_the_end_of_the_narration_is_its_own_anchor_and_names_no_phrase():
    # Wart 2 of Cut and Advance: the end was the shortest unique tail of the
    # last words, a phrase the author never wrote, which grows when the last
    # words repeat earlier ones ("Down. Up" here).
    class Rhythm(Chapter):
        lines = Narration("Up. Down. Up.")
        view = View(Playground, camera=Playground.far)
        beat = Shot(Frame, {Frame.stage: view}, until=lines.end(plus=0.9),
                    model=Playground.run(0, 2),
                    cues=[Cue(0, view.move(Playground.near, until=lines.end()))])
    shot = Rhythm._compiled['shots'][0]
    assert shot['until'] == {'narrationEnd': True, 'plus': 0.9}
    assert shot['cues'][0]['actions'][0]['until'] == {'narrationEnd': True}


def test_a_label_does_not_draw_in():
    with refused('label', 'draw', 'fade'):
        View(Playground, camera=Playground.far).label(Seesaw.beam, "Beam", enter=("draw", 0.5))


def test_a_ring_draws_in():
    view = View(Playground, camera=Playground.far)
    assert view.ring(Seesaw.beam, enter=("draw", 0.5)).fields['enter'] == {'kind': 'draw',
                                                                           'duration': 0.5}


def test_unknown_easing():
    with refused('bounce', 'linear, smooth, in, out or in-out'):
        View(Playground, camera=Playground.far).move(Playground.near, ease="bounce", until=1)


def test_a_picture_shows_a_still_and_fits_it():
    with refused('Picture', 'fit', 'stretch'):
        Picture(Playground.plate, fit="stretch")
    with refused('Picture', 'Still'):
        Picture("plate.png")


def test_a_spoken_reveal_needs_the_title_in_the_narration():
    with refused('Closing', 'rhythm', 'Cut. Advance.', 'absent'):
        class Closing(Chapter):
            lines = Narration("Up and down.")
            view = View(Playground, camera=Playground.far)
            beat = Title("Cut. Advance.")
            rhythm = Shot(Bill, {Bill.stage: view, Bill.headline: beat}, until=lines.end(),
                          model=Playground.run(0, 2),
                          cues=[Cue(0, beat.show(reveal=Reveal.spoken()), until=lines.end())])


##############################################
# Emphasis

def emphasis_chapter(anchor, *words, lines="The stand holds the beam and its pivot."):
    narration = Narration(lines)

    class Drive(Chapter):
        text = narration
        view = View(Playground, camera=Playground.far)
        code = Source.panel(Playground.declaration)
        coupling = Shot(Split, {Split.left: code, Split.right: view}, until=narration.end(),
                        model=Playground.run(0, 2),
                        cues=[Cue(0, code.type(through_line=24, over=1)),
                              Cue(anchor(narration), code.emphasize(*words))])
    return Drive


def test_emphasis_words_and_pairs():
    chapter = emphasis_chapter(lambda n: n.spoken("holds the beam"), "beam", ("holds", "Stand"))
    action = chapter._compiled['shots'][0]['cues'][1]['actions'][0]
    assert action == {'element': 'code', 'action': 'emphasize',
                      'words': [{'spoken': 'beam', 'token': 'beam'},
                                {'spoken': 'holds', 'token': 'Stand'}]}


def test_emphasis_needs_a_spoken_anchor():
    with refused('Drive', 'coupling', 'emphasize', 'spoken phrase'):
        emphasis_chapter(lambda n: 0.5, "beam")


def test_emphasis_anchor_has_no_plus():
    with refused('Drive', 'coupling', 'emphasize', 'plus'):
        emphasis_chapter(lambda n: n.spoken("the beam", plus=0.1), "beam")


def test_emphasis_anchor_is_not_a_phrase_end():
    with refused('Drive', 'coupling', 'emphasize', 'spoken phrase'):
        emphasis_chapter(lambda n: n.spoken_end("the beam"), "beam")


def test_a_spoken_part_absent_from_the_phrase_is_refused_word_bounded():
    # 'bea' is inside 'beam' but is not a word of the phrase.
    with refused('Drive', 'coupling', 'cues[1]', "'bea'", 'absent', 'the beam'):
        emphasis_chapter(lambda n: n.spoken("the beam"), ("bea", "beam"))


def test_a_spoken_part_repeated_in_the_phrase():
    with refused('Drive', 'coupling', "'the'", 'ambiguous', 'holds the beam and the pivot'):
        emphasis_chapter(lambda n: n.spoken("holds the beam and the pivot"), ("the", "beam"),
                         lines="The stand holds the beam and the pivot.")


def test_a_token_is_an_identifier():
    with refused('emphasize', 'feed pawl', 'token'):
        Source.panel(Playground.declaration).emphasize(("the pawl", "feed pawl"))
    with refused('emphasize', 'words'):
        Source.panel(Playground.declaration).emphasize(("only one",))


def test_words_and_tokens_are_bounded():
    assert count_words("the beam rests on the beams", "beam") == 1
    assert count_words("Up. Down.", "Up.") == 1
    # A dot is a boundary: a word inside a dotted path is a token, and a
    # dotted path is one token; an underscore or a digit binds.
    excerpt = ("cycle.drives(water_drive.waterwheel.spin)\n"
               "water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)\n"
               "(feed.pawl.turn, feed.pawl.shift_x, 3feed, pawl_mount)")
    assert count_token(excerpt, 'waterwheel') == 2
    assert count_token(excerpt, 'drives') == 2
    assert count_token(excerpt, 'crankshaft') == 1
    assert count_token(excerpt, 'water_drive.waterwheel.spin') == 2
    assert count_token(excerpt, 'water_drive.waterwheel.spin.drives') == 1
    assert count_token(excerpt, 'feed.pawl.turn') == 1
    assert count_token(excerpt, 'feed.pawl') == 2
    assert count_token(excerpt, 'pawl') == 2
    assert count_token(excerpt, 'feed') == 2
    assert count_token(excerpt, 'shift') == 0
    # Counting on one line of the excerpt, by file line number.
    assert count_token(excerpt_line(excerpt, 413, 414), 'waterwheel') == 1
    assert excerpt_line(excerpt, 413, 416) is None


##############################################
# Typing and state across a chapter

def test_typing_through_a_line_outside_the_excerpt():
    with refused('Drive', 'wheel', 'cues[0]', 'through_line', '22 to 24'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            code = Source.panel(Playground.declaration)
            wheel = Shot(Frame, {Frame.stage: code}, until=lines.end(), model=Playground.run(0, 2),
                         cues=[Cue(0, code.type(through_line=30, over=1))])


def test_a_placed_panel_is_typed_to_its_end():
    with refused('Drive', 'wheel', 'code', 'complete', '24'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            code = Source.panel(Playground.declaration)
            wheel = Shot(Frame, {Frame.stage: code}, until=lines.end(), model=Playground.run(0, 2),
                         cues=[Cue(0, code.type(through_line=23, over=1))])


def test_typing_runs_forward():
    with refused('Drive', 'wheel', 'cues[1]', 'through_line', 'already'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            code = Source.panel(Playground.declaration)
            wheel = Shot(Frame, {Frame.stage: code}, until=lines.end(), model=Playground.run(0, 2),
                         cues=[Cue(0, code.type(through_line=23, over=1)),
                               Cue(0.5, code.type(through_line=23, over=1))])


def test_a_completed_panel_needs_no_typing_in_a_later_shot():
    class Feed(Chapter):
        lines = Narration("The beam rests. On its pivot.")
        code = Source.panel(Playground.declaration)
        view = View(Playground, camera=Playground.far)
        pawls = Shot(Split, {Split.left: code, Split.right: view}, until=lines.spoken("On its"),
                     model=Playground.run(0, 2), cues=[Cue(0, code.type(through_line=24, over=1))])
        holding = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(),
                       model=Playground.run(2, 4))
    assert Feed._compiled['shots'][1]['cues'] == []


def test_a_completed_panel_is_not_typed_again():
    with refused('Feed', 'holding', 'code', 'already'):
        class Feed(Chapter):
            lines = Narration("The beam rests. On its pivot.")
            code = Source.panel(Playground.declaration)
            pawls = Shot(Frame, {Frame.stage: code}, until=lines.spoken("On its"),
                         model=Playground.run(0, 2), cues=[Cue(0, code.type(through_line=24, over=1))])
            holding = Shot(Frame, {Frame.stage: code}, until=lines.end(), model=Playground.run(2, 4),
                           cues=[Cue(0, code.type(through_line=24, over=1))])


##############################################
# Shots, chapters, movies

def test_shot_needs_model_time():
    with refused('Drive', 'wheel', 'model'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            wheel = Shot(Frame, {Frame.stage: view}, until=lines.end())


def test_attribute_that_is_not_a_slug():
    with refused('Drive', 'Wheel', 'lower-case'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            Wheel = Shot(Frame, {Frame.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2))


def test_chapter_needs_one_narration():
    with refused('Silent', 'Narration'):
        class Silent(Chapter):
            view = View(Playground, camera=Playground.far)


def test_misspelled_part_is_refused_where_it_is_written():
    # The framework refuses a path through the model at the line that
    # writes it, naming the written spelling.
    with pytest.raises(Exception, match=r'beam\.plonk'):
        Seesaw.beam.plonk


def test_style_colours():
    with refused('Style', 'accent', '#rrggbb'):
        Style(accent="teal")


class Short(Chapter):
    lines = Narration("A seesaw.")
    view = View(Playground, camera=Playground.far)
    whole = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Playground.run(0, 2))


def movie(**body):
    base = dict(title="Untitled", status="rehearsal", learning_goal="None.",
                format=Format(640, 360, fps=10),
                narrator=Narrator(provider="elevenlabs", model="eleven_v3", voice="v"))
    base.update(body)
    return type('Untitled', (Movie,), {k: v for k, v in base.items() if v is not None})


def test_movie_needs_a_format():
    with refused('Untitled', 'Format'):
        movie(format=None, only=Short())


def test_movie_needs_a_chapter():
    with refused('Untitled', 'Chapter'):
        movie()


def test_shot_ids_are_unique_across_the_movie():
    with refused('Untitled', 'whole', 'first', 'second', 'shot id'):
        movie(first=Short(), second=Short())


def test_an_elements_props_have_one_kind_in_a_movie():
    class One(Chapter):
        lines = Narration("One.")
        card = Card(items=["a"])
        one = Shot(Bill, {Bill.aside: card}, until=lines.end(), model=Playground.run(0, 1))

    class Two(Chapter):
        lines = Narration("Two.")
        card = Card(items="a")
        two = Shot(Bill, {Bill.aside: card}, until=lines.end(), model=Playground.run(1, 2))
    with refused('Untitled', 'card', 'items', 'list', 'string', 'one', 'two'):
        movie(one=One(), two=Two())


##############################################
# The reframe: a join that moves a view's box and fades the rest

def test_a_reframe_is_a_join_of_a_duration_and_an_easing():
    assert Reframe(0.8).document() == {'kind': 'reframe', 'duration': 0.8}
    assert Reframe(1.2, ease="in-out").document() == {'kind': 'reframe', 'duration': 1.2,
                                                      'ease': 'in-out'}
    with refused('Reframe', '0'):
        Reframe(0)
    with refused('sideways', 'Reframe'):
        Reframe(0.8, ease="sideways")
    # Only a wipe or a slide has a direction and only a fade a colour.
    with pytest.raises(TypeError):
        Reframe(0.8, direction="left")
    with pytest.raises(TypeError):
        Reframe(0.8, color="#000000")


def test_a_reframe_moves_a_view_both_shots_place():
    class Shrink(Chapter):
        lines = Narration("A seesaw. Then its declaration.")
        view = View(Playground, camera=Playground.far)
        code = Source.panel(Playground.declaration)
        whole = Shot(Frame, {Frame.stage: view}, until=lines.spoken("Then"),
                     model=Playground.run(0, 2))
        split = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(),
                     model=Playground.run(2, 4), transition=Reframe(0.8),
                     cues=[Cue(0, code.type(through_line=24, over=1))])
    assert Shrink._compiled['shots'][1]['transition'] == {'kind': 'reframe', 'duration': 0.8}


def test_a_reframe_without_a_view_in_both_shots_is_refused_naming_both():
    with refused('Lone', 'read', 'watch', 'transition', 'no view element in both'):
        class Lone(Chapter):
            lines = Narration("Watch it. Then read.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            watch = Shot(Frame, {Frame.stage: view}, until=lines.spoken("Then"),
                         model=Playground.run(0, 2))
            read = Shot(Frame, {Frame.stage: code}, until=lines.end(), model=Playground.run(2, 4),
                        transition=Reframe(0.8), cues=[Cue(0, code.type(through_line=24, over=1))])


def test_a_chapter_that_opens_with_a_reframe_is_refused_by_its_movie():
    class Before(Chapter):
        lines = Narration("A seesaw.")
        view = View(Playground, camera=Playground.far)
        before = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Playground.run(0, 2))

    class After(Chapter):
        lines = Narration("Again.")
        view = View(Playground, camera=Playground.far)
        after = Shot(Frame, {Frame.stage: view}, until=lines.end(), model=Playground.run(2, 4),
                     transition=Reframe(0.5))
    # The chapter alone is sound: its first shot's previous shot is not its own.
    assert After._compiled['shots'][0]['transition'] == {'kind': 'reframe', 'duration': 0.5}
    with refused('Untitled', 'after', 'before', 'no view element in both'):
        movie(first=Before(), second=After())
