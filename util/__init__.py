# flake8: noqa

from data_loading import make_package_path_finder

import arcade

from util.procedural_animator import *

import util.data as data

get_font_path = make_package_path_finder(data, "ttf")
get_sound_path = make_package_path_finder(data, "wav")
def load_font(name: str = "gohu"): arcade.load_font(get_font_path(name))
def load_sound(name: str = "blip_c"): return arcade.load_sound(get_sound_path(name))
