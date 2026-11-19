"""Importazione MusicXML sicura e identità vocali stabili."""

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Callable
import re
from xml.etree import ElementTree

from defusedxml import ElementTree as SafeXML
from defusedxml.common import DefusedXmlException


NOMI = dict(S='Soprano', A='Contralto', T='Tenore', B='Basso')
MAX_BYTES = 10 * 1024 * 1024
MAX_NOTE = 20000


class ErroreIngresso(ValueError):
    """File non interpretabile nel contratto SATB supportato."""


def percorso(value: str) -> Path:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return Path(value).expanduser()


def xml_sicuro(path: Path):
    if path.suffix.lower() not in ('.xml', '.musicxml'):
        raise ErroreIngresso('Usare un file MusicXML .xml o .musicxml; .mxl non supportato.')
    try:
        with path.open('rb') as handle:
            data = handle.read(MAX_BYTES + 1)
    except OSError as exc:
        raise ErroreIngresso(f'File non leggibile: {path} ({exc.strerror}).') from exc
    if len(data) > MAX_BYTES:
        raise ErroreIngresso('File troppo grande: limite 10 MiB.')
    try:
        root = SafeXML.fromstring(data, forbid_entities=True, forbid_external=True)
    except (ElementTree.ParseError, DefusedXmlException, ValueError) as exc:
        raise ErroreIngresso(f'XML non valido o non sicuro: {exc}.') from exc
    # MusicXML ordinario dichiara una DTD esterna: non viene caricata e non
    # viene inoltrata a music21; si passa soltanto l'albero già validato.
    if root.tag != 'score-partwise':
        raise ErroreIngresso('Occorre MusicXML score-partwise; riesportare il singolo brano in questo formato.')
    if len(root.findall('.//note')) > MAX_NOTE:
        raise ErroreIngresso(f'Troppe note: limite {MAX_NOTE}.')
    if root.find('.//transpose') is not None:
        raise ErroreIngresso('Parti trasposte non supportate: esportare le quattro voci ad altezza reale.')
    if any(root.find(f'.//{tag}') is not None for tag in ('unpitched', 'grace', 'senza-misura')):
        raise ErroreIngresso('Percussioni, abbellimenti senza durata o metro libero non supportati.')
    for time in root.findall('.//time'):
        if (len(time.findall('beats')) != 1 or len(time.findall('beat-type')) != 1
                or time.findtext('beats') not in ('2','3','4','6','9','12')
                or time.findtext('beat-type') not in ('2','4','8','16')):
            raise ErroreIngresso('Metro non supportato: usare un metro semplice o composto regolare.')
    for p in root.findall('.//note/pitch'):
        try:
            if p.findtext('step') not in 'C D E F G A B'.split() or not -1 <= int(p.findtext('octave', '')) <= 9:
                raise ValueError
        except ValueError:
            raise ErroreIngresso('Altezza incompleta o non valida: ogni nota richiede nome e ottava scritti.') from None
    for alter in root.findall('.//pitch/alter'):
        try:
            if Fraction(alter.text or '0').denominator != 1:
                raise ValueError
        except (ValueError, ZeroDivisionError):
            raise ErroreIngresso('Altezze microtonali non supportate.') from None
    return root


@dataclass
class Evento:
    voce: str
    pitch: object | None
    inizio: Fraction
    fine: Fraction
    legature: tuple[str, ...] = ()
    fermata: bool = False


@dataclass
class Misura:
    numero: str
    indice: int
    inizio: Fraction
    fine: Fraction
    metro: object
    padding: Fraction


@dataclass
class Annotazione:
    inizio: Fraction
    tipo: str
    valore: object
    fine: Fraction | None = None


@dataclass
class Partitura:
    file: Path
    score: object
    linee: dict[str, list[Evento]]
    mappatura: dict[str, str]
    misure: list[Misura]
    contesti: list[tuple[Fraction, object]]
    annotazioni: list[Annotazione] = field(default_factory=list)
    limiti: list[str] = field(default_factory=list)


def _nome_voce(text: str) -> str | None:
    words = re.findall(r'[a-z]+', text.lower())
    aliases = {'s': 'S', 'soprano': 'S', 'sopran': 'S', 'a': 'A', 'alto': 'A',
               'contralto': 'A', 't': 'T', 'tenor': 'T', 'tenore': 'T',
               'b': 'B', 'bass': 'B', 'basso': 'B'}
    found = {aliases[w] for w in words if w in aliases}
    return found.pop() if len(found) == 1 else None


