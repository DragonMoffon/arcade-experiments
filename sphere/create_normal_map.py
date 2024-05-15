from PIL import Image

from pyglet.math import Vec3

from common.data_loading import make_package_path_finder
import sphere.data as data

img_path = make_package_path_finder(data, "png")

img = Image.open(img_path("world_elev"))
normals = Image.new("RGBA", img.size)

for x in range(img.width):
    for y in range(1, img.height-1):
        s11 = img.getpixel((x, y))[0]

        s01 = img.getpixel(((x-1)%img.width, y))[0] / 255
        s21 = img.getpixel(((x+1)%img.width, y))[0] / 255

        s10 = img.getpixel((x, (y-1)%img.height))[0] / 255
        s12 = img.getpixel((x, (y+1)%img.height))[0] / 255

        va = Vec3(2.0, 0.0, (s21 - s01)).normalize()
        vb = Vec3(0.0, 2.0, (s12 - s10)).normalize()

        normal = va.cross(vb) * 0.5
        normal = Vec3(normal.x + 0.5, normal.y + 0.5, normal.z + 0.5)
        normals.putpixel((x, y), (int(255.0*normal.x), int(255.0*normal.y), int(-255*normal.z), 255))

normals.save(img_path("world_norm"))
