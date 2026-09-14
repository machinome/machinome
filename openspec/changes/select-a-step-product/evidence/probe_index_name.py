"""Probe: why the selector may not be spelled `index`.

`declarative._check_index` refuses to repeat a class that declares a
class attribute named `index`. A StepNode declaring `index = 2` as its
selector would therefore be unrepeatable -- and a repeated STEP part is
the ordinary case (the fourteen-bolt scenario of the step-assembly spec).
"""
from solid_node.node import AssemblyNode, StepNode


class Bolt(StepNode):
    step_source = 'tests/step_project/single_product.step'
    index = 2          # stands in for a selector spelled `index`


try:
    class Bracket(AssemblyNode):
        bolts = Bolt().repeat(14)
    print('repeat accepted -- no clash')
except TypeError as error:
    print('TypeError:', error)
