from __future__ import annotations

from common.util import clamp
import multi_variable_sorting.data as data
from common.data_loading import make_package_string_loader
from json import loads

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, TypeVar, Type

import arcade
from arcade import Window
from pyglet.graphics import Batch

load_json_string = make_package_string_loader(data, "json")
load_json = lambda name: loads(load_json_string(name))  # noqa: E731


### CONSTANTS
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
JSON_NAME = "objects"
POINT_SIZE = 2
FONT_NAME = "GohuFont 11 Nerd Font Mono"
SELECTED_CHOICES = 10
BEST_X = 10
TOP_X = 30
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
# def points_from_objects(val: float, objects: list[DigiObject], int_priority: float = 1, one_priority: float = 1) -> PointsAndLabels:
#     li = []
#     for obj in objects:
#         ratio = val / obj.unitlength
#         rounded_ratio = round(ratio)
#         intness = 2.0 * (ratio-rounded_ratio)  # -1.0 to 1.0
#
#         oneness = (1.0-ratio if ratio > 1 else 1.0/ratio - 1.0)
#         oneness = math.copysign(oneness**2 / 25.0, oneness)
#
#         p = oneness / one_priority, intness / int_priority
#         d = math.dist((0, 0), p)
#
#         li.append((p, d, obj.name, obj.unitlength, ratio))
#     return sorted(li, key=lambda x: x[1])


def points_from_objects(val: float, objects: list[DigiObject], int_prio = 1.0, one_prio = 1.0):
    for obj in objects:
        ratio = val / obj.unitlength
        rounded_ratio = round(ratio)
        intness = 2.0 * (ratio-rounded_ratio)  # -1.0 to 1.0

        oneness = (1.0-ratio if ratio > 1 else 1.0/ratio - 1.0)
        oneness = math.copysign(oneness**2 / 25.0, oneness)

        p = oneness / one_prio, intness / int_prio
        d = oneness**2 + intness**2

        yield p, d, obj


def x_best(val: float, objects: list[DigiObject], x: int, int_prio = 1.0, one_prio = 1.0):
    best_dict: dict[float, list] = {
        1.0: [],
        0.5: [],
        2.0: [],
        1.5: [],
        3.0: [],
        2.5: [],
        4.0: [],
        5.0: [],
        6.0: []
    }

    dists = []
    for obj in objects:
        ratio = val / obj.unitlength
        ratio_semi = round(ratio, 1)
        rounded_ratio = round(ratio)

        intness = 2.0 * (ratio - rounded_ratio) / int_prio

        oneness = (1.0 - ratio if ratio > 1.0 else 1.0 / ratio - 1.0) / one_prio

        dist = intness ** 2 + oneness ** 2

        p = (dist, (oneness, intness), obj)
        if ratio_semi in best_dict:
            best_dict[ratio_semi].append(p)
        else:
            dists.append(p)

    best = []
    for at_val in best_dict.values():
        best.extend(at_val)
        if len(best) >= x:
            break
    else:
        dists = sorted(dists, key=lambda p: p[0])
        best.extend(dists[:x])

    return best[:x]


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

        self.top_x = []
        self.dists = []

        self.batch = Batch()
        self.texts: list[arcade.Text] = []
        for _ in range(TOP_X):
            self.texts.append(arcade.Text(
                "", 0, 0,
                font_name=FONT_NAME,
                font_size=16, batch=self.batch
            ))
            self.texts.append(arcade.Text(
                "", 0, 0,
                font_name=FONT_NAME,
                font_size=16, anchor_y="top", batch=self.batch
            ))

        self.are_points_dirty: bool = True

    def create_objects(self) -> list[DigiObject]:
        objs = []
        j: JSONData = load_json(self.objects_path)
        for o in j:
            objs.append(DigiObject.from_JSON(o))
        return objs

    def create_points(self) -> PointsAndLabels:
        self.dists = tuple(points_from_objects(self.current_height, self.objects, self.int_priority, self.one_priority))
        self.top_x = x_best(self.current_height, self.objects, TOP_X, self.int_priority, self.one_priority)

        for index, vals in enumerate(self.top_x):
            dist, point, obj = vals
            screen_p = point[0] * self.graph_size, point[1] * self.graph_size
            r = self.current_height / obj.unitlength
            i_t, i_s = 2 * index, 2 * index + 1

            self.texts[i_t].x = self.texts[i_s].x = screen_p[0] + 1
            self.texts[i_t].y = screen_p[1] + 1
            self.texts[i_s].y = screen_p[1] - 1

            self.texts[i_t].text = str(obj.name)
            self.texts[i_s].text = f"{obj.unitlength:.2f}m ({r:.1f}x)"

            if index < BEST_X:
                self.texts[i_t].color = arcade.color.GREEN
            else:
                self.texts[i_t].color = arcade.color.BLUE

            if point[1] < 0.5:
                self.texts[i_s].color = arcade.color.GOLD
            else:
                self.texts[i_s].color = arcade.color.WHITE
        self.are_points_dirty = False

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
            self.dist_limit += 0.1
        elif symbol == arcade.key.Z:
            self.graph_size *= 1.1
        elif symbol == arcade.key.X:
            self.graph_size /= 1.1

        self.camera.zoom = max(0.1, self.camera.zoom)
        self.current_height = max(0, round(self.current_height, 2))
        self.int_priority = max(0.1, round(self.int_priority, 1))
        self.one_priority = max(0.1, round(self.one_priority, 1))

        self.are_points_dirty = False
        self.create_points()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        m_pos = self.camera.unproject((x, y))
        c_pos = self.camera.position

        if scroll_y > 0:
            self.graph_size = self.graph_size * 1.1
            self.camera.position = m_pos[0] * 1.1 + (c_pos[0] - m_pos[0]), m_pos[1] * 1.1 + (c_pos[1] - m_pos[1])
        else:
            self.graph_size = self.graph_size / 1.1
            self.camera.position = m_pos[0] / 1.1 + (c_pos[0] - m_pos[0]), m_pos[1] / 1.1 + (c_pos[1] - m_pos[1])
        self.graph_size = clamp(1, self.graph_size, 50000)

        self.are_points_dirty = True

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.mouse_down:
            ox, oy = self.camera.position
            self.camera.position = ox - dx, oy - dy

    def on_draw(self):
        if self.are_points_dirty:
            self.create_points()

        self.camera.use()
        self.clear()

        # Draw plot
        arcade.draw_line(-self.width * self.graph_size + self.camera.position[0], 0, self.width * self.graph_size + self.camera.position[0], 0, arcade.color.GRAY)
        arcade.draw_line(0, -self.height * self.graph_size + self.camera.position[1], 0, self.height * self.graph_size + self.camera.position[1], arcade.color.GRAY)
        points = [(p[0] * self.graph_size, p[1] * self.graph_size) for p, _, _ in self.dists]

        # Draw points
        arcade.draw_points(points, arcade.color.WHITE, POINT_SIZE)

        # Draw radius
        arcade.draw_circle_filled(0, 0, self.dist_limit * self.graph_size, (0, 0, 255, 32))

        with self.ctx.pyglet_rendering():
            self.batch.draw()

        self.default_camera.use()
        # Draw current height
        arcade.draw_text(f"Current height: {self.current_height}m\nInteger priority: {self.int_priority}\nOneness priority: {self.one_priority}",
                          5, self.height - 5,
                          font_name = FONT_NAME, color = arcade.color.RED, font_size = 24,
                          anchor_y = "top", multiline = True, width = self.width)


def main():
    window = PlotWindow()
    window.run()
