from __future__ import annotations

import arcade
from arcade.future.input.inputs import MouseButtons
from arcade.draw import draw_triangle_filled

from common.util.procedural_animator import ProceduralAnimator


GRID_WIDTH = 10
GRID_HEIGHT = 10

SQUARE_SIZE = 50

triangulations = (
    (), # 0000
    ((0, 1, 7),), # 0001 x=0 (x, x+1, x-1)
    ((2, 3, 1),), # 0010 x=2 (x, x+1, x-1)
    ((0, 2, 7), (7, 2, 3),), # 0011 x=0 (x, x+2, x-1) (x-1, x+2, x+3)
    ((4, 3, 5),), # 0100 x=4 (x, x+1, x-1)
    ((0, 1, 7), (7, 1, 3), (7, 3, 5), (3, 4, 5),), # 0101 x=0 (x, x+1, x-1) (x-1, x+1, x+3) (x-1, x+3, x+5) (x+3, x+4, x+5)
    ((2, 4, 1), (1, 4, 5),), # 0110 x=2 (x, x+2, x-1) (x-1, x+2, x+3)
    ((2, 4, 5), (2, 5, 7), (2, 7, 0),), # 0111 x=2 (x, x+2, x+3) (x, x+3, x+5) (x, x+5, x+6)
    ((6, 7, 5),), # 1000 x=6 (x, x+1, x-1)
    ((6, 0, 5), (5, 0, 1),), # 1001 x=6 (x, x+2, x-1) (x-1, x+2, x+3)
    ((2, 3, 1), (1, 3, 5), (1, 5, 7), (5, 6, 7),), # 1010 x=2 (x, x+1, x-1) (x-1, x+1, x+3) (x-1, x+3, x+5) (x+3, x+4, x+5)
    ((0, 2, 3), (0, 3, 5), (0, 5, 6),), # 1011 x=0  (x, x+2, x+3) (x, x+3, x+5) (x, x+5, x+6)
    ((4, 6, 3), (3, 6, 7),), # 1100 x=4 (x, x+2, x-1) (x-1, x+2, x+3)
    ((6, 0, 1), (6, 1, 3), (6, 3, 4),), # 1101 x=6 (x, x+2, x+3) (x, x+3, x+5) (x, x+5, x+6)
    ((4, 6, 7), (4, 7, 1), (4, 1, 2),), # 1110 x=4 (x, x+2, x+3) (x, x+3, x+5) (x, x+5, x+6)
    ((0, 2, 4), (0, 4, 6),), # 1111 x=0 (x, x+2, x-2), (x-2, x+2, x+4)
)


