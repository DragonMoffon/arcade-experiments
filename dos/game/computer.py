from dataclasses import dataclass

import arcade

from dos.emulator import CHAR_COUNT, CHAR_SIZE
from dos.emulator.screen import Screen

@dataclass
class Data:
    channel: int
    sender: str
    time: int
    message: str

class Computer:
    def __init__(self) -> None:
        self.data: list[Data]

        self.current_data: Data | None = None

        window = arcade.get_window()
        self.screen = Screen(CHAR_COUNT, CHAR_SIZE, window.center, window.ctx)

    def draw(self, camera: arcade.Camera2D):
        with camera.activate():
            self.screen.render()
            self.screen.draw()