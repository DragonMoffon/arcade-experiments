import importlib.resources as pkg_resources

import arcade
from pyglet.math import Vec2

from animator.lerp import ease_linear
import common.sfx
from dda2d.dda import Grid, dda

GRID_X_SIZE = 525
GRID_Y_SIZE = 525
GRID_TILE_SIZE = 25


def sound_loader(s: str) -> arcade.Sound:
    with pkg_resources.path(common.sfx, s + ".wav") as p:
        return arcade.Sound(p)


class Application(arcade.Window):
    def __init__(self):
        super().__init__(1280, 720, "DDA 2D")
        self.started = False
        self.local_time = 0.0

        self.grid = Grid(GRID_X_SIZE, GRID_Y_SIZE, GRID_TILE_SIZE,
                         (self.width - GRID_X_SIZE) / 2, (self.height - GRID_Y_SIZE) / 2 - 50)

        text_center_y = self.height - ((self.height - self.grid.max_y) / 2)
        self.text = arcade.Text("[LMB] to draw, [RMB] to clear",
                                self.center_x, text_center_y,
                                font_name="GohuFont 11 Nerd Font Mono", font_size=22,
                                anchor_x = "center", anchor_y = "center")

        with pkg_resources.path(common.sfx, "ambience.wav") as p:
            self.ambience = arcade.Sound(p, True)

        self.cursor = Vec2(-100, -100)
        self.start_point = Vec2(-100, -100)
        self.end_point = Vec2(-100, -100)
        self.point_list = []
        self.drawing = False

        self.first_click: float = None
        self.fade_time = 1.0

        self.sounds: dict[str, arcade.Sound] = {s: sound_loader(s) for s in ["blip_a", "blip_c", "blip_e"]}
        self.last_played_sound = 0.0

        self.ambience.play(volume = 0.5, loop = True)

        self.started = True

    def on_show(self):
        self.local_time = 0.0
        self.started = True

    def play_sound(self, s: str):
        self.sounds[s].play()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.started:
            self.cursor = Vec2(x, y)
            if self.drawing:
                old_point_list = self.point_list
                self.end_point = Vec2(x, y)
                self.point_list = dda(self.grid.snap(self.start_point), self.grid.snap(self.end_point))

                if (old_point_list != self.point_list and self.last_played_sound + self.sounds["blip_e"].get_length() / 2 <= self.local_time):
                    self.play_sound("blip_e")
                    self.last_played_sound = self.local_time

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.first_click is None:
                self.first_click = self.local_time
            self.drawing = True
            self.start_point = Vec2(x, y)
            self.play_sound("blip_a")
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.point_list = []
            self.play_sound("blip_c")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.drawing = False
            self.end_point = Vec2(x, y)
            self.point_list = dda(self.grid.snap(self.start_point), self.grid.snap(self.end_point))

    def on_draw(self):
        self.clear()
        self.grid.draw()
        self.grid.draw_point(self.cursor)
        self.grid.draw_point_list(self.point_list)
        self.text.draw()

    def on_update(self, delta_time: float):
        self.local_time += delta_time

        if self.local_time <= self.fade_time:
            alpha = int(ease_linear(0, 255, 0, self.fade_time, self.local_time))
            self.text.color = arcade.color.WHITE.rgb + (alpha,)
        elif self.first_click is not None and self.first_click <= self.local_time <= self.first_click + self.fade_time:
            alpha = int(ease_linear(255, 0, self.first_click, self.first_click + self.fade_time, self.local_time))
            self.text.color = arcade.color.WHITE.rgb + (alpha,)


def main():
    app = Application()
    app.run()
