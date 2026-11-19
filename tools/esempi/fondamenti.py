"""Esempi delle Parti I-III: serie armonica, intervalli, triadi, rivolti, condotta, secondo rivolto.
Gli accordi a quattro parti sono risolti dal solver (zona medio-alta, voci separate)."""
import itertools
from ..armonia.chords import spec
from ..armonia.music import check_pair, check_chord, midi
from ..armonia.solver import cdict, cost
from .base import ch, add, add_blocks, join, A, catena, isolati

def coppia(s1, s2, pred, bar=True):
    """la coppia di accordi (con la migliore disposizione) tale che pred(avvisi di check_pair) sia vera"""
    c1, c2 = cdict(s1), cdict(s2)
    best = None
    for a, pa in c1.items():
        if check_chord(list(a)): continue
        for b, pb in c2.items():
            if check_chord(list(b)): continue
            if not pred(check_pair(list(a), list(b))): continue
            sc = pa + pb + 0.3 * cost(a, b)
            if best is None or sc < best[0]: best = (sc, a, b)
    if not best: raise ValueError('coppia non trovata')
    return best[1], best[2]

def genera():
    # ---- cap. 1: serie armonica di Do (7 armonici) e rivolto di un intervallo
    arm = [('C2', 'Do2'), ('C3', 'Do3'), ('G3', 'Sol3'), ('C4', 'Do4'), ('E4', 'Mi4'), ('G4', 'Sol4'), ('Bb4', 'Si♭4')]
    add_blocks('es_cap01_01', [dict(p=[n], name=str(i + 1), sub=s) for i, (n, s) in enumerate(arm)], clef='grand', dx=70)
    add_blocks('es_cap01_02', [dict(p=['C4', 'E4'], name='3ª maggiore', sub='Do–Mi', bar=True),
                               dict(p=['E4', 'C5'], name='6ª minore', sub='Mi–Do')], dx=130)

    # ---- cap. 3: le quattro specie di triade e le triadi sui gradi di Do maggiore
    add_blocks('es_cap02_01', [
        dict(p=['C4', 'E4', 'G4'], name='maggiore', sub='3ª M + 3ª m', bar=True),
        dict(p=['C4', 'Eb4', 'G4'], name='minore', sub='3ª m + 3ª M', bar=True),
        dict(p=['C4', 'Eb4', 'Gb4'], name='diminuita', sub='3ª m + 3ª m', bar=True),
        dict(p=['C4', 'E4', 'G#4'], name='eccedente', sub='3ª M + 3ª M')], dx=110)
    gradi = [('I', 'M', ['C4', 'E4', 'G4']), ('II', 'm', ['D4', 'F4', 'A4']), ('III', 'm', ['E4', 'G4', 'B4']),
             ('IV', 'M', ['F4', 'A4', 'C5']), ('V', 'M', ['G4', 'B4', 'D5']), ('VI', 'm', ['A4', 'C5', 'E5']),
             ('VII', 'dim', ['B4', 'D5', 'F5'])]
    add_blocks('es_cap02_02', [dict(p=p, name=g, sub=q, bar=True) for g, q, p in gradi], dx=70)

    # ---- cap. 4: basso reale, primo e secondo rivolto
    # (blocchi sul solo rigo di violino, senza legature: il basso reale e' la nota piu' grave)
    add_blocks('es_cap02_03', [dict(p=['C4', 'E4', 'G4'], name='I', sub='basso reale: Do', bar=True),
                               dict(p=['E4', 'G4', 'C5'], name='I', sub='basso reale: Mi', bar=True),
                               dict(p=['G4', 'C5', 'E5'], name='I', sub='basso reale: Sol')], dx=105)
    add_blocks('es_cap02_04', [dict(p=['E4', 'G4', 'C5'], name='I', fig=['6'])], dx=60)
    add_blocks('es_cap02_05', [dict(p=['G4', 'C5', 'E5'], name='I', fig=['6', '4'])], dx=60)

    # ---- cap. 6: sensibile
    add('es_cap04_01', catena([A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I')]), dx=70)
    add('es_cap04_02', catena([A('G', '7', 0, 'V', lt='B', bach=True, alt='B', bas='G2', mv={'F': 'down'}),
                               A('C', 'M', 0, 'I', alt='G', bas='C3')]), dx=70)

    # ---- cap. 7: quinte e ottave parallele, quinta giusta seguita da diminuita
    I_, II_ = spec('C', 'M', 0), spec('D', 'm', 0)
    q5 = coppia(I_, II_, lambda w: len(w) == 1 and '5e tra T-B' in w[0])
    q8 = coppia(I_, II_, lambda w: len(w) == 1 and '8ve tra S-B' in w[0])
    sis = [ch(list(q5[0]), [], 'I', conn=True), ch(list(q5[1]), [], 'ii', bar=True),
           ch(list(q8[0]), [], 'I', conn=True), ch(list(q8[1]), [], 'ii')]
    add('es_cap04_03', sis, dx=75, registro=False, caps=[(0, 1, 'quinte parallele'), (2, 3, 'ottave parallele')],
        marks=[(0, 2, 3, '5ª'), (1, 2, 3, '5ª'), (2, 0, 3, '8ª'), (3, 0, 3, '8ª')])
    V_, VII_ = spec('G', 'M', 0), spec('B', 'd', 0, nodbl=('B',))
    c1, c2 = cdict(V_), cdict(VII_)
    best = None
    for a, pa in c1.items():
        for b, pb in c2.items():
            if check_chord(list(a)) or check_chord(list(b)) or check_pair(list(a), list(b)): continue
            ok = any((midi(a[i]) - midi(a[j])) % 12 == 7 and (midi(b[i]) - midi(b[j])) % 12 == 6
                     and midi(b[i]) > midi(a[i]) and midi(b[j]) > midi(a[j])
                     for i in range(4) for j in range(i + 1, 4))
            if ok and (best is None or pa + pb + 0.3 * cost(a, b) < best[0]): best = (pa + pb + 0.3 * cost(a, b), a, b)
    add('es_cap04_04', [ch(list(best[1]), [], 'V', conn=True), ch(list(best[2]), [], 'vii°')], dx=75)
