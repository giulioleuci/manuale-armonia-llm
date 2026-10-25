from doc import *
def pair(a, b, fa, ra, fb, rb, ann=None, bar=True):
    return [ch(a, fa, ra, conn=True, ann=ann), ch(b, fb, rb, bar=bar)]

# ---------- C major dominant
CM = {
 'root_c':  pair(['B4','D4','F3','G2'], ['C5','C4','E3','C3'], ['7'],'V7',[],'I', {'S':'sens.↑','T':'7ª↓'} ),
 'root_i':  pair(['B4','G4','F3','G2'], ['C5','G4','E3','C3'], ['7'],'V7',[],'I', {'S':'sens.↑','T':'7ª↓'}),
 'v65':     pair(['D5','F4','G3','B2'], ['C5','E4','G3','C3'], ['6','5'],'V6/5',[],'I', {'A':'7ª↓','B':'sens.↑'}),
 'v43':     pair(['B4','F4','G3','D3'], ['C5','E4','G3','C3'], ['4','3'],'V4/3',[],'I', {'S':'sens.↑','A':'7ª↓'}),
 'v2':      pair(['D5','G4','B3','F3'], ['C5','G4','C4','E3'], ['2'],'V2',['6'],'I6', {'T':'sens.↑','B':'7ª↓'}),
}
AM = {
 'root_c':  pair(['G#4','B3','D3','E2'], ['A4','A3','C3','A2'], ['7'],'V7',[],'i', {'S':'sens.↑','T':'7ª↓'}),
 'root_i':  pair(['G#4','E4','D3','E2'], ['A4','E4','C3','A2'], ['7'],'V7',[],'i', {'S':'sens.↑','T':'7ª↓'}),
 'v65':     pair(['B4','D4','E3','G#2'], ['A4','C4','E3','A2'], ['6','5'],'V6/5',[],'i', {'A':'7ª↓','B':'sens.↑'}),
 'v43':     pair(['G#4','D4','E3','B2'], ['A4','C4','E3','A2'], ['4','3'],'V4/3',[],'i', {'S':'sens.↑','A':'7ª↓'}),
 'v2':      pair(['B4','E4','G#3','D3'], ['A4','E4','A3','C3'], ['2'],'V2',['6'],'i6', {'T':'sens.↑','B':'7ª↓'}),
}
# ---------- leading-tone sevenths
VII_C = pair(['D5','A4','F3','B2'], ['C5','G4','E3','C3'], ['7'],'VII7',[],'I', {'S':'','A':'7ª↓','T':'↓'})
VII_A = pair(['D5','B4','F3','G#2'], ['C5','A4','E3','A2'], ['7'],'VII7',[],'i', {'S':'','T':'7ª↓','B':'sens.↑'})

# ---------- chains of sevenths (descending fifths)
def build(S_,A_,T_,B_, figs, rns, subs=None):
    out=[]
    for i in range(len(S_)):
        out.append(ch([S_[i],A_[i],T_[i],B_[i]], figs[i], rns[i], conn=(i<len(S_)-1), sub=(subs[i] if subs else None)))
    return out
CHAIN_C = build(['G5','F5','F5','E5','E5','D5','D5','C5'],
                ['B4','A4','A4','G4','G4','F4','F4','E4'],
                ['E4','E4','D4','D4','C4','C4','B3','C4'],
                ['C3','F3','B2','E3','A2','D3','G2','C3'],
                [['7'],['7'],['7'],['7'],['7'],['7'],['7'],[]],
                ['I7','IV7','VII7','III7','VI7','II7','V7','I'],
                ['completa','incompleta','completa','incompleta','completa','incompleta','completa','incompleta'])
CHAIN_A = build(['G5','F5','F5','E5','E5','D5','D5','C5'],
                ['A4','A4','G4','G4','F4','F4','E4','E4'],
                ['C4','C4','B3','B3','A3','A3','G#3','A3'],
                ['A2','D3','G2','C3','F3','B2','E3','A2'],
                [['7'],['7'],['7'],['7'],['7'],['7'],['7'],[]],
                ['I7','IV7','VII7','III7','VI7','II7','V7','i'],
                ['incompleta','completa','incompleta','completa','incompleta','completa','incompleta','completa'])
if __name__ == '__main__':
    for k,v in CM.items(): validate('CM '+k, v)
    for k,v in AM.items(): validate('Am '+k, v)
    validate('VII_C', VII_C); validate('VII_A', VII_A)
    validate('CHAIN_C', CHAIN_C); validate('CHAIN_A', CHAIN_A)
    print('fatto')
