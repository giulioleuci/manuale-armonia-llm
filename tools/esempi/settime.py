"""Settime (cap. 9 e 13): sette specie, collocazione nelle scale, risoluzioni."""
from ..armonia.chords import spec, fig, ann
from ..armonia.solver import solve2
from ..armonia.scales import SCALES, scale_row
from .base import ch, add, add_blocks, pair, join, caps_for, R7

# ---- Le sette specie su Do e collocazione nelle scale
def specie():
    add_blocks('es_cap13_10', [
        dict(p=['C4','E4','G4','Bb4'], name='1ª specie', sub='7ª di dominante', sub2='M + m + m', bar=True),
        dict(p=['C4','Eb4','G4','Bb4'], name='2ª specie', sub='7ª minore', sub2='m + M + m', bar=True),
        dict(p=['C4','Eb4','Gb4','Bb4'], name='3ª specie', sub='7ª semidiminuita', sub2='m + m + M', bar=True),
        dict(p=['C4','E4','G4','B4'], name='4ª specie', sub='7ª maggiore', sub2='M + m + M', bar=True)], dx=110)
    add_blocks('es_cap13_11', [
        dict(p=['C4','Eb4','Gb4','Bbb4'], name='5ª specie', sub='7ª diminuita', sub2='m + m + m', bar=True),
        dict(p=['C4','Eb4','G4','B4'], name='6ª specie', sub='7ª minore-maggiore', sub2='m + M + M', bar=True),
        dict(p=['C4','E4','G#4','B4'], name='7ª specie', sub='7ª maggiore con 5ª ecc.', sub2='M + M + m', bar=True)], dx=110)
    SP = {'Do maggiore': {4: '1ª sp. (dominante)', 6: '3ª sp. (sensibile)'},
          'La minore naturale': {6: '1ª sp. (dominante)'},
          'La minore armonica': {4: '1ª sp. (dominante)', 6: '5ª sp. (sensibile)'},
          'La minore melodica (ascendente)': {3: '1ª sp.', 4: '1ª sp. (dominante)', 5: '3ª sp.', 6: '3ª sp. (sensibile)'}}
    NOMI = {'7ª magg.': '4ª sp.', '7ª min.': '2ª sp.'}
    for eid, scala in (('es_cap13_12', 'Do maggiore'), ('es_cap13_13', 'La minore naturale'),
                       ('es_cap13_14', 'La minore armonica'), ('es_cap13_15', 'La minore melodica (ascendente)')):
        row = scale_row(SCALES[scala])
        SPECIE = {'di dominante': '1ª specie', 'minore': '2ª specie', 'semidiminuita': '3ª specie', 'maggiore': '4ª specie',
                  'diminuita': '5ª specie', 'minore-maggiore': '6ª specie', 'quinta eccedente': '7ª specie'}
        for x in row:
            x['sub2'] = SPECIE[x['sub']]; x['sub'] = ''
        add_blocks(eid, row, dx=82)

# ---- Settima di dominante, tutti gli stati (Do maggiore e La minore armonica)
CM = {
 'root_c': pair(['B4','D4','F3','G2'], ['C5','C4','E3','C3'], ['7'], 'V', [], 'I', {'S':'sens.↑','T':R7}, suba='completa', subb='incompleta'),
 'root_i': pair(['B4','G4','F3','G2'], ['C5','G4','E3','C3'], ['7'], 'V', [], 'I', {'S':'sens.↑','T':R7}, suba='incompleta', subb='completa'),
 'v65': pair(['D5','F4','G3','B2'], ['C5','E4','G3','C3'], ['6','5'], 'V', [], 'I', {'A':R7,'B':'sens.↑'}),
 'v43': pair(['B4','F4','G3','D3'], ['C5','E4','G3','C3'], ['4','3'], 'V', [], 'I', {'S':'sens.↑','A':R7}),
 'v2': pair(['D5','G4','B3','F3'], ['C5','G4','C4','E3'], ['2'], 'V', ['6'], 'I', {'T':'sens.↑','B':R7}),
}
AM = {
 'root_c': pair(['G#4','B3','D3','E2'], ['A4','A3','C3','A2'], ['7'], 'V', [], 'i', {'S':'sens.↑','T':R7}, suba='completa', subb='incompleta'),
 'root_i': pair(['G#4','E4','D3','E2'], ['A4','E4','C3','A2'], ['7'], 'V', [], 'i', {'S':'sens.↑','T':R7}, suba='incompleta', subb='completa'),
 'v65': pair(['B4','D4','E3','G#2'], ['A4','C4','E3','A2'], ['6','5'], 'V', [], 'i', {'A':R7,'B':'sens.↑'}),
 'v43': pair(['G#4','D4','E3','B2'], ['A4','C4','E3','A2'], ['4','3'], 'V', [], 'i', {'S':'sens.↑','A':R7}),
 'v2': pair(['B4','E4','G#3','D3'], ['A4','E4','A3','C3'], ['2'], 'V', ['6'], 'i', {'T':'sens.↑','B':R7}),
}
VII_C = pair(['D5','A4','F3','B2'], ['C5','G4','E3','C3'], ['7'], 'viiø', [], 'I', {'A':R7,'T':'5ª↓','B':'sens.↑'})
VII_A = pair(['D5','B4','F3','G#2'], ['C5','A4','E3','A2'], ['7'], 'vii°', [], 'i', {'S':'5ª↓','A':'3ª↓','T':R7,'B':'sens.↑'})

