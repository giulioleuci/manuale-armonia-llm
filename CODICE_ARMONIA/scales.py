from music import *
SCALES = {
 'Do maggiore': ['C','D','E','F','G','A','B'],
 'La minore naturale': ['A','B','C','D','E','F','G'],
 'La minore armonica': ['A','B','C','D','E','F','G#'],
 'La minore melodica (ascendente)': ['A','B','C','D','E','F#','G#'],
}
ROM = ['I','II','III','IV','V','VI','VII']
TYPES = {
 (4,3,3): ('7', 'di dominante'),
 (4,3,4): ('7', 'maggiore'),
 (3,4,3): ('7', 'minore'),
 (3,3,4): ('7', 'semidiminuita'),
 (3,3,3): ('7', 'diminuita'),
 (3,4,4): ('7', 'minore-maggiore'),
 (4,4,3): ('7', 'quinta eccedente'),
}
def chord_on(scale, d, base_oct=4):
    names = [scale[(d+k*2) % 7] for k in (0,1,2,3)]
    pitches = []; prev = None
    for n in names:
        o = base_oct
        while True:
            p = with_octave(n, o)
            if prev is None or midi(p) > prev: break
            o += 1
        # for first note ensure within base octave
        pitches.append(p); prev = midi(p)
    return pitches
def chord_type(pitches):
    m = [midi(p) for p in pitches]
    return tuple(m[i+1]-m[i] for i in range(3))
def scale_row(scale, special=None):
    out = []
    for d in range(7):
        ps = chord_on(scale, d)
        t = chord_type(ps)
        sym, nm = TYPES[t]
        sub2 = (special or {}).get(d, nm)
        out.append(dict(p=ps, name=ROM[d]+sym, rn='', sub=nm if d not in (special or {}) else special[d], bar=True))
    return out
