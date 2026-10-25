#!/usr/bin/env python3
r"""Controlli sul testo italiano dei capitoli (ortografia meccanica, convenzioni del progetto, riferimenti).
Uso: python3 tools/lint_testo.py [--fix]   (--fix applica solo le correzioni sicure)
"""
import glob, re, sys

# (regex, sostituzione sicura | None, messaggio)
REGOLE = [
    (r'\bperchè\b', 'perché', 'accento'), (r'\bpoichè\b', 'poiché', 'accento'), (r'\baffinchè\b', 'affinché', 'accento'),
    (r'\bcioè\b', None, None),
    (r'\bnè\b', 'né', 'accento'), (r'\bsè\b', 'sé', 'accento'), (r'\bcosicchè\b', 'cosicché', 'accento'),
    (r'\bqual\'è\b', 'qual è', 'apostrofo'), (r'\bpò\b', "po'", 'apostrofo'),
    (r'[♯♭♮]', None, 'usare $\\sharp$ / $\\flat$ (CLAUDE.md)'),
    (r'\b(Do|Re|Mi|Fa|Sol|La|Si)#(?![A-Za-z])', None, 'usare $\\sharp$ invece di #'),
    (r'\b(Do|Re|Mi|Fa|Sol|La|Si)b\b', None, 'usare $\\flat$ invece di b'),
    (r' ([,.;:!?])(?=\s|$)', None, 'spazio prima della punteggiatura'),
    (r'\b(\w{2,}) \1\b', None, 'parola ripetuta'),
    (r'(?<!\\)\b(major|minor|tonic|dominant|subdominant|chord|leading tone)\b', None, 'termine inglese'),
    (r'\bsettima di sensibile\b', None, None),
]
FIX = '--fix' in sys.argv
refs, labels, tot = set(), set(), 0
for fn in sorted(glob.glob('Capitoli/*.tex')) + ['manuale.tex']:
    lines = open(fn).read().split('\n')
    out, in_ly = [], False
    for n, line in enumerate(lines, 1):
        code = re.sub(r'(?<!\\)%.*', '', line)
        labels.update(re.findall(r'\\label\{([^}]+)\}', code))
        refs.update((fn, n, r) for r in re.findall(r'\\(?:ref|pageref|autoref|eqref)\{([^}]+)\}', code))
        in_ly = in_ly or '\\musica{' in code
        if not in_ly:  # niente controlli dentro LilyPond
            for rx, rep, msg in REGOLE:
                if msg is None: continue
                for m in re.finditer(rx, code):
                    if FIX and rep is not None:
                        line = re.sub(rx, rep, line); break
                    print('%s:%d: %s: "%s"' % (fn, n, msg, m.group(0))); tot += 1
        if in_ly and code.strip() == '}' and not line.startswith(' ' * 8): in_ly = False
        out.append(line)
    if FIX: open(fn, 'w').write('\n'.join(out))
for fn, n, r in sorted(refs):
    if r not in labels:
        print('%s:%d: riferimento a etichetta inesistente: %s' % (fn, n, r)); tot += 1
dup = [l for l in labels if sum(open(f).read().count('\\label{%s}' % l) for f in glob.glob('Capitoli/*.tex')) > 1]
for l in dup: print('etichetta duplicata:', l); tot += 1
print('%d segnalazioni' % tot)