def leggi(path: Path, scegli: Callable | None = None) -> Partitura:
    root = xml_sicuro(path)
    from music21 import chord, converter, expressions, harmony, key, meter, stream
    try:
        score = converter.parseData(ElementTree.tostring(root, encoding='unicode'), format='musicxml')
    except Exception as exc:
        raise ErroreIngresso(f'MusicXML non importabile: {exc}.') from exc
    candidates = {}
    origins = {}
    for part_index, part in enumerate(score.parts, 1):
        measures = list(part.getElementsByClass(stream.Measure))
        voice_ids = {str(v.id) for m in measures for v in m.voices}
        if not voice_ids:
            voice_ids = {'unica'}
        if len(voice_ids) > 1 and any(m.notesAndRests for m in measures):
            raise ErroreIngresso('Identificatori vocali incompleti: riesportare con voci separate in ogni misura.')
        for voice_id in sorted(voice_ids):
            label = f'{part_index}: {part.partName or part.id} / voce {voice_id}'
            events = []
            for m in measures:
                for obj in m.recurse().notesAndRests:
                    if isinstance(obj, harmony.Harmony):
                        continue
                    v = obj.getContextByClass(stream.Voice)
                    obj_id = str(v.id) if v is not None else next(iter(voice_ids))
                    if obj_id != voice_id:
                        continue
                    if isinstance(obj, chord.Chord):
                        raise ErroreIngresso('Linee non monodiche: riesportare con voci separate, senza accordi che perdono le identità.')
                    start = Fraction(obj.getOffsetInHierarchy(part))
                    end = start + Fraction(obj.quarterLength)
                    if end <= start:
                        raise ErroreIngresso('Evento senza durata positiva: riesportare senza abbellimenti senza durata.')
                    ties = (obj.tie.type,) if obj.tie else ()
                    events.append(Evento('', None if obj.isRest else obj.pitch, start, end, ties,
                                         any(isinstance(e, expressions.Fermata) for e in obj.expressions)))
            events.sort(key=lambda e: e.inizio)
            merged = []
            for event in events:
                if merged and event.inizio < merged[-1].fine:
                    raise ErroreIngresso('Eventi sovrapposti nella stessa voce: riesportare quattro linee monodiche separate.')
                continuation = bool(event.legature and event.legature[0] in ('stop', 'continue'))
                if continuation:
                    if not merged or merged[-1].fine != event.inizio or merged[-1].pitch != event.pitch or not merged[-1].legature or merged[-1].legature[-1] not in ('start', 'continue'):
                        raise ErroreIngresso('Legatura di valore senza preparazione coerente nella stessa voce.')
                    previous = merged[-1]
                    previous.fine = event.fine
                    previous.legature += event.legature
                    previous.fermata |= event.fermata
                else:
                    if merged and merged[-1].legature and merged[-1].legature[-1] in ('start', 'continue'):
                        raise ErroreIngresso('Legatura di valore interrotta o incompleta.')
                    merged.append(event)
            if merged and merged[-1].legature and merged[-1].legature[-1] in ('start', 'continue'):
                raise ErroreIngresso('Legatura di valore incompleta alla fine della voce.')
            if merged:
                candidates[label] = merged
                origins[label] = part
    if len(candidates) != 4 or any(not any(e.pitch is not None for e in events) for events in candidates.values()):
        raise ErroreIngresso(f'Ricostruite {len(candidates)} linee; servono quattro voci con note. Riesportare quattro parti monodiche oppure due pentagrammi con due voci separate ciascuno.')
    inferred = {}
    for label in candidates:
        part = origins[label]
        voice = _nome_voce(f'{part.partName or ""} {part.partAbbreviation or ""}')
        if voice and voice not in inferred:
            inferred[voice] = label
    if len(inferred) != 4:
        if scegli is None:
            raise ErroreIngresso('Mappatura SATB ambigua: specificare una sola assegnazione delle quattro linee.')
        inferred = scegli(list(candidates))
    if set(inferred) != set(NOMI) or set(inferred.values()) != set(candidates):
        raise ErroreIngresso('Mappatura non valida: ogni linea deve essere assegnata una volta a S, A, T, B.')
    lines = {v: candidates[inferred[v]] for v in NOMI}
    for v, events in lines.items():
        for event in events:
            event.voce = v
    reference = origins[inferred['B']]
    measures = []
    contexts = []
    for i, m in enumerate(reference.getElementsByClass(stream.Measure), 1):
        ts = m.timeSignature or m.getContextByClass(meter.TimeSignature)
        if ts is None or ts.numerator not in (2, 3, 4, 6, 9, 12) or ts.denominator not in (2, 4, 8, 16):
            raise ErroreIngresso('Metro assente o non supportato: usare un metro semplice o composto regolare.')
        start = Fraction(m.offset)
        end = start + Fraction(m.highestTime)
        if end <= start or end - start > Fraction(ts.barDuration.quarterLength):
            raise ErroreIngresso('Durata della misura non coerente con il metro.')
        measures.append(Misura(str(m.measureNumberWithSuffix()), i, start, end, ts, Fraction(m.paddingLeft)))
        for context in m.recurse().getElementsByClass(key.KeySignature):
            contexts.append((Fraction(context.getOffsetInHierarchy(reference)), context))
    if not measures:
        raise ErroreIngresso('Nessuna misura riconoscibile nel basso.')
    for part in score.parts:
        pm = list(part.getElementsByClass(stream.Measure))
        if len(pm) != len(measures) or any(Fraction(m.offset) != ref.inizio or Fraction(m.highestTime) != ref.fine - ref.inizio
                                          for m, ref in zip(pm, measures)):
            raise ErroreIngresso('Misure non allineate fra le parti: includere pause esplicite e riesportare.')
        for m, ref in zip(pm, measures):
            ts = m.timeSignature or m.getContextByClass(meter.TimeSignature)
            if ts is not None and ts.ratioString != ref.metro.ratioString:
                raise ErroreIngresso('Metri differenti fra le parti non supportati.')
        for k in part.recurse().getElementsByClass(key.KeySignature):
            t = Fraction(k.getOffsetInHierarchy(part))
            reference_key = next((r for at,r in reversed(contexts) if at <= t), None)
            if reference_key is not None and (reference_key.sharps != k.sharps or
                    isinstance(k,key.Key) and isinstance(reference_key,key.Key) and k.mode != reference_key.mode):
                raise ErroreIngresso('Armature o modi discordanti fra le parti: verificare l’esportazione.')
    annotations = []
    for part in score.parts:
        for symbol in part.recurse().getElementsByClass(harmony.ChordSymbol):
            annotations.append(Annotazione(Fraction(symbol.getOffsetInHierarchy(part)), 'simbolo', symbol))
    # La cifratura non è importata uniformemente dai convertitori music21.
    # Si conserva quindi direttamente dall'XML con i tempi del basso.
    bass_part = root.findall('part')
    reference_id = str(reference.id).split('-Staff')[0]
    bass_xml = next((p for p in bass_part if p.get('id') == reference_id), bass_part[-1] if bass_part else None)
    if bass_xml is not None:
        divisions = 1
        for raw, m in zip(bass_xml.findall('measure'), measures):
            cursor = Fraction(0)
            for obj in raw:
                if obj.tag == 'attributes':
                    divisions = int(obj.findtext('divisions', str(divisions)))
                    if divisions <= 0:
                        raise ErroreIngresso('Valore divisions non valido.')
                elif obj.tag in ('backup', 'forward'):
                    cursor += Fraction(int(obj.findtext('duration', '0')), divisions) * (-1 if obj.tag == 'backup' else 1)
                elif obj.tag == 'note' and obj.find('chord') is None:
                    cursor += Fraction(int(obj.findtext('duration', '0')), divisions)
                elif obj.tag == 'figured-bass':
                    figures = tuple(''.join(f.findtext(tag, '') for tag in ('prefix','figure-number','suffix')) for f in obj.findall('figure'))
                    duration = obj.findtext('duration')
                    annotations.append(Annotazione(m.inizio + cursor, 'cifre', figures,
                                       m.inizio + cursor + Fraction(int(duration), divisions) if duration else None))
    limits = []
    if any(root.find(f'.//{tag}') is not None for tag in ('repeat', 'ending', 'sound[@dacapo]', 'sound[@dalsegno]', 'segno', 'coda')):
        limits.append('Ritornelli/finali/salti presenti: analizzato solo l’ordine scritto; collegamenti di esecuzione non controllati.')
    if root.find('.//pedal') is not None:
        limits.append('Pedale notato: eccezioni armoniche specifiche da verificare.')
    return Partitura(path, score, lines, inferred, measures, sorted(contexts, key=lambda x: x[0]), annotations, limits)
