import json
import math
import random

import arcade

from common.data_loading import make_package_file_opener, make_package_path_finder
from common.util import load_shared_sound
import heightviz2d.data as data
import heightviz2d.bg as bg

open_json_file = make_package_file_opener(data, "json")
get_png_path = make_package_path_finder(data, "png")
get_bg_path = make_package_path_finder(bg, "png")


def cm_to_str(cm: float) -> str:
    if cm < 0.1:
        return f"{cm * 10:,.2f}mm"
    if cm < 1:
        return f"{cm * 10:,.1f}mm"
    elif cm < 100:
        return f"{cm:,.1f}cm"
    elif cm < 100000:
        return f"{cm / 100:,.1f}m"
    elif cm < 100000000:
        return f"{cm / 100000:,.1f}km"
    else:
        return f"{cm / 100000:,.0f}km"


class ZoomBucket:
    def __init__(self, min_scale: int = -4, max_scale: int = 4):
        self._min: int = min_scale
        self._max: int = max_scale
        self.zoom_levels: tuple[list[arcade.Sprite], ...] = tuple(list() for _ in range(min_scale, max_scale+1))
        self._active_sprites = ()
        self._sprites: arcade.SpriteList = arcade.SpriteList()
        self.current_focus_level: int = 0
        self._item_map: dict[str, float] = {}

    def load_items(self, scale_data: dict):
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
            sprite.properties['level'] = level

            self.zoom_levels[level].append(sprite)
            self._sprites.append(sprite)

        self._sprites.sort(key=lambda s: s.depth)

    def draw(self):
        self._sprites.draw()

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

    def bring_to_front(self, sprite):
        self._sprites.remove(sprite)
        self._sprites.append(sprite)


