from random import randint, randrange

from enum import Enum
from arcade import key

from dos.emulator.terminal import Terminal
from dos.emulator.app import App
from dos.emulator.sheet import MAP
from dos.emulator.element import Window, Boundary

logo_str = (
'███ █ █ ███ ███ ███\n'
'█ █ █ █ █ █ █ █ █ █\n'
'█   █ █ ███ █   █ █\n'
'███ █ █ █   ███ ███\n'
'  █ █ █ █   █   ██ \n'
'█ █ █ █ █   █ █ █ █\n'
'███ ███ █   ███ █ █\n'
'\n'
'█████████ █████████\n'
'█████████ █████████\n'
'█████████ █████████\n'
'   ███          ███\n'
'   ███          ███\n'
'   ███          ███\n'
'   ███    █████████\n'
'   ███    █████████\n'
'   ███    █████████\n'
'   ███          ███\n'
'   ███          ███\n'
'   ███          ███\n'
'   ███    █████████\n'
'   ███    █████████\n'
'   ███    █████████\n'
)


tic_locs = (
    (34, 18), (40, 18), (46, 18),
    (34, 14), (40, 14), (46, 14),
    (34, 10), (40, 10), (46, 10),
)

class State(Enum):
    EMPTY = 0
    NAUGHT = 1
    CROSS = 2

class SuperTicTacToeApp(App):

    def __init__(self, terminal) -> None:
        self.terminal: Terminal = terminal
        
        self.super_board = [State.EMPTY]*9
        self.board = [State.EMPTY]*9

        self.super_window = Window('Super', (1, 17), (23, 12), None, None, (255, 255, 255), Boundary.DOUBLE, terminal)
        self.board_window = Window('Info', (1, 1), (23, 15), None, None, (255, 255, 255), Boundary.DOUBLE, terminal)

        self.current = State.NAUGHT
        self.selected = 4


    def on_run(self, tick):
        self.draw()
        with self.terminal.record_clear():
            # Draw Logo
            self.terminal.draw_text(57, 26, logo_str, (255, 255, 255), (0, 0, 0))
            # Draw Tic Tac Toe Grid
            self.terminal.draw_row(12, 32, 49, 1, '─', (255, 255, 255))
            self.terminal.draw_row(16, 32, 49, 1, '─', (255, 255, 255))
            self.terminal.draw_column(37, 9, 20, 1, '│', (255, 255, 255))
            self.terminal.draw_column(43, 9, 20, 1, '│', (255, 255, 255))
            self.terminal.draw_char(37, 12, '┼', (255, 255, 255))
            self.terminal.draw_char(43, 12, '┼', (255, 255, 255))
            self.terminal.draw_char(37, 16, '┼', (255, 255, 255))
            self.terminal.draw_char(43, 16, '┼', (255, 255, 255))


    def draw(self):
        self.terminal.clear()
        self.super_window.draw()
        self.board_window.draw()
        for box in range(9):
            s = self.board[box]
            x, y = tic_locs[box]
            if s == State.NAUGHT:
                self.draw_naught(x, y)
            elif s == State.CROSS:
                self.draw_cross(x, y)

    def draw_naught(self, x, y):
        #  000
        # 00 00
        #  000
        self.terminal.draw_text(x-2, y-1, " OOO ", (255, 255, 255))
        self.terminal.draw_text(x-2,   y, "OO OO", (255, 255, 255))
        self.terminal.draw_text(x-2, y+1, " OOO ", (255, 255, 255))

    def draw_cross(self, x, y):
        # xx xx
        #   x
        # xx xx
        self.terminal.draw_text(x-2, y-1, "XX XX", (255, 255, 255))
        self.terminal.draw_text(x-2,   y, "  X  ", (255, 255, 255))
        self.terminal.draw_text(x-2, y+1, "XX XX", (255, 255, 255))
    
