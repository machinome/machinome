"""Chapter 6: prove the fit."""
from .c03_dimensions import DRUM_RADIUS, POST_DEPTH
from .c05_buttons import Counter as ButtonedCounter


class Counter(ButtonedCounter):

    def check(self):
        super().check()
        if self.post_offset - POST_DEPTH / 2 <= DRUM_RADIUS:
            raise ValueError(
                f'{self.name}: a post {self.post_offset} mm from the axis '
                f'cuts into drums of radius {DRUM_RADIUS} mm')
