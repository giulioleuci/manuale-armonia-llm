"""Sesta napoletana (cap. 21)."""
from .base import add, add_blocks, seq, join

def genera():
    NA = {
     'N6_V':  seq([['E5','A4','C4','A2'], ['D5','F4','Bb3','D3'], ['B4','E4','G#3','E3'], ['C5','E4','A3','A2']],
                  [([], 'i'), (['6'], 'II♭', '', {'T': '3ª dim.↓'}), ([], 'V'), ([], 'i')]),
     'N6_V7': seq([['E5','A4','C4','A2'], ['D5','F4','Bb3','D3'], ['D5','E4','G#3','E3'], ['C5','E4','A3','A2']],
                  [([], 'i'), (['6'], 'II♭', '', {'T': '3ª dim.↓', 'S': 'tenuta'}), (['7'], 'V', 'incompleta'), ([], 'i')]),
     'CAD':   seq([['A4','E4','C4','A2'], ['Bb4','F4','D4','D3'], ['A4','E4','C4','E3'], ['G#4','D4','B3','E3'], ['A4','C4','A3','A2']],
                  [([], 'i'), (['6'], 'II♭'), (['6','4'], 'i', 'cadenziale'), (['7'], 'V'), ([], 'i')]),
    }
    NC = {
     'N6_V':  seq([['C5','E4','G3','C3'], ['Db5','F4','Ab3','F2'], ['B4','D4','G3','G2'], ['C5','E4','G3','C3']],
                  [([], 'I'), (['6'], 'II♭', '', {'S': '3ª dim.↓'}), ([], 'V'), ([], 'I')]),
     'N6_V7': seq([['C5','E4','G3','C3'], ['Db5','F4','Ab3','F2'], ['B4','F4','G3','G2'], ['C5','E4','G3','C3']],
                  [([], 'I'), (['6'], 'II♭', '', {'S': '3ª dim.↓', 'A': 'tenuta'}), (['7'], 'V', 'incompleta'), ([], 'I')]),
     'CAD':   seq([['C5','E4','G3','C3'], ['Db5','F4','Ab3','F2'], ['C5','E4','G3','G2'], ['B4','D4','F3','G2'], ['C5','C4','E3','C3']],
                  [([], 'I'), (['6'], 'II♭'), (['6','4'], 'I', 'cadenziale'), (['7'], 'V'), ([], 'I')]),
    }
    add_blocks('es_cap21_01', [
        dict(p=['Db4','F4','Ab4'], name='II♭', sub='Do maggiore', sub2='stato fondamentale', bar=True),
        dict(p=['F4','Ab4','Db5'], name='II♭', fig=['6'], sub='Do maggiore', sub2='primo rivolto', bar=True),
        dict(p=['Bb4','D5','F5'], name='II♭', sub='La minore', sub2='stato fondamentale', bar=True),
        dict(p=['D4','F4','Bb4'], name='II♭', fig=['6'], sub='La minore', sub2='primo rivolto', bar=True)], dx=110)
    add('es_cap21_02', join(NA['N6_V'], NA['N6_V7']), dx=78, caps=[(0, 3, 'con la triade di V'), (4, 7, 'con la settima di V')])
    add('es_cap21_03', NA['CAD'], dx=100, caps=[(0, 4, 'i – II♭ – i – V – i')])
    add('es_cap21_04', join(NC['N6_V'], NC['N6_V7']), dx=78, caps=[(0, 3, 'con la triade di V'), (4, 7, 'con la settima di V')])
    add('es_cap21_05', NC['CAD'], dx=100, caps=[(0, 4, 'I – II♭ – I – V – I')])
