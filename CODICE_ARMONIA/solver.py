import itertools
from music import *

URANGE = {'S':(62,81), 'A':(55,72), 'T':(48,64), 'B':(40,57)}

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
                        if m[0]-m[1] > 12 or m[1]-m[2] > 17 or m[2]-m[3] > 19: continue
                        if m[0]-m[2] < spec.get('min_st', 13): continue
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
    s += abs(m[0]-76)*0.1   # prefer S around E5
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
