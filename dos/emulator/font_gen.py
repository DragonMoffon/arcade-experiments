from arcade import Window, Text, gl, Camera2D, LBWH, XYWH
from PIL import Image, ImageDraw, ImageFont

CHAR_SIZE = 8, 16
encoding_str = (
'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'
'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F'
' !"#$%&\'()*+,-./'
'0123456789:;<=>?'
'@ABCDEFGHIJKLMNO'
R'PQRSTUVWXYZ[\]^_'
'`abcdefghijklmno'
'pqrstuvwxyz{|}~\x7f'
'ÇüéâäàåçêëèïîìÄÅ'
'ÉæÆôöòûùÿÖÜ¢£¥₧ƒ'
'áíóúñÑªº¿⌐¬½¼¡«»'
'░▒▓│┤╡╢╖╕╣║╗╝╜╛┐'
'└┴┬├─┼╞╟╚╔╩╦╠═╬╧'
'╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀'
'αßΓπΣσµτΦΘΩδ∞φε∩'
'≡±≥≤⌠⌡÷≈°∙·√ⁿ²■'
)
MAP = {
    c: b for c, b in zip(encoding_str, encoding_str.encode('cp437'))
}
MAP['ÿ'] = 0x98
IMAP = {
    b: c for c,b in MAP.items()
}

name = "MxPlus_IBM_CGA-2y"
with open(f'{name}.ttf', 'rb+') as fp:
    fnt = ImageFont.truetype(fp, 16)
img = Image.new('RGBA', (16 * CHAR_SIZE[0], 16 * CHAR_SIZE[1]))
draw = ImageDraw.Draw(img)
for char in range(255):
    x = char % 16 * CHAR_SIZE[0]
    y = (char // 16) * CHAR_SIZE[1]
    draw.text((x, y), IMAP[char], fill=(255, 255, 255, 255), font=fnt)
with open(f"{name}.png", "wb+") as fp:
    img.save(fp)