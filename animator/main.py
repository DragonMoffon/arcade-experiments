from arcade import Window
from arcade import SpriteSolidColor

from animator.animator import DragonAnimator
from animator import lerp


class AnimWindow(Window):
    def __init__(self):
        super().__init__(1280, 720, "Animator Test")

        self.a_b: DragonAnimator[SpriteSolidColor] = DragonAnimator(("center_x", "center_y"), lerp.ease_quadinout)
        self.sprite = self.a_b.proxy(SpriteSolidColor(100, 100, 100, self.center_y))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(self.sprite.__dict__)
        self.sprite.center_x = self.width - 100

    def on_update(self, delta_time: float):
        self.a_b.update(delta_time)
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.sprite.draw()


def main():
    window = AnimWindow()
    window.run()
