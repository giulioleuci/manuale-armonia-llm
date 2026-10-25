#!/usr/bin/env python3
"""
Convert LilyPond examples from Capitoli/*.tex into structured Python data in tools/esempi_data.py
"""
import glob, os, re, json

KEY_ACC = {
    ('do', 'major'): 0, ('la', 'minor'): 0,
    ('sol', 'major'): 1, ('mi', 'minor'): 1,
    ('re', 'major'): 2, ('si', 'minor'): 2,
    ('la', 'major'): 3, ('fad', 'minor'): 3,
    ('mi', 'major'): 4, ('dod', 'minor'): 4,
    ('si', 'major'): 5, ('sold', 'minor'): 5,
    ('fa', 'major'): -1, ('re', 'minor'): -1,
    ('sib', 'major'): -2, ('sol', 'minor'): -2,
    ('mib', 'major'): -3, ('do', 'minor'): -3,
    ('lab', 'major'): -4, ('fa', 'minor'): -4,
    ('reb', 'major'): -5, ('sib', 'minor'): -5,
}

PITCH_BASE = {'do':'C', 're':'D', 'mi':'E', 'fa':'F', 'sol':'G', 'la':'A', 'si':'B'}
LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def parse_pitch_absolute(tok):
    tok = tok.strip('~()')
    m = re.match(r'^([a-z]+)([\',]*)(\d+)?(\.)?$', tok)
    if not m: return None
    name, oct_marks, dur, dot = m.groups()
    base = None
    alt = ''
    for p in ['sol', 'do', 're', 'mi', 'fa', 'la', 'si']:
        if name.startswith(p):
            base = PITCH_BASE[p]
            rest = name[len(p):]
            if rest in ('d', 'diesis'): alt = '#'
            elif rest in ('dd', 'doppiodiesis'): alt = '##'
            elif rest in ('b', 'bemolle'): alt = 'b'
            elif rest in ('bb', 'doppiobemolle'): alt = 'bb'
            elif rest == '': alt = ''
            else: return None
            break
    if not base: return None
    octv = 3
    for ch in oct_marks:
        if ch == "'": octv += 1
        elif ch == ',': octv -= 1
    return f'{base}{alt}{octv}'

def parse_relative_notes(body, default_oct=3):
    # parse \relative <ref> { ... }
    m_rel = re.search(r'\\relative\s+([a-z]+[\',]*)', body)
    if m_rel:
        ref_tok = m_rel.group(1)
        ref_p = parse_pitch_absolute(ref_tok)
        cur_oct = int(ref_p[-1]) if ref_p else default_oct
        cur_letter = ref_p[0] if ref_p else 'C'
    else:
        cur_oct = default_oct
        cur_letter = 'C'

    # clean commands
    clean = re.sub(r'\\(key\s+[a-z]+\s+\\[a-z]+|clef\s+[a-z]+|time\s+\d+/\d+|bar\s+"[^"]+"|relative\s+[a-z]+[\',]*|voiceOne|voiceTwo|passaggio)', ' ', body)
    tokens = clean.split()
    notes = []
    bar_next = False
    for tok in tokens:
        if tok == '|':
            if notes:
                notes[-1]['bar'] = True
            continue
        # handle chords <p1 p2>
        m_chord = re.findall(r'[a-z]+[\',]*', tok)
        if not m_chord: continue
        pitches = []
        for ptok in m_chord:
            m = re.match(r'^([a-z]+)([\',]*)(\d+)?(\.)?$', ptok)
            if not m: continue
            name, oct_marks, _, _ = m.groups()
            base = None; alt = ''
            for p in ['sol', 'do', 're', 'mi', 'fa', 'la', 'si']:
                if name.startswith(p):
                    base = PITCH_BASE[p]
                    rest = name[len(p):]
                    if rest in ('d', 'diesis'): alt = '#'
                    elif rest in ('dd', 'doppiodiesis'): alt = '##'
                    elif rest in ('b', 'bemolle'): alt = 'b'
                    elif rest in ('bb', 'doppiobemolle'): alt = 'bb'
                    elif rest == '': alt = ''
                    else: base = None
                    break
            if not base: continue
            # determine octave in relative mode
            prev_idx = LETTERS.index(cur_letter)
            new_idx = LETTERS.index(base)
            diff = new_idx - prev_idx
            if diff > 3: cur_oct -= 1
            elif diff < -3: cur_oct += 1
            for ch in oct_marks:
                if ch == "'": cur_oct += 1
                elif ch == ',': cur_oct -= 1
            cur_letter = base
            pitches.append(f'{base}{alt}{cur_oct}')
        if pitches:
            notes.append({'p': pitches, 'bar': False})
    return notes

