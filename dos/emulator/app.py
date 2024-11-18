from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dos.emulator.terminal import Terminal


class App:
    
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal

    def launch(self, tick: int, **options):
        self.on_launch(tick)

    def kill(self, tick: int):
        self.on_kill(tick)
        if self.terminal.awake_app == self:
            self.terminal.awake_app = None
        if self in self.terminal.asleep_apps:
            self.terminal.asleep_apps.remove(self)

    def open(self, tick: int):
        self.on_open(tick)

    def close(self, tick: int):
        self.on_close(tick)

    def run(self, tick: int):
        self.on_run(tick)

    def sleep(self, tick: int):
        self.on_sleep(tick)

    def input(self, input: int, modifiers: int, pressed: bool):
        self.on_input(input, modifiers, pressed)

    # OVERRIDE EVENTS ---------

    def on_launch(self, tick: int, **options):
        self.open(tick)

    def on_kill(self, tick: int):
        pass

    def on_open(self, tick: int):
        pass

    def on_close(self, tick: int):
        self.kill(tick)

    def on_run(self, tick: int):
        pass

    def on_sleep(self, tick: int):
        pass

    def on_input(self, input: int, modifiers: int, pressed: bool):
        pass
