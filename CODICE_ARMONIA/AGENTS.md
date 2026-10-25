# AGENTS.md

## Project
PDF generator for tonal harmony exercises (voice-leading, seventh chords, Neapolitan, augmented sixths). Pure Python, outputs to `out/`.

## Dependencies
- `reportlab`, `fonttools` (see `requirements.txt`)
- System fonts referenced in `engrave.py`/`glyphs.py` (Linux paths): `DejaVu Sans` at `/usr/share/fonts/truetype/dejavu/`, `FreeSerif` at `/usr/share/fonts/truetype/freefont/FreeSerif.ttf`. Must exist or font registration will fail.

## Build
```bash
python3 build_all.py                          # both orientations
python3 build1.py                             # landscape only (default)
PDF_ORIENT=verticale python3 build1.py        # portrait only
```
`build_all.py` runs `build1/2/3.py` for `orizzontale` and `verticale`, writing to `out/orizzontale/` and `out/verticale/`. Scripts import from local modules and write PDFs via `Doc` (`doc.py`) + engraving (`engrave.py`); folders are created as needed.

## Architecture
- `music.py`: pitch/interval/spelling, parallel/hidden fifths/octaves, voice-crossing, range checks
- `solver.py`: DP voice-leading solver. Generates candidates per chord spec (`candidates`), prunes by voice ranges/spacing/crossing, scores with `cost`/`static_cost`, enforces transitions via `trans_ok` (rules per move). Uses fixed `URANGE` per voice (S/A/T/B).
- `scales.py`: scale rows/diatonic seventh-chord constructions
- `glyphs.py`: draw clefs/accidentals as font glyph outlines (via fonttools)
- `engrave.py`: grand staff layout, note heads/stems/ledger lines, key signatures, accidentals, arrows/labels, colored voices (`VCOL`), voice-leading arrows
- `doc.py`: pagination/layout helpers (`Doc`, `page`, `cols`, `blocks`, `system`, tables)
- `data1.py`, `data23.py`: example 4-voice realizations (S,A,T,B)
- `build1.py`,`build2.py`,`build3.py`: assemble content per PDF

## Conventions / Gotchas
- Voice order in chord tuples is `(S, A, T, B)`. `midi()`/`pname()`/`step()` from `music.py` are used throughout.
- Ranges/spacings are enforced by `solver` (`m[0]>m[1]>m[2]>m[3]`, min soprano/alto gap, max leaps). Tight coupling between `solver` rules and `engrave` display.
- Key signatures/accidentals handled by `layout_accs` + `draw_acc`; memory tracks last accidental per `(letter, octave)`.
- Fonts hardcoded to system paths (not bundled). If missing, PDF generation fails at import/time of registration.
- No tests/lint/CI present. No package setup (`setup.py`/`pyproject.toml`) — run as scripts from repo root.
