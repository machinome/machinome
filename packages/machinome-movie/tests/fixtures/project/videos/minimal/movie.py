"""The smallest movie: one chapter, one shot on the shipped Frame, no cues."""

from machinome_movie import Chapter, Format, Frame, Movie, Narration, Narrator, Shot, View

from videos.takes import Playground


class Only(Chapter):
    lines = Narration("A seesaw.")
    view = View(Playground, camera=Playground.far)
    whole = Shot(Frame, {Frame.stage: view}, until=lines.end(plus=0.5),
                 model=Playground.run(0, 2))


class Minimal(Movie):
    title = "Minimal"
    status = "rehearsal"
    learning_goal = "Show the smallest movie that evaluates."
    format = Format(640, 360, fps=10)
    narrator = Narrator(provider="elevenlabs", model="eleven_v3", voice="fixture-voice")
    only = Only()
