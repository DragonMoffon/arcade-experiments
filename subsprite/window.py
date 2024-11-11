from __future__ import annotations
from math import cos, sin, acos, asin, atan2, pi

import arcade

from common.data_loading import make_package_path_finder
import subsprite.data as data

get_img = make_package_path_finder(data, 'png')

SPEED = 180.0
ACCELERATION = 18.0
DRAG = 0.0001
ROTATION = 8.0

TO_RADIANS = pi / 180.0
TO_DEGREES = 180.0 / pi

class vec2:
    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0.0, y: float | None = None) -> None:
        self.x: float = x
        self.y: float = x if y is None else y

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<{self.x} {self.y}>"

    def cross_scalar(self, scalar: float) -> vec2:
        return vec2(self.y * scalar, -self.x * scalar)

    def cross_vector(self, vec: vec2) -> float:
        return self.x * vec.y - self.y * vec.x

    def dot(self, vec: vec2) -> float:
        return self.x * vec.x + self.y * vec.y

    def add_scalar(self, scalar: float) -> vec2:
        return vec2(
            self.x + scalar,
            self.y + scalar
        )

    def add_vec(self, vec: vec2) -> vec2:
        return vec2(
            self.x + vec.x,
            self.y + vec.y
        )

    def sub_vec(self, vec: vec2) -> vec2:
        return vec2(
            self.x - vec.x,
            self.y - vec.y
        )

class rot2: 
    __slots__ = ('c', 's')

    def __init__(self, cos: float = 1.0, sin: float = 0.0) -> None:
        self.c: float = cos
        self.s: float = sin

    @classmethod
    def from_angle(cls, angle: float):
        r = angle * TO_RADIANS
        return cls(cos(r), sin(r))

    @classmethod
    def from_radians(cls, radians: float):
        return cls(cos(radians), sin(radians))

    def apply(self, vec: vec2) -> vec2:
        return vec2(
            vec.x * self.c + vec.y * self.s,
            -vec.x * self.s + vec.y * self.c
        )

    def reverse(self, vec: vec2) -> vec2:
        return vec2(
            vec.x * self.c - vec.y * self.s,
            vec.x * self.s + vec.y * self.c
        )

    @property
    def x(self) -> vec2:
        return vec2(self.c, self.s)

    @property
    def y(self) -> vec2:
        return vec2(-self.s, self.c)

class transform2:
    __slots__ = ('p', 'r')

    def __init__(self, position: vec2, rotation: rot2) -> None:
        self.p: vec2 = position
        self.r: rot2 = rotation

    def apply(self, vec: vec2):
        return self.r.reverse(vec).add_vec(self.p)

    def reverse(self, vec: vec2):
        return self.r.apply(vec.sub_vec(self.p))

class SuperSprite(arcade.Sprite):

    def __init__(self, size: tuple[int, int], atlas: arcade.texture_atlas.DefaultTextureAtlas = None, name: str = None) -> None:
        name = name or str(hash(id(self)))
        self.atlas = atlas is atlas is not None or arcade.get_window().ctx.default_atlas
        texture = arcade.Texture.create_empty(name, size)
        super().__init__(texture)
        self._proj = -0.5 * size[0], 0.5 * size[0], -0.5 * size[1], 0.5 * size[1]
        self.sub_renderer = arcade.SpriteList(atlas=self.atlas)
        self.transform = transform2(vec2(), rot2())

    def render(self):
        with self.atlas.render_into(self.texture, projection=self._proj) as fbo:
            fbo.clear()
            self.sub_renderer.draw(pixelated=True)

    def add_subsprite(self, sprite: arcade.Sprite):
        self.sub_renderer.append(sprite)

    def remove_subsprite(self, sprite: arcade.Sprite):
        self.sub_renderer.remove(sprite)

    @property
    def position(self) -> Point2:
        """Get or set the center x and y position of the sprite."""
        return self._position

    @position.setter
    def position(self, new_value: Point2):
        if new_value == self._position:
            return

        self._position = new_value
        self.transform.p = vec2(new_value[0], new_value[1])
        self._hit_box.position = new_value
        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position(self)

    @property
    def angle(self) -> float:
        """
        Get or set the rotation or the sprite.

        The value is in degrees and is clockwise.
        """
        return self._angle

    @angle.setter
    def angle(self, new_value: float) -> None:
        if new_value == self._angle:
            return

        self._angle = new_value
        self.transform.r = rot2.from_angle(-new_value)
        self._hit_box.angle = new_value

        for sprite_list in self.sprite_lists:
            sprite_list._update_angle(self)

        self.update_spatial_hash()


