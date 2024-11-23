from functools import partial
from typing import Callable

import arcade
from arcade.types import Color

from dos.emulator import CHAR_COUNT, CHAR_SIZE
from dos.emulator.screen import Screen
from dos.emulator.sheet import CharSheet, MAP, IMAP
from dos.processing.frame import Frame, FrameConfig, TextureConfig, CRT, Bloom
from dos.emulator.draw import Boundary
from dos.emulator.app import App


TPS = 20 # Ticks per second
TR = 1.0 / TPS # Tick Rate

class Terminal:
    
    def __init__(self, position: tuple[int, int] = None, window: arcade.Window = None) -> None:
        self.window = window or arcade.get_window

        self.screen = Screen(CHAR_COUNT, CHAR_SIZE, position, window.ctx)
        self.saved_clear_grid = [[]] # TODO

        self.char_sheet: CharSheet = None

        self.clear_commands: list[Callable] = []

        self.awake_app: App = None
        self.asleep_apps: list[App] = []

        self.terminal_time = 0.0
        self.tick_time = 0.0
        self.current_tick: int = 0

    # TERMINAL COMMANDS -----------------------
    def draw(self):
        self.screen.draw()

    def update(self, dt: float):
        self.tick_time += dt
        while self.tick_time > TR:
            self.tick_time -= TR
            self.terminal_time += TR
            self.current_tick += 1
            self.tick(self.current_tick)

    def tick(self, t: int):
        if self.awake_app:
            self.awake_app.run(t)
        for app in self.asleep_apps:
            app.sleep(t)

    def input(self, input: int, modifiers: int, pressed: bool):
        if self.awake_app:
            self.awake_app.input(input, modifiers, pressed)

    # OS COMMANDS -----------------------------
    def launch(self, app: App, **options):
        if app.terminal != self:
            raise ValueError('App is not synced to this terminal')
        if self.awake_app:
            self.asleep_apps.append(self.awake_app)
            self.awake_app.close(self.current_tick)
        app.launch(self.current_tick, **options)
        self.awake_app = app
            
            
    # DRAW COMMANDS ----------------------------
    def clear(self):
        self.screen.clear()
        for command in self.clear_commands:
            command()

    def add_clear_command(self, cmd: Callable, *args, **kwds):
        self.clear_commands.append(partial(cmd, *args, **kwds))

    def reset_clear_commands(self):
        self.clear_commands = []

    def draw_char(self, x, y, char: str = None, fore: Color = None, back: Color = None):
        if char is not None:
            char = MAP[char]
        self.screen.set_char((x, y), char, fore, back, self.char_sheet)

    def draw_text(self, start_x: int, start_y: int, text: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        line_shift = 0
        idx_shift = 0
        for idx, char in enumerate(text):
            if char == '\f' or char == '\t':continue
            if char == '\n': 
                idx_shift = idx + 1
                line_shift += 1
                continue
            if char == '\r':
                idx_shift = idx + 1
                continue
            s.set_char((start_x + idx - idx_shift, start_y - line_shift), MAP[char], fore, back, c)

    def draw_box(self, left: int, bottom: int, width: int, height: int, bound: Boundary | int = Boundary.NONE, fore: Color = None, back: Color = None, is_filled: bool = True, is_edged: bool = True):
        l, b = left, bottom
        r, t = l + width, b + height

        if is_edged:
            match bound:
                case Boundary.SINGLE:
                    bounds = (0xC0, 0xD9, 0xDA, 0xBF, 0xB3, 0xC4) # bl, br, tl, tr, v, h
                case Boundary.DOUBLE:
                    bounds = (0xC8, 0xBC, 0xC9, 0xBB, 0xBA, 0xCD) # bl, br, tl, tr, v, h
                case _:
                    bounds = (None, None, None, None, None, None) # bl, br, tl, tr, v, h

            s = self.screen
            c = self.char_sheet

            s.set_char((l, b), bounds[0], fore, back, c)
            s.set_char((r-1, b), bounds[1], fore, back, c)
            s.set_char((l, t-1), bounds[2], fore, back, c)
            s.set_char((r-1, t-1), bounds[3], fore, back, c)

            for y in range(b+1, t-1):
                s.set_char((l, y), bounds[4], fore, back, c)
                s.set_char((r-1, y), bounds[4], fore, back, c)

            for x in range(l + 1, r - 1):
                s.set_char((x, b), bounds[5], fore, back, c)
                s.set_char((x, t-1), bounds[5], fore, back, c)

        if is_filled:
            for x in range(l+1, r-1):
                for y in range(b+1, t-1):
                    s.set_char((x, y), None, None, back)

    def draw_row(self, row: int, start: int = 0, stop: int = None, step: int = 1, char: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        if char is not None:
            char = MAP[char]
        stop = stop if stop is not None else s.char_count[0]
        for idx in range(start, stop, step):
            s.set_char((idx, row), char, fore, back, c)

    def draw_column(self, column: int, start: int = 0, stop: int = None, step: int= 1, char: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        if char is not None:
            char = MAP[char]
        stop = stop if stop is not None else s.char_count[1]
        for idx in range(start, stop, step):
            s.set_char((column, idx), char, fore, back, c)


    # COLOUR COMMANDS --------------------------