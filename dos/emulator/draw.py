from enum import IntEnum

from arcade.types import Color
from dos.emulator.sheet import CharSheet, MAP
from dos.emulator.screen import Screen


class Boundary(IntEnum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2


def draw_text(text: str, colour: Color, start_x: int, start_y: int, screen: Screen, sheet: CharSheet = None):
    for idx, char in enumerate(text):
        if char == '\b':
            continue
        screen.set_char((start_x + idx, start_y), MAP[char], colour, sheet=sheet)

# TODO: Add boundary options
def draw_box(colour: Color, left: int, right: int, bottom: int, top: int, screen: Screen):
    screen[left, bottom] = 0xC8, colour
    screen[right-1, top-1] = 0xBB, colour
    screen[left, top-1] = 0xC9, colour
    screen[right-1, bottom] = 0xBC, colour
    for col in range(left+1, right-1):
        screen[col, top-1] = 0xCD, colour
        screen[col, bottom] = 0xCD, colour
    for row in range(bottom+1, top-1):
        screen[left, row] = 0xBA, colour
        screen[right-1, row] = 0xBA, colour

def colour_box(colour: Color, left: int, right: int, bottom: int, top: int, screen: Screen):
    for x in range(left, right):
        for y in range(bottom, top):
            screen[x, y] = colour

def colour_row(colour: Color, row: int, column_start: int, column_end: int, screen: Screen):
    for idx in range(column_start, column_end):
        screen[idx, row] = colour

def draw_row(char: int, colour: Color, row: int, column_start: int, column_end: int, screen: Screen):
        for idx in range(column_start, column_end):
            screen[idx, row] = char, colour

def colour_column(colour: Color, column: int, row_start: int, row_end: int, screen: Screen):
    for idx in range(row_start, row_end):
        screen[column, idx] = colour

def draw_column(char: int, colour: Color, column: int, row_start: int, row_end: int, screen: Screen):
    for idx in range(row_start, row_end):
        screen[column, idx] = char, colour