from arcade import Window as ArcadeWindow
from arcade import Camera2D, draw_texture_rect, load_texture
from arcade.future.background import Background
from pyglet.display import get_display

from common.data_loading import make_package_path_finder

import scoundrel.data as data

get_image_path = make_package_path_finder(data, "png")

class Window(ArcadeWindow):
    WIDTH = 1280
    HEIGHT = 720
    RATIO = WIDTH / HEIGHT
    SCROLL_SPEED = 16.0

    def __init__(self):
        screen = get_display().get_default_screen()
        screen_mode = screen.get_mode()
        print(screen_mode)
        rate = 1/60.0 if screen_mode.rate is None or screen_mode.rate == 0.0 else 1.0 / screen_mode.rate
        super().__init__(1280, 720, "Scoundrel", resizable=True, draw_rate=rate, update_rate=1/10000.0)
        self.background_color = (0x2c, 0x34, 0x38)
        self._bounds_t = 0.0
        self._bounds_offset = (0.0, 0.0)
        self._screen_origin = self.get_location()
        self.camera = Camera2D()

        self.bounds_lb = Background.from_file(get_image_path('bounds'), filters=(self.ctx.LINEAR, self.ctx.LINEAR)) # Left or Bottom
        self.bounds_rt = Background.from_file(get_image_path('bounds'), filters=(self.ctx.LINEAR, self.ctx.LINEAR)) # Right or Top
        self.show_bounds = False

        self.background_texture = load_texture(get_image_path('Play Space'))

    def on_draw(self):
        self.clear()
        if self.show_bounds:
            bounds_offset_true = self._bounds_offset[0] - self._bounds_t * self.SCROLL_SPEED, self._bounds_offset[1] + self._bounds_t * self.SCROLL_SPEED
            self.bounds_lb.texture.offset = bounds_offset_true
            self.bounds_rt.texture.offset = bounds_offset_true
            self.bounds_lb.draw()
            self.bounds_rt.draw()
        with self.camera.activate():
            draw_texture_rect(self.background_texture, self.camera.viewport, pixelated=True)

    def on_update(self, delta_time: float):
        self._bounds_t = self.time
    
    def on_move(self, x, y):
        self._bounds_offset = x - self._screen_origin[0], self._screen_origin[1] - y

    def on_resize(self, width, height):
        self.camera.match_window(position=True, aspect=self.RATIO)
        view = self.camera.viewport
        if view.width == width and view.height == height:
            self.show_bounds = False
            return
        self.show_bounds = True        

        if view.width == width:
            h = (height - view.height) / 2.0
            self.bounds_rt.pos = (0.0, view.top)
            self.bounds_lb.size = self.bounds_rt.size = width, h
        else:
            w = (width - view.width) / 2.0
            self.bounds_rt.pos = (view.right, 0.0)
            self.bounds_lb.size = self.bounds_rt.size = w, height



def main():
    win = Window()
    win.run()
