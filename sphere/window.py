import math

from arcade import Window, camera, key
from pyglet.math import Vec2

from common.util import clamp

from sphere.render import Renderer


class App(Window):

    def __init__(self):
        super().__init__(1280, 720, "3D Sphere")

        self._renderer = Renderer()
        self._camera_data = camera.CameraData(
            position=(0.0, 0.0, 0.0)
        )
        self._projection_data = camera.PerspectiveProjectionData(
            self.width / self.height,
            90,
            100.0,
            20000.0,
            self.ctx.viewport
        )

        self._camera = camera.PerspectiveProjector(view=self._camera_data, projection=self._projection_data)
        self._camera_2 = camera.OrthographicProjector(view=self._camera_data)
        self._camera_2.projection.near = 0.01
        self._camera_2.projection.far = 200000.0

        self.forward = 0
        self.horizontal = 0
        self.vertical = 0

        self._lat = 0
        self._long = 0
        self._radius = 7500

        self.look_at_center()

        self._is_in_center_view_mode = True

    def look_at_center(self):
        y = math.sin(self._lat)
        x = math.cos(-self._long) * math.cos(self._lat)
        z = math.sin(-self._long) * math.cos(self._lat)
        forward = (-x, -y, -z)
        pos = (x * self._radius, y * self._radius, z * self._radius)

        self._camera_data.position = pos
        self._camera_data.forward = forward

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case key.W:
                self.forward += 1
            case key.S:
                self.forward -= 1
            case key.D:
                self.horizontal += 1
            case key.A:
                self.horizontal -= 1
            case key.SPACE:
                self.vertical += 1
            case key.LSHIFT:
                self.vertical -= 1

    def on_key_release(self, symbol: int, modifiers: int):
        match symbol:
            case key.W:
                self.forward -= 1
            case key.S:
                self.forward += 1
            case key.D:
                self.horizontal -= 1
            case key.A:
                self.horizontal += 1
            case key.SPACE:
                self.vertical -= 1
            case key.LSHIFT:
                self.vertical += 1

    def on_draw(self):
        self.clear()
        with self._camera.activate():
            self._renderer.star_draw()

        with self._camera_2.activate():
            self._renderer._texture_program['light'] = self._camera_data.forward
            self._renderer.draw()

    def on_update(self, delta_time: float):
        if self._is_in_center_view_mode:
            if self.vertical:
                self._radius = clamp(7000, self._radius + self.vertical * 1000.0 * delta_time, 10000)

            if self.horizontal:
                self._long = (self._long + (1 + self.horizontal * delta_time) * math.pi) % (2 * math.pi) - math.pi

            if self.forward:
                self._lat = clamp(-math.pi / 2.0, self._lat + self.forward * math.pi * delta_time, math.pi / 2.0)

            if self.forward or self.horizontal or self.vertical:
                self.look_at_center()

        else:
            if self.forward:
                velocity = self.forward * 100.0 * delta_time
                old_pos = self._camera_data.position
                fwd = self._camera_data.forward

                new_pos = old_pos[0] + fwd[0] * velocity, old_pos[1] + fwd[1] * velocity, old_pos[2] + fwd[2] * velocity
                self._camera_data.position = new_pos

            if self.horizontal or self.vertical:
                direction = Vec2(self.horizontal, self.vertical).normalize()
                new_pos = camera.grips.strafe(self._camera_data, direction)
                self._camera_data.position = new_pos


def main():
    app = App()
    app.run()
