from arcade import Text, Window, Rect, draw_line, draw_text
from arcade.draw_commands import draw_rect_outline, draw_point
from arcade.types import Point2
import arcade.color

from pyglet.graphics import Batch
from pyglet.math import Vec2


def closest_point_on_bounds(rect: Rect, point: Point2) -> Vec2:
    px, py = point
    diff = Vec2(px - rect.x, py - rect.y)
    dx = abs(diff.x) - rect.width / 2.0
    dy = abs(diff.y) - rect.height / 2.0
    return Vec2(px + dx, py + dy)


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

    def update_text(self):
        self.width_text.text = f"← {self.rectangle.width:.0f} →"
        self.height_text.text = f"↑\n{self.rectangle.height:.0f}\n↓"
        self.top_text.text = f"{self.rectangle.top:.0f}"
        self.bottom_text.text = f"{self.rectangle.bottom:.0f}"
        self.left_text.text = f"{self.rectangle.left:.0f}"
        self.right_text.text = f"{self.rectangle.right:.0f}"
        self.center_text.text = f"({self.rectangle.center_x:.0f}, {self.rectangle.center_y:.0f})"
        self.area_text.text = f"{self.rectangle.area:.0f}px²"

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
