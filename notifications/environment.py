from arcade import SpriteSolidColor, Rect


class EnivroArea(SpriteSolidColor):

    def __init__(self, area: Rect, material: str):
        super().__init__(area.width, area.height, center_x=area.x, center_y=area.y)
        self.material: str = material
