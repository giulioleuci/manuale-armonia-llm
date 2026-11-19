"""Progressioni (cap. 17): diatoniche, reali, basso cromatico, imitate, catena di settime."""
import math
from ..armonia.chords import spec, diat, fig, ann
from ..armonia.music import LETTERS, step, fmt, spell_up
from ..armonia.solver import solve2, cdict, trans2
from .base import ch, add, R7

DO = ['C','D','E','F','G','A','B']
ROMAN = ['I','II','III','IV','V','VI','VII']

def rn(root, q):
    """grado rispetto a Do: maiuscolo = accordo maggiore"""
    r = ROMAN[LETTERS.index(root[0])]
    r = {'': '', '#': '♯', 'b': '♭'}[root[1:]] + (r if q in ('M', '7', 'M7') else r.lower())
    return r + {'d': '°', 'ø7': 'ø', 'M7': 'maj'}.get(q, '')

# schema: (salto del modulo in gradi, passo tra moduli, n. moduli)
SCHEMI = {'I–IV discendente': (3, -1, 4), 'I–IV ascendente': (3, +1, 5),
          'I–V ascendente': (4, +1, 4), 'I–V discendente': (4, -1, 5)}
SIGLA = {'I–IV discendente': 'i4d', 'I–IV ascendente': 'i4a', 'I–V ascendente': 'i5a', 'I–V discendente': 'i5d'}
TIPI = {'T': 'solo triadi', 'S': 'solo settime', 'TS': 'triadi e settime'}
def sev(tipo, i): return tipo == 'S' or (tipo == 'TS' and i % 2 == 1)

def specs_da(lista, lt_finale=False, tonale=True, complete=False):
    """lista [(radice, qualita')] -> spec. La settima scende; la quinta diminuita scende (se l'accordo
    seguente contiene la nota sotto); la sensibile del V sale sulla tonica nell'ultima battuta.
    tonale: gli accordi di dominante/sensibile di Do non raddoppiano il Si."""
    sp = []
    for i, (r, q) in enumerate(lista):
        sp.append(spec(r, q, form='c' if complete and q in ('M', 'm', 'd') else None,
                       lt='B' if tonale and q in ('M', '7', 'd', 'ø7') and r in ('G', 'B') else None))
    for i, s in enumerate(sp[:-1]):
        if s['sev']: s['mv'][s['sev']] = 'down'
        if s['q'] in ('d', 'ø7'):
            q5 = s['tones'][2]; sotto = DO[(DO.index(q5[0]) - 1) % 7]
            if any(t[0] == sotto and t[1:] == '' for t in sp[i+1]['tones']): s['mv'][q5] = 'down'
    if lt_finale and lista[-2][0] == 'G' and lista[-1][0] == 'C': sp[-2]['mv'][sp[-2]['tones'][1]] = 'up'
    return sp

def diatonica(schema, tipo, ultimo_triade=True):
    salto, passo, nm = SCHEMI[schema]
    g = [(passo*m + (salto if j else 0)) % 7 for m in range(nm) for j in (0, 1)]
    n = len(g)
    return [diat(DO, x, sev(tipo, i) and not (ultimo_triade and i == n-1)) for i, x in enumerate(g)]

def reale(schema, tipo):
    """sequenza reale: ogni modulo trasposto di un tono; accordi maggiori (7a: di dominante). -> lista, arrivi"""
    salto, passo, _ = SCHEMI[schema]
    r = 'C'; out = []; arr = {}
    for m in range(3):
        out += [(r, '7' if tipo == 'S' else 'M'),
                (spell_up(r, salto, {3: 5, 4: 7}[salto]), '7' if tipo != 'T' and m < 2 else 'M')]
        arr[2*m + 1] = 'arrivo: ' + rn(out[-1][0], 'M')
        r = spell_up(r, 1, 2) if passo > 0 else spell_up(r, 6, 10)
    if tipo != 'T': out[-1] = (out[-1][0], 'M')
    return out, arr

def lista_rn(lista, sp): return [rn(r, q) for r, q in lista]

def sistemi(eid, sp, v, rns, subs=None, cs=8, connect_break=True, dx=70):
    """spezza la catena in sistemi di al piu' cs accordi (a fine modulo) -> ES[eid_a], ES[eid_b], ..."""
    n = len(sp); parti = math.ceil(n / cs); k = math.ceil(n / parti); k += k % 2
    ch_ = [ch(list(v[i]), fig(sp[i]), rns[i], conn=(i < n-1 and (i+1) % k != 0), sub=(subs or {}).get(i),
              ann=ann(sp[i], v[i], {sp[i]['sev']: R7}) if i < n-1 and sp[i]['sev'] else None) for i in range(n)]
    for j, a in enumerate(range(0, n, k)):
        parte = [dict(c) for c in ch_[a:a+k]]
        parte[-1]['conn'] = False
        i2 = eid + ('' if parti == 1 else 'abcd'[j])
        add(i2, parte, dx=dx)

def risolvi_catena(lista, **kw):
    """triadi tutte complete se possibile; altrimenti anche incomplete (fondamentale triplicata)"""
    for complete in (True, False):
        sp = specs_da(lista, complete=complete, **kw); v = solve2(sp)
        if v: return sp, v
    return sp, None

def progressioni():
    for schema in SCHEMI:
        sg = SIGLA[schema]
        for tipo in TIPI:
            lista = diatonica(schema, tipo); sp, v = risolvi_catena(lista, lt_finale=True)
            if v: sistemi(f'es_cap17_{sg}_dia_{tipo}', sp, v, lista_rn(lista, sp))
            lista, arr = reale(schema, tipo); sp, v = risolvi_catena(lista, tonale=False)
            if v: sistemi(f'es_cap17_{sg}_rea_{tipo}', sp, v, lista_rn(lista, sp), subs=arr)

