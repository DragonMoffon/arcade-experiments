from arcade import LBWH, Window, Vec2, draw, key, window_commands, Texture
import pyglet
import pyautogui

GRID_WIDTH = 38
GRID_HEIGHT = 29


class PerpGrid():
    
    def __init__(self) -> None:
        self.a: Vec2 = Vec2()
        self.b: Vec2 = Vec2(0.0, 1.0)
        self.c: Vec2 = Vec2(1.0, 0.0)
        self.d: Vec2 = Vec2(1.0, 1.0)

    @property
    def points(self):
        return self.a, self.b, self.c, self.d

    @property
    def grid(self):
        a, b, c, d = self.points
        for x in range(1, GRID_WIDTH):
            fx = x / GRID_WIDTH
            for y in range(1, GRID_HEIGHT):
                fy = y / GRID_HEIGHT
                L = a.lerp(b, fy)
                R = c.lerp(d, fy)
                yield L.lerp(R, fx)


class PerpWindow(Window):

    def __init__(self, grid: PerpGrid):
        screen = window_commands.get_display_size()
        super().__init__(screen[0], screen[1], "Perspective Window", style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS, screen=1)
        self._grid = grid
        self._grid.a = Vec2(100, 100)
        self._grid.b = Vec2(100, 200)
        self._grid.c = Vec2(200, 100)
        self._grid.d = Vec2(200, 200)
        self.screen_height = screen[1]

        self.selected = None

        self._tex = Texture(pyautogui.screenshot().convert('RGBA'))

    def on_draw(self):
        self.clear()
        draw.draw_texture_rect(self._tex, LBWH(0, 0, self.width, self.height))
        a, b, c, d = self._grid.points
        e = sum((a, b, c, d), start=Vec2()) / 4

        draw.draw_line_strip(
            (a, b, d, c, a),
            (255, 255, 255, 255)
        )
        draw.draw_points(
            tuple(self._grid.grid),
            (255, 0, 0, 255)
        )
        draw.draw_point(
            e.x, e.y,
            (255, 255, 0, 255),
            4
        )

    def do_clicks(self):
        # TODO: Lists of spans from points
        for point in self._grid.grid:
            pyautogui.leftClick(int(point.x), int(self.screen_height - point.y), logScreenshot=False, interval=0.0, duration=0.0)
    

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        match self.selected:
            case 'a':
                self._grid.a = Vec2(x, y)
            case 'b':
                self._grid.b = Vec2(x, y)
            case 'c':
                self._grid.c = Vec2(x, y)
            case 'd':
                self._grid.d = Vec2(x, y)
            case 'e':
                dv = Vec2(dx, dy)
                self._grid.a += dv
                self._grid.b += dv
                self._grid.c += dv
                self._grid.d += dv

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pos = Vec2(x, y)
        a, b, c, d = self._grid.points
        e = sum((a, b, c, d), Vec2()) / 4

        dists = ((pos - v).dot(pos - v) for v in (a, b, c, d, e))
        p = min(v for v in zip(dists, ('a', 'b', 'c', 'd', 'e')))
        if p[0] <= 100:
            self.selected = p[-1]

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.selected = None

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.ENTER:
            self.minimize()
            self.do_clicks()
            self.maximize()
        elif symbol == key.SPACE:
            self.minimize()
            self._tex = Texture(pyautogui.screenshot().convert('RGBA'))
            self.maximize()



def main():
    grid = PerpGrid()
    win = PerpWindow(grid)
    win.run()
