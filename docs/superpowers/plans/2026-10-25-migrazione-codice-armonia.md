# Migrazione da LilyPond a Motore Custom CODICE_ARMONIA - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminare completamente la dipendenza da LilyPond e dal pacchetto `lyluatex`, integrando il motore di notazione Python di `CODICE_ARMONIA` per generare gli esempi musicali come PDF vettoriali da includere nel documento LaTeX.

**Architecture:** 
- Creazione di un modulo unificato in `tools/armonia/` derivato da `CODICE_ARMONIA` capace di esportare singoli snippet musicali in PDF ritagliati (`render_snippet`).
- Pipeline batch `tools/build_esempi.py` che genera i PDF vettoriali in `esempi_gen/`.
- Sostituzione della macro LaTeX `\musica` per includere direttamente i PDF compilati con `\includegraphics`, rimuovendo `lyluatex` dal preambolo.

**Tech Stack:** Python 3, ReportLab, fonttools, LaTeX (LuaLaTeX o standard pdfLaTeX senza `--shell-escape`).

---

### Task 1: Modulo di Rendering Vettoriale Snippet (`tools/armonia/`)

**Files:**
- Create: `tools/armonia/__init__.py`
- Create: `tools/armonia/render_snippet.py`
- Copy/Modify: `tools/armonia/engrave.py`, `tools/armonia/music.py`, `tools/armonia/glyphs.py` (da `CODICE_ARMONIA/`)
- Test: `tests/test_render_snippet.py`

**Interfaces:**
- Produces: `render_snippet(spec: dict, out_path: str) -> str`: compila un esempio musicale (grand-staff a 4 voci o rigo singolo) producendo un PDF con bounding box compatto (senza margini pagina vuoti).

- [ ] **Step 1: Scrivere il test per il rendering di uno snippet SATB**
```python
# tests/test_render_snippet.py
import os
from tools.armonia.render_snippet import render_satb_snippet

def test_render_satb_snippet(tmp_path):
    out_pdf = tmp_path / "test_chord.pdf"
    chords = [
        {'v': ['C5', 'G4', 'E4', 'C3'], 'rn': 'I', 'fig': []},
        {'v': ['B4', 'G4', 'F4', 'D3'], 'rn': 'V7', 'fig': ['7']}
    ]
    render_satb_snippet(chords, str(out_pdf))
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
```

- [ ] **Step 2: Eseguire il test per verificare il fallimento**
Run: `pytest tests/test_render_snippet.py`
Expected: FAIL (modulo non trovato).

- [ ] **Step 3: Implementare `render_satb_snippet` e adattività del canvas tight**
Integrare il codice di `engrave.py` in `tools/armonia/` configurando ReportLab su un canvas di dimensioni calibrate sull'altezza e larghezza del sistema musicale (`system_height()` e larghezza dinamica), evitando pagine A4 intere.

- [ ] **Step 4: Eseguire il test per verificare il successo**
Run: `pytest tests/test_render_snippet.py`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add tools/armonia tests/test_render_snippet.py
git commit -m "feat(armonia): add standalone snippet renderer from CODICE_ARMONIA"
```

---

### Task 2: Catalogo Esempi e Generatore Batch (`tools/build_esempi.py`)

**Files:**
- Create: `tools/esempi_data.py` (definizioni strutturate degli esempi musicali dei capitoli)
- Create: `tools/build_esempi.py`
- Test: `tests/test_build_esempi.py`

**Interfaces:**
- Consumes: `render_satb_snippet`, `render_block_snippet` da `tools.armonia.render_snippet`
- Produces: cartella `esempi_gen/` contenente tutti i PDF vettoriali `es_capXX_YY.pdf`.

- [ ] **Step 1: Scrivere il test di generazione batch**
```python
# tests/test_build_esempi.py
from tools.build_esempi import build_all_esempi
import os

def test_build_all_esempi(tmp_path):
    out_dir = str(tmp_path / "out")
    generated = build_all_esempi(out_dir=out_dir, limit=2)
    assert len(generated) == 2
    for path in generated:
        assert os.path.exists(path)
```

- [ ] **Step 2: Eseguire il test per verificare il fallimento**
Run: `pytest tests/test_build_esempi.py`
Expected: FAIL.

- [ ] **Step 3: Popolare `tools/esempi_data.py` e implementare `tools/build_esempi.py`**
Convertire gli esempi dai capitoli (iniziando dai 70 esempi `\partilate` e gestendo i 21 singoli) nelle strutture dati Python supportate dal motore.

- [ ] **Step 4: Eseguire la generazione batch e verificare i file generati**
Run: `pytest tests/test_build_esempi.py && python3 tools/build_esempi.py`
Expected: Tutti gli esempi compilati correttamente in `esempi_gen/`.

- [ ] **Step 5: Commit**
```bash
git add tools/esempi_data.py tools/build_esempi.py tests/test_build_esempi.py
git commit -m "feat: batch builder for harmony musical examples"
```

---

### Task 3: Sostituzione Macro LaTeX e Rimozione LilyPond

**Files:**
- Modify: `preamble.tex` (rimozione `lyluatex`)
- Modify: `music_macros.tex` (aggiornamento definizione `\musica`)
- Modify: `Capitoli/*.tex` (sostituzione blocchi inline `\musica{...}` con riferimenti all'ID dell'esempio `\musica{es_capXX_YY}`)
- Modify: `AGENTS.md` e `CLAUDE.md` / `GEMINI.md` (aggiornamento istruzioni di build)

**Interfaces:**
- Consumes: file PDF in `esempi_gen/`
- Produces: `manuale.pdf` compilabile senza `--shell-escape` e senza LilyPond installato.

- [ ] **Step 1: Aggiornare `music_macros.tex` e `preamble.tex`**
In `preamble.tex`, rimuovere:
```latex
\usepackage[
program=lilypond,
...
]{lyluatex}
```
In `music_macros.tex`, ridefinire:
```latex
\newcommand{\musica}[1]{%
    \begin{center}
        \includegraphics[max width=\textwidth]{esempi_gen/#1.pdf}%
    \end{center}
}
```

- [ ] **Step 2: Aggiornare le chiamate `\musica` nei capitoli**
Sostituire i blocchi di codice Lilypond con l'identificativo corrispondente (`\musica{es_cap02_01}`, etc.).

- [ ] **Step 3: Testare la compilazione LaTeX senza LilyPond**
Run: `lualatex manuale.tex`
Expected: Compilazione completata con codice 0 senza errori, tempo di esecuzione ridotto drasticamente, `manuale.pdf` generato e integro.

- [ ] **Step 4: Aggiornare la documentazione di progetto**
Aggiornare `AGENTS.md`, `GEMINI.md` rimuovendo il requisito di Lilypond e documentando il comando di rigenerazione esempi: `python3 tools/build_esempi.py`.

- [ ] **Step 5: Commit**
```bash
git add preamble.tex music_macros.tex Capitoli/ AGENTS.md GEMINI.md
git commit -m "refactor: replace LilyPond with custom Python engraving engine"
```