class Ship(SuperSprite):

    def __init__(self, atlas: arcade.DefaultTextureAtlas = None) -> None:
        self.body = arcade.Sprite(get_img('ship_large_body'))
        super().__init__(self.body.texture.size, atlas, f"ship_{str(hash(id(self)))}")
        self.main_gun = arcade.Sprite(get_img('ship_big_gun_dual'), center_x=16)
        self.ripple = arcade.Sprite(get_img('water_ripple_big'))
        self.ripple.alpha = 0

        self.target: vec2 = vec2()

        self.velocity: float = 0.0
        self.move: int = 0
        self.turn: int = 0

        self.add_subsprite(self.ripple)
        self.add_subsprite(self.body)
        self.add_subsprite(self.main_gun)

    def update(self, delta_time):
        self.velocity += self.move * delta_time * ACCELERATION
        self.velocity -= self.velocity**2 * DRAG * delta_time
        self.velocity = min(SPEED, max(-SPEED, self.velocity))
        rot = (self.velocity / SPEED) * ROTATION * self.turn * delta_time
        self.angle += rot

        self.ripple.alpha = int(255.0 * (self.velocity**2 / SPEED**2))

        pos = self.position
        x = self.transform.r.x
        self.position = pos[0] + delta_time * self.velocity * x.x, pos[1] + delta_time * self.velocity * x.y

        t = self.transform.reverse(self.target)
        self.main_gun.radians = -atan2(t.y - self.main_gun.center_y, t.x - self.main_gun.center_x)

class TestView(arcade.View):

    def __init__(self) -> None:
        super().__init__()
        self.camera = arcade.Camera2D(position=(0.0, 0.0))
        self.ship = Ship()
        self.ships = arcade.SpriteList()
        self.ships.append(self.ship)

        self.mouse_p = 0.0, 0.0

        self.forward = False
        self.backward = False
        self.leftward = False
        self.rightward = False

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.W:
            self.forward = True
        elif symbol == arcade.key.S:
            self.backward = True
        elif symbol == arcade.key.D:
            self.rightward = True
        elif symbol == arcade.key.A:
            self.leftward = True

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.W:
            self.forward = False
        elif symbol == arcade.key.S:
            self.backward = False
        elif symbol == arcade.key.D:
            self.rightward = False
        elif symbol == arcade.key.A:
            self.leftward = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self.mouse_p = x, y

    def on_update(self, delta_time: float) -> bool | None:
        w = self.window.width
        zx = w / (2.0 * abs(self.ship.position[0]) + 400)
        h = self.window.height
        zh = h / (2.0 * abs(self.ship.position[1]) + 400)

        z = max(0.0001, min(1.0, min(zx, zh)))
        self.camera.zoom = z

        x, y, _ = self.camera.unproject(self.mouse_p)

        self.ship.target = vec2(x, y)
        self.ship.move = self.forward - self.backward
        self.ship.turn = self.rightward - self.leftward

        self.ship.update(delta_time)
    
    def on_draw(self) -> bool | None:
        self.clear(arcade.color.SEA_BLUE)
        self.ship.render()
        with self.camera.activate():
            self.ships.draw()


def main():
    win = arcade.Window()
    view = TestView()

    win.show_view(view)
    win.run()
