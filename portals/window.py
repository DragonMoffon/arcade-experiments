from __future__ import annotations

from math import pi
import arcade
from pyglet.math import Vec2, Vec3, Mat3

DEG_TO_RADS = pi / 180.0

class Portal:

    def __init__(self, position: Vec2, direction: Vec2, width: float, thickness: float):
        self._direction: Vec2 = direction
        self._normal: Vec2 = None
        self._position: Vec2 = position
        self._offset: Vec2 = None
        self.width = width
        self.thickness = thickness
        self.sibling: Portal = None

        self.direction = direction
        self.position = position
    
    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, direction: Vec2):
        self._direction = direction
        self._normal = Vec2(direction.y, -direction.x)

        
        self._offset = Vec2(self._position.dot(self._normal), self._position.dot(direction))

    @property
    def normal(self):
        return self._normal
    
    @normal.setter
    def normal(self, normal: Vec2):
        self._normal = normal
        self._direction = Vec2(-normal.y, normal.x)

        self._offset = Vec2(self._position.dot(normal), self._position.dot(self._direction))

    @property
    def position(self):
        return self._position   

    @position.setter
    def position(self, position: Vec2):
        self._position = position
        self._offset = Vec2(position.dot(self.normal), position.dot(self.direction))

    @property
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self, offset: Vec2):
        self._offset = offset
        self.position = self._normal * offset.x + self._direction * offset.y

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
            self.thickness * 2
        )

        arcade.draw_line(self.position.x, self.position.y, self.position.x + self.normal.x * 10, self.position.y + self.normal.y * 10, (0, 255, 0), 2)
        arcade.draw_line(self.position.x, self.position.y, self.position.x + self.direction.x * 10, self.position.y + self.direction.y * 10, (255, 0, 0), 2)

    def check_overlap(self, vector: Vec2):
        offset = vector - self._position
        x = self._normal.dot(offset)
        y = self._direction.dot(offset)

        return abs(x) <= self.width and abs(y) <= self.thickness

    def map_to(self, vector: Vec3):
        mat = Mat3(
            self._normal.x, self._direction.x, 0.0,
            self._normal.y, self._direction.y, 0.0,
            -self._offset.x, -self._offset.y, 1.0
        )
        return mat @ vector

    def map_across(self, vector: Vec3):
        map_to = Mat3(
            self._normal.x, self._direction.x, 0.0,
            self._normal.y, self._direction.y, 0.0,
            -self._offset.x, -self._offset.y, 1.0
        )
        sibl = self.sibling
        map_out = Mat3(
            -sibl._normal.x, -sibl._normal.y, 0.0,
            -sibl._direction.x, -sibl._direction.y, 0.0,
            sibl.position.x, sibl.position.y, 1.0
        )
        return map_out @ map_to @ vector

    def map_out(self, vector: Vec3):
        mat = Mat3(
            -self._normal.x, -self._normal.y, 0.0,
            -self._direction.x, -self._direction.y, 0.0,
            self.position.x, self.position.y, 1.0
        )
        return mat @ vector


class PortalWindow(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "portal")
        self.portal_a = Portal(Vec2(100, 100), Vec2.from_heading(DEG_TO_RADS * 60.0), 50.0, 2.0)
        self.portal_b = Portal(Vec2(400, 600), Vec2.from_heading(DEG_TO_RADS * 230.0), 50.0, 2.0)
        self.portal_a.link(self.portal_b)

        self.dragged = None

        self.cooldown = -float('inf')

        self.m_pos : Vec2 = Vec2(0.0, 0.0)

        self.drag_mode = False
        self.move_mouse = False

    def on_draw(self):
        self.clear()
        self.portal_a.draw()
        self.portal_b.draw()

    def on_update(self, delta_time: float):
        # When dragging don't tp
        if self.drag_mode or self.dragged:
            return
        
        # TP cooldown isn't done yet
        if self.time - self.cooldown < 1.0:
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_NO))
            return
        self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_DEFAULT))
        
        # Check to tp portal a
        if self.portal_a.check_overlap(self.m_pos):
            self.move_mouse = True
            new = self.portal_a.map_across(Vec3(*self.m_pos, 1.0))
            self.set_mouse_position(int(new.x), int(new.y))
            self.cooldown = self.time
            return


        # Check to tp portal b
        if self.portal_b.check_overlap(self.m_pos):
            self.move_mouse = True
            new = self.portal_b.map_across(Vec3(*self.m_pos, 1.0))
            self.set_mouse_position(int(new.x), int(new.y))
            self.cooldown = self.time
            return

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.drag_mode:
            return
        
        d1 = (Vec2(x, y) - self.portal_a.position).length_squared()
        d2 = (Vec2(x, y) - self.portal_b.position).length_squared()

        if 200 > d1 and 200 > d2:
            return

        if d1 <= d2:
            self.dragged = self.portal_a
        else:
            self.dragged = self.portal_b

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        self.m_pos = Vec2(x, y)
        if self.move_mouse:
            self.move_mouse = False
            return

        if not self.dragged:
            return
        
        self.dragged.position = Vec2(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.dragged:
            return
        
        self.dragged.direction = self.dragged.direction.rotate(scroll_y * 10 * DEG_TO_RADS)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.LSHIFT or symbol == arcade.key.RSHIFT:
            self.drag_mode = True
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_HAND))

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LSHIFT or symbol == arcade.key.RSHIFT:
            self.drag_mode = False
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_DEFAULT))


def main():
    win = PortalWindow()
    win.run()
