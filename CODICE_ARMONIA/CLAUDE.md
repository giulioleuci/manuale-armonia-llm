# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

No git repo, no tests, no lint, no CI. Run as scripts from repo root.

```bash
pip install reportlab fonttools        # or: pip install -r requirements.txt
python3 build_all.py                   # all PDFs, both orientations -> out/orizzontale/, out/verticale/
python3 build1.py                      # one PDF, landscape (default)
PDF_ORIENT=verticale python3 build1.py # one PDF, portrait
```

Verify a change by building and opening the PDF. No automated check exists.

## Architecture

Pipeline: `dataN.py` (4-voice chord data) -> `solver.py` (voice-leading DP) -> `engrave.py` (grand-staff drawing) -> `doc.py` (page layout) -> PDF, assembled by `build1/2/3.py`.

- `build1/2/3.py` each produce one PDF and hold its text and page content. `build_all.py` runs all three once per orientation via subprocess.
- Orientation is read from env `PDF_ORIENT` in `doc.py` (`ORIENT`, `PORTRAIT`, page size `PW/PH`). `build*.py` branch on `PORTRAIT` for layout (e.g. `d.blocks(..., dx=...)` vs stacked). Any layout change must work in both orientations.
- `solver.py` generates candidate voicings per chord spec (`candidates`), then runs DP across chords with `trans_ok` (hard rules: `check_pair` from `music.py`, leap limits, per-voice allowed note-to-note moves via `rules`) and `cost`/`static_cost` (soft preferences). Voice ranges are the fixed `URANGE` dict. Voice order everywhere is `(S, A, T, B)`.
- `music.py` holds pitch math (`midi`, `pname`, `with_octave`, `LETTERS`) and `check_pair` (parallel/hidden fifths and octaves, crossing). Other modules rely on these helpers.
- `engrave.py` draws staves, note heads, accidentals and arrows. Accidental state is tracked per `(letter, octave)` via `layout_accs`/`draw_acc`. Clefs and accidentals are outlines from `glyphs.py` (fonttools). Voice colors are `VCOL`.
- `scales.py` builds diatonic seventh-chord rows (`scale_row`, `SCALES`) used by build2/3.

Solver rules and engraving are coupled: a voicing the solver rejects never reaches `engrave.py`, and display assumptions (e.g. staff spacing `S`, `GAP`) are not checked by the solver. Change both sides together.

## Gotchas

- System fonts are hardcoded to Linux paths in `engrave.py` and `glyphs.py`. Missing fonts fail at import (`pdfmetrics.registerFont`). Adjust those paths on other machines; they are not bundled.
- Text content is Italian; keep new prose in Italian to match the existing PDFs.
- Output goes to `out/`, which is generated. `__pycache__/` is also generated.
- `AGENTS.md` has overlapping project notes; this file is the Claude-facing summary.
