import itertools, re
LETTERS = 'CDEFGAB'
SEMI = [0,2,4,5,7,9,11]

def parse(p):
    m = re.match(r'^([A-G])(bb|b|##|#|n)?(-?\d)$', p)
    L, acc, o = m.group(1), m.group(2) or '', int(m.group(3))
    alt = {'':0,'#':1,'##':2,'b':-1,'bb':-2,'n':0}[acc]
    return LETTERS.index(L), o, alt, acc == 'n'

def name_parse(n):
    m = re.match(r'^([A-G])(bb|b|##|#)?$', n)
    return LETTERS.index(m.group(1)), {'':0,'#':1,'##':2,'b':-1,'bb':-2}[m.group(2) or '']

def midi(p):
    l, o, a, _ = parse(p)
    return 12*(o+1) + SEMI[l] + a

def step(p):
    l, o, a, _ = parse(p)
    return o*7 + l

def alt_of(p): return parse(p)[2]
def letter_of(p): return parse(p)[0]

def fmt(l, o, a):
    return LETTERS[l] + {0:'',1:'#',2:'##',-1:'b',-2:'bb'}[a] + str(o)

def pname(p):
    l, o, a, _ = parse(p)
    return LETTERS[l] + {0:'',1:'#',2:'##',-1:'b',-2:'bb'}[a]

def name_pc(n):
    l, a = name_parse(n)
    return (SEMI[l] + a) % 12

def with_octave(name, octv):
    l, a = name_parse(name)
    return fmt(l, octv, a)

# ---------- interval spelling (for tables)
def spell_up(name, diatonic_steps, semitones):
    """name + interval defined by diatonic steps and semitones -> spelled name"""
    l, a = name_parse(name)
    nl = (l + diatonic_steps) % 7
    base = SEMI[l] + a
    target = (base + semitones) % 12
    nat = SEMI[nl]
    d = (target - nat) % 12
    if d > 6: d -= 12
    return LETTERS[nl] + {0:'',1:'#',2:'##',-1:'b',-2:'bb'}[d]

# ---------- checker
RANGES = {'S':(60,81), 'A':(55,74), 'T':(45,66), 'B':(38,60)}
VN = ['S','A','T','B']

def check_pair(ch1, ch2, label=''):
    """ch = [S,A,T,B] pitch strings. returns list of warnings."""
    w = []
    m1 = [midi(x) for x in ch1]; m2 = [midi(x) for x in ch2]
    for i in range(4):
        for j in range(i+1, 4):
            a1, b1 = m1[i]-m1[j], m2[i]-m2[j]
            moved_i = m1[i] != m2[i]; moved_j = m1[j] != m2[j]
            if moved_i and moved_j:
                c1, c2 = a1 % 12, b1 % 12
                if (c1 == 7 and c2 == 7) or (c1 == 0 and c2 == 0):
                    w.append(f'{label} parallele {"5e" if c1==7 else "8ve"} tra {VN[i]}-{VN[j]}')
    # hidden octaves/fifths outer voices with soprano leap
    if m1[0] != m2[0] and m1[3] != m2[3]:
        same = (m2[0]-m1[0])*(m2[3]-m1[3]) > 0
        if same and (m2[0]-m2[3]) % 12 in (0,7) and abs(m2[0]-m1[0]) > 2:
            w.append(f'{label} esplicite/dirette tra S-B con salto in S')
    return w

def check_chord(ch, label=''):
    w = []
    m = [midi(x) for x in ch]
    for i in range(3):
        if not m[i] > m[i+1]: w.append(f'{label} incrocio/unisono {VN[i]}-{VN[i+1]}')
    if m[0]-m[1] > 12: w.append(f'{label} S-A > 8a')
    if m[1]-m[2] > 19: w.append(f'{label} A-T > 12a')
    if m[2]-m[3] > 19: w.append(f'{label} T-B > 12a')
    for k,v in enumerate(VN):
        lo, hi = RANGES[v]
        if not lo <= m[k] <= hi: w.append(f'{label} {v} fuori estensione ({ch[k]})')
    return w

def chord_names(ch):
    return sorted(pname(x) for x in ch)
