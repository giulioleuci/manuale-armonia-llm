#!/usr/bin/env python3
r"""Verifica musicale dei blocchi \partilate con music21.

Per ogni blocco: parse delle 4 voci (con durate), analisi (lyricmode), basso numerato
(figuremode); poi controlli di condotta delle parti, riconoscimento accordi e coerenza
tra accordi, analisi e cifratura.

Uso (serve il venv: python3 -m venv .venv && .venv/bin/pip install music21):
  .venv/bin/python tools/analisi_music21.py                 # tutti i capitoli
  .venv/bin/python tools/analisi_music21.py --chapter 09    # un capitolo
  .venv/bin/python tools/analisi_music21.py --block 09:3    # un blocco, con tabella verticale
  .venv/bin/python tools/analisi_music21.py --json
Exit code 1 se ci sono errori (ERR) fuori dagli ambienti `errore`.
"""
import argparse, glob, json, os, re, sys
from music21 import pitch as m21pitch

sys.path.insert(0, os.path.dirname(__file__))
from verifica_voci import partilate_groups

STEP = {'do': 'C', 're': 'D', 'mi': 'E', 'fa': 'F', 'sol': 'G', 'la': 'A', 'si': 'B'}
ACC = {'': '', 'd': '#', 'dies': '#', 'diesis': '#', 'dd': '##', 'b': '-', 'bemolle': '-', 'bb': '--'}
NOTE = re.compile(r"(do|re|mi|fa|sol|la|si)(dd|dies|diesis|d|bb|bemolle|b|)([',]*)[!?]*(\d+)?(\.*)")
REST = re.compile(r"[rsR](\d+)?(\.*)")
VOCI = ['S', 'A', 'T', 'B']
# estensioni (MIDI): sopr do'-la'', contr fa-re'', ten do-mi' (regola di progetto), basso re,-re'
RANGE = {'S': (60, 81), 'A': (53, 74), 'T': (48, 64), 'B': (36, 62)}
ROMAN = r'(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)'
LABEL = re.compile(r'^' + ROMAN + r'(°|ø|\+)?(7|6/5|65|4/3|43|6/4|64|4/2|42|2|6)?(?:/' + ROMAN + r')?(\s.*)?$')
DEG = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7}
STEPS = 'CDEFGAB'


def balanced(s, i):
    """s[i] == '{': ritorna indice dopo la graffa di chiusura."""
    d = 0
    for j in range(i, len(s)):
        d += (s[j] == '{') - (s[j] == '}')
        if d == 0:
            return j + 1
    return len(s)


def dur(num, dots, last):
    """last = (valore, punti) precedenti: in LilyPond una durata omessa eredita anche i punti."""
    n, dots = (int(num), dots or '') if num else last
    return (n, dots), (4 / n) * (2 - 0.5 ** len(dots))


def clean(s):
    s = re.sub(r'%[^\n]*', '', s)
    out, i = '', 0
    while i < len(s):
        m = re.compile(r'\\(markup|column|bold|line)\s*').match(s, i)
        if m and m.group(1) == 'markup' and s[m.end():m.end() + 1] == '{':
            i = balanced(s, m.end())
        else:
            out += s[i]; i += 1
    s = re.sub(r'[\^_]\s*"[^"]*"', ' ', s)
    return re.sub(r'\\(freccia\w*|glissando|bold|fermata|[<>!])|[()|\[\]]', ' ', s)


def parse_voice(text):
    """-> [(offset, durata, Pitch|None, legata)] ; durate in quarti."""
    s, i, off, last, ev, tie = clean(text), 0, 0.0, (4, ''), [], False
    while i < len(s):
        if s[i] == '~':
            tie = True; i += 1; continue
        m = NOTE.match(s, i)
        if m and (m.end() == len(s) or not s[m.end()].isalpha()):
            nm, ac, oc, num, dots = m.groups()
            last, d = dur(num, dots, last)
            p = m21pitch.Pitch(STEP[nm] + ACC[ac] + str(3 + oc.count("'") - oc.count(',')))
            if tie and ev and ev[-1][2] is not None and ev[-1][2].ps == p.ps:
                ev[-1] = (ev[-1][0], ev[-1][1] + d, ev[-1][2])
            else:
                ev.append((off, d, p))
            tie, off, i = False, off + d, m.end(); continue
        m = REST.match(s, i)
        if m and (m.end() == len(s) or not s[m.end()].isalpha()):
            last, d = dur(m.group(1), m.group(2), last)
            ev.append((off, d, None)); off, i = off + d, m.end(); continue
        i += 1
    return ev


