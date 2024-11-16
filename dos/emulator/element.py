# Dos Terminal Ui Elements (I'm OOPing your procedure!)
from enum import Enum

from arcade.types import Color

from dos.emulator.draw import draw_box, draw_row, colour_box, colour_row, draw_text, Boundary
from dos.emulator.screen import Screen
from dos.emulator.sheet import CharSheet

class Element:

    def __init__(self, screen: Screen, sheet: CharSheet = None) -> None:
        self.screen = screen
        self.sheet = sheet

    def draw(self):
        pass

class Window(Element):
    """

    >>> Coloured and Named Top Bar
    >>> Box area
    >>> possible boundary

    """
    def __init__(
            self,
            name: str,
            start: tuple[int, int],
            size: tuple[int, int],
            header: Color,
            body: Color,
            boundary: Color,
            boundary_type: Boundary,
            screen: Screen,
            sheet: CharSheet = None
        ) -> None:
        super().__init__(screen, sheet)
        self.name = name
        self.start = start
        self.size = size
        self.l, self.b = self.start
        self.w, self.h = self.size
        self.r, self.t = self.l + self.w, self.b + self.h

        self.header = header
        self.body = body
        self.boundary = boundary

        self.boundary_type = boundary

    def draw(self):
        colour_box(self.body, self.l, self.r, self.b, self.t, self.screen)
        colour_row(self.header, self.t-1, self.l, self.r, self.screen)
        draw_box(self.boundary, self.l, self.r, self.b, self.t, self.screen)
        draw_text(self.name, self.boundary, self.l + 1, self.t - 1, self.screen)