from arcade import Window, Text


class ExpWin(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._show_fps: bool = False
        self._average_length: int = 10
        self._fps_history: list = []
        self._fps_text = Text("", x=self.width, y=self.height, anchor_x="right", anchor_y="top",
                              font_name="GohuFont 11 Nerd Font Mono")

    def show_fps(self, show: bool = False):
        self._show_fps = show

    def update_fps_text(self, *, n_x=None, n_y=None, n_x_anchor=None, n_y_anchor=None):
        if n_x:
            self._fps_text.x = n_x
            
        if n_y:
            self._fps_text.y = n_y

        if n_x_anchor:
            self._fps_text.anchor_x = n_x_anchor

        if n_y_anchor:
            self._fps_text.anchor_y = n_y_anchor

    def _dispatch_updates(self, delta_time: float):
        super()._dispatch_updates(delta_time)
        self._fps_history.append(1 / delta_time)
        if len(self._fps_history) > self._average_length:
            self._fps_history = self._fps_history[-self._average_length:]

    def on_refresh(self, dt):
        if self._show_fps and self._fps_history:
            self._fps_text.text = f"FPS: {sum(self._fps_history) / len(self._fps_history): .1f}"
            self._fps_text.draw()
