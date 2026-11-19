"""Controlli deterministici: superficie certa e ipotesi armoniche distinte."""

from dataclasses import dataclass
from importlib.resources import files
from itertools import combinations
import re
import tomllib

from .analisi import Analisi, CERTA, CONDIZIONATA, VERIFICARE
from .lettura import NOMI
from .sintassi import controlla_sintassi


def carica_profilo():
    return tomllib.loads(files('armonia').joinpath('profili/complementare_it.toml').read_text(encoding='utf-8'))


@dataclass
class Segnalazione:
    regola: str
    inizio: object
    fine: object
    voci: tuple[str, ...]
    note: str
    evidenza: str
    interpretazione: str
    gravita: str
    affidabilita: str
    indicazione: str


@dataclass
class Risultato:
    analisi: Analisi
    profilo: dict
    segnalazioni: list[Segnalazione]
    copertura: dict[str, str]

    @property
    def parziale(self):
        return bool(self.analisi.limiti) or any('non supportata' in c or 'non valutabile' in c for c in self.copertura.values())

    @property
    def conteggi(self):
        return {
            'errori': sum(f.gravita == 'errore' and f.affidabilita == CERTA for f in self.segnalazioni),
            'avvertimenti': sum(f.gravita == 'avvertimento' and f.affidabilita == CERTA for f in self.segnalazioni),
            'verificare': sum(f.affidabilita != CERTA for f in self.segnalazioni),
        }


def _intervallo(a, b):
    from music21 import interval
    return interval.Interval(a, b)


def _perfetto(a, b):
    i = _intervallo(a, b)
    if i.specifier.name != 'PERFECT':
        return None
    if i.generic.simpleUndirected == 5:
        return 'P5'
    if i.generic.simpleUndirected == 1:
        return 'P8'
    return None


def _pitch(segment, voice):
    e = segment.eventi[voice]
    return e.pitch if e else None


def _nota(p):
    return p.nameWithOctave if p is not None else 'pausa'


def _prossimo_movimento(events, event):
    previous = event
    for current in events[events.index(event) + 1:]:
        if previous.fermata or current.inizio != previous.fine or current.pitch is None:
            return None
        if current.pitch != event.pitch:
            return current
        previous = current
    return None


