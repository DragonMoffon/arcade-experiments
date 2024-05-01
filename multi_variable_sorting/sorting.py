from __future__ import annotations

import multi_variable_sorting.data as data
from data_loading import make_package_string_loader
from json import loads

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, TypeVar, Type

import arcade
from arcade import Window
from pyglet.graphics import Batch

load_json_string = make_package_string_loader(data, "json")
load_json = lambda name: loads(load_json_string(name))


### CONSTANTS
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
JSON_NAME = "objects"
POINT_SIZE = 2
FONT_NAME = "bahnschrift"
SELECTED_CHOICES = 10
#############

dimensionmap = {
    "h": "height",
    "l": "length",
    "w": "width",
    "d": "diameter",
    "p": "depth",
    "t": "thickness"
}

T = TypeVar("T")
PointsAndLabels = list[tuple[tuple[float, float], float, str, float, float]]


def cast_or_none(obj, t: Type[T]) -> T | None:
    if obj is None:
        return None
    return t(obj)


# NOTE: THIS IS THE FUNCTION ACTUALLY IN THE BOT
def points_from_objects(val: float, objects: list[DigiObject], int_priority: float = 1, one_priority: float = 1) -> PointsAndLabels:
    li = []
    for obj in objects:
        ratio = val / obj.unitlength
        rounded_ratio = round(ratio)
        intness = 2.0 * (ratio-rounded_ratio)  # -1.0 to 1.0

        oneness = (1.0-ratio if ratio > 1 else 1.0/ratio - 1.0)
        oneness = math.copysign(oneness**2 / 25.0, oneness)

        p = oneness / one_priority, intness / int_priority
        d = math.dist((0, 0), p)

        li.append((p, d, obj.name, obj.unitlength, ratio))
    return sorted(li, key=lambda x: x[1])


class ObjectData(TypedDict):
    name: str
    dimension: str
    height: str | None
    length: str | None
    width: str | None
    diameter: str | None
    depth: str | None
    thickness: str | None
    weight: str | None


JSONData = list[ObjectData]


@dataclass
class DigiObject:
    name: str
    dimension: str
    height: float | None = None
    length: float | None = None
    width: float | None = None
    diameter: float | None = None
    depth: float | None = None
    thickness: float | None = None
    weight: float | None = None

    @property
    def unitlength(self) -> float:
        return getattr(self, dimensionmap[self.dimension])

    @classmethod
    def from_JSON(cls, data: ObjectData) -> DigiObject:
        return DigiObject(
            name = data["name"],
            dimension = data["dimension"],
            height = cast_or_none(data.get("height", None), float),
            length = cast_or_none(data.get("length", None), float),
            width = cast_or_none(data.get("width", None), float),
            diameter = cast_or_none(data.get("diameter", None), float),
            depth = cast_or_none(data.get("depth", None), float),
            thickness = cast_or_none(data.get("thickness", None), float),
            weight = cast_or_none(data.get("weight", None), float),
        )

BestList = tuple[float, tuple[float, float], DigiObject]


