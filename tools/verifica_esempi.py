#!/usr/bin/env python3
"""Verifica gli esempi SATB con il rivelatore (tools/rivelatore-errori-armonia): parallele, dirette,
sensibile, settime, salti, risoluzioni, cadenze, progressioni, modulazioni; e confronta i titoli dei capitoli con
quanto rilevato (--testo). Uso: python3 tools/verifica_esempi.py [--testo] [id ...]   (exit 1 se ci sono errori)

Ogni segnalazione e' [automatica] (certa o condizionata alla tonalita' dichiarata dall'esempio) oppure
[da verificare a mano] (il rivelatore la dichiara incerta)."""
import glob, os, re, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'tools' / 'rivelatore-errori-armonia'))
from armonia.lettura import leggi
from armonia.analisi import analizza
from armonia.regole import controlla
from armonia.analisi import VERIFICARE
from music21 import key, meter, note, pitch, stream, tie
from tools.armonia.music import pname
from tools.esempi import genera
from tools.esempi.dati import ESEMPI

DA_EVITARE = {'es_cap22_07', 'es_cap04_03'}   # esempi di errore (parallele) voluti
# vincoli rigidi: parallele 5e/8ve, incroci, sovrapposizioni, sensibile non risolta (l'eccezione di Bach, discesa di
# terza in voce interna, esce come 'da verificare' e non fallisce), settima non discendente
RIGIDE = {'VL-P5', 'VL-P8', 'VL-CROSS', 'VL-OVERLAP', 'HA-LEADING', 'HA-SEVENTH', 'HA-INV7',
          'RS-NAPOLETANA', 'RS-ECCEDENTE', 'RS-64', 'RS-RITARDO'}   # risoluzioni di napoletana, seste eccedenti, 6/4 cadenzale, ritardi
# falsi positivi noti: basso cromatico (Si-Sib letto come settima non risolta)
NOTI = {'es_cap17_crom_sin_T', 'es_cap17_crom_leg_TS'}
SENZA_TONALITA = ('VL-', 'ME-', 'CA-', 'PR-', 'MO-', 'RS-', 'HA-FIGURATION')  # senza tonalita' nota gli altri controlli armonici (HA-*, HR-*) non sono affidabili

def etichetta(affidabilita):
    return 'da verificare a mano' if affidabilita == VERIFICARE else 'automatica'

CAPITOLI = Path(__file__).parents[1] / 'Capitoli'
TONO = re.compile(r'\b(Do|Re|Mi|Fa|Sol|La|Si)\s+(Maggiore|maggiore|M|minore|m)\b')

def titoli():
    """{id esempio: [titolo dell'ambiente esempio che lo include]}"""
    out = {}
    for f in sorted(CAPITOLI.glob('*.tex')):
        for titolo, corpo in re.findall(r'\\begin\{esempio\}\[(.*?)\]\s*(.*?)\\end\{esempio\}', f.read_text(encoding='utf-8'), re.S):
            for eid in re.findall(r'\\musica\{([^}]+)\}', corpo):
                out.setdefault(eid, []).append(titolo)
    return out

_TITOLI = None

def titolo_di(eid):
    global _TITOLI
    if _TITOLI is None: _TITOLI = titoli()
    return _TITOLI.get(eid, [])

TONI = {'Do': 'C', 'Re': 'D', 'Mi': 'E', 'Fa': 'F', 'Sol': 'G', 'La': 'A', 'Si': 'B'}

def tonalita(chords):
    """tonalita' dichiarata ('Do M: I', 'La m: V'), altrimenti tonica/modo del primo accordo 'I'/'i' in stato fondamentale; None se assente"""
    for c in chords:
        if m := re.match(r'(Do|Re|Mi|Fa|Sol|La|Si) (M|m):', c['rn']):
            return key.Key(TONI[m[1]], 'major' if m[2] == 'M' else 'minor')
    for c in chords:
        if c['rn'] in ('I', 'i') and not c['fig']:
            return key.Key(pname(c['v'][3]), 'major' if c['rn'] == 'I' else 'minor')

def tonalita_titolo(eid):
    """tonalita' dichiarata dal titolo dell'esempio ('... in Do Maggiore', 'Do M -> Sol M'): la prima citata"""
    for t in titolo_di(eid):
        if m := TONO.search(t):
            return key.Key(TONI[m[1]], 'major' if m[2] in ('Maggiore', 'maggiore', 'M') else 'minor')

def tratti(chords):
    """serie di accordi collegati (conn): le coppie affiancate da join() restano indipendenti"""
    run = []
    for c in chords:
        run.append(c)
        if not c['conn']:
            yield run; run = []

def analisi(run, k):
    s = stream.Score()
    for i, nome in enumerate(('Soprano', 'Contralto', 'Tenore', 'Basso')):
        p = stream.Part(); p.partName = nome
        p.append(meter.TimeSignature('4/4'))
        if k: p.append(k)   # senza tonalita' nota il rivelatore la stima e declassa le segnalazioni a 'da verificare'
        # come nell'incisione, le note comuni fra accordi consecutivi sono legate
        prev = None
        for c in run:
            n = note.Note(c['v'][i], quarterLength=4)
            if n.pitch.accidental is None: n.pitch.accidental = pitch.Accidental('natural')
            n.pitch.accidental.displayStatus = True   # senza, nelle legature music21 omette il bequadro e la rilettura altera la nota
            if prev is not None and prev.nameWithOctave == n.nameWithOctave:
                prev.tie = tie.Tie('continue' if prev.tie else 'start'); n.tie = tie.Tie('stop')
            p.append(n); prev = n
        p.makeMeasures(inPlace=True)
        s.append(p)
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'esempio.musicxml'; s.write('musicxml', fp=f)
        return controlla(analizza(leggi(f)))

