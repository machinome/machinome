"""A clocked take on screen: the counter turns once, eight more times to
nine, and carries, on the shipped Frame and Split, with its relations typed
beside it."""

from machinome_movie import (Chapter, Cue, Dissolve, Format, Frame, Movie, Narration, Narrator,
                             Shot, Source, Split, View)

from models.counter import Counter
from videos.takes import Turns


class Counting(Chapter):
    lines = Narration("""Turn the crank once and the units drum shows one. Eight more
                         turns bring it to nine. On the tenth turn the counter commits
                         a carry: the units return to zero and the tens show one.""")
    view = View(Turns, camera=Turns.front)
    code = Source.panel(Turns.relations)
    once = Shot(Frame, {Frame.stage: view}, until=lines.spoken("Eight more"),
                model=Turns.run(0, "one"))
    nine = Shot(Frame, {Frame.stage: view}, until=lines.spoken("On the tenth turn"),
                model=Turns.run("one", "nine"))
    carry = Shot(Split, {Split.left: code, Split.right: view}, until=lines.end(plus=0.5),
                 transition=Dissolve(0.5), model=Turns.run("nine", "ten"),
                 cues=[Cue(0, code.type(through_line=153, over=1.0)),
                       Cue(lines.spoken("commits a carry"), code.emphasize("commits", hold=0.5)),
                       Cue(lines.spoken("the tens show one"), view.highlight(Counter.tens_drum, others="ghost"),
                           until=lines.end())])


class Count(Movie):
    title = "Count"
    status = "rehearsal"
    learning_goal = "Film a clocked take: a counter counts its turns and carries."
    format = Format(640, 360, fps=10)
    narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="fixture-voice")
    counting = Counting()
