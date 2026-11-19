#!/usr/bin/env python3
"""
Generatore batch di tutti gli esempi musicali in PDF vettoriali per il manuale.
"""
import os, sys

# Ensure root dir is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tools.esempi.dati import ESEMPI
from tools.esempi import genera
from tools.armonia.render_snippet import render_satb_snippet, render_block_snippet

def build_all_esempi(out_dir=None, limit=None):
    if out_dir is None:
        out_dir = os.path.join(BASE_DIR, 'esempi_gen')
    os.makedirs(out_dir, exist_ok=True)

    generated = []
    items = list({**ESEMPI, **genera()}.items())
    if limit is not None:
        items = items[:limit]

    for ex_id, spec in items:
        out_path = os.path.join(out_dir, f"{ex_id}.pdf")
        ex_type = spec.get('type', 'satb')
        nacc = spec.get('nacc', 0)
        caps = spec.get('caps')
        marks = spec.get('marks')
        chords = spec.get('chords', [])
        dx = spec.get('dx')

        if ex_type == 'satb':
            render_satb_snippet(chords, out_path, nacc=nacc, caps=caps, marks=marks, **({'dx': dx} if dx else {}))
        else:
            clef = spec.get('clef', 'treble')
            render_block_snippet(chords, out_path, nacc=nacc, clef=clef, caps=caps, **({'dx': dx} if dx else {}))

        generated.append(out_path)

    return generated

if __name__ == '__main__':
    paths = build_all_esempi()
    print(f"Generati con successo {len(paths)} esempi in PDF vettoriale.")
