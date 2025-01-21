from math import cos, sin, pi

from arcade import Window
from arcade.types import Color
import arcade

from dos.emulator import CHAR_COUNT, CHAR_SIZE
from dos.emulator.screen import Screen
from dos.emulator.element import  Window as WindowElement
from dos.emulator.draw import colour_box, colour_row, draw_text, Boundary
from dos.emulator.terminal import Terminal
from dos.processing.frame import Frame, FrameConfig, TextureConfig, Bloom, TonemapAGX

from dos.game.snake import SnakeApp
from dos.game.starcomm import StarCommApp
from dos.game.tictactoe import SuperTicTacToeApp

from random import choice, randint
c = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')


class DOSWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "DOS")
        self.terminal = Terminal(self.center, self)
        self.frame = Frame(FrameConfig(self.size, self.size, self.center, TextureConfig()), self.ctx)
        # self.frame.add_process(Bloom(self.size, 5, self.ctx))
        # self.frame.add_process(TonemapAGX(self.ctx))

        self.snake = SnakeApp(self.terminal)
        self.terminal.launch(self.snake)
        self.starcomm = StarCommApp(self.terminal)
        # self.terminal.launch(self.starcomm)
        self.tictactoe = SuperTicTacToeApp(self.terminal)
        # self.terminal.launch(self.tictactoe)
        self.scene_camera = arcade.Camera2D()

        # text

        self.h = 0
        self.v = 0

    def on_draw(self):
        self.clear((15, 15, 15))

        with self.frame as fbo:
            fbo.clear()
            with self.scene_camera.activate():
                self.terminal.draw()
        
    def on_update(self, delta_time: float) -> bool | None:
        pos = self.scene_camera.position
        self.scene_camera.position = pos[0] + delta_time * self.h * 100.0, pos[1] + delta_time * self.v * 100.0

        self.terminal.update(delta_time)

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
        self.terminal.input(symbol, modifiers, True)

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
        self.terminal.input(symbol, modifiers, False)


    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool | None:
        self.scene_camera.zoom = max(0.1, min(10.0,self.scene_camera.zoom + scroll_y /10.0))

def main():
    win = DOSWindow()
    win.run()
