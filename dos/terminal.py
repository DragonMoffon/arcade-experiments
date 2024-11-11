import arcade
import arcade.gl as gl

from common.data_loading import make_package_path_finder
import dos.data as data

CHAR_COUNT = 80, 30
CHAR_SIZE = 9, 16

get_image_path = make_package_path_finder(data, 'png')
get_shader_path = make_package_path_finder(data, 'glsl')

# RANDOM
from random import randint


class Terminal:
    pass


class CharSheet:

    def __init__(self, name: str, size: tuple[int, int]) -> None:
        self.name = name
        self.char_size = size
        self.sheet = arcade.load_spritesheet(get_image_path(name))
        self.chars = self.sheet.get_texture_grid(size, 16, 256)
        self.codes = {t: idx for idx, t in enumerate(self.chars)}

    def __getitem__(self, key: int) -> arcade.Texture:
        return self.chars[key]
    
    def code(self, t: arcade.Texture) -> int:
        return self.codes[t]

class Screen:
    
    def __init__(self, count: tuple[int, int], size: tuple[int, int]) -> None:
        self.ctx = ctx = arcade.get_window().ctx
        self.char_count = count
        self.char_size = size
        self.size = (size[0] * count[0]), (size[1] * count[1]) # Pixel size of screen
        self.character_set = CharSheet('sheet_ascii_demo', size)

        # for x, y 
        self.character_list = arcade.SpriteList(capacity=2 * count[0] * count[1])
        self._character_grid: list[list[arcade.Sprite]] = []
        self._backing_grid: list[list[arcade.Sprite]] = []
        self._char_blank = arcade.Texture.create_empty('char_blank', size)
        hw, hh = size[0] / 2.0, size[1] / 2.0
        for x in range(self.char_count[0]):
            cc = []
            cb = []
            self._character_grid.append(cc)
            self._backing_grid.append(cb)
            x_pos = hw + x * size[0]
            for y in range(self.char_count[1]):
                y_pos = hh + y * size[1]
                char = arcade.Sprite(self._char_blank, center_x=x_pos, center_y=y_pos)
                back = arcade.SpriteSolidColor(size[0], size[1], x_pos, y_pos, arcade.color.TRANSPARENT_BLACK)
                cc.append(char)
                cb.append(back)
                self.character_list.append(back)
                self.character_list.append(char)

        self.refresh_colour: arcade.types.Color = arcade.color.BLACK

        self.source_texture: gl.Texture2D = ctx.texture(self.size, wrap_x=ctx.CLAMP_TO_EDGE, wrap_y=ctx.CLAMP_TO_EDGE)

        self.source_fbo: gl.Framebuffer = ctx.framebuffer(color_attachments=[self.source_texture])

        self.output_geo = gl.geometry.quad_2d(self.size, arcade.get_window().center)

        self.output_program = self.ctx.load_program(
            vertex_shader=get_shader_path('terminal_vs'),
            fragment_shader=get_shader_path('terminal_fs')
        )
        self.output_program["atlas_texture"] = 0
        self.output_program["adjust"] = 0.05
        self.output_program["source_size"] = self.size

        self.source_camera = arcade.Camera2D(render_target=self.source_fbo)
        # self.output_program["source"] = 0.0, 0.0, 0.5, 0.5


    def __setitem__(self, key: tuple[int, int], value: arcade.types.Color | int):
        if isinstance(value, int):
            self._character_grid[key[0]][key[1]].texture = self.character_set[value]
        else:
            self._backing_grid[key[0]][key[1]].color = value

    def __getitem__(self, key: tuple[int, int]) -> tuple[int, arcade.types.Color]:
        char = self.character_set.code(self._character_grid[key[0]][key[1]].texture)
        back = self._backing_grid[key[0]][key[1]].color
        return char, back

    def render(self):
        with self.source_camera.activate():
            self.source_fbo.clear(color=self.refresh_colour)
            self.character_list.draw(pixelated=True)

    def draw(self):
        self.source_texture.use()
        self.output_geo.render(self.output_program)


def draw_text(text: str, start_x: int, start_y: int, screen: Screen):
    for idx, char in enumerate(text):
        screen[start_x + idx, start_y] = ord(char)

def colour_box(colour: arcade.types.Color, left: int, right: int, bottom: int, top: int, screen: Screen):
    for x in range(left, right):
        for y in range(bottom, top):
            screen[x, y] = colour

def colour_row(colour: arcade.types.Color, row: int, column_start: int, column_end: int, screen: Screen):
    for idx in range(column_start, column_end):
        screen[idx, row] = colour

def colour_column(colour: arcade.types.Color, column: int, row_start: int, row_end: int, screen: Screen):
    for idx in range(row_start, row_end):
        screen[column, idx] = colour