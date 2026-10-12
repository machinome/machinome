from machinome.node import AssemblyNode
from machinome.parameters import Angle, Count
from machinome_mechanics import meshed_angle


class GearPair(AssemblyNode):
    driver_teeth = Count(12)
    driven_teeth = Count(24)
    phase = Angle(0)
    initial_driven = meshed_angle(
        phase.value, driver_teeth.value, driven_teeth.value,
        driver_gap=180 / driver_teeth.value,
    )
