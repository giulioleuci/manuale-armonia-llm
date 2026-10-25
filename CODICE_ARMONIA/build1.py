from data1 import *
from scales import *
d = Doc('out/1_Accordi_di_settima.pdf', 'Accordi di settima', 'Struttura · collocazione nelle scale · risoluzioni · progressioni')

# ---------------- pagina 1
d.page('1. Che cos’è un accordo di settima')
d.cols([
 'L’accordo di settima si ottiene sovrapponendo <b>quattro suoni per terze</b>: fondamentale, terza, quinta e <b>settima</b>. '
 'La settima è un intervallo dissonante rispetto alla fondamentale: per questo l’accordo è <b>instabile</b> e tende a risolvere. '
 'Il tipo di accordo dipende dalla qualità della triade di base e dalla specie della settima (maggiore, minore, diminuita).',
 '<b>Regole fondamentali della condotta delle voci.</b><br/>'
 '• La <b>settima scende di grado</b> (di tono o di semitono) sulla nota che segue.<br/>'
 '• La <b>sensibile sale</b> alla tonica (quando è presente nell’accordo).<br/>'
 '• La settima di dominante (e la settima di sensibile) può essere attaccata <b>liberamente</b>; le altre settime, nello stile tradizionale, vanno <b>preparate</b>: la nota che diventa settima è già presente, come consonanza, nella stessa voce dell’accordo precedente.<br/>'
 '• In 4 voci l’accordo può essere <b>completo</b> o <b>incompleto</b> (quinta omessa, fondamentale raddoppiata).'])
d.h('Le sei specie di accordi di settima (costruite su Do)')
blocks = [
 dict(p=['C4','E4','G4','Bb4'], name='7ª di dominante', sub='3ª magg. + 3ª min. + 3ª min.', bar=True),
 dict(p=['C4','E4','G4','B4'], name='7ª maggiore', sub='3ª magg. + 3ª min. + 3ª magg.', bar=True),
 dict(p=['C4','Eb4','G4','Bb4'], name='7ª minore', sub='3ª min. + 3ª magg. + 3ª min.', bar=True),
 dict(p=['C4','Eb4','Gb4','Bb4'], name='7ª semidiminuita', sub='3ª min. + 3ª min. + 3ª magg.', bar=True),
 dict(p=['C4','Eb4','Gb4','Bbb4'], name='7ª diminuita', sub='3ª min. + 3ª min. + 3ª min.', bar=True),
 dict(p=['C4','Eb4','G4','B4'], name='7ª minore-maggiore', sub='3ª min. + 3ª magg. + 3ª magg.', bar=True),
]
if PORTRAIT:
    d.blocks(blocks[:3])
    d.blocks(blocks[3:])
else:
    d.blocks(blocks, dx=118)
d.p('Nota: 3ª magg. = terza maggiore (4 semitoni), 3ª min. = terza minore (3 semitoni). Le denominazioni “per specie” (prima, seconda, … specie) variano da un manuale all’altro; qui si usano i nomi per qualità, che sono univoci. '
    'Gli accordi più importanti in tonalità sono la <b>settima di dominante</b> (V7), la <b>settima di sensibile</b> (VII7: semidiminuita in modo maggiore, diminuita in minore armonica) e le settime dei gradi secondari (II7, VI7, …).', 'small')
d.y -= 6
d.h('Legenda dei fogli seguenti')
d.p('Ogni esempio è scritto a <b>4 voci in disposizione late</b> (parti late = voci distanziate, con più di un’ottava tra soprano e baritono): '
    'soprano e contralto nel pentagramma in chiave di violino, baritono (parte del tenore) e basso in chiave di basso. '
    'Le frecce colorate collegano la nota di ogni voce con la nota dell’accordo successivo e ne mostrano il moto (ascendente, discendente, nota tenuta).')
d.y -= 4
draw_legend(d.c, M, d.y - 8, PW - 2*M)

# ---------------- pagina 2
d.page('2. Collocazione degli accordi di settima nelle scale – 1')
d.p('Gli accordi di settima si formano sovrapponendo terze <b>restando nei suoni della scala</b>: a ogni grado corrisponde quindi un accordo di specie determinata. Le cifre romane indicano il grado; il simbolo accanto indica la specie.', 'body')
sp_major = {4:'di dominante', 6:'sett. di sensibile'}
def row(scale, sp):
    r = scale_row(SCALES[scale], sp)
    for x in r:
        if x['sub']=='magg. quinta ecc.': pass
    return r