class PlotWindow(Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, title = "Object Plot")
        self.int_priority = 1
        self.one_priority = 1
        self.dist_limit = 1.0

        self.draw_labels = True

        self.current_height = 1.0

        self.camera = arcade.camera.Camera2D(position=(0.0, 0.0))

        self.graph_size = 100.0

        self.mouse_down = False

        self.objects_path = Path(JSON_NAME)
        self.objects = self.create_objects()
        self.points = self.create_points()

        self.batch = Batch()
        self.texts: list[arcade.Text] = []

    def create_objects(self) -> list[DigiObject]:
        objs = []
        j: JSONData = load_json(self.objects_path)
        for o in j:
            objs.append(DigiObject.from_JSON(o))
        return objs

    def create_points(self) -> PointsAndLabels:
        self.points = points_from_objects(self.current_height, self.objects, self.int_priority, self.one_priority)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_0 or symbol == arcade.key.NUM_0:
            self.camera.position = (0.0, 0.0)
            self.graph_size = 100.0
        elif symbol == arcade.key.NUM_7:
            self.current_height += 1
        elif symbol == arcade.key.NUM_1:
            self.current_height -= 1
        elif symbol == arcade.key.NUM_8:
            self.current_height += 0.1
        elif symbol == arcade.key.NUM_2:
            self.current_height -= 0.1
        elif symbol == arcade.key.NUM_9:
            self.current_height += 0.01
        elif symbol == arcade.key.NUM_3:
            self.current_height -= 0.01
        elif symbol == arcade.key.L:
            self.draw_labels = not self.draw_labels
        elif symbol == arcade.key.NUM_DIVIDE:
            self.int_priority -= (1 if self.int_priority > 1.01 else 0.1)
        elif symbol == arcade.key.NUM_MULTIPLY:
            self.int_priority += (1 if self.int_priority > 0.99 else 0.1)
        elif symbol == arcade.key.NUM_SUBTRACT:
            self.one_priority -= (1 if self.one_priority > 1.01 else 0.1)
        elif symbol == arcade.key.NUM_ADD:
            self.one_priority += (1 if self.one_priority > 0.99 else 0.1)
        elif symbol == arcade.key.MINUS:
            self.dist_limit -= 0.1
        elif symbol == arcade.key.EQUAL:
            self.camera.zoom -= 0.1
        elif symbol == arcade.key.Z:
            self.camera.zoom += 1.1
        elif symbol == arcade.key.X:
            self.graph_size /= 1.1

        self.camera.zoom = max(0.1, self.camera.zoom)
        self.current_height = max(0, round(self.current_height, 2))
        self.int_priority = max(0.1, round(self.int_priority, 1))
        self.one_priority = max(0.1, round(self.one_priority, 1))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0:
            self.graph_size = self.graph_size * 1.1
        else:
            self.graph_size = self.graph_size / 1.1
        self.graph_size = max(1, self.graph_size)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.mouse_down:
            ox, oy = self.camera.position
            self.camera.position = ox - dx, oy - dy

    def on_draw(self):
        self.camera.use()
        self.create_points()
        self.texts.clear()
        self.clear(arcade.color.GRAY_BLUE)

        # Draw plot
        arcade.draw_line(-self.width, 0, self.width, 0, arcade.color.GRAY)
        arcade.draw_line(0, -self.height, 0, self.height, arcade.color.GRAY)
        points = [(p[0] * self.graph_size,p[1] * self.graph_size) for p, _, _, _, _ in self.points]

        # Draw points
        arcade.draw_points(points, arcade.color.WHITE, POINT_SIZE)

        # Draw radius
        arcade.draw_circle_filled(0, 0, self.dist_limit * self.graph_size, (0, 0, 255, 32))

        point_num = 0
        possible_matches = 0

        # Draw points in the circle blue
        for p, d, l, s, r in self.points:
            point_num += 1

            # get screen p
            screen_p = p[0] * self.graph_size, p[1] * self.graph_size
            if d < self.dist_limit:
                arcade.draw_point(screen_p[0], screen_p[1], arcade.color.BLUE, POINT_SIZE)
                possible_matches += 1

            # If point is first 10, draw line
            if point_num <= 10 and d < self.dist_limit:
                arcade.draw_line(0, 0, screen_p[0], screen_p[1], arcade.color.RED)

            # Draw labels
            intness = abs(r - round(r))
            if self.draw_labels and point_num <= 100:
                if d < self.dist_limit * 2:
                    c = arcade.color.BLUE if d <= self.dist_limit else arcade.color.WHITE
                    self.texts.append(arcade.Text(l, screen_p[0] + 1, screen_p[1] + 1,
                                      font_name = FONT_NAME, color = arcade.color.GREEN if point_num <= 10 else c,
                                      font_size = 16, batch = self.batch))
                    self.texts.append(arcade.Text(f"{s:.2f}m ({r:.1f}x)", screen_p[0] + 1, screen_p[1] - 1,
                                      font_name = FONT_NAME, color = arcade.color.GOLD if intness <= 0.05 or intness >= 0.95 else c,
                                      font_size = 16, anchor_y = "top", batch = self.batch))

        with self.ctx.pyglet_rendering():
            self.batch.draw()

        self.default_camera.use()
        # Draw current height
        arcade.draw_text(f"Current height: {self.current_height}m\nInteger priority: {self.int_priority}\nOneness priority: {self.one_priority}\nMatches: {possible_matches}",
                          5, self.height - 5,
                          font_name = FONT_NAME, color = arcade.color.RED, font_size = 24,
                          anchor_y = "top", multiline = True, width = self.width)


def main():
    window = PlotWindow()
    window.run()
