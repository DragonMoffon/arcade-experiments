from queue import Queue
from time import perf_counter
from math import sin, pi

from arcade import Window, get_window
from arcade.clock import GLOBAL_CLOCK
import arcade.gl as gl

from common.data_loading import make_package_string_loader
import oscilliscope.data as data

get_shader = make_package_string_loader(data, 'glsl')

class Oscilliscope:

    def __init__(self, display_size: tuple[int, int]) -> None:
        self.ctx = ctx = get_window().ctx
        self._display_texture: gl.Texture2D = ctx.texture(display_size)
        self._strike_texture: gl.Texture2D = ctx.texture(display_size)

        self._display_layer: gl.Framebuffer = ctx.framebuffer(color_attachments=[self._display_texture])
        self._strike_layer: gl.Framebuffer = ctx.framebuffer(color_attachments=[self._strike_texture])

        self._full_geometry = gl.geometry.quad_2d_fs()

        self._crt_program: gl.Program = ctx.program(
            vertex_shader=get_shader('osc_vs'),
            fragment_shader=get_shader('osc_fs')
        )
        self._display_program: gl.Program = ctx.program(
            vertex_shader=get_shader('disp_vs'),
            fragment_shader=get_shader('disp_fs')
        )

        try:
            self._crt_program['radius'] = 0.0001
            self._crt_program['decay'] = 40.0
        except:
            pass

        self._i_signal = Queue()
        self._x_signal = Queue()
        self._y_signal = Queue()
        self._d_signal = Queue()

        self.time = None

    def pass_signal(self, x, y, i, d):
        self._x_signal.put(x, False)
        self._y_signal.put(y, False)
        self._i_signal.put(i, False)
        self._d_signal.put(d, False)

    def process_signal(self):
        if self.time is None:
            self.time = perf_counter()
        x = 0.0 if self._x_signal.empty() else self._x_signal.get(False)
        y = 0.0 if self._y_signal.empty() else self._y_signal.get(False)
        i = 0.0 if self._i_signal.empty() else self._i_signal.get(False)
        d = 0.0 if self._d_signal.empty() else self._d_signal.get(False)

        blend_func = self.ctx.blend_func
        with self._strike_layer.activate():
            self.ctx.blend_func = gl.BLEND_DEFAULT
            self._crt_program['signal'] = x, y, i, d
            self._display_texture.use()
            self._full_geometry.render(self._crt_program)
        self.ctx.blend_func = blend_func

        self._strike_layer, self._display_layer = self._display_layer, self._strike_layer
        self._strike_texture, self._display_texture = self._display_texture, self._strike_texture

    def display_signal(self):
        blend_func = self.ctx.blend_func
        self.ctx.blend_func = gl.BLEND_DEFAULT
        self._display_texture.use()
        self._full_geometry.render(self._display_program)
        self.ctx.blend_func = blend_func


class OscWindow(Window):

    def __init__(self):
        super().__init__(720, 720, "Oscilliscope", update_rate=1/10000, draw_rate=1/60)
        self.set_mouse_visible(False)
        self.oscilliscope: Oscilliscope = Oscilliscope(self.size)
        # Oscilliscope properties
        self.sweep = 0.01
        self.x_bounds = 2.0 # Seconds
        self.y_bounds = 2.0 # Volts

        # Signal properties
        self.frequency = 4.0
        self.amplitude = 1.0

    def on_draw(self):
        self.clear()
        self.oscilliscope.display_signal()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool | None:
        self.x_bounds = min(10.0, max(0.1, self.x_bounds + scroll_y / 10))

    def on_update(self, delta_time: float):
        print(1/delta_time)
        x = 2.0 * (GLOBAL_CLOCK.time % self.sweep) / self.sweep - 1.0
        t = GLOBAL_CLOCK.time + x * self.x_bounds
        y = self.amplitude * sin(2 * pi * self.frequency * t) / self.y_bounds
        i = 1.0
        d = GLOBAL_CLOCK.delta_time
        self.oscilliscope.pass_signal(x, y, i, d)
        self.oscilliscope.process_signal()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self.oscilliscope.pass_signal(2.0 * (x - self.center_x) / self.width, 2.0 * (y - self.center_y) / self.height, 5.0, 0.0)
        self.oscilliscope.process_signal()
        
def main():
    win = OscWindow()
    win.run()
