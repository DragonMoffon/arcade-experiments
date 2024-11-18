# Dos Terminal Ui Elements (I'm OOPing your procedure!)
from arcade.types import Color

from dos.emulator.draw import draw_box, draw_row, colour_box, colour_row, draw_text, Boundary
from dos.emulator.terminal import Terminal
from dos.emulator.sheet import CharSheet

class Element:

    def __init__(self, terminal: Terminal, sheet: CharSheet = None) -> None:
        self.terminal = terminal
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
            terminal: Terminal,
            sheet: CharSheet = None
        ) -> None:
        super().__init__(terminal, sheet)
        self.name = name
        self.start = start
        self.size = size
        self.l, self.b = self.start
        self.w, self.h = self.size
        self.r, self.t = self.l + self.w, self.b + self.h

        self.header = header
        self.body = body
        self.boundary = boundary
        self.boundary_type = boundary_type

    def draw(self):
        self.terminal.draw_box(self.l, self.b, self.w, self.h, self.boundary_type, fore=self.boundary, back=self.body)
        self.terminal.draw_row(self.t-1, self.l, self.r, back=self.header)
        self.terminal.draw_text(self.l + 1, self.t - 1, self.name, self.boundary)