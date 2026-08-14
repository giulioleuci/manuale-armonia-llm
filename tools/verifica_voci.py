#!/usr/bin/env python3
"""Verifica la scrittura a quattro parti dei blocchi partilate.

Regole obbligatorie:
  R1. Nessun incrocio/unisono: Basso < Tenore < Contralto < Soprano.
  R2. Il Tenore non supera mi' (E4): linee di guida solo per do'/re' (mi' tollerato).

Uso:
  python3 tools/verifica_voci.py            # tutti i capitoli
  python3 tools/verifica_voci.py --chapter 04   # solo un capitolo (numero file)
  python3 tools/verifica_voci.py --verbose  # stampa tutte le verticali dei blocchi falliti
  python3 tools/verifica_voci.py --json     # output macchina (per CI/commit check)

Exit code: 0 se nessuna violazione, 1 altrimenti.
"""
import argparse, glob, json, re, sys

PITCH = {
    'do': 0, 'dod': 1, 'dodies': 1, 'reb': 1, 'rebemolle': 1,
    're': 2, 'red': 3, 'redies': 3, 'mib': 3, 'mibemolle': 3,
    'mi': 4, 'fa': 5, 'fad': 6, 'fadies': 6, 'solb': 6, 'solbemolle': 6,
    'sol': 7, 'sold': 8, 'soldies': 8, 'lab': 8, 'labemolle': 8,
    'la': 9, 'lad': 10, 'ladies': 10, 'sib': 10, 'sibemolle': 10, 'si': 11,
}
NAMES = {0:'do',1:'dod',2:'re',3:'red',4:'mi',5:'fa',6:'fad',7:'sol',8:'sold',9:'la',10:'sib',11:'si'}

def midi_to_name(m):
    """Converte un numero MIDI in nome italiano stile LilyPond (do' = C4 = 60)."""
    octv = (m - 36) // 12
    pc = (m - 36) % 12
    if octv == 0:
        return NAMES[pc] + ','  # ottava sotto il Do centrale
    if octv == 1:
        return NAMES[pc]
    return NAMES[pc] + "'" * (octv - 1)

def parse_voice(notes):
    out = []
    for name, octv in re.findall(r"([a-z]+)('+|,+)?", notes):
        if name not in PITCH:
            continue
        up = octv.count("'") if octv else 0
        down = octv.count(",") if octv else 0
        out.append(36 + 12 * (1 + up) + PITCH[name] - 12 * down)
    return out

def blocks_in(text):
    out = []
    for m in re.finditer(r'\\musica\{', text):
        start = m.end()
        depth, i = 1, start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        out.append(text[start:i - 1])
    return out

def partilate_groups(content):
    idx = content.find('partilate')
    if idx < 0:
        return None
    tail = content[idx + len('partilate'):]
    i, groups = 0, []
    while i < len(tail):
        if tail[i] == '{':
            d, j = 1, i + 1
            while j < len(tail) and d > 0:
                if tail[j] == '{':
                    d += 1
                elif tail[j] == '}':
                    d -= 1
                j += 1
            groups.append(tail[i + 1:j - 1])
            i = j
        else:
            i += 1
    return groups if len(groups) >= 7 else None

def analyze(fn, block_idx, content, verbose):
    groups = partilate_groups(content)
    if groups is None:
        return None
    s = parse_voice(groups[1]); a = parse_voice(groups[2])
    t = parse_voice(groups[3]); b = parse_voice(groups[4])
    n = min(len(s), len(a), len(t), len(b))
    if n == 0:
        return None
    hard_beats, warn_beats = [], []
    rows = []
    for k in range(n):
        hard, warn = False, False
        if t[k] >= a[k] or a[k] >= s[k]:
            hard = True
            hard_beats.append(k + 1)
        if not (b[k] < t[k]):  # il basso non è la voce più grave
            warn = True
        if t[k] - b[k] > 19:  # dodicesima = 19 semitoni
            warn = True
        if a[k] - t[k] > 12 or s[k] - a[k] > 12:
            warn = True
        if warn:
            warn_beats.append(k + 1)
        rows.append((midi_to_name(s[k]), midi_to_name(a[k]), midi_to_name(t[k]), midi_to_name(b[k])))
    tenor_max = max(t)
    over = tenor_max - 64  # E4 = 64
    rows_full = ['  b%-2d  S:%s  A:%s  T:%s  B:%s' % (k + 1, r[0], r[1], r[2], r[3])
                 for k, r in enumerate(rows)]
    return {
        'file': fn, 'block': block_idx + 1,
        'hard_beats': hard_beats,
        'warn_beats': warn_beats,
        'tenor_max': midi_to_name(tenor_max), 'tenor_over_e4': over > 0,
        'rows': rows_full,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter', help='filtra per capitolo (numero file, es. 04)')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    bad = []
    files = sorted(glob.glob('Capitoli/*.tex'))
    if args.chapter:
        files = [f for f in files if f.split('_')[0].split('/')[-1] == args.chapter]
    for fn in files:
        text = open(fn).read()
        for bi, content in enumerate(blocks_in(text)):
            r = analyze(fn, bi, content, args.verbose)
            if not r:
                continue
            if r['hard_beats'] or r['tenor_over_e4'] or r['warn_beats']:
                r['warn_only'] = not (r['hard_beats'] or r['tenor_over_e4'])
                bad.append(r)

    if args.json:
        print(json.dumps([{ 'file': r['file'], 'block': r['block'],
                            'hard_beats': r['hard_beats'],
                            'warn_beats': r['warn_beats'],
                            'tenor_max': r['tenor_max'],
                            'tenor_over_e4': r['tenor_over_e4'],
                            'warn_only': r['warn_only'] } for r in bad]))
    else:
        for r in bad:
            tag = ' SOLO AVVISI' if r['warn_only'] else ''
            print("### %s  blocco #%d%s" % (r['file'], r['block'], tag))
            print("  INCROCI ai beat: %s   TENORE max: %s %s" % (
                r['hard_beats'] or '-', r['tenor_max'],
                '(SUPERA mi\'!)' if r['tenor_over_e4'] else ''))
            if r['warn_beats']:
                print("  warning (basso non piu' grave / spaziature): beat %s" % r['warn_beats'])
            if args.verbose:
                for line in r['rows']:
                    print(line)
    print("Blocchi SATB con violazioni: %d" % len(bad))
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
