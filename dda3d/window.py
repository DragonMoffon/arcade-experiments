from arcade import Window, camera, draw, SpriteSolidColor, SpriteList
from pyglet.math import Vec3

from dda3d.dda import dda
from common.util import clamp


GRID_SIZE = (10, 10, 1)
SQUARE_SIZE = 32


class DDA3DWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "DDA 3D")
        self._camera = camera.Camera2D()
        self._camera.position = GRID_SIZE[0] * SQUARE_SIZE / 2.0, GRID_SIZE[1] * SQUARE_SIZE / 2.0
        self._ray_pos = (0.0, 0.0, 0.5)
        self._ray_dir = (1.0, 0.0, 0.0)
        self._ray_len = 0.0

        self._grid_sprites: SpriteList = SpriteList()
        self._grid: dict[tuple[int, int], SpriteSolidColor] = dict()
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                sprite = SpriteSolidColor(SQUARE_SIZE, SQUARE_SIZE, (x + 0.5) * SQUARE_SIZE, (y + 0.5) * SQUARE_SIZE)
                self._grid[(x, y)] = sprite
                self._grid_sprites.append(sprite)

        self._dirty = True

    def do_dda(self):
        self._dirty = False
        for sprite in self._grid_sprites:
            sprite.color = 0, 0, 0, 0

        result = dda(*self._ray_pos, *self._ray_dir, *GRID_SIZE)

        for point in result.path[1:-1]:
            sprite = self._grid[(point.x, point.y)]
            sprite.color = 0, 255, 255, int(255 * (point.d / 2**0.5))

        start = self._grid[(result.x1, result.y1)]
        start.color = 0, 0, 255, 255

        end = self._grid[(result.x2, result.y2)]
        end.color = 0, 255, 0, 255

        self._ray_len = result.d

    def on_draw(self):
        if self._dirty:
            self.do_dda()

        self.clear()
        self._camera.use()
        self._grid_sprites.draw()
        draw.draw_line(
            self._ray_pos[0] * SQUARE_SIZE, self._ray_pos[1] * SQUARE_SIZE,
            (self._ray_pos[0] + self._ray_dir[0]*self._ray_len) * SQUARE_SIZE,
            (self._ray_pos[1] + self._ray_dir[1]*self._ray_len) * SQUARE_SIZE,
            color=(255, 0, 0, 255)
        )
        draw.draw_point(self._ray_pos[0]*SQUARE_SIZE, self._ray_pos[1]*SQUARE_SIZE, (255, 0, 0, 255), 2)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        n_x, n_y, _ = self._camera.unproject((x, y))
        d_x = n_x / SQUARE_SIZE - self._ray_pos[0]
        d_y = n_y / SQUARE_SIZE - self._ray_pos[1]
        d = Vec3(d_x, d_y, 0.0).normalize()

        self._ray_dir = d.x, d.y, d.z
        self._dirty = True

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        n_x, n_y, _ = self._camera.unproject((x, y))
        x = clamp(0.0001, n_x / SQUARE_SIZE, GRID_SIZE[0] - 0.0001)
        y = clamp(0.0001, n_y / SQUARE_SIZE, GRID_SIZE[1] - 0.0001)
        self._ray_pos = (x, y, 0.5)
        self._ray_dir = (1.0, 0.0, 0.0)
        self._dirty = True


def main():
    win = DDA3DWindow()
    win.run()
