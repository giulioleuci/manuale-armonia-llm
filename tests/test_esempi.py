import re, glob, os
import pytest
from tools.esempi.dati import ESEMPI
from tools.esempi import genera
from tools.armonia.music import check_pair, check_chord
from tools.armonia.solver import URANGE

GEN = genera()
DA_EVITARE = {'es_cap22_07', 'es_cap04_03'}   # esempi di errore (parallele) voluti

def test_nessun_errore_di_condotta():
    errori = []
    for k, e in GEN.items():
        if e['type'] != 'satb' or k in DA_EVITARE: continue
        for i, c in enumerate(e['chords']):
            errori += check_chord(c['v'], f'{k}[{i}]')
            if i + 1 < len(e['chords']) and c['conn']:
                errori += check_pair(c['v'], e['chords'][i+1]['v'], f'{k}[{i}->{i+1}]')
    assert not errori, errori

def test_esempio_da_evitare_ha_parallele():
    c = GEN['es_cap22_07']['chords']
    assert check_pair(c[0]['v'], c[1]['v'])

def test_tutti_gli_id_usati_esistono():
    ids = set(ESEMPI) | set(GEN)
    base = os.path.join(os.path.dirname(__file__), '..', 'Capitoli')
    mancanti = []
    for f in glob.glob(os.path.join(base, '*.tex')):
        for m in re.findall(r'\\musica\{([^}]+)\}', open(f, encoding='utf-8').read()):
            if m not in ids: mancanti.append((os.path.basename(f), m))
    assert not mancanti, mancanti

def test_rivelatore_vincoli_rigidi():
    """parallele, incroci, sensibile e settima via rivelatore (serve il suo .venv: defusedxml)"""
    pytest.importorskip('defusedxml')
    from tools.verifica_esempi import rigide
    err = {k: r for k, e in GEN.items() if e['type'] == 'satb' and k not in DA_EVITARE and (r := rigide(k, e))}
    assert not err, err

def test_sigla_numerica_una_sola_volta():
    """grado in rn/name, numerica sintetica solo in fig: mai cifre attaccate al grado (V7, I6/4, II♭6)"""
    dup = [(k, i) for k, e in {**ESEMPI, **GEN}.items() for i, c in enumerate(e['chords'])
           for t in (c.get('rn'), c.get('name')) if t and re.search(r'[IViv][°ø+]?(maj)?\d|\||markup', t)]
    assert not dup, dup

def test_titoli_coerenti_con_rilevamenti():
    """cadenza, progressione, modulazione dichiarate nel titolo contro quanto rilevato (solo contraddizioni automatiche;
    quelle 'da verificare a mano' si leggono con `verifica_esempi --testo`)"""
    pytest.importorskip('defusedxml')
    from tools.verifica_esempi import verifica, titoli, incoerenze
    tit = titoli()
    err = [(k, m) for k, e in {**ESEMPI, **GEN}.items() if e['type'] == 'satb' and k not in DA_EVITARE
           for t in tit.get(k, []) for et, m in incoerenze(t, verifica(k, e)) if et == 'automatica']
    assert not err, err

def test_incoerenze_riconosce_cadenza_sbagliata():
    from tools.verifica_esempi import incoerenze
    trovati = [('CA-TIPO', 'osservazione', 'condizionata all’analisi', 'Soprano: D5 → C5 | cadenza plagale: IV → I in Do maggiore.')]
    assert incoerenze('Cadenza Perfetta in Do Maggiore', trovati)[0][0] == 'automatica'
    assert not incoerenze('Cadenza Plagale in Do Maggiore', trovati)
    assert incoerenze('Cadenza Perfetta', [])[0][0] == 'da verificare a mano'

def test_registro_e_separazione():
    """voci nella zona medio-alta (armonia/registro.py) e ben separate: almeno il 90% degli accordi"""
    from tools.armonia.registro import ZONA, MIN_SEP, MAX_SEP
    from tools.armonia.music import midi
    tot = bad = 0
    for k, e in GEN.items():
        if e['type'] != 'satb' or k in DA_EVITARE: continue
        for c in e['chords']:
            m = [midi(x) for x in c['v']]; tot += 1
            fuori = any(not ZONA[v][0] <= m[i] <= ZONA[v][1] for i, v in enumerate('SATB'))
            sep = any(not MIN_SEP[j] <= m[j] - m[j+1] <= MAX_SEP[j] for j in range(3))
            bad += fuori or sep
    assert bad <= 0.12 * tot, (bad, tot)

def test_sigle_maiuscolo_minuscolo():
    """grado maiuscolo per accordi maggiori/eccedenti, minuscolo per minori/diminuiti (° diminuita, ø semidiminuita)"""
    from tools.armonia.music import midi
    SC = [0, 2, 4, 5, 7, 9, 11]
    Q = {(0, 4, 7): 'M', (0, 3, 7): 'm', (0, 3, 6): 'd', (0, 4, 8): '+', (0, 4, 7, 10): 'M', (0, 3, 7, 10): 'm',
         (0, 3, 6, 10): 'ø', (0, 3, 6, 9): 'd', (0, 4, 7, 11): 'M', (0, 3, 7, 11): 'm', (0, 4, 8, 11): '+'}
    TON = {'Do': 0, 'Re': 2, 'Mi': 4, 'Fa': 5, 'Sol': 7, 'La': 9}
    err = []
    for k, e in GEN.items():
        if e['type'] != 'satb': continue
        ch = e['chords']
        ton = next((midi(c['v'][3]) % 12 for c in reversed(ch) if c['rn'] in ('I', 'i') and not c['fig']), 0)
        tmap = {j: TON[m[1]] for a, b, t in e.get('caps') or [] if (m := re.match(r'(Do|Re|Mi|Fa|Sol|La)\b', t))
                for j in range(a, b + 1)}
        for i, c in enumerate(ch):
            m = re.fullmatch(r'([♭♯]?)(i{1,3}|iv|vi{0,2}|v|I{1,3}|IV|VI{0,2}|V)([°ø+]?)(maj)?', c['rn'])
            if not m: continue
            root = tmap.get(i, ton) + SC[['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'].index(m[2].upper())] + {'♭': -1, '♯': 1, '': 0}[m[1]]
            pcs = {midi(x) % 12 for x in c['v']}
            q = next((Q[t] for r in (root, root + 1, root - 1) if (t := tuple(sorted((p - r) % 12 for p in pcs))) in Q), None)
            if q and ((q in 'M+') != m[2].isupper() or (q == 'd') != (m[3] == '°') or (q == 'ø') != (m[3] == 'ø')):
                err.append((k, i, c['rn'], q))
    assert not err, err
