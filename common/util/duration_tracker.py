from typing import Callable
from logging import getLogger
from time import perf_counter_ns


try:
    import imgui

    class _TrackerBase:

        def __init__(self):
            self._func_timings: dict[Callable, list] = {}
            self._func_call_count: dict[Callable, int] = {}
            self._contexts: dict[str, set[Callable]] = {"": set()}

        def imgui_draw(self, *contexts):
            for context in contexts:
                expanded, visible = imgui.collapsing_header(f"Function Timings: {context}")

                if expanded:
                    for func in self._contexts[context]:
                        count = self._func_call_count[func]
                        if not count:
                            imgui.text(f"{func.__qualname__} - avg: N/A - count: {count}")
                            if imgui.is_item_hovered():
                                imgui.set_tooltip(f"{func}")
                            return
                        timings = self._func_timings[func]
                        avg_count = min(count, 10)
                        avg_timing = sum(timings[-avg_count:]) / avg_count

                        imgui.text(f"{func.__qualname__} - avg: {avg_timing * 1e-6:.3f}ms - count: {count}")
                        if imgui.is_item_hovered():
                            imgui.set_tooltip(f"{func}")

            imgui.separator()

except ImportError:
    class _TrackerBase:

        def __init__(self):
            self._func_timings: dict[Callable, list] = {}
            self._func_call_count: dict[Callable, int] = {}
            self._contexts: dict[str, set[Callable]] = {"": set()}

        def imgui_draw(self, *contexts):
            raise NotImplementedError("Failed to import Imgui so this func doesn't exsist")


__all__ = (
    "perf_timed",
    "perf_timed_context",
    "PERF_TRACKER"
)


class PerfTracker(_TrackerBase):

    def track_function(self, func: Callable, contexts: tuple[str, ...] = ()):
        if func in self._func_timings:
            raise KeyError("This function is already being tracked")

        self._func_timings[func] = []
        self._func_call_count[func] = 0
        self._contexts[""].add(func)
        for context in contexts:
            context_funcs = self._contexts.get(context, set())
            context_funcs.add(func)
            self._contexts[context] = context_funcs

    def print(self, *contexts):
        if not contexts:
            contexts = [""]

        print("|--- PERF TRACKING ---|")
        for context in contexts:
            funcs = self._contexts[context]
            for func in funcs:
                count = self._func_call_count[func]
                if not count:
                    print(f"- {func.__qualname__} - Uncalled")
                    continue

                timings = self._func_timings[func]
                avg_count = min(count, 10)
                avg_timing = sum(timings[-avg_count:]) / avg_count

                print(f"- {func.__qualname__} - avg: {avg_timing * 1e-6: .3f}ms - count: {count}")

    def __setitem__(self, func: Callable, elapsed_time: float):
        self._func_timings[func].append(elapsed_time)
        self._func_call_count[func] += 1


PERF_TRACKER = PerfTracker()


def perf_timed_context(*contexts):
    def perf_timed(func: Callable):
        PERF_TRACKER.track_function(func, contexts)

        def _count(*args, **kwargs):
            start = perf_counter_ns()
            val = func(*args, **kwargs)
            elapsed = (perf_counter_ns() - start)
            PERF_TRACKER[func] = elapsed
            return val

        return _count

    return perf_timed


def perf_timed(func: Callable):
    PERF_TRACKER.track_function(func, (func.__name__,))

    def _count(*args, **kwargs):
        start = perf_counter_ns()
        val = func(*args, **kwargs)
        elapsed = (perf_counter_ns() - start)
        PERF_TRACKER[func] = elapsed
        return val

    return _count


class LogSection:
    def __init__(self, name: str = "perf counter", logger: str = "lux"):
        self.logger = getLogger(logger)
        self.name = name
        self.start_time = -1.0

    def done(self):
        duration = (perf_counter_ns() - self.start_time) / 1e6
        self.logger.debug(f"Done {self.name} ({duration:.3f}ms)")

    def __enter__(self):
        self.logger.debug(f"Starting {self.name}")
        self.start_time = perf_counter_ns()

    def __exit__(self, type, value, traceback):
        if type is None:
            self.done()
