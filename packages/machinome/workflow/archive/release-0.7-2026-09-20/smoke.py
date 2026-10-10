"""Run with an isolated artifact installation, outside every source checkout."""
import importlib.metadata as metadata
from importlib.machinery import PathFinder
import json
from pathlib import Path
import subprocess
import sys

import machinome
import machinome_mechanics as mechanics
import machinome_viewer
from build123d import Box
from cadquery import Workplane
from solid2 import get_animation_time
from solid2.core.object_base import OpenSCADConstant
from machinome.simulation import Play, Sim

expected = {"machinome": "0.7.0", "machinome-viewer": "0.2.0",
            "machinome-mechanics": "0.1.0"}
for name, version in expected.items():
    assert metadata.version(name) == version
for module in (machinome, mechanics, machinome_viewer):
    assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix)), module
assert PathFinder.find_spec("machinome.mechanisms", machinome.__path__) is None
assert len(mechanics.__all__) == 12
assert mechanics.screw_travel(360, 2) == 2
assert mechanics.piston_height(0, 15, 60) == 75
assert mechanics.circle_intersection((0, 0), 5, (8, 0), 5) == (4, 3)
assert isinstance(mechanics.piston_height(get_animation_time(), 15, 60),
                  OpenSCADConstant)
assert abs(Box(2, 3, 4).volume - 24) < 1e-8
assert abs(Workplane().box(2, 3, 4).val().Volume() - 24) < 1e-8
result = subprocess.run([str(Path(sys.executable).with_name("machinome")), "viewer"],
                        check=True, capture_output=True, text=True)
viewer = json.loads(result.stdout)
assert viewer["apiVersion"] == 22, viewer
assert viewer["documentVersions"] == list(range(1, 10)), viewer
assert viewer["version"] == "0.2.0", viewer
assert Path(viewer["path"]).is_file(), viewer
assert Path(viewer["index"]).is_file(), viewer
print(json.dumps({"versions": expected, "viewer": viewer}, indent=2))
print("Installed CAD, numeric/symbolic mechanics, extraction boundary and CLI passed.")
