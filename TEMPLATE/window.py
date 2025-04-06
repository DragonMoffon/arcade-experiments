from arcade import Window as ArcadeWindow

__all__ = (
    'main'
)

class Window(ArcadeWindow):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE")

    def on_draw(self):
        ...

    def on_update(self, delta_time: float):
        ...


def main():
    win = Window()
    win.run()
