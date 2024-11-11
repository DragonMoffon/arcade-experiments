from math import cos, sin, pi

from arcade import Window, load_texture, Sprite, draw_sprite, Camera2D, Texture, LBWH
import arcade.gl as gl
import arcade

from dos.terminal import Screen, CHAR_COUNT, CHAR_SIZE

import dos.data as data
from common.data_loading import make_package_path_finder


get_image_path = make_package_path_finder(data, 'png')
get_shader_path = make_package_path_finder(data, 'glsl')

class DOSWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "DOS")
        self.t_screen = Screen(CHAR_COUNT, CHAR_SIZE)
        #self.terminal_texture = load_texture(get_image_path('starcom'), hash='terminal_input')
        #self.terminal_output = Texture.create_empty('terminal_output', (self.terminal_texture.width, self.terminal_texture.height))
        #self.terminal_camera = Camera2D(position=(0.0, 0.0))

        #self.ctx.default_atlas.add(self.terminal_texture)
        #self.ctx.default_atlas.add(self.terminal_output)

        #self.terminal_sprite = Sprite(self.terminal_output, scale=1.0)
        #
        #atlas_region = self.ctx.default_atlas.get_texture_region_info(self.terminal_texture.atlas_name)

        #self.terminal_program = self.ctx.load_program(
        #    vertex_shader=get_shader_path('terminal_vs'),
        #    fragment_shader=get_shader_path('terminal_fs')
        #)
        #self.terminal_program["atlas_texture"] = 0
        #self.terminal_program["source_size"] = self.terminal_texture.width * 1.0, self.terminal_texture.height * 1.0
        #coords = atlas_region.texture_coordinates
        #self.terminal_program["source"] = coords[0], coords[1], (coords[-2] - coords[0]), (coords[-1] - coords[1])

        #self.terminal_geo = gl.geometry.quad_2d_fs()

    def on_draw(self):
        self.t_screen.render()
        self.t_screen.draw()
        #self.clear()
        #with self.ctx.default_atlas.render_into(self.terminal_output) as fbo:
        #    fbo.clear()
        #    self.ctx.default_atlas.texture.filter = self.ctx.LINEAR, self.ctx.LINEAR
        #    self.ctx.default_atlas.texture.use(0)
        #    self.ctx.default_atlas.use_uv_texture(1)
        #    self.terminal_geo.render(self.terminal_program)
    
        #with self.terminal_camera.activate():
        #    self.ctx.default_atlas.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST
        #    draw_sprite(self.terminal_sprite)
        #    arcade.draw_text(f'adjustment: -{self.terminal_program['adjust']:.2f}', self.terminal_sprite.center_x, self.terminal_sprite.bottom, anchor_x='center', anchor_y='top')

    def on_update(self, delta_time: float):
        pass
        #self.terminal_program['adjust'] = 0.05 + 0.05 * cos(0.25 * pi * self.time)


def main():
    win = DOSWindow()
    win.run()
