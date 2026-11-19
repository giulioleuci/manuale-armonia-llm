"""Sintassi armonica: cadenze, risoluzioni cadenzali e alterate, progressioni, modulazioni.

Lavora sulle armonie riconosciute da analisi.py (un'armonia = segmenti contigui con la stessa identità).
Tutto dipende dall'analisi tonale: dove il centro non è dichiarato o la lettura è ambigua la
segnalazione resta 'da verificare'; le altre sono 'condizionate' (deterministiche sul centro assunto)."""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from .analisi import CONDIZIONATA, VERIFICARE, Segmento, _accordo

LETTERE = 'CDEFGAB'
SCALA = {False: frozenset({0, 2, 4, 5, 7, 9, 11}), True: frozenset({0, 2, 3, 5, 7, 8, 10, 11})}  # minore: con sensibile
# classe di altezza della radice rispetto alla tonica -> (grado 0-6, alterazione)
GRADI = {False: {0: (0, 0), 1: (1, -1), 2: (1, 0), 3: (2, -1), 4: (2, 0), 5: (3, 0), 6: (3, 1), 7: (4, 0), 8: (5, -1), 9: (5, 0), 10: (6, -1), 11: (6, 0)},
         True: {0: (0, 0), 1: (1, -1), 2: (1, 0), 3: (2, 0), 4: (2, 1), 5: (3, 0), 6: (3, 1), 7: (4, 0), 8: (5, 0), 9: (5, 1), 10: (6, 0), 11: (6, 0)}}