class HeightViz2DWindow(arcade.Window):
    def __init__(self):
        super().__init__()
        self._zoom_factor = 0

        self._cam = arcade.camera.Camera2D(position=(0.0, 0.0), far=10000001)

        self._zoom_buckets = ZoomBucket()
        with open_json_file('scales') as file:
            self._zoom_buckets.load_items(json.load(file))

        self.selected_box: tuple[float, float, float, float] | None = None
        self.selected_sprite: arcade.Sprite = None
        self.selected_name: str = ""
        self.selected_size: float = 0

        self.dragging: bool = False

        self.beep = load_shared_sound("blip_c")

        self.one_hundred_px: float = 0.0
        self.closest_length_px_length: float = 0.0
        self.closest_unit_measurement: float = 0.0
        self.one_hundred_px_calc()

        bg_names = ["micro", "indoors", "outdoors", "space"]
        self.bgs = {k: arcade.Sprite(get_bg_path(k), 1, self.center_x, self.center_y) for k in bg_names}

        self.local_time = 0.0

    def one_hundred_px_calc(self) -> float:
        p1 = self._cam.unproject((0, 0))
        p2 = self._cam.unproject((100, 0)) 
        self.one_hundred_px = (p2[0] - p1[0]) * (10 ** (self._zoom_buckets.current_focus_level * 2))

        # If 100px = self.one_hundred_px...
        magnitude = math.floor(math.log10(self.one_hundred_px))
        self.closest_unit_measurement = 10 ** magnitude
        one_px = self.one_hundred_px / 100
        self.closest_length_px_length = self.closest_unit_measurement / one_px

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if self.dragging and self.selected_sprite:
            self.selected_sprite.center_y = self.selected_sprite.height / 2.0
        self.dragging = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        old_selected_name = self.selected_name
        x, y, _ = self._cam.unproject((x, y))
        for sprite in self._zoom_buckets._sprites[::-1]:
            if abs(sprite.properties.get('level', 1000000) - self._zoom_buckets.current_focus_level) > 2:
                continue

            if (sprite.left <= x <= sprite.right) and (sprite.bottom <= y <= sprite.top):
                self.selected_box = (sprite.left, sprite.right, sprite.bottom, sprite.top)
                self.selected_name = sprite.properties["name"]
                self.selected_size = sprite.height * (10 ** (self._zoom_buckets.current_focus_level * 2))
                self.selected_sprite = sprite

                if self.selected_name != old_selected_name:
                    self.beep.play()
                break
        else:
            self.selected_box = None
            self.selected_sprite = None
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
        self.one_hundred_px_calc()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons & arcade.MOUSE_BUTTON_MIDDLE:
            ox, oy = self._cam.position
            self._cam.position = ox - dx / self._cam.zoom, oy - dy / self._cam.zoom
        elif buttons & arcade.MOUSE_BUTTON_LEFT and self.selected_sprite:
            if not self.dragging:
                self._zoom_buckets.bring_to_front(self.selected_sprite)

            n_dx, n_dy, _ = self._cam.unproject((dx, dy))

            p = self.selected_sprite.position
            self.selected_sprite.position = p[0] + (n_dx - self._cam.left), p[1] + (n_dy - self._cam.bottom)
            self.dragging = True
        else:
            self.on_mouse_motion(x, y, dx, dy)

    def on_update(self, delta_time: float):
        self.local_time += delta_time

    def draw_bg(self):
        if self.one_hundred_px < 0.1:
            self.bgs["micro"].draw()
        elif self.one_hundred_px < 50:
            self.bgs["indoors"].draw()
        elif self.one_hundred_px < 2500000:
            self.bgs["outdoors"].draw()
        else:
            self.bgs["space"].draw()

    def on_draw(self):
        self.ctx.disable(self.ctx.DEPTH_TEST)
        self.clear(color=(20, 20, 20))

        self.draw_bg()

        self._cam.use()
        self._zoom_buckets.draw()

        if self.selected_sprite:
            alpha = abs(int(math.sin(self.local_time) * 255))
            l, r, b, t = self.selected_sprite.left, self.selected_sprite.right, self.selected_sprite.bottom, self.selected_sprite.top
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE_SMOKE[:3] + (alpha, ), 3 / self._cam.zoom)

        self.default_camera.use()

        if self.selected_box:
            s_x, s_y = self._cam.project((self.selected_sprite.right, self.selected_sprite.top, 0.0))
            _, s_y_b = self._cam.project((self.selected_sprite.right,  self.selected_sprite.bottom, 0.0))
            px_size = s_y - s_y_b

            # Selected box text
            arcade.draw_text(self.selected_name.title() + "\n" + cm_to_str(self.selected_size),
                             s_x+4, s_y,
                             arcade.color.WHITE_SMOKE,
                             anchor_x="left", anchor_y="top",
                             font_name="GohuFont 11 Nerd Font Mono",
                             font_size=max(min(22.0, px_size*0.25), 1.0),
                             multiline=True,
                             width=1000)

        # 100px equiv. text
        arcade.draw_text(f"100px ~= {cm_to_str(self.one_hundred_px)}",
                         5, self.height - 5,
                         arcade.color.WHITE_SMOKE,
                         anchor_x="left", anchor_y="top",
                         font_name="GohuFont 11 Nerd Font Mono",
                         font_size=22)

        # Closest unit text
        arcade.draw_text(f"{round(self.closest_length_px_length)}px ~= {cm_to_str(self.closest_unit_measurement)}",
                         5, self.height - 30,
                         arcade.color.WHITE_SMOKE,
                         anchor_x="left", anchor_y="top",
                         font_name="GohuFont 11 Nerd Font Mono",
                         font_size=22)

        # Draw measurement bar
        arcade.draw_line(5, self.height - 65, 5 + self.closest_length_px_length, self.height - 65, arcade.color.WHITE_SMOKE, 3)
        arcade.draw_line(5, self.height - 60, 5, self.height - 70, arcade.color.WHITE_SMOKE, 3)
        arcade.draw_line(5 + self.closest_length_px_length, self.height - 60, 5 + self.closest_length_px_length, self.height - 70, arcade.color.WHITE_SMOKE, 3)


def main():
    win = HeightViz2DWindow()
    win.run()
