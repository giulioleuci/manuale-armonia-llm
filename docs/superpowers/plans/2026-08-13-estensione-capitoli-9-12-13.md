# Estensione capitoli 9, 12, 13 con SINTESI.txt — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estendere i capitoli 9, 12 e 13 del manuale "Appunti sparsi di Armonia" con le informazioni di `SETTIME/SINTESI.txt`, orientate all'armonizzazione del basso dato.

**Architecture:** Integrazione in-place nei tre file LaTeX dei capitoli, riusando gli ambienti esistenti (`definizione`, `regola`, `esempio`, `errore`, `osservazione`), la macro `\musica`/`\partilate` per gli esempi e le tabelle di sintesi nel formato del capitolo 9.

**Tech Stack:** LuaLaTeX + lyluatex + LilyPond (v2.24.0+), `partilate` da `definizioni.ly`.

## Global Constraints

- Lingua del documento: **italiano**; nomi musicali italiani (sensibile, sottodominante, sopradominante, ecc.).
- Alterazioni nel testo: usare `\sharp` e `\flat` in math mode (`$\sharp$`); macro nome-nota esistenti (es. `\Soldiesis`, `\Dodiesis`); **mai** caratteri Unicode ♯/♭ né `#`/`b` nel testo.
- Nei blocchi LilyPond: linguaggio italiano (`dodies`, `sib`, `sold`, ecc.).
- Esempi a 4 voci: sempre `\partilate` (7 argomenti: global, soprano, alto, tenor, bass, analysis, figures).
- Ambienti disponibili: `definizione`, `esempio`, `regola`, `errore`, `fisica`, `matematica`, `osservazione` (definiti in `styles.tex`).
- Label esistenti da usare nei rinvii: `chap:teoria_dissonanza`, `chap:settima_dominante`, `chap:vii7_ii7`, `chap:sette_specie`, `chap:cadenze`, `chap:regola_ottava_completa`.
- Non modificare altri capitoli, `manuale.tex`, `styles.tex`, `definizioni.ly`.
- Correzioni musicali da `SINTESI.txt`: le collocazioni errate della 2ª specie (I, IV, V della minore melodica ascendente; VII della minore naturale/melodica discendente) sono **rimosse**; la 3ª specie sul VI della minore melodica ascendente è **corretta** e va in capitolo 12.
- Verifica dopo ogni task: `lualatex --shell-escape manuale.tex` dalla root; nessun nuovo errore nel log; commit in italiano (stile repo: "Aggiungi ...", "Correggi ...").

---

### Task 1: Capitolo 9 — nuova sezione finale "per il basso dato"

**Files:**
- Modify: `Capitoli/09_settima_dominante.tex` (append alla fine del file, dopo `\end{fisica}` di riga 234)

**Interfaces:**
- Produces: label `sec:v7_basso_dato`, `sec:v7_inganno`, `sec:v7_cadenze`, `reg:collocazione_v7`, `reg:v7_inganno`, `ex:v7_inganno`, `oss:eccezione_bach`. Usa `chap:cadenze` e `chap:teoria_dissonanza` (esistenti).

- [ ] **Step 1: Appendere la nuova sezione**

