import random

from typing import Any
from arcade import Sprite, Text, Texture, get_window

FONT_NAME = "GohuFont 11 Nerd Font Mono"


def get_digit(number: float, place: int) -> tuple[int, float]:
    i = number % (10 ** place) // (10 ** (place - 1))
    f = (number % (10 ** (place - 1)) / (10 ** (place))) % 1.0
    return i, f


class RollingDigit(Sprite):
    def __init__(self, place: int = 1,
                 *, font_size: int = 22, scale: float = 1, center_x: float = 0, center_y: float = 0, angle: float = 0, **kwargs: Any):
        self.place = place

        self._label = Text("0", 0, 0, font_size = font_size, font_name = FONT_NAME, anchor_y = "bottom")

        self._prev_label = Text("0", 0, 0, font_size = font_size, font_name = FONT_NAME, anchor_y = "bottom")
        self._next_label = Text("0", 0, 0, font_size = font_size, font_name = FONT_NAME, anchor_y = "bottom")

        self._default_atlas = get_window().ctx.default_atlas
        random_hash = ''.join(random.choice('0123456789abcdef') for n in range(16))
        self._tex = Texture.create_empty(f"rolling_digit_{random_hash}", (int(self._label.content_width + 1), int(self._label.content_height + 1)))
        self._default_atlas.add(self._tex)

        with self._default_atlas.render_into(self._tex):
            self._label.draw()

        super().__init__(self._tex, scale, center_x, center_y, angle, **kwargs)

    def update(self, total: float):
        current, progress = get_digit(total, self.place)
        pre, nex = current - 1 % 10, current + 1 % 10

        self._label.text = str(current)
        self._prev_label.text = str(pre)
        self._next_label.text = str(nex)

        self._label.y = self._tex.height * progress
        self._prev_label.y = self._label.bottom - self._prev_label.content_height
        self._next_label.y = self._label.content_height

        with self._default_atlas.render_into(self._tex) as fbo:
            fbo.clear()
            self._label.draw()
            self._prev_label.draw()
            self._next_label.draw()