def controlla(analysis: Analisi, profilo=None) -> Risultato:
    from music21 import pitch
    profile = carica_profilo() if profilo is None else profilo
    findings = []
    seen = {}
    coverage = {}
    first = analysis.posizione(analysis.segmenti[0].inizio)
    last = analysis.posizione(analysis.segmenti[-1].fine)
    extent = f'{first} → {last}'
    for rule, meta in profile['regole'].items():
        coverage[rule] = ('disattivata dal profilo' if not meta['attiva'] else
                          'non supportata: ' + meta['eccezioni'] if not meta['disponibile'] else
                          f'applicata ove presenti le condizioni; intervallo: {extent}')

    def add(rule, s, voices, evidence, suggestion, confidence=CERTA, before=None, severity=None):
        meta = profile['regole'][rule]
        if not meta['attiva'] or not meta['disponibile']:
            return
        voices = tuple(voices)
        notes = '; '.join(f'{NOMI[v]}: ' + (f'{_nota(_pitch(before, v))} → ' if before else '') + _nota(_pitch(s, v)) for v in voices)
        identity = (rule, voices, tuple((v, s.eventi[v].inizio if s.eventi[v] else None, _nota(_pitch(s, v))) for v in voices),
                    (tuple(before.eventi[v].inizio if before.eventi[v] else None for v in voices)
                     if before and rule.startswith('HA-') else before.inizio if before else None))
        if identity in seen:
            old = seen[identity]
            if old.fine == s.inizio:
                old.fine = s.fine
            return
        f = Segnalazione(rule, before.inizio if before else s.inizio, s.inizio if before else s.fine,
                         voices, notes, evidence,
                         f'{s.grado} in {s.tonalita.name}' if confidence != CERTA else 'superficie musicale; nessuna riduzione richiesta',
                         severity or meta['gravita'], confidence, suggestion)
        findings.append(f)
        seen[identity] = f

    segments = analysis.segmenti
    by_start = {s.inizio: s for s in segments}
    preceding = {right.inizio: left for left,right in zip(segments,segments[1:])}
    for s in segments:
        for upper, lower in zip('SAT', 'ATB'):
            p, q = _pitch(s, upper), _pitch(s, lower)
            if p is None or q is None:
                continue
            if q.ps > p.ps:
                add('VL-CROSS', s, (upper, lower), 'La voce inferiore supera quella superiore.',
                    'Rivedere la disposizione mantenendo riconoscibili le identità vocali e il basso dato.')
            distance = p.ps - q.ps
            if upper != 'T' and distance > profile['soglie']['spaziatura_superiori']:
                add('VL-SPACE', s, (upper, lower), f'Distanza di {distance:g} semitoni, oltre l’ottava.',
                    'Avvicinare le parti superiori e ricontrollare tutti i collegamenti.')
            elif upper == 'T' and distance > profile['soglie']['spaziatura_basso_avviso']:
                add('VL-BASS-SPACE', s, (upper, lower), f'Distanza di {distance:g} semitoni fra tenore e basso.',
                    'Valutare equilibrio e cantabilità; questa soglia non è un divieto universale.')
        for voice in NOMI:
            p = _pitch(s, voice)
            if p is None:
                continue
            lo, hi = (pitch.Pitch(n).ps for n in profile['estensioni'][voice])
            if not lo <= p.ps <= hi:
                add('ME-RANGE', s, (voice,), f'{p.nameWithOctave} fuori registro {profile["estensioni"][voice]}.',
                    'Verificare che la nota sia comoda per la voce prevista, rispettando il basso dato.')
        for v, w in combinations(NOMI, 2):
            p, q = _pitch(s, v), _pitch(s, w)
            if p is not None and q is not None and p.step == q.step and p.pitchClass != q.pitchClass:
                add('HA-CHROMATIC', s, (v,w), 'Stesso nome diatonico con alterazioni simultanee differenti.',
                    'Verificare ortografia, modo minore, note estranee e funzione locale prima di correggere.', VERIFICARE)

    # Il confronto si aggiorna per ogni coppia, senza generare moto quando
    # cambia soltanto una terza voce o compare un confine metrico.
    for voices in combinations(NOMI, 2):
        previous = None
        for s in segments:
            events = [s.eventi[v] for v in voices]
            if any(e is None or e.pitch is None for e in events):
                previous = None
                continue
            if previous is None:
                previous = s
                continue
            old_events = [previous.eventi[v] for v in voices]
            if any(e.fermata and e.fine <= s.inizio for e in old_events):
                previous = s
                continue
            p, q = (e.pitch for e in old_events)
            r, t = (e.pitch for e in events)
            if p == r and q == t:
                previous = s
                continue
            motion = (r.ps - p.ps) * (t.ps - q.ps)
            old, new = _perfetto(p,q), _perfetto(r,t)
            evidence = f'{_intervallo(q,p).name} → {_intervallo(t,r).name}; movimenti {r.ps-p.ps:+g}, {t.ps-q.ps:+g} semitoni.'
            if old and new == old and motion > 0:
                add('VL-' + new, s, voices, evidence,
                    'Rivedere una parte superiore con moto contrario o obliquo, conservare il basso e ricontrollare le sei coppie.', before=previous)
            elif old and new == old and motion < 0:
                add('VL-CONTRARY', s, voices, evidence,
                    'Confrontare il trattamento del moto contrario e dei cambi di registro con il programma del docente.', VERIFICARE, previous)
            elif new and motion > 0 and old != new and abs(_intervallo(p,r).generic.directed) > 2:
                outer = voices == ('S','B')
                add('VL-DIRECT', s, voices, evidence + ' Salto della voce superiore.',
                    'Valutare un arrivo per grado congiunto della voce superiore; ricontrollare accordi e altre parti.',
                    CERTA if outer else VERIFICARE, previous,
                    None if outer else 'osservazione')
            if _intervallo(q,p).simpleName == 'd5' and new == 'P5' and motion > 0:
                add('VL-UNEQUAL', s, voices, evidence,
                    'Verificare il passaggio diminuita–giusta, le parti coinvolte e la risoluzione della dissonanza.', VERIFICARE, previous)
            if voices in (('S','A'),('A','T'),('T','B')) and (r.ps < q.ps or t.ps > p.ps):
                add('VL-OVERLAP', s, voices, 'Una parte supera la posizione precedente della voce adiacente. ' + evidence,
                    'Rivedere il collegamento rispettando l’ambito occupato dalla voce vicina.', before=previous)
            previous = s

    for voice, events in analysis.partitura.linee.items():
        for i, (left, right) in enumerate(zip(events, events[1:])):
            if left.pitch is None or right.pitch is None or left.fine != right.inizio or left.fermata:
                continue
            s = by_start[right.inizio]
            before = preceding[right.inizio]
            interval = _intervallo(left.pitch, right.pitch)
            altered = str(interval.specifier).startswith(('A','d')) and interval.generic.undirected > 1
            if abs(interval.semitones) > profile['soglie']['salto_massimo'] or altered:
                add('ME-LEAP', s, (voice,), f'Intervallo melodico {interval.directedName}.',
                    'Controllare la cantabilità; per la seconda aumentata nel minore confrontare la convenzione del docente.', before=before)
            if interval.generic.undirected >= 5 and i + 2 < len(events):
                following = events[i + 2]
                if following.pitch is not None and following.inizio == right.fine and not right.fermata:
                    recovery = _intervallo(right.pitch, following.pitch)
                    if not (recovery.generic.undirected == 2 and recovery.direction == -interval.direction and abs(recovery.semitones) <= 2):
                        add('ME-RECOVERY', s, (voice,), f'Salto {interval.directedName} seguito da {recovery.directedName}.',
                            'Valutare un recupero per grado congiunto contrario e la forma complessiva della linea.', before=before)

    harmonies = []
    for s in segments:
        if (not harmonies or s.identita != harmonies[-1].identita or s.tonalita.name != harmonies[-1].tonalita.name
                or tuple(_nota(_pitch(s,v)) for v in NOMI) != tuple(_nota(_pitch(harmonies[-1],v)) for v in NOMI)
                or s.figurazioni != harmonies[-1].figurazioni):
            harmonies.append(s)
    origin = None
    for s in segments:
        if s.accordo is None or any(e is None or e.pitch is None for e in s.eventi.values()):
            origin = None
            continue
        if (origin is None or s.identita != origin.identita or s.tonalita.name != origin.tonalita.name
                or any(e is not None and e.fermata and e.fine == s.inizio
                       for e in preceding.get(s.inizio,s).eventi.values())):
            origin = s
        elif s.accento > origin.accento:
            add('HR-SYNC', s, tuple(s.strutturali), f'Stesso accordo da accento {origin.accento:g} a {s.accento:g}; disposizione e rivolto non cambiano l’identità.',
                'Verificare l’articolazione armonica sul forte; distinguere anacrusi, pedali e formule cadenzali.',
                VERIFICARE if s.figurazioni or origin.figurazioni or analysis.misura(origin.inizio).padding else CONDIZIONATA, origin)
            origin = s

    for i, s in enumerate(harmonies):
        adjacent = harmonies[i+1] if i+1 < len(harmonies) else None
        following = next((t for t in harmonies[i+1:] if t.identita != s.identita
                          or t.tonalita.name != s.tonalita.name
                          or any(_pitch(t,v) is None for v in NOMI)), None)
        previous = harmonies[i-1] if i else None
        c = s.accordo
        if c is None:
            if s.alterato:
                continue
            if sum(_pitch(s,v) is not None for v in NOMI) == 4:
                add('HA-INCOMPLETE', s, tuple(NOMI), 'Le note non determinano una triade o settima completa riconosciuta.',
                    'Verificare omissioni e figurazioni nel contesto; non sostituire automaticamente l’accordo.', VERIFICARE)
            continue
        for voice, ornament in s.figurazioni.items():
            add('HA-FIGURATION', s, (voice,), ornament + '; lettura della superficie e riduzione tenute distinte.',
                'Verificare preparazione, accento e risoluzione; le parallele certe sono controllate sulla superficie.', CONDIZIONATA)
        leading = s.tonalita.getLeadingTone().name
        dominant = (s.romano is not None and s.romano.scaleDegree in (5,7)) or c.isDominantSeventh() and s.funzione == 'dominante secondaria'
        doubles = [v for v,p in s.strutturali.items() if p.name == leading]
        if dominant and len(doubles) > 1:
            add('HA-LEADING-DOUBLE', s, doubles, f'Sensibile {leading} presente in {len(doubles)} parti strutturali.',
                'Evitare il raddoppio del suono obbligato nel contesto dominante riconosciuto.', CONDIZIONATA)
        seventh = c.seventh
        if seventh is not None:
            voices = [v for v,p in s.strutturali.items() if p.name == seventh.name]
            if len(voices) > 1:
                add('HA-DOUBLING', s, voices, f'Settima accordale {seventh.name} raddoppiata.',
                    'Rivedere il raddoppio della dissonanza e le sue risoluzioni.', CONDIZIONATA)
            dominant_species = (c.third is not None and _intervallo(c.root(),c.third).simpleName == 'M3'
                                and _intervallo(c.root(),seventh).simpleName == 'm7')
            if not dominant_species:
                for voice in voices:
                    e = s.eventi[voice]
                    prior = [p for p in analysis.partitura.linee[voice] if p.fine == e.inizio]
                    sustained = e.inizio < s.inizio
                    prepared = bool(prior and prior[-1].pitch == e.pitch)
                    if not sustained and not prepared:
                        add('HA-PREPARATION', s, (voice,), f'Settima {seventh.name} non preparata per nota comune osservabile.',
                            'Verificare la specie d’accordo: la preparazione non è richiesta nello stesso modo per tutte le settime.', VERIFICARE)
        connected = following is not None and following.accordo is not None and all(
            _pitch(following,v) is not None and _pitch(s,v) is not None
            and not (s.eventi[v].fermata and s.eventi[v].fine <= following.inizio) for v in NOMI)
        if connected:
            for voice, p in s.strutturali.items():
                e = s.eventi[voice]
                # Si segue la prima risoluzione reale, anche se il suono è
                # tenuto oltre il primo cambiamento di armonia.
                events = analysis.partitura.linee[voice]
                after = _prossimo_movimento(events,e)
                if after is None or after.pitch is None or e.fermata:
                    continue
                movement = _intervallo(p, after.pitch)
                resolution = by_start.get(after.inizio, following)
                if seventh is not None and p.name == seventh.name and not (movement.generic.directed == -2 and -2 <= movement.semitones <= -1):
                    add('HA-SEVENTH', resolution, (voice,), f'Settima {p.name} risolve per {movement.directedName} invece di scendere di grado.',
                        'Verificare la discesa della settima, oppure motivare una risoluzione eccezionale nel contesto.', CONDIZIONATA, s)
                tonic_next = resolution.accordo is not None and resolution.accordo.root().name == s.tonalita.tonic.name
                if dominant and p.name == leading and tonic_next and not (movement.generic.directed == 2 and movement.semitones == 1):
                    inner_exception = voice in 'AT' and movement.generic.directed == -3
                    add('HA-LEADING', resolution, (voice,), f'Sensibile {leading} segue {movement.directedName}.' + (' Possibile eccezione in parte interna.' if inner_exception else ''),
                        'Verificare l’ascesa alla tonica o l’eccezione ammessa per la parte interna.',
                        VERIFICARE if inner_exception else CONDIZIONATA, s,
                        'osservazione' if inner_exception else None)
            if c.seventh is not None and c.inversion() == 3:
                move = _intervallo(_pitch(s,'B'), _pitch(following,'B'))
                if not (move.generic.directed == -2 and -2 <= move.semitones <= -1):
                    add('HA-INV7', following, ('B',), f'Basso del terzo rivolto: {move.directedName}.',
                        'Il basso è la settima dell’accordo: verificare la sua discesa di grado.', CONDIZIONATA, s)
            if s.funzione == 'dominante' and following.funzione == 'predominante':
                add('HA-CONNECTION', following, tuple(NOMI), f'{s.grado} → {following.grado}: ritorno da dominante a predominante.',
                    'Esaminare frase, progressione e prolungamenti; la coppia di gradi da sola non dimostra un errore.', VERIFICARE, s)
            elif (s.romano.scaleDegree, following.romano.scaleDegree) in ((5,1),(5,6),(4,5),(2,5)):
                following.esito = 'compatibile con il contesto analizzato (ipotesi funzionale)'
        if c.isTriad() and c.inversion() == 2:
            category = 'forma non determinabile'
            bass = _pitch(s,'B')
            if (adjacent and adjacent.accordo is not None and bass == _pitch(adjacent,'B')
                    and adjacent.accordo.root().name == bass.name and bass.name == s.tonalita.pitchFromDegree(5).name):
                category = 'quarta e sesta di cadenza (ipotesi; verificare risoluzioni 6–5 e 4–3)'
            elif previous and adjacent and _pitch(previous,'B') is not None and _pitch(adjacent,'B') is not None:
                a, b = _intervallo(_pitch(previous,'B'),bass), _intervallo(bass,_pitch(adjacent,'B'))
                if a.generic.undirected == b.generic.undirected == 2 and a.direction == b.direction and s.accento < previous.accento:
                    category = 'quarta e sesta di passaggio (ipotesi)'
                elif _pitch(previous,'B') == bass == _pitch(adjacent,'B'):
                    category = 'quarta e sesta su pedale (ipotesi)'
            s.alternative.append(category)
            add('HA-64', s, tuple(s.strutturali), category,
                'Controllare preparazione e risoluzione della quarta e della sesta nella categoria proposta.', VERIFICARE)
            if category == 'forma non determinabile':
                coverage['HA-64'] += f'; non valutabile: {analysis.posizione(s.inizio)} (tipo di 6/4 non definito)'
        if s.funzione == 'dominante secondaria':
            add('HA-MODULATION', s, tuple(s.strutturali), '; '.join(s.alternative),
                'Verificare la tonicizzazione sulla risoluzione e sul seguito; non equivale da sola a una modulazione stabile.', CONDIZIONATA)

    for left, right in zip(harmonies, harmonies[1:]):
        if not left.accordo or not right.accordo or any(_pitch(s,v) is None for s in (left,right) for v in NOMI):
            continue
        chromatic_voices = {v for v in NOMI if _pitch(left,v).step == _pitch(right,v).step and _pitch(left,v).pitchClass != _pitch(right,v).pitchClass}
        for v,w in combinations(NOMI,2):
            if v in chromatic_voices or w in chromatic_voices:
                continue
            for a,b in ((v,w),(w,v)):
                p,q = _pitch(left,a),_pitch(right,b)
                if p.step == q.step and p.pitchClass != q.pitchClass:
                    add('HA-CHROMATIC', right, (v,w), f'{p.name} → {q.name} in parti differenti su armonie contigue.',
                        'Confrontare centro locale, modo minore e distanza temporale; non correggere automaticamente un cromatismo.', VERIFICARE, left)

    controlla_sintassi(analysis, add)

    figures = [a for a in analysis.partitura.annotazioni if a.tipo == 'cifre']
    if not figures:
        coverage['HA-FIGURES'] = 'non applicabile: nessuna cifratura presente; consegna originale non confrontabile'
    for annotation in analysis.partitura.annotazioni:
        s = by_start.get(annotation.inizio)
        if s is None:
            coverage['HA-FIGURES' if annotation.tipo == 'cifre' else 'HA-SYMBOL'] += '; non valutabile: annotazione fuori dalla linea temporale'
            continue
        if annotation.tipo == 'simbolo':
            expected = {p.name for p in annotation.valore.pitches}
            unexpected = {p.name for p in s.strutturali.values()} - expected
            if unexpected:
                add('HA-SYMBOL', s, tuple(s.strutturali), f'Simbolo {annotation.valore.figure}; note estranee al simbolo: {", ".join(sorted(unexpected))}.',
                    'Verificare sia l’annotazione sia le note e le figurazioni: il simbolo non è una soluzione autorevole.', CONDIZIONATA)
        else:
            _cifre(annotation, segments, analysis, coverage, add)
    if not any(a.tipo == 'simbolo' for a in analysis.partitura.annotazioni):
        coverage['HA-SYMBOL'] = 'non applicabile: nessun simbolo accordale presente'
    findings.sort(key=lambda f: (f.inizio, f.fine, f.regola, f.voci))
    return Risultato(analysis, profile, findings, coverage)


