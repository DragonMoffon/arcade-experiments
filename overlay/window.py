from arcade import Window, draw_texture_rect, load_texture
from tkinter.filedialog import askopenfilename

class OveralyWindow(Window):

    def __init__(self, texture):
        super().__init__(1280, 720, "TEMPLATE", fullscreen=True, style=Window.WINDOW_STYLE_OVERLAY)
        self.overlay = texture


    def on_draw(self):
        self.clear()
        draw_texture_rect(self.overlay, self.rect)


def main():
    img = askopenfilename(title="Select Overlay Image", filetypes=[("Portable Network Graphics", "*.png")])
    win = OveralyWindow(load_texture(img))
    win.run()
