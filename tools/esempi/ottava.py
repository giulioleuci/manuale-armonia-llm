"""Regola dell'Ottava: scale armonizzate (Parti VI e VIII).
Il soprano e' scritto a mano (linea cantabile, in moto contrario al basso); gli altri voci sono risolte dal solver.
La scala maggiore e' in Sol (Sol3-Sol2) e la minore in La (La3-La2) per tenere il basso nella zona medio-alta."""
from .base import add, A, catena

def genera():
    # Sol maggiore, scala discendente: V6, V2 e V4/3 colorano la discesa; il IV grado e' il V2
    s = ['B4', 'D5', 'E5', 'F#5', 'F#5', 'G5', 'F#5', 'G5']
    add('es_cap31_01', catena([
        A('G', 'M', 0, 'I', bas='G3', sop=s[0]), A('D', 'M', 1, 'V', lt='F#', sop=s[1]), A('C', 'M', 1, 'IV', sop=s[2]),
        A('D', 'M', 0, 'V', lt='F#', sop=s[3]), A('D', '7', 3, 'V', lt='F#', sop=s[4], mv={'C': 'down'}),
        A('G', 'M', 1, 'I', sop=s[5]), A('D', '7', 2, 'V', lt='F#', sop=s[6], mv={'C': 'down'}), A('G', 'M', 0, 'I', bas='G2', sop=s[7])]), nacc=1, dx=70)
    # La minore armonica, scala discendente
    s = ['A4', 'B4', 'D5', 'E5', 'E5', 'E5', 'D5', 'C5']
    add('es_cap31_02', catena([
        A('A', 'm', 0, 'i', bas='A3', sop=s[0]), A('E', 'M', 1, 'V', lt='G#', sop=s[1]), A('D', 'm', 1, 'iv', sop=s[2]),
        A('E', 'M', 0, 'V', lt='G#', sop=s[3]), A('E', '7', 3, 'V', lt='G#', sop=s[4], mv={'D': 'down'}),
        A('A', 'm', 1, 'i', sop=s[5]), A('E', '7', 2, 'V', lt='G#', sop=s[6], mv={'D': 'down'}), A('A', 'm', 0, 'i', bas='A2', sop=s[7])]), dx=70)
    # La minore armonica, scala ascendente
    s = ['C5', 'D5', 'C5', 'B4', 'B4', 'D5', 'D5', 'C5']
    add('es_cap14_02', catena([
        A('A', 'm', 0, 'i', bas='A2', sop=s[0]), A('E', '7', 2, 'V', lt='G#', sop=s[1], mv={'D': 'down'}),
        A('A', 'm', 1, 'i', sop=s[2], mv={'^A': 'hold'}), A('B', 'ø7', 1, 'iiø', sop=s[3], mv={'A': 'down'}),
        A('E', 'M', 0, 'V', lt='G#', sop=s[4]), A('D', 'm', 1, 'iv', sop=s[5]),
        A('E', '7', 1, 'V', lt='G#', sop=s[6], mv={'D': 'down'}), A('A', 'm', 0, 'i', bas='A3', sop=s[7])]), dx=70)
    # La minore melodica, scala ascendente: ii6/5 e IV6 con il Fa#, niente seconda eccedente al basso;
    # il Re del soprano nel IV6 prepara la settima del V6/5
    s = ['C5', 'D5', 'C5', 'B4', 'B4', 'D5', 'D5', 'C5']
    add('es_cap31_03', catena([
        A('A', 'm', 0, 'i', bas='A2', sop=s[0]), A('E', '7', 2, 'V', lt='G#', sop=s[1], mv={'D': 'down'}),
        A('A', 'm', 1, 'i', sop=s[2], mv={'^A': 'hold'}), A('B', 'm7', 1, 'ii', sop=s[3], mv={'A': 'down'}),
        A('E', 'M', 0, 'V', lt='G#', sop=s[4]), A('D', 'M', 1, 'IV', sop=s[5], nodbl=('F#',)),
        A('E', '7', 1, 'V', lt='G#', sop=s[6], mv={'D': 'down'}), A('A', 'm', 0, 'i', bas='A3', sop=s[7])]), dx=70)
    # Sol maggiore, scala discendente con la dominante secondaria V/V sul VI grado
    s = ['B4', 'D5', 'C#5', 'D5', 'D5', 'D5', 'C5', 'B4']
    add('es_cap14_01', catena([
        A('G', 'M', 0, 'I', bas='G3', sop=s[0]), A('D', 'M', 1, 'V', lt='F#', sop=s[1]),
        A('A', '7', 2, 'V/V', lt='C#', sop=s[2], mv={'G': 'down'}),
        A('D', 'M', 0, 'V', lt='F#', sop=s[3]), A('D', '7', 3, 'V', lt='F#', sop=s[4], mv={'C': 'down'}),
        A('G', 'M', 1, 'I', sop=s[5]), A('D', '7', 2, 'V', lt='F#', sop=s[6], mv={'C': 'down'}), A('G', 'M', 0, 'I', bas='G2', sop=s[7])]), nacc=1, dx=70)
    # La minore armonica, scala discendente con la sesta italiana sul VI grado
    s = ['A4', 'B4', 'D#5', 'E5', 'E5', 'E5', 'D5', 'C5']
    it = A('F', 'M', 0, 'sesta it.', fig=['♯6'], ups=[('A', 'A', 'D#')], mv={'D#': 'up'}, sop=s[2])
    add('es_cap14_03', catena([
        A('A', 'm', 0, 'i', bas='A3', sop=s[0]), A('E', 'M', 1, 'V', lt='G#', sop=s[1]), it,
        A('E', 'M', 0, 'V', lt='G#', sop=s[3]), A('E', '7', 3, 'V', lt='G#', sop=s[4], mv={'D': 'down'}),
        A('A', 'm', 1, 'i', sop=s[5]), A('E', '7', 2, 'V', lt='G#', sop=s[6], mv={'D': 'down'}), A('A', 'm', 0, 'i', bas='A2', sop=s[7])]), dx=70)
