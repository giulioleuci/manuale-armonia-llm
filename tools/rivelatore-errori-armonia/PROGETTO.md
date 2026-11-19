# Analizzatore di armonia complementare

Specifica progettuale — 18 ottobre 2026. Non contiene implementazione.

## Obiettivo e criterio musicale

Applicazione Python locale che riceve un corale già armonizzato a quattro voci, scritto sopra un basso dato, e produce un’analisi didattica in Markdown. L’interazione ordinaria richiede soltanto il percorso del MusicXML.

Il riferimento è l’esame di armonia complementare in Italia: armonia tonale scolastica, scrittura SATB, attenzione alla condotta delle parti, alla realizzazione del basso e al ritmo armonico. Non si presume che un corale storico di Bach rispetti tutti i divieti di un esercizio scolastico.

Non è stato indicato un trattato o un docente. Il profilo iniziale, denominato `complementare_it`, deve quindi dichiarare le proprie convenzioni: non esiste qui la pretesa di certificare un unico regolamento valido per ogni commissione italiana. Il report riporta sempre versione del profilo, regole applicate ed eccezioni.

Un risultato utile deve spiegare dove si trova il problema, quali note coinvolge, perché è segnalato e quale principio permette di correggerlo. Nessun voto numerico automatico senza una griglia di valutazione concordata.

## Approccio scelto

Si propone un motore deterministico di regole musicali sopra music21. Rispetto a un semplice controllo di intervalli, permette di esaminare accordi, ritmo e risoluzioni; rispetto a un modello generativo, permette di ricostruire ogni segnalazione dalle note e dalla regola applicata.

Il riconoscimento armonico produce ipotesi motivate. Le regole indipendenti dalla tonalità restano utilizzabili anche quando l’interpretazione di un accordo è dubbia. Le valutazioni dipendenti da un’ipotesi incerta vengono marcate come tali.

## Pacchetti e ambiente

Ambiente proposto: Python 3.12, ambiente virtuale e dipendenze fissate a versioni compatibili al momento dell’implementazione.

| Strumento | Impiego |
|---|---|
| `music21` | Importazione MusicXML; note, durate, intervalli, metrica, accordi, tonalità e supporto all’analisi dei collegamenti |
| `defusedxml` | Protezione della lettura XML, integrata prima del caricamento attraverso music21 |
| `pathlib`, `datetime`, `zoneinfo` | Percorsi, nome del report e data con fuso orario |
| `fractions` | Posizioni temporali esatte, senza arrotondamenti dei tempi musicali |
| `dataclasses`, `enum`, `itertools` | Pochi dati di analisi, stati e sei coppie di voci |
| `tomllib` | Lettura del profilo di regole in TOML, senza dipendenze aggiuntive |
| `tempfile`, `os` | Scrittura del report senza lasciare un file finale incompleto |
| `unittest` | Verifiche previste durante lo sviluppo |

Il Markdown è testo UTF-8 generato direttamente. Non servono un renderer, un database, un server o un programma di notazione installato. L’analisi ordinaria avviene offline.

