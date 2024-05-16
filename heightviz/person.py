import math

from pyglet import model, shapes
from pyglet.math import Vec3, Mat4

from common.util import load_shared_model


class PersonRenderer:

    def __init__(self):
        self.person_batch = shapes.Batch()
        self.player_model: model.Model = load_shared_model("person")
        self.player_model.batch = self.person_batch

        self._position: Vec3 = Vec3(0.0, 6371.0, 0.0)
        self._rotation: Vec3 = Vec3(0.0, 1.0, 0.0)
        self._angle: float = 0.0
        self._scale: Vec3 = Vec3(48.0, 48.0, 48.0)

        self._dirty = True

    def set_world_coord(self, lat, long, R: float = 6371):
        x = math.cos(-long) * math.cos(lat)
        y = math.sin(lat)
        z = math.sin(-long) * math.cos(lat)

        self._rotation = Vec3(-math.sin(long), 0.0, math.cos(long))
        self._position = Vec3(x * R, y * R, z * R)
        self._dirty = True

    def update_model_matrix(self):
        self._dirty = False

        rotation_mat = Mat4.from_rotation(self._angle, self._rotation)
        translation_mat = Mat4.from_translation(self._position)
        scale_mat = Mat4.from_scale(self._scale)

        self.player_model.matrix = translation_mat @ rotation_mat @ scale_mat

    def draw(self):
        if self._dirty:
            self.update_model_matrix()

        self.person_batch.draw()
