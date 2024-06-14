from random import random, choices

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
    draw_point,
    MOUSE_BUTTON_RIGHT
)

from common.util import ProceduralAnimator, load_shared_sound
from common.experimentwindow import ExpWin

from pool.pool import Pool


SPRITE_COUNT = 100
ANIMATOR_COUNT = 20

RESPAWN_TIME = 1.0

GRAVITY_MAX = 200.0


def pick_point_in_rect(rect: Rect) -> tuple[float, float]:
    return rect.left + random() * rect.width, rect.bottom + random() * rect.height


def pick_point_along_rect(rect: Rect, d_x: float, d_y: float) -> tuple[float, float]:
    along_y = choices((True, False), weights=(abs(d_x), abs(d_y)))
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
        super().__init__(1280, 720)
        self.show_fps(show_fps)

        self._control_sound: Sound = load_shared_sound('blip_e')
        self._deposit_sound: Sound = load_shared_sound('blip_a')
        self._get_sound: Sound = load_shared_sound('blip_c')

        self._fall_bounds: Rect = XYWH(self.center_x, self.center_y, 600, 600)
        self._fall_cut_bounds: Rect = XYWH(self.center_x, self.center_y, 650, 650)

        self._deposit_bounds: Rect = XYWH(200, self.center_y, 150, 350)
        self._deposit_visual: Rect = XYWH(200, self.center_y, 200, 400)

        self._gravity: float = 100.0
        self._gravity_dir: tuple[float, float] = 0.0, -1.0

        sprites = list(SpriteSolidColor(50, 50, *pick_point_in_rect(self._deposit_bounds)) for _ in range(SPRITE_COUNT))
        self._sprites: SpriteList = SpriteList()
        self._sprites.extend(sprites)
        self._sprite_pool: Pool[Sprite] = Pool(sprites)

        self._respawn_timer: float = 0.0

        self._slider_rect: Rect = XYWH(self.width-200, self.center_y - GRAVITY_MAX/2.0 - 50, 10, GRAVITY_MAX+10)
        self._slider_text: Text = Text(f'{self._gravity}', self._slider_rect.right + 10, self._slider_rect.y, anchor_x='left', anchor_y='center')

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        button = MouseButtons(button)
        match button:
            case MouseButtons.LEFT:
                if self._fall_bounds.point_in_rect((x, y)) and self._sprite_pool.has_free_slot():
                    sprite = self._sprite_pool.get()
                    sprite.position = (x, y)
                    self._control_sound.play()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons & MOUSE_BUTTON_RIGHT:
            self._gravity = max(0.0, min(GRAVITY_MAX, self._gravity + dy))
            self._slider_text.text = f'{self._gravity}'
            self._control_sound.play(0.1)

    def on_update(self, delta_time: float):
        # `gravity` here is just velocity not acceleration, but eh we could use the sprite's change x and y ;-;
        g = self._gravity * delta_time
        gravity = self._gravity_dir[0] * g, self._gravity_dir[1] * g
        for sprite in self._sprite_pool.given_items:
            o_pos = sprite.position
            n_pos = sprite.position = o_pos[0] + gravity[0], o_pos[1] + gravity[1]

            if not self._fall_cut_bounds.point_in_rect(n_pos):
                self._sprite_pool.give(sprite)
                sprite.position = pick_point_in_rect(self._deposit_bounds)
                self._deposit_sound.play()

        self._respawn_timer += delta_time
        if self._respawn_timer >= RESPAWN_TIME:
            self._respawn_timer -= RESPAWN_TIME

            if self._sprite_pool.has_free_slot():
                sprite = self._sprite_pool.get()
                sprite.position = pick_point_along_rect(self._fall_bounds, *self._gravity_dir)
                self._get_sound.play()

    def on_draw(self):
        self.clear()

        draw_rect_outline(self._fall_bounds, (255, 255, 255, 255))
        draw_rect_outline(self._fall_cut_bounds, (255, 0, 0, 255))
        draw_rect_outline(self._deposit_visual, (255, 255, 255, 255))

        draw_rect_filled(self._slider_rect, (100, 100, 100, 255))
        draw_point(self._slider_rect.x, self._slider_rect.bottom + 5 + self._gravity, (255, 255, 255, 255), 10)
        self._slider_text.draw()

        self._sprites.draw(pixelated=True)


def main(show_fps: bool):
    win = PoolWindow(show_fps)
    win.run()
