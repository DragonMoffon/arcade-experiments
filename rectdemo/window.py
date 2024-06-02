from arcade import Text, Window, Rect, draw_line
from arcade.draw_commands import draw_rect_outline, draw_point
from arcade.types import Point2
import arcade.color

from pyglet.graphics import Batch
from pyglet.math import Vec2


def closest_point_on_bounds(rect: Rect, point: Point2) -> Vec2:
    d = rect.distance_from_bounds(point)

    if d > 0:
        return point

    px, py = point

    d_bottom = rect.bottom - py
    d_top = rect.top - py

    d_left = rect.left - px
    d_right = rect.right - px

    dx = d_left if abs(d_left) < abs(d_right) else d_right
    dy = d_bottom if abs(d_bottom) < abs(d_top) else d_top

    if abs(dx) < abs(dy):
        return Vec2(px + dx, py)
    return Vec2(px, py + dy)


class RectWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "Rect Demo")

        self.rectangle = self.rect.scale(0.75)

        self.text_batch = Batch()

        self.width_text = Text(f"← {self.rectangle.width:.0f} →", self.rectangle.center_x, self.rectangle.top - 5,
                               font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                               anchor_x = "center", anchor_y = "top", batch = self.text_batch)

        self.height_text = Text(f"↑\n{self.rectangle.height:.0f}\n↓", self.rectangle.right - 5, self.rectangle.center_y,
                                font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                                anchor_x = "right", anchor_y = "center", batch = self.text_batch,
                                multiline = True, width = 100, align = "right")

        self.top_text = Text(f"{self.rectangle.top:.0f}", self.rectangle.center_x, self.rectangle.top + 5,
                             font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                             anchor_x = "center", anchor_y = "bottom", batch = self.text_batch,
                             color = arcade.color.BABY_BLUE)

        self.bottom_text = Text(f"{self.rectangle.bottom:.0f}", self.rectangle.center_x, self.rectangle.bottom - 5,
                                font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                                anchor_x = "center", anchor_y = "top", batch = self.text_batch,
                                color = arcade.color.BABY_BLUE)

        self.left_text = Text(f"{self.rectangle.left:.0f}", self.rectangle.left - 5, self.rectangle.center_y,
                              font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                              anchor_x = "right", anchor_y = "center", batch = self.text_batch,
                              color = arcade.color.BABY_BLUE)

        self.right_text = Text(f"{self.rectangle.right:.0f}", self.rectangle.right + 5, self.rectangle.center_y,
                               font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                               anchor_x = "left", anchor_y = "center", batch = self.text_batch,
                               color = arcade.color.BABY_BLUE)

        self.center_text = Text(f"({self.rectangle.center_x:.0f}, {self.rectangle.center_y:.0f})", self.rectangle.center_x, self.rectangle.center_y - 5,
                                font_name="GohuFont 11 Nerd Font Mono", font_size = 24,
                                anchor_x = "center", anchor_y = "top", batch = self.text_batch,
                                color = arcade.color.RED)

        self.area_text = Text(f"{self.rectangle.area:,.0f}px²", self.rectangle.right - 3, self.rectangle.bottom + 3,
                              font_name="GohuFont 11 Nerd Font Mono", font_size = 12,
                              anchor_x = "right", anchor_y = "bottom", batch = self.text_batch,
                              color = arcade.color.YELLOW)

        self.mouse_text = Text("(???, ???)", 0, 0,
                               font_name="GohuFont 11 Nerd Font Mono", font_size = 12,
                               anchor_x = "center", anchor_y = "center", batch = self.text_batch,
                               color = arcade.color.GREEN)

        self.mouse_pos = Vec2(0, 0)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = Vec2(x, y)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        self.on_mouse_motion(x, y, dx, dy)
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            d_x, d_y = self.rectangle.x - x, self.rectangle.y - y
            s_x, s_y = d_x / abs(d_x), d_y / abs(d_y)

            anchor = Vec2(s_x * 0.5 + 0.5, s_y * 0.5 + 0.5)
            n_width = self.rectangle.width + dx * -s_x
            n_height = self.rectangle.height + dy * -s_y
            self.rectangle = self.rectangle.resize(n_width, n_height, anchor)

    def update_text(self):
        self.width_text.text = f"← {self.rectangle.width:.0f} →"
        self.width_text.position = (self.rectangle.center_x, self.rectangle.top - 5)
        self.height_text.text = f"↑\n{self.rectangle.height:.0f}\n↓"
        self.height_text.position = (self.rectangle.right - 5, self.rectangle.center_y)
        self.top_text.text = f"{self.rectangle.top:.0f}"
        self.top_text.position = (self.rectangle.center_x, self.rectangle.top + 5)
        self.bottom_text.text = f"{self.rectangle.bottom:.0f}"
        self.bottom_text.position = (self.rectangle.center_x, self.rectangle.bottom - 5)
        self.left_text.text = f"{self.rectangle.left:.0f}"
        self.left_text.position = (self.rectangle.left - 5, self.rectangle.center_y)
        self.right_text.text = f"{self.rectangle.right:.0f}"
        self.right_text.position = (self.rectangle.right + 5, self.rectangle.center_y)
        self.center_text.text = f"({self.rectangle.center_x:.0f}, {self.rectangle.center_y:.0f})"
        self.center_text.position = (self.rectangle.center_x, self.rectangle.center_y - 5)
        self.area_text.text = f"{self.rectangle.area:.0f}px²"
        self.area_text.position = (self.rectangle.right - 3, self.rectangle.bottom + 3)

    def on_draw(self):
        self.clear()

        draw_rect_outline(self.rectangle, arcade.color.WHITE, 3)
        draw_point(self.rectangle.center_x, self.rectangle.center_y, arcade.color.RED, 3)

        line_end = closest_point_on_bounds(self.rectangle, self.mouse_pos)
        mid_point = self.mouse_pos.lerp(line_end, 0.5)
        draw_line(self.mouse_pos.x, self.mouse_pos.y, line_end.x, line_end.y, arcade.color.GREEN)
        self.mouse_text.text = f"{self.rectangle.distance_from_bounds(self.mouse_pos):.1f}"
        self.mouse_text.position = mid_point

        self.text_batch.draw()

    def on_update(self, delta_time: float):
        self.update_text()


def main():
    win = RectWindow()
    win.run()
