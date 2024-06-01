from arcade import Window
from arcade.draw_commands import draw_rect_outline, draw_point
import arcade.color


class RectWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "Rect Demo")

        self.rectangle = self.rect.scale(0.75)

    def on_draw(self):
        draw_rect_outline(self.rectangle, arcade.color.WHITE, 3)

    def on_update(self, delta_time: float):
        ...


def main():
    win = RectWindow()
    win.run()