def parse_key_acc(s):
    m = re.search(r'\\key\s+([a-z]+)\s+\\([a-z]+)', s)
    if m:
        root, mode = m.groups()
        return KEY_ACC.get((root, mode), 0)
    return 0

def extract_braced_groups(s):
    groups = []
    i = 0
    while i < len(s):
        if s[i] == '{':
            count = 1; j = i + 1
            while j < len(s) and count > 0:
                if s[j] == '{': count += 1
                elif s[j] == '}': count -= 1
                j += 1
            groups.append(s[i+1:j-1].strip())
            i = j
        else: i += 1
    return groups

def parse_voice_tokens(s):
    # tokenize notes, connection arrows, marks
    tokens = re.split(r'\s+', s.strip())
    notes = []
    is_arrow = False
    has_markup = None
    for tok in tokens:
        if not tok: continue
        if tok == '|' or '\\bar' in tok:
            if notes: notes[-1]['bar'] = True
            continue
        if '\\freccia' in tok or '\\glissando' in tok:
            is_arrow = True
            continue
        if 'markup' in tok or 'bold' in tok:
            continue
        # check if it is a pitch
        p = parse_pitch_absolute(tok)
        if p:
            notes.append({'p': p, 'conn': is_arrow, 'bar': False})
            is_arrow = False
    return notes

def parse_lyrics(s):
    # find quotes or tokens
    items = []
    tokens = re.findall(r'"([^"]*)"|(\S+)', s)
    for q, tok in tokens:
        val = q if q else tok
        # ignore pure duration tokens like 1, 2, 4
        if re.match(r'^\d+(\.)?$', val): continue
        # strip trailing digits
        val = re.sub(r'\d+(\.)?$', '', val)
        if val in ('\\lyricmode', '{', '}'): continue
        items.append(val)
    return items

def parse_figures(s):
    # e.g. <6 4>4, <6>, <7>, s1, etc.
    res = []
    matches = re.findall(r'<([^>]+)>\d*|s\d*|_', s)
    for m in matches:
        if m:
            figs = m.strip().split()
            res.append(figs)
        else:
            res.append([])
    return res

def convert_partilate(groups):
    global_s = groups[0]
    nacc = parse_key_acc(global_s)
    S_notes = parse_voice_tokens(groups[1])
    A_notes = parse_voice_tokens(groups[2])
    T_notes = parse_voice_tokens(groups[3])
    B_notes = parse_voice_tokens(groups[4])
    lyrics = parse_lyrics(groups[5])
    figures = parse_figures(groups[6])

    # pad or align
    n = max(len(S_notes), len(A_notes), len(T_notes), len(B_notes))
    # if lengths differ, pad with last
    def pad(lst):
        if not lst: return [{'p': 'C4', 'conn': False, 'bar': False}] * n
        while len(lst) < n:
            lst.append({'p': lst[-1]['p'], 'conn': False, 'bar': False})
        return lst[:n]

    S_notes = pad(S_notes)
    A_notes = pad(A_notes)
    T_notes = pad(T_notes)
    B_notes = pad(B_notes)

    chords = []
    for i in range(n):
        s_p = S_notes[i]['p']
        a_p = A_notes[i]['p']
        t_p = T_notes[i]['p']
        b_p = B_notes[i]['p']
        rn = lyrics[i] if i < len(lyrics) else ''
        fig = figures[i] if i < len(figures) else []
        conn = S_notes[i]['conn'] or A_notes[i]['conn'] or T_notes[i]['conn'] or B_notes[i]['conn'] or (i < n - 1)
        bar = S_notes[i]['bar'] or A_notes[i]['bar'] or T_notes[i]['bar'] or B_notes[i]['bar']
        chords.append({
            'v': [s_p, a_p, t_p, b_p],
            'rn': rn,
            'fig': fig,
            'conn': conn,
            'bar': bar
        })
    return {'type': 'satb', 'nacc': nacc, 'chords': chords}

def convert_single_staff(body):
    clef = 'bass' if r'\clef bass' in body else 'treble'
    nacc = parse_key_acc(body)
    notes = parse_relative_notes(body, default_oct=(2 if clef == 'bass' else 4))
    chords = []
    for n in notes:
        chords.append({
            'p': n['p'],
            'bar': n['bar'],
            'name': '',
            'rn': ''
        })
    return {'type': 'single', 'clef': clef, 'nacc': nacc, 'chords': chords}
