# Analizzatore di armonia complementare

CLI Python locale per analizzare un corale SATB in MusicXML e salvare un report didattico Markdown accanto alla partitura. Implementa il progetto descritto in [PROGETTO.md](PROGETTO.md).

Richiede **Python 3.12 o successivo**. Non occorrono un server, un database o un programma di notazione. L'installazione iniziale richiede l'accesso a PyPI; l'analisi è offline.

## Installazione e avvio

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m armonia
```

Su Windows attivare l'ambiente con `.venv\Scripts\activate`. È disponibile anche il comando `armonia` dopo l'installazione.

Se music21 è già installato nel Python usato per creare l'ambiente, riutilizzarlo con `python3 -m venv --system-site-packages .venv`. Nel checkout attuale questa impostazione è già attiva: avviare direttamente `.venv/bin/python -m armonia`.

Al prompt inserire il percorso `.musicxml` o `.xml`, anche con spazi, accenti, `~` o virgolette esterne. Provare `esempi/corale.musicxml`: è un esercizio dimostrativo con problemi intenzionali, non un modello da imitare.

Il file di uscita ha forma `corale_analisi_20261018_153012_123456.md`. Data locale, offset UTC, versioni, convenzioni e copertura sono inclusi nel documento. Non vengono sovrascritti report esistenti. Se la destinazione non è scrivibile, si può indicare un'altra **cartella**, conservando l'analisi già calcolata. La pubblicazione atomica richiede un filesystem che supporti gli hard link all'interno della cartella.

Un ingresso vuoto chiude la sessione; Ctrl+C interrompe. Se i nomi delle linee non identificano SATB, viene chiesta una mappatura unica: quattro indici nell'ordine soprano, contralto, tenore, basso. Le altezze non vengono riordinate: incroci e sovrapposizioni restano visibili.

| Codice di uscita | Significato |
|---|---|
| 0 | Report completo rispetto al profilo, anche con errori musicali; oppure uscita volontaria iniziale |
| 1 | Fallimento operativo o uscita dopo un ingresso non valido senza produrre un report |
| 2 | Report salvato con copertura parziale |
| 130 | Interruzione con Ctrl+C |

## Copertura musicale

Il profilo [complementare_it.toml](armonia/profili/complementare_it.toml) dichiara versione, soglie, definizioni, eccezioni, fonti ed esempi. Il motore esamina tutte le sei coppie sulla superficie musicale e propone accordi, rivolti, figurazioni e contesti tonali. Comprende controlli su cadenze (tipo e chiusura), risoluzioni di napoletana, seste eccedenti, 6/4 cadenzale e ritardi, progressioni e modulazioni/tonicizzazioni (`armonia/sintassi.py`), oltre a parallele, dirette, incroci, sovrapposizioni, distanze, registri, salti, sensibile, settime, quarta e sesta, cifratura, simboli accordali e sincope armonica.

Le interpretazioni armoniche sono ipotesi. Un caso condizionato non entra nel totale degli errori confermati. Non viene attribuito un voto; non viene certificata la correttezza assoluta dell'esercizio.

**Il profilo iniziale produce report parziali (codice 2):** false relazioni di tritono, grammatica estesa, accordi alterati e modulazioni estese non hanno ancora una definizione operativa validata. Il report indica inoltre i segmenti non interpretabili e le cifrature non supportate. Le regole indipendenti dalla tonalità restano utilizzabili.

Sono supportate quattro parti monodiche oppure due pentagrammi con voci separate, pause, legature, anacrusi, metri semplici/composti regolari e cambi di armatura. XML limitato a 10 MiB e 20000 note; solo `score-partwise`. Archivi `.mxl`, parti trasposte, microtoni, percussioni, note senza durata e metri irregolari richiedono una riesportazione. Gli accordi che hanno perso l'identità delle voci non vengono separati artificialmente. Ritornelli e finali sono segnalati e analizzati solo nell'ordine scritto.

La riduzione supporta una figurazione superiore alla volta. Non ricostruisce tutte le parallele nascoste da ornamenti. La rilevazione di tonicizzazioni richiede una dominante secondaria seguita dalla risoluzione osservata; non basta un'alterazione isolata. Il basso è quello del file: senza la consegna originale non si verifica che lo studente l'abbia conservato.

Prima dell'impiego per un esame, un docente deve validare regole, esempi ed eccezioni sul proprio programma e su un corpus indipendente. Questa validazione non è stata eseguita.

## Verifiche

```bash
python -m unittest discover -v
python -m compileall -q armonia tests
```

I test musicali richiedono music21: in sua assenza sono marcati `skipped`, non verificati. Una suite con casi saltati non dimostra che l'integrazione musicale funzioni. Per una verifica completa installare prima il progetto e richiedere una suite senza skip, poi analizzare l'esempio da terminale. `tests/support.py` genera fixture MusicXML con music21; attese ed esempi sono dichiarati nei test.

## File

- `armonia/__main__.py`: prompt e recupero degli errori.
- `armonia/lettura.py`: XML sicuro e ricostruzione delle linee.
- `armonia/analisi.py`: timeline, contesti e ipotesi armoniche.
- `armonia/sintassi.py`: cadenze, risoluzioni cadenzali/alterate, progressioni, modulazioni (ogni segnalazione dichiara se richiede verifica manuale: nel report la riga «Verifica manuale»).
- `armonia/regole.py`: controlli e risultati tracciabili.
- `armonia/report.py`: Markdown e salvataggio atomico.
- `armonia/profili/complementare_it.toml`: convenzioni musicali versionate.
