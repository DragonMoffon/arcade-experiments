from math import cos, sin, pi

from arcade import Window, load_texture, Sprite, draw_sprite, Camera2D, Texture, LBWH
import arcade.gl as gl
import arcade

from dos.terminal import Screen, CHAR_COUNT, CHAR_SIZE, draw_text, colour_column, colour_row, colour_box

import dos.data as data
from common.data_loading import make_package_path_finder


get_image_path = make_package_path_finder(data, 'png')
get_shader_path = make_package_path_finder(data, 'glsl')

class DOSWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "DOS")
        self.t_screen = Screen(CHAR_COUNT, CHAR_SIZE)

        # background
        colour_box(arcade.types.Color(0, 0, 168), 0, 80, 0, 30, self.t_screen)
        colour_row(arcade.types.Color(0, 168, 168), 0, 0, 80, self.t_screen) # bottom row
        colour_row(arcade.types.Color(0, 168, 168), -1, 0, 80, self.t_screen) # top row

        # windows
        colour_box(arcade.types.Color(84, 84, 252), 2, 76, 2, 7, self.t_screen)
        colour_row(arcade.types.Color(168, 168, 168), 6, 2, 76, self.t_screen)

        colour_box(arcade.types.Color(84, 84, 252), 2, 54, 8, 28, self.t_screen)
        colour_row(arcade.types.Color(168, 168, 168), 27, 2, 54, self.t_screen)

        colour_box(arcade.types.Color(84, 84, 252), 55, 76, 8, 28, self.t_screen)
        colour_row(arcade.types.Color(168, 168, 168), 27, 55, 76, self.t_screen)

        # text
        draw_text('StarCom v1.4.00', 0, -1, self.t_screen)
        draw_text('ID:T44  KEY:XXXXXX', 0, 0, self.t_screen)

    def on_draw(self):
        self.t_screen.render()
        self.t_screen.draw()

    def on_update(self, delta_time: float):
        pass


def main():
    win = DOSWindow()
    win.run()
