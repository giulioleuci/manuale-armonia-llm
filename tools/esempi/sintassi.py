"""Esempi delle Parti III, V-VII: funzioni, secondo rivolto, cadenze, note estranee, ritardi sulla tonica,
settime (Regola dell'Ottava, anticipate, II7 minore), tonicizzazione e modulazione."""
from .base import ch, add, add_blocks, join, A, catena, isolati

def genera():
    # ---- cap. 9: funzioni
    add('es_cap05_01', catena([A('C', 'M', 0, 'I', sub='tonica'), A('F', 'M', 0, 'IV', sub='sottodominante'),
                               A('G', 'M', 0, 'V', lt='B', sub='dominante'), A('C', 'M', 0, 'I', sub='tonica')]), dx=85)
    add('es_cap05_02', catena([A('C', 'M', 0, 'I'), A('D', 'm', 0, 'ii', sub='sottodominante'),
                               A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I')]), dx=85)

    # ---- cap. 10: secondo rivolto
    add('es_cap03_01', catena([A('F', 'M', 0, 'IV'), A('C', 'M', 2, 'I', sub='cadenziale', mv={'C': 'down', 'E': 'down', 'G': 'hold'}),
                               A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I')]), dx=80)
    add('es_cap03_02', catena([A('C', 'M', 0, 'I'), A('G', 'M', 2, 'V', sub='di passaggio'), A('C', 'M', 1, 'I')]), dx=85)

    # ---- cap. 12: cadenze
    add('es_cap06_01', catena([A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sop='C')]), dx=70)
    add('es_cap06_02', catena([A('G', 'M', 0, 'V', lt='B', sop='D'), A('C', 'M', 0, 'I', sop='E')]), dx=70)
    add('es_cap06_03', catena([A('G', 'M', 1, 'V', lt='B'), A('C', 'M', 0, 'I')]), dx=70)
    add('es_cap06_04', catena([A('F', 'M', 0, 'IV'), A('C', 'M', 0, 'I')]), dx=70)
    add('es_cap06_05', catena([A('F', 'M', 0, 'IV'), A('G', 'M', 0, 'V')]), dx=70)
    add('es_cap06_06', catena([A('G', 'M', 0, 'V', lt='B'), A('A', 'm', 0, 'vi', ups=[('C', 'E', 'C')])]), dx=70)
    add('es_cap06_07', catena([A('C', 'M', 0, 'I', sub='T'), A('F', 'M', 0, 'IV', sub='S'),
                               A('G', 'M', 0, 'V', lt='B', sub='D'), A('C', 'M', 0, 'I', sub='T', sop='C')]), dx=80)

    # ---- cap. 18: ciclo della dissonanza (I - II7 - V: la settima Do è preparata, percossa e risolta)
    add('es_cap08_01', catena([A('C', 'M', 0, 'I', sop='C', vmv={0: 'hold'}), A('D', 'm7', 0, 'ii', sop='C', vmv={0: 'down'}),
                               A('G', 'M', 0, 'V', lt='B', sop='B')]), dx=85,
        caps=[(0, 0, 'preparazione'), (1, 1, 'dissonanza'), (2, 2, 'risoluzione')])

    # ---- cap. 22-23: tritono (blocchi) e V7 -> VI
    add_blocks('es_cap09_01', [dict(p=['G4', 'B4', 'D5', 'F5'], name='V', fig=['7'], sub='Do maggiore', bar=True),
                               dict(p=['B4', 'F5'], name='tritono', sub='Si–Fa: 5ª diminuita')], dx=130)
    add('es_cap09_04', catena([A('G', '7', 0, 'V', lt='B', mv={'F': 'down'}, form='c'),
                               A('A', 'm', 0, 'vi', ups=[('C', 'E', 'C')])]), dx=85)

    # ---- cap. 19: note estranee (le voci A, T, B restano ferme mentre il soprano canta la nota estranea)
    c = catena([A('C', 'M', 0, 'I', sop='C5', vmv={1: 'hold', 2: 'hold', 3: 'hold'}), A('C', 'M', 0, 'I', sop='E5')])
    mezzo = ch([ 'D5'] + list(c[0]['v'][1:]), [], '', conn=True, ann={'S': 'nota di passaggio'})
    add('es_cap11_01', [c[0], mezzo, c[1]], dx=85)
    d = catena([A('C', 'M', 0, 'I', sop='G5', vmv={1: 'hold', 2: 'hold', 3: 'hold'}), A('C', 'M', 0, 'I', sop='E5'),
                A('G', 'M', 0, 'V', lt='B', sop='D5'), A('C', 'M', 0, 'I', sop='C5')])
    mezzo = ch(['F5'] + list(d[0]['v'][1:]), [], '', conn=True, ann={'S': 'nota di passaggio'})
    add('es_cap11_03', [d[0], mezzo, d[1], d[2], d[3]], dx=85)
    e = catena([A('G', 'M', 0, 'V', lt='B', sop='B4'), A('C', 'M', 0, 'I', sop='C5')])
    ant = ch(['C5'] + list(e[0]['v'][1:]), [], '', conn=True, ann={'S': 'anticipazione'})
    add('es_cap11_02', [e[0], ant, e[1]], dx=85)

    # ---- cap. 20: ritardo 4-3 sulla dominante (preparato dall'accordo di IV)
    add('es_cap11_04', catena([A('F', 'M', 0, 'IV', sop='C', mv={'C': 'hold'}),
                               A('G', 'M', 0, 'V', ups=[('C', 'D', 'G')], fig=['4'], mv={'C': 'down'}, sop='C'),
                               A('G', 'M', 0, 'V', lt='B', fig=['3'], sop='B', bar=False),
                               A('C', 'M', 0, 'I')]), dx=85)

    # ---- cap. 23: V7 e ritardo 4-3 sulla tonica (forma A: V7 completa, tonica incompleta; forma B: V7 incompleta, tonica completa)
    def forma(eid, tonica, dom, sub, lt, quarta, terza, completa, nacc=0):
        (r4, q4), (rd, qd) = sub, dom
        prima = A(r4, q4, 0 if q4 == 'M' else 1, 'IV' if q4 == 'M' else 'iv', mv={'^' + quarta: 'hold'}, bar=False)
        v7 = A(rd, '7', 0, 'V', form='c' if completa else 'i', lt=lt, mv={'^' + quarta: 'hold'}, bar=True)
        if completa:
            rit = A(tonica, 'M' if lt == 'B' else 'm', 0, 'I' if lt == 'B' else 'i', ups=[(tonica, quarta, tonica)], fig=['4'], mv={'^' + quarta: 'down'})
        else:
            quinta = {'C': 'G', 'A': 'E'}[tonica]
            rit = A(tonica, 'M' if lt == 'B' else 'm', 0, 'I' if lt == 'B' else 'i', ups=[(tonica, quarta, quinta)], fig=['4'], mv={'^' + quarta: 'down'})
        fin = A(tonica, 'M' if lt == 'B' else 'm', 0, 'I' if lt == 'B' else 'i', fig=['3'], form=None if completa else 'c')
        add(eid, catena([prima, v7, rit, fin]), nacc=nacc, dx=85)
    forma('es_cap10_01', 'C', ('G', 'G'), ('F', 'M'), 'B', 'F', 'E', True)
    forma('es_cap10_02', 'C', ('G', 'G'), ('F', 'M'), 'B', 'F', 'E', False)
    forma('es_cap10_03', 'A', ('E', 'E'), ('D', 'm'), 'G#', 'D', 'C', True)
    forma('es_cap10_04', 'A', ('E', 'E'), ('D', 'm'), 'G#', 'D', 'C', False)

    # ---- cap. 27 e 31: V6/5 sul VII grado, risoluzione anticipata, II6/5 nel minore
    add('es_cap12_02', catena([A('C', 'M', 0, 'I'), A('G', '7', 1, 'V', lt='B', mv={'F': 'down'}), A('C', 'M', 0, 'I')]), dx=85)
    add('es_cap12_03', catena([A('B', 'ø7', 0, 'viiø', mv={'A': 'down'}), A('G', '7', 1, 'V', lt='B', mv={'F': 'down'}), A('C', 'M', 0, 'I')]), dx=85)
    add('es_cap12_04', catena([A('A', 'm', 0, 'i', mv={'^A': 'hold'}), A('B', 'ø7', 1, 'iiø', mv={'A': 'down'}),
                               A('E', 'M', 0, 'V', lt='G#')]), dx=85)
    add('es_cap12_05', catena([A('A', 'm', 1, 'i', mv={'^A': 'hold'}), A('B', 'ø7', 1, 'iiø', mv={'A': 'down'}),
                               A('E', 'M', 0, 'V', lt='G#')]), dx=85)

    # ---- cap. 33: dominanti secondarie
    add('es_cap15_01', catena([A('C', 'M', 0, 'I'), A('D', '7', 0, 'V/V', lt='F#', mv={'C': 'down'}), A('G', 'M', 0, 'V', lt='B'),
                               A('C', 'M', 0, 'I')]), dx=85)
    add('es_cap15_02', catena([A('C', 'M', 0, 'I'), A('C', '7', 0, 'V/IV', lt='E', mv={'Bb': 'down'}), A('F', 'M', 0, 'IV')]), dx=85)

    # ---- cap. 34-35: modulazioni ai toni vicini (pivot)
    add('es_cap16_01', catena([A('C', 'M', 0, 'I'), A('D', 'm', 0, 'ii', sub='pivot: ii = iv'),
                               A('E', 'M', 0, 'V', lt='G#'), A('A', 'm', 0, 'i', sop='A')]), dx=85, caps=[(0, 0, 'Do M'), (2, 3, 'La m')])
    add('es_cap16_02', catena([A('C', 'M', 0, 'I'), A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sub='pivot: I = IV'),
                               A('D', 'M', 0, 'V', lt='F#'), A('G', 'M', 0, 'I', sop='G')]), dx=85, caps=[(0, 1, 'Do M'), (3, 4, 'Sol M')])
    add('es_cap16_03', catena([A('C', 'M', 0, 'I'), A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sub='pivot: I = V'),
                               A('C', '7', 0, 'V', lt='E', mv={'Bb': 'down'}), A('F', 'M', 0, 'I', sop='F')]), dx=85, caps=[(0, 1, 'Do M'), (3, 4, 'Fa M')])
    add('es_cap16_04', catena([A('C', 'M', 0, 'I'), A('B', 'ø7', 0, 'viiø', sub='pivot: viiø = iiø', free7=True, mv={'A': 'down', 'F': 'down'}),
                               A('E', 'M', 0, 'V', lt='G#'), A('A', 'm', 0, 'i', sop='A')]), dx=85, caps=[(0, 0, 'Do M'), (2, 3, 'La m')])
    add('es_cap16_05', catena([A('C', 'M', 0, 'I'), A('D', 'm7', 0, 'ii', sub='pivot: ii = vi', mv={'C': 'down'}),
                               A('G', 'm', 0, 'ii'), A('C', '7', 0, 'V', lt='E', mv={'Bb': 'down'}), A('F', 'M', 0, 'I', sop='F')]), dx=85,
        caps=[(0, 0, 'Do M'), (2, 4, 'Fa M')])
    add('es_cap16_06', catena([A('C', 'M', 0, 'I'), A('A', 'm', 0, 'vi', sub='pivot: vi = ii'),
                               A('D', '7', 0, 'V', lt='F#', mv={'C': 'down'}), A('G', 'M', 0, 'I', sop='G')]), dx=85,
        caps=[(0, 0, 'Do M'), (2, 3, 'Sol M')])
