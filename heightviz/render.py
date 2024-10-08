from PIL import Image

from arcade import gl
from arcade import get_window

from common.data_loading import make_package_string_loader, make_package_path_finder
import sphere.data as data

get_shader_string = make_package_string_loader(data, 'glsl')
get_img_path = make_package_path_finder(data, "png")


class Renderer:

    def __init__(self):
        self._ctx = ctx = get_window().ctx

        self._sphere = gl.geometry.sphere(1.0, 1024, 1024)
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

    def draw(self):
        self._ctx.enable(self._ctx.DEPTH_TEST)

        self._world_texture.use(0)
        self._elev_texture.use(1)
        self._sphere.render(self._texture_program)