def settima_dominante():
    add('es_cap09_02', join(CM['root_c']), caps=[(0, 1, 'Do maggiore')], dx=95)
    add('es_cap09_03', join(CM['root_i']), caps=[(0, 1, 'Do maggiore')], dx=95)
    add('es_cap09_05', join(AM['root_c'], AM['root_i']), caps=[(0, 3, 'La minore')], dx=80)
    add('es_cap09_06', join(CM['v65'], AM['v65']), caps=[(0, 1, 'Do maggiore'), (2, 3, 'La minore')], dx=95)
    add('es_cap09_07', join(CM['v43'], AM['v43']), caps=[(0, 1, 'Do maggiore'), (2, 3, 'La minore')], dx=95)
    add('es_cap09_08', join(CM['v2'], AM['v2']), caps=[(0, 1, 'Do maggiore'), (2, 3, 'La minore')], dx=95)

# ---- Altre specie: risoluzioni generate dal solver
CTX = [
 dict(id='maggiore_do', title='Settima maggiore (4ª specie) – Do maggiore: I7 → IV', src=('C','M7'), dst=('F','M'), srn='Imaj', drn='IV', tinv=(0,0,0,1),
      mv={'B':'down'}, lab={'B':R7}),
 dict(id='maggiore_la', title='Settima maggiore (4ª specie) – La minore: VI7 → ii°', src=('F','M7'), dst=('B','d'), srn='VImaj', drn='ii°', tinv=(0,0,0,1),
      mv={'E':'down'}, lab={'E':R7}),
 dict(id='minore_do', title='Settima minore (2ª specie) – Do maggiore: II7 → V', src=('D','m7'), dst=('G','M'), srn='ii', drn='V', tinv=(0,0,0,1),
      mv={'C':'down'}, lab={'C':R7}, lt='B'),
 dict(id='minore_la', title='Settima minore (2ª specie) – La minore: I7 → IV', src=('A','m7'), dst=('D','m'), srn='i', drn='iv', tinv=(0,0,0,1),
      mv={'G':'down'}, lab={'G':R7}),
 dict(id='semidim_la', title='Settima semidiminuita (3ª specie) – La minore: II7 → V', src=('B','ø7'), dst=('E','M'), srn='iiø', drn='V', tinv=(0,0,0,1),
      mv={'A':'down'}, lab={'A':R7}, lt='G#'),
 dict(id='semidim_do', title='Settima semidiminuita (3ª specie) – Do maggiore: VII7 → I', src=('B','ø7'), dst=('C','M'), srn='viiø', drn='I', tinv=(0,1,1,2), noinc=1,
      mv={'A':'down','B':'up'}, lab={'A':R7,'B':'sens.↑'}, lt='B'),
 dict(id='dim_la', title='Settima diminuita (5ª specie) – La minore: VII7 → i', src=('G#','o7'), dst=('A','m'), srn='vii°', drn='i', tinv=(0,0,1,2), noinc=1,
      mv={'F':'down','G#':'up'}, lab={'F':R7,'G#':'sens.↑'}, lt='G#'),
 dict(id='minmagg_la', title='Settima minore-maggiore (6ª specie) – La minore: I7 → IV', src=('A','mM7'), dst=('D','m'), srn='imaj', drn='iv', tinv=(0,0,0,2),
      mv={'G#':'up'}, lab={'G#':'7ª↑'}, nodbl=('G#',)),
 dict(id='ecc_la', title='Settima con quinta eccedente (7ª specie) – La minore: III7 → VI', src=('C','+M7'), dst=('F','M'), srn='III+', drn='VI', tinv=(0,0,1,1),
      mv={'B':'down','G#':'up'}, lab={'B':R7,'G#':'5ª↑'}),
]

STATO = ['stato fondamentale', '1º rivolto', '2º rivolto', '3º rivolto']

def risolvi(cx):
    """-> lista di (didascalia, sub, [accordo1, accordo2]) per: fondamentale completa/incompleta, 6/5, 4/3, 2"""
    out = []
    for inv, form in ((0, 'c'), (0, 'i'), (1, None), (2, None), (3, None)):
        if form == 'i' and cx.get('noinc'): continue
        kw = dict(nodbl=cx.get('nodbl', ()))
        s = spec(*cx['src'], inv=inv, mv=cx['mv'], form=form, lt=cx.get('lt') if cx.get('lt') in cx['mv'] else None, **kw)
        t = spec(*cx['dst'], inv=cx['tinv'][inv], form='c' if form == 'i' else None,
                 lt=cx.get('lt') if cx['dst'][1] == 'M' else None, **kw)
        r = solve2([s, t])
        if not r: out.append((None, s, t)); continue
        out.append(([ch(list(r[0]), fig(s), cx['srn'], conn=True, ann=ann(s, r[0], cx['lab']),
                        sub={'c': 'completa', 'i': 'incompleta'}.get(form)),
                     ch(list(r[1]), fig(t), cx['drn'], bar=True)],
                    STATO[inv], s, t))
    return out

def altre_specie():
    for cx in CTX:
        res = risolvi(cx)
        cx['res'] = res
        # primo sistema: stato fondamentale (completa/incompleta) e primo rivolto; secondo: secondo e terzo rivolto
        n1 = 3 if not cx.get('noinc') else 2
        sys1 = [r for r in res[:n1] if r[0]]; sys2 = [r for r in res[n1:] if r[0]]
        for k, grp in ((1, sys1), (2, sys2)):
            if not grp: continue
            chords = join(*[r[0] for r in grp])
            add(f"es_cap13_{cx['id']}_{k}", chords, caps=caps_for([r[0] for r in grp], [r[1] for r in grp]), dx=80 if k == 1 else 95)

def genera():
    specie(); settima_dominante(); altre_specie()
