"""
Post Processing FrameBuffer
"""
from array import array
from dataclasses import dataclass

import arcade
import arcade.gl as gl

from dos import get_shader_path

@dataclass
class TextureConfig:
    components = 4
    dtype = 'f4'
    wrap_x = gl.CLAMP_TO_EDGE
    wrap_y = gl.CLAMP_TO_EDGE
    filter_x = gl.NEAREST
    filter_y = gl.NEAREST
    

@dataclass
class FrameConfig:
    input_size: tuple[int, int]
    output_size: tuple[int, int]
    pos: tuple[int, int]
    textures: tuple[TextureConfig, ...]
    has_depth: bool = True


# Upstream
class Frame:
    fs_geo: gl.Geometry = None

    def __init__(self, config: FrameConfig, ctx: arcade.ArcadeContext = None) -> None:
        ctx = ctx or arcade.get_window().ctx
        self.config = config
        
        self.ctx = ctx
        self.textures = list(
            ctx.texture(
                config.input_size,
                components = t.components,
                dtype = t.dtype,
                wrap_x = t.wrap_x,
                wrap_y = t.wrap_y,
                filter = (t.filter_x, t.filter_y)
            )
            for t in config.textures
        )
        self.depth = None if not config.has_depth else ctx.depth_texture(config.input_size)
        self.textures_b = list(
            ctx.texture(
                config.input_size,
                components = t.components,
                dtype = t.dtype,
                wrap_x = t.wrap_x,
                wrap_y = t.wrap_y,
                filter = (t.filter_x, t.filter_y)
            )
            for t in config.textures
        )
        self.depth_b = None if not config.has_depth else ctx.depth_texture(config.input_size)
        self._fbo = ctx.framebuffer(color_attachments=self.textures, depth_attachment=self.depth)
        self._fbo_b = ctx.framebuffer(color_attachments=self.textures_b, depth_attachment=self.depth_b)

        if Frame.fs_geo is None:
            Frame.fs_geo = gl.geometry.quad_2d_fs
            
        self.render_data = ctx.buffer(reserve=4*16) # 4 sets of 4 floats
        self.render_geo = ctx.geometry(
            [
                gl.BufferDescription(
                    self.render_data,
                    "2f 2f",
                    ["in_vert", "in_uv"],
                )
            ],
            mode=ctx.TRIANGLE_STRIP,
        )
        self.set_location(config.pos, config.output_size)
        self.render_prog = ctx.load_program(
            vertex_shader=get_shader_path('frame_render_vs'),
            fragment_shader=get_shader_path('frame_render_fs')
        )

        # --- holding values for context management
        self._previous_fbo = None
        self._previous_camera = None

    def set_location(self, pos: tuple[int, int], size: tuple[int, int]):
        self.config.pos = pos
        self.config.output_size = size
        w, h = size
        w2, h2 = w/2.0, h/2.0
        x, y = pos
        self.render_data.write(
            array('f', (
                x - w2, y + h2, 0.0, 1.0,
                x - w2, y - h2, 0.0, 0.0,
                x + w2, y + h2, 1.0, 1.0,
                x + w2, y - h2, 1.0, 0.0,
            ))
        )


    def __enter__(self):
        self._previous_fbo = self.ctx.active_framebuffer
        self._previous_camera = self.ctx.current_camera
        self._fbo.use()
        self.ctx._default_camera.use()
        return self._fbo

    def __exit__(self, *_):
        if self._previous_fbo is not None:
            self._previous_fbo.use()
        if self._previous_camera is not None:
            self._previous_camera.use()
        self.textures[0].use()
        self.render_geo.render(self.render_prog)
        return True