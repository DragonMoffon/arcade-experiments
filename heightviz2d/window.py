import json
import math
import random

import arcade

from common.data_loading import make_package_file_opener, make_package_path_finder
from common.util import load_shared_sound
import heightviz2d.data as data

open_json_file = make_package_file_opener(data, "json")
get_png_path = make_package_path_finder(data, "png")


def cm_to_str(cm: float) -> str:
    if cm < 1:
        return f"{cm * 10:.1f}mm"
    elif cm < 100:
        return f"{cm:.1f}cm"
    elif cm < 100000:
        return f"{cm / 100:.1f}m"
    else:
        return f"{cm / 100000:.1f}km"


class ZoomBucket:

    def __init__(self, min_scale: int = -2, max_scale: int = 4):
        self._min: int = min_scale
        self._max: int = max_scale
        self.zoom_levels: tuple[arcade.SpriteList, ...] = tuple(arcade.SpriteList() for _ in range(min_scale, max_scale+1))
        self.current_focus_level: int = 0
        self._sprites: tuple[arcade.Sprite, ...] = ()
        self._item_map: dict[str, float] = {}

    def load_items(self, scale_data: dict):
        sprites = []

        for name, scale in scale_data.items():
            level = int(math.log10(scale / 10.0))
            if not (self._min <= level <= self._max):
                print(f"{name} is a level {level} object, but the range is {self._min}-{self._max}. Skipped")
                continue

            self._item_map[name] = scale
            sprite = arcade.Sprite(
                get_png_path(name),
                center_x=2.0 * (random.random() - 0.5) * 10**level
            )
            aspect = sprite.width / sprite.height

            sprite.height = scale
            sprite.depth = -scale
            sprite.width = scale * aspect
            sprite.center_y = sprite.height / 2.0
            sprite.properties["name"] = name

            self.zoom_levels[level].append(sprite)
            sprites.append(sprite)

        self._sprites = tuple(sprites)

    def draw(self):
        for level in self.zoom_levels:
            level.draw()

    def incr(self):
        self.current_focus_level += 1
        for sprite in self._sprites:
            sprite.width /= 100
            sprite.height /= 100
            sprite.center_x /= 100
            sprite.center_y = sprite.height / 2.0

    def decr(self):
        self.current_focus_level -= 1
        for sprite in self._sprites:
            sprite.width *= 100
            sprite.height *= 100
            sprite.center_x *= 100
            sprite.center_y = sprite.height / 2.0


class HeightViz2DWindow(arcade.Window):

    def __init__(self):
        super().__init__()
        self._zoom_factor = 0

        self._cam = arcade.camera.Camera2D(position=(0.0, 0.0), far=10000001)

        self._zoom_buckets = ZoomBucket()
        with open_json_file('scales') as file:
            self._zoom_buckets.load_items(json.load(file))

        self.selected_box: tuple[float, float, float, float] | None = None
        self.selected_name: str = ""
        self.selected_size: float = 0

        self.beep = load_shared_sound("blip_c")

        self.one_hundred_px = self.one_hundred_px_calc()

    def one_hundred_px_calc(self) -> float:
        p1 = self._cam.unproject((0, 0))
        p2 = self._cam.unproject((100, 0)) 
        return (p2[0] - p1[0]) * (10 ** (self._zoom_buckets.current_focus_level * 2))

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        old_selected_name = self.selected_name
        x, y, _ = self._cam.unproject((x, y))
        for sprite in sorted(self._zoom_buckets._sprites, key = lambda s: s.height):
            if (sprite.left <= x <= sprite.right) and (sprite.bottom <= y <= sprite.top):
                self.selected_box = (sprite.left, sprite.right, sprite.bottom, sprite.top)
                self.selected_name = sprite.properties["name"]
                self.selected_size = sprite.height * (10 ** (self._zoom_buckets.current_focus_level * 2))

                if self.selected_name != old_selected_name:
                    self.beep.play()
                break
        else:
            self.selected_box = None
            self.selected_name = ""
            self.selected_size = 0

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0:
            self._cam.zoom *= 1.1
            if self._cam.zoom >= 10.0:
                self._cam.zoom = 0.1
                self._zoom_factor -= 1
                self._zoom_buckets.decr()

                ox, oy = self._cam.position
                self._cam.position = ox * 100, oy * 100
        elif scroll_y < 0:
            self._cam.zoom /= 1.1
            if self._cam.zoom < 0.1:
                self._cam.zoom = 10.0
                self._zoom_factor += 1
                self._zoom_buckets.incr()

                ox, oy = self._cam.position
                self._cam.position = ox / 100.0, oy / 100.0
        self.one_hundred_px = self.one_hundred_px_calc()
        print(self.one_hundred_px)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        ox, oy = self._cam.position
        self._cam.position = ox - dx / self._cam.zoom, oy - dy / self._cam.zoom

    def on_draw(self):
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.clear(color=(20, 20, 20))
        self._cam.use()
        self._zoom_buckets.draw()

        if self.selected_box:
            arcade.draw_lrbt_rectangle_outline(*self.selected_box, arcade.color.WHITE_SMOKE, 3 / self._cam.zoom)
            arcade.draw_text(self.selected_name.title() + "\n" + cm_to_str(self.selected_size),
                             self.selected_box[1], self.selected_box[3],
                             arcade.color.WHITE_SMOKE,
                             anchor_x = "left", anchor_y = "top",
                             font_name="GohuFont 11 Nerd Font Mono",
                             font_size = max(22 / (self._cam.zoom), 22),
                             multiline = True,
                             width = 1000)

        self.default_camera.use()
        self.ctx.disable(self.ctx.DEPTH_TEST)
        arcade.draw_text(f"100px ~= {cm_to_str(self.one_hundred_px)}",
                         5, self.height - 5,
                         arcade.color.WHITE_SMOKE,
                         anchor_x = "left", anchor_y = "top",
                         font_name="GohuFont 11 Nerd Font Mono",
                         font_size = 22)


def main():
    win = HeightViz2DWindow()
    win.run()
