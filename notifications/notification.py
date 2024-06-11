"""
This is a low-class count version of notifier, but there is another way which lets us type
notifications alot stronger, but it is more work for the end developer we can discuss DX later.

Currently:
    Notifications are just hashable tuples of items which link to a list of callbacks,
    This lets the notifications be created at run time

Possibly:
    If we make Notifier and Notification inheritable types you could make notifications statically typed,
    but it means that the developer has to hand-write the typing for every notification.

    It could be as simple as making Notifier subclass TypedDict so when we fetch a spceific notifcation
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

from typing import Callable, Any
from enum import IntEnum
import inspect


class NotificationCreateMode(IntEnum):
    NEVER = 0b00
    LISTENER = 0b01
    PUSH = 0b10
    BOTH = 0b11


class Notifier:

    def __init__(self):
        self._create_mode: NotificationCreateMode = NotificationCreateMode.BOTH
        self._notifications: dict[str, list] = {}
        self._defaults: dict[str, dict[str, Any]] = {}

        self._notification_cache: list[tuple[str, dict[str, Any]]] = []

    def create_notification(self, name_: str, **kwargs):
        if name_ in self._notifications:
            raise ValueError("notification already exists")

        self._notifications[name_] = []
        self._defaults[name_] = kwargs

    def does_notification_exist(self, notification_: str):
        return notification_ in self._notifications

    def add_listener(self, notification_: str, listener_: Callable):
        if notification_ not in self._notifications and NotificationCreateMode.LISTENER & self._create_mode:
            self.create_notification(notification_)
        if listener_ in self._notifications[notification_]:
            return
        self._notifications[notification_].append(listener_)

    def push_notification(self, notification_, immediate_: bool = False, **kwargs):
        if notification_ not in self._notifications and NotificationCreateMode.PUSH & self._create_mode:
            self.create_notification(notification_, **kwargs)
        if immediate_:
            self._dispatch_notification(notification_, kwargs)
        else:
            self._notification_cache.append((notification_, kwargs))

    def push_cache(self):
        if not self._notification_cache:
            return
        # This make a copy, but maybe don't?
        # like if you do a notification in the push step
        # then it will be called later this dispatch,
        # so we don't get that delay we had to worry about?
        # We could get an infinite loop which would be bad so maybe not.

        for notification, arguments in self._notification_cache[:]:
            self._dispatch_notification(notification, arguments)
        self._notification_cache = []

    def _dispatch_notification(self, notification_, arguments_: dict[str, Any]):
        # TODO: add try loop to make exceptions more obvious
        defaults = self._defaults[notification_]
        for listener in self._notifications[notification_]:
            kwargs = {parameter: arguments_.get(parameter, None) if parameter in arguments_ else defaults[parameter] for parameter in inspect.signature(listener).parameters if parameter in arguments_ or parameter in defaults}
            listener(**kwargs)


def player_enable(time: float):
    print("player", time)


def enemy_enable():
    print("enemy")


notifier = Notifier()

notifier.create_notification("enable", time=100.0)
notifier.add_listener("enable", player_enable)
notifier.add_listener("enable", enemy_enable)  # Even though enemy_enable has no arguments that isn't an issue

notifier.push_notification("enable")  # with no time kwarg so use default
notifier.push_notification("enable", time=20.0)  # with a time kwarg so ignore default

print("Before notifications 1")
notifier.push_cache()
print("After notifications 1")
notifier.push_notification("enable", True, time=10.0)  # with immediate as true
print("Before notifications 2")
notifier.push_cache()  # No notifications get called because the only one since last push_cache was immediate
print("After notifications 2")
