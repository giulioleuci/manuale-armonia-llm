#!/usr/bin/env python3
r"""Riscrive soprano/contralto/tenore dei blocchi \partilate omoritmici tenendo fisso il basso.

Accordi: dall'analisi (grado nella tonalità, settima da etichetta/cifra); se manca o il basso non
ne fa parte, dalle note scritte. Ricerca Viterbi sulle disposizioni delle 3 voci superiori:
estensioni, spaziatura, raddoppi, niente 5e/8e parallele, sensibile e settima risolte,
moto minimo, e costo per ogni nota cambiata (il soprano si tocca il meno possibile).

Uso: .venv/bin/python tools/armonizza.py [--chapter 09] [--block 09:3] [--apply] [--libero]
Senza --apply stampa solo la proposta con segnalazioni prima/dopo.
"""
import argparse, glob, itertools, os, re, sys
from music21 import pitch as P, interval as I, scale as SC

sys.path.insert(0, os.path.dirname(__file__))
import analisi_music21 as AM
from verifica_voci import partilate_groups

RANGE = {'S': (60, 79), 'A': (53, 72), 'T': (48, 64)}
CENTRO = {'S': 68, 'A': 62, 'T': 55}
IT = {'C': 'do', 'D': 're', 'E': 'mi', 'F': 'fa', 'G': 'sol', 'A': 'la', 'B': 'si'}
DURS = {4: '1', 2: '2', 1: '4', .5: '8', .25: '16', 6: '1.', 3: '2.', 1.5: '4.', .75: '8.'}


def nome(p):
    acc = {'': '', '#': 'd', '##': 'dd', '-': 'b', '--': 'bb'}[p.name[1:]]
    o = p.octave - 3
    return IT[p.step] + acc + ("'" * o if o > 0 else ',' * -o)


def scala(tonic, minor, armonica):
    s = SC.HarmonicMinorScale(tonic) if minor and armonica else SC.MinorScale(tonic) if minor else SC.MajorScale(tonic)
    return [s.pitchFromDegree(d) for d in range(1, 8)]


def accordo(m, tonic, minor, fig, basso):
    """Etichetta già parsata (match LABEL) -> (radice, [terza, quinta, (settima)]) come Pitch, o None."""
    d = AM.DEG[m.group(1).lower()]
    sec = m.group(4)
    if sec:
        ty = AM.DEG[sec.lower()]
        tonic = scala(tonic, minor, False)[ty - 1] if True else tonic
        minor = sec.islower()
        arm = True
    else:
        arm = d in (5, 7) and m.group(2) != '+' and (d == 5 or m.group(2) == '°' or m.group(1).islower() and d == 7)
    sc = scala(tonic, minor, arm)
    if minor and not sec and d == 7 and m.group(2) is None and m.group(1).isupper():
        sc = scala(tonic, True, False)
    # sec: la dominante secondaria ha terza maggiore (armonica anche se Y maggiore)
    if sec:
        sc = scala(tonic, minor, True) if minor else scala(tonic, False, False)
        if d == 5: sc = scala(tonic, False, False)
    ch = [sc[(d - 1 + k) % 7] for k in (0, 2, 4, 6)]
    # ottave: portale sopra la radice
    return ch


def con_settima(m, fig, ch, basso):
    """True se l'accordo ha settima (etichetta o cifra coerente col basso)."""
    if m.group(3) in ('7', '65', '6/5', '43', '4/3', '42', '4/2', '2'): return True
    if m.group(1) and m.group(0).endswith('7') and m.group(3) is None: return True
    f = {int(x) for x in re.findall(r'\d+', fig or '')}
    pos = {frozenset({7}): 0, frozenset({6, 5}): 1, frozenset({4, 3}): 2, frozenset({4, 2}): 3, frozenset({2}): 3}.get(frozenset(f))
    return pos is not None and ch[pos].pitchClass == basso.pitchClass


def candidati(voce, pcs):
    lo, hi = RANGE[voce]
    out = []
    for midi in range(lo, hi + 1):
        for p in pcs:
            if midi % 12 == p.pitchClass:
                q = P.Pitch(p.name); q.octave = (midi - p.pitchClass + (12 if False else 0)) // 12 - 1
                q.octave = round((midi - (q.ps - q.octave * 12 - 12)) / 12) - 1 if False else q.octave
                out.append(q); break
    return out


