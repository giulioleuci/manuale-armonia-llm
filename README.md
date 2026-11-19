# Appunti sparsi di Armonia

Manuale di armonia tonale in italiano, composto in LaTeX (LuaLaTeX).

> **Questo manuale è scritto da LLM.**
> Il testo, gli esempi musicali e il codice che li produce e li verifica sono stati generati in gran parte da modelli linguistici (Google Gemini e Claude di Anthropic). L'autore, fisico di formazione e insegnante di matematica, ha scelto l'impostazione, ha guidato la stesura a partire dalle lezioni del proprio insegnante e dalla manualistica classica, e ha riletto e corretto il risultato. Gli LLM non hanno orecchio e dicono il falso con lo stesso tono del vero: **il manuale può contenere errori**. Va confrontato con un insegnante e con i testi di riferimento.

## Che cos'è

Una guida alla sintassi tonale che parte dai principi (acustica, aritmetica degli intervalli) e ne ricava le regole, in nove parti: basi acustiche e tonali, triade e scrittura a quattro parti, funzioni e cadenze, progressioni di triadi, dissonanza, settime, modulazione, armonia cromatica, basso dato.

Ogni concetto segue lo schema di un capitolo di matematica: definizione, regola, esempio, errore. Box «Con la fisica» e «Con la matematica» (Appendice A) approfondiscono i fondamenti scientifici. Non è un eserciziario.

## Come lavorano gli LLM qui

- **Testo:** spiegazioni, riepiloghi e box scritti e riveduti con Gemini e Claude, poi riletti dall'autore.
- **Esempi musicali:** non sono disegnati a mano. Un motore di incisione in Python (`tools/armonia/`, ReportLab e FontTools, font Bravura) produce PDF vettoriali; un solver (`solver.py`, `registro.py`) sceglie il collegamento delle quattro voci.
- **Verifica:** un rivelatore di errori armonici (`tools/rivelatore-errori-armonia/`) controlla gli esempi SATB: parallele, sensibile, settime, salti, distanze, cadenze, risoluzioni, progressioni, modulazioni. I test (`tests/`) fanno fallire la build sui vincoli rigidi.

## Compilare

Servono TeX Live con LuaLaTeX e Python 3.

```bash
pip install -r requirements.txt
python3 tools/build_esempi.py      # genera gli esempi in esempi_gen/
lualatex manuale.tex               # due passate per indici e riferimenti
```

Test e verifica armonica degli esempi (il rivelatore vuole il proprio ambiente, vedi il suo README):

```bash
python3 -m pytest tests
tools/rivelatore-errori-armonia/.venv/bin/python -m tools.verifica_esempi
```

Il PDF e gli esempi generati non sono nel repository: si ottengono con i comandi sopra.

## Struttura

```
manuale.tex, preamble.tex, styles.tex, music_macros.tex   documento e macro
Capitoli/                                                 un file per capitolo
tools/armonia/                                            motore di incisione e solver
tools/esempi/                                             generatori degli esempi per capitolo
tools/rivelatore-errori-armonia/                          analizzatore di errori armonici
tests/                                                    test
docs/                                                     materiali di lavoro
```

`CLAUDE.md`, `AGENTS.md` e `GEMINI.md` contengono le convenzioni di progetto per gli agenti LLM che lavorano sul repository.

## Licenza e font

Nessuna licenza è stata ancora scelta per testo e codice. I font in `tools/armonia/fonts/` (Bravura, EB Garamond) sono sotto SIL Open Font License; i testi delle licenze sono nella stessa cartella.
