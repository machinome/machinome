"""The fixture machines before the camera: the seesaw's posed loop, its
marks, cameras, layers, source excerpt and picture, and the counter's
clocked take. Declared once, used by every fixture movie."""

from machinome_movie import Camera, Layer, Loop, Mark, Move, Source, Still, Take, Trigger

from models.counter import Counter
from models.seesaw import Seesaw


class Playground(Loop):
    model = Seesaw
    export = "../export/seesaw"
    marks = {"rise": 5, "top": 10, "fall": 15}
    readiness = "Exported by machinome export; the beam tips on its pivot through the loop."
    far = Camera(position=(400, -600, 300), target=(0, 0, 50), fov=37)
    near = Camera(position=(200, -300, 150), target=(0, 0, 50), fov=37)
    side = Camera(position=(0, -500, 100), target=(0, 0, 50), fov=30)
    rolled = Camera(position=(-150, 250, 120), target=(0, 0, 60), up=(0.15, 0, 1), fov=42)
    ground = Layer(Seesaw.base)
    load = Layer(Seesaw.beam.plank, Seesaw.beam.weight)
    declaration = Source("../models/seesaw.py", lines=(22, 24))
    plate = Still("../media/plate.png", credit="Fixture drawing of a seesaw",
                  rights="Made for the Videomaker test suite", upscale=1.5)


class Turns(Take):
    model = Counter
    export = "../export/counter"
    readiness = "Exported by machinome export; the drums count the crank's turns and carry."
    steps = [Trigger("Turn once"), Mark("one"),
             Move(Counter.crank, to=3240, over=4), Mark("nine"),
             Trigger("Turn once"), Mark("ten")]
    front = Camera(position=(160, -260, 140), target=(0, 0, 20), fov=37)
    relations = Source("../models/counter.py", lines=(150, 153))
