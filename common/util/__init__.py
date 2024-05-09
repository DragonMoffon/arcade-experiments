# flake8: noqa

import arcade

from common.data_loading import make_package_path_finder
import common.data.fonts as fonts
import common.data.sounds as sounds
from common.util.procedural_animator import ProceduralAnimator, SecondOrderAnimatorBase

__all__ = (
    "get_shared_font_path",
    "get_shared_sound_path",
    "load_shared_font",
    "load_shared_sound",
    "ProceduralAnimator",
    "SecondOrderAnimatorBase"
)

get_shared_font_path = make_package_path_finder(fonts, "ttf")
get_shared_sound_path = make_package_path_finder(sounds, "wav")
def load_shared_font(name: str): arcade.load_font(get_shared_font_path(name))
def load_shared_sound(name: str): return arcade.load_sound(get_shared_sound_path(name))

def clamp(minVal, val, maxVal):
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(minVal, min(maxVal, val))
