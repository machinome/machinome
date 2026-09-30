"""A tour of every construct the validation film uses, on the seesaw."""

from machinome_movie import (Arrow, Chapter, Credits, Cue, Dissolve, Evidence,
    FadeIn, FadeOut, Format, Label, Movie, Narration, Narrator, Paper,
    PaperSplit, Release, Reveal, Ring, Shot, Source, Title, View, Wipe)

from models.seesaw import Seesaw
from videos.takes import Playground

fixture_voice = Narrator(provider="elevenlabs", model="eleven_v3", voice="fixture-voice",
                         label="Fixture", output="pcm_24000",
                         settings={"stability": 0.5, "similarity_boost": 0.75},
                         direction="Plain and unhurried.")


class Opening(Chapter):
    lines = Narration("A seesaw balances a beam on a stand. How does the weight tip it?")
    wide = View(Playground, camera=Playground.far)
    hook = Shot(Paper, {Paper.stage: wide}, until=lines.spoken("How"), fade_in=FadeIn(1.0),
                model=Playground.run(0, 4),
                cues=[Cue(0, wide.move(Playground.near, ease="out", until=lines.spoken("How")))])
    question = Shot(Paper, {Paper.stage: wide}, until=lines.end(plus=0.8),
                    model=Playground.run(4, 8),
                    cues=[Cue(0, Title("SEESAW", subtitle="One beam, one stand",
                                       enter=0.6, leave=0.6), until=lines.end())])


class Balance(Chapter):
    lines = Narration("""A stand carries the plank. In the source, the beam rests
                         on its pivot. The weight pushes one end down.""")
    mill = View(Playground, camera=Playground.side, hide=[Playground.ground])
    code = Source.panel(Playground.declaration)
    holds = Shot(Paper, {Paper.stage: mill}, until=lines.spoken("In the source"),
                 model=Playground.run(8, 10))
    source = Shot(PaperSplit, {PaperSplit.left: code, PaperSplit.right: mill},
                  until=lines.spoken("The weight"), transition=Dissolve(0.6),
                  model=Playground.run(10, 12),
                  cues=[Cue(0, code.type(through_line=24, over=1.2)),
                        Cue(lines.spoken("beam"), mill.highlight(Seesaw.beam, others="ghost"),
                            until=lines.spoken("pivot")),
                        Cue(lines.spoken("pivot"), mill.highlight(Seesaw.beam.pivot, others="ghost"),
                            until=lines.spoken("The weight")),
                        Cue(lines.spoken("the beam rests on its pivot"),
                            code.emphasize("beam"))])
    push = Shot(Paper, {Paper.stage: mill}, until=lines.end(plus=0.6),
                transition=Wipe(0.6, direction="right"), model=Playground.run(12, 16),
                cues=[Cue(0, mill.move(Playground.near, ease="smooth", until=lines.end())),
                      Cue(lines.spoken("The weight"),
                          Arrow(Seesaw.beam.weight, "Weight", place=(0.2, 0.25),
                                enter=("draw", 0.8), leave=("fade", 0.4)),
                          until=lines.end(plus=0.6))])


class Tip(Chapter):
    lines = Narration("Watch the plank rise and fall. On the way down, the stand takes the load. "
                      "Up. Down. Explore the model.")
    close = View(Playground, camera=Playground.near, hide=[Playground.ground])
    wide = View(Playground, camera=Playground.far, hide=[Playground.ground, Playground.load])
    rise = Shot(Paper, {Paper.stage: close}, until=lines.spoken("Up."),
                model=Playground.keys({0: "rise", lines.spoken("On the way down"): ("top", "out"),
                                       lines.spoken("Up."): "fall"}),
                cues=[Cue(0, Title("Rise", position="top"), until=lines.spoken("On the way down")),
                      Cue(lines.spoken("the plank"),
                          Ring(Seesaw.beam.plank, enter=("draw", 0.8), leave=("fade", 0.4)),
                          Label(Seesaw.beam.plank, "Plank", offset=(0.12, -0.08),
                                enter=("fade", 0.4), leave=("fade", 0.4)),
                          close.highlight(Seesaw.beam.plank, Seesaw.beam.weight, others="ghost"),
                          until=lines.spoken("On the way down")),
                      Cue(lines.spoken("On the way down"), Title("Fall", position="top"),
                          until=lines.spoken("Up.")),
                      Cue(lines.spoken("the stand"),
                          Ring(Seesaw.stand, enter=("draw", 0.8)),
                          Label(Seesaw.stand, "Stand", offset=(0.12, 0.08), enter=("fade", 0.4)),
                          close.highlight(Seesaw.stand, others="dim"),
                          until=lines.spoken("Up."))])
    rhythm = Shot(Paper, {Paper.stage: close}, until=lines.spoken("Explore"),
                  transition=Dissolve(0.6), model=Playground.run(16, 17),
                  cues=[Cue(0, close.move(Playground.rolled, ease="smooth", until=lines.spoken("Explore"))),
                        Cue(0, Title("Up. Down.", position="top", reveal=Reveal.spoken()),
                            until=lines.spoken("Explore"))])
    still = Shot(Paper, {Paper.stage: close}, until=lines.spoken("the model"),
                 model=Playground.run(17, 18),
                 cues=[Cue(0, Playground.plate.show(area="frame", fit="contain", enter=0.5, leave=0.5,
                                                    view=[(0, (0.5, 0.5), 1.0),
                                                          (lines.spoken("the model", plus=-0.2),
                                                           (0.5, 0.42), 1.4, "in-out")]),
                           until=lines.spoken("the model"))])
    invitation = Shot(Paper, {Paper.stage: wide}, until=lines.end(plus=1.2),
                      transition=Dissolve(0.6), fade_out=FadeOut(1.2), model=Playground.run(18, 19),
                      cues=[Cue(0, wide.highlight(Seesaw.beam, others="dim"), until=lines.end(plus=1.2))])


class Tour(Movie):
    title = "Tour"
    series = "VIDEOMAKER · FIXTURES"
    status = "rehearsal"
    learning_goal = "Exercise every construct the validation film uses."
    format = Format(1280, 720, fps=30)
    narrator = fixture_voice
    style = Paper.style(background="#faf7ef", foreground="#222222", accent="#237c86",
                        font="DejaVu Sans, sans-serif", safe_inset=0.08)
    evidence = Evidence(model="../../models/seesaw.py")
    credits = Credits(project="Videomaker fixtures", creator="The Videomaker test suite",
                      copyright="No copyright is claimed for this fixture",
                      license="None", license_file="../../NOTICE")
    release = Release(simulation_url=None, source_url=None, description="description.md")
    opening = Opening()
    balance = Balance()
    tip = Tip()
