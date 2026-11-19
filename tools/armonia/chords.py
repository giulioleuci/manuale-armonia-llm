from .music import *

# qualita' -> intervalli (passi, semitoni) di 3a, 5a, (7a)
Q = {
 'M': [(2,4),(4,7)], 'm': [(2,3),(4,7)], 'd': [(2,3),(4,6)], 'A': [(2,4),(4,8)],
 '7': [(2,4),(4,7),(6,10)], 'M7': [(2,4),(4,7),(6,11)], 'm7': [(2,3),(4,7),(6,10)],
 'ø7': [(2,3),(4,6),(6,10)], 'o7': [(2,3),(4,6),(6,9)], 'mM7': [(2,3),(4,7),(6,11)], '+M7': [(2,4),(4,8),(6,11)],
}
def tones(root, q): return [root] + [spell_up(root, s, k) for s, k in Q[q]]

def spec(root, q, inv=0, mv=None, vmv=None, form=None, nodbl=(), free7=None, lt=None, bach=False):
    """Accordo: basso + opzioni per le 3 voci superiori (multiinsiemi con penalita').
    mv: {nota: 'down'|'up'|'hold'} per il passaggio al prossimo accordo; vmv: {voce: ...}.
    form: 'c' completo / 'i' incompleto (solo stato fondamentale).
    lt: sensibile della tonalita' (mai raddoppiata; se l'accordo seguente contiene la tonica sale di semitono,
        oppure, con bach=True, una voce interna puo' scendere di terza).
    Le triadi maggiori e minori in stato fondamentale possono essere incomplete (fondamentale triplicata,
    con penalita'); la triade diminuita mai."""
    t = tones(root, q); n = len(t)
    oth = tuple(t[:inv] + t[inv+1:])
    if n == 4:
        opts = []
        if form != 'i': opts.append((oth, 0))
        if inv == 0 and form != 'c': opts.append(((t[0], t[1], t[3]), 1.5))
    else:
        opts = [(oth + (x,), p) for x, p in zip(t, (0, 1.5, 1.2))]
        if inv == 0 and q in ('M', 'm') and form != 'c': opts.append(((t[0], t[0], t[1]), 4))
        if form == 'c': opts = [o for o in opts if t[2] in o[0] + (t[inv],)]
    # mai raddoppiate: sensibile, settima, quinta diminuita/eccedente (dissonante), terza della settima di dominante
    bad = set(nodbl) | ({t[3]} if n == 4 else set()) | ({lt} if lt else set())
    if q in ('d', 'ø7', 'o7', 'A', '+M7'): bad.add(t[2])
    if q == '7': bad.add(t[1])
    opts = [(o, p) for o, p in opts if all((o + (t[inv],)).count(b) < 2 for b in bad)]
    return dict(root=root, q=q, inv=inv, bass=t[inv], tones=t, sev=t[3] if n == 4 else None, ups=opts,
                mv=dict(mv or {}), vmv=dict(vmv or {}), free7=(q == '7') if free7 is None else free7, lt=lt, lt_up=spell_up(lt, 1, 1) if lt else None, bach=bach)

def diat(scale, d, sev):
    """accordo diatonico sul grado d (0..6) -> (radice, qualita')"""
    t = [scale[(d + 2*k) % 7] for k in range(4 if sev else 3)]
    iv = tuple((name_pc(t[k]) - name_pc(t[0])) % 12 for k in range(1, len(t)))
    return t[0], {(4,7): 'M', (3,7): 'm', (3,6): 'd', (4,7,10): '7', (4,7,11): 'M7', (3,7,10): 'm7', (3,6,10): 'ø7'}[iv]

def fig(sp):
    """cifratura sotto il pentagramma"""
    return ([['7'], ['6','5'], ['4','3'], ['2']] if sp['sev'] else [[], ['6'], ['6','4']])[sp['inv']]
def ann(s1, c1, lab):
    """etichette sulle frecce: lab = {nota: testo} per le note di s1 con regola di moto"""
    return {VN[k]: lab[pname(c1[k])] for k in range(4) if pname(c1[k]) in lab}