def verifica(eid, e):
    """-> [(regola, gravita, affidabilita, testo)] per l'esempio"""
    k = tonalita(e['chords']); kt = k or tonalita_titolo(eid); out = []
    for run in tratti(e['chords']):
        if len(run) < 2: continue
        for f in analisi(run, kt).segnalazioni:
            if k or f.regola.startswith(SENZA_TONALITA):
                out.append((f.regola, f.gravita, f.affidabilita, f'{f.note} | {f.evidenza}'))
    return out

def rigide(eid, e):
    return [f for f in verifica(eid, e) if f[0] in RIGIDE and f[1] == 'errore' and f[2] != VERIFICARE and eid not in NOTI]

def incoerenze(titolo, trovati):
    """Confronta cio' che il titolo afferma (cadenza, progressione, modulazione, ritardo) con i rilevamenti
    `trovati` (= verifica()). -> [(etichetta, messaggio)]: 'automatica' se rilevamenti certi o condizionati alla
    tonalita' dichiarata contraddicono il titolo; 'da verificare a mano' se il rilevamento e' incerto o assente."""
    def rel(regola): return [(r, g, a, t) for r, g, a, t in trovati if r == regola]
    def lab(rilevati): return 'automatica' if rilevati and all(a != VERIFICARE for _, _, a, _ in rilevati) else 'da verificare a mano'
    out = []
    for m in re.finditer(r"[Cc]adenza\s+(perfetta|imperfetta|plagale|sospesa|d.inganno|frigia)", titolo, re.I):
        nome = re.sub(r"d.inganno", "d'inganno", 'cadenza ' + m[1].lower())
        r = rel('CA-TIPO')
        visti = {re.search(r"\| (cadenza [a-z' ]+?)(?: \(|:)", t)[1] for _, _, _, t in r}
        if nome not in visti:
            out.append((lab(r), f"il titolo dice '{nome}', rilevato: {', '.join(sorted(visti)) or 'nessuna cadenza'}"))
    for m in re.finditer(r'[Pp]rogressione per (quinte|terze|seconde|quarte)(?: (ascendenti|discendenti))?', titolo):
        voluto = f'{m[1]} {m[2]}' if m[2] else m[1]
        r = rel('PR-RILEVATA')
        if not any(voluto in t for _, _, _, t in r):
            out.append((lab(r), f"il titolo dice 'progressione per {voluto}', rilevato: {' / '.join(re.findall(r'per ([^:]+):', ' '.join(t for _, _, _, t in r))) or 'nessuna progressione'}"))
    modulante = rel('MO-RILEVATA') + [x for x in rel('PR-RILEVATA') if 'modulante:' in x[3] and 'non modulante' not in x[3]]
    if '$\\rightarrow$' in titolo and re.search(r'[Mm]odulazione', titolo):
        toni = [f'{n} {"maggiore" if k in ("Maggiore", "maggiore", "M") else "minore"}' for n, k in TONO.findall(titolo)]
        mod = rel('MO-RILEVATA')
        if len(toni) >= 2 and not any(f'da {toni[0]} a {toni[1]}' in t for _, _, _, t in mod):
            out.append((lab(mod), f"il titolo dice 'modulazione da {toni[0]} a {toni[1]}', rilevato: {' / '.join(re.findall(r'da [^(;]+ a [^(;]+', ' '.join(t for _, _, _, t in mod))) or 'nessuna modulazione'}"))
    if re.search(r'\bmodulante\b', titolo):
        non = bool(re.search(r'\bnon modulante\b', titolo))
        if non == bool(modulante):
            out.append((lab(modulante), f"il titolo dice '{'non ' if non else ''}modulante', rilevato: {'modulazione' if modulante else 'nessuna modulazione'}"))
    if re.search(r'\b[Rr]itardo\b', titolo) and not any('ritardo' in t for _, _, _, t in rel('HA-FIGURATION')):
        out.append(('da verificare a mano', "il titolo parla di ritardo, nessun ritardo riconosciuto"))
    return out

def main(args):
    ids = {a for a in args if not a.startswith('--')}; con_testo = '--testo' in args
    gen = genera(); tutti = {**ESEMPI, **gen}
    tit = {i: titolo_di(i) for i in tutti} if con_testo else {}
    bad = 0
    for eid, e in tutti.items():
        if e['type'] != 'satb' or (ids and eid not in ids) or eid in DA_EVITARE: continue
        trovati = verifica(eid, e)
        for r, g, a, t in trovati:
            print(f'{eid}: [{g}; {etichetta(a)}] {r}: {t}')
        for titolo in tit.get(eid, []):
            for et, msg in incoerenze(titolo, trovati):
                print(f'{eid}: [testo; {et}] {msg}')
                if eid in gen and et == 'automatica': bad += 1
        if eid in gen: bad += len([f for f in trovati if f[0] in RIGIDE and f[1] == 'errore' and f[2] != VERIFICARE and eid not in NOTI])   # i dati scritti a mano includono errori didattici voluti
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
