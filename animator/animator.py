from typing import Callable, Iterable, TypeVar, Protocol, Generic

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

    def __init__(self, obj: T, anim_speed: float, animated_attributes: tuple[str, ...]):
        self.__dict__['_core'] = obj
        self.__dict__['_time'] = 0.0
        self.__dict__['_speed'] = anim_speed
        self.__dict__['_attr'] = set(animated_attributes)
        self.__dict__['_old_values'] = {attr: getattr(obj, attr) for attr in animated_attributes}
        self.__dict__['_target_values'] = {attr: getattr(obj, attr) for attr in animated_attributes}
        self.__dict__['_start_time'] = {attr: 0.0 for attr in animated_attributes}
        self.__dict__['_end_time'] = {attr: 0.0 for attr in animated_attributes}

    def __setattr__(self, key, value):
        old = getattr(self.__dict__['_core'], key)

        self.__dict__['_old_values'][key] = old
        self.__dict__['_target_values'][key] = value
        self.__dict__['_start_time'][key] = self.__dict__['_time']
        self.__dict__['_end_time'][key] = self.__dict__['_time'] + self.__dict__['_speed']

    def __getattr__(self, item):
        return getattr(self.__dict__['_core'], item)

    def update(self, dt):
        self.__dict__['_time'] = time = self.__dict__['_time'] + dt
        old = self.__dict__['_old_values']
        target = self.__dict__['_target_values']
        start = self.__dict__['_start_time']
        end = self.__dict__['_end_time']

        for attr in self.__dict__['_attr']:
            lerp = ease_linear(
                old[attr], target[attr],
                start[attr], end[attr],
                time
            )
            setattr(self.__dict__['_core'], attr, lerp)


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