# ---- basso cromatico discendente
CROM = {'T': [('C','M',0,'I'), ('G','M',1,'V'), ('Bb','M',0,'♭VII'), ('F','M',1,'IV'), ('F','m',1,'iv'), ('G','M',0,'V')],
        'TS': [('C','M',0,'I'), ('G','M',1,'V'), ('C','7',3,'I'), ('F','M',1,'IV'), ('F','m',1,'iv'), ('G','7',0,'V')]}

def crom(tipo):
    sp = [spec(r, q, inv, lt='B' if r == 'G' else None) for r, q, inv, _ in CROM[tipo]]
    for s_ in sp[:-1]:
        if s_['sev']: s_['mv'][s_['sev']] = 'down'
    return sp

def sincopa(eid, sp, v, rns, subs=None, cs=12, dx=60):
    """basso sincopato: ogni nota del basso entra sul tempo debole e resta legata fino al tempo forte (oltre la stanghetta);
    le voci superiori cambiano solo sul tempo forte. Accordi: forte (accordo k), debole (accordo k sopra il basso k+1)."""
    n = len(sp); blocchi = []
    for k in range(n):
        blocchi.append(ch(list(v[k]), fig(sp[k]), rns[k], conn=True, sub=(subs or {}).get(k),
                          ann=ann(sp[k], v[k], {sp[k]['sev']: R7}) if k < n-1 and sp[k]['sev'] and sp[k]['inv'] == 3 else None))
        if k < n-1:
            w = list(v[k][:3]) + [v[k+1][3]]
            a = ann(sp[k], w, {sp[k]['sev']: R7}) if sp[k]['sev'] and sp[k]['inv'] != 3 else None
            blocchi.append(ch(w, [], '', conn=True, bar=True, ann={x: y for x, y in (a or {}).items() if x != 'B'} or None))
    parti = math.ceil(len(blocchi) / cs); k = math.ceil(len(blocchi) / parti)
    for j, a in enumerate(range(0, len(blocchi), k)):
        parte = [dict(c) for c in blocchi[a:a+k]]; parte[-1]['conn'] = False
        i2 = eid + ('' if parti == 1 else 'abcd'[j]); add(i2, parte, dx=dx)

def cromatico():
    for tipo in CROM:
        sp = crom(tipo); v = solve2(sp)
        if not v: continue
        rns = [CROM[tipo][i][3] for i in range(len(sp))]
        subs = {2: 'V/IV'} if tipo == 'TS' else None
        sistemi(f'es_cap17_crom_leg_{tipo}', sp, v, rns, subs=subs)
        sincopa(f'es_cap17_crom_sin_{tipo}', sp, v, rns, subs=subs)

# ---- progressioni imitate
def shift(p, k): n = step(p) + k; return fmt(n % 7, n // 7, 0)

def imita(schema, tipo):
    """un solo modulo e' liberamente disposto; i moduli seguenti lo ripetono identico, un grado sopra/sotto"""
    passo, nm = SCHEMI[schema][1], SCHEMI[schema][2]
    lista = diatonica(schema, tipo, ultimo_triade=False); sp = specs_da(lista, tonale=False); cs = [cdict(s_) for s_ in sp]
    best = None
    for c1 in cs[0]:
        for c2 in cs[1]:
            sq = [tuple(shift(p, passo*m) for p in c) for m in range(nm) for c in (c1, c2)]
            if all(c in cs[i] for i, c in enumerate(sq)) and all(trans2(sq[i], sq[i+1], sp[i], sp[i+1], 7) for i in range(len(sq)-1)):
                sc = sum(cs[i][c] for i, c in enumerate(sq))
                if best is None or sc < best[0]: best = (sc, sq)
    return lista, sp, best and best[1]

def imitate():
    for schema in ('I–IV discendente', 'I–IV ascendente', 'I–V ascendente'):
        for tipo in TIPI:
            lista, sp, v = imita(schema, tipo)
            if v: sistemi(f'es_cap17_{SIGLA[schema]}_imi_{tipo}', sp, v, lista_rn(lista, sp))

def catena(S_, A_, T_, B_, rns, subs):
    n = len(S_)
    return [ch([S_[i], A_[i], T_[i], B_[i]], ['7'] if i < n-1 else [], rns[i], conn=(i < n-1), sub=subs[i]) for i in range(n)]

def catene():
    """catena di settime per quinte discendenti (si alternano accordi completi e incompleti)"""
    add('es_cap17_catena_do', catena(['G5','F5','F5','E5','E5','D5','D5','C5'], ['B4','A4','A4','G4','G4','F4','F4','E4'],
                                     ['E4','E4','D4','D4','C4','C4','B3','C4'], ['C3','F3','B2','E3','A2','D3','G2','C3'],
                                     ['I','IV','viiø','iii','vi','ii','V','I'],
                                     ['completa','incompleta','completa','incompleta','completa','incompleta','completa','incompleta']), dx=80)
    add('es_cap17_catena_la', catena(['G5','F5','F5','E5','E5','D5','D5','C5'], ['A4','A4','G4','G4','F4','F4','E4','E4'],
                                     ['C4','C4','B3','B3','A3','A3','G#3','A3'], ['A2','D3','G2','C3','F3','B2','E3','A2'],
                                     ['i','iv','VII','III','VI','iiø','V','i'],
                                     ['incompleta','completa','incompleta','completa','incompleta','completa','incompleta','completa']), dx=80)

def genera():
    progressioni(); cromatico(); imitate(); catene()
