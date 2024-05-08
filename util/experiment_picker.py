from typing import Callable
import arcade
import pyglet

from util import ProceduralAnimator, SecondOrderAnimatorBase


class ExperimentPickerWindow(arcade.Window):

    def __init__(self, experiments: dict[str, tuple[Callable, tuple, dict]]):
        super().__init__(640, 360, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.center_window()
        self._experiments = experiments
        self._experiment_names = tuple(experiments.keys())

        self._selected: int = 0
        self._scroll_animator: SecondOrderAnimatorBase = ProceduralAnimator(1.0, 0.75, 1.0, 0.0, 0.0, 0.0)
        self._text_cam: arcade.camera.Camera2D = arcade.camera.Camera2D(position=(0.0, 0.0), viewport=(10, 10, self.width-20, self.height-100))
        self._text_cam.equalise()

        self._text_batch = pyglet.shapes.Batch()
        self._text = []
        text_start = 0
        max_right = float("inf")
        for experiment in experiments:
            t = arcade.Text(experiment, 0, text_start, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="center", anchor_y="center")
            self._text.append(t)
            text_start = t.bottom - 10
            max_right = min(t.right, max_right)

        self._selector_left = arcade.Text(">", int(max_right) - 10, 0, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="right", anchor_y="center")
        self._selector_right = arcade.Text("<", 10 - int(max_right), 0, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="left", anchor_y="center")
        self._title_text = arcade.Text("Arcade Experiments", int(self.center_x), self.height-10, font_name="GohuFont 11 Nerd Font Mono", font_size=40, anchor_x="center", anchor_y="top")

    def on_draw(self):
        self.clear()
        self.default_camera.use()
        self._title_text.draw()

        self._text_cam.use()
        self._text_batch.draw()

    def select_next(self):
        self._selected = (self._selected + 1) % len(self._experiment_names)
        y = self._text[self._selected].position[1]
        self._selector_left.y = y
        self._selector_right.y = y

    def select_prev(self):
        self._selected = (self._selected - 1) % len(self._experiment_names)
        y = self._text[self._selected].position[1]
        self._selector_left.y = y
        self._selector_right.y = y

    def select(self):
        selected = self._experiment_names[self._selected]
        main_func, args, kwargs = self._experiments[selected]
        del self._experiments
        del self._experiment_names
        self.default_camera.use()
        self.close()
        main_func(*args, **kwargs)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.ESCAPE:
                self.close()
            case arcade.key.UP:
                self.select_prev()
            case arcade.key.W:
                self.select_prev()
            case arcade.key.DOWN:
                self.select_next()
            case arcade.key.S:
                self.select_next()
            case arcade.key.SPACE:
                self.select()
            case arcade.key.ENTER:
                self.select()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y >= 1:
            self.select_prev()
        elif scroll_y <= -1:
            self.select_next()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.select()

    def on_update(self, delta_time: float):
        pos = self._text[self._selected].position[1]
        self._scroll_animator.update(delta_time, pos)
        self._text_cam.position = 0, int(self._scroll_animator.y)


def main(experiments: dict[str, tuple[Callable, tuple, dict]]):
    window = ExperimentPickerWindow(experiments)
    window.run()
