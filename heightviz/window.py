import math

from arcade import Text, Window, camera, key
from pyglet.math import Vec2, Vec3

from common.util import clamp

from heightviz.render import Renderer
from heightviz.person import PersonRenderer


CAM_SPEED = 1000.0
CAM_SENS = 0.1


class App(Window):

    def __init__(self):
        super().__init__(1280, 720, "3D Sphere")

        self._renderer = Renderer()
        self._person = PersonRenderer()
        self._camera_data = camera.CameraData(
            position=(0.0, 0.0, 0.0)
        )
        self._projection_data = camera.PerspectiveProjectionData(
            self.width / self.height,
            90,
            0.01,
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

        self._gui_cam = camera.Camera2D()

        self.forward = 0
        self.horizontal = 0
        self.vertical = 0

        self.yaw = 180.0
        self.pitch = 0.0

        self._lat = 0
        self._long = 0
        self._radius = 7500

        self.person_scale = 48
        self.text = Text(f"{self.person_scale}km",
                         5, self.height - 5,
                         font_name="GohuFont 11 Nerd Font Mono", font_size=36,
                         anchor_x = "left", anchor_y = "top")

        self._is_in_center_view_mode = True
        self.look_at_center()

    def look_at_center(self):
        y = math.sin(self._lat)
        x = math.cos(-self._long) * math.cos(self._lat)
        z = math.sin(-self._long) * math.cos(self._lat)
        forward = (-x, -y, -z)
        pos = (x * self._radius, y * self._radius, z * self._radius)

        self._camera_data.position = pos
        self._camera_data.forward = forward
        fw = Vec3(forward[0], forward[1], forward[2])
        up = Vec3(0.0, 1.0, 0.0)
        ri = fw.cross(up)
        up = ri.cross(fw)
        self._camera_data.up = up.x, up.y, up.z

        self._person.set_world_coord(self._lat, self._long)

    def scale_person(self):
        self._person._scale = Vec3(self.person_scale / 1.7, self.person_scale / 1.7, self.person_scale / 1.7)
        self._person.update_model_matrix()
        self.text.text = f"{self.person_scale}km"

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case key.ESCAPE:
                self.close()
            case key.GRAVE:
                self._is_in_center_view_mode = not self._is_in_center_view_mode
                if self._is_in_center_view_mode:
                    self.look_at_center()
                    self.set_exclusive_mouse(False)
                else:
                    self.set_exclusive_mouse(True)
                    self.yaw = self._long + 180
                    self.pitch = -self._lat
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
            case key.NUM_ADD:
                if modifiers & key.MOD_SHIFT:
                    self.person_scale += 10
                else:
                    self.person_scale += 1
                self.scale_person()
            case key.NUM_SUBTRACT:
                if modifiers & key.MOD_SHIFT:
                    self.person_scale -= 10
                else:
                    self.person_scale -= 1
                self.person_scale = max(1, self.person_scale)
                self.scale_person()

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

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0.0:
            self._camera_data.zoom *= 1.1
        elif scroll_y < 0.0:
            self._camera_data.zoom /= 1.1

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self._is_in_center_view_mode:
            return

        self.yaw += dx * CAM_SENS
        self.pitch = clamp(-89.0, self.pitch + dy * CAM_SENS, 89.0)

        y, p = math.radians(self.yaw), math.radians(self.pitch)
        fw = Vec3(
            math.cos(y) * math.cos(p),
            math.sin(p),
            math.sin(y) * math.cos(p)
        )
        self._camera_data.forward = fw.normalize()
        self._camera_data.up = (0.0, 1.0, 0.0)
        camera.data_types.constrain_camera_data(self._camera_data, forward_priority=True)

    def on_draw(self):
        self.clear()

        cam = self._camera_2 if self._is_in_center_view_mode else self._camera

        with cam.activate():
            self._renderer._texture_program['light'] = self._camera_data.forward
            self._renderer.draw()
            self._person.draw()

        with self._gui_cam.activate():
            self.ctx.disable(self.ctx.DEPTH_TEST)
            self.text.draw()

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
                old_pos = self._camera_data.position
                fw = self._camera_data.forward
                vel = CAM_SPEED * delta_time * self.forward

                self._camera_data.position = old_pos[0] + fw[0] * vel, old_pos[1] + fw[1] * vel, old_pos[2] + fw[2] * vel,

            if self.horizontal or self.vertical:
                direction = Vec2(self.horizontal, self.vertical).normalize()
                self._camera_data.position = camera.grips.strafe(self._camera_data, direction * CAM_SPEED * delta_time)


def main():
    app = App()
    app.run()