def parse_labels(text, kind):
    """lyricmode/figuremode -> [(offset, durata, testo)]; come LilyPond, ogni sillaba/markup consuma una durata."""
    s = re.sub(r'%[^\n]*', '', text)
    s = re.sub(r'\\(un)?set\s+\S+(\s*=\s*\S+)?', ' ', s)
    out, i, off, last = [], 0, 0.0, (4, '')
    tok = re.compile(r'\s*(?:"([^"]*)"|(<(?:[^<>]|\\markup\s*\{[^}]*\})*>)|([a-zA-Z_|]\S*?))(?=[\d.\s<"\\]|$)')
    while i < len(s):
        m = re.compile(r'\s*(\\(?:markup|column|line)\s*)?(?=\{)').match(s, i)
        if m:
            j = balanced(s, m.end())
            txt, k = ' '.join(re.findall(r'"([^"]*)"', s[m.end():j])), j
        else:
            m = tok.match(s, i)
            if not m or m.end() == i:
                i += 1; continue
            txt, k = next(g for g in m.groups() if g is not None), m.end()
        if txt == '|' or (kind == 'lyr' and txt.startswith('\\')):
            i = k; continue
        dm = re.compile(r'\s*(\d+)?(\.*)').match(s, k)
        last, d = dur(dm.group(1), dm.group(2), last)
        out.append((off, d, txt)); off, i = off + d, dm.end()
    return out


def normalize_label(t):
    t = t.replace('$', '').replace('\\oslash', 'ø').replace('^', '').replace('{', '').replace('}', '').strip()
    return t


def find_root(ps):
    """ps: pitch list (voci). -> (root_pitch, inversione, qualità, ha_settima) o None."""
    def stp(p): return p.diatonicNoteNum
    bass = min(ps, key=lambda p: p.ps)
    for r in sorted(set(ps), key=lambda p: (p.name, p.ps)):
        steps = {(stp(p) - stp(r)) % 7 for p in ps}
        if steps <= {0, 2, 4, 6} and 2 in steps or steps == {0, 2, 6}:
            sem = {(p.pitchClass - r.pitchClass) % 12 for p in ps}
            sev = 6 in steps
            third = 4 if 4 in sem else 3 if 3 in sem else None
            fifth = 6 if 6 in sem else 8 if 8 in sem else 7
            q = {(4, 7): 'M', (3, 7): 'm', (3, 6): 'd', (4, 8): 'A'}.get((third, fifth), '?')
            if sev: q += {11: '/M7', 10: '7', 9: '°7'}.get(next(x for x in sem if x in (9, 10, 11)), '7')
            inv = {0: 0, 2: 1, 4: 2, 6: 3}[(stp(bass) - stp(r)) % 7]
            return r, inv, q, sev
    return None


