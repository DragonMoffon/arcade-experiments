from itertools import cycle
import arcade
from pyglet.math import Vec2

from animator.lerp import ease_linear
from common.util import clamp
from common.util.procedural_animator import ProceduralAnimator, SecondOrderAnimatorBase
from dda2d.dda import PointList, snap


class Grid:
    def __init__(self, x_size: int, y_size: int, tile_size: int = 1,
                 x_offset: float = 0.0, y_offset: float = 0.0):
        self.x_size = x_size
        self.y_size = y_size
        self.tile_size = tile_size
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.x_len = self.x_size // self.tile_size
        self.y_len = self.y_size // self.tile_size

        # Color
        self.color_cycle = cycle((arcade.color.RED, arcade.color.ORANGE, arcade.color.YELLOW,
                                  arcade.color.GREEN, arcade.color.BLUE, arcade.color.PURPLE,
                                  arcade.color.WHITE))
        self.color = next(self.color_cycle)

        # Create 2D animator array
        self.animators: list[list[SecondOrderAnimatorBase]] = []
        for x in range(self.x_len):
            li = []
            for y in range(self.y_len):
                p = ProceduralAnimator(1.0, 0.75, 1.0, 0.0, 0.0, 0.0)
                li.append(p)
            self.animators.append(li)

        # Create 2D sprite array and spritelist
        self.sprite_list = arcade.SpriteList()
        self.sprites = []
        for x in range(self.x_len):
            li = []
            for y in range(self.y_len):
                p = self.index_to_point((x, y))
                s = arcade.SpriteSolidColor(self.tile_size, self.tile_size, p.x, p.y, self.color)
                li.append(s)
                self.sprite_list.append(s)
                s.scale = 0
            self.sprites.append(li)

        # Create 2D scale array
        self.scales = []
        for x in range(self.x_len):
            li = []
            for y in range(self.y_len):
                li.append(0)
            self.scales.append(li)

        # Pulse
        self.local_time = 0.0
        self.last_pulse_time = 0.0
        self.pulse_sprite = arcade.SpriteSolidColor(self.tile_size, self.tile_size, 10000, 10000, arcade.color.WHITE)

    @property
    def max_x(self) -> float:
        return self.x_offset + self.x_size

    @property
    def max_y(self) -> float:
        return self.y_offset + self.y_size

    def next_color(self):
        self.color = next(self.color_cycle)
        for x in range(self.x_len):
            for y in range(self.y_len):
                self.sprites[x][y].color = self.color

    def pulse(self, point: Vec2):
        self.pulse_sprite.position = self.snap(point)
        self.last_pulse_time = self.local_time

    def draw(self, color = arcade.color.WHITE, line_width = 1):
        cur_x = self.x_offset
        cur_y = self.y_offset

        self.sprite_list.draw()

        for x in range(int(self.x_size / self.tile_size) + 1):
            arcade.draw_line(cur_x, self.y_offset, cur_x, self.max_y, color, line_width)
            cur_x += self.tile_size

        for y in range(int(self.y_size / self.tile_size) + 1):
            arcade.draw_line(self.x_offset, cur_y, self.max_x, cur_y, color, line_width)
            cur_y += self.tile_size

        self.pulse_sprite.draw()

    def get_lrbt(self, point: Vec2) -> tuple[float, float, float, float]:
        return (point.x - (self.tile_size / 2), point.x + (self.tile_size / 2),
                point.y - (self.tile_size / 2), point.y + (self.tile_size / 2))

    def draw_cursor(self, point: Vec2, color = arcade.color.WHITE_SMOKE):
        snap_p = self.snap(point)
        arcade.draw_lrbt_rectangle_filled(
            *self.get_lrbt(snap_p),
            color
        )

    def draw_point(self, point: Vec2):
        sprite_index = self.point_to_index(point)
        try:
            self.sprites[int(sprite_index[0])][int(sprite_index[1])]
        except IndexError:
            return
        self.scales[int(sprite_index[0])][int(sprite_index[1])] = 1

    def draw_point_list(self, point_list: PointList):
        for x in range(self.x_len):
            for y in range(self.y_len):
                self.scales[x][y] = 0
        for p in point_list:
            self.draw_point(p)

    def snap(self, point: Vec2) -> Vec2:
        point = Vec2(clamp(self.x_offset + self.tile_size / 2, point.x, self.max_x - self.tile_size / 2),
                     clamp(self.y_offset + self.tile_size / 2, point.y, self.max_y - self.tile_size / 2))
        return snap(point, self.tile_size, self.x_offset, self.y_offset)

    def point_to_index(self, point: Vec2) -> tuple[int, int]:
        snap = self.snap(point)
        return (int((snap.x - self.x_offset - (self.tile_size / 2)) / self.tile_size),
                int((snap.y - self.y_offset - (self.tile_size / 2)) / self.tile_size))

    def index_to_point(self, index: tuple[int, int]) -> Vec2:
        point = Vec2(index[0] * self.tile_size + (self.tile_size / 2) + self.x_offset,
                     index[1] * self.tile_size + (self.tile_size / 2) + self.y_offset)
        return point

    def update(self, delta_time: float):
        self.local_time += delta_time

        for x in range(self.x_len):
            for y in range(self.y_len):
                anim = self.animators[x][y]
                self.sprites[x][y].scale = anim.update(delta_time, self.scales[x][y])

        pulse_scale = ease_linear(1, 2, self.last_pulse_time, self.last_pulse_time + 0.5, self.local_time)
        pulse_alpha = ease_linear(255, 0, self.last_pulse_time, self.last_pulse_time + 0.5, self.local_time)

        self.pulse_sprite.alpha = pulse_alpha
        self.pulse_sprite.scale = pulse_scale
