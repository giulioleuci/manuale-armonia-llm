# Design: Estensione capitoli 9, 12 e 13 con SINTESI.txt

Data: 2026-08-13
Stato: approvato

## Obiettivo

Estendere i capitoli 9, 12 e 13 del manuale ("Appunti sparsi di Armonia") con le informazioni contenute in `SETTIME/SINTESI.txt`, allo scopo di ottenere un manuale utile per l'**armonizzazione del basso dato**. Per ogni specie di settima descritta nel file devono essere presenti: stato fondamentale, tutti i rivolti, i gradi di scala su cui si trova e le risoluzioni.

## Decisioni concordate

1. **Correzione musicale**: le collocazioni sulle scale palesemente errate in SINTESI.txt vengono corrette (es. 2ª specie sul I, IV, V della minore melodica ascendente e sul VII della minore naturale non corrispondono ad accordi di settima minore). Il resto viene trascritto fedelmente.
2. **Esempi selettivi**: tabelle di sintesi per ogni specie + esempi `partilate` solo per i casi chiave.
3. **6ª e 7ª specie**: dettaglio dello stato fondamentale come da file, con note sui rivolti basate sulle norme generali delle dissonanze (il file non le dettaglia).

## Approccio

Integrazione in-place nei tre capitoli esistenti, riusando le convenzioni del manuale (ambienti `definizione`, `regola`, `errore`, `osservazione`; esempi `partilate`; tabelle di sintesi come quella del cap. 9; `\sharp`/`\flat` in math mode; riferimenti `\label`/`\ref`). Nessuna modifica a `manuale.tex` né ad altri capitoli.

## Contenuti per capitolo

### Capitolo 9 — `09_settima_dominante.tex`

Struttura attuale invariata. Nuova sezione finale `\section{Collocazione sulle scale e casi particolari per il basso dato}`:

- **Collocazione sulle scale**: V grado del modo maggiore e del modo minore (armonica e melodica ascendente). Nota: nel modo minore la settima scende di un tono, nel maggiore di un semitono. [box regola/osservazione]
- **Risoluzione d'inganno** (V7 → VI): regola con vincolo della triade di destinazione completa + esempio `partilate`. [box regola + esempio]
- **La V7 nelle cadenze**: cadenza composta consonante ($I_4^6 - V^7$), dissonante ($V_5^4 - V_3^7$), cadenza doppia ($V - I_4^6 - V_5^4 - V_3^7$), con rinvio al capitolo sulle cadenze. [itemize]
- **Eccezione di Bach**: sensibile in voce interna che, per moto contrario col basso, salta di terza discendente sul I grado. [box osservazione]

### Capitolo 12 — `12_settima_sensibile.tex`

**VII7 nel modo maggiore** — espansione di `\subsection{I rivolti della VII7}`:
- Comportamento voci: fondamentale (sensibile) sale e non si raddoppia; quinta e settima a risoluzione obbligata discendente, non raddoppiabili; terza parte libera ma che sale di grado se nel grave (PS) sotto la settima; disposizione: settima a distanza di 7ª dalla sensibile, mai di 2ª o 9ª.
- Tabella di sintesi dei rivolti: VII6/5 → I6; VII4/3 → I6/4 poi I6; VII4/2 → V (I6/4).
- Nota speciale: distanza di 9ª tollerata al 3° rivolto purché la settima sia preparata da un accordo consonante.
- **Risoluzioni anticipate** (nuova sezione): VII7 → V6/5 → I; VII6/5 → V4/3 → I (o I6); VII4/3 → V4/2 → I6; VII4/2 → V7 → I. Con esempio `partilate`.

**II7 nel modo minore** — aggiunte a `\section{La settima sul secondo grado nel modo minore}`:
- Collocazione: II grado del modo minore armonico (presente anche sul VI grado della minore melodica ascendente come accordo derivato).
- La quinta diminuita (oltre alla settima) risolve obbligatoriamente per grado congiunto discendente. [box regola]
- Rivolti regolati come la 2ª specie del cap. 13, con le alterazioni del minore. [tabella sintesi + rinvio]
- Polemica sull'omissione della quinta nel collegamento I – II7 → V. [box osservazione]

