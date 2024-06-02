from arcade import Window


class Clock:

    def __init__(self):
        self.fixed_delta_time: float = 1/60.0  # The time in seconds that each fixed time step will increase by
        self.elapsed_time_speed: float = 1.0  # The rate at which time is tracked to elapse

        self.elapsed_time: float = 0.0  # The time in seconds that are considered to have elapsed

        self.accumulated_time: float = 0.0  # The time in seconds that the window has been 'ticking'
        self.frame: int = 0  # The number of frames that the clock has ticked for

        self.current_time: float = 0.0  # The time in seconds that have been stepped through at a constant rate
        self.fixed_frame: int = 0  # The number of frames the clock has ticked at a constant rate for

    def tick(self, delta_time):
        self.elapsed_time += delta_time * self.elapsed_time_speed
        self.frame += 1

    def tick_fixed(self):
        self.current_time += self.fixed_delta_time
        self.fixed_frame += 1

    @property
    def next_time(self):
        return self.current_time + self.fixed_delta_time

    @property
    def fraction(self):
        diff = self.elapsed_time - self.current_time
        return diff / self.fixed_delta_time


class RigidWindow(Window):

    def __init__(self):
        super().__init__()
        self.register_event_type('on_fixed_update')

        self.clock = Clock()

    def _dispatch_updates(self, delta_time: float):
        self.clock.tick(delta_time)

        while self.clock.next_time < self.clock.elapsed_time:
            self.clock.tick_fixed()
            self.dispatch_event('on_fixed_update', self.clock.fixed_delta_time)

        self.dispatch_event('on_update', delta_time)

    def on_fixed_update(self, delta_time: float):
        pass

    def on_update(self, delta_time: float):
        pass


def main():
    app = RigidWindow()
    app.run()
