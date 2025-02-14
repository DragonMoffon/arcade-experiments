from math import cos, sin, pi, tau
from array import array
from arcade import Window, draw_triangle_filled, draw_triangle_outline, draw_line, Text, Camera2D, XYWH, Vec2, draw_points
from arcade.types import RGBOrA255
import arcade.gl as gl
import pyglet.gl as pygl

from common.data_loading import make_package_string_loader
import instanced.data as data

from random import random

get_prog_string = make_package_string_loader(data, "glsl")


from instanced.style_box import gen_stylebox

def gen_star(point: int):

    fraction = pi / point
    dp = point * 2
    points = [0.0, 0.0]
    colors = [1.0, 1.0, 1.0]

    for idx in range(dp):
        theta = idx * fraction
        scale = 0.5 + 0.5 * (idx % 2)
        points.extend((scale * cos(theta - fraction / 2), scale * sin(theta - fraction / 2)))
        colors.extend((
            sin(theta / 3 - 0.3) * 0.5 + 0.5,
            sin(theta / 2 + 0.8) * 0.5 + 0.5,
            sin(theta + 1.6) * 0.5 + 0.5
        ))
    
    indices = []
    for a, b in zip(range(0, dp), range(1, dp + 1)):
        indices.extend((0, a + 1, b % dp + 1))
    
    return points, colors, indices

def place_stars(count: int, width: float, height: float, min_: float, max_: float):
    for _ in range(count):
        r1 = random()
        r2 = random()
        r3 = random()
        r4 = random()
        yield width * r3
        yield height * r4
        yield r2 * 2 * pi
        yield max_ * r1 + (1 - r1) * min_

class InstancedWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "Instanced", draw_rate=1/140, vsync=True, update_rate=1/10000, resizable=True)
        self.points, self.colors, self.indices = gen_star(5)

        self.point_buffer = gl.BufferDescription(
            self.ctx.buffer(data=array('f', self.points)), '2f', ['in_pos']
        )

        self.color_buffer = gl.BufferDescription(
            self.ctx.buffer(data=array('f', self.colors)), '3f', ['in_colour']
        )
        self.index_buffer = self.ctx.buffer(data=array('I', self.indices))

        self.geometry = self.ctx.geometry(
            [self.point_buffer, self.color_buffer], self.index_buffer, mode=self.ctx.TRIANGLES, index_element_size=4
        )
        self.shader = self.ctx.program(
            vertex_shader=get_prog_string('instanced_vs'),
            fragment_shader=get_prog_string('instanced_fs')
        )
        self.shader['StarBlock'] = 1

        self.star_buffer = self.ctx.buffer(reserve=4*1024)
        self.star_data = array('f', place_stars(1024, self.width, self.height, 1.0, 200.0)) # scale, rotation, x, y 1024 times
        self._data_b = self.star_data[:]
        self._data_stale = True

        self.text = Text("FPS: 0000", self.center_x, self.center_y, (255, 255, 255), anchor_x='center', anchor_y='center')

        self.camera = Camera2D()
        self.base = self.camera.viewport.size

        self.box_idx, self.box_points, self.box_colours = gen_stylebox(200, 200, self.center, (70.0, 70.0, 70.0, 70.0), (20.0, 20.0, 20.0, 20.0), resolution=12, inner_corner_radius_control=False, inner_colour=(0, 0, 0, 255), gradient=True)

        def flatten(items):
            for item in items:
                for element in item:
                    yield element
        self.point_buffer = self.ctx.buffer(data=array('f', flatten(self.box_points)))
        self.colour_buffer = self.ctx.buffer(data=array('B', flatten(self.box_colours)))
        self.indices_buffer = self.ctx.buffer(data=array('i', self.box_idx))

        self.box_geometry = self.ctx.geometry(
            [
                gl.BufferDescription(self.point_buffer, '2f', ['in_pos']),
                gl.BufferDescription(self.colour_buffer, '4f1', ['in_colour'])
            ],
            index_buffer=self.indices_buffer,
            mode=gl.TRIANGLES
        )
        self.box_shader = self.ctx.program(
            vertex_shader=get_prog_string('style_vs'),
            fragment_shader=get_prog_string('style_fs')
        )

    def on_resize(self, width, height):
        # self.camera.match_window(projection=False, aspect=16.0/9.0)
        self.camera.match_window(projection=False)

        aspect = 16.0 / 9.0
        v_aspect = width / height

        if aspect * height < width:
            w = v_aspect * self.base[1]
            h = self.base[1]
        else:
            w = self.base[0]
            h = self.base[0] / v_aspect
        self.camera.projection = XYWH(0.0, 0.0, w, h)

    def on_draw(self):
        self.clear()

        #self.ctx.disable(self.ctx.CULL_FACE)
        #with self.camera.activate():
        #    for tri in range(10):
        #        ai, bi, ci = self.indices[3*tri], self.indices[3*tri+1], self.indices[3*tri+2]
        #        ax, ay = self.points[2*ai], self.points[2*ai+1]
        #        bx, by = self.points[2*bi], self.points[2*bi+1]
        #        cx, cy = self.points[2*ci], self.points[2*ci+1]
        #        draw_triangle_filled(ax, ay, cx, cy, bx, by, (255, 255, 255))

        # if self._data_stale:
        #     self.star_buffer.write(self.star_data)
        #     self._data_stale = False

        # with self.camera.activate():
        #     with self.ctx.enabled(self.ctx.DEPTH_TEST):
        #         self.star_buffer.bind_to_uniform_block(1)
        #         self.geometry.render(self.shader, instances=1024)
        #     # self.text.draw()

        # with self.camera.activate():
        #     for tri in range(0, len(self.box_idx)//3):
        #         ai = self.box_idx[3*tri]
        #         bi = self.box_idx[3*tri + 1]
        #         ci = self.box_idx[3*tri + 2]
        #         ax, ay = self.box_points[ai]
        #         bx, by = self.box_points[bi]
        #         cx, cy = self.box_points[ci]
        #         draw_triangle_filled(ax, ay, bx, by, cx, cy, (255, 255, 255))
        #         # draw_triangle_outline(ax, ay, bx, by, cx, cy, (0, 255, 0), 2)
        #     # draw_points(self.box_points[:4*5], (255, 0, 0), 4)

        self.box_geometry.render(self.box_shader)

    
    def on_update(self, delta_time):
        # self.text.text = f"FPS: {1.0/delta_time:.0f}"
        a = self.star_data
        b = self._data_b
        speed = 2.0 * delta_time
        for idx in range(1024):
            b[4*idx+2] = (a[4*idx+2] + speed * (0.5 + (idx * 997) % 1.5)) % tau
        self.star_data, self._data_b = self._data_b, self.star_data
        self._data_stale = True



def main():
    win = InstancedWindow()
    win.run()
