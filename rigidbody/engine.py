from arcade import Vec2


class World:

    def __init__(self):
        pass


class RigidOrigin:

    def __init__(self):
        self.origin: Vec2 = Vec2(0.0, 0.0)
        self.direction: Vec2 = Vec2(0.0, 0.0)
        self.normal: Vec2 = Vec2(0.0, 0.0)


class RigidBody:

    def __init__(self):
        self.velocity: Vec2 = Vec2(0.0, 0.0)
        self.angular_velocity: float = 0.0
        self.mass: float = 0.0


class SolidRectangle:

    def __init__(self):
        self.width: float = 0.0
        self.height: float = 0.0


class BorderRectangle:

    def __init__(self):
        pass
       # ????


class SolidCircle:

    def __init__(self):
        pass


class BorderCircle:

    def __init__(self):
        pass


if __name__ == '__main__':
    world = World()
