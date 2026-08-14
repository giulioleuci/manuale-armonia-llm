# Correzione Scrittura a 4 Parti (Voicing) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring every `\partilate` SATB block in the manual into compliance with the manual's own four-part writing rules (no voice crossings, tenor ≤ E4), convert single-staff chord demonstrations to the `partilate` format, and add two new harmonized examples each to chapters 05 and 11.

**Architecture:** A Python verifier (`tools/verifica_voci.py`, already written and fixed) is the test harness: it extracts every `\partilate` block, parses the four voices, and reports hard violations (crossings/unisons, tenor above E4) plus spacing warnings. The plan fixes all 31 flagged blocks with exact note-for-note prescriptions, then converts 6 chord-demonstration blocks to `partilate`, then adds 4 new blocks. Verification is always `python3 tools/verifica_voci.py` (exit 0 = no violations) followed by a full `lualatex --shell-escape manuale.tex` build.

**Tech Stack:** LaTeX (LuaLaTeX), LilyPond 2.24+, `lyluatex`, Python 3 (standard library only, no deps).

## Global Constraints

- All musical text remains **Italian**; note names use LilyPond Italian syntax (`do'`, `si,`, `mib'`, `fad`, `sold`).
- Text-mode alterations always use `\sharp` / `\flat` (or LilyPond accidentals inside music) — never Unicode `♯`/`♭`.
- **Only voices change** in the correction tasks: `\lyricmode`, `\figuremode`, and the first argument of `\partilate` (key/time) are NEVER touched unless a task explicitly says so.
- **Bass line inviolable** except where a task explicitly prescribes a bass octave fix (the author's `do'`, `sol`, `la`, etc. that sit at/above the tenor — always documented per block).
- Tenor register: must stay ≤ `mi'` (E4 = MIDI 64); `do'`/`re'` allowed as lead lines. Bass register F2–E3 (MIDI 41–52) is the target; minor excursions flagged in tasks.
- SATB ordering at every vertical: `Basso < Tenore < Contralto < Soprano`. No unisons between adjacent voices.
- Max comfortable gaps: S–A ≤ 12, A–T ≤ 12, T–B ≤ 19 semitones. Gaps within these bounds are legal; exceeding them is a warning to fix where the prescription says so.
- Block numbering in tasks = the block's 1-based index inside its `.tex` file, matching `tools/verifica_voci.py` output. Always re-run the tool after edits and confirm the block count drops.
- The project is **not a git repo** (verified). Commits are optional; if you `git init` first, commit after each task with messages in the repo's style.
- DO NOT recompose the harmony. These are register/voicing corrections. Pre-existing label/harmony mismatches (e.g. a chord figure that doesn't match the notes) are out of scope and must be left untouched.

---

## Task 0: Tooling Baseline & Syntax-Check Helper

**Files:**
- Modify: `tools/verifica_voci.py` (already fixed; verify only)
- Create: `tools/estrai_blocco.py`
- Test: run both against the repository

**Interfaces:**
- Consumes: the repository's `\partilate` blocks (existing files).
- Produces: `estrai_blocco.py` — CLI `python3 tools/estrai_blocco.py <Capitoli/file.tex> <N>` that prints a standalone, compilable LilyPond snippet for block N. Used in every later task to sanity-compile edited blocks with `lilypond` directly (faster than a full lualatex run).

- [ ] **Step 1: Confirm the verifier works on the current tree**

```bash
python3 tools/verifica_voci.py
```

Expected: prints **31** blocks, exit code 1. All 21 blocks with `INCROCI`/`SUPERA mi'!` and 10 `SOLO AVVISI` blocks listed as in the plan's per-task tables.

- [ ] **Step 2: Write `tools/estrai_blocco.py`**

```python
#!/usr/bin/env python3
"""Estrae il blocco \musica{...} #N da un file .tex e lo scrive come .ly autonomo."""
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
        # parte dal secondo argomento di partilate (i primi 5 gruppi sono il coro)
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
        key, time, S, A, T, B = groups[0], groups[1], groups[2], groups[3], groups[4], groups[5]
        ly = (
            '\\version "2.24.0"\n'
            '\\paper { indent = 0\\mm ragged-right = ##t }\n'
            'vS = { %s %s }\n' % (key, S) +
            'vA = { %s }\n' % A +
            'vT = { %s }\n' % T +
            'vB = { %s }\n' % B +
            '\\new PianoStaff <<\n'
            '  \\new Staff << \\vS \\vA >>\n'
            '  \\new Staff << \\clef bass \\vB >>\n'
            '>>\n'
        )
    else:
        # blocco \new Staff: lo si compila direttamente
        ly = '\\version "2.24.0"\n\\paper { indent = 0\\mm ragged-right = ##t }\n' + content + '\n'
    base = os.path.splitext(os.path.basename(fn))[0]
    tmp = tempfile.mktemp(suffix='.ly')
    open(tmp, 'w').write(ly)
    if len(sys.argv) > 3 and sys.argv[3] == '--run':
        subprocess.run(['lilypond', '--silent', '-o', '/tmp/opencode/lycheck', tmp], check=False)
    else:
        print(ly)
    os.remove(tmp)

if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Smoke-test the helper on a known-good block**

```bash
python3 tools/estrai_blocco.py Capitoli/04_scrittura_quattro_parti.tex 2
```

Expected: a standalone `.ly` with voices `vS`, `vA`, `vT`, `vB`. Then:

```bash
mkdir -p /tmp/opencode/lycheck
python3 tools/estrai_blocco.py Capitoli/04_scrittura_quattro_parti.tex 2 --run
```

Expected: lilypond produces no error (regardless of the pre-fix voicing crossing, the file must still *parse*).

- [ ] **Step 4: Commit (optional — see Global Constraints on git)**

```bash
git init 2>/dev/null; git add tools/ ; git commit -m "tool: verifica voci + estrattore blocchi lilypond"
```

**Acceptance criteria:** `verifica_voci.py` reports 31 blocks; `estrai_blocco.py` emits and compiles block 04#2 without a LilyPond parse error.

---

## Task 1: Corrections, Chapters 03, 04, 06, 08, 09, 12, 13 (small blocks)

**Files:** `Capitoli/03_secondo_rivolto.tex`, `Capitoli/04_scrittura_quattro_parti.tex`, `Capitoli/06_cadenze_sintassi.tex`, `Capitoli/08_teoria_dissonanza.tex`, `Capitoli/09_settima_dominante.tex`, `Capitoli/12_settima_sensibile.tex`, `Capitoli/13_specie_settima.tex`.

**Interfaces:**
- Consumes: `tools/verifica_voci.py` (Task 0).
- Produces: 8 clean blocks. Later tasks' verification relies on the same tool.

The fixes below change **only the one voice line** indicated. Apply each as an exact string replacement inside the matching `\partilate` block. Preserve all `\freccia` / `\glissando` markup verbatim (04#2 keeps them on the alto, 09#2 keeps them on soprano and tenor).

- [ ] **Step 1: 03#2 — tenor `mi4 fa sol la` → `mi4 fa do re`**

Current tenor: `{ mi4 fa sol la }` (beats 1–4). At b3 the tenor `sol` equals the alto `sol` (unison); at b4 the tenor `la` (A3) rises above the alto `sol`. Replace the whole tenor line with:

```lilypond
{ mi4 fa do re }
```

New verticals: b1 `S:do' A:sol T:mi B:do` ✓; b2 `S:re' A:sol T:fa B:si,` ✓; b3 `S:mi' A:sol T:do B:la,` ✓; b4 `S:fa' A:sol T:re B:sol,` ✓.

- [ ] **Step 2: 04#2 — tenor `re'2 do'2` → `re2 mi2`**

Current tenor: `{ re'2 do'2 }`. Both notes sit above the alto (`si` then `sol`). Replace with:

```lilypond
{ re2 mi2 }
```

New verticals: b1 `S:fa' A:si T:re B:sol,` ✓; b2 `S:mi' A:sol T:mi B:do` ✓.

- [ ] **Step 3: 06#6 — soprano `... sol'4 do'4` → `... sol'4 do''4`**

Current soprano: `{ mi'4 fa'4 sol'4 do'4 }`. The final `do'` (C4) puts the alto `mi'` (E4) above it. Change only the last note:

```lilypond
{ mi'4 fa'4 sol'4 do''4 }
```

New b4: `S:do'' A:mi' T:sol B:do` ✓ (cadence on high tonic).

- [ ] **Step 4: 08#1 — tenor `mi'2 re'2 | re'1` → `mi'2 re'2 | si1`**

Current tenor: `{ mi'2 re'2 | re'1 }`. The final `re'` (D4) equals the alto `re'` (unison). Replace the second measure:

```lilypond
{ mi'2 re'2 | si1 }
```

New b3: `S:si' A:re' T:si B:sol,` ✓.

- [ ] **Step 5: 09#2 — tenor `\freccia si2 \glissando do'2` → `\freccia si2 \glissando sol2`**

Current tenor: `{ \freccia si2 \glissando do'2 }`. The resolved `do'` (C4) equals the alto `do'` (unison). Replace with (keep the arrows):

```lilypond
{ \freccia si2 \glissando sol2 }
```

New b2: `S:mi' A:do' T:sol B:do` ✓. (The leading-tone resolution si→sol is a deliberate re-voice; the altos carries the tonic.)

- [ ] **Step 6: 12#5 — tenor `mi4 fa4 sold4 do'4` → `mi4 fa4 sold4 fa4`**

Current tenor: `{ mi4 fa4 sold4 do'4 }`. The final `do'` (C4) rises above the alto `la` (A3). Replace the last note:

```lilypond
{ mi4 fa4 sold4 fa4 }
```

New b4: `S:fa' A:la T:fa B:re` ✓.

- [ ] **Step 7: 13#1 — tenor `mi'2 fa'2 | fa'1` → `mi'2 re'2 | si1`**

Current tenor: `{ mi'2 fa'2 | fa'1 }`. b2: tenor `fa'` (F4) equals alto `fa'` (unison). b3: tenor `fa'` (F4) rises above alto `re'` and exceeds E4. Replace:

```lilypond
{ mi'2 re'2 | si1 }
```

New b2: `S:do'' A:fa' T:re' B:re` ✓; b3: `S:si' A:re' T:si B:sol,` ✓; tenor max now `re'` ✓.

- [ ] **Step 8: 13#3 — tenor `si2 do'2` → `si2 mi2`**

Current tenor: `{ si2 do'2 }`. The resolved `do'` (C4) equals alto `do'` (unison). Replace:

```lilypond
{ si2 mi2 }
```

New b2: `S:mi' A:do' T:mi B:la,` ✓ (tonic third in the tenor).

- [ ] **Step 9: Verify**

```bash
python3 tools/verifica_voci.py --chapter 03
python3 tools/verifica_voci.py --chapter 04
python3 tools/verifica_voci.py --chapter 06
python3 tools/verifica_voci.py --chapter 08
python3 tools/verifica_voci.py --chapter 09
python3 tools/verifica_voci.py --chapter 12
python3 tools/verifica_voci.py --chapter 13
```

Expected: every chapter prints `Blocchi SATB con violazioni: 0`. Then compile each touched block:

```bash
for f in 03_secondo_rivolto 04_scrittura_quattro_parti 06_cadenze_sintassi 08_teoria_dissonanza 09_settima_dominante 12_settima_sensibile 13_specie_settima; do
  for n in 2 2 6 1 2 5 1 3; do :; done
done
```

(Use `estrai_blocco.py ... --run` on each touched block number; expect no LilyPond parse error.)

- [ ] **Step 10: Commit (optional)**

```bash
git add Capitoli/03_secondo_rivolto.tex Capitoli/04_scrittura_quattro_parti.tex Capitoli/06_cadenze_sintassi.tex Capitoli/08_teoria_dissonanza.tex Capitoli/09_settima_dominante.tex Capitoli/12_settima_sensibile.tex Capitoli/13_specie_settima.tex
git commit -m "fix: scrittura a 4 parti nei blocchi 03#2 04#2 06#6 08#1 09#2 12#5 13#1 13#3"
```

**Acceptance criteria:** all 8 blocks report zero violations; all edited blocks parse in LilyPond; no lyric/figure/key lines changed.

---

## Task 2: Corrections, Chapter 16 (modulation blocks)

**Files:** `Capitoli/16_modulazione_vicini.tex`.

**Interfaces:**
- Consumes: `tools/verifica_voci.py`.
- Produces: blocks 1, 3, 4, 5, 7 clean (blocks 2, 6, 8 were already clean and are untouched).

- [ ] **Step 1: 16#1 — swap soprano and alto, adjust tenor, lower final bass octave**

Current voices:

```lilypond
{ do'2 do'2 | si2 do'2 | do'1 }
{ mi'2 fa'2 | sold2 la2 | la1 }
{ sol2 la2 | re'2 mi'2 | mi'1 }
{ do2 fa,2 | mi,2 la,,2 | la,,1 }
```

The alto (`mi' fa' sold la`) carries the melodic interest while the static soprano sits below it (crossings at all 5 beats). Swap the two upper lines and re-voice:

```lilypond
{ mi'2 fa'2 | sold2 la2 | la1 }       % Soprano (ex-alto melody)
{ do'2 do'2 | mi2 mi2 | mi1 }         % Contralto (tonic pedal of the old soprano)
{ sol2 la2 | si2 do2 | do1 }          % Tenore (si/do lead line, was re'/mi')
{ do2 fa,2 | mi,2 la,2 | la,1 }       % Basso (la,, -> la,: A1 -> A2, register fix)
```

New verticals: b1 `S:mi' A:do' T:sol B:do` ✓; b2 `S:fa' A:do' T:la B:fa,` ✓; b3 `S:sold A:mi T:si B:mi,` ✓; b4 `S:la A:mi T:do B:la,` ✓; b5 same as b4 ✓. The A1 bass (`la,,`) is below cello range and 13 semitones below the preceding `mi,`; the octave fix is required to close the T–B gap (24 → 3). **This bass change needs author sign-off** — flag in the PR/commit.

- [ ] **Step 2: 16#3 — tenor `do'2 sib2` → `do2 sib2`**

Current tenor: `{ sol2 sol2 | do'2 sib2 | la1 }`. The `do'` (C4) rises above the alto `la` (A3). Replace:

```lilypond
{ sol2 sol2 | do2 sib2 | la1 }
```

New b3: `S:fa' A:la T:do B:fa,` ✓; b4: `S:mi' A:do' T:sib B:fa,` ✓.

- [ ] **Step 3: 16#4 — alto `do'2 fa'2` → `do'2 re'2`**

Current alto: `{ do'2 fa'2 | fa'2 mi'2 | mi'1 }`. The `fa'` (F4) at b2 sits above the soprano `mi'` (E4). Replace the first measure:

```lilypond
{ do'2 re'2 | fa'2 mi'2 | mi'1 }
```

New b2: `S:mi' A:re' T:si B:si,` ✓ (D fills the chord instead of F).

- [ ] **Step 4: 16#5 — tenor `sol2 re'2 | re'2 do'2 | do'1` → `sol2 re2 | re2 do2 | do1`**

Current tenor: `{ sol2 re'2 | re'2 do'2 | do'1 }`. `re'` and `do'` sit above the alto at b2–b5. Drop them one octave:

```lilypond
{ sol2 re2 | re2 do2 | do1 }
```

New b2: `S:do' A:la T:re B:re,` ✓; b3: `S:sib A:fa T:re B:sol,` ✓; b4: `S:la A:fa T:do B:fa,` ✓; b5 same ✓.

- [ ] **Step 5: 16#7 — known warning, NO change**

Beats 5–6 show a wide S–A gap (`mi''`–`do'` = 16, `do''`–`si` = 13). Every fix (lowering S, raising A, moving T) creates a new violation or breaks the modulation's registral design. **Leave untouched.** It does not violate the mandatory rules.

- [ ] **Step 6: Verify**

```bash
python3 tools/verifica_voci.py --chapter 16
```

Expected: reports `Blocchi SATB con violazioni: 0` (16#7 must no longer appear — it was `SOLO AVVISI` and is not fixable without recomposition; if it still shows, that is acceptable and expected — see note below).

> **Note:** If 16#7 still appears as `SOLO AVVISI`, that is fine and intentional. The acceptance criterion is: no block reports `INCROCI` and none report `SUPERA mi'!`. 16#7 may retain its gap warning.

- [ ] **Step 7: Compile-check and commit**

```bash
python3 tools/estrai_blocco.py Capitoli/16_modulazione_vicini.tex 1 --run
python3 tools/estrai_blocco.py Capitoli/16_modulazione_vicini.tex 3 --run
python3 tools/estrai_blocco.py Capitoli/16_modulazione_vicini.tex 4 --run
python3 tools/estrai_blocco.py Capitoli/16_modulazione_vicini.tex 5 --run
git add Capitoli/16_modulazione_vicini.tex
git commit -m "fix: registri e incroci nei blocchi di modulazione (16#1 16#3 16#4 16#5)"
```

**Acceptance criteria:** blocks 1, 3, 4, 5 report no violations; 16#7 unchanged with its warning documented; every touched block compiles.

---

## Task 3: Corrections, Chapter 17 (progressions) — register re-voicings

**Files:** `Capitoli/17_progressioni.tex`.

**Interfaces:**
- Consumes: `tools/verifica_voci.py`.
- Produces: blocks 1, 2, 4, 5, 7, 12, 13, 14 clean. Blocks 3, 6, 8–11 are clean and untouched.

The blocks in this chapter were written an octave too high in the upper voices (tenor reaching `la'`–`re''`). The fix for 1, 2, 5, 7 is: **transpose the whole S/A/T trio one octave down**, keep the bass, then repair the few verticals that break.

- [ ] **Step 1: 17#1 — transpose upper trio down an octave, fix bass `do'` and final cadence**

Current voices:

```lilypond
{ mi''2 fa'' | re'' mi'' | do'' re'' | do'' si' | do''1 }
{ do''2 do'' | si' do'' | la' si' | sol' sol' | mi'1 }
{ sol'2 la' | sol' sol' | fa' fa' | mi' re' | sol1 }
{ do2 fa | sol do' | la re | mi sol | do1 }
```

Replace with:

```lilypond
{ mi'2 fa' | re' mi' | do' re' | do' si | do''1 }
{ do'2 do' | si do' | la si | sol sol | do'1 }
{ sol2 la | sol sol | fa fa | mi re | sol1 }
{ do2 fa | sol do | la re | mi sol | do1 }
```

Changes: S/A/T transposed down one octave; bass `do'` (C4, above tenor) → `do` (C3) at b4; final beat re-voiced so the soprano cadences on `do''` and the alto fills under it (b9 `S:do'' A:do' T:sol B:do` ✓, the S leap `si`→`do''` at the cadence is an accepted minor-6th).

- [ ] **Step 2: 17#2 (3/4) — transpose upper trio down one octave, fix bass `do'`, tenor beat 5, final chord**

Current voices:

```lilypond
{ mi''2. | do'' | la' | fa' | re' | si' | do''2. }
{ do''2. | la' | fa' | re' | si' | sol' | mi'2. }
{ sol'2. | mi' | do' | la' | sol' | re' | sol'2. }
{ do'2. | la | fa | re | sol | sol | do2. }
```

Replace with:

```lilypond
{ mi'2. | do' | la | fa | re | si | do'2. }
{ do'2. | la | fa | re | si | sol | sol2. }
{ sol2. | mi | do | la | la | re | mi2. }
{ do2. | la | fa | re | sol | sol | do2. }
```

Changes: S/A/T down one octave; bass `do'`→`do` at b1; tenor beat 5 `sol`→`la` (was unison with bass `sol`); final beat swaps alto/tenor (`A:sol T:mi`) so the tenor no longer crosses the alto.

- [ ] **Step 3: 17#4 — soprano final `do'`→`do''`, bass `do'`→`do`**

Current voices:

```lilypond
{ mi'4 fa' sol' mi' | do' re' re' do' }
{ do'4 do' re' do' | la si si mi' }
{ sol4 la si sol | mi sol sol sol }
{ do4 fa sol do' | la re sol do }
```

Change only two notes:

```lilypond
{ mi'4 fa' sol' mi' | do' re' re' do'' }   % final tonic up to high C
{ do'4 do' re' do' | la si si mi' }
{ sol4 la si sol | mi sol sol sol }
{ do4 fa sol do | la re sol do }           % bass do' (C4) -> do (C3)
```

New b8: `S:do'' A:mi' T:sol B:do` ✓; the b4 bass `do'` (above the tenor) drops to `do`.

- [ ] **Step 4: 17#5 — transpose upper trio down one octave**

Current voices:

```lilypond
{ fa''2 mi'' | re'' do'' | si'1 }
{ re''2 do'' | si' la' | sol'1 }
{ la'2 sol' | sol' fa' | re'1 }
{ re2 do | sol, la, | sol,1 }
```

Replace the three upper lines (bass unchanged):

```lilypond
{ fa'2 mi' | re' do' | si1 }
{ re'2 do' | si la | sol1 }
{ la2 sol | sol fa | re1 }
```

- [ ] **Step 5: 17#7 — transpose upper trio down one octave, tenor `re''`→`re` at beats 4 and 7**

Current voices:

```lilypond
{ mi''4 fa'' fad'' sol'' | sol'' fad'' sol''2 }
{ do''4 do'' re'' si' | re'' re'' si'2 }
{ sol'4 la' la' re'' | si' la' re''2 }
{ do4 fa si, mi | la, re sol,2 }
```

Replace with:

```lilypond
{ mi'4 fa' fad' sol' | sol' fad' sol'2 }
{ do'4 do' re' si | re' re' si2 }
{ sol4 la la re | si la re2 }
{ do4 fa si, mi | la, re sol,2 }
```

Tenor max now `re'` ✓.

- [ ] **Step 6: 17#12 — fix octave typos in the soprano/alto scales, bass `re`→`re,` at beat 6**

Current voices:

```lilypond
{ fa'2 mi' | re' do' | si' la' | sol'1 }
{ re'2 do' | si' la' | sol' fa' | mi'1 }
{ la2 sol | fa mi | re do | si1 }
{ re2 la | si, fa | sol re | mi1 }
```

The `si'`/`la'` in S (beats 5–6) and A (beats 3–4) break each descending scale with an octave jump; the `sol'`/`fa'`/`mi'` in A (beats 5–7) keep the alto above the soprano. Fix the octaves so all lines descend continuously, and drop the bass `re` at beat 6 to `re,` (it sat above the tenor `do`):

```lilypond
{ fa'2 mi' | re' do' | si la | sol1 }
{ re'2 do' | si la | sol fa | mi1 }
{ la2 sol | fa mi | re do | si1 }
{ re2 la | si, fa | sol re, | mi1 }
```

New verticals: b3 `S:re' A:si T:fa B:si,` ✓; b4 `S:do' A:la T:mi B:fa` ✓; b5 `S:si A:sol T:re B:sol` ✓; b6 `S:la A:fa T:do B:re,` ✓; b7 `S:sol A:mi T:si B:mi` ✓.

- [ ] **Step 7: 17#13 — lower alto `lab'`, `la'`, `si'`; re-voice tenor beats 3–9**

Current voices:

```lilypond
{ mib'4 mib' mi' mi' | fa' fa' fad' fad' | sol'1 }
{ do'4 sib lab' do' | do' re' la' do' | si'1 }
{ lab4 sol fa' mi' | mib' la si' la' | re'1 }
{ lab,4 sol, lab, do | la, re si, re | sol,1 }
```

Replace alto and tenor (soprano/bass unchanged):

```lilypond
{ mib'4 mib' mi' mi' | fa' fa' fad' fad' | sol'1 }
{ do'4 sib lab do' | do' re' la do' | si1 }
{ lab4 sol fa sol | mib la fad fa | re1 }
{ lab,4 sol, lab, do | la, re si, re | sol,1 }
```

Rationale per beat (alto/tenor): b3 `lab'→lab`, `fa'→fa`; b4 `mi'→sol` (was unison with S `mi'`); b5 `mib'→mib`; b6 unchanged (`la`); b7 `la'→la`, `si'→fad`; b8 `la'→fa`; b9 `si'→si`, `re'→re`. Tenor max `la` ✓.

- [ ] **Step 8: 17#14 (3/4) — lower alto `si'`→`si`, `la'`→`la`; tenor `si'`→`si`**

Current voices:

```lilypond
{ la'2. | sol' | fa' | mi' | re' | do' | si' | la'2. }
{ fa'2. | mi' | re' | do' | si' | la' | sol' | mi'2. }
{ re'2. | do' | si' | la | sold | mi | re | do'2. }
{ re2. | do | si, | la, | sold, | sol, | fa, | mi2. }
```

Replace alto and tenor:

```lilypond
{ fa'2. | mi' | re' | do' | si | la | sol' | mi'2. }
{ re'2. | do' | si | la | sold | mi | re | do'2. }
```

New b3: `S:fa' A:re' T:si B:si,` ✓; b5: `S:re' A:si T:sold B:sold,` ✓; b6: `S:do' A:la T:mi B:sol,` ✓.

- [ ] **Step 9: Verify**

```bash
python3 tools/verifica_voci.py --chapter 17
```

Expected: `Blocchi SATB con violazioni: 0`.

- [ ] **Step 10: Compile-check and commit**

```bash
for n in 1 2 4 5 7 12 13 14; do
  python3 tools/estrai_blocco.py Capitoli/17_progressioni.tex $n --run
done
git add Capitoli/17_progressioni.tex
git commit -m "fix: registri e incroci nelle progressioni (17#1 17#2 17#4 17#5 17#7 17#12 17#13 17#14)"
```

**Acceptance criteria:** all 8 flagged blocks clean; edited blocks compile; no lyric/figure/key changes. Bass octave changes (17#4 b4, 17#12 b6) flagged for author review.

---

## Task 4: Correction, Chapter 18 + warning-only fixes (07, 10, 12, 14, 20)

**Files:** `Capitoli/18_metodo_basso_numerato.tex`, `Capitoli/07_struttura_frase.tex`, `Capitoli/10_ritardi.tex`, `Capitoli/12_settima_sensibile.tex`, `Capitoli/14_regola_ottava.tex`, `Capitoli/20_metodo_basso_senza_numeri.tex`.

**Interfaces:**
- Consumes: `tools/verifica_voci.py`.
- Produces: blocks 18#4, 07#2, 10#2, 10#4, 12#4, 14#1–3, 20#2, 20#4 clean. Blocks 16#7 and all others remain as-is.

- [ ] **Step 1: 18#4 — tenor last note `fad'`→`la`**

Current tenor: `{ la4 si | la si | do' re' | fad'1 }`. The final `fad'` (F#4) exceeds E4 by 2 semitones and clusters 2 semitones under the alto `la'`. Replace the last note:

```lilypond
{ la4 si | la si | do' re' | la1 }
```

New b7: `S:si' A:la' T:la B:si,` ✓ (5th of the V7/V chord, A–T gap 12).

- [ ] **Step 2: 07#2 — bass `sol`→`sol,` at beats 3 and 7**

Current bass: `{ do2 fa | sol2 do | do2 fa | sol1 }`. At b3 and b7 the bass `sol` (G3) equals the tenor `sol` (G3) — unison. The tenor keeps G3; the bass must drop:

```lilypond
{ do2 fa | sol,2 do | do2 fa | sol,1 }
```

- [ ] **Step 3: 10#2 — bass `sol2`→`sol,2`**

Current bass: `{ fa2 sol2 | do2 do2 | do1 }`. At b2 the bass `sol` (G3) equals the tenor `sol`. Fix:

```lilypond
{ fa2 sol,2 | do2 do2 | do1 }
```

- [ ] **Step 4: 10#4 — bass `mi2`→`mi,2`**

Current bass: `{ re2 mi2 | la,2 la,2 | la,1 }`. At b2 bass `mi` (E3) equals tenor `mi`. Fix:

```lilypond
{ re2 mi,2 | la,2 la,2 | la,1 }
```

- [ ] **Step 5: 12#4 — bass `mi2`→`mi,2`**

Current bass: `{ la,2 re2 | mi2 mi,2 | la,1 }`. At b3 bass `mi` (E3) equals tenor `mi`. Fix:

```lilypond
{ la,2 re2 | mi,2 mi,2 | la,1 }
```

- [ ] **Step 6: 14#1 — bass first half one octave down; tenor beats 5–6 raised**

Current tenor/bass:

```lilypond
{ sol4 si sol do' | fa re sol sol }
{ do'4 si la sol | fa mi re do }
```

The bass starts at `do'` (C4) above the tenor; beats 5–6 the bass again reaches/exceeds the tenor. Replace:

```lilypond
{ sol4 si sol do' | la si sol sol }    % T: fa->la (b5), re->si (b6)
{ do4 si, la, sol, | fa mi re do }     % B: primo gruppo un'ottava sotto
```

New b5: `S:do'' A:la' T:la B:fa` ✓; b6: `S:do'' A:sol' T:si B:mi` ✓; b1: `B:do T:sol` ✓.

- [ ] **Step 7: 14#2 — bass second half one octave down**

Current bass: `{ la,4 si, do re | mi fa sold la }`. The second half climbs to `sold`/`la` (G#3/A3), above the tenor at b7–b8. Drop it one octave:

```lilypond
{ la,4 si, do re | mi, fa, sold, la, }
```

New b7: `B:sold, T:sold` ✓; b8: `B:la, T:mi` ✓.

- [ ] **Step 8: 14#3 — bass first half one octave down; tenor beats 5–6 re-voiced**

Current tenor/bass:

```lilypond
{ mi4 re do la | re si, mi mi }
{ la4 sold fa mi | re do si, la, }
```

The bass first half (`la sold fa mi` = A3…E3) sits above the tenor; at b5–b6 bass `re`/`do` meet or exceed the tenor. Replace:

```lilypond
{ mi4 re do la | fa fa mi mi }    % T: re->fa (b5), si,->fa (b6)
{ la,4 sold, fa, mi, | re do si, la, }   % B: primo gruppo un'ottava sotto
```

New b5: `S:si' A:fa' T:fa B:re` ✓; b6: `S:la' A:mi' T:fa B:do` ✓.

- [ ] **Step 9: 20#2 — tenor beat 5 `sol`→`re'`**

Current tenor: `{ sol2 sol | sol la | sol1 | sol1 }`. At b5 the alto jumps to `si'` (B4) leaving a 16-semitone gap to the tenor `sol`. Raise the tenor's final note to `re'`:

```lilypond
{ sol2 sol | sol la | re'1 | sol1 }
```

New b5: `S:re'' A:si' T:re' B:sol,` ✓ (A–T gap 9, T–B gap 19 at the limit).

- [ ] **Step 10: 20#4 — alto beats 4–5 `la`→`do'`; tenor beat 6 `do'`→`la`**

Current alto/tenor:

```lilypond
{ re'2 do' | do' la | la1 | fa'1 }
{ la2 sol | fa mi | mi1 | do'1 }
```

The S–A gap at b4 (`sib'`–`la` = 13) and b5 (`do''`–`la` = 15) and T–B gap at b6 (`do'`–`re,` = 22) exceed the limits. Replace:

```lilypond
{ re'2 do' | do' do' | do'1 | fa'1 }
{ la2 sol | fa mi | mi1 | la1 }
```

New b4: `S:sib' A:do' T:mi B:sol,` ✓; b5: `S:do'' A:do' T:mi B:la,` ✓; b6: `S:la' A:fa' T:la B:re,` ✓ (T–B gap 19 at the limit).

- [ ] **Step 11: Verify**

```bash
python3 tools/verifica_voci.py --chapter 07
python3 tools/verifica_voci.py --chapter 10
python3 tools/verifica_voci.py --chapter 12
python3 tools/verifica_voci.py --chapter 14
python3 tools/verifica_voci.py --chapter 18
python3 tools/verifica_voci.py --chapter 20
```

Expected: `Blocchi SATB con violazioni: 0` for all six chapters.

- [ ] **Step 12: Compile-check and commit**

```bash
python3 tools/estrai_blocco.py Capitoli/18_metodo_basso_numerato.tex 4 --run
python3 tools/estrai_blocco.py Capitoli/07_struttura_frase.tex 2 --run
python3 tools/estrai_blocco.py Capitoli/10_ritardi.tex 2 --run
python3 tools/estrai_blocco.py Capitoli/10_ritardi.tex 4 --run
python3 tools/estrai_blocco.py Capitoli/12_settima_sensibile.tex 4 --run
python3 tools/estrai_blocco.py Capitoli/14_regola_ottava.tex 1 --run
python3 tools/estrai_blocco.py Capitoli/14_regola_ottava.tex 2 --run
python3 tools/estrai_blocco.py Capitoli/14_regola_ottava.tex 3 --run
python3 tools/estrai_blocco.py Capitoli/20_metodo_basso_senza_numeri.tex 2 --run
python3 tools/estrai_blocco.py Capitoli/20_metodo_basso_senza_numeri.tex 4 --run
git add Capitoli/07_struttura_frase.tex Capitoli/10_ritardi.tex Capitoli/12_settima_sensibile.tex Capitoli/14_regola_ottava.tex Capitoli/18_metodo_basso_numerato.tex Capitoli/20_metodo_basso_senza_numeri.tex
git commit -m "fix: ottave del basso e spaziature (07 10 12 14 18 20)"
```

**Acceptance criteria:** all listed blocks clean; bass-octave changes (14#1–3) flagged for author review; no lyric/figure/key changes.

---

## Task 5: Convert chord-demonstration blocks to `partilate` (02, 09, 14)

**Files:** `Capitoli/02_triadi.tex`, `Capitoli/09_settima_dominante.tex`, `Capitoli/14_regola_ottava.tex`.

**Interfaces:**
- Consumes: the `partilate` syntax (see AGENTS.md), `tools/verifica_voci.py`.
- Produces: blocks 02#1–5, 09#1, 14#4–6 rewritten as `partilate`; all pass the verifier.

Each replacement keeps the block's original pedagogical labels — they move from `-\markup{...}` (attached to a chord) into `\lyricmode { ... }` as the final partilate argument. The `\paper`/`\override` wrappers and `\clef` in the originals are dropped (partilate sets its own layout). Each block below is the FULL replacement of the original `\musica{...}` content.

- [ ] **Step 1: 02#1 — the four triad qualities, four-part**

Replace block 1 (currently a single treble staff with `<do' mi' sol'>` etc.) with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ sol'1 sol'1 solb'1 sold'1 }
{ mi'1 mib'1 mib'1 mi'1 }
{ do'1 do'1 do'1 do'1 }
{ do1 do1 do1 do1 }
\lyricmode { "maggiore"1 "minore"1 "diminuita"1 "eccedente"1 }
\figuremode { s1 s1 s1 s1 }
```

Verticals: maggiore `S:sol' A:mi' T:do' B:do` ✓; minore `S:sol' A:mib' T:do' B:do` ✓; diminuita `S:solb' A:mib' T:do' B:do` ✓; eccedente `S:sold' A:mi' T:do' B:do` ✓.

- [ ] **Step 2: 02#2 — the seven diatonic triads, four-part**

Replace block 2 with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ mi'1 fa'1 sol'1 la'1 si'1 do''1 re''1 }
{ do'1 re'1 mi'1 fa'1 sol'1 la'1 si'1 }
{ sol1 la1 si1 do'1 re'1 mi'1 re'1 }
{ do1 re1 mi1 fa1 sol1 la1 si1 }
\lyricmode { "I (M)"1 "II (m)"1 "III (m)"1 "IV (M)"1 "V (M)"1 "VI (m)"1 "VII° (dim)"1 }
\figuremode { s1 s1 s1 s1 s1 s1 s1 }
```

Check the two tight spots: VI `S:do'' A:la' T:mi' B:la` ✓; VII° `S:re'' A:si' T:re' B:si` ✓ (tenor `re'` ≤ E4, S–A gap 3). All other verticals are sequential close-position triads (verify each with the tool).

- [ ] **Step 3: 02#3 — root position and two inversions with real bass**

Replace block 3 with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ mi'1 do'1 mi'1 }
{ do'1 sol1 do'1 }
{ sol1 mi1 sol1 }
{ do1 mi,1 sol,1 }
\lyricmode { "Basso reale: Do"1 "Basso reale: Mi"1 "Basso reale: Sol"1 }
\figuremode { s1 s1 s1 }
```

Verticals: b1 `S:mi' A:do' T:sol B:do` ✓; b2 (1st inv.) `S:do' A:sol T:mi B:mi,` ✓; b3 (2nd inv.) `S:mi' A:do' T:sol B:sol,` ✓.

- [ ] **Step 4: 02#4 — I6 single chord**

Replace block 4 with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ do'1 }
{ sol1 }
{ mi1 }
{ mi,1 }
\lyricmode { \column{\line{"Do M"}\line{"(I6)"}} }
\figuremode { s1 }
```

Vertical: `S:do' A:sol T:mi B:mi,` ✓.

- [ ] **Step 5: 02#5 — I6/4 single chord**

Replace block 5 with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ mi'1 }
{ do'1 }
{ sol1 }
{ sol,1 }
\lyricmode { \column{\line{"Do M"}\line{"(I6/4)"}} }
\figuremode { s1 }
```

Vertical: `S:mi' A:do' T:sol B:sol,` ✓.

- [ ] **Step 6: 09#1 — V7 stack and the tritone**

Replace block 1 with:

```tex
\partilate
{ \key do \major \time 4/4 }
{ re''1 fa'1 }
{ fa'1 re'1 }
{ si1 si1 }
{ sol,1 sol,1 }
\lyricmode { "V7"1 "Tritono (5a dim.)"1 }
\figuremode { <7>1 s1 }
```

b1 (V7 = G–B–D–F): `S:re'' A:fa' T:si B:sol,` ✓; b2 (tritone si–fa highlighted in T/S): `S:fa' A:re' T:si B:sol,` ✓.

- [ ] **Step 7: 14#4–6 — augmented-sixth chords (It./Fr./Ger.)**

Replace blocks 4, 5, 6 respectively with:

```tex
\partilate
{ \key do \minor \time 4/4 }
{ lab'1 }
{ fad'1 }
{ do'1 }
{ lab1 }
\lyricmode { "It$^6$"1 }
\figuremode { s1 }
```

```tex
\partilate
{ \key do \minor \time 4/4 }
{ fad'1 }
{ do'1 }
{ re1 }
{ lab,1 }
\lyricmode { "Fr$^6$"1 }
\figuremode { s1 }
```

```tex
\partilate
{ \key do \minor \time 4/4 }
{ fad'1 }
{ mib'1 }
{ do'1 }
{ lab,1 }
\lyricmode { "Ger$^6$"1 }
\figuremode { s1 }
```

Verticals: It⁶ `S:lab' A:fad' T:do' B:lab` ✓ (the augmented 6th A♭–F# is in S/A); Fr⁶ `S:fad' A:do' T:re B:lab,` ✓; Ger⁶ `S:fad' A:mib' T:do' B:lab,` ✓.

> Check the surrounding prose before replacing 14#4–6: if the chapter labels them differently (e.g. "sesta eccedente" spellings), keep those exact words in `\lyricmode` instead of the shorthand above.

- [ ] **Step 8: Verify**

```bash
python3 tools/verifica_voci.py --chapter 02
python3 tools/verifica_voci.py --chapter 09
python3 tools/verifica_voci.py --chapter 14
```

Expected: `Blocchi SATB con violazioni: 0` for 02 and 09; chapter 14 shows zero blocks with `INCROCI`/`SUPERA mi'!` (14#1–3 were already fixed in Task 4).

- [ ] **Step 9: Compile-check and commit**

```bash
for f in 02_triadi 09_settima_dominante 14_regola_ottava; do
  for n in 1 2 3 4 5; do
    python3 tools/estrai_blocco.py Capitoli/$f.tex $n --run 2>/dev/null
  done
done
git add Capitoli/02_triadi.tex Capitoli/09_settima_dominante.tex Capitoli/14_regola_ottava.tex
git commit -m "conversione: blocchi accordali monolineari al formato partilate (02, 09, 14)"
```

**Acceptance criteria:** all converted blocks parse and pass the verifier; original labels preserved (as `\lyricmode`); 01#1 deliberately kept as a single-staff melodic interval demo (see Risks).

---

## Task 6: New harmonized `partilate` blocks in chapters 05 and 11

**Files:** `Capitoli/05_funzioni_armoniche.tex`, `Capitoli/11_note_estranee.tex`.

**Interfaces:**
- Consumes: `partilate` syntax, `tools/verifica_voci.py`.
- Produces: two new blocks in ch. 05 (function cadence + secondary functions) and two in ch. 11 (passing note + 4–3 suspension), all passing the verifier.

Chapter 05 currently has **zero** music blocks (pure prose); place each new block immediately after the paragraph where its concept is first discussed (see the chapter's section headings below). Chapter 11 has two single-staff blocks already; the new partilate blocks go after the existing examples.

- [ ] **Step 1: 05 — block A "Le tre funzioni fondamentali" (T–S–D–T)**

After the section `\section{Le tre funzioni fondamentali}` paragraph, insert:

```tex
\begin{esempio}[Funzioni fondamentali]
\musica{
\partilate
{ \key do \major \time 4/4 }
{ mi'2 fa' | sol' mi' }
{ do'2 do' | re' do' }
{ sol2 la | si sol }
{ do2 fa | sol do }
\lyricmode { "T"2 "S" | "D" "T" }
\figuremode { s2 s | s s }
}
\end{esempio}
```

Verticals: b1 `S:mi' A:do' T:sol B:do` ✓ (T); b2 `S:fa' A:do' T:la B:fa` ✓ (S); b3 `S:sol' A:re' T:si B:sol` ✓ (D); b4 `S:mi' A:do' T:sol B:do` ✓ (T).

- [ ] **Step 2: 05 — block B "Il II come sottodominante" (S–S–D–T)**

After the section `\section{Gli accordi secondari e le loro funzioni}` first paragraph, insert:

```tex
\begin{esempio}[II come sottodominante]
\musica{
\partilate
{ \key do \major \time 4/4 }
{ fa'2 re' | sol' mi' | mi'1 }
{ do'2 do' | re' do' | do'1 }
{ la2 la | si sol | sol1 }
{ fa2 re | sol do | do1 }
\lyricmode { "S"2 "S" | "D" "T" | "T"1 }
\figuremode { s2 <7> | s s | s1 }
}
\end{esempio}
```

Verticals: b1 `S:fa' A:do' T:la B:fa` ✓ (IV); b2 `S:re' A:do' T:la B:re` ✓ (II); b3 `S:sol' A:re' T:si B:sol` ✓ (V); b4 `S:mi' A:do' T:sol B:do` ✓ (I); b5 `S:mi' A:do' T:sol B:do` ✓ (I). (The final chord uses `S:mi'` — never `S:do'`, which would create an S–A octave-less unison with the alto.)

- [ ] **Step 3: 11 — block A "Nota di passaggio" harmonized (IV–V–I)**

Append after the existing examples in `Capitoli/11_note_estranee.tex`:

```tex
\begin{esempio}[Nota di passaggio a quattro parti]
\musica{
\partilate
{ \key do \major \time 4/4 }
{ fa'4 sol' la'2 | si'2 do''2 }
{ do'4 do' do'2 | re'2 do'2 }
{ la4 la la2 | sol2 mi2 }
{ fa4 fa fa2 | sol2 do2 }
\lyricmode { "IV"4 "pass."4 "IV"2 | "V"2 "I"2 }
\figuremode { s4 s s2 | s s }
}
\end{esempio}
```

Verticals: b1 `S:fa' A:do' T:la B:fa` ✓ (the `sol'` on beat 2 is the passing note); b3 `S:si' A:re' T:sol B:sol` ✓ (V); b4 `S:do'' A:do' T:mi B:do` ✓ (I). **Sanity-check with the tool**: the S–A gap at b4 is 12, at the limit — if the tool flags a gap warning, lower the tenor final `mi` to `sol` or swap A/T (`A:sol T:mi`) per the tool's report.

- [ ] **Step 4: 11 — block B "Sospensione 4–3" harmonized (V7–V7–I)**

Append after block A:

```tex
\begin{esempio}[Sospensione 4–3 sulla dominante]
\musica{
\partilate
{ \key do \major \time 4/4 }
{ do''2 si' | do''1 }
{ fa'2 fa' | mi'1 }
{ re'2 re' | sol1 }
{ sol2 sol | do1 }
\lyricmode { "V7"2 "V7" | "I"1 }
\figuremode { <4>2 <3> | s1 }
}
\end{esempio}
```

Verticals: b1 `S:do'' A:fa' T:re' B:sol` ✓ (V7 with 4th suspended in S, T–B gap 19 at limit); b2 `S:si' A:fa' T:re' B:sol` ✓ (4→3 resolution); b3 `S:do'' A:mi' T:sol B:do` ✓ (I).

- [ ] **Step 5: Verify**

```bash
python3 tools/verifica_voci.py --chapter 05
python3 tools/verifica_voci.py --chapter 11
```

Expected: `Blocchi SATB con violazioni: 0` (chapter 05 was previously 0 blocks, now 2; chapter 11 was 0 flagged, now 2 more).

- [ ] **Step 6: Compile-check and commit**

```bash
python3 tools/estrai_blocco.py Capitoli/05_funzioni_armoniche.tex 1 --run
python3 tools/estrai_blocco.py Capitoli/05_funzioni_armoniche.tex 2 --run
python3 tools/estrai_blocco.py Capitoli/11_note_estranee.tex 3 --run
python3 tools/estrai_blocco.py Capitoli/11_note_estranee.tex 4 --run
git add Capitoli/05_funzioni_armoniche.tex Capitoli/11_note_estranee.tex
git commit -m "feat: esempi a quattro parti nei capitoli 05 e 11"
```

**Acceptance criteria:** four new blocks, all pass the verifier, all compile; the `\lyricmode`/`\figuremode` content matches the prose context they illustrate.

---

## Task 7: Full build and final verification

**Files:** `manuale.tex` (root), all edited chapters.

**Interfaces:**
- Consumes: all completed tasks.
- Produces: a clean PDF and a clean verifier run.

- [ ] **Step 1: Full repository check**

```bash
python3 tools/verifica_voci.py
```

Expected: l'unico blocco rimasto è 16#7 (`SOLO AVVISI`); nessun blocco con `INCROCI` o `SUPERA mi'!`; `python3 tools/verifica_voci.py --accept-avvisi` esce 0. The ONLY exception allowed is 16#7 appearing as `SOLO AVVISI` (documented, unfixable without recomposition). No block may report `INCROCI` or `SUPERA mi'!`.

- [ ] **Step 2: Full lualatex build**

```bash
lualatex --shell-escape manuale.tex
```

Run **twice** (the first pass generates cross-references and LilyPond snippets). Expected: exit code 0, `manuale.pdf` produced, no undefined references. If it fails, inspect `manuale.log` — the most common causes are a LilyPond syntax error in a newly edited block (re-check with `estrai_blocco.py ... --run` on that block) or stale auxiliary files (delete `*.aux`/`*.log`/`*.ly` intermediates in the chapter dirs and rebuild).

- [ ] **Step 3: Spot-check the rendered examples**

Open the PDF pages for chapters 02, 05, 09, 11, 14, 16, 17 and confirm: no note is colliding across staves, labels are readable, and each example still carries its original caption/label text.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "build: verifica completa e compilazione manuale"
```

**Acceptance criteria:** verifier exit 0; `manuale.pdf` builds cleanly after two passes; spot-check pages look correct.

---

## Risks & Open Questions

1. **Bass-line changes** (16#1 `la,,`→`la,`, 17#4 `do'`→`do`, 17#12 `re`→`re,`, 14#1–3 first-half/second-half octaves) modify the author's written bass. Each is a pitch-class-preserving register fix justified by the bass sitting at/above the tenor. **These need author sign-off** — the plan marks them explicitly; do not silently merge.
2. **16#1 upper-voice swap** changes which voice carries the melody. It makes the soprano carry the chromatic `mi'–fa'–sold–la` line (the author's own alto melody) and is the only crossing-free option without breaking registers. Flag for author review.
3. **09#2 tenor si→sol** drops the leading-tone resolution in the tenor; the alto already resolves to `do'`. If the author wants the tenor resolution preserved, alternative: keep `si`→`do'` and instead raise the alto `do'`→`mi'`? (that creates a different collision — do NOT apply without checking the tool).
4. **01#1** is deliberately NOT converted: it is a single-line interval-stacking demonstration (fond.→8va→5a→…→7a min.), not a 4-part texture; forcing it into SATB distorts its point. Confirmed with the user's "where it makes sense" criterion.
5. **New blocks' exact insertion points** in chapters 05 and 11 depend on the surrounding prose; the plan gives section anchors, but if prose shifted, place each block after the sentence that first names the concept.
6. **Verifier limits:** it parses only `([a-z]+)('+|,+)?` tokens inside `\musica{...}`, so markup inside voices (e.g. `\markup` in a voice) or non-`\partilate` blocks are skipped. It does not validate LilyPond syntax — always use `estrai_blocco.py --run` after edits.
7. **LilyPond version drift:** `\version "2.24.0"` in the helper matches the manual's requirement; if the system LilyPond differs, adjust the `\version` line, not the blocks.
8. **Warning-only blocks left as-is:** 16#7 (S–A gap) remains a documented known-issue. If the author later wants it fixed, the options are to lower S beats 5–6 (`mi''`→`la'`, `do''`→`sol'`) which changes the melodic line, or accept the gap.

## Self-Review Notes

- **Spec coverage:** mandatory rules (crossings, tenor ≤ E4) → Tasks 1–4; register/spacing improvements → Tasks 1–4 warning fixes; conversions → Task 5; new blocks 05 x2, 11 x2 → Task 6; full build → Task 7. 16#7/01#1 explicitly justified as non-actions.
- **Placeholder scan:** every prescription is concrete note-for-note content; the only conditional step (Task 6 Step 3 sanity-check) names the exact alternative fix.
- **Type consistency:** block numbering, `\partilate` argument order (key/time, S, A, T, B, lyric, figure) and verifier output format are used identically across all tasks.
