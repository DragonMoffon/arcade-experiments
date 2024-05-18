import math

from arcade import SpriteList, Window, camera, key, Sprite
from arcade.draw_commands import get_image

from common.data_loading import make_package_path_finder
from common.util import clamp

from sphere.render import Renderer
import sphere.data as data


get_img_path = make_package_path_finder(data, "png")


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
        self._orthographic_data = camera.OrthographicProjectionData(
            -7000 * self._projection_data.aspect, 7000 * self._projection_data.aspect,
            -7000, 7000,
            100.0,
            20000.0,
            self.ctx.viewport
        )

        self._camera = camera.PerspectiveProjector(view=self._camera_data, projection=self._projection_data)
        self._camera_2 = camera.OrthographicProjector(view=self._camera_data, projection=self._orthographic_data)
        self._camera_2.projection.near = 0.01
        self._camera_2.projection.far = 200000.0

        self.forward = 0
        self.horizontal = 0
        self.vertical = 0

        self._lat = 0
        self._long = 0
        self._radius = 7500

        self.stars = SpriteList()

        # Northeast stars
        self.stars_ne = Sprite(get_img_path("stars"))
        self.stars_ne.bottom = self.center_y
        self.stars_ne.left = self.center_x
        self.stars.append(self.stars_ne)

        # Northwest stars
        self.stars_nw = Sprite(get_img_path("stars"))
        self.stars_nw.bottom = self.center_y
        self.stars_nw.right = self.center_x
        self.stars.append(self.stars_nw)

        # Southeast stars
        self.stars_se = Sprite(get_img_path("stars"))
        self.stars_se.top = self.center_y
        self.stars_se.left = self.center_x
        self.stars.append(self.stars_se)

        # Southwest stars
        self.stars_sw = Sprite(get_img_path("stars"))
        self.stars_sw.top = self.center_y
        self.stars_sw.right = self.center_x
        self.stars.append(self.stars_sw)

        for s in self.stars:
            s.width = self.width
            s.height = self.height * 2
            s.center_y = self.center_y

        self.look_at_center()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0.0:
            self._camera_data.zoom *= 1.1
        elif scroll_y < 0.0:
            self._camera_data.zoom /= 1.1

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
                if modifiers & key.MOD_CTRL:
                    img = get_image()
                    img.save("Screenshot.png")
                    print("hmmmm")
                else:
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
                if not modifiers & key.MOD_CTRL:
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
        self.stars.draw()
        with self._camera_2.activate():
            self._renderer._texture_program['light'] = self._camera_data.forward
            self._renderer.draw()

    def on_update(self, delta_time: float):
        if self.vertical:
            self._radius = clamp(7000, self._radius + self.vertical * 1000.0 * delta_time, 10000)

        if self.horizontal:
            self._long = (self._long + (1 + self.horizontal * delta_time) * math.pi) % (2 * math.pi) - math.pi
            percent = (self._long + math.pi) / math.tau
            cent = percent * self.width
            self.stars_ne.left = cent
            self.stars_nw.right = cent
            self.stars_se.left = cent
            self.stars_sw.right = cent

        if self.forward:
            self._lat = clamp(-math.pi / 2.0, self._lat + self.forward * math.pi * delta_time, math.pi / 2.0)
            percent = (self._lat + (math.pi / 2)) / math.pi
            cent = percent * self.height
            self.stars_ne.bottom = cent
            self.stars_nw.bottom = cent
            self.stars_se.top = cent
            self.stars_sw.top = cent

        if self.forward or self.horizontal or self.vertical:
            self.look_at_center()


def main():
    app = App()
    app.run()
