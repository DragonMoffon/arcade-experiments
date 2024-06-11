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


class Notifier:

    def __init__(self):
        pass

    def create_notification(self, name: str, ):
        pass

    def note_notification(self):
        pass

    def push_notification(self):
        pass