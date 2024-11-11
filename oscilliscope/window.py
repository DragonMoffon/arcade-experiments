from queue import Queue
from time import perf_counter
from math import sin, pi

from arcade import Window, get_window, Text, key as keys
from arcade.key import MOD_CTRL, MOD_ALT, MOD_SHIFT
from arcade.clock import GLOBAL_CLOCK
import arcade.gl as gl

from common.data_loading import make_package_string_loader
from common.util import clamp
import oscilliscope.data as data

get_shader = make_package_string_loader(data, 'glsl')

class Oscilliscope:

    def __init__(self, display_size: tuple[int, int]) -> None:
        self.ctx = ctx = get_window().ctx
        self._display_texture: gl.Texture2D = ctx.texture(display_size, dtype='f4')
        self._strike_texture: gl.Texture2D = ctx.texture(display_size, dtype='f4')

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


X_DEV_COUNT = 10
Y_DEV_COUNT = 10

SCROLL_SENSITIVITY = 1.0 / 1000.0
SENSITIVITY_MAP = {
    keys.KEY_1: 1,
    keys.KEY_2: 10,
    keys.KEY_3: 100,
    keys.KEY_4: 1000
} 

class OscWindow(Window):

    def __init__(self):
        super().__init__(720, 720, "Oscilliscope", update_rate=1/10000, draw_rate=1/60)
        self.set_mouse_visible(False)
        self.oscilliscope: Oscilliscope = Oscilliscope(self.size)
        # Oscilliscope properties
        self.sec_dev = 1.0 # Seconds / Devision
        self.volt_dev = 0.2 # Volts / Devision

        # Signal properties
        self.frequency = 200.0
        self.amplitude = 1.0

        self.input_modifiers = 0

        self.sensitivity = 1 / 10

        self.signal_label = Text('', 10, 10, font_name="GohuFont 11 Nerd Font Mono")
        self.oscilliscope_label = Text('', 10, self.height - 10, anchor_y='top', font_name="GohuFont 11 Nerd Font Mono")

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool | None:
        scroll = self.sensitivity * scroll_y
        if not scroll:
            return

        if self.input_modifiers & MOD_CTRL:
            # MODIFY THE SIGNAL
            if self.input_modifiers & MOD_SHIFT:
                # MODIFY AMPLITUDE
                self.amplitude = clamp(0.0, self.amplitude + scroll, 100.0)
                if self.input_modifiers & MOD_ALT:
                    self.amplitude = 0.0 if scroll < 0 else 100.0
            else:
                # MODIFY FREQUENCY
                self.frequency = clamp(0.0, self.frequency + scroll, 100.0)
                if self.input_modifiers & MOD_ALT:
                    self.frequency = 0.0 if scroll < 0 else 1 / self.sensitivity
        else:
            # MODIFY THE OSCILLISCOPE
            if self.input_modifiers & MOD_SHIFT:
                # MODIFY VOLTS PER DIVISION
                self.volt_dev = clamp(self.sensitivity, self.volt_dev + scroll, 10.0)
                if self.input_modifiers & MOD_ALT:
                    self.volt_dev = self.sensitivity if scroll < 0 else 1.0
            else:
                # MODIFY SECONDS PER DIVISION
                self.sec_dev = clamp(self.sensitivity, self.sec_dev + scroll, 1.0)
                if self.input_modifiers & MOD_ALT:
                    self.sec_dev = self.sensitivity if scroll < 0 else 1.0

    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        return
        self.oscilliscope.pass_signal(2.0 * (x - self.center_x) / self.width, 2.0 * (y - self.center_y) / self.height, 5.0, 0.0)
        self.oscilliscope.process_signal()
    
    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        self.input_modifiers = modifiers
        if symbol in SENSITIVITY_MAP:
            self.sensitivity = 1 / SENSITIVITY_MAP[symbol]

        print(f'pressed: {symbol}, {GLOBAL_CLOCK.ticks}')

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.input_modifiers = modifiers

    def on_update(self, delta_time: float):
        sweep = (self.sec_dev * X_DEV_COUNT)
        x = 2.0 * (GLOBAL_CLOCK.time % sweep) / sweep - 1.0
        y = self.amplitude * sin(2 * pi * self.frequency * GLOBAL_CLOCK.time) / (self.volt_dev * Y_DEV_COUNT)
        i = 4.0
        d = GLOBAL_CLOCK.delta_time
        self.oscilliscope.pass_signal(x, y, i, d)
        self.oscilliscope.process_signal()
        print(f'update: {GLOBAL_CLOCK.ticks}')

    def on_draw(self):
        self.clear()
        self.oscilliscope.display_signal()
        self.oscilliscope_label.text = f'Seconds per division: {self.sec_dev: .3f} - Volts per division: {self.volt_dev: .3f}'
        self.oscilliscope_label.draw()
        self.signal_label.text = f'Amplitude: {self.amplitude: .3f} - Frequency: {self.frequency: .3f}'
        self.signal_label.draw()
        print(f'draw: {GLOBAL_CLOCK.ticks}')


def main():
    win = OscWindow()
    win.run()
