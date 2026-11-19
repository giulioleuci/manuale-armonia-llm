"""Report Markdown UTF-8 e pubblicazione atomica senza sovrascrittura."""

from collections import Counter
from datetime import datetime, timedelta
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import html
import os
import tempfile

from . import __version__
from .analisi import CERTA
from .lettura import NOMI


def _testo(value):
    value = html.escape(str(value), quote=False).replace('\\', '\\\\')
    for char in '|`*[]_#':
        value = value.replace(char, '\\' + char)
    return value.replace('\r', ' ').replace('\n', ' ')


def markdown(result, data=None):
    timestamp = data or datetime.now().astimezone()
    analysis = result.analisi
    score = analysis.partitura
    profile = result.profilo
    counts = result.conteggi
    try:
        m21_version = version('music21')
    except PackageNotFoundError:
        m21_version = 'non installato nell’ambiente di generazione'
    out = [
        '# Analisi di armonia complementare', '',
        '## 1. Dati dell’analisi', '',
        f'- File: {_testo(score.file)}',
        f'- Data locale: {timestamp.isoformat(timespec="microseconds")}',
        f'- Versione applicazione: {__version__}; music21: {m21_version}',
        f'- Profilo: {profile["nome"]} — versione {profile["versione"]}',
        f'- {_testo(profile["descrizione"])}',
        f'- Tonalità proposte: {_testo("; ".join(analysis.tonalita))}',
        f'- Metri: {_testo(", ".join(dict.fromkeys(m.metro.ratioString for m in score.misure)))}; misure: {len(score.misure)}',
        '', '### Mappatura SATB', '',
    ]
    out.extend(f'- {NOMI[v]}: {_testo(label)}' for v,label in score.mappatura.items())
    out += ['', '### Convenzioni applicate', '']
    out.extend('- ' + _testo(c) for c in profile['convenzioni'])
    out += ['', '## 2. Sintesi', '',
            '**Analisi parziale.** Consultare la copertura: alcune verifiche non sono disponibili o valutabili.' if result.parziale else '**Analisi completa rispetto alle regole disponibili del profilo.**', '',
            f'Errori confermati: **{counts["errori"]}** | Avvertimenti certi: **{counts["avvertimenti"]}** | Casi condizionati o da verificare: **{counts["verificare"]}**.', '',
            'Gravità e affidabilità sono campi separati. I casi condizionati non sono conteggiati come errori confermati. Nessun voto numerico.', '']
    if not result.segnalazioni:
        out += ['Nessuna violazione rilevata dalle regole applicate.', '']
    else:
        out += ['| Famiglia | Gravità | Affidabilità | Numero |', '|---|---|---|---:|']
        counter = Counter((f.regola.split('-')[0], f.gravita, f.affidabilita) for f in result.segnalazioni)
        out.extend(f'| {family} | {severity} | {_testo(confidence)} | {count} |'
                   for (family,severity,confidence), count in sorted(counter.items()))
        out += ['', 'Priorità: rivedere prima gli errori certi di condotta, poi i casi dipendenti dall’interpretazione armonica.', '']
    out += ['## 3. Analisi armonica', '',
            '| Posizione / fine | Basso | Note strutturali | Figurazioni | Tonalità locale | Grado / rivolto | Funzione | Esito | Affidabilità |',
            '|---|---|---|---|---|---|---|---|---|']
    for s in analysis.segmenti:
        bass = s.eventi['B']
        pitches = ', '.join(f'{v}: {p.nameWithOctave}' for v,p in s.strutturali.items())
        ornaments = '; '.join(f'{v}: {name}' for v,name in s.figurazioni.items()) or 'nessuna riconosciuta'
        cells = (analysis.posizione(s.inizio) + ' → ' + analysis.posizione(s.fine),
                 bass.pitch.nameWithOctave if bass and bass.pitch else 'pausa', pitches, ornaments,
                 s.tonalita.name, s.grado, s.funzione, s.esito, s.affidabilita)
        out.append('| ' + ' | '.join(_testo(c) for c in cells) + ' |')
    out += ['', '## 4. Segnalazioni', '']
    if not result.segnalazioni:
        out += ['Nessuna segnalazione prodotta.', '']
    for i,f in enumerate(result.segnalazioni, 1):
        out.append(f'- [E{i:03d} — {_testo(profile["regole"][f.regola]["titolo"])}](#e{i:03d}): {_testo(analysis.posizione(f.inizio))}')
    for i,f in enumerate(result.segnalazioni, 1):
        rule = profile['regole'][f.regola]
        out += ['', f'<a id="e{i:03d}"></a>',
                f'### E{i:03d} — {_testo(rule["titolo"])} — {f.gravita}', '',
                f'- **Posizione:** {_testo(analysis.posizione(f.inizio))} → {_testo(analysis.posizione(f.fine))}.',
                f'- **Voci:** {", ".join(NOMI[v] for v in f.voci)}.',
                f'- **Note:** {_testo(f.note)}.',
                f'- **Evidenza:** {_testo(f.evidenza)}',
                f'- **Regola:** {f.regola}. {_testo(rule["definizione"])}',
                f'- **Eccezioni valutate / cautele:** {_testo(rule["eccezioni"])}',
                f'- **Interpretazione richiesta:** {_testo(f.interpretazione)}.',
                f'- **Affidabilità:** {_testo(f.affidabilita)}.',
                f'- **Verifica manuale:** {"necessaria" if f.affidabilita != CERTA else "non necessaria"}.',
                f'- **Indicazione didattica:** {_testo(f.indicazione)}',
                f'- **Fonte:** {_testo(rule["fonte"])}.',
                '- **Riscontri collegati:** ' + (', '.join(f'[E{j:03d}](#e{j:03d})' for j,g in enumerate(result.segnalazioni,1)
                                                          if j != i and g.inizio <= f.fine and g.fine >= f.inizio and set(g.voci) & set(f.voci)) or 'nessuno nella stessa posizione.'),
                '']
    out += ['## 5. Valutazione dell’armonizzazione', '',
            'Il basso analizzato è quello presente nel file. Non è possibile verificare che coincida con la consegna originale. Un accordo riconosciuto non è automaticamente appropriato allo stile scolastico.', '']
    for s in analysis.segmenti:
        out.append(f'- **{_testo(analysis.posizione(s.inizio))}:** {_testo(s.esito)}. {_testo(s.grado)}; funzione {_testo(s.funzione)}. Affidabilità: {_testo(s.affidabilita)}.')
        out.extend('  - Lettura alternativa / contesto: ' + _testo(a) for a in s.alternative)
    out += ['', '## 6. Copertura e limiti', '',
            'Superficie: condotta delle parti. Riduzione: note strutturali e figurazioni ipotizzate; non produce parallele certe. Non sono confrontati collegamenti attraverso pause o fermate.', '',
            '| Regola | Stato e intervallo |', '|---|---|']
    out.extend(f'| {rule} | {_testo(status)} |' for rule,status in result.copertura.items())
    out += ['', '### Limiti dell’analisi', '']
    out.extend('- ' + _testo(c) for c in analysis.limiti)
    out += ['- Riconoscimento delle figurazioni limitato a una nota superiore estranea per segmento; altre riduzioni restano indeterminate.',
            '- Centri locali senza cambio di armatura: solo tonicizzazioni motivate da dominante secondaria e risoluzione osservata; altre modulazioni non determinate.',
            '- Nessuna verifica sulla riduzione armonica delle parallele occultate da figurazioni; la copertura delle parallele riguarda la superficie.',
            '- Cifratura: solo intervalli e abbreviazioni esplicitamente supportati; simboli accordali trattati come annotazioni.',
            '- Risposte musicali ed eccezioni non ancora validate da un docente su corpus indipendente.',
            '- Le indicazioni non sono sostituzioni di note garantite corrette: ogni modifica va ricontrollata sulle altre voci e armonie.', '',
            '### Catalogo delle regole', '']
    for rule, meta in profile['regole'].items():
        out += [f'**{rule} — {_testo(meta["titolo"])}**', '',
                f'{_testo(meta["definizione"])} Eccezioni: {_testo(meta["eccezioni"])}', '',
                f'Esempi: {_testo(meta["esempi"])} Fonte: {_testo(meta["fonte"])}.', '']
    out += ['### Riferimenti del profilo', '']
    out.extend('- ' + _testo(source) for source in profile['fonti'])
    return '\n'.join(out) + '\n'


def salva(testo: str, ingresso: Path, cartella: Path | None = None, data=None) -> Path:
    timestamp = data or datetime.now().astimezone()
    directory = ingresso.parent if cartella is None else cartella
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=directory,
                                         prefix='.armonia-', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(testo)
            handle.flush()
            os.fsync(handle.fileno())
        while True:
            target = directory / f'{ingresso.stem}_analisi_{timestamp:%Y%m%d_%H%M%S_%f}.md'
            try:
                # link pubblica il file completo ed è esclusivo anche fra processi.
                os.link(temporary, target)
                return target
            except FileExistsError:
                timestamp += timedelta(microseconds=1)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
