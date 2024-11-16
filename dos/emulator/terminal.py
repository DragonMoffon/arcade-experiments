import arcade
from arcade.types import Color

from dos.emulator import CHAR_COUNT, CHAR_SIZE
from dos.emulator.screen import Screen
from dos.emulator.sheet import CharSheet, MAP, IMAP
from dos.processing.frame import Frame, FrameConfig, TextureConfig
from dos.emulator.draw import Boundary


class Terminal:
    
    def __init__(self, position: tuple[int, int] = None, window: arcade.Window = None) -> None:
        self.window = window or arcade.get_window

        self.screen = Screen(CHAR_COUNT, CHAR_SIZE, (CHAR_COUNT[0]*CHAR_SIZE[0]//2, CHAR_COUNT[1]*CHAR_SIZE[1]//2), window.ctx)
        self.frame = Frame(
            FrameConfig(
                self.screen.size, self.screen.size, position, (TextureConfig(),)
            )
        )

        self.char_sheet: CharSheet = None

    # TERMINAL COMMANDS -----------------------
    def draw(self):
        with self.frame:
            self.screen.render()
            self.screen.draw()

    # DRAW COMMANDS ----------------------------

    def draw_char(self, x, y, char: str = None, fore: Color = None, back: Color = None):
        self.screen.set_char((x, y), char, fore, back, self.char_sheet)

    def draw_text(self, start_x: int, start_y: int, text: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        for idx, char in enumerate(text):
            if char == '\b':continue
            s.set_char((start_x + idx, start_y), MAP[char], fore, back, c)

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
                    bounds = (None, None, None, None, None) # bl, br, tl, tr, v, h

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
            for x in range(l+2, r-1):
                for y in range(b+2, t-1):
                    s.set_char((x, y), None, None, back)

    def draw_row(self, row: int, start: int = 0, stop: int = None, step: int = 1, char: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        stop = stop if stop is not None else s.char_count[0]
        for idx in range(start, stop, step):
            s.set_char((idx, row), char, fore, back, c)

    def draw_column(self, column: int, start: int = 0, stop: int = None, step: int= 1, char: str = None, fore: Color = None, back: Color = None):
        s = self.screen
        c = self.char_sheet
        stop = stop if stop is not None else s.char_count[1]
        for idx in range(start, stop, step):
            s.set_char((column, idx), char, fore, back, c)


    # COLOUR COMMANDS --------------------------