def _cifre(annotation, segments, analysis, coverage, add):
    from music21 import pitch
    figures = list(annotation.valore)
    expanded = {'6': ['6','3'], '7': ['7','5','3'], '64': ['6','4'], '65': ['6','5','3'],
                '43': ['6','4','3'], '42': ['6','4','2'], '2': ['6','4','2']}
    token = ''.join(figures)
    figures = expanded.get(token, figures)
    parsed = []
    for f in figures:
        match = re.fullmatch(r'(#|b|sharp|flat|natural|n)?(2|3|4|5|6|7|8|9|11|13)(#|b|sharp|flat|natural|n)?', f)
        if not match or match[1] and match[3]:
            coverage['HA-FIGURES'] += f'; non valutabile: cifre {annotation.valore} a {analysis.posizione(annotation.inizio)}'
            return
        parsed.append((int(match[2]), match[1] or match[3]))
    # Senza durata esplicita la cifra vale fino al successivo attacco del basso
    # o alla prossima cifra, non arbitrariamente fino alla fine del brano.
    later = [e.inizio for e in analysis.partitura.linee['B'] if e.inizio > annotation.inizio]
    later += [a.inizio for a in analysis.partitura.annotazioni if a.tipo == 'cifre' and a.inizio > annotation.inizio]
    end = annotation.fine or min(later, default=segments[-1].fine)
    for s in segments:
        if not annotation.inizio <= s.inizio < end:
            continue
        bass = _pitch(s,'B')
        if bass is None or len(s.strutturali) != 4:
            coverage['HA-FIGURES'] += f'; non valutabile: pausa o riduzione a {analysis.posizione(s.inizio)}'
            continue
        missing = []
        for number, accidental in parsed:
            step = 'CDEFGAB'[('CDEFGAB'.index(bass.step) + number - 1) % 7]
            base = pitch.Pitch(step + '4')
            signature = next((k for t,k in reversed(analysis.partitura.contesti) if t <= s.inizio), s.tonalita)
            acc = signature.accidentalByStep(step)
            alteration = acc.alter if acc else 0
            if accidental:
                # Nella cifratura scolastica l'alterazione è rispetto alla nota
                # diatonica dell'armatura, il bequadro la rende naturale.
                if accidental in ('n','natural'):
                    alteration = 0
                else:
                    alteration += 1 if accidental in ('#','sharp') else -1
            base.accidental = pitch.Accidental(alteration)
            expected = base.pitchClass
            if not any(p.step == step and p.pitchClass == expected and p.ps >= bass.ps
                       and (number < 8 or _intervallo(bass,p).generic.directed >= number)
                       for v,p in s.strutturali.items() if v != 'B'):
                missing.append(str(number) + (accidental or ''))
        if missing:
            s.esito = 'costruzione incompatibile con la cifratura (lettura condizionale)'
            add('HA-FIGURES', s, tuple(s.strutturali), f'Cifre {annotation.valore}; intervalli richiesti assenti: {", ".join(missing)}.',
                'Rivedere gli intervalli sopra il basso secondo le cifre scritte, poi controllare condotta e risoluzioni.', CONDIZIONATA)
