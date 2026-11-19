"""Linea temporale razionale e ipotesi armoniche contestuali."""

from bisect import bisect_right
from dataclasses import dataclass, field
from fractions import Fraction

from .lettura import Evento, Partitura, ErroreIngresso

CERTA = 'certa sui dati e sul profilo'
CONDIZIONATA = 'condizionata all’analisi'
VERIFICARE = 'da verificare'


@dataclass
class Segmento:
    inizio: Fraction
    fine: Fraction
    eventi: dict[str, Evento | None]
    accento: float
    tonalita: object
    accordo: object | None = None
    romano: object | None = None
    grado: str = 'non determinabile'
    funzione: str = 'non determinabile'
    strutturali: dict[str, object] = field(default_factory=dict)
    figurazioni: dict[str, str] = field(default_factory=dict)
    alternative: list[str] = field(default_factory=list)
    affidabilita: str = VERIFICARE
    esito: str = 'interpretazione non determinabile'
    centro_certo: bool = False
    alterato: str = ''   # sesta italiana / francese / tedesca (riconosciuta per classi di altezza)

    @property
    def identita(self):
        # Identità scritta dell'accordo: indipendente da registro e rivolto.
        return frozenset(p.name for p in self.accordo.pitches) if self.accordo else frozenset()


@dataclass
class Analisi:
    partitura: Partitura
    segmenti: list[Segmento]
    tonalita: list[str]
    limiti: list[str]

    def misura(self, offset):
        starts = [m.inizio for m in self.partitura.misure]
        return self.partitura.misure[max(0, bisect_right(starts, offset) - 1)]

    def posizione(self, offset):
        m = self.misura(offset)
        local = offset - m.inizio + m.padding
        unit = Fraction(4, m.metro.denominator)
        compound = m.metro.numerator >= 6 and m.metro.numerator % 3 == 0
        pulse = unit * (3 if compound else 1)
        beat = local // pulse + 1
        remainder = local % pulse
        if compound:
            sub = remainder / unit + 1
            where = f'pulsazione {beat}, suddivisione {sub}'
        else:
            where = f'tempo {local / pulse + 1}'
        return f'battuta {m.numero} (indice {m.indice}), {where}'


def _accento(data: Partitura, t: Fraction) -> float:
    m = data.misure[max(0, bisect_right([m.inizio for m in data.misure], t) - 1)]
    local = t - m.inizio + m.padding
    return float(m.metro.getAccentWeight(local, forcePositionMatch=True))


def _figurazione(event, events, t, accento, data):
    from music21 import interval
    i = next(i for i, e in enumerate(events) if e is event)
    previous = events[i - 1] if i else None
    following = events[i + 1] if i + 1 < len(events) else None
    if following is None or following.pitch is None or following.inizio != event.fine or event.fermata:
        return None
    resolution = interval.Interval(event.pitch, following.pitch)
    step = abs(resolution.generic.directed) == 2 and abs(resolution.semitones) <= 2
    prepared = previous is not None and previous.pitch is not None and previous.fine == event.inizio and not previous.fermata
    if event.inizio < t and step and resolution.direction < 0:
        return 'ritardo preparato (ipotesi; verificare la consonanza della preparazione)'
    if not prepared:
        return None
    approach = interval.Interval(previous.pitch, event.pitch)
    weak = accento < _accento(data, previous.inizio) or accento < _accento(data, following.inizio)
    if step and abs(approach.generic.directed) == 2 and abs(approach.semitones) <= 2 and weak:
        if approach.direction == resolution.direction:
            return 'nota di passaggio'
        if previous.pitch == following.pitch:
            return 'nota di volta'
    if weak and event.pitch == following.pitch:
        return 'anticipazione (ipotesi)'
    if step and abs(approach.generic.directed) > 2 and not weak:
        return 'appoggiatura (ipotesi)'
    return None


_SESTE = {frozenset({8, 0, 6}): 'sesta italiana', frozenset({8, 0, 6, 2}): 'sesta francese',
          frozenset({8, 0, 6, 3}): 'sesta tedesca'}


def _sesta_aumentata(sounding, tonica):
    """Sesta eccedente: basso sul VI abbassato, sesta aumentata ortografica verso il IV alterato.
    Riconosciuta prima di _accordo, che la leggerebbe come triade o settima di radice errata."""
    from music21 import interval
    bass = sounding.get('B')
    if bass is None or len(sounding) != 4:
        return ''
    rel = lambda p: (p.pitchClass - tonica) % 12
    if rel(bass) != 8 or not any(rel(p) == 6 and interval.Interval(bass, p).simpleName == 'A6'
                                 for v, p in sounding.items() if v != 'B'):
        return ''
    return _SESTE.get(frozenset(rel(p) for p in sounding.values()), '')


