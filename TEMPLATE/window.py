from arcade import Window


class TEMPLATEWindow(Window):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE")

    def on_draw(self):
        ...

    def on_update(self, delta_time: float):
        ...


def main():
    win = TEMPLATEWindow()
    win.run()
