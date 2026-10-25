import os
from reportlab.pdfgen import canvas
from .engrave import draw_system, system_height, draw_blocks, draw_legend

def render_satb_snippet(chords, out_path, nacc=0, caps=None, dx=70, arrows=True, marks=None, width=None, legend=False):
    """
    Renders an SATB chord progression system to a tight-cropped PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    n = len(chords)
    x0 = 15
    # calculate layout width
    ks_width = 14 * abs(nacc) if nacc != 0 else 0
    xfirst = x0 + 4 + 22 + ks_width + 24 + (6 if nacc else 0)
    needed_content_w = (n - 0.35) * dx + 25
    x1 = xfirst + needed_content_w
    if width and width > x1 + 15:
        x1 = width - 15
    total_width = x1 + 15

    # calculate layout height
    nfig = max([len(ch.get('fig') or []) for ch in chords] + [1])
    hassub = any(ch.get('sub') for ch in chords)
    hascaps = bool(caps)
    top_margin = 35 if hascaps else 20
    body_h = system_height(nfig) + (14 if hassub else 0)
    leg_h = 25 if legend else 0
    total_height = top_margin + body_h + leg_h + 10

    ytop = total_height - top_margin

    c = canvas.Canvas(out_path, pagesize=(total_width, total_height))
    ybot = draw_system(c, x0, ytop, x1, chords, nacc=nacc, caps=caps, dx=dx, show_labels=True, final=True, arrows=arrows, marks=marks)
    if legend:
        draw_legend(c, x0, ybot - 10, width=total_width - 30)

    c.showPage()
    c.save()
    return out_path

def render_block_snippet(chords, out_path, nacc=0, clef='treble', dx=80, caps=None, width=None):
    """
    Renders single-staff chord blocks to a tight-cropped PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    n = len(chords)
    x0 = 15
    ks_width = 12 * abs(nacc) if nacc != 0 else 0
    xfirst = x0 + 4 + 22 + ks_width + 25
    x1 = xfirst + (n - 0.35) * dx + 20
    if width and width > x1 + 15:
        x1 = width - 15
    total_width = x1 + 15

    top_margin = 30 if caps else 18
    # Staff height 4*S=26, labels take ~40pt, ledger margin ~20pt
    body_h = 95
    total_height = top_margin + body_h + 10
    ytop = total_height - top_margin

    c = canvas.Canvas(out_path, pagesize=(total_width, total_height))
    draw_blocks(c, x0, ytop, x1, chords, nacc=nacc, clef=clef, dx=dx, caps=caps)
    c.showPage()
    c.save()
    return out_path