ROMANI = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII')
NOMI_IT = {'C': 'Do', 'D': 'Re', 'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'A': 'La', 'B': 'Si'}
SETTIME = ('7', 'o7', 'ø', 'S')
RIVOLTI = {False: ('', '6', '64'), True: ('7', '65', '43', '42')}


def nome_it(nome):
    """'E-' -> 'Mib', 'F#' -> 'Fa#'"""
    return NOMI_IT[nome[0]] + nome[1:].replace('-', 'b')


@dataclass
class Armonia:
    prima: Segmento
    ultima: Segmento
    fine: Fraction
    tonica: int          # tonalità del segmento (per progressioni)
    lettera: int         # lettera della tonica (0 = Do)
    minore: bool
    radice: int          # classe di altezza assoluta
    lett_radice: int
    nome_radice: str     # ortografia music21 della radice
    qual: str            # M m d A | 7 o7 ø S | +6
    rivolto: int
    tipo: str = ''       # napoletana | sesta italiana/francese/tedesca
    fermata: bool = False
    k_tonica: int | None = None    # tonalità effettiva (aggiornata dalle modulazioni)
    k_minore: bool | None = None
    k_nome: str | None = None

    @property
    def t(self): return self.tonica if self.k_tonica is None else self.k_tonica
    @property
    def m(self): return self.minore if self.k_minore is None else self.k_minore
    @property
    def nome_tonica(self): return self.prima.tonalita.tonic.name if self.k_nome is None else self.k_nome
    @property
    def inizio(self): return self.prima.inizio
    @property
    def rel(self): return (self.radice - self.t) % 12
    @property
    def grado(self): return (self.lett_radice - self.lettera) % 7
    @property
    def basso(self): return self.ultima.eventi['B'].pitch
    @property
    def sopra(self): return self.ultima.eventi['S'].pitch
    @property
    def brel(self): return (self.basso.pitchClass - self.t) % 12
    @property
    def srel(self): return (self.sopra.pitchClass - self.t) % 12
    @property
    def certa(self): return self.prima.centro_certo
    @property
    def chiave(self): return (self.prima.identita, self.basso.pitchClass, self.tipo, self.tonica, self.minore)

    def dominante(self): return (self.rel == 7 and self.qual in ('M', '7')) or (self.rel == 11 and self.qual in ('d', 'ø', 'o7'))
    def tonico(self): return self.rel == 0 and self.qual in ('M', 'm')
    def sesta(self): return self.tipo.startswith('sesta')
    def pcs(self): return {p.pitchClass for p in self.prima.strutturali.values()}

    @property
    def nome(self): return self.nome_in(self.t, self.m)

    def nome_in(self, tonica, minore):
        """Sigla leggibile rispetto a una tonalità: V, ii6, vii°, bII6, sesta tedesca ..."""
        if self.sesta():
            return self.tipo
        gr, alt = GRADI[minore][(self.radice - tonica) % 12]
        num = ROMANI[gr]
        if self.qual in ('m', 'd', 'o7', 'ø'):
            num = num.lower()
        sigla = ('b' if alt < 0 else '#' if alt > 0 else '') + num + {'d': '°', 'o7': '°', 'ø': 'ø', 'A': '+'}.get(self.qual, '')
        return sigla + RIVOLTI[self.qual in SETTIME][self.rivolto if self.rivolto < len(RIVOLTI[self.qual in SETTIME]) else 0]


def _qual(c):
    r = c.root().pitchClass
    pcs = {(p.pitchClass - r) % 12 for p in c.pitches}
    if 4 in pcs and 10 in pcs: return '7'
    if 3 in pcs and 9 in pcs: return 'o7'
    if 3 in pcs and 6 in pcs and 10 in pcs: return 'ø'
    if pcs & {10, 11, 9}: return 'S'
    if 4 in pcs: return 'A' if 8 in pcs else 'M'
    if 3 in pcs: return 'd' if 6 in pcs else 'm'
    return 'S'


def _lettura(s, tonica, lettera, minore):
    """Armonia di un segmento o None se non riconosciuta."""
    sounding = {v: e.pitch for v, e in s.eventi.items() if e is not None and e.pitch is not None}
    if len(sounding) != 4:
        return None
    base = dict(prima=s, ultima=s, fine=s.fine, tonica=tonica, lettera=lettera, minore=minore,
                fermata=any(e.fermata and e.fine == s.fine for e in s.eventi.values() if e))
    b = sounding['B']
    if s.alterato:
        return Armonia(radice=b.pitchClass, lett_radice=LETTERE.index(b.step), nome_radice=b.name, qual='+6', rivolto=0, tipo=s.alterato, **base)
    c = s.accordo
    if c is not None:
        a = Armonia(radice=c.root().pitchClass, lett_radice=LETTERE.index(c.root().step), nome_radice=c.root().name,
                    qual=_qual(c), rivolto=c.inversion(), **base)
        if a.rel == 1 and a.qual == 'M':
            a.tipo = 'napoletana'
        return a
    # triade incompleta (quinta omessa) in stato fondamentale: radice e terza soltanto
    others = {p.pitchClass for v, p in s.strutturali.items() if v != 'B'} - {b.pitchClass}
    if len(others) == 1 and (third := (others.pop() - b.pitchClass) % 12) in (3, 4):
        return Armonia(radice=b.pitchClass, lett_radice=LETTERE.index(b.step), nome_radice=b.name,
                       qual='M' if third == 4 else 'm', rivolto=0, **base)
    return None


def armonie(analysis):
    """Armonie in ordine; None segna un tratto non riconosciuto (interrompe ogni confronto)."""
    names = Counter(s.tonalita.name for s in analysis.segmenti if s.funzione != 'dominante secondaria')
    prevalente = next((s.tonalita for s in analysis.segmenti if names and s.tonalita.name == names.most_common(1)[0][0]),
                      analysis.segmenti[0].tonalita)
    out = []
    for s in analysis.segmenti:
        k = prevalente if s.funzione == 'dominante secondaria' else s.tonalita
        a = _lettura(s, k.tonic.pitchClass, LETTERE.index(k.tonic.step), k.mode == 'minor')
        if a is None:
            if out and out[-1] is not None:
                out.append(None)
            continue
        if out and out[-1] is not None and out[-1].chiave == a.chiave and out[-1].fine == s.inizio and not out[-1].fermata:
            out[-1].fine, out[-1].ultima, out[-1].fermata = s.fine, s, a.fermata
        else:
            out.append(a)
    return out


def _vicine(a, b):
    return a is not None and b is not None and a.fine == b.inizio and not a.fermata


def _tratti(H, minimo):
    run = []
    for h in H:
        if h is None or (run and not _vicine(run[-1], h)):
            if len(run) >= minimo: yield run
            run = [] if h is None else [h]
        else:
            run.append(h)
    if len(run) >= minimo: yield run


def _pitch(h, voce, ultima):
    e = (h.ultima if ultima else h.prima).eventi[voce]
    return e.pitch if e else None


def _rel(p, tonica): return None if p is None else (p.pitchClass - tonica) % 12


# --- modulazioni -----------------------------------------------------------------------------

def _nome_chiave(nome, minore):
    return f'{nome_it(nome)} {"minore" if minore else "maggiore"}'


def _relazione(a_t, a_min, b_t, b_min):
    d = (b_t - a_t) % 12
    if a_min == b_min:
        return {7: 'dominante', 5: 'sottodominante'}.get(d)
    if not a_min:   # maggiore -> minore
        return {9: 'relativa', 4: 'relativa della dominante', 2: 'relativa della sottodominante'}.get(d)
    return {3: 'relativa', 10: 'relativa della dominante', 8: 'relativa della sottodominante'}.get(d)


def _diatonica(h, tonica, minore):
    return all((p - tonica) % 12 in SCALA[minore] for p in h.pcs())


def _romano(h, tonica, minore): return h.nome_in(tonica, minore)


def modulazioni(H, add, prog):
    for R in _tratti(H, 2):
        nome = R[0].prima.tonalita.tonic.name
        corrente = (R[0].tonica, R[0].minore)
        nomi = {corrente[0]: nome}
        for j in range(1, len(R)):
            c, p = R[j], R[j - 1]
            if (c.tonica, c.minore) != (p.tonica, p.minore):       # cambio di armatura/tonalità dichiarato
                nomi[c.tonica] = c.prima.tonalita.tonic.name
                _segnala(R, j, corrente, (c.tonica, c.minore), nomi, 'dichiarato', add, True)
                corrente = (c.tonica, c.minore)
                continue
            if p.qual not in ('M', '7') or c.qual not in ('M', 'm') or (c.radice - p.radice) % 12 != 5:
                continue
            if prog.get(id(p)) == 'reale' and prog.get(id(c)) == 'reale':   # il passo di una sequenza reale non è una cadenza
                continue
            nuova = (c.radice, c.qual == 'm')
            if nuova == corrente:
                continue
            # serve un'alterazione estranea al tono corrente nel V–I, altrimenti è solo I–IV, ii–V ecc.;
            # eccezione: dal minore alla relativa maggiore non occorre alcuna alterazione (resta da verificare)
            senza_alterazioni = _diatonica(p, *corrente) and _diatonica(c, *corrente)
            if senza_alterazioni and not (corrente[1] and nuova == ((corrente[0] + 3) % 12, False)):
                continue
            nomi[nuova[0]] = c.nome_radice
            dopo = R[j + 1:]
            # il nuovo tono si stabilisce se segue un accordo che il vecchio non contiene, oppure due accordi diatonici nel nuovo
            resta = bool(dopo) and ((_diatonica(dopo[0], *nuova) and not _diatonica(dopo[0], *corrente))
                                   or (len(dopo) >= 2 and all(_diatonica(h, *nuova) for h in dopo[:2])))
            preparata = j >= 2 and _diatonica(R[j - 2], *nuova)    # almeno un accordo del nuovo tono prima del V–I
            if resta or ((j == len(R) - 1 or c.fermata) and preparata):
                _segnala(R, j, corrente, nuova, nomi, 'cadenza', add, c.certa and not senza_alterazioni)
                corrente = nuova
                for h in R[j - 1:]:
                    h.k_tonica, h.k_minore, h.k_nome = nuova[0], nuova[1], c.nome_radice
            else:
                add('MO-TONICIZZAZIONE', c.prima, ('B',),
                    f'{_romano(p, *corrente)} – {_romano(c, *corrente)}: cadenza su {_nome_chiave(c.nome_radice, nuova[1])} senza permanenza nel nuovo tono.',
                    'Tonicizzazione (dominante secondaria): non è una modulazione se il discorso torna al tono d\'impianto.',
                    VERIFICARE, p.prima, 'osservazione')


def _segnala(R, j, vecchia, nuova, nomi, come, add, sicura):
    c = R[j]
    rel = _relazione(*vecchia, *nuova)
    # catena: armonie fino a j tutte diatoniche nel nuovo tono; pivot = la prima, se diatonica anche nel vecchio
    i0 = j
    while i0 > 0 and _diatonica(R[i0 - 1], *nuova):
        i0 -= 1
    # pivot = ultimo accordo comune alle due tonalità prima del primo accordo estraneo al vecchio tono
    f = next((k for k in range(i0, j + 1) if not _diatonica(R[k], *vecchia)), None)
    pivot = R[f - 1] if come == 'cadenza' and f is not None and f > i0 else None
    testo = (f'Modulazione da {_nome_chiave(nomi[vecchia[0]], vecchia[1])} a {_nome_chiave(nomi[nuova[0]], nuova[1])} '
             f'({"tono vicino: " + rel if rel else "tono non vicino"}); '
             + ('cambio di tonalità dichiarato nel file' if come == 'dichiarato'
                else f'confermata dalla cadenza {_romano(R[j - 1], *nuova)} – {_romano(c, *nuova)}'))
    if pivot is not None:
        testo += f'; pivot {_romano(pivot, *vecchia)} = {_romano(pivot, *nuova)}'
    origine = R[max(i0 - 1, 0)].prima
    add('MO-RILEVATA', c.prima, ('B',), testo + '.',
        'Confrontare con il testo: tono d\'arrivo, relazione con il tono d\'impianto e accordo pivot.',
        CONDIZIONATA if sicura else VERIFICARE, origine)
    if come == 'cadenza' and pivot is None:
        add('MO-PIVOT', c.prima, ('B',), 'Nessun accordo diatonico in entrambe le tonalità prima del primo accordo estraneo al tono d\'impianto.',
            'Modulazione diretta o pivot non riconosciuto: verificare il passaggio e la scelta dell\'accordo di collegamento.',
            VERIFICARE, origine, 'avvertimento')
    if not rel:
        add('MO-NONVICINO', c.prima, ('B',), f'{_nome_chiave(nomi[nuova[0]], nuova[1])} non è un tono vicino di {_nome_chiave(nomi[vecchia[0]], vecchia[1])}.',
            'Fuori dai toni vicini la modulazione richiede passaggi ulteriori; verificare le armature e il testo.',
            VERIFICARE, origine, 'osservazione')


# --- cadenze ---------------------------------------------------------------------------------

def _cadenza(p, c):
    """-> (nome, dettaglio, conclusiva) o None. p precede c."""
    if c.tonico() and p.dominante():
        dettagli = []
        if p.rel != 7: dettagli.append('accordo di sensibile al posto di V')
        if p.rivolto: dettagli.append('V non in stato fondamentale')
        if c.rivolto: dettagli.append('I non in stato fondamentale')
        if c.srel != 0: dettagli.append('soprano non sulla tonica')
        return ('cadenza perfetta', '', True) if not dettagli else ('cadenza imperfetta', '; '.join(dettagli), True)
    if c.tonico() and p.rel == 5 and p.qual in ('M', 'm'):
        return 'cadenza plagale', '', True
    if c.rel == 7 and c.qual in ('M', '7'):
        if c.m and p.rel == 5 and p.rivolto == 1 and p.qual == 'm' and p.brel == 8 and c.brel == 7:
            return 'cadenza frigia', 'iv6 – V con basso discendente di semitono', False
        return 'cadenza sospesa', '', False
    inganno = (c.m and c.rel == 8 and c.qual == 'M') or (not c.m and c.rel == 9 and c.qual == 'm')
    if p.dominante() and inganno:
        return "cadenza d'inganno", '', False
    if p.dominante():
        return 'cadenza evitata', f'dominante seguita da {c.nome}', False
    return None


def cadenze(H, add):
    ultimo = max((j for j, h in enumerate(H) if h is not None), default=-1)   # pause finali non interrompono la frase
    for j, c in enumerate(H):
        if c is None or not (j == ultimo or c.fermata):
            continue
        p = H[j - 1] if j else None
        if not _vicine(p, c):
            continue
        chiave = _nome_chiave(c.nome_tonica, c.m)
        r = _cadenza(p, c)
        if r is None:
            add('CA-FINALE', c.prima, ('S', 'B'), f'{p.nome} → {c.nome} chiude la frase senza formula cadenzale riconosciuta.',
                'Verificare se la frase deve concludere con una cadenza (V–I, IV–I, V–VI, ... –V).', VERIFICARE, p.prima)
            continue
        nome, dettaglio, conclusiva = r
        cad64 = j >= 2 and H[j - 2] is not None and H[j - 2].tonico() and H[j - 2].rivolto == 2 and p.rel == 7 and nome in ('cadenza perfetta', 'cadenza imperfetta')
        add('CA-TIPO', c.prima, ('S', 'B'),
            f'{nome}' + (f' ({dettaglio})' if dettaglio else '') + f': {p.nome} → {c.nome}' + (' (preceduta da I64 cadenziale)' if cad64 else '')
            + f' in {chiave}.',
            'Confrontare il tipo di cadenza con la collocazione nella frase e con quanto dichiarato nel testo.',
            CONDIZIONATA if c.certa else VERIFICARE, p.prima)
        if conclusiva and c.rivolto:
            add('CA-FINALE', c.prima, ('B',), f'Accordo di arrivo {c.nome} non in stato fondamentale.',
                'La chiusura definitiva richiede di norma la tonica in stato fondamentale.', VERIFICARE, p.prima)


# --- risoluzioni -----------------------------------------------------------------------------

def risoluzioni(H, add, prog):
    for a, b in zip(H, H[1:]):
        if not _vicine(a, b):
            continue
        da = lambda v: _pitch(a, v, True)
        verso = lambda v: _pitch(b, v, False)
        conf = CONDIZIONATA if a.certa else VERIFICARE
        if a.tipo == 'napoletana':
            if a.rivolto != 1:
                add('RS-NAPOLETANA', b.prima, ('B',), f'La napoletana è in {"stato fondamentale" if a.rivolto == 0 else "secondo rivolto"}.',
                    'La sesta napoletana si usa di norma in primo rivolto (II$\\flat$6).', VERIFICARE, a.prima, 'osservazione')
            if not ((b.dominante() and b.rel == 7) or (b.tonico() and b.rivolto == 2)):
                lieve = b.rel == 11
                add('RS-NAPOLETANA', b.prima, ('B',), f'{a.nome} è seguita da {b.nome} invece di V (o I64 poi V).',
                    'La sesta napoletana risolve su V (anche tramite I64) o, più raramente, sulla sensibile.',
                    VERIFICARE if lieve else conf, a.prima, 'osservazione' if lieve else 'errore')
            elif b.rel == 7:
                for v in 'SAT':
                    if _rel(da(v), a.t) == 1 and _rel(verso(v), a.t) != 11:
                        add('RS-NAPOLETANA', b.prima, (v,), 'La fondamentale della napoletana (II$\\flat$) non scende di terza diminuita alla sensibile.',
                            'Verificare la risoluzione melodica della voce con il II$\\flat$ (terza diminuita discendente).', VERIFICARE, a.prima, 'osservazione')
        elif a.sesta():
            if not ((b.rel == 7 and b.qual in ('M', '7')) or (b.tonico() and b.rivolto == 2)):
                add('RS-ECCEDENTE', b.prima, ('B',), f'{a.nome} è seguita da {b.nome} invece di V (o I64 poi V).',
                    'La sesta aumentata risolve per moto contrario sull\'ottava della dominante.', conf, a.prima, 'errore')
            else:
                if _rel(verso('B'), a.t) != 7:
                    add('RS-ECCEDENTE', b.prima, ('B',), 'Il basso (VI abbassato) non scende di semitono sulla dominante.',
                        'Il basso e il IV alzato convergono sulla dominante per moto contrario.', conf, a.prima, 'errore')
                for v in 'SAT':
                    if _rel(da(v), a.t) == 6 and _rel(verso(v), a.t) != 7:
                        add('RS-ECCEDENTE', b.prima, (v,), 'Il IV alzato non sale di semitono alla dominante.',
                            'La voce con il IV alzato risolve di semitono ascendente sulla dominante.', conf, a.prima, 'errore')
                if a.tipo == 'sesta tedesca' and b.rel == 7 and not b.tonico():
                    add('RS-ECCEDENTE', b.prima, ('B',), 'Sesta tedesca risolta direttamente su V: rischio di quinte parallele.',
                        'Di norma si passa per I64 (o si controllano le quinte fra basso e voce interna).', VERIFICARE, a.prima, 'osservazione')
        elif a.rel == 11 and a.qual in ('d', 'ø', 'o7'):
            if not (b.tonico() or b.rel in (8, 9) or b.dominante() or (id(a) in prog and id(b) in prog)):
                add('RS-SENSIBILE', b.prima, ('B',), f'{a.nome} è seguito da {b.nome}.',
                    'L\'accordo di sensibile risolve di norma sulla tonica (o sul VI per inganno, o su V).', VERIFICARE, a.prima, 'avvertimento')
        elif a.tonico() and a.rivolto == 2 and b.rel == 7 and b.brel == a.brel:
            # 6/4 cadenziale: la quarta (tonica) scende alla sensibile, la sesta alla quinta di V
            for v in 'SAT':
                x = _rel(da(v), a.t)
                if x in (0, 3, 4) and _rel(verso(v), a.t) != (11 if x == 0 else 2):
                    add('RS-64', b.prima, (v,), f'{"Quarta" if x == 0 else "Sesta"} del 6/4 cadenziale non risolve su V ({"quarta → terza" if x == 0 else "sesta → quinta"}).',
                        'Nel 6/4 cadenziale la sesta scende alla quinta e la quarta alla terza di V.', conf, a.prima, 'errore')


def ritardi(analysis, add):
    seg = analysis.segmenti
    by_start = {s.inizio: s for s in seg}
    for s in seg:
        if s.accordo is not None or s.alterato:
            continue
        sounding = {v: e.pitch for v, e in s.eventi.items() if e and e.pitch is not None}
        if len(sounding) != 4:
            continue
        for v in 'SAT':
            e = s.eventi[v]
            cambio = max(o.inizio for w, o in s.eventi.items() if w != v)   # le altre voci hanno cambiato dopo l'attacco di e
            if e.inizio >= cambio:
                continue
            resto = _accordo([p for w, p in sounding.items() if w != v])
            if resto is None or e.pitch.name in {p.name for p in resto.pitches}:
                continue
            events = analysis.partitura.linee[v]
            dopo = next((x for x in events[events.index(e) + 1:] if x.pitch is None or x.pitch != e.pitch), None)
            if dopo is None or dopo.pitch is None or dopo.inizio != e.fine or e.fermata:
                continue
            prima = by_start.get(e.inizio)
            preparato = prima is not None and prima.accordo is not None and e.pitch.name in {p.name for p in prima.accordo.pitches}
            passo = 1 <= abs(dopo.pitch.ps - e.pitch.ps) <= 2 and dopo.pitch.step != e.pitch.step
            ref = by_start.get(dopo.inizio, s)
            if passo and dopo.pitch.ps < e.pitch.ps:
                if not preparato:
                    add('RS-RITARDO', s, (v,), f'Ritardo {e.pitch.nameWithOctave} → {dopo.pitch.nameWithOctave} senza preparazione consonante osservabile.',
                        'Il ritardo si prepara con una nota consonante dell\'armonia precedente, tenuta sul tempo debole.', VERIFICARE, None, 'avvertimento')
            elif passo:
                add('RS-RITARDO', ref, (v,), f'Nota tenuta estranea {e.pitch.nameWithOctave} risolve verso l\'alto ({dopo.pitch.nameWithOctave}).',
                    'Ritardo ascendente (ammesso per la sensibile) o errore: verificare.', VERIFICARE, s, 'avvertimento')
            else:
                add('RS-RITARDO', ref, (v,), f'Nota tenuta estranea {e.pitch.nameWithOctave} non risolve per grado ({dopo.pitch.nameWithOctave}).',
                    'Il ritardo risolve per grado discendente sull\'armonia successiva.', CONDIZIONATA if s.centro_certo else VERIFICARE, s, 'errore')


# --- progressioni ----------------------------------------------------------------------------

PASSO = {1: 'seconde ascendenti', 6: 'seconde discendenti', 2: 'terze ascendenti', 5: 'terze discendenti',
         3: 'quarte ascendenti (quinte discendenti)', 4: 'quarte discendenti (quinte ascendenti)'}


def _moduli(R, i, L):
    """(numero di moduli di lunghezza L da i, passo diatonico) con passo costante e stessa presenza di settime."""
    if i + 2 * L > len(R): return 0, 0
    T = (R[i + L].grado - R[i].grado) % 7
    if T == 0: return 0, 0
    n = 1
    while i + (n + 1) * L <= len(R):
        if not all((R[i + n * L + m].grado - R[i + m].grado) % 7 == (n * T) % 7
                   and (R[i + n * L + m].qual in SETTIME) == (R[i + m].qual in SETTIME)
                   and R[i + n * L + m].tipo == R[i + m].tipo for m in range(L)):
            break
        n += 1
    return n, T


def progressioni(H, add):
    """-> {id(armonia): 'reale' | 'diatonica'} per le armonie comprese in una progressione"""
    span = {}
    for R in _tratti(H, 3):
        i = 0
        while i < len(R):
            best = None
            for L in (1, 2, 3, 4):
                n, T = _moduli(R, i, L)
                if n >= (4 if L == 1 else 3) and (best is None or n * L > best[0] * best[1]):
                    best = (n, L, T)
            if best is None:
                i += 1
                continue
            n, L, T = best
            mod, fine = R[i:i + L], R[i + n * L - 1]
            passo = (R[i + L].radice - R[i].radice) % 12
            reale = all((R[i + k * L + m].radice - R[i + m].radice) % 12 == k * passo % 12 and R[i + k * L + m].qual == R[i + m].qual
                        for k in range(n) for m in range(L))
            catena = ' – '.join(h.nome_in(h.tonica, h.minore) for h in R[i:i + n * L][:10]) + (' …' if n * L > 10 else '')
            add('PR-RILEVATA', fine.prima, ('B',),
                f'Progressione {"reale" if reale else "diatonica"} per {PASSO[T]}: modello di {L} accord{"i" if L > 1 else "o"} '
                f'ripetuto {n} volte ({catena})' + ('; modulante: il centro tonale si sposta a ogni modulo.' if reale else '; non modulante.'),
                'Confrontare con la dicitura del testo (tipo di progressione e numero di moduli).',
                CONDIZIONATA if mod[0].certa else VERIFICARE, R[i].prima)
            if L > 1:
                diversi = [k for k in range(1, n) if [R[i + k * L + m].rivolto for m in range(L)] != [h.rivolto for h in mod]]
                if diversi:
                    add('PR-IRREGOLARE', fine.prima, ('B',), f'I rivolti del modello non si ripetono nel modulo {diversi[0] + 1}.',
                        'Nelle progressioni il modello è di norma ripetuto con gli stessi rivolti; verificare se la variante è voluta.',
                        VERIFICARE, R[i].prima, 'avvertimento')
            for h in R[i:i + n * L]:
                span[id(h)] = 'reale' if reale else 'diatonica'
            i += n * L
    return span


def controlla_sintassi(analysis, add):
    H = armonie(analysis)
    prog = progressioni(H, add)
    modulazioni(H, add, prog)    # fissa la tonalità effettiva usata da cadenze e risoluzioni
    cadenze(H, add)
    risoluzioni(H, add, prog)
    ritardi(analysis, add)
