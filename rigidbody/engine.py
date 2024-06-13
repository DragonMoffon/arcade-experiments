from typing import Callable

from arcade import Vec2


class RigidBody:

    def __init__(self, origin: Vec2, direction: Vec2, mass: float, rotational_inertia: float):
        self.origin: Vec2 = origin
        self.direction: Vec2 = direction
        self.mass: float = mass
        self.rotational_inertia: float = rotational_inertia

        self.linear_velocity: Vec2 = Vec2(0.0, 0.0)
        self.rotation_velocity: float = 0.0


class RigidRect(RigidBody):

    def __init__(self, origin: Vec2, direction: Vec2, size: Vec2, mass: float):
        super().__init__(origin, direction, mass, (1.0/12.0) * mass * size.dot(size))
        self.size: Vec2 = size


class RigidCircle(RigidBody):

    def __init__(self, origin: Vec2, direction: Vec2, radius: float, mass: float):
        super().__init__(origin, direction, mass, (1.0 / 2.0) * mass * radius**2)
        self.radius: float = radius


def rect_collision(a: RigidRect, b: RigidRect):
    pass


def sphere_collision(a: RigidCircle, b: RigidCircle):
    pass


COLLISION_MAP: dict[tuple[type, type], Callable] = {
    (RigidRect, RigidRect): rect_collision,
    (RigidCircle, RigidCircle): sphere_collision
}
def rigid_collision(a: RigidBody, b: RigidBody):
    a_type, b_type = type(a), type(b)
    return COLLISION_MAP[a_type, b_type](a, b)


class RigidEngine:

    def __init__(self):
        pass

    def fixed_update(self, dt: float):
        pass