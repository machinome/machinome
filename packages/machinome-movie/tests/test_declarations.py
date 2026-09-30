"""Layer 1: the declarations refuse by name when the class is created.

Each test declares a chapter or a movie inline and asserts that the refusal
names what is wrong: the chapter, the shot, the field, the phrase, the mark,
the camera, the slot.
"""

import pytest

from machinome_movie import (Camera, Chapter, Cue, Element, Format, Loop,
                             Movie, MovieError, Narration, Narrator, Paper,
                             PaperSplit, Set, Shot, Source, Title, View)

from models.seesaw import Seesaw
from videos.takes import Playground


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


def test_a_well_formed_chapter_is_accepted():
    class Fine(Chapter):
        lines = Narration("A seesaw. But it tips.")
        view = View(Playground, camera=Playground.far)
        hook = Shot(Paper, {Paper.stage: view}, until=lines.spoken("But"),
                    model=Playground.run(0, 2))
    assert issubclass(Fine, Chapter)


def test_unknown_slot_of_the_shots_set():
    with refused('Question', 'hook', 'stage', 'PaperSplit', 'left', 'right'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            hook = Shot(PaperSplit, {Paper.stage: view, PaperSplit.left: code},
                        until=lines.end(), model=Playground.run(0, 2))


def test_slot_filled_twice():
    with refused('Question', 'hook', 'stage', 'twice'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            one = View(Playground, camera=Playground.far)
            two = View(Playground, camera=Playground.near)
            hook = Shot(Paper, {Paper.stage: one, Paper.stage: two},
                        until=lines.end(), model=Playground.run(0, 2))


def test_slot_left_empty():
    with refused('Question', 'hook', 'left'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(PaperSplit, {PaperSplit.right: view},
                        until=lines.end(), model=Playground.run(0, 2))


def test_slot_holding_the_wrong_element():
    with refused('Question', 'hook', 'left', 'source panel'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            hook = Shot(PaperSplit, {PaperSplit.left: view, PaperSplit.right: code},
                        until=lines.end(), model=Playground.run(0, 2))


def test_element_the_chapter_does_not_declare():
    with refused('Question', 'hook', 'stage', 'does not declare'):
        class Question(Chapter):
            lines = Narration("A seesaw.")
            hook = Shot(Paper, {Paper.stage: View(Playground, camera=Playground.far)},
                        until=lines.end(), model=Playground.run(0, 2))


def test_phrase_absent_from_the_narration():
    with refused('Question', 'hook', 'until', 'Buut'):
        class Question(Chapter):
            lines = Narration("A seesaw can tip. But how?")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Paper, {Paper.stage: view}, until=lines.spoken("Buut"),
                        model=Playground.run(0, 2))


def test_phrase_repeated_in_the_narration():
    with refused('Drive', 'wheel', 'cues[0]', "'wheel'", '2 times'):
        class Drive(Chapter):
            lines = Narration("The wheel turns the waterwheel.")
            view = View(Playground, camera=Playground.far)
            wheel = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2),
                         cues=[Cue(lines.spoken("wheel"), Title("Wheel"), until=lines.end())])


def test_anchor_from_another_chapters_narration():
    other = Narration("Another narration entirely.")
    with refused('Question', 'hook', 'until', 'another'):
        class Question(Chapter):
            lines = Narration("A seesaw. Another narration entirely.")
            view = View(Playground, camera=Playground.far)
            hook = Shot(Paper, {Paper.stage: view}, until=other.spoken("Another"),
                        model=Playground.run(0, 2))


def test_unknown_mark():
    with refused('Feed', 'pawls', 'rize', 'rise'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.keys({0: "rize", lines.end(): "top"}))


def test_model_keys_without_the_shots_start():
    with refused('Feed', 'pawls', 'start'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.keys({lines.spoken("Watch"): "rise", lines.end(): "top"}))


def test_model_keys_without_the_shots_end():
    with refused('Feed', 'pawls', 'end', 'until'):
        class Feed(Chapter):
            lines = Narration("Watch it rise.")
            view = View(Playground, camera=Playground.far)
            pawls = Shot(Paper, {Paper.stage: view}, until=lines.end(plus=0.8),
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
            hook = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                        model=Playground.run(0, 2),
                        cues=[Cue(0, view.move(Elsewhere.faraway, until=lines.end()))])


def test_project_defined_set():
    with refused('Stage', 'does not exist yet'):
        class Stage(Set):
            pass


def test_project_defined_element():
    with refused('ForceArrows', 'does not exist yet'):
        class ForceArrows(Element):
            pass


def test_emphasis_needs_a_spoken_anchor():
    with refused('Drive', 'coupling', 'emphasize', 'spoken phrase'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            coupling = Shot(PaperSplit, {PaperSplit.left: code, PaperSplit.right: view},
                            until=lines.end(), model=Playground.run(0, 2),
                            cues=[Cue(0, code.type(through_line=24, over=1)),
                                  Cue(0.5, code.emphasize("beam"))])


def test_cue_on_an_element_the_shot_does_not_place():
    with refused('Drive', 'wheel', 'code', 'does not place'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            wheel = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2),
                         cues=[Cue(0, code.type(through_line=24, over=1))])


def test_span_cue_needs_until():
    with refused('Drive', 'wheel', 'cues[0]', 'until'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            wheel = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2),
                         cues=[Cue(0, view.highlight(Seesaw.beam))])


