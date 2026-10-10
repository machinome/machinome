"""Chapter 7: step it through a move."""
from machinome.simulation import Instruction

from .c06_fit import Counter as FittedCounter


class Counter(FittedCounter):

    instructions = {
        **FittedCounter.instructions,
        'Turn once': Instruction(by={'crank': 360.0}, duration=2.0),
    }
