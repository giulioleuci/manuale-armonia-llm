import itertools
from .music import *
from .registro import penalita

URANGE = {'S':(62,81), 'A':(55,72), 'T':(48,64), 'B':(40,60)}

def candidates(spec):
    bass = spec['bass']; ups = spec['up']
    out = set()
    perms = set(itertools.permutations(ups))
    for perm in perms:
        opts = []
        for v, nm in zip(['S','A','T'], perm):
            lo, hi = URANGE[v]
            o = [with_octave(nm, k) for k in range(2,7)]
            o = [p for p in o if lo <= midi(p) <= hi]
            opts.append(o)
        bo = [with_octave(bass, k) for k in range(1,5)]
        bo = [p for p in bo if URANGE['B'][0] <= midi(p) <= URANGE['B'][1]]
        for s in opts[0]:
            for a in opts[1]:
                for t in opts[2]:
                    for b in bo:
                        ch = (s,a,t,b)
                        m = [midi(x) for x in ch]
                        if not (m[0] > m[1] > m[2] > m[3]): continue
                        if m[0]-m[1] > 12 or m[1]-m[2] > 12 or m[2]-m[3] > 19: continue
                        if m[0]-m[2] < spec.get('min_st', 6): continue
                        out.add(ch)
    return sorted(out)

def trans_ok(c1, c2, rules, bass_rules=None, maxleap=5):
    if check_pair(list(c1), list(c2)): return False
    m1=[midi(x) for x in c1]; m2=[midi(x) for x in c2]
    for k in range(3):
        if abs(m1[k]-m2[k]) > maxleap: return False
        if rules:
            n1 = pname(c1[k])
            if n1 in rules:
                if pname(c2[k]) not in rules[n1]: return False
                # direction constraint: step (<=2 semis) unless rule marks leap ok
                d = abs(m1[k]-m2[k])
                if d > rules.get('_maxstep', 4) and not rules.get('_leapok'): return False
    if abs(m1[3]-m2[3]) > 12: return False
    if bass_rules:
        n1 = pname(c1[3])
        if n1 in bass_rules and pname(c2[3]) not in bass_rules[n1]: return False
    return True

def cost(c1, c2):
    m1=[midi(x) for x in c1]; m2=[midi(x) for x in c2]
    cst = 0
    for k in range(3): cst += abs(m1[k]-m2[k]) * (1.5 if k==0 else 1.0)
    cst += abs(m1[3]-m2[3]) * 0.3
    return cst

def static_cost(c, spec):
    m=[midi(x) for x in c]
    s = 0
    s += abs(m[0]-m[1]-5)*0.2 + abs(m[1]-m[2]-8)*0.15 + abs(m[2]-m[3]-9)*0.15
    s += abs(m[0]-74)*0.1   # soprano verso il Re5
    s += 2*penalita(c)    # zona medio-alta e separazione delle voci (registro.py)
    return s

def solve(specs, rules_list, bass_rules_list=None, topn=5, start_filter=None, end_filter=None, fixed=None):
    """specs: list of chord specs; rules_list[i]: rules for transition i->i+1"""
    n = len(specs)
    cands = [candidates(s) for s in specs]
    for i,sp in enumerate(specs):
        if sp.get('filt'): cands[i] = [c for c in cands[i] if sp['filt'](c)]
    if fixed:
        for i, ch in fixed.items(): cands[i] = [tuple(ch)]
    if start_filter: cands[0] = [c for c in cands[0] if start_filter(c)]
    if end_filter: cands[-1] = [c for c in cands[-1] if end_filter(c)]
    best = [{c: (static_cost(c, specs[0]), None) for c in cands[0]}]
    for i in range(1, n):
        cur = {}
        r = rules_list[i-1]; br = bass_rules_list[i-1] if bass_rules_list else None
        for c2 in cands[i]:
            bc = None
            for c1, (v, _) in best[i-1].items():
                if trans_ok(c1, c2, r, br):
                    tot = v + cost(c1, c2) + static_cost(c2, specs[i])
                    if bc is None or tot < bc[0]: bc = (tot, c1)
            if bc: cur[c2] = bc
        best.append(cur)
        if not cur: return None
    last = sorted(best[-1].items(), key=lambda kv: kv[1][0])[:topn]
    sols = []
    for c, (v, _) in last:
        path = [c]; prev = best[-1][c][1]; k = n-1
        while prev is not None:
            path.append(prev); k -= 1; prev = best[k][prev][1] if k >= 0 and best[k].get(prev) else None
        sols.append((v, list(reversed(path))))
    return sols

