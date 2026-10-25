from data23 import *
TON = ['C','G','D','A','E','B','F#','Db','Ab','Eb','Bb','F']
SOL = {'C':'Do','D':'Re','E':'Mi','F':'Fa','G':'Sol','A':'La','B':'Si'}
def nice(n): return SOL[n[0]] + n[1:].replace('#','♯').replace('b','♭')
d = Doc('out/3_Seste_eccedenti.pdf', 'Seste eccedenti', 'Italiana · tedesca · francese – struttura e risoluzioni a 4 voci')

d.page('1. Struttura delle seste eccedenti')
d.cols([
 'La <b>sesta eccedente</b> è un accordo cromatico che contiene l’intervallo di sesta eccedente tra il <b>VI grado abbassato</b> (al basso) e il <b>IV grado alzato</b>. '
 'In La minore: Fa – Re♯ (la sesta Fa–Re♯ misura 10 semitoni, come una settima minore, ma è scritta come sesta). '
 'Per <b>moto contrario</b> i due suoni si allargano fino all’<b>ottava sul V grado</b>: il basso scende di semitono (Fa→Mi), la voce superiore sale di semitono (Re♯→Mi).<br/><br/>'
 '<b>Funzione.</b> Accordo di preparazione alla dominante (predominante): risolve sul V, direttamente o passando per il 6/4 di cadenza.',
 '<b>Le tre specie</b> (in La minore, con Fa al basso):<br/>'
  '• <b>Italiana</b> (6 ecc. it.): VI♭ – I – IV♯ → Fa–La–Re♯ (tre suoni: si raddoppia la tonica La).<br/>'
  '• <b>Tedesca</b> (6 ecc. ted.): VI♭ – I – III♭ – IV♯ → Fa–La–Do–Re♯.<br/>'
  '• <b>Francese</b> (6 ecc. fr.): VI♭ – I – II – IV♯ → Fa–La–Si–Re♯ (cifratura ♯6 4 3).<br/>'
  'In tonalità maggiore si usano gli stessi accordi con il VI grado abbassato (Do maggiore: La♭, Do, Mi♭ o Re, Fa♯).<br/>'
  'Non si raddoppiano né il VI♭ né il IV♯: sono le note caratteristiche, che devono risolvere in semitono.'])
d.blocks([
 dict(p=['F4','A4','D#5'], name='6 ecc. it.', sub='italiana', sub2='VI♭ · I · IV♯', bar=True),
 dict(p=['F4','A4','B4','D#5'], name='6 ecc. fr.', sub='francese', sub2='VI♭ · I · II · IV♯', bar=True),
 dict(p=['F4','A4','C5','D#5'], name='6 ecc. ted.', sub='tedesca', sub2='VI♭ · I · III♭ · IV♯', bar=True)],
 title='La minore', dx=150)
d.y -= 4
d.blocks([
 dict(p=['Ab4','C5','F#5'], name='6 ecc. it.', sub='italiana', sub2='VI♭ · I · IV♯', bar=True),
 dict(p=['Ab4','C5','D5','F#5'], name='6 ecc. fr.', sub='francese', sub2='VI♭ · I · II · IV♯', bar=True),
 dict(p=['Ab4','C5','Eb5','F#5'], name='6 ecc. ted.', sub='tedesca', sub2='VI♭ · I · III♭ · IV♯', bar=True)],
 title='Do maggiore (VI grado abbassato: La♭)', dx=150)
d.page('1. (segue) – Le seste eccedenti in tutte le tonalità')
rows = []
for t in TON:
    rows.append([nice(t), nice(spell_up(t,5,8)), nice(t), nice(spell_up(t,2,3)), nice(spell_up(t,1,2)), nice(spell_up(t,3,6))])
hdr = ['Tonalità','VI♭ (basso)','I','III♭ (solo ted.)','II (solo fr.)','IV♯']
if PORTRAIT:
    d.table([hdr]+rows, [70,80,40,100,90,50])
