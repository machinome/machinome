"""pytest plugin: run the repository's witness tests against the sketch."""
import functools, os
import side as sketch
import machinome.engine.brep as brep
brep._false_empty_witness = functools.partial(sketch.witness, mode=os.environ.get('SKETCH_MODE', 'small-first'))
