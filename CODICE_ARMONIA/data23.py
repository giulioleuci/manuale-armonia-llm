from doc import *
def seq(vs, labels, caps_conn=None):
    """labels: list of (fig list, rn, sub, ann) ; connect all consecutive except where bar"""
    out = []
    for i,(v,l) in enumerate(zip(vs,labels)):
        fig, rn, sub, ann = (list(l)+[None]*4)[:4]
        out.append(ch(v, fig or [], rn, conn=(i < len(vs)-1), ann=ann, sub=sub))
    return out
def endgroup(lst):
    lst[-1]['conn'] = False; lst[-1]['bar'] = True
    return lst

# ================= SESTA NAPOLETANA =================
NA = {
 'N6_V': endgroup(seq([['E5','A4','C4','A2'],['D5','F4','Bb3','D3'],['B4','E4','G#3','E3'],['C5','E4','A3','A2']],
        [([],'i','',None),(['6'],'II♭6','',{'T':'3ª dim.↓','S':''}),([],'V','',None),([],'i','',None)])),
 'N6_V7': endgroup(seq([['E5','A4','C4','A2'],['D5','F4','Bb3','D3'],['D5','E4','G#3','E3'],['C5','E4','A3','A2']],
        [([],'i','',None),(['6'],'II♭6','',{'T':'3ª dim.↓'}),(['7'],'V7','incompleta',None),([],'i','',None)])),
 'CAD': seq([['A4','C4','E3','A2'],['Bb4','D4','F3','D3'],['A4','C4','E3','E2'],['G#4','B3','D3','E2'],['A4','C4','C3','A2']],
        [([],'i','',None),(['6'],'II♭6','',{'S':'↑ 2ª'}),(['6','4'],'i6/4','(cadenziale)',None),(['7'],'V7','',None),([],'i','',None)]),
}
NC = {
 'N6_V': endgroup(seq([['C5','E4','G3','C3'],['Db5','F4','Ab3','F2'],['B4','D4','G3','G2'],['C5','E4','G3','C3']],
        [([],'I','',None),(['6'],'II♭6','',{'S':'3ª dim.↓'}),([],'V','',None),([],'I','',None)])),
 'N6_V7': endgroup(seq([['C5','E4','G3','C3'],['Db5','F4','Ab3','F2'],['B4','F4','G3','G2'],['C5','E4','G3','C3']],
        [([],'I','',None),(['6'],'II♭6','',{'S':'3ª dim.↓','A':'7ª'}),(['7'],'V7','incompleta',None),([],'I','',None)])),
 'CAD': seq([['C5','E4','G3','C3'],['Db5','F4','Ab3','F2'],['C5','E4','G3','G2'],['B4','D4','F3','G2'],['C5','C4','E3','C3']],
        [([],'I','',None),(['6'],'II♭6','',None),(['6','4'],'I6/4','(cadenziale)',None),(['7'],'V7','',None),([],'I','',None)]),
}
# ================= SESTE ECCEDENTI =================
EA = {
 'IT': endgroup(seq([['E5','A4','C4','A3'],['D#5','A4','A3','F3'],['E5','G#4','B3','E3'],['E5','A4','C4','A3']],
        [([],'i','',None),(['♯6'],'6 ecc. it.','',{'S':'6ª ecc.↗8ª'}),([],'V','',None),([],'i','',None)])),
 'FR': endgroup(seq([['E5','A4','C4','A3'],['D#5','A4','B3','F3'],['E5','G#4','B3','E3'],['E5','A4','C4','A3']],
        [([],'i','',None),(['♯6','4','3'],'6 ecc. fr.','',{'S':''}),([],'V','',None),([],'i','',None)])),
 'GE': endgroup(seq([['E5','A4','C4','A3'],['D#5','A4','C4','F3'],['E5','A4','C4','E3'],['E5','G#4','B3','E3'],['E5','A4','C4','A3']],
        [([],'i','',None),(['♯6','5','3'],'6 ecc. ted.','',None),(['6','4'],'i6/4','',None),([],'V','',None),([],'i','',None)])),
}
EC = {
 'IT': endgroup(seq([['G4','C4','E3','C3'],['F#4','C4','C3','Ab2'],['G4','B3','D3','G2'],['G4','C4','E3','C3']],
        [([],'I','',None),(['♯6'],'6 ecc. it.','',None),([],'V','',None),([],'I','',None)])),
 'FR': endgroup(seq([['G4','C4','E3','C3'],['F#4','C4','D3','Ab2'],['G4','B3','D3','G2'],['G4','C4','E3','C3']],
        [([],'I','',None),(['♯6','4','3'],'6 ecc. fr.','',None),([],'V','',None),([],'I','',None)])),
 'GE': endgroup(seq([['G4','C4','E3','C3'],['F#4','C4','Eb3','Ab2'],['G4','C4','E3','G2'],['G4','B3','D3','G2'],['G4','C4','E3','C3']],
        [([],'I','',None),(['♯6','5','3'],'6 ecc. ted.','',None),(['6','4'],'I6/4','',{'T':'♭3→♮3'}),([],'V','',None),([],'I','',None)])),
}
GE_BAD = seq([['D#5','A4','C4','F3'],['E5','G#4','B3','E3']],[(['♯6','5','3'],'6 ecc. ted.','',None),([],'V','',None)])
GE_BAD[-1]['bar']=True
if __name__=='__main__':
    for nm,dd in (('NA',NA),('NC',NC),('EA',EA),('EC',EC)):
        for k,v in dd.items(): validate(nm+' '+k, v)
    validate('GE_BAD', GE_BAD)