else:
    d.table([hdr]+rows[:6], [70,80,40,100,90,50], advance=False)
    d.table([hdr]+rows[6:], [70,80,40,100,90,50], x=M+420)
d.p('Italiana = VI♭ · I · IV♯ &nbsp;&nbsp; Francese = VI♭ · I · II · IV♯ &nbsp;&nbsp; Tedesca = VI♭ · I · III♭ · IV♯. Le note valgono sia per la tonalità maggiore sia per la minore omonima.', 'small')

d.page('2. Risoluzione delle seste eccedenti – La minore')
d.p('Il basso Fa scende a Mi; il Re♯ (qui al soprano) sale a Mi: i due suoni formano così un’ottava (doppia ottava, perché la sesta eccedente è scritta in forma composta). '
    'Italiana: la tonica raddoppiata si divide (La→Sol♯ e La→Si). Francese: La→Sol♯, Si resta ferma. Tedesca: passa per il 6/4 di cadenza: Do e La restano fermi, Re♯ e Fa si portano a Mi; poi La→Sol♯ e Do→Si.')
d.system(EA['IT'] + EA['FR'], nacc=0, dx=88, caps=[(0,3,'i – 6 ecc. it. – V – i'),(4,7,'i – 6 ecc. fr. – V – i')], title='Sesta italiana e sesta francese → V')
d.y -= 2
d.system(EA['GE'], nacc=0, dx=125, caps=[(0,4,'i – 6 ecc. ted. – i6/4 – V – i')], title='Sesta tedesca → 6/4 di cadenza → V')

d.page('3. Risoluzione delle seste eccedenti – Do maggiore')
d.p('In Do maggiore le seste eccedenti sono formate sul La♭ (VI grado abbassato): La♭–Fa♯ si allargano a Sol–Sol. Nella tedesca il Mi♭ sale a Mi♮ nel passaggio al 6/4 di tonica maggiore.')
d.system(EC['IT'] + EC['FR'], nacc=0, dx=88, caps=[(0,3,'I – 6 ecc. it. – V – I'),(4,7,'I – 6 ecc. fr. – V – I')], title='Sesta italiana e sesta francese → V')
d.y -= 2
d.system(EC['GE'], nacc=0, dx=125, caps=[(0,4,'I – 6 ecc. ted. – I6/4 – V – I')], title='Sesta tedesca → 6/4 di cadenza → V')

d.page('4. Errori da evitare e quadro riassuntivo')
d.p('<b>Sesta tedesca che risolve direttamente sulla dominante.</b> I movimenti Fa→Mi (basso) e Do→Si formano quinte parallele (Fa–Do → Mi–Si). Per evitarle si passa per il 6/4 di cadenza, come negli esempi precedenti.')
d.system(GE_BAD, nacc=0, dx=150, x1=M+14+420, marks=[(0,2,3,'5ª'),(1,2,3,'5ª')], title='Da evitare: 6 ecc. ted. → V (quinte parallele tra baritono e basso)')
d.y -= 4
d.table([
 ['Specie','Note (La minore)','Cifratura','Risoluzione'],
 ['Italiana','Fa – La – Re♯ (La raddoppiato)','♯6','Fa→Mi · Re♯→Mi · La→Sol♯ · La→Si : V completa'],
 ['Francese','Fa – La – Si – Re♯','♯6 4 3','Fa→Mi · Re♯→Mi · La→Sol♯ · Si ferma : V completa'],
 ['Tedesca','Fa – La – Do – Re♯','♯6 5 3','Fa→Mi · Re♯→Mi · La ferma · Do ferma : i6/4; poi La→Sol♯, Do→Si : V']],
 [80,200,70,420])
d.p('<b>Regole generali.</b> La sesta eccedente risolve per moto contrario verso l’ottava sul V; il basso scende di semitono; il IV♯ sale di semitono; non si raddoppiano le note caratteristiche (VI♭ e IV♯); la forma tipica ha il VI♭ al basso.', 'body')
d.save(); print('ok3')