d.blocks(row('Do maggiore', sp_major), title='Scala maggiore – Do maggiore', dx=100)
d.y -= 12
d.blocks(row('La minore naturale', {6:'tipo dominante'}), title='Scala minore naturale – La minore', dx=100)
d.p('<b>Osservazioni.</b> In modo maggiore le specie sono: maggiore (I, IV), minore (II, III, VI), di dominante (V), semidiminuita (VII). '
    'Nel minore naturale la dominante è <i>minore</i> (Vm7) e non ha la sensibile: per questo nella pratica tonale si ricorre alla scala armonica (pagina seguente).', 'small')

# ---------------- pagina 3
d.page('3. Collocazione degli accordi di settima nelle scale – 2')
d.blocks(row('La minore armonica', {4:'di dominante', 6:'sensibile (dim.)'}), title='Scala minore armonica – La minore (sol♯ = sensibile)', dx=100)
d.y -= 12
mel = scale_row(SCALES['La minore melodica (ascendente)'], {3:'tipo dominante', 4:'di dominante', 5:'semidiminuita', 6:'di sensibile'})
mel[2]['sub'] = 'magg. 5ª ecc.'; mel[0]['sub']='minore-maggiore'
d.blocks(mel, title='Scala minore melodica (forma ascendente) – La minore', dx=100)
d.y -= 4
d.p('<b>Quali accordi si usano di più.</b> Nel modo minore la tonalità si fonda sulla scala <b>armonica</b>: V7 (settima di dominante, con la sensibile sol♯) e VII7 (settima diminuita di sensibile) sono gli accordi caratteristici; '
    'molto frequente è anche II7 (settima semidiminuita) come accordo di preparazione alla dominante. '
    'Gli accordi con quinta eccedente (III7) e minore-maggiore (I7) sono rari e colorano il discorso armonico.', 'body')
d.table([
 ['Grado','Do maggiore','La min. naturale','La min. armonica','La min. melodica (asc.)'],
 ['I','7ª magg.','7ª min.','7ª min.-magg.','7ª min.-magg.'],['II','7ª min.','7ª semidim.','7ª semidim.','7ª min.'],
 ['III','7ª min.','7ª magg.','7ª 5ª ecc.','7ª 5ª ecc.'],['IV','7ª magg.','7ª min.','7ª min.','7ª dom.'],
 ['V','7ª dom.','7ª min.','7ª dom.','7ª dom.'],['VI','7ª min.','7ª magg.','7ª magg.','7ª semidim.'],
 ['VII','7ª semidim.','7ª dom.','7ª dim.','7ª semidim.']],
 [70,150,150,150,200])

# ---------------- pagina 4-5: dominante
def dom_page(title, intro, data, nacc, keyname):
    d.page(title)
    d.p(intro)
    d.system(data['root_c'] + data['root_i'] + data['v65'], nacc=nacc,
             caps=[(0,1,'V7 completa → I incompleta'),(2,3,'V7 incompleta → I completa'),(4,5,'V6/5 → I')], dx=118,
             title=f'Stato fondamentale e primo rivolto – {keyname}')
    d.y -= 6
    d.system(data['v43'] + data['v2'], nacc=nacc, caps=[(0,1,'V4/3 → I'),(2,3,'V2 → I6 (la settima al basso scende)')], dx=170,
             title=f'Secondo e terzo rivolto – {keyname}')
dom_page('4. Settima di dominante – Do maggiore',
 'La <b>settima di dominante</b> (Sol–Si–Re–Fa) è una triade maggiore con settima minore sul V grado. Contiene il <b>tritono</b> Si–Fa (sensibile e settima), che risolve per moto contrario: '
 'Si sale a Do, Fa scende a Mi. La quinta (Re) può scendere a Do o restare ferma; la fondamentale resta ferma o segue il basso. '
 'Regola pratica: V7 <b>completa</b> → I <b>incompleta</b> (fondamentale triplicata, senza quinta); V7 <b>incompleta</b> (quinta omessa, fondamentale raddoppiata) → I <b>completa</b>.',
 CM, 0, 'Do maggiore')
