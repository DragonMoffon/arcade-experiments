from __future__ import annotations

from math import pi
import arcade
from pyglet.math import Vec2, Vec3, Mat3

DEG_TO_RADS = pi / 180.0

class Portal:

    def __init__(self, position: Vec2, direction: Vec2, width: float):
        self.position = position
        self._direction = direction
        self._normal = Vec2(-direction.y, direction.x)
        self.width = width
        self.sibling: Portal = None

    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, direction: Vec2):
        self._direction = direction
        self._normal = Vec2(-direction.y, direction.x)

    @property
    def normal(self):
        return self._normal
    
    @normal.setter
    def normal(self, normal: Vec2):
        self._normal = normal
        self._direction = Vec2(normal.y, -normal.x)

    def link(self, other: Portal):
        self.sibling, other.sibling = other, self
     
    def unlink(self):
        self.sibling = self.sibling.sibling = None

    def draw(self):
        arcade.draw_line(
            self.position.x - self.normal.x * self.width,
            self.position.y - self.normal.y * self.width,
            self.position.x + self.normal.x * self.width,
            self.position.y + self.normal.y * self.width,
            (255, 255, 255),
            4
        )

        arcade.draw_line(self.position.x, self.position.y, self.position.x + self.normal.x * 10, self.position.y + self.normal.y * 10, (0, 255, 0), 2)
        arcade.draw_line(self.position.x, self.position.y, self.position.x + self.direction.x * 10, self.position.y + self.direction.y * 10, (255, 0, 0), 2)

    def map_to(self, vector: Vec3):
        pass

    def map_accross(self, vector: Vec3):
        pass

    def map_out(self, vector: Vec3):
        pass


class PortalWindow(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "portal")
        self.portal_a = Portal(Vec2(100, 100), Vec2.from_heading(DEG_TO_RADS * 60.0), 50)
        self.portal_b = Portal(Vec2(400, 600), Vec2.from_heading(DEG_TO_RADS * 230.0), 50)
        self.portal_a.link(self.portal_b)

        self.dragged = None

    def on_draw(self):
        self.clear()
        self.portal_a.draw()
        self.portal_b.draw()

    def on_update(self, delta_time: float):
        ...

    def on_mouse_press(self, x, y, button, modifiers):
        d1 = (Vec2(x, y) - self.portal_a.position).length_squared()
        d2 = (Vec2(x, y) - self.portal_b.position).length_squared()

        if 200 > d1 and 200 > d2:
            return

        if d1 < d2:
            self.dragged = self.portal_a
        else:
            self.dragged = self.portal_b

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.dragged:
            return
        
        self.dragged.position = Vec2(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.dragged:
            return
        
        self.dragged.direction = self.dragged.direction.rotate(scroll_y * 10 * DEG_TO_RADS)


def main():
    win = PortalWindow()
    win.run()
