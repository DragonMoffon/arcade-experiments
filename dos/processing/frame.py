"""
Post Processing FrameBuffer
"""
from dataclasses import dataclass

import arcade
import arcade.gl as gl

@dataclass
class TextureConfig:
    componenets = 4
    

@dataclass
class FrameConfig:
    size: tuple[int, int]
    


class Frame:

    def __init__(self, config: FrameConfig, ctx: arcade.ArcadeContext = None) -> None:
        ctx = ctx or arcade.get_window().ctx
        
        self.ctx = ctx
        self.textures = tuple(
            ctx.texture(config.s)
        )
        self._fbo = None

    def __enter__(self):
        pass

    def __exit__(self, *_):
        return True