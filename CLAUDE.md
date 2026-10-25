# Harmony Manual (Appunti sparsi di Armonia)

This project is a comprehensive manual on tonal harmony, blending musical theory with insights from physics (acoustics) and mathematics (modular arithmetic).

## Project Overview

The document is a LaTeX-based book titled **"Appunti sparsi di Armonia"**. It uses a custom Python engraving engine (`tools/armonia/`, derived from `CODICE_ARMONIA`) to render musical examples into vector PDFs (`esempi_gen/`), included in LaTeX via the `\musica{id}` macro.

### Key Technologies

*   **LaTeX (LuaLaTeX):** The primary typesetting engine.
*   **Custom Python Engraver (`tools/armonia/`):** Based on ReportLab and FontTools for vector musical snippets (SATB grand staff, voice-leading arrows, figured bass, Roman numerals).
*   **TikZ:** Used for geometric diagrams (e.g., the Circle of Fifths).
*   **tcolorbox:** Provides stylized containers for definitions, examples, and technical notes.

## Language and Localization

*   **Language:** The project is written entirely in **Italian**. All technical terms must follow Italian musical nomenclature (e.g., "Sesta Napoletana", "Settima di Dominante").
*   **Musical Nomenclature:** Use Italian note names (Do, Re, Mi, Fa, Sol, La, Si).

## Building and Running

### Prerequisites

1.  **TeX Live:** A full TeX distribution (e.g., TeX Live 2023 or newer).
2.  **LuaLaTeX:** The document is compiled with `lualatex`.
3.  **Python 3:** With `reportlab` and `fonttools` (`pip install reportlab fonttools`).

### Generation and Compilation Commands

1.  **Generate musical examples:**
```bash
python3 tools/build_esempi.py
```

2.  **Compile the manual:**
```bash
lualatex manuale.tex
```

*Note: LilyPond and `--shell-escape` are no longer required.*

## Development Conventions

### Musical Symbols and Formatting

*   **Sharps and Flats in Text:** For musical alterations within the LaTeX text, **always use the commands `\sharp` and `\flat`** (often within math mode: `$\sharp$` and `$\flat$`).
    *   *Do not* use literal Unicode characters (♯, ♭) or simple characters (#, b) in the main body text.
    *   Example: `Do$\sharp$`, `Si$\flat$`.

### Musical Examples Integration

Musical examples are defined in `tools/esempi_data.py` and included in LaTeX via:
```latex
\begin{esempio}[Titolo esempio]
    \label{ex:mio_esempio}
    \musica{es_capXX_YY}
\end{esempio}
```
    { do1 }                      % 5. Bass
    \lyricmode { I IV }          % 6. Analysis (Roman numerals/Degrees)
    \figuremode { s1 <6> }       % 7. Figured Bass (Numbers)
```

### Custom LaTeX Environments

The project uses several `tcolorbox` environments to categorize information:

*   `definizione`: Formal music theory definitions.
*   `esempio`: Musical examples (often including LilyPond code).
*   `regola`: Theoretical rules.
*   `errore`: Common mistakes to avoid.
*   `fisica`: Scientific insights into acoustics.
*   `matematica`: Mathematical formalizations of musical concepts.

### Organization

*   **Modular Chapters:** Keep individual chapters in the `Capitoli/` directory.
*   **Cross-references:** Use `\label` and `\ref` extensively to link concepts across the manual.
*   **Shared Definitions:** Update `definizioni.ly` for any global LilyPond graphical overrides or functions.
