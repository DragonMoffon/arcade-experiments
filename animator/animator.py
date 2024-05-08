from typing import Callable, TypeVar, Protocol, Generic

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


class AnimatableProxy(Generic[T]):

    def __init__(self, obj: T, anim_speed: float, animated_attributes: tuple[str, ...],
                 animation_function: Callable[[float, float, float, float, A], A] = ease_linear):
        self._core = obj
        self._time = 0.0
        self._speed = anim_speed
        self._attr = set(animated_attributes)
        self._old_values = {attr: getattr(obj, attr) for attr in animated_attributes}
        self._target_values = {attr: getattr(obj, attr) for attr in animated_attributes}
        self._start_time = {attr: 0.0 for attr in animated_attributes}
        self._end_time = {attr: 0.0 for attr in animated_attributes}

        self._animation_function = animation_function

    def __setattr__(self, key: str, value):
        if key.startswith("_"):
            self.__dict__[key] = value
            return

        old = getattr(self._core, key)
        self._old_values[key] = old
        self._target_values[key] = value
        self._start_time[key] = self._time
        self._end_time[key] = self._time + self._speed

    def __getattr__(self, item: str):
        return getattr(self._core, item)

    def update(self, dt: float):
        self._time = time = self._time + dt
        old = self._old_values
        target = self._target_values
        start = self._start_time
        end = self._end_time

        for attr in self._attr:
            lerp = self._animation_function(
                old[attr], target[attr],
                start[attr], end[attr],
                time
            )
            setattr(self._core, attr, lerp)


class DragonAnimator(Generic[T]):

    def __init__(self, animated_attributes: tuple[str, ...]):
        self._proxies: list[AnimatableProxy[T]] = list()
        self._attrs = animated_attributes

    def proxy(self, obj: T) -> AnimatableProxy[T]:
        proxy = AnimatableProxy(obj, 1.0, self._attrs)
        self._proxies.append(proxy)
        return proxy

    def update(self, dt: float):
        for proxy in self._proxies:
            proxy.update(dt)
