import os
from engrave import *
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
ORIENT = os.environ.get('PDF_ORIENT', 'orizzontale')
PORTRAIT = ORIENT == 'verticale'
PW, PH = (595, 842) if PORTRAIT else (842, 595)
M = 36
ST = {
 'body': ParagraphStyle('body', fontName='DV', fontSize=9, leading=12.6, alignment=TA_LEFT),
 'small': ParagraphStyle('small', fontName='DV', fontSize=8, leading=11, textColor=HexColor('#333333')),
 'h2': ParagraphStyle('h2', fontName='DVB', fontSize=12.5, leading=16, textColor=HexColor('#12355b'), spaceAfter=2),
 'h3': ParagraphStyle('h3', fontName='DVB', fontSize=10, leading=13, textColor=HexColor('#12355b')),
 'cell': ParagraphStyle('cell', fontName='DV', fontSize=8.2, leading=10.4),
 'cellb': ParagraphStyle('cellb', fontName='DVB', fontSize=8.2, leading=10.4),
}
class Doc:
    def __init__(self, path, title, subtitle):
        folder = os.path.join(os.path.dirname(path), ORIENT)
        os.makedirs(folder, exist_ok=True)
        self.c = canvas.Canvas(os.path.join(folder, os.path.basename(path)), pagesize=(PW, PH))
        self.c.setTitle(title); self.c.setAuthor('Appunti di armonia')
        self.title = title; self.sub = subtitle; self.n = 0
        self.y = 0
    def page(self, heading=None):
        if self.n: self.footer(); self.c.showPage()
        self.n += 1
        c = self.c
        c.setFillColor(HexColor('#12355b')); c.rect(0, PH-34, PW, 34, stroke=0, fill=1)
        c.setFillColor(white); c.setFont('DVB', 11); c.drawString(M, PH-22, self.title)
        c.setFont('DV', 8.5); c.drawRightString(PW-M, PH-22, self.sub)
        self.y = PH - 34 - 22
        if heading:
            self.h(heading, 'h2')
    def footer(self):
        c = self.c; c.setFillColor(HexColor('#777777')); c.setFont('DV', 7.5)
        c.drawString(M, 18, 'Esempi a 4 voci in disposizione late (aperta): soprano e contralto in chiave di violino, baritono e basso in chiave di basso.')
        c.drawRightString(PW-M, 18, f'pag. {self.n}')
    def p(self, text, style='body', w=None, x=None):
        w = w or (PW - 2*M); x = M if x is None else x
        para = Paragraph(text, ST[style]); _, h = para.wrap(w, 1000)
        para.drawOn(self.c, x, self.y - h); self.y -= h + 4
        return h
    def h(self, text, style='h3'):
        self.p(text, style)
    def cols(self, texts, widths=None, style='body'):
        n = len(texts); gap = 16; W = PW - 2*M
        widths = widths or [(W - gap*(n-1))/n]*n
        x = M; hmax = 0
        for t, w in zip(texts, widths):
            para = Paragraph(t, ST[style]); _, h = para.wrap(w, 1000)
            para.drawOn(self.c, x, self.y - h); x += w + gap; hmax = max(hmax, h)
        self.y -= hmax + 6
    def table(self, data, colw, header=True, fs=None, x=None, advance=True):
        rows = [[Paragraph(str(x), ST['cellb'] if (header and i == 0) else ST['cell']) for x in r] for i, r in enumerate(data)]
        avail = PW - M - (M if x is None else x)
        if sum(colw) > avail:
            colw = [w*avail/sum(colw) for w in colw]
        t = Table(rows, colWidths=colw)
        sty = [('GRID',(0,0),(-1,-1),0.4,HexColor('#9aa7b5')),('VALIGN',(0,0),(-1,-1),'TOP'),
               ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5)]
        if header: sty.append(('BACKGROUND',(0,0),(-1,0),HexColor('#dbe6f2')))
        t.setStyle(TableStyle(sty))
        w, h = t.wrap(sum(colw), 1000)
        t.drawOn(self.c, M if x is None else x, self.y - h)
        if advance: self.y -= h + 8
        return h
    def system(self, chords, nacc=0, caps=None, dx=None, title=None, marks=None, x0=None, x1=None):
        if title: self.p(f'<b>{title}</b>', 'body')
        top = self.y - (36 if caps else 26)
        nfig = max([len(ch.get('fig') or []) for ch in chords] + [1])
        h = system_height(nfig)
        bottom = draw_system(self.c, x0 or (M+14), top, x1 or (PW-M), chords, nacc=nacc, caps=caps, dx=dx, marks=marks)
        self.y = bottom - 4
    def blocks(self, chords, nacc=0, title=None, clef='treble', dx=None):
        if title: self.p(f'<b>{title}</b>', 'body')
        top = self.y - 22
        b = draw_blocks(self.c, M+10, top, PW-M, chords, nacc=nacc, clef=clef, dx=dx)
        self.y = b
    def save(self):
        self.footer(); self.c.save()

def ch(v, fig=None, rn='', bar=False, conn=False, ann=None, sub=None):
    return dict(v=v, fig=fig or [], rn=rn, bar=bar, conn=conn, ann=ann, sub=sub)

def validate(name, chords, expect=None):
    """run checks across connected chords"""
    for i, k in enumerate(chords):
        for w in check_chord(k['v'], f'[{name} acc.{i+1}]'): print('WARN', w)
        if expect and expect[i]:
            got = sorted(set(pname(x) for x in k['v']))
            if got != sorted(set(expect[i])): print('WARN', name, i+1, 'note', got, 'attese', sorted(set(expect[i])))
        if i+1 < len(chords) and k.get('conn'):
            for w in check_pair(k['v'], chords[i+1]['v'], f'[{name} {i+1}->{i+2}]'): print('WARN', w)
