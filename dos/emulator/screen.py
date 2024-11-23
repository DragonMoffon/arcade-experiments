from typing import Any
from arcade import ArcadeContext, SpriteList, Sprite, Texture, SpriteSolidColor, Camera2D, XYWH, LBWH, color as colours
from arcade.types import Color
import arcade.gl as gl

from dos import get_shader_path
from dos.emulator.sheet import CharSheet, MAP
from dos.processing.frame import Frame, FrameConfig, TextureConfig, CRT


class CharSprite(Sprite):

    def __init__(self, char: int, sheet: CharSheet, center_x, center_y, color: Color = Color(255, 255, 255)) -> None:
        super().__init__(sheet[char], 1.0, center_x, center_y)
        self.char = char
        self.color = color


class Screen:
    
    def __init__(self, count: tuple[int, int], size: tuple[int, int], pos: tuple[int, int], ctx: ArcadeContext) -> None:
        self.ctx = ctx
        self.char_count = count
        self.char_size = size
        self.size = (size[0] * count[0]), (size[1] * count[1]) # Pixel size of screen
        self.default = CharSheet('MxPlus_IBM_CGA-2y', size)

        # for x, y 
        self.character_list = SpriteList(capacity=2 * count[0] * count[1])
        self._character_grid: list[list[CharSprite]] = []
        self._backing_grid: list[list[CharSprite]] = []

        start_char = MAP[' ']
        hw, hh = size[0] / 2.0, size[1] / 2.0
        for x in range(self.char_count[0]):
            cc = []
            cb = []
            self._character_grid.append(cc)
            self._backing_grid.append(cb)
            x_pos = hw + x * size[0]
            for y in range(self.char_count[1]):
                y_pos = hh + y * size[1]
                char = CharSprite(start_char, self.default, center_x=x_pos, center_y=y_pos)
                back = SpriteSolidColor(size[0], size[1], x_pos, y_pos, colours.BLACK)
                cc.append(char)
                cb.append(back)
                self.character_list.append(back)
                self.character_list.append(char)

        self.refresh_colour: Color = colours.BLACK

        self.frame_camera = Camera2D(viewport=LBWH(0, 0, self.size[0],self.size[1]), position=(0, 0), projection=LBWH(0.0, 0.0, self.size[0], self.size[1]))
        self.frame = Frame(
            FrameConfig((self.size[0],self.size[1]), self.size, pos, TextureConfig()),
            ctx,
            ctx.load_program(
                vertex_shader=get_shader_path('frame_render_vs'),
                fragment_shader=get_shader_path('CRT_r_fs')
            )
        )
        self.frame.add_process(CRT(self.size, self.ctx))

    def __setitem__(self, loc: tuple[int, int], value: Color | int | tuple[int, Color] | tuple[int, Color, Color]):
        if isinstance(value, int):
            char = value
            fore = None
            back = None
        elif isinstance(value, Color):
            char = None
            fore = None
            back = value
        else:
            char, fore, *back = value
            back = None if not back else back[0]
        self.set_char(loc, char, fore, back)

    def __getitem__(self, loc: tuple[int, int]) -> tuple[int, Color]:
        return self.get_char(loc)

    def draw(self):
        with self.frame as fbo:
            fbo.clear(colour=self.refresh_colour)
            with self.frame_camera.activate():
                self.character_list.draw(pixelated=True)

    def set_char(self, loc: tuple[int, int], char: int = None, fore: Color = None, back: Color = None, sheet: CharSheet = None):
        sheet = sheet or self.default
        character = self._character_grid[loc[0]][loc[1]]
        background = self._backing_grid[loc[0]][loc[1]]
        if char is not None:
            character.char = char
            character.texture = sheet[char]
        if fore is not None:
            character.color = fore
        if back is not None:
            background.color = back

    def get_char(self, loc: tuple[int, int]) -> tuple[int, Color, Color]:
        character = self._character_grid[loc[0]][loc[1]]
        background = self._backing_grid[loc[0]][loc[1]]
        return character.char, character.color, background.color
    
    def clear(self, l: int = 0, b: int = 0, w: int = 0, h: int = 0):
        w = w or self.char_count[0]
        h = h or self.char_count[1]
        start_char = MAP[' ']
        for x in range(l, l+w):
            for y in range(b, b+h):
                char = self._character_grid[x][y]
                back = self._backing_grid[x][y]

                char.color = colours.WHITE
                char.char = start_char
                char.texture = self.default[start_char]
                
                back.color = colours.BLACK