dom_page('5. Settima di dominante – La minore (scala armonica)',
 'In La minore la settima di dominante è Mi–Sol♯–Si–Re. La <b>sensibile Sol♯</b> deve salire a La (non può scendere né restare); la settima Re scende a Do. '
 'Le regole sono le stesse del modo maggiore: la risoluzione avviene sull’accordo di tonica minore (La–Do–Mi). '
 'Nel secondo rivolto (4/3) il basso Si scende a La; nel terzo rivolto (2) il basso Re scende a Do e l’accordo si risolve sul primo rivolto di tonica (i6).',
 AM, 0, 'La minore')

# ---------------- pagina 6: sensibile
d.page('6. Settima di sensibile (VII grado)')
d.p('La <b>settima di sensibile</b> si forma sul VII grado: in modo maggiore è <b>semidiminuita</b> (Si–Re–Fa–La), in minore armonica è <b>diminuita</b> (Sol♯–Si–Re–Fa). '
    'È un accordo di funzione dominantica: contiene la sensibile e la settima (tritono). Risolve sulla tonica: la sensibile sale, la settima scende di grado, '
    'le altre due note scendono di grado (o, nella diminuita, possono salire). Può essere attaccata liberamente.')
d.system(VII_C + VII_A, nacc=0, caps=[(0,1,'Do maggiore: VII7 (semidim.) → I'),(2,3,'La minore: VII7 (dim.) → i')], dx=110,
         title='Settima di sensibile in stato fondamentale')
d.y -= 4
d.p('Nel VII7 semidiminuito → I il basso Si sale a Do, la settima La scende a Sol, la quinta Fa scende a Mi e la terza Re scende a Do (tonica completa con fondamentale raddoppiata). '
    'Nel VII7 diminuito → i il basso Sol♯ sale a La, la settima Fa scende a Mi, la quinta Re scende a Do e la terza Si scende a La. '
    'Nei rivolti valgono gli stessi movimenti obbligati (sensibile ↑, settima ↓); occorre solo controllare, caso per caso, di non produrre quinte o ottave parallele.', 'small')

# ---------------- pagina 7: progressioni
d.page('7. Progressione di settime per quinte discendenti')
d.p('Quando gli accordi di settima si succedono per <b>quinte discendenti</b> (o quarte ascendenti), la settima di ogni accordo è <b>preparata</b> dalla terza dell’accordo precedente e scende alla terza del successivo. '
    'Le voci seguono uno schema costante: la settima scende di grado, la quinta scende di grado sulla fondamentale seguente, la terza resta ferma e diventa settima. '
    'Per questo gli accordi si alternano <b>completo / incompleto</b> (quinta omessa e fondamentale raddoppiata). Nel basso il tritono fa–si è inevitabile nella scala diatonica.')
d.system(CHAIN_C, nacc=0, dx=88, title='Do maggiore: I7 – IV7 – VII7 – III7 – VI7 – II7 – V7 – I')
d.y -= 6
d.system(CHAIN_A, nacc=0, dx=88, title='La minore: I7 – IV7 – VII7 – III7 – VI7 – II7 – V7 – i')

# ---------------- pagina 8: riepilogo
d.page('8. Quadro riassuntivo: settima di dominante e suoi rivolti')
d.table([
 ['Stato','Cifratura','Basso','Risoluzione delle voci (Do maggiore)','Accordo di arrivo'],
 ['Fondamentale','7','Sol (fondamentale)','Si↑Do (sensibile) · Fa↓Mi (settima) · Re↓Do o ferma · Sol↑Do (basso)','I (tonica incompleta se V7 completa; completa se V7 incompleta)'],
 ['1° rivolto','6/5','Si (terza, sensibile)','Si↑Do (basso) · Fa↓Mi (settima) · Re↓Do · Sol ferma','I completa'],
 ['2° rivolto','4/3','Re (quinta)','Re↓Do (basso) · Si↑Do · Fa↓Mi · Sol ferma','I completa'],
 ['3° rivolto','2','Fa (settima)','Fa↓Mi (basso, la settima scende) · Si↑Do · Re↓Do · Sol ferma','I6 (primo rivolto di tonica)'],
], [90,60,120,330,170])
d.p('<b>Errori da evitare.</b> Quinte e ottave parallele tra due voci qualsiasi; sensibile che non sale (salvo quando è in una voce interna e il suo salto di terza verso la quinta serve per completare la tonica); settima che non scende; incroci tra le voci.', 'body')
d.p('<b>Trasposizione.</b> Tutti gli esempi si trasportano in qualsiasi tonalità mantenendo la stessa condotta delle voci: cambiano soltanto i nomi delle note e le alterazioni in chiave.', 'body')
d.save()
print('ok')
