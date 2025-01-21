from dos.emulator.app import App
from dos.emulator.terminal import Terminal
from dos.emulator.element import Window, Boundary


class StarCommApp(App):

    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal
        self.output = Window('Output', (2, 2), (74, 5), (168, 168, 168), (84, 84, 252), (255, 255, 255), Boundary.DOUBLE, self.terminal)
        self.channel = Window('Channel', (2, 8), (52, 20), (168, 168, 168), (84, 84, 252), (255, 255, 255), Boundary.DOUBLE, self.terminal)
        self.signal = Window('Signal', (55, 8), (21, 20), (168, 168, 168), (84, 84, 252), (255, 255, 255), Boundary.DOUBLE, self.terminal)


    def on_open(self, tick: int):
       with self.terminal.record_clear():
            self.terminal.draw_box(0, 0, 80, 30, back=(0, 0, 168))
            self.terminal.draw_row(0, 0, 80, back=(0, 168, 168))
            self.terminal.draw_row(-1, 0, 80, back=(0, 168, 168))
            self.terminal.draw_text(0, -1, 'StarCom v1.4.00', (0, 0, 0))
            self.terminal.draw_text(0, 0, 'ID:T44  KEY:XXXXXX', (0, 0, 0))

    def on_run(self, tick: int):
        self.terminal.clear()
        self.draw()

    def draw(self):
        self.output.draw()
        self.channel.draw()
        self.signal.draw()