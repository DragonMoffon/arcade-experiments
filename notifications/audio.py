"""
Normally in games we just play a sounds using arcade.Sound.play() which is great in simple cases,
but what if we want a sound to get affected by where the player is standing? or if we change the volume
we need to know every sound currently playing. Obviously we need some form of audio manager.

However, if we created this as a singleton we would a) need to access it in loads of places, and b) we would
be locked to a single listening location. What if we were doing a split screen game? Then we need an audio manager
per player.

The solution: Notifications, When we want to make a sound we send out a "play_sound" notification with the sound
we want played, and where it is in world space.

Then for every audio listener we figure out how loud, with what panning the sound should be played at.
Also since the sound we want played is just a label we can change what sound should be played based on the environment

I.E. if the player walks on sand and then steps onto cobble they could both output "player-walk" but since
we know where it is from we can query what material the player just stepped on. (We could also do the query before
the notification, but this increases the amount of work the player animator has to do)
"""
from arcade import SpriteList, get_sprites_at_point

from notifications.notification import Notifier
from notifications.environment import EnivroArea
from common.data_loading import make_package_path_finder
from common.util import load_shared_sound

from arcade import get_window, load_sound
from enum import IntEnum
from pyglet.math import Vec2
from pyglet.media import Player

import notifications.data.audio as audio_src

get_audio_path = make_package_path_finder(audio_src, ".wav")
load_audio = lambda name: load_sound(get_audio_path(name))

class AudioChannel(IntEnum):
    GLOBAL = 0b0001
    SFX = 0b0010
    MUSIC = 0b0100
    GUI = 0b1000


class AudioListener:
    """
    We call it an Audio listener because it `listens` to where audio is played from, don't mind that it actually
    plays the audio.

    Normally this would be a generic base class which we would inherit for the player, global, etc.
    but for the demo I am assuming only the player is a listener
    """

    def __init__(self, environment: SpriteList[EnivroArea]):
        notif: Notifier = get_window().notifier

        notif.add_listener('play-audio', self.on_play_audio)

        self._players: list[Player] = list()
        self.environment: SpriteList[EnivroArea] = environment

        self.step_audio = {
            'a': load_shared_sound('blip_a'),
            'b': load_shared_sound('blip_c')
        }
        self.hurt_sound = load_shared_sound('blip_e')

    def on_play_audio(self, track: str, channel: AudioChannel, location: Vec2):
        match channel:
            case AudioChannel.GLOBAL:
                pass

            case AudioChannel.GUI:
                pass

            case AudioChannel.SFX:
                if track == 'player-step':
                    current_env = get_sprites_at_point(location, self.environment)
                    material = 'a' if not current_env else current_env[0].material
                    self._players.append(self.step_audio.get(material, self.step_audio['a']).play())
                elif track == 'player-hurt':
                    self._players.append(self.hurt_sound.play())

            case AudioChannel.MUSIC:
                pass

        self._players = list(filter(lambda p: p.playing, self._players))

    def on_update_volume(self, channel: AudioChannel, new_volume: AudioChannel):
        pass
