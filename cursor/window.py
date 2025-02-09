from arcade import Window

import arcade
import arcade.future
import pyglet

CURSOR_SPEED = 120
DEAD_ZONE = 0.01

class CursorWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "Cursor")
        controllers = pyglet.input.get_controllers()
        controller = None if not controllers else controllers[0]
        self.manager: arcade.future.input.InputManager = arcade.future.input.InputManager(controller)
        self.manager.new_axis("stick_x")
        self.manager.new_axis("stick_y")
        self.manager.add_axis_input("stick_x", arcade.future.input.ControllerAxes.RIGHT_STICK_X)
        self.manager.add_axis_input("stick_y", arcade.future.input.ControllerAxes.RIGHT_STICK_Y)

        self.cursor_position = (0.0, 0.0)

    def on_draw(self):
        ...

    def on_update(self, delta_time: float):
        self.manager.update()

        dx = self.manager.axis("stick_x")
        dy = self.manager.axis("stick_y")

        if abs(dx) >= DEAD_ZONE or abs(dy) >= DEAD_ZONE:
            print(dx, dy)
            x = self.cursor_position[0] + delta_time * CURSOR_SPEED * dx
            y = self.cursor_position[1] + delta_time * CURSOR_SPEED * dy

            self.set_mouse_position(int(x), int(y))

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor_position = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor_position = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor_position = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor_position = (x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.cursor_position = (x, y)

    def on_mouse_enter(self, x, y):
        self.cursor_position = (x, y)

    def on_mouse_leave(self, x, y):
        self.cursor_position = (x, y)


def main():
    win = CursorWindow()
    win.run()
