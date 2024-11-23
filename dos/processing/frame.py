"""
Post Processing FrameBuffer
"""
from array import array
from dataclasses import dataclass
from typing import Any

import arcade
import arcade.gl as gl
import pyglet.gl as pygl

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
    source_texture: TextureConfig


class Process:

    def __init__(self, ctx: arcade.ArcadeContext = None) -> None:
        self.ctx = ctx or arcade.get_window().ctx
        self.geo = gl.geometry.quad_2d_fs()

    def __call__(self, source: gl.Texture2D) -> Any:
        pass


class CRT(Process):
    def __init__(self, size: tuple[int, int], ctx: arcade.ArcadeContext = None) -> None:
        super().__init__(ctx)
        self.program = self.ctx.load_program(
            vertex_shader=get_shader_path('basic_vs'),
            fragment_shader=get_shader_path('CRT_p_fs')
        )
        self.program['source_texture'] = 0
        self.program['source_size'] = size

    def __call__(self, source: gl.Texture2D) -> Any:
        source.use()
        self.geo.render(self.program)


class Bloom(Process):
    def __init__(self, size: tuple[int, int], count: int, ctx: arcade.ArcadeContext = None) -> None:
        super().__init__(ctx)
        self.textures = [
            self.ctx.texture((size[0]>>level, size[1]>>level), components=3, dtype="f2", wrap_x=gl.CLAMP_TO_EDGE, wrap_y=gl.CLAMP_TO_EDGE, filter=(gl.NEAREST, gl.NEAREST)) for level in range(count)
        ]
        self.fbo = self.ctx.framebuffer(color_attachments=self.textures[0])

        self.downsample_program = self.ctx.load_program(
            vertex_shader=get_shader_path('basic_vs'),
            fragment_shader=get_shader_path('Bloom_p_downsample_fs')
        )
        self.upsample_program = self.ctx.load_program(
            vertex_shader=get_shader_path('basic_vs'),
            fragment_shader=get_shader_path('Bloom_p_upsample_fs')
        )
        self.render_program = self.ctx.load_program(
            vertex_shader=get_shader_path('basic_vs'),
            fragment_shader=get_shader_path('Bloom_p_fs')
        )
        self.render_program['strength'] = 0.1
        self.render_program['source'] = 0
        self.render_program['blur'] = 1

    def downsample(self, source: gl.Texture2D):
        viewport = self.ctx.viewport
        self.downsample_program.use()
        self.downsample_program["resolution"] = 1.0 / self.textures[0].width, 1.0 / self.textures[0].height

        source.use(0)
        for level in self.textures:
            self.ctx.viewport = (0, 0, level.width, level.height)
            pygl.glFramebufferTexture2D(pygl.GL_FRAMEBUFFER, pygl.GL_COLOR_ATTACHMENT0, pygl.GL_TEXTURE_2D, level.glo, 0)
            self.geo.render(self.downsample_program)
            self.downsample_program['resolution'] = 1.0 / level.width, 1.0 / level.height
            level.use()

        self.ctx.viewport = viewport

    def upsample(self, radius: float):
        blend = self.ctx.blend_func
        self.ctx.blend_func = self.ctx.BLEND_ADDITIVE
        self.ctx.enable(self.ctx.BLEND)
        self.upsample_program['radius'] = radius
        
        for idx in range(len(self.textures)-1, 0, -1):
            level = self.textures[idx]
            next_level = self.textures[idx - 1]

            level.use()

            self.ctx.viewport = (0, 0, next_level.width, next_level.height)
            pygl.glFramebufferTexture2D(pygl.GL_FRAMEBUFFER, pygl.GL_COLOR_ATTACHMENT0, pygl.GL_TEXTURE_2D, next_level.glo, 0)
            self.geo.render(self.upsample_program)

        self.ctx.disable(self.ctx.BLEND)
        self.ctx.blend_func = blend

    def __call__(self, source: gl.Texture2D) -> Any:
        viewport = self.ctx.viewport

        with self.fbo.activate():
            self.downsample(source)
            self.upsample(0.005)

        self.ctx.viewport = viewport
        
        source.use(0)
        self.textures[0].use(1)
        self.geo.render(self.render_program)