def test_placed_panel_needs_typing():
    with refused('Drive', 'coupling', 'code', 'typ'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            code = Source.panel(Playground.declaration)
            coupling = Shot(PaperSplit, {PaperSplit.left: code, PaperSplit.right: view},
                            until=lines.end(), model=Playground.run(0, 2))


def test_shot_needs_model_time():
    with refused('Drive', 'wheel', 'model'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            wheel = Shot(Paper, {Paper.stage: view}, until=lines.end())


def test_attribute_that_is_not_a_slug():
    with refused('Drive', 'Wheel', 'lower-case'):
        class Drive(Chapter):
            lines = Narration("The beam rests on its pivot.")
            view = View(Playground, camera=Playground.far)
            Wheel = Shot(Paper, {Paper.stage: view}, until=lines.end(),
                         model=Playground.run(0, 2))


def test_unknown_easing():
    with refused('bounce', 'linear, smooth, in, out or in-out'):
        View(Playground, camera=Playground.far).move(Playground.near, ease="bounce", until=1)


def test_subtitle_belongs_to_a_title():
    with refused('subtitle', 'top'):
        Title("Pull", position="top", subtitle="one tooth")


def test_chapter_needs_one_narration():
    with refused('Silent', 'Narration'):
        class Silent(Chapter):
            view = View(Playground, camera=Playground.far)


def test_misspelled_part_is_refused_where_it_is_written():
    # The framework refuses a path through the model at the line that
    # writes it, naming the written spelling.
    with pytest.raises(Exception, match=r'beam\.plonk'):
        Seesaw.beam.plonk


class Short(Chapter):
    lines = Narration("A seesaw.")
    view = View(Playground, camera=Playground.far)
    whole = Shot(Paper, {Paper.stage: view}, until=lines.end(), model=Playground.run(0, 2))


def test_movie_needs_a_format():
    with refused('Untitled', 'Format'):
        class Untitled(Movie):
            title = "Untitled"
            status = "rehearsal"
            learning_goal = "None."
            narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
            only = Short()


def test_movie_needs_a_chapter():
    with refused('Empty', 'Chapter'):
        class Empty(Movie):
            title = "Empty"
            status = "rehearsal"
            learning_goal = "None."
            format = Format(640, 360, fps=10)
            narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")


def test_shot_ids_are_unique_across_the_movie():
    with refused('Twice', 'whole', 'first', 'second'):
        class Twice(Movie):
            title = "Twice"
            status = "rehearsal"
            learning_goal = "None."
            format = Format(640, 360, fps=10)
            narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="v")
            first = Short()
            second = Short()
