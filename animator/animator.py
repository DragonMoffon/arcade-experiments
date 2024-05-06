from typing import Callable, Iterable, TypeVar, Protocol

from animator.lerp import ease_linear


class Animatable(Protocol):

    def __mul__(self, other):
        ...

    def __add__(self, other):
        ...

    def __sub__(self, other):
        ...


T = TypeVar('T')
A = TypeVar('A', bound=Animatable)


class Animator:
    def __init__(self, targets: Iterable[T], attribute_name: str) -> None:
        self.targets = targets
        self.attribute_name = attribute_name

        self.current_starts: dict[T, A] = {t: getattr(t, self.attribute_name) for t in self.targets}
        self.current_goals: dict[T, A] = {t: getattr(t, self.attribute_name) for t in self.targets}

        self.current_start_times: dict[T, float] = {t: 0.0 for t in self.targets}
        self.current_end_times: dict[T, float] = {t: 0.0 for t in self.targets}

        self.local_time: float = 0.0

        self.animation_time: float = 1.0

        for t in targets:
            f = self.our_setattr(t)
            t.__setattr__ = f
            print(t.__setattr__ == f)

    def our_setattr(self, t: T) -> Callable:
        def sa(a: str, v) -> None:
            print("overloaded!")
            old = getattr(t, a)
            self.current_start_times[t] = self.local_time
            self.current_end_times[t] = self.local_time + self.animation_time
            self.current_starts[t] = old
            self.current_goals[t] = v
        return sa

    def update(self, delta_time: float):
        self.local_time += delta_time

        for t in self.targets:
            t.__dict__[self.attribute_name] = ease_linear(
                self.current_starts[t],
                self.current_goals[t],
                self.current_start_times[t],
                self.current_end_times[t],
                self.local_time
            )
