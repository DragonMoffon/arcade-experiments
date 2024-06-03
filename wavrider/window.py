from glob import glob
from tkinter.filedialog import askdirectory
import wave

import numpy as np
import pyglet.gui

from arcade import LRBT, Sound, Window, Text
from arcade.key import A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, SPACE, \
    UP, DOWN, BACKSPACE, DELETE, ENTER, \
    KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, \
    NUM_0, NUM_1, NUM_2, NUM_3, NUM_4, NUM_5, NUM_6, NUM_7, NUM_8, NUM_9
from arcade.types import Color
import arcade.color

from common.util import load_shared_sound

IRIS_PURPLE = Color.from_hex_string("9900B2")
IRIS_DARK = Color.from_hex_string("5D007E")
IRIS_HAIR = Color.from_hex_string("1A0024")
TEXT_OFFSET = 5
SHOW_LIMIT = 20
PANEL_START = 0.667
PANEL_CENTER = (1 - PANEL_START) / 2 + PANEL_START
FONT_NAME = "GohuFont 11 Nerd Font Mono"

letters = "abcdefghijklmnopqrstuvwxyz 01234567890123456789"
letter_keys = [A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, SPACE,
               KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9,
               NUM_0, NUM_1, NUM_2, NUM_3, NUM_4, NUM_5, NUM_6, NUM_7, NUM_8, NUM_9]
letter_map = {
    letters[idx]: letter_keys[idx] for idx in range(len(letters))
}


def gen_waveform(path: str, width: int, x: int = 0, y: int = 0, max_height = 100) -> list[tuple[float, float]]:
    with open(path, "rb") as f:
        wav = wave.open(f, "rb")
        sample_count = wav.getnframes()
        signal_wave = wav.readframes(sample_count)
    step = int(sample_count / width)
    samples = np.frombuffer(signal_wave, dtype=np.int16)[::step]
    frac = width / len(samples)
    multiplier = np.max(samples) / max_height
    return [(n * frac + x, float(s) / multiplier + y) for n, s in enumerate(samples)]


def get_panel_font_size(window: Window, s: str, max_size = 28) -> int:
    font_size = max_size
    width = window.width * (1 - PANEL_START)
    label = Text(s, window.width * PANEL_CENTER, window.height / 4,
                 font_name = FONT_NAME, font_size = font_size,
                 anchor_x = "center", anchor_y = "center",
                 align = "center", width = width,
                 multiline = True)
    if label.content_width > width:
        font_size = int(font_size / (label.content_width / width))
    return font_size


