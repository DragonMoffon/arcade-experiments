"""
This is a low-class count version of notifier, but there is another way which lets us type
notifications alot stronger, but it is more work for the end developer we can discuss DX later.

Currently:
    Notifications are just hashable tuples of items which link to a list of callbacks,
    This lets the notifications be created at run time

Possibly:
    If we make Notifier and Notification inheritable types you could make notifications statically typed,
    but it means that the developer has to hand-write the typing for every notification.

    It could be as simple as making Notifier subclass TypedDict so when we fetch a specific notifcation
    we know exactly what types
"""
# from typing import TypedDict, Callable
#
#
# class Notification:
#     @staticmethod
#     def push(*args, **kwargs):
#         raise NotImplementedError()
#
#     @staticmethod
#     def add_listener(*args, **kwargs):
#         raise NotImplementedError()
#
#
# class DefaultNotification(Notification):
#
#     @staticmethod
#     def push():
#         pass
#
#     @staticmethod
#     def add_listener(listener: Callable):
#         pass
#
#
# class EnableNotification(Notification):
#
#     @staticmethod
#     def push(scope: str):
#         pass
#
#     @staticmethod
#     def add_listener(listener: Callable):
#         pass
#
#
# class KilledNotification(Notification):
#
#     @staticmethod
#     def push(time: float):
#         pass
#
#     @staticmethod
#     def note(listener: Callable):
#         pass
#
#
# class Notifications(TypedDict):
#     enable: EnableNotification
#
#
# class CustomNotifs(Notifications):
#     kill: KilledNotification
#
#
# notifications: CustomNotifs = {
#     name: Notification() for name in CustomNotifs.__dict__['__annotations__']
# }
#
#
# notifications['kill'].push(0.9)

from typing import Callable, Any, Hashable, NamedTuple, Optional
from enum import IntEnum
import inspect


class NotificationCaller(NamedTuple):
    line: int
    function_name: str
    caller: Optional[object] = None


class NotificationCreateMode(IntEnum):
    NEVER = 0b00
    LISTENER = 0b01
    PUSH = 0b10
    BOTH = 0b11


class Notifier:

    def __init__(self, mode: NotificationCreateMode = NotificationCreateMode.BOTH):
        self._create_mode: NotificationCreateMode = mode
        self._notifications: dict[Hashable, list[Callable]] = {}
        self._defaults: dict[Hashable, dict[str, Any]] = {}
        self._callable_signatures: dict[Callable, tuple] = {}

        self._notification_cache: list[tuple[Hashable, dict[str, Any]]] = []

    def clean_up_signatures(self):
        all_active_listeners = set(sum(self._notifications.values(), start=[]))
        self._callable_signatures = {listener: cache for listener, cache in self._callable_signatures.items() if listener in all_active_listeners}

    def create_notification(self, name_: Hashable, **defaults):
        if name_ in self._notifications:
            raise ValueError("notification already exists")

        self._notifications[name_] = []
        self._defaults[name_] = defaults

    def delete_notification(self, name_: Hashable):
        del self._notifications[name_]
        del self._defaults[name_]

        self._notification_cache = filter(lambda item: item[0] != name_, self._notification_cache)

    def does_notification_exist(self, notification_: Hashable):
        return notification_ in self._notifications

    def add_listener(self, notification_: Hashable, listener_: Callable):
        if notification_ not in self._notifications and NotificationCreateMode.LISTENER & self._create_mode:
            self.create_notification(notification_)
        if listener_ in self._notifications[notification_]:
            return

        if listener_ not in self._callable_signatures:
            self._callable_signatures[listener_] = tuple(inspect.signature(listener_).parameters)

        self._notifications[notification_].append(listener_)

    def remove_listener(self, notification_: Hashable, listener_: Callable):
        self._notifications[notification_].remove(listener_)

    def push_notification(self, notification_: Hashable, immediate_: bool = False, **arguments_):
        if 'caller' not in arguments_:
            frame_code = inspect.currentframe().f_back
            f_name = frame_code.f_code.co_name
            arguments_['caller'] = NotificationCaller(frame_code.f_lineno, f_name if f_name != '<module>' else None, frame_code.f_locals.get('self', None))

        if notification_ not in self._notifications and NotificationCreateMode.PUSH & self._create_mode:
            self.create_notification(notification_, **arguments_)
        if immediate_:
            self._dispatch_notification(notification_, arguments_)
        else:
            self._notification_cache.append((notification_, arguments_))

    def push_cache(self):
        if not self._notification_cache:
            return
        # This make a copy, but maybe don't?
        # like if you do a notification in the push step
        # then it will be called later this dispatch,
        # so we don't get that delay we had to worry about?
        # We could get an infinite loop which would be bad so maybe not.

        notification_cache = self._notification_cache[:]
        self._notification_cache = []

        for notification, arguments in notification_cache:
            self._dispatch_notification(notification, arguments)

    def _dispatch_notification(self, notification_, arguments_: dict[str, Any]):
        # TODO: add try loop to make exceptions more obvious
        defaults = self._defaults[notification_]
        for listener in self._notifications[notification_]:
            kwargs = {parameter: arguments_.get(parameter, None) if parameter in arguments_ else defaults[parameter] for parameter in self._callable_signatures[listener] if parameter in arguments_ or parameter in defaults}
            listener(**kwargs)
