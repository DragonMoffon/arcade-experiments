from typing import Any
from arcade import ArcadeContext, SpriteList, Sprite, Texture, SpriteSolidColor, Camera2D, color as colours
from arcade.types import Color
import arcade.gl as gl

from dos import get_shader_path
from dos.emulator.sheet import CharSheet, MAP

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
        self.default = CharSheet('sheet_ascii_demo', size)

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
                back = SpriteSolidColor(size[0], size[1], x_pos, y_pos, colours.TRANSPARENT_BLACK)
                cc.append(char)
                cb.append(back)
                self.character_list.append(back)
                self.character_list.append(char)

        self.refresh_colour: Color = colours.BLACK

        self.source_texture: gl.Texture2D = ctx.texture(self.size, wrap_x=ctx.CLAMP_TO_EDGE, wrap_y=ctx.CLAMP_TO_EDGE)

        self.source_fbo: gl.Framebuffer = ctx.framebuffer(color_attachments=[self.source_texture])

        self.output_geo = gl.geometry.quad_2d(self.size, pos)

        self.output_program = self.ctx.load_program(
            vertex_shader=get_shader_path('terminal_vs'),
            fragment_shader=get_shader_path('terminal_fs')
        )
        self.output_program["atlas_texture"] = 0
        self.output_program["adjust"] = 0.0
        self.output_program["source_size"] = self.size

        self.source_camera = Camera2D(render_target=self.source_fbo)
        self.output_camera = Camera2D(position=(0.0, 0.0))
        # self.output_program["source"] = 0.0, 0.0, 0.5, 0.5


    def __setitem__(self, loc: tuple[int, int], value: Color | int | tuple[int, Color] | tuple[int, Color, Color]):
        if isinstance(value, int):
            char = self.character_set[value]
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

    def render(self):
        with self.source_camera.activate():
            self.source_fbo.clear(color=self.refresh_colour)
            self.character_list.draw(pixelated=True)

    def draw(self):
        with self.output_camera.activate():
            self.source_texture.use()
            self.output_geo.render(self.output_program)

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