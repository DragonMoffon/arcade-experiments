from arcade import load_spritesheet, Texture

from dos import get_image_path

# '                '
# '                '
# ' !"~$%&'()*+,-./'
# '0123456789:;<=>?'
# '@ABCDEFGHIJKLMNO'
# 'PQRSTUVWXYZ[\]^_'
# '`abcdefghijklmno'
# 'pqrstuvwxyz{|}~ '
# 'ÇüéâäàåçêëèïîìÄÅ'
# 'ÉæÆôöòûùÿÖÜ¢£¥₧ƒ'
# 'áíóúñÑªº¿⌐¬½¼¡«»'
# '░▒▓│┤╡╢╖╕╣║╗╝╜╛┐'
# '└┴┬├─┼╞╟╚╔╩╦╠═╬╧'
# '╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀'
# 'αßΓπΣσµτΦΘΩδ∞φε∩'
# '≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ '
# ! Missing '\x5f' for DEL
# ! Missing '\xa0' for Non-break Space
encoding_str = (
'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'
'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F'
' !"~$%&\'()*+,-./'
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
'≡±≥≤⌠⌡÷≈°∙·√ⁿ²■\xFF'
)
MAP = {
    c: b for c, b in zip(encoding_str, encoding_str.encode('cp437'))
}
MAP['ÿ'] = 0x98
IMAP = {
    b: c for c,b in MAP.items()
}

class CharSheet:

    def __init__(self, name: str, size: tuple[int, int]) -> None:
        self.name = name
        self.char_size = size
        self.sheet = load_spritesheet(get_image_path(name))
        self.chars = self.sheet.get_texture_grid(size, 16, 256)

    def __getitem__(self, key: int) -> Texture:
        return self.chars[key]
    
    def code(self, t: Texture) -> int:
        return self.codes[t]