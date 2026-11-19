import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
from .music import *
from .glyphs import *

pdfmetrics.registerFont(RLTTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(RLTTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(RLTTFont('DVI', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(RLTTFont('DVBI', '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DVB', italic='DVI', boldItalic='DVBI')
# Testo dei bassi (titoli, numeri di battuta): lo stesso serif usato nella versione LilyPond.
pdfmetrics.registerFont(RLTTFont('GAR', str(FONTS / 'EBGaramond12-Regular.ttf')))
pdfmetrics.registerFont(RLTTFont('GARI', str(FONTS / 'EBGaramond12-Italic.ttf')))

S = 6.5            # staff space
H = S/2
GSC = 4*S/UPM      # pt per unità del font (SMuFL: 1 em = 4 spazi)
# Spessori e misure dagli engravingDefaults e dalle ancore di Bravura (in spazi del rigo).
HW = 1.18*S        # larghezza della testa nera
STEM_W = 0.12*S
STEM_DX = HW/2 - STEM_W/2      # dal centro della testa all'asse del gambo
STEMLEN = 3.5*S
LEDGER_W = 0.16*S
LEDGER_X = HW/2 + 0.4*S        # semiampiezza dei tagli addizionali
STAFF_W = 0.13*S
THIN_W, THICK_W, BAR_SEP = 0.16*S, 0.5*S, 0.4*S
BEAM_W = 0.5*S
VCOL = {'S': HexColor('#1f5fbf'), 'A': HexColor('#2e8b3d'), 'T': HexColor('#d9730d'), 'B': HexColor('#c0392b')}
VNAME = ['S','A','T','B']

VOICE_DIRECTIONS = {
    0: {'stem': +1, 'tie': +1},  # S: gambo in su (+1), legatura sopra (+1)
    1: {'stem': -1, 'tie': -1},  # A: gambo in giù (-1), legatura sotto (-1)
    2: {'stem': +1, 'tie': +1},  # T: gambo in su (+1), legatura sopra (+1)
    3: {'stem': -1, 'tie': -1},  # B: gambo in giù (-1), legatura sotto (-1)
}

def get_stem_direction(vi):
    """Restituisce la direzione del gambo per la voce vi (+1 in su, -1 in giù)."""
    return VOICE_DIRECTIONS[vi]['stem'] if isinstance(vi, int) else VOICE_DIRECTIONS[VNAME.index(vi)]['stem']

def get_tie_direction(vi):
    """Restituisce la direzione della legatura per la voce vi (+1 sopra, -1 sotto)."""
    return VOICE_DIRECTIONS[vi]['tie'] if isinstance(vi, int) else VOICE_DIRECTIONS[VNAME.index(vi)]['tie']
GAP = 5.4*S        # between treble bottom line and bass top line

SHARPS_ORDER = 'FCGDAEB'
FLATS_ORDER = 'BEADGCF'
KS_TREBLE_SH = ['F5','C5','G5','D5','A4','E5','B4']
KS_TREBLE_FL = ['B4','E5','A4','D5','G4','C5','F4']
KS_BASS_SH = ['F3','C3','G3','D3','A2','E3','B2']
KS_BASS_FL = ['B2','E3','A2','D3','G2','C3','F2']

def ks_alt(nacc):
    d = {}
    if nacc > 0:
        for L in SHARPS_ORDER[:nacc]: d[LETTERS.index(L)] = 1
    elif nacc < 0:
        for L in FLATS_ORDER[:-nacc]: d[LETTERS.index(L)] = -1
    return d

class Staff:
    def __init__(self, clef, ybottom):
        self.clef = clef; self.yb = ybottom
        self.base = step('E4') if clef == 'treble' else step('G2')
    def y(self, p):
        return self.yb + (step(p) - self.base) * H
    def rel(self, p): return step(p) - self.base
    def ledgers(self, p):
        r = self.rel(p); out = []
        if r <= -2:
            k = -2
            while k >= r: out.append(k); k -= 2
        elif r >= 10:
            k = 10
            while k <= r: out.append(k); k += 2
        return out
    def ly(self, rel): return self.yb + rel*H

# glyph e larghezza (in spazi) delle alterazioni
ACC = {'#': (SHARP, .996), 'n': (NATURAL, .672), 'b': (FLAT, .904), 'bb': (DOUBLE_FLAT, 1.644), '##': (DOUBLE_SHARP, .988)}

def draw_acc(c, kind, x, y, color=black):
    """x = left edge, y = note y (center of bowl / glyph)"""
    c.setFillColor(color)
    draw_glyph(c, ACC[kind][0], x, y, GSC)
    return acc_width(kind)

def acc_width(kind): return ACC[kind][1]*S

def ks_width(nacc):
    """Larghezza dell'armatura disegnata da draw_keysig."""
    return abs(nacc) * (acc_width('#' if nacc > 0 else 'b') + 1.8)

def head(c, x, y, filled=False, color=black):
    c.setFillColor(color)
    draw_glyph(c, NOTEHEAD_BLACK if filled else NOTEHEAD_HALF, x - HW/2, y, GSC)

def draw_brace(c, x, ytop, ybot):
    """Graffa SMuFL alta quanto il sistema, a sinistra di x."""
    sc = (ytop - ybot) / UPM            # il glyph è alto 1 em
    draw_glyph(c, BRACE, x - 0.277*UPM/4*sc - 0.3*S, ybot, sc)

def arrow(c, x1, y1, x2, y2, color, dashed=False, lw=1.15):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(lw)
    ang = math.atan2(y2-y1, x2-x1)
    hl = 4.6; hwid = 2.0
    bx, by = x2 - hl*math.cos(ang), y2 - hl*math.sin(ang)
    if dashed: c.setDash(2.2, 1.8)
    c.line(x1, y1, bx, by)
    c.setDash()
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(bx + hwid*math.sin(ang), by - hwid*math.cos(ang))
    p.lineTo(bx - hwid*math.sin(ang), by + hwid*math.cos(ang))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

def draw_tie(c, x1, y1, x2, y2, direction=+1, color=black, open_start=False, open_end=False):
    """Disegna una legatura di valore (tie) tra due note dello stesso pitch.
    direction: +1 sopra le note (S, T), -1 sotto le note (A, B).
    """
    c.saveState()
    c.setFillColor(color); c.setStrokeColor(color)
    xa = x1 if open_start else x1 + HW/2 + 0.1*S
    xb = x2 if open_end else x2 - HW/2 - 0.1*S
    dx = xb - xa
    if dx <= 0:
        c.restoreState()
        return
    y_off = 3.5 * direction
    ya = y1 + y_off
    yb = y2 + y_off
    sag = min(1.6*S, 0.6*S + 0.04*dx) * direction   # piu' alta se lunga
    mid_y = (ya + yb) / 2 + sag
    if open_start:
        ya += sag
    if open_end:
        yb += sag
    thick = 0.08*S * direction      # con il contorno: 0.1 spazi agli estremi, 0.22 al centro

    p = c.beginPath()
    p.moveTo(xa, ya)
    p.curveTo(xa + 0.2 * dx, mid_y + thick, xa + 0.8 * dx, mid_y + thick, xb, yb)
    p.curveTo(xa + 0.8 * dx, mid_y - thick, xa + 0.2 * dx, mid_y - thick, xa, ya)
    p.close()
    c.setLineWidth(0.1*S); c.setLineJoin(1)
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()

def text_c(c, x, y, t, font='DV', size=8, color=black):
    c.setFont(font, size); c.setFillColor(color); c.drawCentredString(x, y, t)

def draw_clef(c, clef, x, staff):
    c.setFillColor(black)
    if clef == 'treble': draw_glyph(c, G_CLEF, x, staff.yb + S, GSC)      # sulla linea del Sol
    else: draw_glyph(c, F_CLEF, x, staff.yb + 3*S, GSC)                   # sulla linea del Fa

def draw_keysig(c, nacc, x, staff):
    if nacc == 0: return x
    if staff.clef == 'treble': lst = KS_TREBLE_SH if nacc > 0 else KS_TREBLE_FL
    else: lst = KS_BASS_SH if nacc > 0 else KS_BASS_FL
    kind = '#' if nacc > 0 else 'b'
    for p in lst[:abs(nacc)]:
        w = draw_acc(c, kind, x, staff.y(p))
        x += w + 1.8
    return x

def draw_staff_lines(c, staff, x0, x1):
    c.setStrokeColor(black); c.setLineWidth(STAFF_W)
    for k in range(5):
        y = staff.yb + k*S
        c.line(x0, y, x1, y)

def layout_accs(notes, key_alt, memory):
    """notes: list of (idx, pitch, ypos). returns dict idx -> kind (or None), updates memory"""
    res = {}
    for idx, p, _ in notes:
        l, o, a, expl = parse(p)
        cur = memory.get((l, o), key_alt.get(l, 0))
        if a != cur or expl and a == 0 and cur != 0:
            res[idx] = {0:'n',1:'#',-1:'b',-2:'bb',2:'##'}[a]
            memory[(l, o)] = a
        else:
            res[idx] = None
    return res

def draw_system(c, x0, ytop, x1, chords, nacc=0, caps=None, dx=None, show_labels=True, final=True, arrows=True, marks=None, fig_gap=0):
    """Draw grand staff system. ytop = y of top line of treble staff. Returns y of bottom of the label area."""
    T = Staff('treble', ytop - 4*S)
    B = Staff('bass', ytop - 4*S - GAP - 4*S)
    draw_staff_lines(c, T, x0, x1); draw_staff_lines(c, B, x0, x1)
    c.setStrokeColor(black); c.setLineWidth(THIN_W)
    c.line(x0, T.yb+4*S, x0, B.yb)
    c.setFillColor(black); draw_brace(c, x0, T.yb+4*S, B.yb)
    # clefs & key signatures
    draw_clef(c, 'treble', x0+4, T); draw_clef(c, 'bass', x0+4, B)
    xk = x0 + 4 + 22
    xe1 = draw_keysig(c, nacc, xk, T); xe2 = draw_keysig(c, nacc, xk, B)
    xfirst = max(xe1, xe2) + 24 + (6 if nacc else 0)
    n = len(chords)
    dx = min(dx or 95, (x1 - xfirst - 18) / max(1, (n - 0.35)))
    xs = [xfirst + i*dx for i in range(n)]
    kalt = ks_alt(nacc)
    memT, memB = {}, {}
    info = []   # per chord: per voice head x, y, acc info
    active_ties = []   # list of (i, i+1, voice_idx)
    for i, ch in enumerate(chords):
        v = ch['v']
        # accidentals memory reset after barline
        if i > 0 and chords[i-1].get('bar'):
            memT.clear(); memB.clear()
        xc = xs[i]
        heads = {}
        # Rileva note legate con l'accordo successivo (due semiminime legate al posto della minima)
        if i < n - 1:
            nxt_v = chords[i+1]['v']
            explicit_ties = ch.get('ties', [])
            for k in range(4):
                if nxt_v[k] == v[k] and ch.get('conn') or k in explicit_ties or VNAME[k] in explicit_ties:
                    active_ties.append((i, i+1, k))
        for st, mem, vi in ((T, memT, (0,1)), (B, memB, (2,3))):
            up_i, dn_i = vi     # up stem voice, down stem voice
            hx = {up_i: xc, dn_i: xc}
            pu, pd = v[up_i], v[dn_i]
            if pu == pd:
                pass
            elif abs(step(pu) - step(pd)) == 1:
                hx[dn_i] = xc - HW + 0.8
            # accidentals (process top to bottom)
            notes = sorted([(vi_, v[vi_], st.y(v[vi_])) for vi_ in vi], key=lambda t: -t[2])
            accs = layout_accs(notes, kalt, mem)
            cols = []   # list of lists of y in column
            accx = {}
            act = list(vi)
            leftmost = min(hx[k] for k in act) - HW/2
            for idx, p, yy in notes:
                kind = accs[idx]
                if not kind: continue
                col = 0
                while True:
                    if col >= len(cols): cols.append([]); break
                    if all(abs(yy - y2) >= 5.6*H for y2 in cols[col]): break
                    col += 1
                cols[col].append(yy)
                accx[idx] = (kind, col)
            for idx, (kind, col) in accx.items():
                w = acc_width(kind)
                xl = leftmost - 3.2 - w - col*8.2
                draw_acc(c, kind, xl, st.y(v[idx]))
                heads.setdefault('accl', {})[idx] = xl
            # ledger lines
            led = set()
            for vi_ in act:
                for r in st.ledgers(v[vi_]): led.add(r)
            if led:
                lx0 = min(hx[k] for k in act) - LEDGER_X; lx1 = max(hx[k] for k in act) + LEDGER_X
                c.setStrokeColor(black); c.setLineWidth(LEDGER_W)
                for r in led: c.line(lx0, st.ly(r), lx1, st.ly(r))
            # heads and stems: sempre semiminime piene
            for vi_ in act:
                yy = st.y(v[vi_]); xx = hx[vi_]
                head(c, xx, yy, filled=True)
            c.setStrokeColor(black); c.setLineWidth(STEM_W)
            for vi_ in vi:
                direction = get_stem_direction(vi_)
                yy = st.y(v[vi_]); xx = hx[vi_]
                if direction > 0:
                    xs_ = xx + STEM_DX
                    ytip = yy + STEMLEN
                    c.line(xs_, yy + 0.8, xs_, ytip)
                else:
                    xs_ = xx - STEM_DX
                    ytip = yy - STEMLEN
                    c.line(xs_, yy - 0.8, xs_, ytip)
            for vi_ in vi: heads[vi_] = (hx[vi_], st.y(v[vi_]))
        info.append(heads)
        # barline after chord
        if ch.get('bar') or (i == n-1):
            xb = xc + dx*0.5 if i < n-1 else min(x1, xc + dx*0.55)
            if i == n-1: xb = x1
            if i == n-1 and final:
                draw_final_barline(c, x1, T.yb+4*S, B.yb)
            else:
                c.setStrokeColor(black); c.setLineWidth(THIN_W); c.line(xb, T.yb+4*S, xb, B.yb)
    # legature di valore (ties)
    for (ci, c_next, k) in active_ties:
        (xa, ya) = info[ci][k]
        (xb, yb) = info[c_next][k]
        tdir = get_tie_direction(k)
        draw_tie(c, xa, ya, xb, yb, direction=tdir)
    # arrows
    tied_set = {(ci, c_next, k) for (ci, c_next, k) in active_ties}
    if arrows:
        for i, ch in enumerate(chords[:-1]):
            if not ch.get('conn'): continue
            nxt = chords[i+1]
            for k in range(4):
                (xa, ya) = info[i][k]; (xb, yb) = info[i+1][k]
                x_start = xa + HW/2 + 2.4
                left = info[i+1].get('accl', {}).get(k)
                x_end = (left - 1.6) if left is not None else (xb - HW/2 - 2.4)
                col = VCOL[VNAME[k]]
                same = (ch['v'][k] == nxt['v'][k])
                if same:
                    if (i, i+1, k) not in tied_set:
                        arrow(c, x_start, ya, x_end, yb, col, dashed=True)
                else:
                    # shorten slightly vertical to avoid overlapping heads
                    arrow(c, x_start, ya, x_end, yb, col)
                a = (ch.get('ann') or {}).get(VNAME[k])
                if a:
                    mx, my = (x_start + x_end)/2, (ya + yb)/2
                    if (i, i+1, k) in tied_set and get_tie_direction(k) > 0: my += 8   # sopra la legatura
                    c.setFont('DVB', 6.2)
                    tw = c.stringWidth(a, 'DVB', 6.2)
                    c.setFillColor(white); c.setStrokeColor(white)
                    c.rect(mx - tw/2 - 1, my + 2.2, tw + 2, 7.2, stroke=0, fill=1)
                    c.setFillColor(col); c.drawCentredString(mx, my + 3.4, a)
    # marks (e.g. parallel fifths): (chord_i, vA, vB, text)
    if marks:
        for (ci, va, vb, txt) in marks:
            (xa, ya) = info[ci][va]; (xb, yb) = info[ci][vb]
            c.setStrokeColor(HexColor('#d62828')); c.setLineWidth(0.9); c.setDash(1.6, 1.4)
            xm = max(xa, xb) + HW/2 + 6
            c.line(xa + HW/2 + 2, ya, xm, ya); c.line(xm, ya, xm, yb); c.line(xm, yb, xb + HW/2 + 2, yb)
            c.setDash()
            if txt:
                c.setFont('DVB', 6.5); c.setFillColor(HexColor('#d62828'))
                c.drawString(xm + 2.5, (ya + yb)/2 - 2, txt)
    # labels
    ylab = B.yb - 5.0*S - fig_gap
    nfig = max([len(ch.get('fig') or []) for ch in chords] + [1])
    if show_labels:
        for i, ch in enumerate(chords):
            figs = ch.get('fig') or []
            if ch.get('rn'):                      # sigla: grado sopra, numerica sintetica sotto
                text_c(c, xs[i], ylab - 4, ch['rn'], 'DVB', 10.2)
            for k, f in enumerate(figs):
                text_c(c, xs[i], ylab - 15 - k*9.2, f, 'DVB', 8.6)
            if ch.get('sub'):
                text_c(c, xs[i], ylab - 15 - nfig*9.2 - 2, ch['sub'], 'DV', 6.8, HexColor('#555555'))
    # captions
    if caps:
        for (i0, i1, t) in caps:
            xa, xb = xs[i0] - 10, xs[i1] + 12
            yc = T.yb + 4*S + 4.2*S + 6
            c.setStrokeColor(HexColor('#888888')); c.setLineWidth(0.6)
            c.line(xa, yc - 4, xb, yc - 4)
            c.line(xa, yc - 4, xa, yc - 7); c.line(xb, yc - 4, xb, yc - 7)
            text_c(c, (xa+xb)/2, yc, t, 'DVB', 7.8, HexColor('#222222'))
    hassub = any(ch.get('sub') for ch in chords)
    return ylab - nfig*9.2 - (24 if hassub else 12)   # bottom y of the system block

def draw_final_barline(c, x1, ytop, ybot):
    """Stanghetta finale sottile-spessa che termina in x1."""
    c.setStrokeColor(black)
    c.setLineWidth(THIN_W); c.line(x1 - THICK_W - BAR_SEP - THIN_W/2, ytop, x1 - THICK_W - BAR_SEP - THIN_W/2, ybot)
    c.setLineWidth(THICK_W); c.line(x1 - THICK_W/2, ytop, x1 - THICK_W/2, ybot)

def system_height(nfig=2):
    return 4*S + GAP + 4*S + 5.0*S + nfig*9.2 + 26

def _nota_blocco(c, st, ps, xc, kalt, mem):
    """accidenti, tagli addizionali, teste e gambo di un blocco di note sul rigo st"""
    notes = sorted([(k, p, st.y(p)) for k, p in enumerate(ps)], key=lambda t: -t[2])
    accs = layout_accs(notes, kalt, mem)
    cols = []; accx = {}
    for idx, p, yy in notes:
        kind = accs[idx]
        if not kind: continue
        col = 0
        while True:
            if col >= len(cols): cols.append([]); break
            if all(abs(yy - y2) >= 5.6*H for y2 in cols[col]): break
            col += 1
        cols[col].append(yy); accx[idx] = (kind, col)
    for idx, (kind, col) in accx.items():
        w = acc_width(kind)
        draw_acc(c, kind, xc - HW/2 - 3.2 - w - col*8.2, st.y(ps[idx]))
    led = set()
    for p in ps:
        for r in st.ledgers(p): led.add(r)
    c.setStrokeColor(black); c.setLineWidth(LEDGER_W)
    for r in led: c.line(xc - LEDGER_X, st.ly(r), xc + LEDGER_X, st.ly(r))
    prev_shift = 0; prev = None
    for p in ps:
        sh = 0
        if prev is not None and step(p) - step(prev) == 1 and prev_shift == 0: sh = HW - 0.8
        head(c, xc + sh, st.y(p), filled=True)
        prev, prev_shift = p, sh
    ys = [st.y(p) for p in ps]
    up = sum(st.rel(p) for p in ps)/len(ps) < 4
    c.setStrokeColor(black); c.setLineWidth(STEM_W)
    if up: c.line(xc + STEM_DX, min(ys) + 0.8, xc + STEM_DX, max(ys) + STEMLEN)
    else: c.line(xc - STEM_DX, max(ys) - 0.8, xc - STEM_DX, min(ys) - STEMLEN)

def _fondo_sigle(chords, ylab):
    """y del bordo inferiore delle sigle di un sistema a blocchi (per ritagliare il PDF)"""
    nf = max([len(c.get('fig') or []) for c in chords] + [1])
    if any(c.get('sub2') for c in chords): return ylab - 14.2 - nf*9.2 - 12
    if any(c.get('sub') for c in chords): return ylab - 14.2 - nf*9.2 - 4
    return ylab - 11 - (nf - 1)*9.2 - 5

def draw_blocks_grand(c, x0, ytop, x1, chords, nacc=0, dx=None, caps=None):
    """Blocchi su sistema a due righi: dal Do centrale in su chiave di violino, sotto chiave di basso."""
    T = Staff('treble', ytop - 4*S)
    B = Staff('bass', ytop - 4*S - GAP - 4*S)
    draw_staff_lines(c, T, x0, x1); draw_staff_lines(c, B, x0, x1)
    c.setStrokeColor(black); c.setLineWidth(THIN_W)
    c.line(x0, T.yb+4*S, x0, B.yb)
    c.setFillColor(black); draw_brace(c, x0, T.yb+4*S, B.yb)
    draw_clef(c, 'treble', x0+4, T); draw_clef(c, 'bass', x0+4, B)
    xe = draw_keysig(c, nacc, x0+4+22, T); draw_keysig(c, nacc, x0+4+22, B)
    xfirst = xe + 30
    n = len(chords)
    dx = min(dx or 110, (x1 - xfirst - 20)/max(1, n - 0.35))
    kalt = ks_alt(nacc); mem = {}
    for i, ch in enumerate(chords):
        xc = xfirst + i*dx
        if i > 0 and chords[i-1].get('bar'): mem.clear()
        ps = sorted(ch['p'], key=lambda p: midi(p))
        alto = [p for p in ps if midi(p) >= 60]; basso = [p for p in ps if midi(p) < 60]
        if alto: _nota_blocco(c, T, alto, xc, kalt, mem)
        if basso: _nota_blocco(c, B, basso, xc, kalt, mem)
        ylab = B.yb - 6.4*S
        if ch.get('name'): text_c(c, xc, ylab, ch['name'], 'DVB', 9)
        figs = ch.get('fig') or []
        for k, f in enumerate(figs): text_c(c, xc, ylab - 11 - k*9.2, f, 'DVB', 8.6)
        if ch.get('rn'): text_c(c, xc, ylab - 12, ch['rn'], 'DVB', 9.5)
        ysub = ylab - 14.2 - max(len(figs), 1)*9.2
        if ch.get('sub'): text_c(c, xc, ysub, ch['sub'], 'DV', 6.8, HexColor('#555555'))
        if ch.get('sub2'): text_c(c, xc, ysub - 8, ch['sub2'], 'DV', 6.8, HexColor('#555555'))
        if ch.get('bar'):
            xb = xc + dx*0.5
            c.setStrokeColor(black); c.setLineWidth(THIN_W); c.line(xb, T.yb+4*S, xb, B.yb)
    c.setStrokeColor(black); c.setLineWidth(THIN_W)
    c.line(x1, T.yb+4*S, x1, B.yb)
    return _fondo_sigle(chords, B.yb - 6.4*S)

def draw_blocks(c, x0, ytop, x1, chords, nacc=0, clef='treble', dx=None, caps=None):
    """Single-staff chord blocks (whole notes). chords: dict(p=[pitches low->high], name='', rn='', sub='')"""
    if clef == 'grand': return draw_blocks_grand(c, x0, ytop, x1, chords, nacc=nacc, dx=dx, caps=caps)
    st = Staff(clef, ytop - 4*S)
    draw_staff_lines(c, st, x0, x1)
    c.setStrokeColor(black); c.setLineWidth(THIN_W); c.line(x0, st.yb, x0, st.yb+4*S)
    draw_clef(c, clef, x0+4, st)
    xe = draw_keysig(c, nacc, x0+4+22, st)
    xfirst = xe + 30
    n = len(chords)
    dx = min(dx or 110, (x1 - xfirst - 20)/max(1, n - 0.35))
    kalt = ks_alt(nacc); mem = {}
    # sigle sotto il punto piu' basso di teste e gambi in giu' del sistema (mai sovrapposte ai gambi)
    def _fondo(ps):
        ys = [st.y(p) for p in ps]
        return min(ys) - (STEMLEN if sum(st.rel(p) for p in ps)/len(ps) >= 4 else S)
    ylab = min(st.yb - 3.0*S, min(_fondo(ch['p']) for ch in chords) - 12)
    for i, ch in enumerate(chords):
        xc = xfirst + i*dx
        if i > 0 and chords[i-1].get('bar'): mem.clear()
        ps = sorted(ch['p'], key=lambda p: midi(p))
        _nota_blocco(c, st, ps, xc, kalt, mem)
        if ch.get('name'): text_c(c, xc, ylab, ch['name'], 'DVB', 9)
        figs = ch.get('fig') or []
        for k, f in enumerate(figs): text_c(c, xc, ylab - 11 - k*9.2, f, 'DVB', 8.6)
        if ch.get('rn'): text_c(c, xc, ylab - 12, ch['rn'], 'DVB', 9.5)
        ysub = ylab - 14.2 - max(len(figs), 1)*9.2
        if ch.get('sub'): text_c(c, xc, ysub, ch['sub'], 'DV', 6.8, HexColor('#555555'))
        if ch.get('sub2'): text_c(c, xc, ysub - 8, ch['sub2'], 'DV', 6.8, HexColor('#555555'))
        if ch.get('bar'):
            xb = xc + dx*0.5
            c.setStrokeColor(black); c.setLineWidth(THIN_W); c.line(xb, st.yb, xb, st.yb+4*S)
    c.setStrokeColor(black); c.setLineWidth(THIN_W)
    c.line(x1, st.yb, x1, st.yb+4*S)
    return _fondo_sigle(chords, ylab)

def layout_bass(bars, xfirst, beat_width, tie_out=False):
    """Bassi in 4/4: dur in semiminime; spazio anche per i movimenti tenuti."""
    if not bars or beat_width <= 0:
        raise ValueError('Servono battute e una spaziatura positiva')
    notes, ends = [], []
    x = xfirst
    for bar in bars:
        beat = 0
        for note in bar:
            if note['dur'] not in (.5, 1, 2, 4):
                raise ValueError('Durate ammesse: 0.5, 1, 2, 4 semiminime')
            parse(note['p'])
            notes.append((note, x + 10 + beat * beat_width, beat))
            beat += note['dur']
        if beat != 4:
            raise ValueError('Ogni battuta deve contenere quattro semiminime')
        x += 10 + 4 * beat_width
        ends.append(x)
    for i, (note, _, _) in enumerate(notes):
        if note.get('tie'):
            if i == len(notes) - 1:
                if not tie_out:
                    raise ValueError('Legatura senza nota successiva')
            elif parse(note['p'])[:3] != parse(notes[i+1][0]['p'])[:3]:
                raise ValueError('La legatura di valore richiede la stessa altezza')
    return notes, ends


def draw_bass_system(c, x0, ytop, bars, nacc=0, beat_width=34,
                     first=False, final=False, tie_in=False, tie_out=False):
    """Doppio rigo da completare a mano: solo il basso, gambi sempre in giù."""
    T = Staff('treble', ytop - 4*S)
    B = Staff('bass', T.yb - 66 - 4*S)
    xfirst = x0 + 26 + ks_width(nacc) + 36
    notes, ends = layout_bass(bars, xfirst, beat_width, tie_out=tie_out)
    x1 = ends[-1]
    c.setFillColor(black)
    for st in (T, B):
        draw_staff_lines(c, st, x0, x1)
        draw_clef(c, st.clef, x0+4, st)
        xe = draw_keysig(c, nacc, x0+26, st)
        if first:
            draw_glyph(c, TIME_COMMON, xe + 0.8*S, st.yb + 2*S, GSC)
    c.setStrokeColor(black)
    c.setLineWidth(THIN_W)
    c.line(x0, ytop, x0, B.yb)
    draw_brace(c, x0, ytop, B.yb)
    for xb in ends[:-1] if final else ends:
        c.line(xb, ytop, xb, B.yb)
    if final:
        draw_final_barline(c, x1, ytop, B.yb)

    mem, kalt, points = {}, ks_alt(nacc), []
    for i, (note, x, beat) in enumerate(notes):
        if beat == 0:
            mem.clear()
        y = B.y(note['p'])
        kind = layout_accs([(0, note['p'], y)], kalt, mem)[0]
        tied = notes[i-1][0].get('tie') if i else tie_in
        if tied:
            kind = None
        if note.get('acc'):
            kind = {-2: 'bb', -1: 'b', 0: 'n', 1: '#', 2: '##'}[parse(note['p'])[2]]
        if kind:
            draw_acc(c, kind, x - HW/2 - 0.3*S - acc_width(kind), y)
        hw = .844*S if note['dur'] == 4 else HW/2
        c.setStrokeColor(black)
        c.setLineWidth(LEDGER_W)
        for r in B.ledgers(note['p']):
            c.line(x-hw-0.4*S, B.ly(r), x+hw+0.4*S, B.ly(r))
        c.setFillColor(black)
        if note['dur'] == 4:
            draw_glyph(c, NOTEHEAD_WHOLE, x-hw, y, GSC)
        else:
            head(c, x, y, filled=note['dur'] <= 1)
        if note.get('fermata'):
            draw_glyph(c, FERMATA_ABOVE, x - 1.21*S, max(y + 1.2*S, B.yb + 4.6*S), GSC)
        points.append((x, y))

    c.setLineWidth(STEM_W)
    i = 0
    while i < len(notes):
        note, _, beat = notes[i]
        x, y = points[i]
        stemx = x - STEM_DX
        if (note['dur'] == .5 and beat % 1 == 0 and i+1 < len(notes)
                and notes[i+1][0]['dur'] == .5 and notes[i+1][2] == beat+.5):
            xn, yn = points[i+1]
            xn -= STEM_DX
            # Travatura inclinata come le note, al massimo di uno spazio; gambi lunghi almeno STEMLEN.
            slope = max(-S, min(S, (yn - y) / 2))
            tl = min(y, yn - slope) - STEMLEN
            c.line(stemx, y - .168*S, stemx, tl)
            c.line(xn, yn - .168*S, xn, tl + slope)
            p = c.beginPath()
            p.moveTo(stemx - STEM_W/2, tl)
            p.lineTo(xn + STEM_W/2, tl + slope)
            p.lineTo(xn + STEM_W/2, tl + slope + BEAM_W)
            p.lineTo(stemx - STEM_W/2, tl + BEAM_W)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
            i += 2
            continue
        if note['dur'] != 4:
            c.line(stemx, y - .168*S, stemx, y - STEMLEN)
            if note['dur'] == .5:      # ancora stemDownSW di flag8thDown
                draw_glyph(c, FLAG8_DOWN, stemx - STEM_W/2, y - STEMLEN - .132*S, GSC)
        i += 1
    for i, (note, _, _) in enumerate(notes):
        if note.get('tie'):
            xa, ya = points[i]
            xb, yb = points[i+1] if i+1 < len(points) else (x1-2, ya)
            draw_tie(c, xa, ya, xb, yb, direction=+1, open_end=i == len(points)-1)
    if tie_in:
        x, y = points[0]
        draw_tie(c, xfirst-12, y, x, y, direction=+1, open_start=True)
    return x1


def draw_legend(c, x, y, width=770):
    """Legend for voices and arrows."""
    c.setFont('DVB', 8); c.setFillColor(black)
    items = [('S','Soprano'),('A','Contralto'),('T','Baritono (tenore)'),('B','Basso')]
    xx = x; yy = y
    for k, nm in items:
        w = 31 + c.stringWidth(nm, 'DVB', 8) + 18
        if xx + w > x + width: xx = x; yy -= 14
        arrow(c, xx, yy+2.5, xx+26, yy+2.5, VCOL[k])
        c.setFillColor(VCOL[k]); c.setFont('DVB', 8); c.drawString(xx+31, yy, nm)
        xx += w
    txt = 'tratteggiata = nota tenuta (voce ferma)'
    w = 31 + c.stringWidth(txt, 'DV', 8)
    if xx + w > x + width: xx = x; yy -= 14
    arrow(c, xx, yy+2.5, xx+26, yy+2.5, HexColor('#555555'), dashed=True)
    c.setFillColor(HexColor('#444444')); c.setFont('DV', 8); c.drawString(xx+31, yy, txt)
