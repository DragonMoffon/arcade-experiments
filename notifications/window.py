from math import cos, pi
from arcade import Window, SpriteList, Sprite, SpriteSolidColor, SpriteCircle, LRBT
from arcade.experimental.input import Keys

from pyglet.math import Vec2

from notifications.notification import NotificationCreateMode, Notifier
from notifications.environment import EnivroArea
from notifications.audio import AudioChannel, AudioListener


class NotificationWindow(Window):

    def __init__(self, notification_mode: NotificationCreateMode = NotificationCreateMode.BOTH):
        super().__init__(1420, 720, "Notification Demo")
        self.notifier: Notifier = Notifier(notification_mode)

        self.player: Sprite = SpriteSolidColor(25, 40, 0, 0, (255, 255, 255, 255))
        self.player_animation_timer: float = 0.0

        self.fire_circle: Sprite = SpriteCircle(100, (255, 0, 0, 125), True)
        self.fire_circle.position = self.center
        self.fire_burn_timer: float = 0.0

        self._scene_environment: SpriteList[EnivroArea] = SpriteList(use_spatial_hash=True)
        self._scene_environment.extend((
            EnivroArea(LRBT(0, self.center_x, 0, self.height), 'a'),
            EnivroArea(LRBT(self.center_x, self.width, 0, self.height), 'b')
        ))
        self._scene_renderer: SpriteList = SpriteList()

        self._scene_renderer.extend((self.fire_circle, self.player))

        self.directions: list = [0, 0, 0, 0]

        self._audio: AudioListener = AudioListener(self._scene_environment)

    def _dispatch_updates(self, delta_time: float):
        super()._dispatch_updates(delta_time)
        self.notifier.push_cache()

    def on_key_press(self, symbol: int, modifiers: int):
        match Keys(symbol):
            case Keys.W:
                self.directions[0] = 1
            case Keys.S:
                self.directions[1] = 1
            case Keys.D:
                self.directions[2] = 1
            case Keys.A:
                self.directions[3] = 1

    def on_key_release(self, symbol: int, modifiers: int):
        match Keys(symbol):
            case Keys.W:
                self.directions[0] = 0
            case Keys.S:
                self.directions[1] = 0
            case Keys.D:
                self.directions[2] = 0
            case Keys.A:
                self.directions[3] = 0

    def on_draw(self):
        self.clear()
        self._scene_renderer.draw(pixelated=True)

    def on_update(self, delta_time: float):
        v = self.directions[0] - self.directions[1]
        h = self.directions[2] - self.directions[3]

        if not h and not v:
            self.player_animation_timer = 0
            self.player.angle = 0
        else:
            move = Vec2(h, v).normalize() * delta_time * 250.0
            o_pos = self.player.position

            self.player.position = o_pos[0] + move.x, o_pos[1] + move.y

            last_time = self.player_animation_timer
            self.player_animation_timer = (self.player_animation_timer + delta_time * 2.0) % 1.0
            self.player.angle = cos(self.player_animation_timer * 2.0 * pi) * 15

            if self.player_animation_timer < last_time or last_time < 0.5 < self.player_animation_timer:
                # we switched back around so the player took a "step"
                self.notifier.push_notification(
                    "play-audio",
                    track='player-step',
                    channel=AudioChannel.SFX,
                    location=self.player.position
                )

        if self.player.collides_with_sprite(self.fire_circle):
            self.fire_burn_timer += delta_time
            if self.fire_burn_timer >= 2.0:
                self.notifier.push_notification(
                    'play-audio',
                    track='player-hurt',
                    channel=AudioChannel.SFX,
                    location=self.player.position
                )
                self.fire_burn_timer -= 2.0

        else:
            self.fire_burn_timer = 0

def main():
    win = NotificationWindow()
    win.notifier.push_notification('crazy_dave')
    win.run()