def _accordo(pitches):
    from music21 import chord
    if len({p.name for p in pitches}) < 3:
        return None
    c = chord.Chord(list(pitches))
    if c.isTriad() or c.isSeventh():
        return c
    if c.third is not None and c.seventh is not None and c.fifth is None:
        names = {c.root().name, c.third.name, c.seventh.name}
        if {p.name for p in c.pitches} == names:
            return c
    return None


def _contesto(data):
    from music21 import key
    explicit = [(t, k) for t, k in data.contesti if isinstance(k, key.Key)]
    try:
        global_key = data.score.analyze('key')
    except Exception:
        # Senza varietà di altezze la correlazione tonale può non esistere.
        global_key = explicit[0][1] if explicit else key.Key('C')
        label = global_key.name if explicit else 'Tonalità non determinabile: Do maggiore usato solo come ipotesi di calcolo, non come riconoscimento'
        return global_key, explicit, [label, global_key.relative.name + ' (alternativa)']
    alternatives = [global_key.name]
    for candidate in getattr(global_key, 'alternateInterpretations', ())[:2]:
        if abs(global_key.correlationCoefficient - candidate.correlationCoefficient) < 0.08:
            alternatives.append(candidate.name)
    if explicit:
        alternatives.insert(0, f'{explicit[0][1].name} (modo dichiarato nel MusicXML)')
    else:
        relative = global_key.relative.name
        if relative not in alternatives:
            alternatives.append(f'{relative} (relativa dell’armatura, ipotesi alternativa)')
    return global_key, explicit, alternatives


