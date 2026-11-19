"""Strumenti condivisi dai generatori di esempi: registro ES e costruttori di accordi/sistemi.

Convenzioni: voci (S, A, T, B); le note comuni a due accordi consecutivi sono rese
dal motore come due semiminime legate (legatura di valore)."""
from ..armonia.registro import ottimizza
ES = {}
R7 = '7ª↓'

def ch(v, fig=None, rn='', bar=False, conn=False, ann=None, sub=None):
    return dict(v=v, fig=fig or [], rn=rn, bar=bar, conn=conn, ann=ann, sub=sub)

def add(eid, chords, nacc=0, caps=None, dx=None, marks=None, registro=True):
    if registro: ottimizza(chords)   # voci nella zona medio-alta e ben separate
    e = dict(type='satb', nacc=nacc, chords=chords)
    if caps: e['caps'] = caps
    if dx: e['dx'] = dx
    if marks: e['marks'] = marks
    ES[eid] = e

def add_blocks(eid, chords, clef='treble', dx=None):
    chords[-1]['bar'] = False
    ES[eid] = dict(type='single', nacc=0, clef=clef, chords=chords, **({'dx': dx} if dx else {}))

def pair(a, b, fa, ra, fb, rb, ann=None, bar=True, suba=None, subb=None):
    return [ch(a, fa, ra, conn=True, ann=ann, sub=suba), ch(b, fb, rb, bar=bar, sub=subb)]

def seq(vs, labels):
    """labels: (fig, rn, sub, ann) per accordo; tutti connessi tranne l'ultimo"""
    out = []
    for i, (v, l) in enumerate(zip(vs, labels)):
        f, rn, sub, a = (list(l) + [None]*4)[:4]
        out.append(ch(v, f or [], rn, conn=(i < len(vs)-1), ann=a, sub=sub))
    return out

def join(*systems):
    """affianca piu' coppie/sistemi: l'ultimo accordo di ciascuno e' separato da stanghetta"""
    out = []
    for s in systems:
        s = [dict(c) for c in s]
        s[-1]['conn'] = False; s[-1]['bar'] = True
        out += s
    out[-1]['bar'] = False
    return out

def caps_for(systems, labels):
    i = 0; out = []
    for s, t in zip(systems, labels):
        out.append((i, i + len(s) - 1, t)); i += len(s)
    return out

# ---- costruttori su spec/solver (accordi risolti dal solver con vincoli)
from ..armonia.chords import spec as _spec, fig as _fig
from ..armonia.music import pname as _pname
from ..armonia.solver import solve2 as _solve2

def A(root, q, inv=0, rn='', sub=None, ann=None, sop=None, alt=None, ten=None, bas=None, bar=False, fig=None, ups=None, **kw):
    """descrittore di accordo per catena(): kw va a spec(); sop/alt/ten = nota (con o senza ottava) imposta a quella voce"""
    return dict(root=root, q=q, inv=inv, rn=rn, sub=sub, ann=ann, bar=bar, fig=fig, ups=ups, kw=kw, vinc=(sop, alt, ten, bas))

def _filtro(vinc):
    def ok(c):
        for i, w in enumerate(vinc):
            if w and not (c[i] == w or _pname(c[i]) == w): return False
        return True
    return ok

def catena(descs, maxleaps=(5, 7)):
    """risolve una successione di descrittori -> lista di accordi ch() (collegati tra loro)"""
    sps = []
    for d in descs:
        s = _spec(d['root'], d['q'], d['inv'], **d['kw'])
        if d['ups'] is not None: s['ups'] = [(tuple(u), 0) for u in d['ups']]
        if any(d['vinc']): s['filt'] = _filtro(d['vinc'])
        sps.append(s)
    v = _solve2(sps, maxleaps)
    if not v: raise ValueError('catena non risolvibile: ' + ' '.join(d['rn'] or d['root'] + d['q'] for d in descs))
    n = len(descs)
    return [ch(list(v[i]), descs[i]['fig'] if descs[i]['fig'] is not None else _fig(sps[i]), descs[i]['rn'], conn=i < n - 1,
               bar=descs[i]['bar'], ann=descs[i]['ann'], sub=descs[i]['sub']) for i in range(n)]

def isolati(descs):
    """accordi indipendenti (non collegati), ciascuno con la migliore disposizione"""
    out = []
    for d in descs:
        c = catena([d])[0]; c['conn'] = False; c['bar'] = True; out.append(c)
    out[-1]['bar'] = False
    return out

def diagnosi(descs):
    """indica le prime coppie di accordi non collegabili (aiuto per scrivere le catene)"""
    out = []
    for i in range(len(descs) - 1):
        try: catena(descs[i:i + 2])
        except ValueError: out.append(i)
    return out