def pitch_midi(p, midi):
    """p spelling, midi target -> Pitch con stessa classe e ottava corretta."""
    q = P.Pitch(p.name)
    q.octave = 4
    q.octave += round((midi - q.ps) / 12)
    return q


def soluzione(onsets, durs, bassi, accordi, orig, tonici, libero):
    """accordi[j] = (radice, terza, quinta, settima|None); orig[j] = {S,A,T}. -> [(S,A,T)] o None."""
    def cands(j):
        ch = accordi[j]
        pcs = [p for p in ch if p is not None]
        res = []
        for voce in 'SAT':
            lo, hi = RANGE[voce]
            res.append([pitch_midi(p, m) for m in range(lo, hi + 1) for p in pcs if m % 12 == p.pitchClass])
        out = []
        for s, a, t in itertools.product(*res):
            b = bassi[j]
            if not (s.ps > a.ps > t.ps > b.ps): continue
            if s.ps - a.ps > 12 or a.ps - t.ps > 12: continue
            notes = [s, a, t, b]
            pc = [n.pitchClass for n in notes]
            if ch[0].pitchClass not in pc or ch[1].pitchClass not in pc: continue
            if ch[3] is not None and ch[3].pitchClass not in pc: continue
            out.append((s, a, t))
        return out

    def unario(j, v):
        s, a, t = v; ch = accordi[j]; b = bassi[j]
        c = 0.0
        for nm, p in zip('SAT', v):
            c += 0.5 * abs(p.ps - CENTRO[nm])
        if t.ps - b.ps > 19: c += 3 * (t.ps - b.ps - 19)
        pc = [n.pitchClass for n in (s, a, t, b)]
        c += 2 * ((s.ps - a.ps > 12) + (a.ps - t.ps > 12))
        quinta_manca = ch[2].pitchClass not in pc
        if ch[3] is None:
            if quinta_manca: c += 15
        elif quinta_manca: c += float(os.environ.get('PEN_Q7', 8))
        cont = {k: pc.count(k) for k in set(pc)}
        sens = (tonici[j].pitchClass - 1) % 12
        rad, ter = ch[0].pitchClass, ch[1].pitchClass
        dom = rad in (sens, (tonici[j].pitchClass + 7) % 12) and ch[1].pitchClass != tonici[j].pitchClass
        for k, n in cont.items():
            if n > 1:
                if k == sens and dom: c += 300
                elif ch[3] is not None and k == ch[3].pitchClass: c += 300
                elif ch[3] is not None: c += 10   # raddoppio in accordo di settima
                elif k == rad: c += 0 if b.pitchClass == rad else 2
                elif k == ch[2].pitchClass: c += 4
                else: c += 10
        if b.pitchClass == ch[2].pitchClass and ch[3] is None and cont[b.pitchClass] < 2: c += 20  # 6/4: raddoppia il basso
        for nm, p, o in zip('SAT', v, orig[j]):
            if o is None or p.ps != o.ps:
                c += 4 if nm == 'S' and not libero else 0.5 if nm == 'S' else 1
        if not libero and orig[j][0] is not None and s.ps != orig[j][0].ps: c += 8
        return c

    def trans(j, u, v):  # u = voci in j-1, v = voci in j
        c = 0.0
        pu = list(u) + [bassi[j - 1]]; pv = list(v) + [bassi[j]]
        nm = 'SATB'
        for x in range(4):
            for y in range(x + 1, 4):
                m1, m2 = pv[x].ps - pu[x].ps, pv[y].ps - pu[y].ps
                if m1 == 0 or m2 == 0: continue
                i0, i1 = (pu[x].ps - pu[y].ps) % 12, (pv[x].ps - pv[y].ps) % 12
                for cls in (7, 0):
                    if i0 == cls == i1: c += 1000 if m1 * m2 > 0 else 300
                if x == 0 and y == 3 and i1 in (0, 7) and m1 * m2 > 0 and abs(m1) > 2: c += 60
        for x in range(3):
            d = abs(pv[x].ps - pu[x].ps)
            c += d * (1.5 if x == 0 else 1)
            if d > 12: c += 1000
            elif d > 7 and x > 0: c += 6
            if d == 6 or (d == 3 and abs(pv[x].diatonicNoteNum - pu[x].diatonicNoteNum) == 1): c += 80
            if d == 0: c -= 3
        prev = accordi[j - 1]
        if prev[3] is not None and accordi[j][0].pitchClass != prev[0].pitchClass:
            for x in range(4):
                if pu[x].pitchClass == prev[3].pitchClass and not 1 <= pu[x].ps - pv[x].ps <= 2: c += 200
        sens = (tonici[j - 1].pitchClass - 1) % 12
        if accordi[j][0].pitchClass == tonici[j - 1].pitchClass and prev[0].pitchClass != accordi[j][0].pitchClass:
            for x in range(4):
                if pu[x].pitchClass == sens and (prev[0].pitchClass == (tonici[j - 1].pitchClass + 7) % 12 or prev[0].pitchClass == sens):
                    if pv[x].ps - pu[x].ps != 1: c += 100 if x in (0, 3) else 20
        return c

    C = [cands(j) for j in range(len(onsets))]
    if any(not c for c in C): return None
    best = [{v: (unario(0, v), None) for v in C[0]}]
    for j in range(1, len(C)):
        cur = {}
        for v in C[j]:
            u0 = unario(j, v)
            cur[v] = min(((best[-1][u][0] + trans(j, u, v) + u0, u) for u in C[j - 1]), key=lambda x: x[0])
        best.append(cur)
    v = min(best[-1], key=lambda k: best[-1][k][0]); path = [v]
    for j in range(len(C) - 1, 0, -1):
        v = best[j][v][1]; path.append(v)
    return path[::-1]


