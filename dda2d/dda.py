import arcade
from pyglet.math import Vec2

from common.util import clamp

PointList = list[Vec2]


def snap(point: Vec2, step: float, x_offset: float = 0.0, y_offset: float = 0.0) -> Vec2:
    return Vec2(int(point.x / step), int(point.y / step)) * step + Vec2(x_offset % step + (step / 2), y_offset % step + (step / 2) - step)


def dda(start: Vec2, end: Vec2) -> PointList:
    points: PointList = []

    dx = end.x - start.x
    dy = end.y - start.y

    # Number of steps in the loop needed to draw the whole line
    steps = int(abs(dx)) if abs(dx) > abs(dy) else int(abs(dy))

    if steps < 1:
        return [start, end]

    # Rise and rtun
    x_inc = float(dx / steps)
    y_inc = float(dy / steps)

    px = start.x
    py = start.y

    # Gen points
    for _ in range(0, steps + 1):
        points.append(Vec2(px, py))
        px += x_inc
        py += y_inc

    return points


class Grid:
    def __init__(self, x_size: int, y_size: int, tile_size: int = 1,
                 x_offset: float = 0.0, y_offset: float = 0.0):
        self.x_size = x_size
        self.y_size = y_size
        self.tile_size = tile_size
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.sprites = []
        self.sprite_list = arcade.SpriteList()

        for x in range(self.x_size // self.tile_size):
            l = []
            for y in range(self.y_size // self.tile_size):
                p = self.index_to_point((x, y))
                s = arcade.SpriteSolidColor(self.tile_size, self.tile_size, p.x, p.y, arcade.types.Color.random())
                l.append(s)
                self.sprite_list.append(s)
                s.scale = 0
            self.sprites.append(l)


    @property
    def max_x(self) -> float:
        return self.x_offset + self.x_size

    @property
    def max_y(self) -> float:
        return self.y_offset + self.y_size

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

    def draw_point(self, point: Vec2, color = arcade.color.RED):
        sprite_index = self.point_to_index(point)
        try:
            sprite = self.sprites[int(sprite_index[0])][int(sprite_index[1])]
        except IndexError:
            return
        sprite.scale = 1
        sprite.color = color

    def draw_point_list(self, point_list: PointList, color = arcade.color.RED):
        for x in self.sprites:
            for y in x:
                y.scale = 0
        for p in point_list:
            self.draw_point(p, color)

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
