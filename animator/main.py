from arcade import Window
from arcade import SpriteSolidColor

from animator.animator import Animator


class AnimWindow(Window):
    def __init__(self):
        super().__init__(1280, 720, "Animator Test")

        self.sprite = SpriteSolidColor(100, 100, 100, self.center_y)
        self.animator = Animator([self.sprite], "center_x")

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(self.sprite.__dict__)
        self.sprite.center_x = self.width - 100

    def on_update(self, delta_time: float):
        self.animator.update(delta_time)
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.sprite.draw()


def main():
    window = AnimWindow()
    window.run()
