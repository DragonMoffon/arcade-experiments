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

        self._sphere = gl.geometry.sphere(200.0)
        self._texture_program = ctx.program(
            vertex_shader=get_shader_string("sphere_texture_vs"),
            fragment_shader=get_shader_string("sphere_texture_fs")
        )
        img = Image.open(get_img_path("world_oct"))
        self._world_texture = ctx.texture((5400, 2700), components=3, data=img.tobytes())

    def draw(self):
        self._ctx.disable(self._ctx.CULL_FACE)
        self._ctx.enable(self._ctx.DEPTH_TEST)
        self._world_texture.use(0)
        self._sphere.render(self._texture_program)
