"""Ritardi (cap. 10): es_cap10_<ritardo>_<voce>."""
from ..armonia.chords import spec
from ..armonia.music import VN
from ..armonia.solver import solve2
from .base import ch, add, join, caps_for

# (nome, esempi per tonalita'): P = (radice, qualita', rivolto, rn) accordo di preparazione,
# S = (basso, [3 voci superiori col ritardo], rn, cifra), R = (radice, qualita', rivolto, rn, cifra), F = finale o None
# lt: sensibile della tonalita'; bach: la sensibile del V cade di terza in una voce interna perche'
# la nota di risoluzione non puo' comparire durante il ritardo
RIT = [
 ('4_3', {'Do maggiore': (('C','M',0,'I'), ('G', ['C','D','G'], 'V', ['4']), ('G','M',0,'V',['3']), ('C','M',0,'I'), 'B'),
          'La minore':   (('A','m',0,'i'), ('E', ['A','B','E'], 'V', ['4']), ('E','M',0,'V',['3']), ('A','m',0,'i'), 'G#')}),
 ('9_8', {'Do maggiore': (('G','M',0,'V'), ('C', ['D','E','G'], 'I', ['9']), ('C','M',0,'I',['8']), None, 'B'),
          'La minore':   (('E','M',0,'V'), ('A', ['B','C','E'], 'i', ['9']), ('A','m',0,'i',['8']), None, 'G#')}),
 ('9_3', {'Do maggiore': (('F','M',0,'IV'), ('G', ['A','B','D'], 'V', ['9']), ('C','M',1,'I',['6','3']), None, 'B'),
          'La minore':   (('D','m',0,'iv'), ('E', ['F','G#','B'], 'V', ['9']), ('A','m',1,'i',['6','3']), None, 'G#')}),
 ('7_6', {'Do maggiore': (('G','M',0,'V'), ('E', ['D','E','G'], 'I', ['7']), ('C','M',1,'I',['6']), None, 'B'),
          'La minore':   (('E','M',0,'V'), ('C', ['B','C','E'], 'i', ['7']), ('A','m',1,'i',['6']), None, 'G#')}),
 ('7_6d', {'Do maggiore': (('C','M',0,'I'), ('D', ['C','F','D'], 'vii°', ['7']), ('B','d',1,'vii°',['6']), ('C','M',0,'I'), 'B'),
           'La minore':   (('A','m',0,'i'), ('B', ['A','D','B'], 'vii°', ['7']), ('G#','d',1,'vii°',['♯6']), ('A','m',0,'i'), 'G#')}),
]

def esempio_rit(nome, ex, k):
    (pr, pq, pi, prn), (sb, sup, srn, sfig), (rr, rq, ri, rrn, rfig), fin, lt = ex
    bach = nome in ('9_8', '7_6')
    # preparazione: la nota ritardata resta ferma; se P e' la dominante la sua sensibile deve salire
    # (o, nei ritardi sulla tonica, cadere di terza in una voce interna: la risoluzione non puo' comparire durante il ritardo)
    P = spec(pr, pq, pi, vmv={k: 'hold'}, lt=lt if pr in ('E', 'G') and pq == 'M' else None, bach=bach)
    S = spec(sb, 'M', 0, vmv={k: 'down'}, lt=lt if nome == '9_3' else None); S['ups'] = [(tuple(sup), 0)]; S['bass'] = sb
    # le note reali del ritardo; la tonica e' inclusa perche' la sensibile di P deve comunque salire (o cadere di terza)
    S['tones'] = list(dict.fromkeys([sb] + list(sup) + ([P['lt_up']] if P['lt'] else [])))
    mv = {}
    R = spec(rr, rq, ri, lt=lt if rq in ('d', 'M') and fin else None)
    if rq == 'd':                       # quinta diminuita scende, sensibile sale
        R = spec(rr, rq, ri, mv={R['tones'][2]: 'down'} if fin else {}, lt=lt if fin else None)
    sp = [P, S, R] + ([spec(fin[0], fin[1], fin[2])] if fin else [])
    v = solve2(sp)
    if not v:                           # disposizione stretta (S-T < 8a) se quella late non esiste
        for x in sp: x['min_st'] = 6
        v = solve2(sp)
    if not v: return None
    out = [ch(list(v[0]), [], prn, conn=True, ann={VN[k]: 'legatura'}),
           ch(list(v[1]), sfig, srn, conn=True, ann={VN[k]: 'risoluz.↓'}),
           ch(list(v[2]), rfig, rrn, conn=bool(fin), bar=not fin)]
    if fin: out.append(ch(list(v[3]), [], fin[3], bar=True))
    return out

def genera():
    """es_cap10_<ritardo>_<voce>: Do maggiore e La minore affiancati (solo le realizzazioni esistenti)"""
    for nome, ex in RIT:
        for k, voce in ((0, 's'), (1, 'a')):
            res = [(r, t) for t, e in ex.items() if (r := esempio_rit(nome, e, k))]
            if not res: continue
            add(f'es_cap10_{nome}_{voce}', join(*[r for r, _ in res]), dx=62,
                caps=caps_for([r for r, _ in res], [t for _, t in res]))
