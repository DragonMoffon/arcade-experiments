import arcade


class Application(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "DDA 3D")


def main():
    app = Application()
    app.run()
