# flake8: noqa

from arcade import load_font

from common.util.procedural_animator import *


def load_gohu_font():
    load_font("./common/util/gohu.ttf")

def clamp(minVal, val, maxVal):
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(minVal, min(maxVal, val))