**Tabella comparativa finale** `VII7 vs II7`: estesa con righe aggiuntive (quinta obbligata a scendere, disposizione della settima, grado al basso nei rivolti).

### Capitolo 13 — `13_specie_settima.tex`

**Seconda specie** — sezione espansa:
- Collocazione corretta: II, III, VI del modo maggiore; IV del modo minore armonico. Le collocazioni della minore melodica ascendente (I, IV, V) e della minore naturale/melodica discendente (VII) indicate dal file sono errate (non producono accordi di settima minore) e vengono corrette/rimosse. Focus sul II del maggiore (l'accordo più importante).
- Stato fondamentale: settima preparata e tenuta, risolve scendendo; le altre note parti libere raddoppiabili; quinta omettibile.
- Rivolti con tabella di sintesi: II6/5 (basso IV → V, usato nella formula I – II6/5 – I6/4 – V); II4/3 (basso VI → V discendente); II4/2 (basso I → VII, risolve su V6 o V6/5).
- Evitamento delle quinte consecutive: nel collegamento I – II7 → V si armonizza omettendo la quinta (II7 con raddoppio). [box regola/errore; rinvio alla regola esistente sul raddoppio della terza]
- Progressioni discendenti III7 – VI7 – II7. IV del minore come accordo derivato che si comporta come la 4ª specie sul IV maggiore. [box osservazione]

**Quarta specie** — sezione espansa:
- Collocazione: I e IV del modo maggiore; VI del minore armonico; III e VI della minore melodica discendente. Focus sul I del maggiore.
- Stato fondamentale: settima preparata, risolve scendendo; funzione di sottodominante; quinta omettibile; risoluzione sul IV (triade o accordo di settima).
- Rivolti con tabella di sintesi: I6/5 (basso III → IV ascendente); I4/3 (basso V → IV discendente); I4/2 (basso VII → VI, armonizzato con IV6).
- Esempio `partilate` I7 → IV.

**Quinta specie** — sezione espansa:
- Collocazione: VII grado del modo minore armonico e melodico.
- Natura: accordo principale e derivato (nona di dominante minore senza fondamentale); non richiede preparazione; unico accordo con settima diminuita; sigle $\dim7$, $\circ7$.
- Stato fondamentale: regole della 3ª specie (sensibile sale, quinta e settima scendono); risoluzione sul I.
- Rivolti che ricalcano la 3ª specie; **eccezione unica al 3° rivolto**: nessuna preparazione richiesta (la 2ª aumentata tra sensibile e settima è enarmonica a una 3ª minore consonante).
- Si mantiene l'uso come accordo alterato sul IV grado già presente nel testo.
- Esempio `partilate` VIIº7 → I.

**Sesta e settima specie** — sostituzione della sezione congiunta con due sezioni distinte:
- **Sesta specie** (minore con settima maggiore): collocazione sul I grado del minore armonico e melodico; risolve generalmente sul IV; sigle $m^{maj7}$, $m\Delta$. Rivolti: norme generali (settima discendente), non dettagliati dal file.
- **Settima specie** (aumentata con settima maggiore): collocazione sul III grado del minore armonico e melodico; risolve sul VI; sigle $maj^7(\sharp 5)$, $+\Delta$. Rivolti: norme generali (settima discendente, quinta aumentata che sale).
- Rimossa la chiusa "non approfondite in quanto non richieste nelle prove d'esame".

## Verifica

Compilazione con `lualatex --shell-escape manuale.tex` e controllo assenza di errori.

## Fuori scope

- Modifica di altri capitoli (14–20).
- Modifica di `manuale.tex`, `styles.tex`, `definizioni.ly`.
- Inclusione di `SINTESI.txt` nel documento.
