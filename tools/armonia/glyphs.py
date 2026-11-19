"""Simboli musicali dal font SMuFL Bravura (Steinberg, licenza OFL: fonts/OFL-Bravura.txt)."""
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

FONTS = Path(__file__).with_name('fonts')     # Bravura ed EB Garamond, licenza OFL
_FONT = TTFont(FONTS / 'Bravura.otf')
_CMAP = _FONT.getBestCmap()
_GS = _FONT.getGlyphSet()
UPM = _FONT['head'].unitsPerEm      # SMuFL: 1 em = 4 spazi del rigo

# Codici SMuFL usati dal motore.
NOTEHEAD_BLACK, NOTEHEAD_HALF, NOTEHEAD_WHOLE = 0xE0A4, 0xE0A3, 0xE0A2
G_CLEF, F_CLEF, TIME_COMMON, BRACE = 0xE050, 0xE062, 0xE08A, 0xE000
FLAT, NATURAL, SHARP, DOUBLE_SHARP, DOUBLE_FLAT = 0xE260, 0xE261, 0xE262, 0xE263, 0xE264
FLAG8_DOWN, FERMATA_ABOVE = 0xE241, 0xE4C0


@lru_cache(None)
def glyph_ops(cp):
    pen = RecordingPen()
    _GS[_CMAP[cp]].draw(pen)
    return tuple(pen.value)


def draw_glyph(c, cp, x, y, scale, sy=None):
    """Disegna il glyph con origine SMuFL in (x, y); scale in pt per unità del font.
    sy facoltativo per allungare in verticale (graffa). Usa il colore di riempimento corrente."""
    c.saveState()
    c.translate(x, y)
    c.scale(scale, sy or scale)
    p = c.beginPath()
    for op, args in glyph_ops(cp):     # Bravura è CFF: solo segmenti cubici
        if op == 'moveTo':
            p.moveTo(*args[0])
        elif op == 'lineTo':
            p.lineTo(*args[0])
        elif op == 'curveTo':
            (a, b, d) = args
            p.curveTo(*a, *b, *d)
        elif op in ('closePath', 'endPath'):
            p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
