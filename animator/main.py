from arcade import SpriteSolidColor, Window
import arcade.key

from animator.animator import DragonAnimator
from animator import lerp
from animator.rollingdigit import RollingDigitDisplay


class AnimWindow(Window):
    def __init__(self):
        super().__init__(1280, 720, "Animator Test")

        self.a_b: DragonAnimator[SpriteSolidColor] = DragonAnimator(("center_x", "center_y"), lerp.ease_quadinout)
        self.sprite = self.a_b.proxy(SpriteSolidColor(100, 100, 100, self.center_y))

        self.rolling_digits = RollingDigitDisplay(digits = 4, font_size = 72, center_x = self.center_x, center_y = self.height * 0.75, rolling = True, beep = 3)

        self.forward = False
        self.mouseing = False

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.rolling_digits.rolling = not self.rolling_digits.rolling
        elif symbol == arcade.key.M:
            self.mouseing = not self.mouseing
        elif symbol == arcade.key.SPACE or symbol == arcade.key.ENTER:
            self.forward = not self.forward

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.mouseing:
            self.sprite.center_x = x

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.forward:
            self.sprite.center_x = self.width - 100
        else:
            self.sprite.center_x = 100

        self.forward = not self.forward

    def on_update(self, delta_time: float):
        self.a_b.update(delta_time)
        self.rolling_digits.update(delta_time, self.sprite.center_x)

        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.sprite)
        self.rolling_digits.draw()


def main():
    window = AnimWindow()
    window.run()
