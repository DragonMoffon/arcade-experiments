from random import random, choices
from typing import Callable

from arcade.experimental.input import MouseButtons, Keys
from arcade import (
    Sound,
    SpriteSolidColor,
    Sprite,
    SpriteList,
    Rect,
    XYWH,
    Text,
    draw_rect_outline,
    draw_rect_filled,
    draw_circle_outline,
    draw_lines,
    draw_point,
    MOUSE_BUTTON_LEFT,
    load_texture
)

from common.util import ProceduralAnimator, load_shared_sound
from common.data_loading import make_package_path_finder
from common.experimentwindow import ExpWin

from pool.pool import Pool
import pool.data as data

get_png_path = make_package_path_finder(data, 'png')
get_texture = lambda name: load_texture(get_png_path(name))

SPRITE_COUNT = 100
ANIMATOR_COUNT = 20

SPEEDS = (100, 1000)

RESPAWN_TIME = 1.0

GRAVITY_MAX = 200.0

LANE_FRACTION = 1.0 / 4.0


def generate_notes():
    t = 0.0
    lanes = (0, 1, 2, 3)  # lanes 1-4 with 5 being a note-speed event
    weights = (1.0, 1.0, 1.0, 1.0)
    loop = True
    yield 0, t
    while loop:
        lane = choices(lanes, weights)[0]
        t += 0.5
        loop = (yield lane, t)
    yield None


def pick_point_in_rect(rect: Rect) -> tuple[float, float]:
    return rect.left + random() * rect.width, rect.bottom + random() * rect.height


def pick_point_along_rect(rect: Rect, d_x: float, d_y: float) -> tuple[float, float]:
    along_y = choices((True, False), weights=(abs(d_x), abs(d_y)))
    print(along_y)
    if along_y:
        x = rect.left + random() * rect.width
        if d_y > 0:
            y = rect.bottom
        else:
            y = rect.top
        return x, y
    y = rect.bottom + random() * rect.height
    if d_x > 0:
        x = rect.left
    else:
        x = rect.right

    return x, y


