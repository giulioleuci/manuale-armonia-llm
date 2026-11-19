"""Trascrizione manuale di basso38.png e basso39.png; nessuna armonizzazione."""

from pathlib import Path

from .render_snippet import render_bass_exercises


def n(p, dur=1, **marks):
    return {'p': p, 'dur': dur, **marks}


BASSO_38 = [
    # Riga 1 dell'immagine: battute 1–4.
    [n('D3'), n('F#3', .5), n('D3', .5), n('A3', 2, tie=True)],
    [n('A3'), n('G3', tie=True), n('G3'), n('F#3', .5), n('D3', .5)],
    [n('E3', 2), n('D3'), n('D4', tie=True)],
    [n('D4'), n('C#4'), n('D4', .5), n('D3', .5), n('D4')],
    # Riga 2: battute 5–9.
    [n('G3'), n('C#4'), n('F#3'), n('B3')],
    [n('E3'), n('A3'), n('D3'), n('D4', tie=True)],
    [n('D4'), n('C#4', .5), n('A3', .5), n('G#3', .5), n('E3', .5), n('F#3', .5), n('G#3', .5)],
    [n('A3', .5), n('A2', .5), n('A3'), n('D3'), n('G#3')],
    [n('C#3'), n('F#3'), n('B2'), n('E3')],
    # Riga 3: battute 10–14.
    [n('A2'), n('A3', tie=True), n('A3'), n('Gn3', .5, acc=True), n('E3', .5)],
    [n('F#3', 2), n('E3'), n('E4')],
    [n('A3'), n('D4'), n('G3'), n('Cn4', acc=True)],
    [n('F#3'), n('B3'), n('E3'), n('G3', .5), n('E3', .5)],
    [n('F#3', 2), n('E3'), n('E4', tie=True)],
    # Riga 4: battute 15–19.
    [n('E4'), n('D4'), n('C#4', 2, acc=True)],
    [n('B3', .5), n('B2', .5), n('B3'), n('E3'), n('A3')],
    [n('D3'), n('G3'), n('C#3'), n('F#3')],
    [n('B2'), n('D3', .5), n('B2', .5), n('E3', .5), n('D3', .5), n('E3', .5), n('C#3', .5)],
    [n('F#3', 4)],
    # Riga 5: battute 20–24.
    [n('B2'), n('B3', tie=True), n('B3'), n('A3', tie=True)],
    [n('A3'), n('G3', tie=True), n('G3'), n('F#3')],
    [n('E3'), n('A3'), n('B3'), n('G3')],
    [n('A3', 4)],
    [n('D3', 4, fermata=True)],
]

BASSO_39 = [
    # Riga 1: battute 1–4.
    [n('Bb2'), n('Bb3', tie=True), n('Bb3'), n('A3')],
    [n('Bb3', .5), n('A3', .5), n('G3', .5), n('F3', .5), n('Eb3'), n('F3', .5), n('Eb3', .5)],
    [n('D3', .5), n('Bb2', .5), n('Bb3'), n('Eb3'), n('A3')],
    [n('D3'), n('G3'), n('C3'), n('F3')],
    # Riga 2: battute 5–9.
    [n('Bb2', .5), n('F3', .5), n('Bb3', .5), n('A3', .5), n('G3'), n('A3')],
    [n('D3', .5), n('En3', .5), n('F3', .5), n('D3', .5), n('G3', .5), n('E3', .5), n('A3', .5), n('G3', .5)],
    [n('F3', .5), n('D3', .5), n('D4'), n('G3'), n('C4')],
    [n('F3'), n('Bb3'), n('En3'), n('A3')],
    [n('D3'), n('D4', tie=True), n('D4'), n('C4', tie=True)],
    # Riga 3: battute 10–14.
    [n('C4'), n('Bb3', tie=True), n('Bb3'), n('A3')],
    [n('G3', 2), n('F3'), n('En3')],
    [n('F3'), n('A3'), n('G3'), n('D4', .5), n('Bb3', .5)],
    [n('A3', .5), n('G3', .5), n('F3', tie=True), n('F3'), n('En3')],
    [n('F3', 2), n('Eb3', 2, acc=True)],
    # Riga 4: battute 15–19.
    [n('D3'), n('D4', tie=True), n('D4'), n('C4', tie=True)],
    [n('C4'), n('Bb3'), n('A3', 2)],
    [n('G3', .5), n('G2', .5), n('G3', tie=True), n('G3'), n('F#3')],
    [n('G3', .5), n('G2', .5), n('G3'), n('C3'), n('Fn3', acc=True)],
    [n('Bb2'), n('Eb3'), n('A2'), n('D3')],
    # Riga 5: battute 20–24.
    [n('G2'), n('G3', tie=True), n('G3'), n('F3', tie=True)],
    [n('F3'), n('Eb3', tie=True), n('Eb3'), n('D3')],
    [n('C3'), n('F3'), n('G3'), n('Eb3', .5), n('En3', .5)],
    [n('F3', 2), n('F2', 2)],
    [n('Bb2', 4, fermata=True)],
]


if __name__ == '__main__':
    out = Path(__file__).resolve().parents[2] / 'out'
    # Un file per basso: PDF custom, MusicXML e versione LilyPond.
    for number, nacc, bars in [(38, 2, BASSO_38), (39, -2, BASSO_39)]:
        output = out / f'basso_{number}.pdf'
        render_bass_exercises([{'title': f'Basso {number}', 'nacc': nacc, 'bars': bars}], output)
        print(output)
        print(output.with_suffix('.musicxml'))
        print(output.with_name(output.stem + '_lilypond.pdf'))
