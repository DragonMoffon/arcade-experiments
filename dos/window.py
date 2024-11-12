from math import cos, sin, pi

from arcade import Window, load_texture, Sprite, draw_sprite, Camera2D, Texture, LBWH
from arcade.types import Color
import arcade.gl as gl
import arcade

from dos.emulator import CHAR_COUNT, CHAR_SIZE
from dos.emulator.screen import Screen
from dos.emulator.element import ElementBoundary, Window as WindowElement
from dos.emulator.draw import colour_box, colour_row, draw_text



class DOSWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "DOS")
        self.t_screen = Screen(CHAR_COUNT, CHAR_SIZE, self.center, self.ctx)

        # background
        colour_box(Color(0, 0, 168), 0, 80, 0, 30, self.t_screen)
        colour_row(Color(0, 168, 168), 0, 0, 80, self.t_screen) # bottom row
        colour_row(Color(0, 168, 168), -1, 0, 80, self.t_screen) # top row

        # windows
        self.output = WindowElement('Output', (2, 2), (74, 5), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), ElementBoundary.DOUBLE, self.t_screen)
        self.channel = WindowElement('Channel', (2, 8), (52, 20), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), ElementBoundary.DOUBLE, self.t_screen)
        self.signal = WindowElement('Signal', (55, 8), (21, 20), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), ElementBoundary.DOUBLE, self.t_screen)

        self.output.draw()
        self.channel.draw()
        self.signal.draw()

        # text
        draw_text('StarCom v1.4.00', arcade.color.BLACK, 0, -1, self.t_screen)
        draw_text('ID:T44  KEY:XXXXXX', arcade.color.BLACK, 0, 0, self.t_screen)

        self.h = 0
        self.v = 0

    def on_draw(self):
        self.clear()
        self.t_screen.render()
        self.t_screen.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.D:
                self.h += 1
            case arcade.key.A:
                self.h -= 1
            case arcade.key.W:
                self.v += 1
            case arcade.key.S:
                self.v -= 1

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.D:
                self.h -= 1
            case arcade.key.A:
                self.h += 1
            case arcade.key.W:
                self.v -= 1
            case arcade.key.S:
                self.v += 1

    def on_update(self, delta_time: float) -> bool | None:
        pos = self.t_screen.output_camera.position
        self.t_screen.output_camera.position = pos[0] + delta_time * self.h * 100.0, pos[1] + delta_time * self.v * 100.0

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool | None:
        self.t_screen.output_camera.zoom = max(0.1, min(10.0,self.t_screen.output_camera.zoom + scroll_y /10.0))

def main():
    win = DOSWindow()
    win.run()