class RiderWindow(Window):
    def __init__(self):
        super().__init__(1280, 720, "WavRider")
        self.local_time = 0.0
        self.directory = None
        self._wavs: list[str] = []
        self.wavs: list[str] = self._wavs.copy()

        self.selected_index = 0

        self.directory_text = Text("[directory_name]", 5, self.height - TEXT_OFFSET,
                                   font_name = FONT_NAME, font_size = 20,
                                   anchor_x = "left", anchor_y = "top",
                                   align = "left", bold = True)

        self.wavs_before_text = Text("[files before]", 5, self.directory_text.bottom - TEXT_OFFSET,
                                     font_name = FONT_NAME, font_size = 20,
                                     anchor_x = "left", anchor_y = "top",
                                     align = "left", width = self.width * PANEL_START,
                                     multiline = True)

        self.wav_selected_text = Text("[file]", 5, self.wavs_before_text.bottom - TEXT_OFFSET,
                                      font_name = FONT_NAME, font_size = 20,
                                      anchor_x = "left", anchor_y = "top",
                                      align = "left", width = self.width * PANEL_START,
                                      multiline = True, color = IRIS_PURPLE)

        self.wavs_after_text = Text("[files after]", 5, self.wav_selected_text.bottom - TEXT_OFFSET,
                                    font_name = FONT_NAME, font_size = 20,
                                    anchor_x = "left", anchor_y = "top",
                                    align = "left", width = self.width * PANEL_START,
                                    multiline = True)

        self.search_box = Text("[type to search]", self.width - 5, self.directory_text.top,
                                font_name = FONT_NAME, font_size = 20,
                                anchor_x = "right", anchor_y = "top",
                                align = "right", bold = True, color = arcade.color.LIGHT_GRAY)

        self.panel_text = Text("[title]", self.width * PANEL_CENTER, self.height / 4,
                               font_name = FONT_NAME, font_size = 28,
                               anchor_x = "center", anchor_y = "center",
                               align = "center", width = self.width * (1 - PANEL_START),
                               multiline = True)

        self.prompt_text = Text("Choose a sound folder...", self.center_x, self.center_y,
                                font_name = FONT_NAME, font_size = 36,
                                anchor_x = "center", anchor_y = "center",
                                align = "center", width = self.width * (1 - PANEL_START),
                                multiline = True)

        self.asked_folder = False
        self.show_sound = False

        self.search_term = ""

        self.sound = None
        self.player = None
        self.waveform = []

        self.sfx: dict[str, arcade.Sound] = {s: load_shared_sound(s) for s in ("blip_a", "blip_c", "blip_e")}

        self.gui: pyglet.shapes.Batch = pyglet.shapes.Batch()
        self.text_input = pyglet.gui.TextEntry("", x=self.width-30.0, y=self.height-15.0, width=100.0, batch=self.gui)
        self.push_handlers(self.text_input)
        self._last_text = ""

    @property
    def selected_wav(self) -> str:
        return self.wavs[self.selected_index]

    def play_sound(self, s: str):
        self.sfx[s].play()

    def render_prompt(self):
        arcade.draw_rect_filled(LRBT(0, self.width, 0, self.height), IRIS_DARK)
        self.prompt_text.draw()

    def render_selected_wav(self):
        arcade.draw_rect_filled(LRBT(self.width * PANEL_START, self.width, 0, self.search_box.bottom - TEXT_OFFSET), IRIS_DARK)
        self.panel_text.draw()
        arcade.draw_line_strip(self.waveform[:11], arcade.color.YELLOW, 5)
        arcade.draw_line_strip(self.waveform[10:], arcade.color.WHITE, 5)

    def setup_selected_wav(self):
        if self.player:
            self.player.delete()

        path = self.directory + "/" + self.selected_wav
        self.show_sound = True
        self.sound = Sound(path)
        self.player = self.sound.play()

        stem = self.selected_wav.split("\\")[-1]
        self.panel_text.font_size = get_panel_font_size(self, stem)
        self.panel_text.text = stem

        WAVEFORM_START = self.width * PANEL_START + 50
        WAVEFORM_WIDTH = self.width - WAVEFORM_START - 50

        self.waveform = gen_waveform(path, WAVEFORM_WIDTH, WAVEFORM_START, self.height * 0.6666)

    def unsetup_selected_wav(self):
        self.show_sound = False
        if self.player:
            self.player.delete()

    def get_searched_wavs(self, term: str) -> list[str]:
        return [w for w in self._wavs if term in w.casefold()]

    def update_search(self):
        self.selected_index = 0
        self.wavs = self.get_searched_wavs(self.text_input.value)
        self.search_box.text = self.text_input.value if self.text_input.value else "[type to search]"
        self.update_wav_text()

    def ask_folder(self):
        self.directory = askdirectory()
        self.asked_folder = True
        self.directory_text.text = self.directory

    def get_wavs(self):
        self._wavs = glob("**/*.wav", root_dir = self.directory, recursive = True)
        self.wavs = self._wavs.copy()
        self.update_wav_text()

    def update_wav_text(self):
        # Clear text fields
        self.wavs_before_text.text = "[]"
        self.wav_selected_text.text = "[]"
        self.wavs_after_text.text = "[]"

        if not self.wavs:
            self.wavs_before_text.text = ""
            self.wav_selected_text.text = f"No files with '{self.search_term}' found!"
            self.wavs_after_text.text = ""
            return

        # Update text fields
        if self.selected_index != 0:
            self.wavs_before_text.text = "\n".join(self.wavs[:self.selected_index])
        self.wav_selected_text.text = self.wavs[self.selected_index]
        self.wavs_after_text.text = "\n".join(self.wavs[self.selected_index + 1:SHOW_LIMIT])

        # Positioning in the case that the selected item is the top item
        if self.selected_index == 0:
            self.wav_selected_text.y = self.directory_text.bottom - TEXT_OFFSET
            self.wavs_before_text.text = ""
        else:
            self.wavs_before_text.y = self.directory_text.bottom - TEXT_OFFSET
            self.wav_selected_text.y = self.wavs_before_text.bottom - TEXT_OFFSET
        self.wavs_after_text.y = self.wav_selected_text.bottom - TEXT_OFFSET

        self.unsetup_selected_wav()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == DOWN:
            if self.selected_index < min(len(self.wavs) - 1, SHOW_LIMIT - 1):
                self.selected_index += 1
                self.update_wav_text()
                self.play_sound("blip_a")
        elif symbol == UP:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_wav_text()
                self.play_sound("blip_a")
        elif symbol == DELETE:
            self.text_input.value = ""
        elif symbol == ENTER:
            self.setup_selected_wav()

    def on_update(self, delta_time: float):
        self.text_input.focus = True
        if self._last_text != self.text_input.value:
            self.update_search()
            if len(self._last_text) < len(self.text_input.value):
                self.play_sound("blip_c")
            else:
                self.play_sound("blip_e")
            self._last_text = self.text_input.value
        
        self.local_time += delta_time
        if not self.asked_folder and self.local_time > 1:
            self.ask_folder()
            self.get_wavs()

    def on_draw(self):
        self.clear(IRIS_HAIR)

        if not self.asked_folder:
            self.render_prompt()
            return

        self.directory_text.draw()
        self.wavs_before_text.draw()
        self.wav_selected_text.draw()
        self.wavs_after_text.draw()
        self.search_box.draw()

        if self.show_sound:
            self.render_selected_wav()


def main():
    win = RiderWindow()
    win.run()


if __name__ == "__main__":
    main()
