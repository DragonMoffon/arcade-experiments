from random import randint, randrange

from arcade import key

from dos.emulator.terminal import Terminal
from dos.emulator.app import App
from dos.emulator.element import Window, Boundary


class SnakeApp(App):
    
    def __init__(self, terminal: Terminal) -> None:
        self.terminal: Terminal = terminal
        self.snake_window: Window = Window('', (1, 1), (77, 27), None, None, (255, 255, 255), Boundary.SINGLE, terminal)

        self.snake_body: list[tuple[int, int]] = []
        self.food: set[tuple[int, int]] = set()

        self.launch_tick: int = 0
        self.last_open_tick: int = 0

        self.snake_direction: int = 0
        self.snake_next: int = 0
        self.snake_size: int = 5
        self.food_count: int = 1

        self.move_timer: int = 0
    
    def on_launch(self, tick: int, **options):
        self.launch_tick = tick
        self.open(tick)

    def on_open(self, tick: int):
        self.last_open_tick = tick
        self.terminal.reset_clear_commands()
        self.terminal.add_clear_command(self.terminal.draw_row, -1, back=(255, 255, 255))
        self.terminal.add_clear_command(self.terminal.draw_text, 1, -1, 'SNAKE V0.3', fore=(0, 0, 0))
        self.terminal.clear()
        self.reset()

    def on_run(self, tick: int):
        self.move_timer += 1
        if self.move_timer < 2:
            return
        self.move_timer = 0

        head = self.snake_body[0]
        self.snake_direction = self.snake_next
        match self.snake_direction:
            case 0: # N
                new = head[0], head[1] + 1
            case 1: # S
                new = head[0], head[1] - 1
            case 2: # E
                new = head[0] + 1, head[1]
            case 3: # W
                new = head[0] - 1, head[1]

        w, h = self.snake_window.w - 2, self.snake_window.h - 2
        new = new[0] % w, new[1] % h
        if new in self.food:
            self.snake_size += 3
            self.food.remove(new)
        elif new in self.snake_body:
            self.reset()
            self.last_open_tick = tick
            return

        self.snake_body.insert(0, new)
        while len(self.snake_body) > self.snake_size:
            self.snake_body.pop(-1)

        while len(self.food) < self.food_count:
            food = randrange(0, w), randrange(0, h)
            if food in self.snake_body:
                continue
            self.food.add(food)

        self.draw()

    def on_input(self, input: int, modifiers: int, pressed: bool):
        if pressed:
            if input == key.RIGHT and self.snake_direction != 3:
                self.snake_next = 2
            elif input == key.LEFT and self.snake_direction != 2:
                self.snake_next = 3
            elif input == key.UP and self.snake_direction != 1:
                self.snake_next = 0
            elif input == key.DOWN and self.snake_direction != 0:
                self.snake_next = 1

    def reset(self):
        w, h = self.snake_window.w - 2, self.snake_window.h - 2
        self.snake_size = 5
        self.food_count = 1
        self.snake_direction = 0
        self.snake_next = 0
        self.food = {(randrange(0, w), randrange(0, h))}
        self.snake_body = [(randrange(0, w), randrange(0, h))]
    
    def draw(self):
        l, b = self.snake_window.l, self.snake_window.b
        self.terminal.screen.clear(h = self.terminal.screen.char_count[1]-1)
        self.snake_window.draw()
        for pos in self.food:
            self.terminal.draw_char(l+1+pos[0], b+1+pos[1], back=(255, 0, 0))

        for pos in self.snake_body:
            self.terminal.draw_char(l+1+pos[0], b+1+pos[1], back=(255, 255, 255))

        self.terminal.draw_text(0,0, f'length: {self.snake_size // 5 + 1}', (255, 255, 255))


        self.terminal.draw_text(self.terminal.screen.char_count[0]-6-len(str(self.terminal.current_tick - self.last_open_tick)), 0, f'time: {self.terminal.current_tick - self.last_open_tick}', (255, 255, 255))