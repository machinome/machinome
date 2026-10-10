"""pytest plugin: the sketch with every side test undecided (pure fallback)."""
import functools
import side as sketch
import machinome.engine.brep as brep
sketch.Boundary.side = lambda self, coords: None
brep._false_empty_witness = functools.partial(sketch.witness, mode='small-first')
