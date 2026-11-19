# Verifica dell’implementazione — 18 ottobre 2026

Ambiente: Python 3.14.7, music21 10.5.0, defusedxml 0.7.1. Python 3.12 non disponibile per una prova diretta.

- `python -m unittest discover -v`: **70 test eseguiti con successo, nessun caso saltato**.
- `python -m compileall -q armonia tests`: riuscito.
- `python -m build --no-isolation`: sdist e wheel costruiti.
- Contenuto degli archivi controllato: profilo TOML nella wheel, specifica/esempio/helper di test nello sdist.
- Wheel installata senza dipendenze; avvio da altra cartella e caricamento del profilo verificati.
- Sicurezza XML, Markdown, collisioni, pulizia dopo errore di scrittura, annullamento e recupero del salvataggio verificati.
- Importazione a quattro parti e due pentagrammi, pause, legature, anacrusi, metri composti, cambi di tonalità e controlli musicali verificati con music21.
- Esecuzione reale della CLI su `esempi/corale.musicxml`: report generato, tonalizzazione di Sol riconosciuta, uscita 2 prevista per il profilo parziale.

music21 è disponibile nel Python Miniconda del sistema. Il virtualenv è configurato con `include-system-site-packages = true` per riutilizzarlo; defusedxml è installato nell'ambiente locale. Non è stato necessario scaricare nuovamente music21.

Una revisione indipendente ha individuato tre problemi, corretti nel codice: risoluzioni dopo note ribattute, realizzazioni successive dello stesso accordo e alterazioni implicite nella cifratura. Le regressioni musicali ora passano. L'esecuzione completa ha inoltre corretto la lettura del metro interno alla prima misura e le fixture (metadati SATB, legature prima dell'esportazione, pause finali e casi di risoluzione con un accordo di tonica effettivo).

Per ripetere la verifica nel checkout attuale:

```bash
source .venv/bin/activate
python -m unittest discover -v
python -m armonia
```

Al prompt usare `esempi/corale.musicxml`: il profilo iniziale produce un report parziale con uscita 2. La validazione didattica da parte di un docente su corpus indipendente resta necessaria e non è stata effettuata.
