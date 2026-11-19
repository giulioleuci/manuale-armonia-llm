"""Esempi dei capitoli «Scegliere la numerica del basso» (43) e «Come affrontare il basso dato» (44).
Il soprano e' scritto a mano dove serve (linea cantabile); le altre voci sono risolte dal solver."""
from .base import add, join, ch, A, catena

def genera():
    # ---- cap. 43: formule dal basso
    add('es_cap43_01', catena([                    # I - IV6 - V6/5 - I, soprano 1-1-2-1
        A('C', 'M', 0, 'I', bas='C3', sop='C5'), A('F', 'M', 1, 'IV', sop='C5'),
        A('G', '7', 1, 'V', lt='B', sop='D5', mv={'F': 'down'}), A('C', 'M', 0, 'I', sop='C5')]), dx=85)
    add('es_cap43_02', catena([                    # I - IV6 - I6 (plagale), soprano 3-4-5
        A('G', 'M', 0, 'I', bas='G3', sop='B4'), A('C', 'M', 1, 'IV', sop='C5'), A('G', 'M', 1, 'I', sop='D5')]), nacc=1, dx=85)
    # sottodominante minore (prestito dal modo minore): il solver non fa semitoni cromatici nella stessa voce, quindi a mano
    add('es_cap43_03', [                           # I - IV - iv - I, il La scende a La bemolle nel contralto
        ch(['E5', 'G4', 'C4', 'C3'], [], 'I', conn=True), ch(['F5', 'A4', 'C4', 'F3'], [], 'IV', conn=True),
        ch(['F5', 'Ab4', 'C4', 'F3'], [], 'iv', conn=True), ch(['E5', 'G4', 'C4', 'C3'], [], 'I')], dx=85, registro=False)
    # basso legato: la nota ribattuta diventa la settima (preparata dal basso stesso) e scende di grado
    add('es_cap43_04', catena([                    # I - ii4/2 - V6/5 - I, basso Do-Do-Si-Do
        A('C', 'M', 0, 'I', bas='C3'), A('D', 'm7', 3, 'ii', sop='F5'), A('G', '7', 1, 'V', lt='B', mv={'F': 'down'}),
        A('C', 'M', 0, 'I')]), dx=85)
    add('es_cap43_05', catena([                    # I - IV - V4/2 - I6, basso Do-Fa-Fa-Mi
        A('C', 'M', 0, 'I', bas='C3'), A('F', 'M', 0, 'IV', bas='F3'), A('G', '7', 3, 'V', lt='B', mv={'F': 'down'}),
        A('C', 'M', 1, 'I')]), dx=85)
    # note lunghe: bordone di tonica, Fa tenuto con tre accordi, Sol tenuto prima della cadenza
    add('es_cap43_06', catena([                    # I - IV6/4 - I, Do tenuto
        A('C', 'M', 0, 'I', bas='C3', sop='E5'), A('F', 'M', 2, 'IV', sop='F5'), A('C', 'M', 0, 'I', sop='E5')]), dx=85)
    add('es_cap43_07', catena([                    # IV - ii6/5 - V4/2 - I6, Fa tenuto
        A('F', 'M', 0, 'IV', bas='F3'), A('D', 'm7', 1, 'ii'), A('G', '7', 3, 'V', lt='B', mv={'F': 'down'}),
        A('C', 'M', 1, 'I')]), dx=85)
    add('es_cap43_08', [                           # IV | I6/4 - V - V7 | I, Sol tenuto: il soprano scende per grado
        ch(['F5', 'A4', 'C4', 'F3'], [], 'IV', conn=True), ch(['E5', 'G4', 'C4', 'G3'], ['6', '4'], 'I', conn=True),
        ch(['D5', 'G4', 'B3', 'G3'], [], 'V', conn=True), ch(['D5', 'F4', 'B3', 'G3'], ['7'], 'V', conn=True),
        ch(['C5', 'E4', 'C4', 'C3'], [], 'I')], dx=85, registro=False)

    # ---- cap. 44: quattro bassi svolti
    add('es_cap44_01', catena([
        A('C', 'M', 0, 'I', bas='C3', sop='E5'), A('F', 'M', 1, 'IV', sop='F5'),
        A('G', '7', 1, 'V', lt='B', mv={'F': 'down'}, sop='F5'), A('C', 'M', 0, 'I', sop='E5'),
        A('F', 'M', 0, 'IV', bas='F2', sop='F5'), A('C', 'M', 2, 'I', mv={'C': 'down', 'E': 'down'}, sop='E5'),
        A('G', 'M', 0, 'V', lt='B', sop='D5'), A('C', 'M', 0, 'I', bas='C3', sop='C5')]), dx=75)
    add('es_cap44_02', join(catena([
        A('A', 'm', 0, 'i', bas='A3'), A('B', 'ø7', 3, 'iiø'), A('E', 'M', 1, 'V', lt='G#'), A('A', 'm', 0, 'i')]), catena([
        A('D', 'm', 0, 'iv', bas='D3', sop='A4'), A('E', 'M', 0, 'V', lt='G#', sop='G#4'), A('A', 'm', 0, 'i', bas='A2', sop='A4')])), dx=75)
    add('es_cap44_03', catena([
        A('C', 'M', 0, 'I', bas='C3'), A('A', 'm', 0, 'vi', sub='pivot: vi = ii'), A('D', '7', 1, 'V', lt='F#', mv={'C': 'down'}, bas='F#2'),
        A('G', 'M', 0, 'I', bas='G2', sop='B4'), A('C', 'M', 0, 'IV', bas='C3', sop='C5'), A('D', '7', 0, 'V', lt='F#', sop='A4', mv={'C': 'down'}),
        A('G', 'M', 0, 'I', bas='G2', sop='G4')]), nacc=0, dx=75, caps=[(0, 1, 'Do M'), (2, 6, 'Sol M')])
    add('es_cap44_04', [                           # I - IV - iv - I6/4 - V - I: Fa e Sol tenuti, La bemolle nel contralto
        ch(['E5', 'G4', 'C4', 'C3'], [], 'I', conn=True), ch(['F5', 'A4', 'C4', 'F3'], [], 'IV', conn=True),
        ch(['F5', 'Ab4', 'C4', 'F3'], [], 'iv', conn=True), ch(['E5', 'G4', 'C4', 'G3'], ['6', '4'], 'I', conn=True),
        ch(['D5', 'G4', 'B3', 'G3'], [], 'V', conn=True), ch(['C5', 'E4', 'C4', 'C3'], [], 'I')], dx=75, registro=False)
