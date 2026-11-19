"""Seste eccedenti (cap. 22)."""
from .base import add, add_blocks, seq, join

def genera():
    EA = {
     'IT': seq([['E5','A4','C4','A3'], ['D#5','A4','A3','F3'], ['E5','G#4','B3','E3'], ['E5','A4','C4','A3']],
               [([], 'i'), (['♯6'], 'sesta it.', '', {'S': '6ª ecc. → 8ª'}), ([], 'V'), ([], 'i')]),
     'FR': seq([['E5','A4','C4','A3'], ['D#5','A4','B3','F3'], ['E5','G#4','B3','E3'], ['E5','A4','C4','A3']],
               [([], 'i'), (['♯6','4','3'], 'sesta fr.', '', {'S': '6ª ecc. → 8ª'}), ([], 'V'), ([], 'i')]),
     'GE': seq([['E5','A4','C4','A3'], ['D#5','A4','C4','F3'], ['E5','A4','C4','E3'], ['E5','G#4','B3','E3'], ['E5','A4','C4','A3']],
               [([], 'i'), (['♯6','5','3'], 'sesta ted.', '', {'S': '6ª ecc. → 8ª'}), (['6','4'], 'i'), ([], 'V'), ([], 'i')]),
    }
    EC = {
     'IT': seq([['G4','C4','E3','C3'], ['F#4','C4','C3','Ab2'], ['G4','B3','D3','G2'], ['G4','C4','E3','C3']],
               [([], 'I'), (['♯6'], 'sesta it.', '', {'S': '6ª ecc. → 8ª'}), ([], 'V'), ([], 'I')]),
     'FR': seq([['G4','C4','E3','C3'], ['F#4','C4','D3','Ab2'], ['G4','B3','D3','G2'], ['G4','C4','E3','C3']],
               [([], 'I'), (['♯6','4','3'], 'sesta fr.', '', {'S': '6ª ecc. → 8ª'}), ([], 'V'), ([], 'I')]),
     'GE': seq([['G4','C4','E3','C3'], ['F#4','C4','Eb3','Ab2'], ['G4','C4','E3','G2'], ['G4','B3','D3','G2'], ['G4','C4','E3','C3']],
               [([], 'I'), (['♯6','♭5','3'], 'sesta ted.', '', {'S': '6ª ecc. → 8ª', 'T': '♭3→♮3'}), (['6','4'], 'I'), ([], 'V'), ([], 'I')]),
    }
    GE_BAD = seq([['D#5','A4','C4','F3'], ['E5','G#4','B3','E3']], [(['♯6','5','3'], 'sesta ted.'), ([], 'V')])
    add_blocks('es_cap22_01', [
        dict(p=['F4','A4','D#5'], name='italiana', fig=['♯6'], sub2='VI · I · IV♯', bar=True),
        dict(p=['F4','A4','B4','D#5'], name='francese', fig=['♯6','4','3'], sub2='VI · I · II · IV♯', bar=True),
        dict(p=['F4','A4','C5','D#5'], name='tedesca', fig=['♯6','5','3'], sub2='VI · I · III · IV♯', bar=True)], dx=125)
    add_blocks('es_cap22_02', [
        dict(p=['Ab4','C5','F#5'], name='italiana', fig=['♯6'], sub2='VI♭ · I · IV♯', bar=True),
        dict(p=['Ab4','C5','D5','F#5'], name='francese', fig=['♯6','4','3'], sub2='VI♭ · I · II · IV♯', bar=True),
        dict(p=['Ab4','C5','Eb5','F#5'], name='tedesca', fig=['♯6','♭5','3'], sub2='VI♭ · I · III♭ · IV♯', bar=True)], dx=125)
    add('es_cap22_03', join(EA['IT'], EA['FR']), dx=78, caps=[(0, 3, 'i – sesta it. – V – i'), (4, 7, 'i – sesta fr. – V – i')])
    add('es_cap22_04', EA['GE'], dx=100, caps=[(0, 4, 'i – sesta ted. – i – V – i')])
    add('es_cap22_05', join(EC['IT'], EC['FR']), dx=78, caps=[(0, 3, 'I – sesta it. – V – I'), (4, 7, 'I – sesta fr. – V – I')])
    add('es_cap22_06', EC['GE'], dx=100, caps=[(0, 4, 'I – sesta ted. – I – V – I')])
    GE_BAD[-1]['bar'] = True
    add('es_cap22_07', GE_BAD, dx=130, marks=[(0, 2, 3, '5ª'), (1, 2, 3, '5ª')])