music21 importa MusicXML e offre strumenti di analisi, ma non costituisce da solo un correttore dell’esame italiano. In particolare, i suoi rilevatori di intervalli nascosti individuano anche casi ammessi: il giudizio spetta al profilo dell’applicazione. Alcuni metodi sulle quinte includono anche movimenti contrari; l’applicazione deve distinguere esplicitamente queste categorie. [Importazione](https://music21.org/music21docs/usersGuide/usersGuide_08_installingMusicXML.html), [condotta delle parti](https://music21.org/music21docs/moduleReference/moduleVoiceLeading.html).

## UX e interfaccia da terminale

Avvio previsto: `python -m armonia`.

Esempio di interazione, non codice dell’applicazione:

```text
Analisi di armonia complementare
Profilo: complementare_it

File MusicXML: /home/utente/Musica/Corale 01.musicxml

Lettura della partitura...
Voci riconosciute: Soprano, Contralto, Tenore, Basso
Analisi della condotta delle parti...
Analisi degli accordi e del ritmo armonico...
Scrittura del report...

Analisi completata.
Errori: 4 | Avvertimenti: 3 | Casi da verificare: 2
Report: /home/utente/Musica/Corale 01_analisi_20261018_153012_123456.md
```

I conteggi sono puramente illustrativi. Le fasi devono corrispondere a lavoro effettivo; non serve una percentuale di avanzamento artificiale. I messaggi rimangono comprensibili senza colori o simboli grafici.

Comportamento dell’ingresso:

- Accettare percorsi assoluti o relativi, spazi e un’eventuale coppia esterna di virgolette; espandere `~`.
- Accettare `.musicxml` e `.xml`, verificando il contenuto MusicXML e non soltanto l’estensione. La prima versione non include archivi `.mxl`.
- File inesistente, illeggibile o XML non valido: messaggio italiano concreto e nuova richiesta del percorso.
- File vuoto al prompt: uscita; `Ctrl+C`: annullamento pulito.
- In caso di assegnazione ambigua delle voci, chiedere una sola mappatura delle linee disponibili verso S/A/T/B. Non chiedere note per nota.
- Se le quattro linee non sono ricostruibili dai dati, spiegare come riesportare la partitura con voci separate; non inventarle.

Non occorre chiedere il nome di uscita. Il file viene salvato accanto all’ingresso, conservando il nome senza l’ultima estensione:

`<nome ingresso>_analisi_<YYYYMMDD_HHMMSS_microsecondi>.md`

Esempio: `corale.esame.xml` diventa `corale.esame_analisi_20261018_153012_123456.md`. Usare l’ora locale e riportare nel documento il timestamp completo con offset UTC. I microsecondi riducono le collisioni; un controllo di esistenza impedisce comunque di sovrascrivere report precedenti.

Se la cartella non è scrivibile, proporre un percorso alternativo da terminale e conservare in memoria l’analisi già calcolata. Il successo viene annunciato solo dopo il salvataggio. Codici di uscita: 0 per report completo, anche con errori musicali; 1 per fallimento operativo; 2 per report parziale; 130 per interruzione.

## Contratto dell’ingresso

Sono previsti quattro strumenti/parti monodiche oppure due pentagrammi con due voci ciascuno. L’identità delle parti si ricava da metadati, staff e identificatori di voce; le altezze servono come indizio, non per riordinare le voci a ogni accordo. Altrimenti un vero incrocio verrebbe cancellato dall’importazione.

Note simultanee nello stesso oggetto accordale non identificano necessariamente voci distinte. Se un’esportazione ha perso le identità, l’applicazione deve segnalarlo. Le durate diverse, le pause e le note tenute sono ammesse; una voce temporaneamente in pausa non rende da sola il file invalido.

Per la prima versione si richiede un unico brano, quattro linee vocali senza trasposizione, metrica interpretabile e altezze nel sistema temperato ordinario. Strutture non supportate devono essere riconosciute e dichiarate. Ritornelli e finali alternativi vanno riportati: si analizza l’ordine scritto, senza fingere di avere controllato i collegamenti prodotti dai salti di esecuzione.

L’applicazione verifica la realizzazione rispetto al basso presente nel file. Un solo MusicXML non permette di accertare che lo studente abbia conservato il basso della consegna originale. Se contiene cifratura del basso, questa diventa un vincolo esplicito; eventuali simboli accordali sono annotazioni da confrontare, non una verità automaticamente affidabile.

## Dati musicali e sequenza di analisi

Flusso: lettura → identificazione SATB → linea temporale → ipotesi armoniche → controlli → report.

1. **Validare e importare.** Conservare misure originali, anacrusi, cambi di metro e armatura, nomi delle parti, cifrature ed eventuali annotazioni armoniche. Imporre limiti ragionevoli di dimensione e rifiutare riferimenti XML esterni.
2. **Ricostruire le quattro linee.** Per ogni evento conservare voce, altezza scritta e ottava, alterazione, attacco, durata, pausa e legatura. Una nota legata continua a suonare ma non è un nuovo attacco.
3. **Costruire la linea temporale.** Inserire confini agli attacchi, alle conclusioni delle note, ai cambi di contesto e agli accenti metrici pertinenti, anche senza nuovi attacchi. Questo ultimo punto serve a individuare un’armonia che attraversa un battere.
4. **Riconoscere il contesto tonale.** Usare armatura e analisi globale come indizi; verificare centri locali attraverso alterazioni, cadenze e successioni. Un’armatura non distingue da sola maggiore e relativo minore. Se manca una lettura univoca, conservare le alternative.
5. **Segmentare le armonie.** Formulare insieme ipotesi di accordo e di note estranee, esaminando preparazione e risoluzione. Non ridurre ogni nuova combinazione verticale a un nuovo accordo e non eliminare automaticamente ogni nota dissonante.
6. **Eseguire i controlli.** Esaminare tutte le sei coppie di voci e le successioni armoniche, distinguendo movimenti reali, note tenute, pause e ornamenti. Un cambiamento di una terza voce non crea un nuovo collegamento nella coppia ferma.
7. **Consolidare i risultati.** Unificare duplicati della stessa regola sullo stesso evento; collegare le segnalazioni dipendenti da una causa comune. Non contare una nota tenuta come molti errori identici.

Le verifiche sulla superficie musicale e quelle sulla riduzione armonica hanno etichette diverse. Una riduzione incerta non deve generare una quinta parallela classificata come certa. I collegamenti attraverso pause o confini di frase non vengono trattati indiscriminatamente come collegamenti simultanei.

Ogni risultato conserva: identificatore della regola, posizione iniziale e finale, voci, note, evidenza, interpretazione armonica richiesta, gravità, affidabilità e spiegazione. Per identificare la posizione usare numero originale della misura, indice interno e posizione metrica; nei metri composti mostrare pulsazione e suddivisione senza ambiguità.

## Catalogo dei controlli

“Tutto ciò che è errore” diventa un catalogo esplicito e verificabile. Ogni regola deve avere definizione, condizioni di applicazione, eccezioni, fonte e casi esemplificativi. Il report elenca anche i controlli non applicabili o non supportati.

| Famiglia | Controllo previsto | Convenzione e cautele |
|---|---|---|
| Quinte parallele | Quinte giuste consecutive fra la stessa coppia in moto nella stessa direzione, comprese le forme composte | Controllare tutte le coppie; non confondere quinta diminuita e giusta |
| Ottave e unisoni | Ottave, ottave composte e unisoni consecutivi | Distinguere ottave, unisoni e loro successioni; evitare scorciatoie basate solo sui semitoni modulo 12 |
| Intervalli perfetti per moto contrario | Successioni di quinte/ottave con cambiamento di registro o moto contrario | Categoria separata dalle parallele; divieto e ambito espliciti nel profilo |
| Quinte e ottave dirette/nascoste | Arrivo a intervallo perfetto per moto retto da un intervallo diverso | “Dirette” e “nascoste” indicano qui lo stesso fenomeno; valutare coppia di voci, salto della voce superiore ed eccezioni |
| Quinte disuguali | Passaggi fra quinta diminuita e quinta giusta | Regola autonoma: distinguere direzione, parti coinvolte e risoluzione |
| Relazioni cromatiche | Stesso nome di nota con alterazioni incompatibili fra voci, simultanee o in armonie successive | Considerare ortografia, contesto tonale, distanza temporale e passaggi cromatici ammessi |
| False relazioni di tritono | Relazioni trasversali fra note di armonie successive | Non basta trovare un tritono: occorre una fattispecie vietata dal profilo; altrimenti caso da verificare |
| Incroci | Una voce supera l’altezza di quella adiacente | Conservare le identità SATB; distinguere unisono e incrocio |
| Sovrapposizioni | Una voce oltrepassa la posizione precedente della voce vicina | Distinte dall’incrocio simultaneo |
| Distanze | Spaziatura fra soprano–contralto e contralto–tenore | Profilo iniziale: oltre l’ottava da segnalare; il basso–tenore ha trattamento distinto |
| Estensione e cantabilità | Note fuori registro, salti problematici, intervalli aumentati/diminuiti e successioni difficili | Estensioni e salti ammessi dichiarati nel profilo; distinguere scomodità ed errore formale |
| Sensibile | Raddoppio e mancata risoluzione quando richiesta | Riconoscere sensibile locale, parti interne, prolungamenti e risoluzioni eccezionali ammesse |
| Dissonanze accordali | Preparazione quando richiesta, risoluzione di settime e altri suoni obbligati | Regole specifiche per specie di accordo; non imporre la stessa preparazione a ogni settima |
| Raddoppi e omissioni | Raddoppi incompatibili, note essenziali mancanti, accordi incompleti | Dipende da grado, rivolto, posizione e collegamento; il raddoppio della terza non è un divieto universale |
| Rivolti | Uso e risoluzione dei rivolti delle triadi e delle settime | Per il 6/4 distinguere almeno cadenza, passaggio e pedale; classificare le altre forme come incerte finché non definite |
| Figurazioni | Ritardi, appoggiature, anticipazioni, note di passaggio e di volta | Controllare accento, preparazione se richiesta e risoluzione; non trattarle tutte come accordi sbagliati |
| Ritmo armonico | Sincopi armoniche e articolazione degli accenti | Confrontare identità armonica oltre la disposizione delle note e il semplice nuovo attacco |
| Collegamenti | Successioni incompatibili con la grammatica scolastica adottata | Contestualizzare progressioni, cadenze, pedali e prolungamenti; evitare un divieto universale ottenuto da una tabella di due accordi |
| Cromatismo e modulazione | Dominanti secondarie, accordi alterati, tonicizzazioni, cambio di centro | Considerare anche il modo minore e i suoi gradi mobili; non classificare ogni alterazione come errore |
| Consegna cifrata | Conformità delle note e degli intervalli alle cifre presenti | La verifica richiede una cifratura interpretabile nel file; assenza di cifre esplicitata |

Per le dirette, il profilo iniziale proposto segnala come vietati gli arrivi per moto retto a quinta/ottava fra basso e soprano con salto del soprano; tratta separatamente le eccezioni specifiche. I casi nelle parti interne vengono rilevati e rimangono da verificare finché il profilo non ne definisce il trattamento. È una scelta progettuale prudente, non l’affermazione di una norma italiana unica. Anche i materiali didattici pubblicati differiscono nel trattamento delle dirette: [Open Music Theory](https://openmusictheory.github.io/bassoContinuo.html).

### Sincope armonica

Il controllo cerca la prosecuzione o ripresentazione della stessa armonia da una posizione debole a una più forte, fra battute e nei punti interni previsti dal metro. Ribattere le note, cambiare disposizione o cambiare solo il rivolto non deve cancellare automaticamente il fenomeno. La coincidenza della sola funzione armonica è invece un indizio più debole dell’identità dell’accordo.

Il profilo deve distinguere la ripetizione dell’accordo dai collegamenti fra accordi della stessa famiglia funzionale e dichiarare eventuali divieti aggiuntivi. Anacrusi, pedali e formule cadenzali richiedono eccezioni definite: non si esenta automaticamente ogni fenomeno chiamato “anticipazione”. Dove la distinzione non è sicura, il risultato resta da verificare.

Il divieto scolastico di prolungare l’armonia dal debole al forte è trattato nei [Quaderni di teoria, analisi e composizione del Liceo Bertolucci](https://www.liceoattiliobertolucci.edu.it/wp-content/uploads/2023/11/Lezioni-di-armonia.pdf). Gli [Appunti di Carmine Emanuele Cella](https://www.carminecella.com/teaching/note_armonia.pdf) mostrano anche l’importanza dei collegamenti funzionali nello stile severo: sono riferimenti iniziali per costruire il catalogo, da precisare sulle convenzioni dell’esame.

## Valutazione degli accordi scelti

Per ciascun segmento il report deve rispondere a quattro domande:

1. Quali note sono strutturali e quali sono figurazioni?
2. Quale accordo, fondamentale e rivolto spiegano il segmento nella tonalità locale?
3. La costruzione e la disposizione rispettano cifratura, raddoppi, omissioni e vincoli del basso?
4. L’accordo è appropriato rispetto alla funzione precedente e successiva, all’accento, alla frase e alle risoluzioni?

Produrre una lettura principale e, quando rilevante, un’alternativa motivata. Non serve enumerare ogni accordo teoricamente possibile. Preferire la lettura che spiega il contesto con meno assunzioni, ma non scegliere un’analisi soltanto per far scomparire un errore. Se due letture plausibili producono giudizi diversi, rendere il giudizio condizionale.

Esempi di esito: “compatibile con il contesto analizzato”, “costruzione incompatibile con la cifratura”, “collegamento da verificare”, “interpretazione non determinabile”. Un basso senza cifre ammette spesso più armonizzazioni: l’assenza di una soluzione attesa impedisce di giudicare sbagliata ogni scelta diversa da una preferenza del motore.

music21 può proporre numeri romani anche per combinazioni insolite. Il riconoscimento non certifica l’appropriatezza scolastica, e l’interpretazione delle dominanti secondarie richiede contesto aggiuntivo. [Documentazione del modulo roman](https://music21.org/music21docs/moduleReference/moduleRoman.html).

## Struttura del report Markdown

1. **Dati dell’analisi:** file, data e fuso, versione applicazione e music21, profilo e convenzioni, mappatura SATB, tonalità proposte, metro, misure.
2. **Sintesi:** analisi completa o parziale, conteggi per famiglia e gravità, punti prioritari da rivedere. “Nessuna violazione rilevata dalle regole applicate” sostituisce una certificazione assoluta di correttezza.
3. **Analisi armonica:** tabella dei segmenti con posizione, basso, note strutturali, figurazioni, tonalità locale, grado/rivolto, funzione, esito e affidabilità.
4. **Segnalazioni:** indice cronologico e dettagli con rimandi interni; ogni problema ha note, posizione, regola, eccezioni valutate e spiegazione didattica.
5. **Valutazione dell’armonizzazione:** scelte compatibili, criticità di costruzione, collegamenti dubbi e letture alternative.
6. **Copertura e limiti:** regole applicate, disattivate, non supportate e non valutabili, con intervalli della partitura interessati.

Gravità e affidabilità sono due campi separati. Gravità: errore, avvertimento, osservazione. Affidabilità: certa sui dati e sul profilo, condizionata all’analisi, da verificare. Niente percentuali inventate. Un’ambiguità non viene inclusa nel conteggio degli errori confermati.

Esempio di scheda nel report:

> **E001 — Quinte parallele — errore**  
> **Posizione:** battuta 4, tempo 1 → tempo 2.  
> **Voci:** basso e soprano.  
> **Note:** basso Do3 → Re3; soprano Sol4 → La4.  
> **Evidenza:** due dodicesime giuste consecutive, con entrambe le parti ascendenti.  
> **Regola:** VL-P5, successione vietata nel profilo applicato.  
> **Affidabilità:** certa sui dati importati.  
> **Indicazione:** rivedere la condotta del soprano o il collegamento delle parti superiori, conservando il basso dato e ricontrollando le altre coppie.

Le proposte sono indicazioni motivate. Non si suggerisce una sostituzione puntuale come certamente corretta senza averne ricontrollato gli effetti sulle altre voci e sugli accordi vicini.

## Organizzazione minima dell’applicazione

Un solo pacchetto `armonia`, suddiviso per responsabilità:

- `__main__.py`: prompt, messaggi, gestione dell’annullamento e uscita.
- `lettura.py`: importazione, validazione, mappatura e normalizzazione SATB.
- `analisi.py`: linea temporale, segmentazione, ipotesi armoniche e contesto.
- `regole.py`: controlli musicali e produzione delle segnalazioni.
- `report.py`: ordinamento, spiegazioni e salvataggio Markdown.
- `profili/complementare_it.toml`: convenzioni, soglie ed eccezioni versionate; nessun linguaggio di regole generico.

Usare gli oggetti di music21 finché sono adatti; aggiungere soltanto i dati necessari per tracciare provenienza e risultati. Nessun sistema di plugin o gerarchia di classi per ogni regola. Il profilo modifica criteri già implementati, senza eseguire codice arbitrario.

## Verifica prevista e criteri di accettazione

Queste sono attività del futuro sviluppo; non sono state eseguite e non implicano codice già disponibile.

- Ogni regola necessita di un piccolo esempio vietato, uno ammesso e, quando esiste, un’eccezione. Le risposte musicali attese devono essere validate da un docente competente nel profilo scelto.
- Confrontare lo stesso esempio esportato in quattro parti e in due pentagrammi: l’analisi deve conservare identità delle voci e segnalazioni.
- Includere legature, pause, anacrusi, ritardi, metri composti, cambi di tonalità, incroci, quinte composte e movimenti contrari. Esempi leciti sono essenziali per misurare i falsi positivi.
- Verificare l’interazione con percorsi contenenti spazi e accenti, XML malformato, cartella non scrivibile, annullamento e collisione del nome di uscita.
- Confrontare il Markdown di alcuni esercizi annotati a mano, separando correttezza delle segnalazioni e problemi sfuggiti. Il corpus di sviluppo e quello di valutazione devono essere distinti.
- Un’analisi parziale deve elencare esattamente cosa non ha controllato. Un errore operativo non deve lasciare un report finale apparentemente completo.

Il primo risultato completo deve includere sia i controlli di condotta sia la valutazione contestuale degli accordi: un rilevatore delle sole parallele non soddisfa la richiesta. Le regole non ancora definite con precisione devono risultare non disponibili, senza fingere copertura totale.

## Decisioni ancora dipendenti dal programma d’esame

Prima di attribuire al profilo valore di riferimento per un esame specifico occorre precisare con esempi: dirette ammesse, successioni per moto contrario, false relazioni di tritono, raddoppi, ambito delle sincopi armoniche, eccezioni nelle progressioni e repertorio degli accordi richiesto. La CLI e l’architettura sono già definibili; l’equivalenza con il giudizio del docente richiede questa validazione musicale.
