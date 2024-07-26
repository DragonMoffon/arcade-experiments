from typing import Callable
import arcade
import pyglet

from common.util import ProceduralAnimator, SecondOrderAnimatorBase, load_shared_sound


class ExperimentPickerWindow(arcade.Window):

    def __init__(self, experiments: dict[str, tuple[Callable, tuple, dict]]):
        super().__init__(640, 360, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.center_window()
        self._experiments = experiments
        self._experiment_names = tuple(experiments.keys())

        self._selected: int = 0
        self._blip_sound: arcade.Sound = load_shared_sound("blip_c")
        self._select_sound: arcade.Sound = load_shared_sound("blip_a")
        self._scroll_animator: SecondOrderAnimatorBase = ProceduralAnimator(1.0, 0.75, 1.0, 0.0, 0.0, 0.0)
        self._text_cam: arcade.camera.Camera2D = arcade.camera.Camera2D(position=(0.0, 0.0), viewport=arcade.LRBT(10, self.width-20, 10, self.height-100))
        self._text_cam.equalise()

        self._text_batch = pyglet.shapes.Batch()
        self._text = []
        text_start = 0
        max_right = -float("inf")
        max_left = float('inf')
        for experiment in experiments:
            t = arcade.Text(experiment, 0, text_start, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="center", anchor_y="center")
            self._text.append(t)
            text_start = t.bottom - 10
            max_right = max(t.right, max_right)
            max_left = min(t.left, max_left)

        self._selector_left = arcade.Text(">", int(max_left) - 10, 0, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="right", anchor_y="center")
        self._selector_right = arcade.Text("<", int(max_right) + 10, 0, font_name="GohuFont 11 Nerd Font Mono", font_size=22, batch=self._text_batch, anchor_x="left", anchor_y="center")
        self._title_text = arcade.Text("Arcade Experiments", int(self.center_x), self.height-10, font_name="GohuFont 11 Nerd Font Mono", font_size=40, anchor_x="center", anchor_y="top")

    def on_draw(self):
        self.clear()
        self.default_camera.use()
        self._title_text.draw()

        self._text_cam.use()
        self._text_batch.draw()

    def select_next(self, silent: bool = False):
        self._selected = (self._selected + 1) % len(self._experiment_names)
        y = self._text[self._selected].position[1]
        self._selector_left.y = y
        self._selector_right.y = y

        if silent:
            return

        self._blip_sound.play()

    def select_prev(self, silent: bool = False):
        self._selected = (self._selected - 1) % len(self._experiment_names)
        y = self._text[self._selected].position[1]
        self._selector_left.y = y
        self._selector_right.y = y

        if silent:
            return

        self._blip_sound.play()

    def select(self):
        self._select_sound.play()
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
