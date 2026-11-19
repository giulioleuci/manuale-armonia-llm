"""Registro e separazione delle voci negli esempi SATB.

ZONA: parte medio-alta dell'estensione di ciascuna voce.
Per ogni tratto di accordi collegati (conn) si cerca lo spostamento d'ottava, costante per voce, che
porta le voci nella zona preferibile e le separa meglio, senza introdurre errori di condotta."""
import itertools
from .music import midi, fmt, parse, check_chord, check_pair

ZONA = {'S': (67, 79), 'A': (60, 72), 'T': (52, 64), 'B': (41, 57)}
MIN_SEP = (3, 3, 7)      # S-A, A-T, T-B (semitoni): almeno terza, terza, quinta
MAX_SEP = (12, 12, 19)   # ottava, ottava, dodicesima

def trasponi(p, d):
    l, o, a, _ = parse(p)
    return fmt(l, o + d // 12, a)

def penalita(v):
    m = [midi(x) for x in v]
    pen = 0
    for k, n in enumerate('SATB'):
        lo, hi = ZONA[n]
        pen += max(0, lo - m[k], m[k] - hi) ** 2
    for k in range(3):
        g = m[k] - m[k+1]
        pen += 4 * max(0, MIN_SEP[k] - g) ** 2 + 4 * max(0, g - MAX_SEP[k]) ** 2
    return pen

def tratti(chords):
    out, a = [], 0
    for i, c in enumerate(chords):
        if not c.get('conn') or i == len(chords) - 1:
            out.append((a, i)); a = i + 1
    return out

def _errori(vs):
    e = 0
    for i, v in enumerate(vs):
        e += len(check_chord(v))
        if i + 1 < len(vs): e += len(check_pair(v, vs[i+1]))
    return e

def ottimizza(chords):
    """sposta di ottava (per voce e per tratto) i chords satb; ritorna True se ha modificato qualcosa"""
    mod = False
    for a, b in tratti(chords):
        orig = [list(c['v']) for c in chords[a:b+1]]
        e0 = _errori(orig); p0 = sum(penalita(v) for v in orig)
        best = (p0, 0, [0, 0, 0, 0])
        for off in itertools.product((-12, 0, 12), repeat=4):
            if not any(off): continue
            nv = [[trasponi(x, off[k]) for k, x in enumerate(v)] for v in orig]
            if _errori(nv) > e0: continue
            p = sum(penalita(v) for v in nv)
            cand = (p, sum(1 for o in off if o), list(off))
            if (cand[0], cand[1]) < (best[0], best[1]): best = cand
        if any(best[2]):
            for i, v in enumerate(chords[a:b+1]):
                v['v'] = [trasponi(x, best[2][k]) for k, x in enumerate(v['v'])]
            mod = True
    return mod
