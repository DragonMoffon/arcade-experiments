from arcade import Vec2


class World:

    def __init__(self):
        self._tables_definitions: dict[str, tuple[type, ...]] = {}  # Map the table name to the types of its "columns"
        self._tables: dict[str, dict[int, tuple[int, ...]]] = {}  # Map the table name to the physical table
        self._components: dict[type, list] = {}  # Contiguous arrays of components
        self._constructs: tuple[int, ...] = ()  # Contiguous array of all the construct UUIDs

    def define_table(self, definition: frozenset[type], title: str):
        pass

    def get_table_content(self, table: str):
        table_content = self._tables_definitions[table]
        table = self._tables[table]

        for row in table.values():
            yield (self._components[t][idx] for t, idx in zip(table_content, row))

    def add_component(self, construct: int, component: type, *args, **kwargs):
        pass

    def remove_component(self, construct: int, component: type):
        pass

    def check_tables(self, construct: int):
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
