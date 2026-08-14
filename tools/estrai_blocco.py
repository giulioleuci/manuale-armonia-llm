#!/usr/bin/env python3
r"""Estrae il blocco \musica{...} #N da un file .tex e lo scrive come .ly autonomo."""
import re, sys, subprocess, os, tempfile

def blocks_in(text):
    out = []
    for m in re.finditer(r'\\musica\{', text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(text) and depth > 0:
            if text[i] == '{': depth += 1
            elif text[i] == '}': depth -= 1
            i += 1
        out.append(text[start:i - 1])
    return out

def main():
    fn, n = sys.argv[1], int(sys.argv[2])
    text = open(fn).read()
    blocks = blocks_in(text)
    if not 1 <= n <= len(blocks):
        sys.exit('blocco fuori intervallo: 1..%d' % len(blocks))
    content = blocks[n - 1]
    idx = content.find('partilate')
    if idx >= 0:
        # i gruppi dopo \partilate: [0] = global (tonalità+tempo),
        # [1..4] = soprano/alto/tenore/basso, [5] = analisi, [6] = basso numerato
        tail = content[idx + len('partilate'):]
        groups, i = [], 0
        while i < len(tail):
            if tail[i] == '{':
                d, j = 1, i + 1
                while j < len(tail) and d > 0:
                    if tail[j] == '{': d += 1
                    elif tail[j] == '}': d -= 1
                    j += 1
                groups.append(tail[i + 1:j - 1])
                i = j
            else:
                i += 1
        key, S, A, T, B = groups[0], groups[1], groups[2], groups[3], groups[4]
        ly = (
            '\\version "2.24.0"\n'
            '\\include "definizioni.ly"\n'
            '\\paper { indent = 0\\mm ragged-right = ##t }\n'
            'vS = { %s %s }\n' % (key, S) +
            'vA = { %s }\n' % A +
            'vT = { %s }\n' % T +
            'vB = { %s }\n' % B +
            '\\new PianoStaff <<\n'
            '  \\new Staff << \\vS \\vA >>\n'
            '  \\new Staff << \\clef bass \\vT \\vB >>\n'
            '>>\n'
        )
    else:
        # blocco \new Staff: lo si compila direttamente
        ly = ('\\version "2.24.0"\n'
              '\\include "definizioni.ly"\n'
              '\\paper { indent = 0\\mm ragged-right = ##t }\n' + content + '\n')
    tmp = tempfile.mktemp(suffix='.ly')
    open(tmp, 'w').write(ly)
    if len(sys.argv) > 3 and sys.argv[3] == '--run':
        os.makedirs('/tmp/opencode/lycheck', exist_ok=True)
        rc = subprocess.run(['lilypond', '--silent', '-o', '/tmp/opencode/lycheck', tmp]).returncode
        os.remove(tmp)
        sys.exit(rc)
    print(ly)
    os.remove(tmp)

if __name__ == '__main__':
    main()
