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

    @property
    def value(self):
        return self._value

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


class SoftBody:

    def __init__(self, k1: float, k2: float, dt: float, positions: tuple[tuple[float, float], ...], connections: tuple[tuple[int, int], ...]) -> None:
        self._k1: float = k1
        self._k2: float = k2
        self._dt: float = dt
        self.x = np.asarray(positions)
        self.v = np.zeros((len(positions), 2))
        self.p = np.zeros((len(positions), 2))
        self.m = np.ones(len(positions))


        self.connections = connections
        self.create_connections_matrix()
        self.D = 2*np.sqrt(np.matmul(self.connection_matrix, self.x[:, 0])**2 + np.matmul(self.connection_matrix, self.x[:, 1])**2)

    def create_connections_matrix(self):
        self.connection_matrix = np.zeros((len(self.connections), self.x.shape[0]))
        for i, (a, b) in enumerate(self.connections):
            self.connection_matrix[i, a] = 1
            self.connection_matrix[i, b] = -1

    def add_motor_force(self, point: int, force: tuple[float, float]):
        self.m[point] = force

    def add_point(self, point: tuple[float, float], m: float = 1.0):
        self.x = np.append(self.x, [point], axis=0)
        self.v = np.append(self.v, [[0.0, 0.0]], axis=0)
        self.p = np.append(self.p, [[0.0, 0.0]], axis=0)
        self.m = np.append(self.m, m)

        self.create_connections_matrix()
    
    def remove_point(self, point: int):
        if point >= self.x.shape[0]:
            raise IndexError(f"Point {point} is not in the soft body")
        self.x = np.delete(self.x, point, axis=0)
        self.v = np.delete(self.v, point, axis=0)
        self.p = np.delete(self.p, point, axis=0)
        self.m = np.delete(self.m, point)

        c = list(self.connections)
        n = 0
        for idx, (a, b) in enumerate(self.connections):
            if point == a or point == b:
                c.pop(idx)
                self.D = np.delete(self.D, idx-n)
                n += 1
        self.connections = tuple(c)
        self.create_connections_matrix()

    def move_point(self, point: int, pos: tuple[float, float]):
        self.x[point] = pos

    def add_conection(self, connection: tuple[int, int], d: float | None = None):
        if connection[0] >= self.x.shape[0] or connection[1] >= self.x.shape[0]:
            raise IndexError(f'Connection {connection} has invalid index')
        
        self.connections = self.connections + (connection,)
        if d is None:
            dp = (self.x[connection[0]] - self.x[connection[1]])**2
            d = np.sqrt(dp[0] + dp[1])
        self.D = np.append(self.D, d)
        self.create_connections_matrix()

    def update_values(self, k1: float | None, k2: float | None):
        if k1 is not None:
            self._k1 = k1
        
        if k2 is not None:
            self._k2 = k2

    def update(self):
        self.x = self.x + self._dt*self.v
        dx = np.matmul(self.connection_matrix, self.x[:, 0])
        dy = np.matmul(self.connection_matrix, self.x[:, 1])

        D = np.sqrt(dx**2 + dy**2)
        
        f = - self._k1 * (D - self.D)
        ct = self.connection_matrix.transpose()
        fx = np.matmul(ct, f*dx/D)/self.m
        fy = np.matmul(ct, f*dy/D)/self.m
        F = np.column_stack((fx, fy))
        self.v = self.v + self._dt * (F - self._k2 * self.v + self.p)

    def debug_draw(self):
        for i, j in self.connections:
            x1 = self.x[i]
            x2 = self.x[j]
            draw_line(*x1, *x2, (125, 125, 125), 3)
        for x in self.x:
            draw_point(*x, (255, 255, 255), 12)

class Window(ArcadeWindow):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE", fixed_rate=1/120)
        self._k1_slider = Slider((self.center_x, 20), 200, 0.0, 100.0, 10.0)
        self._k2_slider = Slider((self.center_x, 40), 200, 0.0, 2.0, 2.0)
        self._hovered_slider: Slider | None = None

        self.body = SoftBody(
            self._k1_slider.value, self._k2_slider.value, self._fixed_rate,
            ((self.center_x-50, self.center_y+50), (self.center_x+50, self.center_y+50), (self.center_x+50, self.center_y-50), (self.center_x-50, self.center_y-50), (self.center_x, self.center_y),),
            ((0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (0, 2), (1, 3)),
        )

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
            self.body.update_values(self._k1_slider.value, self._k2_slider.value)
        else:
            idx = self.body.x.shape[0] - 1
            self.body.move_point(idx, (x, y))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self._hovered_slider is None:
            self.body.add_point((x, y), float('inf'))
            idx = self.body.x.shape[0] - 1
            self.body.add_conection((idx, idx-1), 0.0)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if self._hovered_slider is None:
            idx = self.body.x.shape[0] - 1
            self.body.remove_point(idx)

    def on_draw(self):
        self.clear()
        self._k1_slider.draw()
        self._k2_slider.draw()

        self.body.debug_draw()
        # self._system.debug_draw()
        
    def on_fixed_update(self, delta_time: float):
        # self._system.update()
        self.body.update()
        


def main():
    win = Window()
    win.run()
