"""The seesaw before the camera: the posed loop, its marks, cameras, layers,
source excerpt and picture. Declared once, used by every fixture movie."""

from machinome_movie import Camera, Layer, Loop, Source, Still

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