# ---------- solver con vincoli di catena (spec di chords.py)
_OK = {0:(0,), 1:(1,2), 2:(3,4), 3:(5,), 4:(7,), 5:(8,9), 6:(10,11), 7:(12,)}
def _melodic_ok(p, q):   # niente intervalli eccedenti/diminuiti
    a = abs(step(q) - step(p)); return abs(midi(q) - midi(p)) in _OK.get(a, ())
def _mv(p, q, d):
    if d == 'hold': return p == q
    s = 1 if d == 'up' else -1
    return step(q) - step(p) == s and (midi(q) - midi(p)) * s in (1, 2)

def trans2(c1, c2, s1, s2, ml):
    m1 = [midi(x) for x in c1]; m2 = [midi(x) for x in c2]
    for k in range(3):
        if abs(m2[k] - m1[k]) > ml or (m2[k] != m1[k] and not _melodic_ok(c1[k], c2[k])): return False
    if abs(m2[3] - m1[3]) > 12 or abs(m2[3] - m1[3]) in (10, 11): return False   # basso: mai salto di settima
    for k in range(3):
        if m2[k+1] >= m1[k] or m2[k] <= m1[k+1]: return False   # sovrapposizione
    if check_pair(list(c1), list(c2)): return False
    for nt, d in s1['mv'].items():
        solo_alte = nt.startswith('^')            # '^F': vale per le sole voci superiori
        for k in range(3 if solo_alte else 4):
            if pname(c1[k]) == nt.lstrip('^') and not _mv(c1[k], c2[k], d): return False
    for k, d in s1['vmv'].items():
        if not _mv(c1[k], c2[k], d): return False
    if s1['lt'] and s1['lt_up'] in s2['tones']:
        for k in range(3):                  # voci superiori; il basso segue la sua linea
            if pname(c1[k]) == s1['lt'] and not _mv(c1[k], c2[k], 'up'):
                if c1[k] == c2[k] and s1['lt'] in s2['tones']: continue    # nota comune tenuta
                if not (s1['bach'] and k in (1, 2) and step(c1[k]) - step(c2[k]) == 2 and midi(c1[k]) - midi(c2[k]) in (3, 4)):
                    return False
    sv = s2['sev']
    if sv and not s2['free7']:
        if sv not in s1['tones']: return False
        for k in range(4):
            if pname(c2[k]) == sv and c1[k] != c2[k]: return False   # settima preparata
    return True

def cdict(sp):
    """disposizioni possibili di una spec -> costo statico"""
    d = {}
    for opt, pen in sp['ups']:
        for c in candidates({'bass': sp['bass'], 'up': list(opt), 'min_st': sp.get('min_st', 6)}):
            if sp.get('filt') and not sp['filt'](c): continue
            d[c] = min(d.get(c, 99), pen)
    return {c: pen + static_cost(c, sp) for c, pen in d.items()}

def solve2(specs, maxleaps=(5, 7)):
    """DP sulla catena di spec; ritorna la lista di accordi (S,A,T,B) o None."""
    cands = [cdict(sp) for sp in specs]
    for ml in maxleaps:
        best = [{c: (v, None) for c, v in cands[0].items()}]
        for i in range(1, len(specs)):
            cur = {}
            for c2, v2 in cands[i].items():
                bc = None
                for c1, (v, _) in best[i-1].items():
                    if (bc is None or v + cost(c1, c2) < bc[0] - v2) and trans2(c1, c2, specs[i-1], specs[i], ml):
                        bc = (v + cost(c1, c2) + v2, c1)
                if bc: cur[c2] = bc
            if not cur: break
            best.append(cur)
        else:
            c = min(best[-1], key=lambda k: best[-1][k][0]); path = [c]
            for i in range(len(specs)-1, 0, -1): c = best[i][c][1]; path.append(c)
            return path[::-1]
    return None
