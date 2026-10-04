from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Printed
from machinome.production.material import Material
from machinome.production.mass import MeasuredMass, SolidMass
from machinome.production.instruction import Step, Markdown
from .model import Pair


class Draft(Production[Pair]):
    first = Item(
        Pair.first, Printed(Material("polymer", density_kg_m3=1000)), mass=SolidMass()
    )
    second = Item(
        Pair.second, Printed(), mass=MeasuredMass(3.5, evidence="measurement.md")
    )
    finish = Step(first, instructions=Markdown("finish.md"))
    assembly = Step(first, second, instructions=Markdown("assembly.md"))
