from arcade import Sprite, Texture, Window
import arcade

from common.data_loading import make_package_path_finder
import common.data.images as images
from animator.lerp import find_percent

from PIL.Image import Image, new, composite, open

img_path = make_package_path_finder(images, "png")
def get_PIL_image(name: str) -> Image:
    return open(img_path(name))


class Progessor(Sprite):
    def __init__(self, image: Image, mask: Image) -> None:
        tex = Texture.create_empty("_progress", image.size)
        self.image = image.convert("RGBA")
        self.stupid = new("RGBA", image.size)
        self.mask = mask.convert("L")

        self.progress = 0

        super().__init__(tex)

    def update(self, progress: float):
        if self.progress == progress:
            return
        threshold = progress * 255
        mask = self.mask.point(lambda p: 255 if p <= threshold else 0, "1")
        new_tex = composite(self.image, self.stupid, mask)
        self.texture = Texture(new_tex)
        self.progress = progress


class ProgressWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "Custom Progress Loader")

        self.progressor = Progessor(get_PIL_image("normal"), get_PIL_image("mask"))
        self.progressor.position = self.center

        self.end = 5

        self.last_start = 0

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.progressor)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.R:
            self.last_start = self.time

    def on_update(self, delta_time: float):
        self.progressor.update(find_percent(0, self.end, self.time - self.last_start))


def main():
    win = ProgressWindow()
    win.run()
