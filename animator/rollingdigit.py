import random

from arcade import Sprite, SpriteList, Text, Texture, get_window

from common.util import load_shared_sound

FONT_NAME = "GohuFont 11 Nerd Font Mono"


def get_digit(number: float, place: int, rolling = True) -> tuple[int, float]:
    i = (number % (10 ** place)) // (10 ** (place - 1))  # extract one digit from place in decimal number
    f = 0

    # This is technically the "correct" implementation to emulate a rolling digit, but it's unreadable at
    # extreme values. For instance, a "1" at 80% progess to "2" just looks like 2, because the 1 is off-screen
    # at that point.
    if rolling:
        f = number % (10 ** (place - 1)) / (10 ** (place - 1))

    return i, f


class RollingDigit(Sprite):
    def __init__(self, place: int = 1,
                 *, font_name: str = FONT_NAME, font_size: int = 22, scale: float = 1, center_x: float = 0, center_y: float = 0,
                 rolling = True, beep = False, **kwargs):
        self.place = place

        self._label = Text("0", 0, 0, font_size = font_size, font_name = font_name, anchor_y = "bottom")

        # These don't get used unless rolling is True
        self._prev_label = Text("0", 0, 0, font_size = font_size, font_name = font_name, anchor_y = "bottom")
        self._next_label = Text("0", 0, 0, font_size = font_size, font_name = font_name, anchor_y = "top")

        self._default_atlas = get_window().ctx.default_atlas

        # We need a random string here, and this has a 64-bit possibility for collision so that's prob fine
        random_hash = ''.join(random.choice('0123456789abcdef') for n in range(16))

        # We get the size of this from the size of the digit label
        self._tex = Texture.create_empty(f"rolling_digit_{random_hash}", (int(self._label.content_width + 1), int(self._label.content_height + 1)))
        self._default_atlas.add(self._tex)

        with self._default_atlas.render_into(self._tex):
            self._label.draw()

        self.rolling = rolling

        self._progress = 0.0

        self.beep = beep
        self.beep_sound = load_shared_sound("blip_e")

        self.prev_total = 0

        self.settling = False

        super().__init__(self._tex, scale, center_x, center_y, **kwargs)

    def update(self, delta_time: float, total: float):
        old_digit = self._label.text

        current, progress = get_digit(total, self.place, self.rolling)
        pre, nex = current - 1 % 10, current + 1 % 10

        self.settling = total == self.prev_total

        if self.settling:
            self._progress /= 1.1 * (delta_time * 60)
            self._progress = 0 if self._progress < 0.001 else self._progress
        else:
            self._progress = progress

        self._label.text = str(current)
        self._prev_label.text = str(pre)
        self._next_label.text = str(nex)

        if self._label.text != old_digit and self.beep:
            self.beep_sound.play()

        if self.rolling:
            self._label.y = self._tex.height * self._progress
            self._prev_label.y = self._label.top
            self._next_label.y = self._label.bottom
        else:
            self._label.y = 0

        with self._default_atlas.render_into(self._tex) as fbo:
            fbo.clear()
            self._label.draw()
            if self.rolling:
                self._prev_label.draw()
                self._next_label.draw()

        self.prev_total = total


class RollingDigitDisplay:
    def __init__(self, digits: int,
                 *, font_name: str = FONT_NAME, font_size: int = 22, scale: float = 1, center_x: float = 0, center_y: float = 0,
                 rolling = True, beep: int | None = None, **kwargs):

        self.sprite_list = SpriteList()

        self.rolling_digits: list[RollingDigit] = []
        w = font_size * 0.75  # ~approx
        total_w = w * (digits - 1)
        for n in range(digits, 0, -1):
            x = center_x + (total_w / 2) - (w * (n - 1))
            rd = RollingDigit(n, font_name = font_name, font_size = font_size, scale = scale, center_x = x, center_y = center_y,
                              rolling = rolling, beep = beep == n)
            self.rolling_digits.append(rd)
            self.sprite_list.append(rd)

    @property
    def rolling(self) -> bool:
        return self.rolling_digits[0].rolling

    @rolling.setter
    def rolling(self, v):
        for rd in self.rolling_digits:
            rd.rolling = v

    @property
    def beep(self) -> int | None:
        b = None
        for rd in self.rolling_digits:
            if rd.beep:
                b = rd.place
        return b

    @beep.setter
    def beep(self, v: int | None):
        for rd in self.rolling_digits:
            rd.beep = rd.place == v

    def update(self, delta_time: float, total: float):
        for rd in self.rolling_digits:
            rd.update(delta_time, total)

    def draw(self):
        self.sprite_list.draw()