def analizza(data: Partitura) -> Analisi:
    from music21 import chord, key, pitch, roman
    boundaries = {e.inizio for events in data.linee.values() for e in events}
    boundaries.update(e.fine for events in data.linee.values() for e in events)
    boundaries.update(t for t, _ in data.contesti)
    boundaries.update(a.inizio for a in data.annotazioni)
    for m in data.misure:
        boundaries.update((m.inizio, m.fine))
        # Ogni suddivisione scritta, anche quando tutte le note sono tenute.
        unit = Fraction(4, m.metro.denominator)
        t = m.inizio + ((-m.padding) % unit)
        while t < m.fine:
            boundaries.add(t)
            t += unit
    boundaries = sorted(boundaries)
    if len(boundaries) > 50000:
        raise ErroreIngresso('Partitura troppo estesa: limite 50000 confini temporali.')
    global_key, explicit, proposed = _contesto(data)
    limits = list(data.limiti)
    if not explicit:
        limits.append('Modo non dichiarato: tonalità stimata; regole tonali condizionate all’analisi globale e alle cadenze locali.')
    context = global_key
    pointers = dict.fromkeys(data.linee, 0)
    segments = []
    for start, end in zip(boundaries, boundaries[1:]):
        for t, signature in data.contesti:
            if t > start:
                break
            if isinstance(signature, key.Key):
                context = signature
            elif signature.sharps != context.sharps:
                major, minor = signature.asKey('major'), signature.asKey('minor')
                context = minor if global_key.mode == 'minor' else major
        active_context = next((k for t,k in reversed(data.contesti) if t <= start), None)
        tonal_declared = isinstance(active_context, key.Key)
        current = {}
        for voice, events in data.linee.items():
            i = pointers[voice]
            while i < len(events) and events[i].fine <= start:
                i += 1
            pointers[voice] = i
            current[voice] = events[i] if i < len(events) and events[i].inizio <= start < events[i].fine else None
        segment = Segmento(start, end, current, _accento(data, start), context, centro_certo=tonal_declared)
        sounding = {v: e.pitch for v, e in current.items() if e is not None and e.pitch is not None}
        segment.strutturali = sounding.copy()
        segment.alterato = _sesta_aumentata(sounding, context.tonic.pitchClass)
        segment.accordo = None if segment.alterato else _accordo(sounding.values())
        if segment.alterato:
            segment.grado, segment.funzione = segment.alterato, 'predominante'
            segment.affidabilita, segment.esito = CONDIZIONATA, 'accordo alterato riconosciuto per classi di altezza; risoluzione da verificare'
        if segment.accordo is not None and segment.accordo.seventh is not None and segment.accordo.fifth is None:
            segment.alternative.append('Accordo di settima incompleto: quinta omessa; lettura da verificare nel contesto.')
        if segment.accordo is None and not segment.alterato and len(sounding) >= 3:
            reductions = []
            for voice, p in sounding.items():
                remaining = {v: q for v, q in sounding.items() if v != voice}
                candidate = _accordo(remaining.values())
                ornament = _figurazione(current[voice], data.linee[voice], start, segment.accento, data)
                if candidate is None and ornament and segments and segments[-1].accordo is not None:
                    prior = segments[-1].accordo
                    names = {q.name for q in prior.pitches}
                    actual = {q.name for q in remaining.values()}
                    if actual < names and p.name not in names:
                        inferred = [pitch.Pitch(name + str(min(q.octave for q in remaining.values()) + 1)) for name in names - actual]
                        candidate = chord.Chord(list(remaining.values()) + inferred)
                        candidate.root(prior.root())
                if candidate is not None and ornament and voice != 'B':
                    reductions.append((voice, remaining, candidate, ornament))
            if reductions:
                voice, structural, candidate, ornament = reductions[0]
                segment.strutturali = structural
                segment.accordo = candidate
                segment.figurazioni[voice] = ornament
                segment.alternative.append('Superficie non ridotta: ' + ', '.join(p.nameWithOctave for p in sounding.values()))
                missing = {p.name for p in candidate.pitches} - {p.name for p in structural.values()}
                if missing:
                    segment.alternative.append('Note dell’accordo assunte per continuità contestuale, non suonanti: ' + ', '.join(sorted(missing)))
                if len(reductions) > 1:
                    segment.alternative.append('Riduzioni concorrenti: ' + ', '.join(v + ' ' + o for v, _, _, o in reductions[1:]))
        if segment.accordo is not None:
            try:
                rn = roman.romanNumeralFromChord(segment.accordo, context)
                segment.romano = rn
                segment.grado = rn.figure
                degree = rn.scaleDegree
                segment.funzione = ('tonica' if degree in (1, 6) else 'predominante' if degree in (2, 4)
                                    else 'dominante' if degree in (5, 7) else 'mediante / contesto richiesto')
                segment.affidabilita = CONDIZIONATA
                segment.esito = 'compatibile nella costruzione; collegamento da verificare'
            except (ValueError, TypeError) as exc:
                segment.alternative.append(f'Numero romano non determinabile: {exc}')
        if len(sounding) != 4:
            segment.affidabilita = VERIFICARE
            segment.esito = 'tessitura incompleta per pausa o voce assente'
        segments.append(segment)
    # Dominanti secondarie: si richiede una risoluzione osservata, non il solo
    # nome di un accordo estraneo alla scala.
    harmonic_changes = []
    for s in segments:
        if (not harmonic_changes or s.identita != harmonic_changes[-1].identita
                or tuple(v for v,e in s.eventi.items() if e is not None and e.pitch is not None)
                != tuple(v for v,e in harmonic_changes[-1].eventi.items() if e is not None and e.pitch is not None)):
            harmonic_changes.append(s)
    for left, right in zip(harmonic_changes, harmonic_changes[1:]):
        if left.accordo is None or right.accordo is None:
            continue
        if any(e is None or e.pitch is None for s in (left,right) for e in s.eventi.values()):
            continue
        if left.accordo.isDominantSeventh() and (left.accordo.root().pitchClass - right.accordo.root().pitchClass) % 12 == 7:
            local = key.Key(right.accordo.root().name, 'minor' if right.accordo.isMinorTriad() else 'major')
            if right.accordo.root().pitchClass != left.tonalita.tonic.pitchClass:
                target = right.grado
                for s in segments:
                    if left.inizio <= s.inizio < right.inizio:
                        s.alternative.append(f'Dominante secondaria V7/{target}; tonicizzazione di {local.name} motivata dalla risoluzione seguente.')
                        s.tonalita = local
                        s.grado = 'V' + (s.romano.figuresWritten if s.romano else '7') + '/' + target
                        s.funzione = 'dominante secondaria'
                        s.centro_certo = False
    for s in segments:
        if not s.alternative and s.accordo is not None:
            relative = s.tonalita.relative
            alternative = roman.romanNumeralFromChord(s.accordo, relative).figure
            if not s.centro_certo:
                s.alternative.append(f'{alternative} in {relative.name}: relativa da confrontare con le cadenze.')
    return Analisi(data, segments, list(dict.fromkeys(proposed)), limits)
