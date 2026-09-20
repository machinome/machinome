"""Chapter 5: buttons."""
from machinome.simulation import Instruction

from .c04_relations import Counter as TallyCounter


class Counter(TallyCounter):

    instructions = {
        'Rest': Instruction({'crank': 0.0}, duration=1.0),
        'Count to ten': Instruction({'crank': 3600.0}, duration=5.0),
    }