class MarchGrid:

    def __init__(self):
        self.grid = list(
            list(-1.0 for _ in range(GRID_WIDTH))
            for _ in range(GRID_HEIGHT)
        )

        self._freq = 1.0
        self._damp = 0.5
        self._resp = 2.0

        self.animators: tuple[ProceduralAnimator, ...] = tuple(
            ProceduralAnimator(1.0, 0.5, 2.0, -1.0, -1.0, 0.0)
            for _ in range(GRID_WIDTH * GRID_HEIGHT)
        )

    @property
    def frequency(self):
        return self._freq

    @frequency.setter
    def frequency(self, new_freq):
        if new_freq == self._freq:
            return

        self._freq = new_freq
        for anim in self.animators:
            anim.update_frequency(new_freq)

    @property
    def damping(self):
        return self._damp

    @damping.setter
    def damping(self, new_damp):
        if new_damp == self._damp:
            return

        self._damp = new_damp
        for anim in self.animators:
            anim.update_damping(new_damp)

    @property
    def response(self):
        return self._resp

    @response.setter
    def response(self, new_resp):
        if new_resp == self._resp:
            return

        self._resp = new_resp
        for anim in self.animators:
            anim.update_response(new_resp)

    def __getitem__(self, item: tuple[int, int]):
        x, y = item
        return self.grid[y][x]

    def __setitem__(self, key: tuple[int, int], value: float):
        x, y = key
        self.grid[y][x] = min(1.0, max(-1.0, value))

    def to_point(self, idx: int):
        return idx % GRID_WIDTH, idx // GRID_WIDTH

    def from_point(self, x, y):
        return y * GRID_WIDTH + x

    def update(self, dt: float):
        for idx in range(GRID_WIDTH * GRID_HEIGHT):
            x, y = self.to_point(idx)
            val = self[x, y]
            self.animators[idx].update(dt, val)

    def closest_point(self, x: float, y: float):
        s_x = x / SQUARE_SIZE
        s_y = y / SQUARE_SIZE

        i_x = int(round(s_x))
        i_y = int(round(s_y))

        return i_x, i_y

    def set_closest_point(self, x: float, y: float, value: float):
        i_x, i_y = self.closest_point(x, y)

        if 0 <= i_x < GRID_WIDTH and 0 <= i_y < GRID_HEIGHT:
            self[i_x, i_y] = value

    def get_closest_point(self, x, y):
        i_x, i_y = self.closest_point(x, y)
        if 0 <= i_x < GRID_WIDTH and 0 <= i_y < GRID_HEIGHT:
            return self[i_x, i_y]
        return None

    def anim_val(self, x, y):
        idx = self.from_point(x, y)
        return self.animators[idx].y

    def triangulate_point(self, x: int, y: int):
        a = self.anim_val(x, y)
        b = self.anim_val(x, y+1)
        c = self.anim_val(x+1, y+1)
        d = self.anim_val(x+1, y)

        a_b = (0.5 if a == b else (1.0 if b == 0.0 else -a/(b - a)))
        b_c = (0.5 if b == c else (1.0 if c == 0.0 else -b/(c - b)))
        d_c = (0.5 if d == c else (1.0 if c == 0.0 else -d/(c - d)))
        a_d = (0.5 if a == d else (1.0 if d == 0.0 else -a/(d - a)))

        idx = (a > 0) * 1 + (b > 0) * 2 + (c > 0) * 4 + (d > 0) * 8
        triangulation = triangulations[idx]
        points = (
            (x, y), (x, y+a_b),
            (x, y+1), (x+b_c, y+1),
            (x+1, y+1), (x+1, y+d_c),
            (x+1, y), (x+a_d, y)
        )

        return (tuple(points[i] for i in tri) for tri in triangulation)

    def update_animators(self, new_frequency = None, new_damping = None, new_response = None):
        for animator in self.animators:
            animator.update_values(new_frequency, new_damping, new_response)

    def draw(self):
        for y, row in enumerate(self.grid[:]):
            for x, val in enumerate(row[:]):
                if x < GRID_WIDTH-1 and y < GRID_HEIGHT-1:
                    triangles = self.triangulate_point(x, y)
                    for tri in triangles:
                        a, b, c = tri
                        draw_triangle_filled(
                            a[0]*SQUARE_SIZE, a[1]*SQUARE_SIZE,
                            b[0]*SQUARE_SIZE, b[1]*SQUARE_SIZE,
                            c[0]*SQUARE_SIZE, c[1]*SQUARE_SIZE,
                            (255, 255, 255, 255)# , 2
                        )
                c = (255 * (val < 0), 255 * (val > 0),  255, 255)
                arcade.draw_point(x * SQUARE_SIZE, y * SQUARE_SIZE, c, 5)


class SquareWindow(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "Marching Squares")
        self.cam = arcade.camera.Camera2D(position=(0.0, 0.0))
        self.grid = MarchGrid()

        self.grid[0, 0] = 1
        self.grid[0, 1] = 1
        self.grid[2, 3] = 1

        self.grid.triangulate_point(0, 0)
        self.grid.triangulate_point(0, 1)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        w_x, w_y, w_z = self.cam.unproject((x, y))
        v = self.grid.get_closest_point(w_x, w_y)
        self.grid.set_closest_point(w_x, w_y, v + scroll_y / 16.0)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int):
        try:
            button = MouseButtons(_buttons)
        except ValueError:
            return

        if button == MouseButtons.MIDDLE:
            o_pos = self.cam.position
            self.cam.position = int(o_pos[0] - dx), int(o_pos[1] - dy)
        elif button == MouseButtons.LEFT:
            w_x, w_y, w_z = self.cam.unproject((x, y))
            self.grid.set_closest_point(w_x, w_y, 1)
        elif button == MouseButtons.RIGHT:
            w_x, w_y, w_z = self.cam.unproject((x, y))
            self.grid.set_closest_point(w_x, w_y, -1)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        button = MouseButtons(button)

        if button == MouseButtons.LEFT:
            w_x, w_y, w_z = self.cam.unproject((x, y))
            self.grid.set_closest_point(w_x, w_y, 1)

        elif button == MouseButtons.RIGHT:
            w_x, w_y, w_z = self.cam.unproject((x, y))
            self.grid.set_closest_point(w_x, w_y, -1)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time: float):
        self.grid.update(delta_time)
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.cam.use()

        self.grid.draw()


# For use once arcade-experiments has imgui
"""
def draw_debug_menu(self):
    imgui.new_frame()
    imgui.set_next_window_size(150, 350, condition=imgui.FIRST_USE_EVER)

    imgui.begin("March Square Debug Menu", False)
    _, self.grid.frequency = imgui.slider_float("Frequency", self.grid.frequency, 0.1, 10.0)
    _, self.grid.damping = imgui.slider_float("Damping", self.grid.damping, 0.1, 10.0)
    _, self.grid.response = imgui.slider_float("Response", self.grid.response, 0.1, 10.0)
    imgui.separator()
    PERF_TRACKER.imgui_draw("updates", "on_draw")

    imgui.end()
    imgui.end_frame()
"""


def main():
    win = SquareWindow()
    win.run()