class TonemapAGX(Process):
    
    def __init__(self, ctx: arcade.ArcadeContext = None) -> None:
        super().__init__(ctx)
        self.program = self.ctx.load_program(
            vertex_shader=get_shader_path('basic_vs'),
            fragment_shader=get_shader_path('Tonemap_p_AGX_fs')
        )
        self.program['offset'] = 0.0, 0.0, 0.0
        self.program['slope'] = 1.0, 1.0, 1.0
        self.program['power'] = 1.0, 1.0, 1.0
        self.program['saturation'] = 1.0

    def __call__(self, source: gl.Texture2D) -> Any:
        source.use()
        self.geo.render(self.program)


# Upstream
class Frame:

    def __init__(self, config: FrameConfig, ctx: arcade.ArcadeContext = None, render: gl.Program = None) -> None:
        ctx = ctx or arcade.get_window().ctx
        self.config = config
        
        self.ctx = ctx
        texture = config.source_texture
        self.process_texture_a = ctx.texture(config.input_size, components=texture.components, dtype=texture.dtype, wrap_x=texture.wrap_x, wrap_y=texture.wrap_y, filter=(texture.filter_x, texture.filter_y))
        self.process_texture_b = ctx.texture(config.input_size, components=texture.components, dtype=texture.dtype, wrap_x=texture.wrap_x, wrap_y=texture.wrap_y, filter=(texture.filter_x, texture.filter_y))
        self.process_fbo_a = ctx.framebuffer(color_attachments=self.process_texture_a)
        self.process_fbo_b = ctx.framebuffer(color_attachments=self.process_texture_b)

        self.processes: list[Process] = []

        # Vertex Data to do the final render
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
        self.render_prog = render or ctx.load_program(
            vertex_shader=get_shader_path('frame_render_vs'),
            fragment_shader=get_shader_path('frame_render_fs')
        )

        # --- holding values for context management
        self._previous_fbo = None
        self._previous_camera = None
        self._previous_viewport = None

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

    def add_process(self, process: Process, order: int = -1):
        self.processes.insert(order, process)

    def clear(self, colour: arcade.types.RGBOrA255 = None, depth: float = 1.0, viewport: float = None):
        self.process_fbo_a.clear(color=colour, depth=depth, viewport=viewport)
        self.process_fbo_b.clear(color=colour, depth=depth, viewport=viewport)

    def __enter__(self):
        self.use()
        return self
    
    def use(self):
        self.clear()
        self._previous_fbo = self.ctx.active_framebuffer
        self._previous_camera = self.ctx.current_camera
        self._previous_viewport = self.ctx.viewport
        self.process_fbo_a.use()
        self.ctx._default_camera.use()

    def __exit__(self, *_):
        self.render()
        return False

    def render(self):
        self.ctx.viewport = (0, 0, self.config.input_size[0], self.config.input_size[1])
        for process in self.processes:
            with self.process_fbo_b.activate():
                process(self.process_texture_a)
            self.process_texture_a, self.process_texture_b = self.process_texture_b, self.process_texture_a
            self.process_fbo_a, self.process_fbo_b = self.process_fbo_b, self.process_fbo_a
        
        if self._previous_fbo is not None:
            self._previous_fbo.use()
        if self._previous_camera is not None:
            self._previous_camera.use()
        if self._previous_viewport is not None:
            self.ctx.viewport = self._previous_viewport
        self._previous_viewport = self._previous_camera = self._previous_fbo = None

        
        func = self.ctx.blend_func
        self.ctx.blend_func = self.ctx.BLEND_DEFAULT
        with self.ctx.enabled(self.ctx.BLEND):
            self.process_texture_a.use()
            self.render_geo.render(self.render_prog)
        self.ctx.blend_func = func