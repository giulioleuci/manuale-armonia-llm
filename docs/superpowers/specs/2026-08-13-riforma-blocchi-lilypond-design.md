# Riforma dei blocchi LilyPond: voci, incroci e linee di guida

Data: 2026-08-13

## Contesto e obiettivo

Il manuale contiene **86 blocchi musicali** (tutti racchiusi nel wrapper `\musica`):
56 scrittura a quattro parti SATB (via `\partilate`) e ~30 blocchi non-SATB
(singole linee di basso/esercizi, accordi dimostrativi, melodie).

L'obiettivo è duplice:

1. **Correggere tutti i blocchi esistenti** applicando le regole obbligatorie
   della scrittura corale:
   - **Mai incrociare le voci**: a ogni verticale vale Basso < Tenore < Contralto
     < Soprano (vietati incrocio E unisono).
   - **Linee di guida**: evitare il più possibile le note del Tenore sopra il
     rigo in chiave di basso; ammesse solo per do' (C4) e re' (D4), tollerato
     mi' (E4). Mai sopra E4.
   - Conservare il **basso dato e il basso figurato** (inviolabili), la funzione
     armonica, il ruolo delle voci citato nel testo e il punto didattico di ogni
     esempio (frecce `\freccia`/`\frecciag`, errori dimostrativi).
2. **Massimizzare l'uniformità**: convertire a `\partilate` i blocchi
   dimostrativi di accordi che oggi usano `\new Staff`/`\PianoStaff` grezzi.

## Regole di correzione (Parte 1 — 56 blocchi SATB)

- Ordine delle voci a ogni verticale: Basso < Tenore < Contralto < Soprano.
- Registro del Tenore: preferibilmente dentro il rigo di basso (Do–La,
  C3–A3); linee di guida solo per do'/re' (mi' tollerato), mai sopra mi'.
- Dopo ogni re-voicing verificare: Soprano–Contralto ≤ 8ª, Contralto–Tenore ≤
  8ª, Tenore–Basso ≤ 12ª, estensioni SATB (def:estensione_voci).
- Preservare: basso dato, figurazione, grado (`\lyricmode`), la nota specifica
  citata per voce nel testo (es. "la sensibile al contralto"), il collegamento
  delle frecce di glissando (stesse coppie di note, in nuova ottava).
- Negli esempi-errore (quinte/ottave parallele ecc.) mantenere l'errore
  dimostrato ma in registro corretto e senza incroci.

### Metodo di lavoro

1. Diagnosticare ogni blocco (script Python già scritto: parsa i `\partilate`,
   calcola incroci e superi di registro a ogni verticale).
2. Rieseguire la diagnostica dopo ogni capitolo modificato: tolleranza zero
   incroci e zero superi di E4.
3. Verifica finale: compilazione completa `lualatex --shell-escape manuale.tex`.

## Uniformità (Parte 2 — conversione a `\partilate`)

Convertire i blocchi dimostrativi di accordi, scrivendo accordature SATB a
quattro parti coerenti con le regole della Parte 1:

- `01_fondamenti` blocco 1 (posizioni/inversioni della triade)
- `02_triadi` blocchi 1–5 (triadi sui gradi + inversioni)
- `09_settima_dominante` blocco 1 (V7 e rivolti)
- `14_regola_ottava` blocchi 4–6 (sonorità di settima diminuita)

Restano single-line `\musica` (esercizi da armonizzare: non si convertono,
sarebbe controproducente): `07/1`, `11/1–2`, `17/3,6,8,9,10`, `18/1,3`, `19/1`,
`20/1,3,6,7,8,9,10`.

## Nuovi blocchi (Parte 3)

- **Cap. 05**: due realizzazioni a quattro parti della Regola dell'Ottava
  (Do maggiore ascendente e discendente), secondo le liste di `reg:regola_ottava_maggiore_asc`/`disc`.
- **Cap. 11**: esempi di nota di volta e di appoggiatura, coerenti con lo stile
  del capitolo.

## Criteri di completamento

- Diagnostica: 0 incroci, 0 note di Tenore sopra mi', in tutti i 56+ blocchi SATB.
- Il documento compila con `lualatex --shell-escape manuale.tex` senza errori
  di LilyPond introdotti.
- Il testo (note nominate per voce, basso dato, figurazione) resta coerente
  con la notazione.