def elabora(fn, bi, line, content, env, libero):
    g = partilate_groups(content)
    if g is None: return None, 'non partilate'
    if env == 'errore': return None, 'ambiente errore (volutamente errato)'
    if any('\\' in g[i] for i in (1, 2, 3, 4)): return None, 'markup/glissando nelle voci'
    voci = [AM.parse_voice(g[i]) for i in (1, 2, 3, 4)]
    if any(p is None for ev in voci for _, _, p in ev): return None, 'pause'
    ons = [[e[0] for e in ev] for ev in voci]
    if any(o != ons[0] for o in ons): return None, 'non omoritmico'
    onsets, durs = ons[0], [e[1] for e in voci[0]]
    tm = re.search(r'\\time\s+(\d+)/(\d+)', g[0]); barlen = int(tm.group(1)) * 4 / int(tm.group(2)) if tm else 4
    km = re.search(r'\\key\s+(\w+)\s+\\(major|minor)', g[0])
    if not km: return None, 'senza tonalità'
    n = re.fullmatch(r'(do|re|mi|fa|sol|la|si)(dd|dies|diesis|d|bb|bemolle|b|)', km.group(1))
    tonic0 = P.Pitch(AM.STEP[n.group(1)] + AM.ACC[n.group(2)] + '4'); minor = km.group(2) == 'minor'
    labels = AM.parse_labels(g[5], 'lyr'); figs = AM.parse_labels(g[6], 'fig')
    KEY = re.compile(r'^(do|re|mi|fa|sol|la|si)\s*([#b]?)\s*(M|m):\s*(.*)$', re.I)
    N = len(onsets)
    bassi = [e[2] for e in voci[3]]
    orig = [(voci[0][j][2], voci[1][j][2], voci[2][j][2]) for j in range(N)]
    at = lambda lst, j: next((t for o, d, t in lst if o <= onsets[j] + 1e-9 < o + d - 1e-9), None)
    tonici, minori, acc, fonte, conflitti = [tonic0] * N, [minor] * N, [], [], []
    for off, d, txt in labels:
        k = KEY.match(txt.strip())
        if k:
            t_ = P.Pitch(AM.STEP[k.group(1).lower()] + {'#': '#', 'b': '-', '': ''}[k.group(2)] + '4')
            for j in range(N):
                if onsets[j] >= off - 1e-9: tonici[j], minori[j] = t_, k.group(3) == 'm'
    for j in range(N):
        lab = at(labels, j); lab = KEY.sub(r'\4', lab.strip()) if lab else None
        m = AM.LABEL.match(AM.normalize_label(lab)) if lab else None
        ch = None
        if lab and lab.startswith('@'):  # accordo esplicito: @fa#,la,do,mib (note con alterazioni music21: F#,A,C,E-)
            ps4 = [P.Pitch(x.strip() + '4') for x in lab[1:].split(',')]
            if bassi[j].pitchClass in [p.pitchClass for p in ps4]:
                ch = (ps4[0], ps4[1], ps4[2], ps4[3] if len(ps4) > 3 else None); fonte.append('esplicito')
        elif m:
            c4 = accordo(m, tonici[j], minori[j], at(figs, j), bassi[j])
            sev = con_settima(m, at(figs, j), c4, bassi[j])
            if bassi[j].pitchClass in [p.pitchClass for p in (c4 if sev else c4[:3])]:
                ch = (c4[0], c4[1], c4[2], c4[3] if sev else None); fonte.append('analisi')
            else:
                conflitti.append('%s: etichetta "%s" non contiene il basso %s' % (AM.posizione(onsets[j], barlen, 1), lab, bassi[j].nameWithOctave))
        if ch is None:  # dalle note scritte
            r = AM.find_root([p for p in orig[j] if p] + [bassi[j]])
            if r is None or None in orig[j]: return None, 'accordo non riconosciuto alla slice %d' % (j + 1)
            root = r[0]; ps_ = [p for p in orig[j]] + [bassi[j]]
            def membro(step):
                return next((p for p in ps_ if (p.diatonicNoteNum - root.diatonicNoteNum) % 7 == step), None)
            t_, q_ = membro(2), membro(4)
            if t_ is None: return None, 'terza mancante slice %d' % (j + 1)
            if q_ is None:
                q_ = P.Pitch((root.transpose('P5')).name)
            ch = (root, t_, q_, membro(6)); fonte.append('note')
        acc.append(ch)
    sol = soluzione(onsets, durs, bassi, acc, orig, tonici, libero)
    if sol is None: return None, 'nessuna disposizione valida'
    # riscrive S A T con le stesse durate e stessa barratura
    def voce(k):
        out, tot = [], 0.0
        for j in range(N):
            out.append(nome(sol[j][k]) + DURS[durs[j]])
            tot += durs[j]
            if abs(tot / barlen - round(tot / barlen)) < 1e-9 and j < N - 1: out.append('|')
        return '{ ' + ' '.join(out) + ' }'
    nuove = [voce(k) for k in range(3)]
    new = content
    for i in (1, 2, 3):  # segnaposto: evita che una voce nuova coincida col testo di un'altra vecchia
        if '{' + g[i] + '}' not in new: return None, 'gruppo non trovato'
        new = new.replace('{' + g[i] + '}', '\0%d\0' % i, 1)
    for i, nv in zip((1, 2, 3), nuove):
        new = new.replace('\0%d\0' % i, nv)
    return (new, fonte, nuove, conflitti), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter'); ap.add_argument('--block')
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--libero', action='store_true')
    a = ap.parse_args()
    tot = [0, 0, 0]
    for fn in sorted(glob.glob('Capitoli/*.tex')):
        num = os.path.basename(fn).split('_')[0]
        if a.chapter and num != a.chapter: continue
        text = open(fn).read(); new_text = text
        for bi, (line, content, env) in enumerate(AM.blocchi(fn), 1):
            if a.block and a.block != '%s:%d' % (num, bi): continue
            if partilate_groups(content) is None: continue
            res, why = elabora(fn, bi, line, content, env, a.libero)
            tag = '%s:%d (riga %d)' % (num, bi, line)
            if res is None:
                print('%-18s salto: %s' % (tag, why)); tot[2] += 1; continue
            new, fonte, nuove, conflitti = res
            f = lambda c: [x for x in AM.analyze(fn, bi, line, c, env) if x['sev'] != 'INFO' and x['cod'] in
                           ('PARALLELE', 'INCROCIO', 'ESTENSIONE', 'SPAZIATURA', 'SALTO', 'SETTIMA-NON-RISOLTA', 'SENSIBILE-RADDOPPIATA',
                            'SENSIBILE-NON-RISOLTA', 'TRITONO', 'SECONDA-ECC', 'NASCOSTE')]
            b, d = f(content), f(new)
            print('%-18s problemi %2d -> %2d   (accordi da: %s)' % (tag, len(b), len(d), '/'.join(sorted(set(fonte)))))
            for c_ in conflitti: print('      ATTENZIONE', c_)
            if a.block or len(d) > 0:
                for r in nuove: print('      ' + r)
                for x in d: print('      resta: %s %s %s' % (x['cod'], x['pos'], x['msg']))
            tot[0] += len(b); tot[1] += len(d)
            if a.apply and len(d) < len(b):
                new_text = new_text.replace(content, new, 1)
        if a.apply and new_text != text: open(fn, 'w').write(new_text)
    print('\nproblemi prima %d, dopo %d; blocchi saltati %d' % tuple(tot))


if __name__ == '__main__':
    main()
