from array import array
from PIL import Image
from math import radians

from arcade import gl
from arcade import get_window

from common.data_loading import make_package_string_loader, make_package_path_finder
import sphere.data as data

get_shader_string = make_package_string_loader(data, 'glsl')
get_img_path = make_package_path_finder(data, "png")


class Renderer:

    def __init__(self):
        self._ctx = ctx = get_window().ctx

        self._sphere = gl.geometry.sphere(1.0, 1440, 720)
        self._texture_program = ctx.program(
            vertex_shader=get_shader_string("sphere_texture_vs"),
            fragment_shader=get_shader_string("sphere_texture_fs")
        )
        self._texture_program["radius"] = 6371
        self._texture_program["wrldText"] = 0
        self._texture_program["elevText"] = 1
        img = Image.open(get_img_path("world_blend_oct"))
        self._world_texture = ctx.texture(img.size, components=4, data=img.tobytes(), wrap_x=ctx.CLAMP_TO_EDGE, wrap_y=ctx.CLAMP_TO_EDGE)
        img = Image.open(get_img_path("world_bump"))
        self._elev_texture = ctx.texture(img.size, components=4, data=img.tobytes(), wrap_x=ctx.CLAMP_TO_EDGE, wrap_y=ctx.CLAMP_TO_EDGE)

        self._ring_program = ctx.program(
            vertex_shader=get_shader_string("blank_sphere_texture_vs"),
            fragment_shader=get_shader_string("sphere_circle_fs")
        )
        self._ring_program['line_width'] = radians(0.2)
        # self._ring_program['error_transparency'] = 0.2
        self._ring_program['radius'] = 6500
        self._rings = ctx.buffer(
            data=array('f', (
                radians(174.704), radians(-41.309), radians(31.39), 0.05,  # First Ring (SNZO)
                radians(119.7531), radians(-21.159), radians(41.02), 0.05,  # Second Ring (MBWA)
                radians(110.5354), radians(-66.2792), radians(65.9), 0.05  # Third Ring (CASY)
            ))
        )

    def draw(self):
        self._ctx.disable(self._ctx.CULL_FACE)
        self._ctx.enable(self._ctx.DEPTH_TEST)

        self._world_texture.use(0)
        self._elev_texture.use(1)
        self._sphere.render(self._texture_program)

        self._rings.bind_to_storage_buffer()
        self._sphere.render(self._ring_program)
