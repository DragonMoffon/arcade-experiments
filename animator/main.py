from arcade import SpriteList, Window
from arcade import SpriteSolidColor

from animator.animator import DragonAnimator
from animator import lerp
from animator.rollingdigit import RollingDigit


class AnimWindow(Window):
    def __init__(self):
        super().__init__(1280, 720, "Animator Test")

        self.a_b: DragonAnimator[SpriteSolidColor] = DragonAnimator(("center_x", "center_y"), lerp.ease_quadinout)
        self.sprite = self.a_b.proxy(SpriteSolidColor(100, 100, 100, self.center_y))

        self.sprite_list = SpriteList()

        self.rolling_digits = [
            RollingDigit(place = 4, font_size = 72, center_x = self.center_x - 75, center_y = self.height * 0.75),
            RollingDigit(place = 3, font_size = 72, center_x = self.center_x - 25, center_y = self.height * 0.75),
            RollingDigit(place = 2, font_size = 72, center_x = self.center_x + 25, center_y = self.height * 0.75),
            RollingDigit(place = 1, font_size = 72, center_x = self.center_x + 75, center_y = self.height * 0.75)
        ]

        for rd in self.rolling_digits:
            self.sprite_list.append(rd)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(self.sprite.__dict__)
        self.sprite.center_x = self.width - 100

    def on_update(self, delta_time: float):
        self.a_b.update(delta_time)

        for rd in self.rolling_digits:
            rd.update(self.sprite.center_x)

        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.sprite.draw()
        self.sprite_list.draw()


def main():
    window = AnimWindow()
    window.run()