Aprire `Capitoli/09_settima_dominante.tex`, posizionarsi alla fine del file (dopo `\end{fisica}` dell'ultimo box) e aggiungere:

```latex

\section{Collocazione sulle scale e casi particolari per il basso dato}
\label{sec:v7_basso_dato}

\begin{regola}[Collocazione della V7]
	\label{reg:collocazione_v7}
	La settima di dominante si costruisce sul \textbf{V grado} sia del modo maggiore sia del modo minore (armonico e melodico ascendente). È un accordo \textbf{naturale ed indipendente}: \textbf{non richiede la preparazione} della dissonanza (Capitolo \ref{chap:teoria_dissonanza}), perché la sua risoluzione è talmente direzionale da giustificarne l'introduzione "di petto".
\end{regola}

\begin{osservazione}[La settima nel modo minore]
	Nel modo maggiore la settima scende di \textbf{semitono} sulla tonica (es. in Do maggiore: Fa $\searrow$ Mi); nel modo minore scende invece di \textbf{tono} (es. in La minore: Re $\searrow$ Do). Nell'armonizzazione del basso dato in tonalità minore, ogni qualvolta la V7 risolve, la terza della tonica di arrivo si raggiunge scendendo di un tono.
\end{osservazione}

\subsection{Risoluzione d'inganno (V7 $\rightarrow$ VI)}
\label{sec:v7_inganno}

Oltre alla risoluzione naturale sulla tonica, la V7 può risolvere sul \textbf{VI grado} (cadenza d'inganno, Capitolo \ref{chap:cadenze}). Le note obbligate del tritono continuano a muoversi come nella risoluzione naturale: la sensibile sale alla tonica, la settima scende alla terza del VI grado.

\begin{regola}[V7 $\rightarrow$ VI]
	\label{reg:v7_inganno}
	La risoluzione d'inganno della V7 sul VI grado è ammessa \textbf{purché la triade di destinazione sia allo stato completo}. La sensibile sale comunque alla tonica (terza del VI grado), la settima scende di grado sulla quinta del VI grado.
\end{regola}

\begin{esempio}[V7 completa $\rightarrow$ VI in Do Maggiore]
	\label{ex:v7_inganno}
	La sensibile (Si) sale alla tonica (Do), la settima (Fa) scende sulla quinta del VI grado (Mi).
	\musica{
		\partilate
		{ \key do \major \time 4/4 }
		{ re'2 mi'2 }
		{ si2 do'2 }
		{ fa2 mi2 }
		{ sol,2 la,2 }
		\lyricmode { "V7"2 "VI"2 }
		\figuremode { <7>2 s2 }
	}
\end{esempio}

\subsection{La V7 nelle cadenze}
\label{sec:v7_cadenze}

La V7 trova applicazione al posto della triade di dominante all'interno delle formule cadenzali (Capitolo \ref{chap:cadenze}):

\begin{itemize}
	\item \textbf{Cadenza composta consonante}: $I^6_4 - V^7$;
	\item \textbf{Cadenza composta dissonante}: $V^5_4 - V^7_3$;
	\item \textbf{Cadenza doppia}: $V - I^6_4 - V^5_4 - V^7_3$.
\end{itemize}

\begin{osservazione}[Eccezione di Bach]
	\label{oss:eccezione_bach}
	Se la sensibile si trova in una \textbf{voce interna} e si muove per \textbf{moto contrario} rispetto al basso, può eccezionalmente risolvere \textbf{saltando di terza discendente} sul I grado, per permettere alla voce superiore di raggiungere la tonica.
\end{osservazione}
```

- [ ] **Step 2: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: terminazione senza errori; nel `manuale.log` nessun nuovo `! ` (errori) riferiti al capitolo 9; nessun "Undefined control sequence".

- [ ] **Step 3: Commit**

```bash
git add Capitoli/09_settima_dominante.tex
git commit -m "Aggiungi collocazione, inganno, cadenze ed eccezione di Bach alla settima di dominante"
```

---

### Task 2: Capitolo 12 — settima di sensibile maggiore (VII7) completa

**Files:**
- Modify: `Capitoli/12_settima_sensibile.tex` (inserire dopo `\end{esempio}` di `ex:vii65_regola_maggiore` — riga 69 — e prima di `\section{La settima sul secondo grado nel modo minore}`)

**Interfaces:**
- Produces: `reg:comportamento_vii7`, `oss:disposizione_settima`, `subsec:risoluzioni_anticipate`, `reg:risoluzioni_anticipate`, `ex:risoluzione_anticipata`. Consumes: `chap:teoria_dissonanza` (esistente).

- [ ] **Step 1: Inserire il contenuto VII7**

Posizionarsi dopo `\end{esempio}` (fine di `ex:vii65_regola_maggiore`, subito prima di `\section{La settima sul secondo grado nel modo minore}`) e inserire:

```latex

\begin{regola}[Comportamento delle voci della VII7]
	\label{reg:comportamento_vii7}
	Alla risoluzione della settima di sensibile valgono le seguenti norme:
	\begin{itemize}
		\item La \textbf{fondamentale} (la sensibile) \textbf{sale di grado} alla tonica e \textbf{non si raddoppia}.
		\item La \textbf{quinta} e la \textbf{settima} sono note a risoluzione obbligata: \textbf{scendono di grado} e \textbf{non si raddoppiano}.
		\item La \textbf{terza} è parte libera. \textbf{Attenzione}: quando la terza si trova nella parte grave, al di sotto della settima, deve obbligatoriamente \textbf{salire di grado}, per evitare due quinte parallele per moto retto.
	\end{itemize}
\end{regola}

\begin{osservazione}[Disposizione della settima]
	\label{oss:disposizione_settima}
	La settima dell'accordo deve trovarsi a distanza di \textbf{settima} dalla sensibile, mai di seconda o di nona. La distanza di nona è tuttavia tollerata al terzo rivolto, purché la settima sia preparata da un accordo consonante.
\end{osservazione}

\begin{center}
\begin{tabular}{|l|l|l|l|l|}
\hline
Stato & Cifratura & Grado al basso & Risolve su & Basso obbligato \\
\hline
Fond. & 7 & VII & I & Sì (sale) \\
I rv. & 6/5 & II & I6 & Sì (sale) \\
II rv. & 4/3 & IV & I6/4, poi I6 & Sì (scende) \\
III rv. & 4/2 & VI & V (I6/4) & Sì (scende) \\
\hline
\end{tabular}
\end{center}

\subsection{Risoluzioni anticipate della VII7}
\label{subsec:risoluzioni_anticipate}

Se si hanno a disposizione due movimenti, è sempre possibile far risolvere \textbf{anticipatamente} la settima dell'accordo (sia allo stato fondamentale sia nei rivolti): la settima scende di grado e il VII7 si trasforma direttamente in un accordo di settima di dominante (V7) o in un suo rivolto, prima di cadere sulla tonica.

\begin{regola}[Risoluzioni anticipate]
	\label{reg:risoluzioni_anticipate}
	\begin{itemize}
		\item $VII^7 \rightarrow V^6_5 \rightarrow I$
		\item $VII^6_5 \rightarrow V^4_3 \rightarrow I$ (oppure $I^6$)
		\item $VII^4_3 \rightarrow V^4_2 \rightarrow I^6$
		\item $VII^4_2 \rightarrow V^7 \rightarrow I$
	\end{itemize}
\end{regola}

\begin{esempio}[Risoluzione anticipata VII7 $\rightarrow$ V6/5 $\rightarrow$ I in Do Maggiore]
	\label{ex:risoluzione_anticipata}
	La settima (La) scende anticipatamente sulla settima di dominante (Sol): il VII7 diventa un V6/5 che risolve regolarmente sulla tonica.
	\musica{
		\partilate
		{ \key do \major \time 4/4 }
		{ la'1 | sol'1 | sol'1 }
		{ fa'1 | fa'1 | mi'1 }
		{ re'1 | re'1 | do'1 }
		{ si,1 | si,1 | do1 }
		\lyricmode { "VIIø7"1 "V6/5"1 "I"1 }
		\figuremode { <7>1 <6 5>1 s1 }
	}
\end{esempio}
```

- [ ] **Step 2: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log; gli esempi LilyPond generano senza warning gravi.

- [ ] **Step 3: Commit**

```bash
git add Capitoli/12_settima_sensibile.tex
git commit -m "Aggiungi comportamento voci, rivolti e risoluzioni anticipate della VII7"
```

---

### Task 3: Capitolo 12 — settima sul II del minore (IIø7) completa + tabella comparativa

**Files:**
- Modify: `Capitoli/12_settima_sensibile.tex`

**Interfaces:**
- Produces: `reg:collocazione_ii7_minore`, `reg:quinta_diminuita`, `subsec:rivolti_ii7_minore`, `oss:omissione_quinta`. Consumes: `chap:sette_specie` (esistente). Estende la tabella `sec:sintesi_vii_ii`.

- [ ] **Step 1: Correggere la denominazione di specie**

In `def:vii7` (riga 15) la frase "Questo accordo è anche chiamato \textbf{semidiminuito} o \textbf{settima di seconda specie}" è errata: il semidiminuito è la **terza** specie (cfr. `sec:classificazione_specie`). Sostituire "seconda specie" con "terza specie".

- [ ] **Step 2: Inserire il contenuto IIø7**

Posizionarsi dopo `\end{esempio}` di `ex:progressione_ii7_minore` (riga 108), prima di `\subsection{II6/5 nella Regola dell'Ottava (modo minore)}`, e inserire:

```latex

\subsection{Collocazione e rivolti del IIø7 nel modo minore}
\label{subsec:rivolti_ii7_minore}

\begin{regola}[Collocazione del IIø7]
	\label{reg:collocazione_ii7_minore}
	L'accordo semidiminuito si trova sul \textbf{II grado della scala minore armonica}; è presente anche sul VI grado della scala minore melodica ascendente come accordo derivato.
\end{regola}

Oltre alla settima, anche la \textbf{quinta diminuita} è un intervallo dissonante: entrambe devono risolvere per grado congiunto discendente in tutti i collegamenti.

\begin{regola}[Quinta diminuita a risoluzione obbligata]
	\label{reg:quinta_diminuita}
	Nella settima di terza specie, sia la settima sia la \textbf{quinta diminuita} devono risolvere \textbf{per grado congiunto discendente} in tutti i collegamenti. La fondamentale è l'unica nota che sale (alla dominante).
\end{regola}

I rivolti del IIø7 ($II^6_5$, $II^4_3$, $II^4_2$) seguono esattamente le regole applicative, i gradi al basso e i movimenti prescritti per la seconda specie (Capitolo \ref{chap:sette_specie}), tenendo conto delle alterazioni proprie del modo minore e dell'obbligo di far scendere la quinta diminuita.

\begin{center}
\begin{tabular}{|l|l|l|l|l|}
\hline
Stato & Cifratura & Grado al basso & Risolve su & Basso obbligato \\
\hline
Fond. & 7 & II & V (o V7) & No \\
I rv. & 6/5 & IV & V & Sì (sale) \\
II rv. & 4/3 & VI & V & Sì (scende) \\
III rv. & 4/2 & I (settima) & V6 o V6/5 & Sì (scende) \\
\hline
\end{tabular}
\end{center}

\begin{osservazione}[Omissione della quinta nel collegamento I $-$ II7 $\rightarrow$ V]
	\label{oss:omissione_quinta}
	A differenza della seconda specie, nel collegamento $I - II^7 \rightarrow V$ la quinta diminuita è un elemento caratteristico dell'accordo: alcuni teorici ne \textbf{vietano l'omissione}, mentre altri accettano l'accordo senza quinta e con raddoppio della terza per evitare quinte parallele.
\end{osservazione}
```

- [ ] **Step 3: Aggiornare la tabella comparativa**

Nella tabella `sec:sintesi_vii_ii` (righe 138-150):
1. Cambiare la riga "Preparazione settima" da `Preferibile & Obbligatoria` a `Non necessaria & Obbligatoria`.
2. Aggiungere dopo la riga "Preparazione settima" le due nuove righe:

```latex
		Quinta diminuita a risoluzione obbligata & Sì (scende) & Sì (scende) \\
		Rivolto principale & VII6/5 $\rightarrow$ I6 & II6/5 $\rightarrow$ V \\
```

- [ ] **Step 4: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log; tabella correttamente composta.

- [ ] **Step 5: Commit**

```bash
git add Capitoli/12_settima_sensibile.tex
git commit -m "Completa la settima sul II del minore e aggiorna la tabella comparativa"
```

---

### Task 4: Capitolo 13 — seconda specie completa

**Files:**
- Modify: `Capitoli/13_specie_settima.tex`

**Interfaces:**
- Produces: `subsec:ii7_collocazione`, `reg:ii7_gradi`, `subsec:ii7_stato_fondamentale`, `reg:ii7_stato_fondamentale`, `subsec:ii7_rivolti`, `oss:ii7_progressioni`. Consumes: `chap:teoria_dissonanza` (esistente). Estende `reg:ii7_raddoppio`.

- [ ] **Step 1: Estendere la regola sul raddoppio**

Nella `reg:ii7_raddoppio` (righe 43-46) aggiungere in coda, dopo "quinte parallele tra la fondamentale e la quinta del II grado nel movimento verso l'accordo di dominante.":

```latex

	In alternativa (o in aggiunta) si può \textbf{omettere la quinta} del II7, raddoppiando una delle altre voci (es. la fondamentale) e lasciando fondamentalmente la terza raddoppiata, come nell'esempio seguente.
```

- [ ] **Step 2: Inserire collocazione, stato fondamentale, rivolti e osservazioni**

Posizionarsi dopo `\end{esempio}` dell'esempio II7 (riga 60), prima di `\section{Quarta Specie}`, e inserire:

```latex

\subsection{Collocazione sulle scale}
\label{subsec:ii7_collocazione}

\begin{regola}[Gradi della seconda specie]
	\label{reg:ii7_gradi}
	L'accordo di settima minore (seconda specie) si trova:
	\begin{itemize}
		\item Sul \textbf{II}, \textbf{III} e \textbf{VI} grado della scala maggiore;
		\item Sul \textbf{IV} grado della scala minore armonica.
	\end{itemize}
	L'accordo di gran lunga più importante è quello sul \textbf{II grado del modo maggiore}, con funzione di sottodominante.
\end{regola}

\subsection{Stato fondamentale}
\label{subsec:ii7_stato_fondamentale}

\begin{regola}[II7 allo stato fondamentale]
	\label{reg:ii7_stato_fondamentale}
	Al II grado al basso, la settima va \textbf{preparata} nell'accordo precedente (presente nella stessa voce, con durata pari o superiore) e \textbf{tenuta}, poi risolve \textbf{scendendo per grado congiunto}. Le altre note, compresa la fondamentale, sono \textbf{parti libere} e si possono raddoppiare. La quinta si può omettere raddoppiando una delle altre voci (mai la settima).
\end{regola}

Risolve naturalmente sul \textbf{V grado}, armonizzato con la triade semplice, con la cadenza composta consonante o dissonante, oppure con la $V^7$.

\subsection{I tre rivolti}
\label{subsec:ii7_rivolti}

\begin{center}
\begin{tabular}{|l|l|l|l|l|}
\hline
Stato & Cifratura & Grado al basso & Risolve su & Basso obbligato \\
\hline
Fond. & 7 & II & V (o V7) & No \\
I rv. & 6/5 & IV & V & Sì (sale) \\
II rv. & 4/3 & VI & V & Sì (scende) \\
III rv. & 4/2 & I (settima) & V6 o V6/5 & Sì (scende) \\
\hline
\end{tabular}
\end{center}

\begin{itemize}
	\item \textbf{II6/5} (IV grado al basso): il basso risolve per grado congiunto ascendente sulla dominante. È impiegato diffusamente nella formula cadenzale $I$ (oppure $I^6$ / $VI$) $- II^6_5 - I^6_4 - V$. Può risolvere anche sulla triade o settima di sensibile allo stato di rivolto.
	\item \textbf{II4/3} (VI grado al basso): il basso risolve per moto discendente sul V grado.
	\item \textbf{II4/2} (I grado al basso, la settima): la settima al basso deve essere preparata e risolve per moto discendente sul VII grado, armonizzato con il primo rivolto della dominante ($V^6$ o $V^6_5$).
\end{itemize}

\begin{osservazione}[Progressioni e IV grado del modo minore]
	\label{oss:ii7_progressioni}
	\begin{itemize}
		\item Il VI7 e gli altri gradi di seconda specie si usano scolasticamente nelle \textbf{progressioni discendenti} (es. $III^7 - VI^7 - II^7$).
		\item La seconda specie sul IV grado del modo minore è un accordo \textbf{derivato} (da una nona di terza specie sul II grado senza fondamentale) e si comporta esattamente come la quarta specie sul IV grado del modo maggiore.
	\end{itemize}
\end{osservazione}
```

- [ ] **Step 3: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log.

- [ ] **Step 4: Commit**

```bash
git add Capitoli/13_specie_settima.tex
git commit -m "Completa la seconda specie di settima con gradi, stati e rivolti"
```

---

### Task 5: Capitolo 13 — quarta specie completa

**Files:**
- Modify: `Capitoli/13_specie_settima.tex`

**Interfaces:**
- Produces: `subsec:iv7_collocazione`, `reg:iv7_gradi`, `subsec:iv7_rivolti`.

- [ ] **Step 1: Inserire collocazione e rivolti**

Posizionarsi dopo `\end{esempio}` dell'esempio `I7 della quarta specie` (riga 81), prima di `\section{Quinta Specie}`, e inserire:

```latex

\subsection{Collocazione sulle scale}
\label{subsec:iv7_collocazione}

\begin{regola}[Gradi della quarta specie]
	\label{reg:iv7_gradi}
	L'accordo di settima maggiore (quarta specie) si trova:
	\begin{itemize}
		\item Sul \textbf{I} e \textbf{IV} grado della scala maggiore;
		\item Sul \textbf{VI} grado della scala minore armonica;
		\item Sul \textbf{III} e \textbf{VI} grado della scala minore melodica discendente.
	\end{itemize}
	L'analisi del corso si concentra sul \textbf{I grado del modo maggiore}.
\end{regola}

\subsection{Rivolti}
\label{subsec:iv7_rivolti}

Al I grado, l'accordo di quarta specie ha funzione di \textbf{sottodominante} (o di settima sul IV grado). La settima va preparata nella voce; le altre note sono parti libere e la quinta si può omettere a favore del raddoppio della fondamentale.

\begin{center}
\begin{tabular}{|l|l|l|l|l|}
\hline
Stato & Cifratura & Grado al basso & Risolve su & Basso obbligato \\
\hline
Fond. & 7 & I & IV (o IV7) & No \\
I rv. & 6/5 & III & IV & Sì (sale) \\
II rv. & 4/3 & V & IV & Sì (scende) \\
III rv. & 4/2 & VII (settima) & IV6 & Sì (scende) \\
\hline
\end{tabular}
\end{center}
```

- [ ] **Step 2: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log.

- [ ] **Step 3: Commit**

```bash
git add Capitoli/13_specie_settima.tex
git commit -m "Completa la quarta specie di settima con gradi e rivolti"
```

---

### Task 6: Capitolo 13 — quinta specie completa

**Files:**
- Modify: `Capitoli/13_specie_settima.tex`

**Interfaces:**
- Produces: `subsec:vii_dim7_natura`, `reg:vii_dim7_gradi`, `ex:vii_dim7`, `oss:dim7_terzo_rivolto`. Consumes: `chap:vii7_ii7` (esistente).

- [ ] **Step 1: Correggere l'intro del capitolo sulla preparazione della prima specie**

Nella `\section{Prima e Terza specie: richiami}` (righe 30-33) la voce della Prima Specie afferma "È l'unica specie che non richiede preparazione obbligatoria della settima." — affermazione contraddetta dal contenuto nuovo (anche terza e quinta specie non la richiedono). Sostituire quella frase con:

```latex
    Non richiede la preparazione obbligatoria della settima (come la terza e la quinta specie).
```

- [ ] **Step 2: Sostituire il contenuto della sezione Quinta Specie**

Nella `\section{Quinta Specie}`, sostituire tutto il testo compreso tra `\subsection{Uso sul VII grado del modo minore}` e la fine della sezione (righe 88-91) con:

```latex
\subsection{Natura e collocazione}
\label{subsec:vii_dim7_natura}

\begin{regola}[Grado della quinta specie]
	\label{reg:vii_dim7_gradi}
	La settima diminuita (quinta specie) si trova sul \textbf{VII grado della scala minore armonica e melodica}, dove è chiamata \textbf{settima di sensibile del modo minore}. È l'unico accordo di settima a contenere l'intervallo di \textbf{settima diminuita}, perciò è chiaramente distinguibile all'ascolto.
\end{regola}

È un accordo \textbf{principale e derivato}: nasce dall'accordo di nona di dominante minore senza la fondamentale, e per questo \textbf{non necessita della preparazione} della settima.

\subsection{Uso sul VII grado del modo minore}
Si studia principalmente sul \textbf{VII grado del modo minore} (sulla sensibile), dove svolge funzione di dominante estrema. Alla risoluzione sul I grado valgono le norme della settima di sensibile di terza specie (Capitolo \ref{chap:vii7_ii7}): la sensibile sale alla tonica, la quinta e la settima scendono per grado.

\begin{esempio}[VII°7 $\rightarrow$ I in La Minore]
	\label{ex:vii_dim7}
	La sensibile (Sol diesis) sale alla tonica, la quinta diminuita (Re) e la settima (Fa) scendono per grado.
	\musica{
		\partilate
		{ \key la \minor \time 4/4 }
		{ fa'2 mi'2 }
		{ re'2 do'2 }
		{ si2 do'2 }
		{ sold,2 la,2 }
		\lyricmode { "VII°7"2 "I"2 }
		\figuremode { <7>2 s2 }
	}
\end{esempio}

I rivolti ricalcano quelli della settima di sensibile (terza specie sul VII), con una \textbf{eccezione unica ed essenziale per il terzo rivolto}.

\begin{osservazione}[Terzo rivolto senza preparazione]
	\label{oss:dim7_terzo_rivolto}
	A differenza della terza specie, nella quinta specie il \textbf{terzo rivolto} può essere disposto \textbf{senza alcuna necessità di preparare la settima al basso}. Motivo teorico: l'urto di \textbf{seconda aumentata} che si crea tra la fondamentale (sensibile) e la settima è \textbf{enarmonico} all'intervallo consonante di terza minore, e all'udito risulta privo della durezza tipica delle seconde.
\end{osservazione}

Oltre che sul VII grado, questa specie trova un uso importante come \textbf{accordo alterato sul IV grado} di entrambi i modi (maggiore e minore), agendo come una sorta di "dominante della dominante" o per scopi coloristici nelle cadenze.
```

- [ ] **Step 3: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log; l'esempio `VII°7` generato senza warning.

- [ ] **Step 4: Commit**

```bash
git add Capitoli/13_specie_settima.tex
git commit -m "Completa la quinta specie di settima con gradi, esempio e rivolti"
```

---

### Task 7: Capitolo 13 — sesta e settima specie

**Files:**
- Modify: `Capitoli/13_specie_settima.tex`

**Interfaces:**
- Produces: `sec:sesta_specie_dettaglio`, `reg:sesta_specie`, `sec:settima_specie_dettaglio`, `reg:settima_specie`.

- [ ] **Step 1: Sostituire la sezione congiunta**

Sostituire l'intera `\section{Sesta e Settima Specie}` (righe 93-103, incluse le liste e la chiusa "Nonostante la loro esistenza teorica, non verranno approfondite ulteriormente in quanto non richieste nelle prove d'esame.") con:

```latex
\section{Sesta specie (minore con settima maggiore)}
\label{sec:sesta_specie_dettaglio}

La sesta specie è formata da una \textbf{triade minore} e una \textbf{settima maggiore}. È un accordo \textbf{secondario e artificiale}, di ambito moderno: non viene usato nell'armonia diatonica tradizionale e classica, dove era considerato un accordo alterato.

\begin{regola}[Grado e risoluzione della sesta specie]
	\label{reg:sesta_specie}
	La sesta specie si trova sul \textbf{I grado della scala minore armonica e melodica}, con sigle $m^{maj7}$ e $m\Delta$ (es. La-Do-Mi-\Soldiesis). Al basso ha la fondamentale (I grado) e risolve \textbf{generalmente sul IV grado}.
\end{regola}

I rivolti non sono dettagliati in questa sede: si applicano le \textbf{norme generali sulle dissonanze secondarie}, cioè la settima va preparata e risolve per grado discendente.

\section{Settima specie (aumentata con settima maggiore)}
\label{sec:settima_specie_dettaglio}

La settima specie è formata da una \textbf{triade aumentata} e una \textbf{settima maggiore}. È anch'essa un accordo \textbf{secondario e artificiale} di ambito moderno/jazzistico, considerato alterato nella prassi classica.

\begin{regola}[Grado e risoluzione della settima specie]
	\label{reg:settima_specie}
	La settima specie si trova sul \textbf{III grado della scala minore armonica e melodica}, con sigle $maj^7(\sharp5)$ e $+\Delta$. Al basso ha la fondamentale (III grado) e risolve \textbf{generalmente sul VI grado}.
\end{regola}

I rivolti non sono dettagliati in questa sede: si applicano le norme generali sulle dissonanze secondarie, con la \textbf{quinta aumentata} che risolve salendo di grado e la settima che scende per grado congiunto. Pur appartenendo al catalogo completo delle quadriadi, queste due specie non trovano applicazione nell'armonia diatonica tradizionale del basso dato.
```

- [ ] **Step 2: Compilare per verificare**

Run: `lualatex --shell-escape manuale.tex`
Expected: nessun errore nuovo nel log.

- [ ] **Step 3: Commit**

```bash
git add Capitoli/13_specie_settima.tex
git commit -m "Dettaglia la sesta e settima specie di settima"
```

---

### Task 8: Verifica finale completa

**Files:**
- Nessuna modifica (solo verifica).

- [ ] **Step 1: Compilazione pulita da zero**

Run: `rm -rf tmp-ly manuale.aux manuale.log manuale.out manuale.toc manuale.lof manuale.fisica manuale.matematica && lualatex --shell-escape manuale.tex`

Run: `lualatex --shell-escape manuale.tex` (seconda passata per riferimenti incrociati e TOC)

Expected: entrambe le passate terminano senza errori; nel `manuale.log` nessun `! ` (errore); controllo dei rinvii: i `\ref{...}` usati nei nuovi contenuti (chap:cadenze, chap:teoria_dissonanza, chap:sette_specie, chap:vii7_ii7) devono risolversi (nessun "??").

- [ ] **Step 2: Controllo contenuti nuovi nel PDF**

Aprire `manuale.pdf` e verificare:
- Cap. 9: sezione "Collocazione sulle scale e casi particolari per il basso dato" con esempio V7→VI;
- Cap. 12: tabelle dei rivolti, "Risoluzioni anticipate della VII7", "Collocazione e rivolti del IIø7", tabella comparativa aggiornata;
- Cap. 13: sezioni completate per 2ª, 4ª, 5ª, 6ª, 7ª specie con tabelle ed esempi.

- [ ] **Step 3: Commit finale**

```bash
git add -A
git commit -m "Verifica finale compilazione capitoli estesi" || echo "Nessuna modifica da committare"
```

---

## Self-Review Notes

- Task 1 copre: collocazione V7, nota tono/semitono minore, inganno, cadenze, eccezione Bach (spec §Capitolo 9).
- Task 2 copre: comportamento voci VII7, disposizione, tabella rivolti, risoluzioni anticipate (spec §Capitolo 12/VII7).
- Task 3 copre: collocazione IIø7, quinta diminuita, rivolti = 2ª specie, polemica omissione, tabella comparativa, correzione "seconda specie" (spec §Capitolo 12/II7).
- Task 4 copre: collocazione 2ª specie (corretta), stato fondamentale, rivolti, quinte consecutive, progressioni, IV del minore (spec §Capitolo 13/2ª).
- Task 5 copre: collocazione 4ª specie, stato fondamentale, rivolti (spec §Capitolo 13/4ª).
- Task 6 copre: collocazione 5ª specie, natura, esempio, eccezione 3° rivolto, mantenuto accordo alterato sul IV (spec §Capitolo 13/5ª).
- Task 7 copre: 6ª e 7ª specie con stato fondamentale e norme generali sui rivolti, chiusa riformulata (spec §Capitolo 13/6ª-7ª).
- Task 8: verifica compilazione e commit finale.
