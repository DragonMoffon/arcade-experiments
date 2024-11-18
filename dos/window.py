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

        self.scene_camera = arcade.Camera2D()

        ## background
        #colour_box(Color(0, 0, 168), 0, 80, 0, 30, self.terminal.screen)
        #colour_row(Color(0, 168, 168), 0, 0, 80, self.terminal.screen) # bottom row
        #colour_row(Color(0, 168, 168), -1, 0, 80, self.terminal.screen) # top row

        ## windows
        #self.output = WindowElement('Output', (2, 2), (74, 5), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), Boundary.DOUBLE, self.terminal.screen)
        #self.channel = WindowElement('Channel', (2, 8), (52, 20), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), Boundary.DOUBLE, self.terminal.screen)
        #self.signal = WindowElement('Signal', (55, 8), (21, 20), Color(168, 168, 168), Color(84, 84, 252), Color(255, 255, 255), Boundary.DOUBLE, self.terminal.screen)

        #self.output.draw()
        #self.channel.draw()
        #self.signal.draw()


        # text
        # draw_text('StarCom v1.4.00', arcade.color.BLACK, 0, -1, self.terminal.screen)
        # draw_text('ID:T44  KEY:XXXXXX', arcade.color.BLACK, 0, 0, self.terminal.screen)

        self.h = 0
        self.v = 0

    def on_draw(self):
        self.clear()

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
