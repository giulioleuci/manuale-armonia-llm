# Harmony Manual (Appunti sparsi di Armonia)

This project is a comprehensive manual on tonal harmony, blending musical theory with insights from physics (acoustics) and mathematics (modular arithmetic).

## Project Overview

The document is a LaTeX-based book titled **"Appunti sparsi di Armonia"**. It uses LilyPond for high-quality music notation integrated directly into the LaTeX source via the `lyluatex` package.

### Key Technologies

*   **LaTeX (LuaLaTeX):** The primary typesetting engine.
*   **LilyPond (v2.24.0+):** For musical notation.
*   **lyluatex:** The bridge between LaTeX and LilyPond.
*   **TikZ:** Used for geometric diagrams (e.g., the Circle of Fifths).
*   **tcolorbox:** Provides stylized containers for definitions, examples, and technical notes.

## Language and Localization

*   **Language:** The project is written entirely in **Italian**. All technical terms must follow Italian musical nomenclature (e.g., "Sesta Napoletana", "Settima di Dominante").
*   **Musical Nomenclature:** Use Italian note names (Do, Re, Mi, Fa, Sol, La, Si).

## Building and Running

### Prerequisites

1.  **TeX Live:** A full TeX distribution (e.g., TeX Live 2023 or newer).
2.  **LuaLaTeX:** The document MUST be compiled with `lualatex` as required by the `lyluatex` package.
3.  **LilyPond:** Version 2.24.0 or compatible must be installed and accessible in the system's PATH.
4.  **Fonts:** `fontspec` is used. The environment must support the musical glyphs provided by the packages.

### Compilation Command

To compile the project, run the following command from the root directory:

```bash
lualatex --shell-escape manuale.tex
```

*Note: The `--shell-escape` flag is required by `lyluatex` to invoke LilyPond during the compilation process.*

## Development Conventions

### Musical Symbols and Formatting

*   **Sharps and Flats in Text:** For musical alterations within the LaTeX text, **always use the commands `\sharp` and `\flat`** (often within math mode: `$\sharp$` and `$\flat$`).
    *   *Do not* use literal Unicode characters (♯, ♭) or simple characters (#, b) in the main body text.
    *   Example: `Do$\sharp$`, `Si$\flat$`.
*   **LilyPond Notation:** Inside LilyPond blocks, use the standard LilyPond language (Italian): `dodies` for Do♯, `sib` for Si♭.

### LilyPond Integration: `partilate`

For 4-part harmony (SATB) writing, always use the custom `partilate` function defined in `definizioni.ly`. It ensures a consistent "PianoStaff" layout with analysis and figured bass.

**Syntax:**
```lilypond
\partilate
    { \key do \major \time 4/4 } % 1. Global (key, time)
    { do'2 mi' }                 % 2. Soprano
    { sol1 }                     % 3. Alto
    { mi1 }                      % 4. Tenor
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

## Codebase Memory (codebase-memory-mcp)

This project is indexed with `codebase-memory-mcp` as a knowledge graph (project name: **`manualearmonia`**). ALWAYS prefer the MCP graph tools over grep/glob for structural queries about the codebase.

### Priority Order

1. `search_graph` — find LilyPond functions, LaTeX commands/environments, and files by pattern (BM25 full-text search).
2. `trace_path` — trace who calls a function or what it calls.
3. `get_code_snippet` — read the source of a specific function/class symbol.
4. `query_graph` — run Cypher queries for complex multi-hop patterns.
5. `get_architecture` — high-level project summary and module detection.

### When to fall back to grep/glob

- Searching for string literals, error messages, or config values.
- Searching non-code files (e.g. `.tex`, `.ly`, `.txt` content).
- When MCP tools return insufficient results.

### Examples

- Find a LilyPond function: `search_graph(query="partilate", project="manualearmonia")`
- Read its source: `get_code_snippet(qualified_name="definizioni.ly.partilate", project="manualearmonia")`
- High-level structure: `get_architecture(project="manualearmonia", aspects=['all'])`
- See all indexed projects: `list_projects`
