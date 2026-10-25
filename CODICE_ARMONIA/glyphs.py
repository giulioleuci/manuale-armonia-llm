from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment
_FONT = TTFont('/usr/share/fonts/truetype/freefont/FreeSerif.ttf')
_CMAP = _FONT.getBestCmap()
_GS = _FONT.getGlyphSet()
UPM = _FONT['head'].unitsPerEm

def glyph_ops(cp):
    pen = RecordingPen()
    _GS[_CMAP[cp]].draw(pen)
    return pen.value

def draw_glyph(c, cp, x, y, scale, fill=(0,0,0)):
    """Draw glyph outline at origin (x,y) with scale (pt per font unit)."""
    ops = glyph_ops(cp)
    p = c.beginPath()
    cur = None
    for op, args in ops:
        if op == 'moveTo':
            (pt,) = args; p.moveTo(x+pt[0]*scale, y+pt[1]*scale); cur = pt
        elif op == 'lineTo':
            (pt,) = args; p.lineTo(x+pt[0]*scale, y+pt[1]*scale); cur = pt
        elif op == 'curveTo':
            a,b,d = args
            p.curveTo(x+a[0]*scale,y+a[1]*scale,x+b[0]*scale,y+b[1]*scale,x+d[0]*scale,y+d[1]*scale); cur = d
        elif op == 'qCurveTo':
            pts = list(args)
            # TrueType implied on-curve handling
            if pts[-1] is None:
                raise ValueError('closed contour w/o on-curve not handled')
            for (q1, q2) in decomposeQuadraticSegment(pts):
                # convert quad (cur,q1,q2) to cubic
                c1 = (cur[0]+2/3*(q1[0]-cur[0]), cur[1]+2/3*(q1[1]-cur[1]))
                c2 = (q2[0]+2/3*(q1[0]-q2[0]), q2[1]+2/3*(q1[1]-q2[1]))
                p.curveTo(x+c1[0]*scale,y+c1[1]*scale,x+c2[0]*scale,y+c2[1]*scale,x+q2[0]*scale,y+q2[1]*scale)
                cur = q2
        elif op in ('closePath','endPath'):
            p.close()
    c.setFillColorRGB(*fill)
    c.drawPath(p, stroke=0, fill=1, fillMode=1)  # nonzero winding... 