def posizione(off, barlen, beat):
    return 'batt.%d:%g' % (off // barlen + 1, (off % barlen) / beat + 1)


def analyze(fn, bi, line, content, env):
    g = partilate_groups(content)
    if g is None:
        return []
    F = []

    def add(sev, cod, msg, off=None):
        F.append(dict(file=fn, block=bi, line=line, env=env, sev=sev, cod=cod, msg=msg,
                      pos=posizione(off, barlen, beat) if off is not None else ''))

    tm = re.search(r'\\time\s+(\d+)/(\d+)', g[0])
    barlen, beat = (int(tm.group(1)) * 4 / int(tm.group(2)), 4 / int(tm.group(2))) if tm else (4, 1)
    km = re.search(r'\\key\s+(\w+)\s+\\(major|minor)', g[0])
    tonic = None
    if km:
        n = re.fullmatch(r'(do|re|mi|fa|sol|la|si)(dd|dies|diesis|d|bb|bemolle|b|)', km.group(1))
        tonic = m21pitch.Pitch(STEP[n.group(1)] + ACC[n.group(2)] + '4')
    minor = bool(km and km.group(2) == 'minor')

    voci = dict(zip(VOCI, [parse_voice(g[i]) for i in (1, 2, 3, 4)]))
    tot = {v: sum(e[1] for e in ev) for v, ev in voci.items()}
    if len(set(tot.values())) > 1:
        add('ERR', 'LUNGHEZZA', 'voci di durata diversa: ' + ', '.join('%s=%g' % kv for kv in tot.items()))
        return F
    total = tot['S']
    labels = parse_labels(g[5], 'lyr')
    figs = parse_labels(g[6], 'fig')
    for nm, lst in (('analisi', labels), ('cifratura', figs)):
        t = sum(x[1] for x in lst)
        if t > total + 1e-6:
            add('WARN', 'LUNGHEZZA', '%s dura %g quarti, voci %g' % (nm, t, total))

    def sounding(v, off):
        for o, d, p in voci[v]:
            if o <= off + 1e-9 < o + d - 1e-9:
                return p
    onsets = sorted({e[0] for ev in voci.values() for e in ev})
    sl = [{v: sounding(v, o) for v in VOCI} for o in onsets]

    if VERBOSE:
        for j, (o, s_) in enumerate(zip(onsets, sl)):
            l = next((t for lo, ld, t in labels if lo <= o + 1e-9 < lo + ld), '')
            f = next((t for lo, ld, t in figs if lo <= o + 1e-9 < lo + ld), '')
            print('  %-10s %s  %-16s %-12s %s' % (posizione(o, barlen, beat), ' '.join('%-5s' % (s_[v].nameWithOctave if s_[v] else '-') for v in VOCI),
                  CH_STR(sl, j), l, f))

    # --- estensione, incroci, spaziatura
    for o, s in zip(onsets, sl):
        for v in VOCI:
            p = s[v]
            if p is None: continue
            lo, hi = RANGE[v]
            if v == 'T' and p.ps > hi:
                add('ERR', 'R2-TENORE', 'tenore %s oltre mi\'' % p.nameWithOctave, o)
            elif not lo <= p.ps <= hi:
                add('WARN', 'ESTENSIONE', '%s fuori estensione: %s' % (v, p.nameWithOctave), o)
        for hi_v, lo_v in zip(VOCI, VOCI[1:]):
            a, b = s[hi_v], s[lo_v]
            if a and b and a.ps <= b.ps:
                add('ERR', 'INCROCIO', '%s (%s) non sopra %s (%s)' % (hi_v, a.nameWithOctave, lo_v, b.nameWithOctave), o)
        for hi_v, lo_v in (('S', 'A'), ('A', 'T')):
            a, b = s[hi_v], s[lo_v]
            if a and b and a.ps - b.ps > 12:
                add('WARN', 'SPAZIATURA', '%s-%s oltre l\'ottava' % (hi_v, lo_v), o)

    # --- moto: parallele, nascoste, salti
    for k in range(1, len(sl)):
        a, b, o = sl[k - 1], sl[k], onsets[k]
        for i, v1 in enumerate(VOCI):
            for v2 in VOCI[i + 1:]:
                if None in (a[v1], a[v2], b[v1], b[v2]): continue
                m1, m2 = b[v1].ps - a[v1].ps, b[v2].ps - a[v2].ps
                if m1 == 0 or m2 == 0: continue
                i0, i1 = (a[v1].ps - a[v2].ps) % 12, (b[v1].ps - b[v2].ps) % 12
                for cls, nome in ((7, '5e'), (0, '8e')):
                    if i0 == cls and i1 == cls:
                        retto = m1 * m2 > 0
                        add('ERR' if retto else 'WARN', 'PARALLELE', '%s %s %s-%s' % (nome, 'parallele' if retto else 'per moto contrario', v1, v2), o)
                if i1 in (0, 7) and i0 != i1 and m1 * m2 > 0 and (v1, v2) == ('S', 'B') and abs(m1) > 2:
                    add('WARN', 'NASCOSTE', '%s nascosta S-B (salto al soprano)' % ('5a' if i1 == 7 else '8a'), o)
        for v in VOCI:
            if None in (a[v], b[v]): continue
            d = abs(b[v].ps - a[v].ps)
            steps = abs(b[v].diatonicNoteNum - a[v].diatonicNoteNum)
            if d > 12 and v != 'B':
                add('WARN', 'SALTO', '%s salta di %d semitoni' % (v, d), o)
            if steps == 1 and d == 3 and v != 'B':
                add('WARN', 'SECONDA-ECC', '%s: seconda eccedente' % v, o)
            if d == 6 and v != 'B':
                add('WARN', 'TRITONO', '%s: salto di tritono' % v, o)

    # --- accordi, analisi, cifratura
    ch = []
    for o, s in zip(onsets, sl):
        ps = [s[v] for v in VOCI]
        ch.append(find_root(ps) if None not in ps else None)

    def chord_at(off):
        idx = max(j for j, o in enumerate(onsets) if o <= off + 1e-9)
        return idx

    KEY = re.compile(r'^(do|re|mi|fa|sol|la|si)\s*([#b]?)\s*(M|m):\s*(.*)$', re.I)
    tonics = [tonic] * len(sl)
    for off, d, txt in labels:  # etichette "La m:" cambiano tonalità da lì in poi
        km2 = KEY.match(txt.strip())
        if km2:
            t_ = m21pitch.Pitch(STEP[km2.group(1).lower()] + {'#': '#', 'b': '-', '': ''}[km2.group(2)] + '4')
            for k in range(chord_at(off), len(sl)): tonics[k] = t_
    for off, d, txt in labels:
        txt = KEY.sub(r'\4', txt.strip())
        t = normalize_label(txt)
        m = LABEL.match(t)
        if not m or not tonic: continue
        j = chord_at(off); tonic = tonics[j]
        c = ch[j]
        if c is None: continue
        root, inv, q, sev = c
        deg_l = DEG[m.group(1).lower()]
        key_t = tonic
        if m.group(4):  # secondaria X/Y
            ty = DEG[m.group(4).lower()]
            key_t = next(p for p in [m21pitch.Pitch(STEPS[(tonic.diatonicNoteNum - 1 + ty - 1) % 7] + '4')])
        deg_c = (root.diatonicNoteNum - key_t.diatonicNoteNum) % 7 + 1
        fg_ = next((t_ for o_, d_, t_ in figs if o_ <= off + 1e-9 < o_ + d_), '')
        expl = m.group(3) is not None and not (m.group(3) == '7' and fg_.startswith('<'))  # altrimenti l'inversione la dà la cifratura
        want_inv = {None: 0, '7': 0, '6': 1, '65': 1, '6/5': 1, '43': 2, '4/3': 2, '6/4': 2, '64': 2, '42': 3, '4/2': 3, '2': 3}[m.group(3)]
        want_sev = m.group(3) in ('7', '65', '6/5', '43', '4/3', '42', '4/2', '2')
        e = []
        if deg_l != deg_c: e.append('grado: analisi %s, accordo %s' % (m.group(1), root.name))
        if expl and want_inv != inv: e.append('rivolto: analisi %s, accordo %d° rivolto' % (m.group(3) or 'fond.', inv))
        if expl and want_sev != sev: e.append('settima: analisi %s' % ('con' if want_sev else 'senza'))
        if m.group(2) in ('°', 'ø') and not q.startswith('d'): e.append('analisi "%s" ma accordo %s' % (m.group(2), q))
        if e:
            add('WARN', 'ANALISI', '"%s": %s' % (txt, '; '.join(e)), onsets[j])
    for off, d, txt in figs:
        j = chord_at(off); c = ch[j]
        if c is None or not txt.startswith('<'): continue
        F_ = {int(x) for x in re.findall(r'\d+', txt)}
        F_ = {n - 7 if n > 8 else n for n in F_} - {8, 1}
        root, inv, q, sev = c
        ok = {(False, 0): [set(), {5, 3}, {5}, {3}], (False, 1): [{6}, {6, 3}], (False, 2): [{6, 4}],
              (True, 0): [{7}, {7, 5, 3}, {7, 5}, {7, 3}], (True, 1): [{6, 5}, {6, 5, 3}], (True, 2): [{4, 3}, {6, 4, 3}],
              (True, 3): [{4, 2}, {2}, {6, 4, 2}]}[(sev, inv)]
        if F_ not in ok:
            add('WARN', 'CIFRATURA', 'cifra %s ma accordo %s%s al %d° rivolto' % (txt, root.name, ' (7a)' if sev else '', inv), onsets[j])
    for j, c in enumerate(ch):  # cifra mancante
        if c and (c[3] or c[1]) and j and sl[j - 1]['B'] and sl[j]['B'].ps != sl[j - 1]['B'].ps:
            f = next((t for o, d, t in figs if o <= onsets[j] + 1e-9 < o + d - 1e-9), 's')
            if not f.startswith('<'):
                add('INFO', 'CIFRA-MANCANTE', 'accordo %s%s al %d° rivolto senza cifra' % (c[0].name, ' (7a)' if c[3] else '', c[1]), onsets[j])

    # --- sensibile e settima
    for j, c in enumerate(ch):
        if not c or not tonics[j]: continue
        tonic = tonics[j]
        root, inv, q, sev = c
        deg = (root.diatonicNoteNum - tonic.diatonicNoteNum) % 7 + 1
        nxt = sl[j + 1] if j + 1 < len(sl) else None
        if deg in (5, 7) and q not in ('m', 'd', 'A') or (deg == 7 and q.startswith('d')) or (deg == 5 and q in ('M', '7')):
            lt = [v for v in VOCI if sl[j][v] and sl[j][v].pitchClass == (tonic.pitchClass - 1) % 12]
            if len(lt) > 1:
                add('WARN', 'SENSIBILE-RADDOPPIATA', 'sensibile raddoppiata (%s)' % '+'.join(lt), onsets[j])
            if nxt and ch[j + 1] and ch[j + 1][0].pitchClass == tonic.pitchClass:
                for v in lt:
                    if v in ('S', 'B') and nxt[v] and nxt[v].ps - sl[j][v].ps != 1:
                        add('WARN', 'SENSIBILE-NON-RISOLTA', 'sensibile in %s non sale di semitono' % v, onsets[j + 1])
        if sev and nxt and ch[j + 1] and ch[j + 1][0].pitchClass != root.pitchClass:
            v7 = [v for v in VOCI if sl[j][v] and (sl[j][v].diatonicNoteNum - root.diatonicNoteNum) % 7 == 6]
            for v in v7:
                dd = sl[j][v].ps - nxt[v].ps if nxt[v] else 1
                if dd not in (1, 2):
                    add('WARN', 'SETTIMA-NON-RISOLTA', 'settima in %s non scende di grado' % v, onsets[j + 1])
    return F


VERBOSE = False


def CH_STR(sl, j):
    ps = [sl[j][v] for v in VOCI]
    c = find_root(ps) if None not in ps else None
    return '%s %s inv%d' % (c[0].name, c[2], c[1]) if c else '?'


def blocchi(path):
    text = open(path).read()
    for m in re.finditer(r'\\musica\{', text):
        i, d = m.end(), 1
        while i < len(text) and d:
            d += (text[i] == '{') - (text[i] == '}'); i += 1
        stack = []
        for e in re.finditer(r'\\(begin|end)\{(errore|esempio|regola|definizione|fisica|matematica)\}', text[:m.start()]):
            stack.append(e.group(2)) if e.group(1) == 'begin' else stack and stack.pop()
        yield text[:m.start()].count('\n') + 1, text[m.end():i - 1], (stack[-1] if stack else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter'); ap.add_argument('--block'); ap.add_argument('--json', action='store_true')
    ap.add_argument('--min', default='WARN', choices=['INFO', 'WARN', 'ERR'])
    a = ap.parse_args()
    global VERBOSE
    VERBOSE = bool(a.block)
    rank = {'INFO': 0, 'WARN': 1, 'ERR': 2}
    res = []
    for fn in sorted(glob.glob('Capitoli/*.tex')):
        num = os.path.basename(fn).split('_')[0]
        if a.chapter and num != a.chapter: continue
        for bi, (line, content, env) in enumerate(blocchi(fn), 1):
            if a.block and a.block != '%s:%d' % (num, bi): continue
            res += analyze(fn, bi, line, content, env)
    res = [f for f in res if rank[f['sev']] >= rank[a.min]]
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1)); return 0
    else:
        last = None
        for f in res:
            h = (f['file'], f['block'])
            if h != last:
                print('\n### %s blocco #%d (riga %d)%s' % (f['file'], f['block'], f['line'], ' [in %s]' % f['env'] if f['env'] else ''))
                last = h
            print('  %-4s %-22s %-10s %s' % (f['sev'], f['cod'], f['pos'], f['msg']))
    err = [f for f in res if f['sev'] == 'ERR' and f['env'] != 'errore']
    print('\n%d segnalazioni (%d ERR fuori da `errore`)' % (len(res), len(err)))
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main())
