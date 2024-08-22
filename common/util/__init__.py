# flake8: noqa

import arcade
import pyglet

from arcade.types import Point2, Color

from PIL.Image import Image

from common.data_loading import make_package_path_finder
import common.data.fonts as fonts
import common.data.models as models
import common.data.sounds as sounds
import common.data.images as images
from common.util.procedural_animator import ProceduralAnimator, SecondOrderAnimatorBase

__all__ = (
    "get_shared_font_path",
    "get_shared_sound_path",
    "get_shared_model_path",
    "clamp",
    "load_shared_font",
    "load_shared_sound",
    "load_shared_model",
    "ProceduralAnimator",
    "SecondOrderAnimatorBase"
)

get_shared_font_path = make_package_path_finder(fonts, "ttf")
get_shared_sound_path = make_package_path_finder(sounds, "wav")
get_shared_model_path = make_package_path_finder(models, "obj")
get_shared_image_path = make_package_path_finder(images, "png")
def load_shared_font(name: str): arcade.load_font(get_shared_font_path(name))
def load_shared_sound(name: str): return arcade.load_sound(get_shared_sound_path(name))
def load_shared_model(name: str) -> pyglet.model.Model: return pyglet.model.load(get_shared_model_path(name))
def load_shared_image(name: str) -> Image: return Image.open(get_shared_image_path(name))
def load_shared_texture(name: str) -> arcade.Texture: return arcade.load_texture(get_shared_image_path(name))


def clamp(minVal, val, maxVal):
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(minVal, min(maxVal, val))


def draw_cross(origin: Point2, size: float, color: Color = arcade.color.WHITE, thickness = 1.0):
    x, y = origin
    arcade.draw_line(
        x - size, y - size,
        x + size, y + size,
        color,
        thickness
        )
    arcade.draw_line(
        x + size, y - size,
        x - size, y + size,
        color,
        thickness
    )
