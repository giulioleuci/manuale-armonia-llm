from data23 import *
TON = ['C','G','D','A','E','B','F#','Db','Ab','Eb','Bb','F']
SOL = {'C':'Do','D':'Re','E':'Mi','F':'Fa','G':'Sol','A':'La','B':'Si'}
def nice(n): return SOL[n[0]] + n[1:].replace('#','♯').replace('b','♭')
d = Doc('out/2_Sesta_napoletana.pdf', 'Sesta napoletana', 'Struttura · funzione · risoluzioni a 4 voci')

# ---------- pag 1
d.page('1. Struttura della sesta napoletana')
d.cols([
 'La <b>sesta napoletana</b> (II♭6) è la <b>triade maggiore costruita sul II grado abbassato</b> della scala, usata in <b>primo rivolto</b> (accordo di sesta: al basso sta la terza, cioè il IV grado). '
 'In La minore: Si♭–Re–Fa con Re al basso; in Do maggiore (accordo preso a prestito dal modo minore): Re♭–Fa–La♭ con Fa al basso.<br/><br/>'
 '<b>Funzione.</b> È un accordo <b>di sottodominante</b> (sostituisce il II6 o il IV): conduce alla dominante, direttamente o attraverso il 6/4 di cadenza (I6/4).',
 '<b>Regole di scrittura.</b><br/>'
 '• Si raddoppia di norma la <b>terza</b> (la nota al basso, IV grado); la fondamentale (II abbassato, “nota napoletana”) <b>non si raddoppia</b>.<br/>'
 '• La nota napoletana risolve <b>discendendo</b> alla sensibile (terza diminuita: Si♭→Sol♯ in La minore; Re♭→Si in Do maggiore) oppure si porta per grado alla nota seguente, mai verso l’alto con un salto di seconda eccedente.<br/>'
 '• La sesta (VI grado: Fa in La min.; La♭ in Do magg.) scende di grado sulla fondamentale della dominante: <b>evitare la seconda eccedente</b> Fa–Sol♯ (La min.) e La♭–Si (Do magg.).<br/>'
 '• Il basso sale di grado verso la dominante (Re→Mi; Fa→Sol).'])
_nb = [
 dict(p=['Db4','F4','Ab4'], name='II♭', sub='Do maggiore', sub2='stato fondamentale', bar=True),
 dict(p=['F4','Ab4','Db5'], name='II♭6', sub='Do maggiore', sub2='primo rivolto (al basso: Fa)', bar=True),
 dict(p=['Bb4','D5','F5'], name='II♭', sub='La minore', sub2='stato fondamentale', bar=True),
 dict(p=['D4','F4','Bb4'], name='II♭6', sub='La minore', sub2='primo rivolto (al basso: Re)', bar=True)]
_title = 'Costruzione: triade maggiore sul II♭ (stato fondamentale e primo rivolto)'
if PORTRAIT:
    d.blocks(_nb[:2], title=_title)
    d.blocks(_nb[2:])
else:
    d.blocks(_nb, title=_title, dx=140)
d.y -= 6
d.h('La sesta napoletana in tutte le tonalità')
rows = [['Tonalità','II♭ (fondamentale)','IV (al basso)','VI','Accordo II♭6 (dal basso)']]
for t in TON:
    r = spell_up(t,1,1); q = spell_up(t,3,5); s = spell_up(t,5,8)
    rows.append([nice(t)+' magg./min.', nice(r), nice(q), nice(s), f'{nice(q)} – {nice(s)} – {nice(r)}'])
half = (len(rows)-1)//2
def mk(rs): return [['Tonalità','II♭6 (dal basso)']] + [[r[0],r[4]] for r in rs]
if PORTRAIT:
    d.table(mk(rows[1:]), [170,300])
else:
    d.table(mk(rows[1:half+1]), [110,150], advance=False)
    d.table(mk(rows[half+1:]), [110,150], x=M+300)
