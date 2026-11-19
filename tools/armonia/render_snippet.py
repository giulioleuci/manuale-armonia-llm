import copy, os, itertools, subprocess, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from .engrave import draw_system, system_height, draw_blocks, draw_legend, layout_bass, draw_bass_system, ks_alt, layout_accs, ks_width
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black
from .music import LETTERS, parse
from .glyphs import FONTS

# Larghezza massima in punti PDF: i passaggi lunghi proseguono su piu' sistemi.
# Tutti gli esempi entrano in LaTeX alla stessa scala (\scalamusica in music_macros.tex).
SCALA = 0.8
LARGHEZZA_MAX = 423 / SCALA     # larghezza utile del box `esempio` (pt) a scala naturale
BASS_SYSTEM_STEP = 196
BASS_SUBTITLE = 'Basso da armonizzare a quattro voci'


def _validate_bass_exercises(exercises):
    if not exercises:
        raise ValueError('Serve almeno un basso')
    for exercise in exercises:
        if not -7 <= exercise.get('nacc', 0) <= 7:
            raise ValueError('Armatura non valida')
        layout_bass(exercise['bars'], 0, 12*mm)


def _bass_bars_per_system(nacc):
    prefix = 26 + ks_width(nacc) + 36
    return int((A4[0] - 24*mm - prefix) // (10+48*mm))


def render_bass_exercises(exercises, out_path, lilypond=True):
    """PDF A4 per armonizzare a mano: 12 mm per semiminima, 3 battute per sistema.
    Con lilypond=True genera anche [nome]_lilypond.pdf dal MusicXML (serve LilyPond)."""
    _validate_bass_exercises(exercises)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle(' – '.join(e['title'] for e in exercises))
    page = 0
    for exercise in exercises:
        bars = exercise['bars']
        nacc = exercise.get('nacc', 0)
        # Non comprimere la scala di scrittura se un'armatura richiede più spazio.
        per_system = _bass_bars_per_system(nacc)
        for start in range(0, len(bars), per_system*4):
            page += 1
            c.setFillColor(black)
            if start == 0:      # frontespizio: titolo e sottotitolo centrati
                c.setFont('GAR', 26)
                c.drawCentredString(A4[0]/2, A4[1]-16*mm, exercise['title'])
                c.setFont('GARI', 12)
                c.drawCentredString(A4[0]/2, A4[1]-22.5*mm, BASS_SUBTITLE)
            else:               # intestazione corrente
                c.setFont('GARI', 10)
                c.drawString(12*mm, A4[1]-14*mm, exercise['title'])
                c.setFont('GAR', 12)
                c.drawRightString(A4[0]-12*mm, A4[1]-14*mm, str(page))
            for row in range(4):
                i = start + row*per_system
                if i >= len(bars):
                    break
                chunk = bars[i:i+per_system]
                last = i+len(chunk) == len(bars)
                ytop = A4[1]-32*mm-row*BASS_SYSTEM_STEP
                c.setFont('GAR', 11)
                c.drawString(12*mm, ytop+12, str(i+1))
                draw_bass_system(c, 12*mm, ytop, chunk, nacc=nacc,
                                 beat_width=12*mm, first=i == 0, final=last,
                                 tie_in=i > 0 and bars[i-1][-1].get('tie', False),
                                 tie_out=not last and chunk[-1][-1].get('tie', False))
            c.showPage()
    c.save()
    xml = export_bass_musicxml(exercises, Path(out_path).with_suffix('.musicxml'))
    if lilypond:
        out = Path(out_path)
        render_musicxml_lilypond(xml, out.with_name(out.stem + '_lilypond.pdf'))
    return out_path


# Rigo superiore vuoto ma largo come nel PDF custom: 23 mm tra i righi, 27,5 mm tra i sistemi
# (1 spazio = 9,17 mm / 4; le distanze LilyPond vanno da linea centrale a linea centrale).
_LY_STILE = r'''
#(ly:font-config-add-directory "@FONTS@")
\layout {
  \context { \Staff
    \omit Rest
    \override AccidentalCautionary.parenthesized = ##f
    printKeyCancellation = ##f }
  % Nessuna armatura o tempo di cortesia a fine pagina tra un basso e il successivo.
  \context { \Score
    explicitKeySignatureVisibility = #end-of-line-invisible
    \override TimeSignature.break-visibility = #end-of-line-invisible }
  \context { \PianoStaff
    \remove Instrument_name_engraver
    \override StaffGrouper.staff-staff-spacing =
      #'((basic-distance . 14) (minimum-distance . 14) (padding . 1) (stretchability . 0)) }
}
\header { tagline = ##f }
\paper {
  #(define fonts (set-global-fonts #:roman "EB Garamond 12" #:factor (/ staff-height pt 20)))
  bookTitleMarkup = \markup \column {
    \fill-line { \fontsize #7 \fromproperty #'header:title }
    \vspace #0.3
    \fill-line { \italic \fontsize #1.5 \fromproperty #'header:subtitle }
  }
  % Quattro sistemi per pagina anche sotto il titolo, come nel PDF custom.
  top-margin = 9\mm
  bottom-margin = 9\mm
  markup-system-spacing = #'((basic-distance . 5) (padding . 2) (stretchability . 0))
  ragged-bottom = ##t
  oddHeaderMarkup = \markup \fill-line {
    \unless \on-first-page \italic \fromproperty #'header:title
    \unless \on-first-page \fromproperty #'page:page-number-string
  }
  evenHeaderMarkup = \oddHeaderMarkup
  system-system-spacing =
    #'((basic-distance . 16) (minimum-distance . 16) (padding . 1) (stretchability . 0))
  ragged-last-bottom = ##t
  indent = 0
}
'''


def render_musicxml_lilypond(musicxml_path, out_pdf):
    """Incide il MusicXML dei bassi con musicxml2ly + lilypond."""
    # musicxml2ly scarta le note print-object="no" e fonderebbe i due righi, quindi le pause
    # segnaposto restano visibili al convertitore e sono nascoste in LilyPond. Ogni pausa di
    # battuta diventa due minime: musicxml2ly unirebbe le pause in R1*3 spostando il titolo.
    tree = ET.parse(musicxml_path)
    for measure in tree.getroot().iter('measure'):
        for k, blank in enumerate(list(measure)):
            if blank.tag == 'note' and blank.get('print-object') == 'no':
                del blank.attrib['print-object']
                blank.find('rest').attrib.pop('measure', None)
                blank.find('duration').text = str(int(blank.findtext('duration')) // 2)
                measure.insert(k + 1, copy.deepcopy(blank))
    out_pdf = Path(out_pdf)
    with tempfile.TemporaryDirectory() as tmp:
        src, ly = Path(tmp, 'bassi.musicxml'), Path(tmp, 'bassi.ly')
        tree.write(src, encoding='utf-8', xml_declaration=True)
        subprocess.run(['musicxml2ly', '-o', str(ly), str(src)], check=True, capture_output=True)
        text = ly.read_text(encoding='utf-8')
        anchor = '% The score definition'      # dopo \paper e \layout di musicxml2ly, prima di \score
        if anchor not in text:
            raise RuntimeError('Output di musicxml2ly inatteso: stile LilyPond non applicabile')
        style = _LY_STILE.replace('@FONTS@', str(FONTS).replace('\\', '/').replace('"', '\\"'))
        ly.write_text(text.replace(anchor, style + anchor, 1), encoding='utf-8')
        subprocess.run(['lilypond', '-s', '--pdf', '-o', str(Path(tmp, 'bassi')), str(ly)],
                       check=True, capture_output=True)
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        out_pdf.write_bytes(Path(tmp, 'bassi.pdf').read_bytes())
    return out_pdf


def export_bass_musicxml(exercises, out_path):
    """Esporta gli stessi bassi in MusicXML, con il rigo superiore da completare."""
    _validate_bass_exercises(exercises)
    root = ET.Element('score-partwise', version='4.0')
    work = ET.SubElement(root, 'work')
    title = ' – '.join(e['title'] for e in exercises)
    ET.SubElement(work, 'work-title').text = title
    defaults = ET.SubElement(root, 'defaults')
    scaling = ET.SubElement(defaults, 'scaling')
    ET.SubElement(scaling, 'millimeters').text = str(26/mm)
    ET.SubElement(scaling, 'tenths').text = '40'
    page = ET.SubElement(defaults, 'page-layout')
    for tag, value in [('page-height', A4[1]), ('page-width', A4[0])]:
        ET.SubElement(page, tag).text = str(value/0.65)
    margins = ET.SubElement(page, 'page-margins', type='both')
    for tag in ('left-margin', 'right-margin', 'top-margin', 'bottom-margin'):
        ET.SubElement(margins, tag).text = str(12*mm/0.65)
    system = ET.SubElement(defaults, 'system-layout')
    ET.SubElement(system, 'system-distance').text = str((BASS_SYSTEM_STEP-118)/0.65)
    staff = ET.SubElement(defaults, 'staff-layout', number='2')
    ET.SubElement(staff, 'staff-distance').text = str(66/0.65)
    # Titolo e sottotitolo sulla prima pagina, come nel PDF custom (unità: decimi di spazio).
    for kind, text, y, size, style in [('title', title, 16, 26, 'normal'),
                                       ('subtitle', BASS_SUBTITLE, 22.5, 12, 'italic')]:
        credit = ET.SubElement(root, 'credit', page='1')
        ET.SubElement(credit, 'credit-type').text = kind
        ET.SubElement(credit, 'credit-words', {
            'default-x': str(A4[0]/2/0.65), 'default-y': str((A4[1]-y*mm)/0.65),
            'font-family': 'EB Garamond', 'font-size': str(size), 'font-style': style,
            'justify': 'center', 'valign': 'bottom'}).text = text
    part_list = ET.SubElement(root, 'part-list')
    score_part = ET.SubElement(part_list, 'score-part', id='P1')
    ET.SubElement(score_part, 'part-name').text = 'Basso da armonizzare'
    part = ET.SubElement(root, 'part', id='P1')
    for ei, exercise in enumerate(exercises):
        nacc = exercise.get('nacc', 0)
        per_system = _bass_bars_per_system(nacc)
        tied = False
        for bi, bar in enumerate(exercise['bars']):
            memory = {}
            measure = ET.SubElement(part, 'measure', number=str(bi+1))
            if bi == 0 or bi % per_system == 0:
                print_attrs = {}
                if ei or bi:
                    print_attrs['new-page' if bi % (per_system*4) == 0 else 'new-system'] = 'yes'
                ET.SubElement(measure, 'print', print_attrs)
            if bi == 0:
                attrs = ET.SubElement(measure, 'attributes')
                ET.SubElement(attrs, 'divisions').text = '2'
                ET.SubElement(ET.SubElement(attrs, 'key'), 'fifths').text = str(nacc)
                time = ET.SubElement(attrs, 'time', symbol='common')
                ET.SubElement(time, 'beats').text = '4'
                ET.SubElement(time, 'beat-type').text = '4'
                ET.SubElement(attrs, 'staves').text = '2'
                # Chiavi una sola volta: musicxml2ly assegnerebbe la chiave di basso anche al rigo 1.
                for number, sign, line in [('1', 'G', '2'), ('2', 'F', '4')] * (ei == 0):
                    clef = ET.SubElement(attrs, 'clef', number=number)
                    ET.SubElement(clef, 'sign').text = sign
                    ET.SubElement(clef, 'line').text = line
                if len(exercises) > 1:      # con un solo basso il titolo è già nell'intestazione
                    direction = ET.SubElement(measure, 'direction', placement='above')
                    ET.SubElement(ET.SubElement(direction, 'direction-type'), 'words').text = exercise['title']
            blank = ET.SubElement(measure, 'note', {'print-object': 'no', 'print-spacing': 'yes'})
            ET.SubElement(blank, 'rest', measure='yes')
            ET.SubElement(blank, 'duration').text = '8'
            ET.SubElement(blank, 'voice').text = '1'
            ET.SubElement(blank, 'staff').text = '1'
            ET.SubElement(ET.SubElement(measure, 'backup'), 'duration').text = '8'
            beat = 0
            for k, note in enumerate(bar):
                item = ET.SubElement(measure, 'note')
                letter, octave, alter, natural = parse(note['p'])
                pitch = ET.SubElement(item, 'pitch')
                ET.SubElement(pitch, 'step').text = LETTERS[letter]
                ET.SubElement(pitch, 'alter').text = str(alter)
                ET.SubElement(pitch, 'octave').text = str(octave)
                ET.SubElement(item, 'duration').text = str(int(note['dur']*2))
                ties = (['stop'] if tied else []) + (['start'] if note.get('tie') else [])
                for kind in ties:
                    ET.SubElement(item, 'tie', type=kind)
                ET.SubElement(item, 'voice').text = '2'
                ET.SubElement(item, 'type').text = {.5: 'eighth', 1: 'quarter', 2: 'half', 4: 'whole'}[note['dur']]
                needed = layout_accs([(0, note['p'], 0)], ks_alt(nacc), memory)[0] and not tied
                if natural or note.get('acc'):
                    ET.SubElement(item, 'accidental', {} if needed else {'cautionary': 'yes'}).text = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}[alter]
                if note['dur'] != 4:
                    ET.SubElement(item, 'stem').text = 'down'
                ET.SubElement(item, 'staff').text = '2'
                # Crome a coppie sullo stesso movimento, come in draw_bass_system.
                nxt = bar[k+1] if k+1 < len(bar) else None
                if note['dur'] == .5 and beat % 1 == 0 and nxt and nxt['dur'] == .5:
                    ET.SubElement(item, 'beam', number='1').text = 'begin'
                elif note['dur'] == .5 and beat % 1 and bar[k-1]['dur'] == .5:
                    ET.SubElement(item, 'beam', number='1').text = 'end'
                beat += note['dur']
                if ties or note.get('fermata'):
                    marks = ET.SubElement(item, 'notations')
                    for kind in ties:
                        ET.SubElement(marks, 'tied', type=kind)
                    if note.get('fermata'):
                        ET.SubElement(marks, 'fermata', type='upright')
                tied = bool(note.get('tie'))
            if bi == len(exercise['bars'])-1:
                ET.SubElement(ET.SubElement(measure, 'barline', location='right'), 'bar-style').text = 'light-heavy'
    ET.indent(root)
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    return out_path

def _label_w(ch):
    t = [(ch.get('rn'), 'DVB', 10.2), (ch.get('name'), 'DVB', 9), (ch.get('sub'), 'DV', 6.8), (ch.get('sub2'), 'DV', 6.8)]
    t += [(f, 'DVB', 8.6) for f in ch.get('fig') or []]
    return max(stringWidth(s or '', f, z) for s, f, z in t)

def _impagina(chords, caps, dx, xfirst, extra):
    """-> (dx, [(i0, i1), ...]): stringe dx fino al minimo leggibile, poi spezza in righe (meglio alle stanghette)"""
    n = len(chords)
    room = LARGHEZZA_MAX - xfirst - extra                  # spazio per (k - 0.35) * dx
    dxmin = min(dx, max(58, max(_label_w(c) for c in chords) + 8))
    fit = room / max(1, n - 0.35)
    if fit >= dxmin: return min(dx, fit), [(0, n)]
    per = int(room / dx + 0.35)

    def pen(b):     # costo di una interruzione prima dell'accordo b
        p = 0 if chords[b-1].get('bar') else (1 if not chords[b-1].get('conn') else 4)
        return p + 10 * any(i0 < b <= i1 for i0, i1, _ in caps or [])
    for L in range(-(-n // per), n + 1):
        best = None
        for bs in itertools.combinations(range(1, n), L - 1):
            cuts = (0,) + bs + (n,)
            lens = [b - a for a, b in zip(cuts, cuts[1:])]
            if max(lens) > per: continue
            cost = sum(map(pen, bs)) + 3 * (max(lens) - min(lens))
            if best is None or cost < best[0]: best = (cost, cuts)
        if best: return dx, list(zip(best[1], best[1][1:]))

def _righe(chords, caps, marks, righe):
    for i0, i1 in righe:
        cc = [c for a, b, t in caps or [] if (c := (max(a, i0) - i0, min(b, i1 - 1) - i0, t))[0] <= c[1]]
        mm = [(ci - i0,) + m[1:] for m in marks or [] if i0 <= (ci := m[0]) < i1]
        yield chords[i0:i1], cc or None, mm or None

def _larghezze(xfirst, extra, dx, righe):
    """x1 comune (riga piu' lunga) e dx di ciascuna riga, giustificata entro un allargamento di 1.3"""
    kmax = max(b - a for a, b in righe)
    x1 = xfirst + (kmax - 0.35) * dx + extra
    return x1, [min(dx * 1.3, (x1 - xfirst - extra) / max(1, b - a - 0.35)) for a, b in righe]

def render_satb_snippet(chords, out_path, nacc=0, caps=None, dx=70, arrows=True, marks=None, width=None, legend=False):
    """
    Renders an SATB chord progression (one or more systems) to a tight-cropped PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    x0 = 15
    ks_width = 14 * abs(nacc) if nacc != 0 else 0
    xfirst = x0 + 4 + 22 + ks_width + 24 + (6 if nacc else 0)
    dx, righe = _impagina(chords, caps, dx, xfirst, 25 + 15)
    x1, dxs = _larghezze(xfirst, 25, dx, righe)
    if width and width > x1 + 15:
        x1 = width - 15
    total_width = x1 + 15

    nfig = max([len(ch.get('fig') or []) for ch in chords] + [1])
    hassub = any(ch.get('sub') for ch in chords)
    top_margin = 46 if caps else 20
    line_h = top_margin + system_height(nfig) + (14 if hassub else 0)
    leg_h = 25 if legend else 0
    total_height = line_h * len(righe) + leg_h + 10

    c = canvas.Canvas(out_path, pagesize=(total_width, total_height))
    ytop = total_height
    for k, ((cs, cc, mm), d) in enumerate(zip(_righe(chords, caps, marks, righe), dxs)):
        ytop -= top_margin
        xr = min(x1, xfirst + (len(cs) - 0.35) * d + 25)
        ybot = draw_system(c, x0, ytop, xr, cs, nacc=nacc, caps=cc, dx=d, show_labels=True,
                           final=k == len(righe) - 1, arrows=arrows, marks=mm)
        ytop -= line_h - top_margin
    if legend:
        draw_legend(c, x0, ybot - 10, width=total_width - 30)
        ybot -= 25
    c.setCropBox((0, max(0, ybot - 4), total_width, total_height))   # niente margine vuoto sotto le sigle
    c.showPage()
    c.save()
    return out_path

def render_block_snippet(chords, out_path, nacc=0, clef='treble', dx=80, caps=None, width=None):
    """
    Renders single-staff (or grand-staff) chord blocks, one or more systems, to a tight-cropped PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    x0 = 15
    ks_width = 12 * abs(nacc) if nacc != 0 else 0
    xfirst = x0 + 4 + 22 + ks_width + 30
    dx, righe = _impagina(chords, caps, dx, xfirst, 20 + 15)
    x1, dxs = _larghezze(xfirst, 20, dx, righe)
    if width and width > x1 + 15:
        x1 = width - 15
    total_width = x1 + 15

    top_margin = 30 if caps else 18
    # Staff height 4*S=26, labels take ~40pt, ledger margin ~20pt
    body_h = 95 + 9.2 * (max([len(ch.get('fig') or []) for ch in chords] + [1]) - 1) + (61 + 21 if clef == 'grand' else 0)
    total_height = (top_margin + body_h) * len(righe) + 10

    c = canvas.Canvas(out_path, pagesize=(total_width, total_height))
    ytop = total_height
    for (cs, cc, _), d in zip(_righe(chords, caps, None, righe), dxs):
        ytop -= top_margin
        xr = min(x1, xfirst + (len(cs) - 0.35) * d + 20)
        ybot = draw_blocks(c, x0, ytop, xr, cs, nacc=nacc, clef=clef, dx=d, caps=cc)
        ytop -= body_h
    c.setCropBox((0, max(0, ybot - 4), total_width, total_height))
    c.showPage()
    c.save()
    return out_path
