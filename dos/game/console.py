from dos.emulator.app import App


class ConsoleApp(App):
    def __init__(self, terminal):
        self.terminal = terminal

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