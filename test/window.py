from arcade import Window, draw_rect_filled
from common.util import smerp

class TEMPLATEWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE", style=Window.WINDOW_STYLE_DIALOG, resizable=True)
        self.goal = self.get_location()

    def on_draw(self):
        self.clear()
        draw_rect_filled(self.rect, (255, 255, 255, 125))

    def on_update(self, delta_time: float):
        self.set_location(*self.goal)

    def on_mouse_enter(self, x: int, y: int) -> bool | None:
        return super().on_mouse_enter(x, y)
    
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> bool | None:
        l = self.get_location()
        self.goal = max(0, min(2*1920, l[0] + dx)), max(0, min(1440, l[1] - dy))


def main():
    win = TEMPLATEWindow()
    win.run()