d.p('La stessa sesta napoletana vale per la tonalità maggiore e per la minore omonima (es. Do maggiore e Do minore hanno II♭6 = Fa–La♭–Re♭). Nelle tonalità con molte alterazioni (Re♭, La♭, Mi♭) la grafia corretta richiede doppi bemolli o bemolli su note già alterate.', 'small')
# ---------- pag 3: minore
d.page('2. Risoluzione della sesta napoletana – La minore')
d.p('Esempi a 4 voci in La minore. La nota napoletana (Si♭) è affidata a una voce interna (baritono) e scende alla sensibile Sol♯ per terza diminuita; il basso Re sale a Mi; la sesta (Fa) scende a Mi; il Re raddoppiato scende a Si (verso V) o resta fermo come settima (verso V7).')
d.system(NA['N6_V'] + NA['N6_V7'], nacc=0, dx=95,
         caps=[(0,3,'i – II♭6 – V – i'),(4,7,'i – II♭6 – V7 – i (V7 incompleta)')], title='II♭6 → V')
d.y -= 4
d.system(NA['CAD'], nacc=0, dx=125,          caps=[(0,4,'i – II♭6 – i6/4 – V7 – i (risoluzione per mezzo del 6/4 di cadenza)')],
         title='II♭6 → 6/4 di cadenza → V7 → i')
d.p('Nella cadenza con il 6/4 il Si♭ del soprano scende al La (nota del 6/4) e poi al Sol♯ della dominante: la linea melodica La–Si♭–La–Sol♯–La.', 'small')
# ---------- pag 4: maggiore
d.page('3. Risoluzione della sesta napoletana – Do maggiore')
d.p('In tonalità maggiore la sesta napoletana è un accordo di prestito dal modo minore: richiede due alterazioni (Re♭ e La♭) che non sono in chiave. Le regole sono le stesse: la nota napoletana Re♭ scende a Si per terza diminuita, La♭ scende a Sol, il Fa al basso sale a Sol.')
d.system(NC['N6_V'] + NC['N6_V7'], nacc=0, dx=95,
         caps=[(0,3,'I – II♭6 – V – I'),(4,7,'I – II♭6 – V7 – I (V7 incompleta)')], title='II♭6 → V')
d.y -= 4
d.system(NC['CAD'], nacc=0, dx=125, caps=[(0,4,'I – II♭6 – I6/4 – V7 – I')], title='II♭6 → 6/4 di cadenza → V7 → I')
d.p('Nella V7 completa (Si–Re–Fa–Sol) l’ultima nota arriva dalla sesta del 6/4 che scende per grado (Do→Si); il Fa è la settima, che scende poi al Mi della tonica.', 'small')
# ---------- pag 5: quadro
d.page('4. Quadro riassuntivo e errori da evitare')
d.table([
 ['Voce / nota','La minore','Do maggiore','Movimento'],
 ['Basso (terza dell’accordo)','Re','Fa','sale di grado alla fondamentale della dominante (Mi / Sol)'],
 ['Nota napoletana (II♭)','Si♭','Re♭','scende alla sensibile (Sol♯ / Si): terza diminuita; mai raddoppiata'],
 ['Sesta (VI grado)','Fa','La♭','scende di grado alla fondamentale della dominante (Mi / Sol)'],
 ['Terza raddoppiata (basso + voce)','Re','Fa','resta ferma (come settima della V7) oppure scende alla terza/quinta della dominante (Si / Re)']],
 [190,110,110,330])
d.p('<b>Errori da evitare.</b>', 'body')
d.p('• Raddoppiare la nota napoletana (la fondamentale).<br/>• Seconda eccedente nella melodia: Fa→Sol♯ in La minore, La♭→Si in Do maggiore.<br/>• Quinte e ottave parallele con il basso quando II♭6 va direttamente a V.<br/>• Usare II♭6 in stato fondamentale come regola: la forma tipica e la più usata è il primo rivolto.', 'body')
d.p('<b>Forme collegate.</b> La sesta napoletana può precedere il 6/4 di cadenza (come negli esempi) oppure andare direttamente a V o V7; talvolta compare anche in stato fondamentale (II♭) o al secondo rivolto (II♭6/4) in contesti più liberi.', 'body')
d.save(); print('ok2')
