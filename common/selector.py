from typing import Callable


class ModeSelector:

    def next(self):
        raise NotImplementedError()

    def prev(self):
        raise NotImplementedError()

    def __call__(self):
        raise NotImplementedError()


class DefaultModeSelector(ModeSelector):

    def __init__(self, final_callback: Callable, arg_options: tuple[tuple] = ((),), kwarg_options: tuple[dict] = ({},)):
        if len(arg_options) != len(kwarg_options):
            raise ValueError("Number of arg variations has to match the number of kwarg options")

        self._callback: Callable = final_callback
        self._arg_options: tuple[tuple] = arg_options
        self._kwarg_options: tuple[dict] = kwarg_options
        self._current: int = 0

    def next(self):
        self._current = (self._current + 1) % len(self._arg_options)

    def prev(self):
        self._current = (self._current - 1) % len(self._arg_options)

    def __call__(self):
        args = self._arg_options[self._current]
        kwargs = self._kwarg_options[self._current]
        self._callback(*args, **kwargs)
