import numpy as np

from arcade import Window as ArcadeWindow, XYWH, draw_rect_filled, draw_point, draw_line

__all__ = (
    'main',
)

class Slider:

    def __init__(self, center: tuple[float, float], width: float, minimum: float, maximum: float, initial: float) -> None:
        self._center = center
        self._width = width
        self._min = minimum
        self._max = maximum
        self._value = initial

    def draw(self):
        rect = XYWH(self._center[0], self._center[1], self._width, 5)
        draw_rect_filled(rect, (125, 125, 125, 125))
        pos = self.slider_position()
        draw_point(pos[0], pos[1], (255, 255, 255, 255), 10)
        
    def slider_position(self):
        percent = (self._value - self._min) / (self._max - self._min)
        x = (percent - 0.5) * self._width + self._center[0]
        return x, self._center[1]

    def contains_point(self, point: tuple[float, float]):
        pos = self.slider_position()
        return abs(pos[0] - point[0]) <= 5 and abs(pos[1] - point[1]) <= 5
    
    def move_value(self, new_pos: float):
        left = self._center[0] - 0.5 * self._width
        percent = max(0.0, min(1.0, (new_pos - left) / self._width))
        self._value = self._max * percent + (1 - percent) * self._min

class System:

    def __init__(self, k1: float, k2: float, x: float, v: float, dt: float) -> None:
        self._k1: float = k1
        self._k2: float = k2
        self._dt: float = dt

        self.x: float = x
        self.v: float = v
        self.a: float = 0

        self._position_matrix = np.asarray([1.0, self._dt, 0.0])
        self._velocity_matrix = np.asarray([0.0, 1.0, self._dt])
        self._acceleration_matrix = np.asarray([-self._k1, -self._k2, 0.0])

    def update_values(self, k1: float | None, k2: float | None):
        if k1 is not None:
            self._k1 = k1
        
        if k2 is not None:
            self._k2 = k2
        
        self._position_matrix = np.asarray([1.0, self._dt, 0.0])
        self._velocity_matrix = np.asarray([0.0, 1.0, self._dt])
        self._acceleration_matrix = np.asarray([-self._k1, -self._k2, 0.0])

    def update(self):
        _state = np.asarray([self.x, self.v, self.a])
        _state[0] = np.matmul(self._position_matrix, _state)
        _state[2] = np.matmul(self._acceleration_matrix, _state) - 9.81
        _state[1] = np.matmul(self._velocity_matrix, _state) 
        self.x, self.v, self.a = _state
        print(self.x, self.v, self.a)
        print(0.5 * (self.v**2 + self._k1 * self.x**2))
        

class Window(ArcadeWindow):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE", fixed_rate=1/120)
        self._k1_slider = Slider((self.center_x, 20), 200, 0.0, 100.0, 50.0)
        self._k2_slider = Slider((self.center_x, 40), 200, 0.0, 2.0, 0.0)
        self._hovered_slider: Slider | None = None

        self._system = System(50.0, 0.0, 20.0, 0.0, self._fixed_rate)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        if self._hovered_slider is not None:
            if not self._hovered_slider.contains_point((x, y)):
                self._hovered_slider = None
        elif self._k1_slider.contains_point((x, y)):
            self._hovered_slider = self._k1_slider
        elif self._k2_slider.contains_point((x, y)):
            self._hovered_slider = self._k2_slider

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        if self._hovered_slider is not None:
            self._hovered_slider.move_value(x)

            self._system.update_values(self._k1_slider._value, self._k2_slider._value)

    def on_draw(self):
        self.clear()
        self._k1_slider.draw()
        self._k2_slider.draw()

        d = 100.0
        y1 = self.center_y
        y2 = y1 + d + self._system.x
        y3 = y1 + d
        x = self.center_x
        draw_line(x, y1, x, y2, (125, 125, 125), 2)
        draw_point(x, y3, (255, 255, 0), 6)
        draw_point(x, y1, (255, 255, 255), 10)
        draw_point(x, y2, (255, 255, 255), 10)
        
    def on_fixed_update(self, delta_time: float):
        self._system.update()
        


def main():
    win = Window()
    win.run()