class PoolWindow(ExpWin):

    def __init__(self, show_fps: bool):
        super().__init__(1280, 720, update_rate=1/1000)
        self._note_gen = generate_notes()

        self.show_fps(show_fps)

        self._textures = (
            get_texture('normal-1'),
            get_texture('normal-2'),
            get_texture('normal-3'),
            get_texture('normal-4'),
            get_texture('default')
        )

        self._control_sound: Sound = load_shared_sound('blip_e')
        self._deposit_sound: Sound = load_shared_sound('blip_a')
        self._get_sound: Sound = load_shared_sound('blip_c')

        self._fall_bounds: Rect = XYWH(self.center_x, self.center_y, 600, 600)
        self._fall_cut_bounds: Rect = XYWH(self.center_x, self.center_y, 650, 650)

        self._deposit_bounds: Rect = XYWH(200, self.center_y, 150, 350)
        self._deposit_visual: Rect = XYWH(200, self.center_y, 200, 400)

        self._note_speed: float = 100.0

        sprites = list(Sprite(self._textures[-1], 0.2, *pick_point_in_rect(self._deposit_bounds)) for _ in range(SPRITE_COUNT))
        self._sprites: SpriteList = SpriteList()
        self._sprites.extend(sprites)
        self._sprite_pool: Pool[Sprite] = Pool(sprites)

        self._active_picker: Callable[[float, float, float, float], None] = None

        self._t = 0.0

        self._next_note = next(self._note_gen)
        self._next_speed_time = self._t + 5.0
        self._next_note_speed: float = 100 + (900 - (self._note_speed - 100))
        self._t_offset: float = (self._fall_bounds.height + 25) / self._note_speed

        self._time_text: Text = Text(f'{self._t: .3f}', x=self._fall_bounds.right + 5, y=self._fall_bounds.y,
                                     anchor_x='left', anchor_y='center')

    def on_update(self, delta_time: float):
        # `gravity` here is just velocity not acceleration, but eh we could use the sprite's change x and y ;-;
        self._t += delta_time
        self._time_text.text = f'{self._t: .3f}'

        next_speed_y = self._fall_bounds.bottom + (self._next_speed_time - self._t) * self._note_speed
        if next_speed_y < self._fall_cut_bounds.top:
            # All notes that get spawned after the note speed change should account for it
            top_t = self._next_speed_time + (self._fall_cut_bounds.top - next_speed_y) / self._next_note_speed
        else:
            # All notes that get spawned before the note speed change should use the note_speed
            top_t = self._t + (self._fall_cut_bounds.top - self._fall_bounds.bottom) / self._note_speed

        while top_t >= self._next_note[-1] and self._sprite_pool.has_free_slot():
            lane, t = self._next_note
            sprite = self._sprite_pool.get()
            x = self._fall_bounds.left + LANE_FRACTION * self._fall_bounds.width * (0.5 + lane)
            if t < self._next_speed_time:
                y = self._fall_bounds.bottom + (t - self._t) * self._note_speed
            else:
                y = next_speed_y + (t - self._next_speed_time) * self._next_note_speed

            sprite.texture = self._textures[lane]
            sprite.position = x, y
            sprite.t = t
            # self._get_sound.play()
            self._next_note = self._note_gen.send(True)

        for sprite in self._sprite_pool.given_items:
            t = sprite.t
            if t < self._next_speed_time:
                y = self._fall_bounds.bottom + (t - self._t) * self._note_speed
            else:
                y = next_speed_y + (t - self._next_speed_time) * self._next_note_speed
            sprite.center_y = y

            if y <= self._fall_bounds.bottom:
                self._sprite_pool.give(sprite)
                sprite.position = pick_point_in_rect(self._deposit_bounds)
                sprite.texture = self._textures[-1]
                self._deposit_sound.play(0.05)
                print(f'{(self._t - sprite.t) * 1000: .0f}')

        if self._t >= self._next_speed_time:
            print('switched')
            self._next_speed_time += 15.0
            self._note_speed = self._next_note_speed
            self._next_note_speed = 100 + (900 - (self._note_speed - 100))
            self._t_offset = (self._fall_bounds.height + 25) / self._note_speed

    def on_draw(self):
        self.clear()

        draw_rect_outline(self._fall_bounds, (255, 255, 255, 255))
        next_speed_y = self._fall_bounds.bottom + (self._next_speed_time - self._t) * self._note_speed
        draw_lines(
            (
                (self._fall_cut_bounds.left, self._fall_cut_bounds.top), (self._fall_cut_bounds.right, self._fall_cut_bounds.top),
                (self._fall_cut_bounds.left, self._fall_cut_bounds.bottom), (self._fall_cut_bounds.right, self._fall_cut_bounds.bottom),
                (self._fall_cut_bounds.left, next_speed_y), (self._fall_cut_bounds.right, next_speed_y)
            ),
            (255, 0, 0, 255)
        )
        l = self._fall_bounds.left
        w = self._fall_bounds.width
        draw_lines(
            (
                (l + LANE_FRACTION * w, self._fall_bounds.top), (l + LANE_FRACTION * w, self._fall_bounds.bottom),
                (l + LANE_FRACTION * 2 * w, self._fall_bounds.top), (l + LANE_FRACTION * 2 * w, self._fall_bounds.bottom),
                (l + LANE_FRACTION * 3 * w, self._fall_bounds.top), (l + LANE_FRACTION * 3 * w, self._fall_bounds.bottom),
            ),
            (100, 100, 100, 255)
        )
        draw_rect_outline(self._deposit_visual, (255, 255, 255, 255))

        self._sprites.draw(pixelated=True)
        self._time_text.draw()


def main(show_fps: bool):
    win = PoolWindow(show_fps)
    win.run()
