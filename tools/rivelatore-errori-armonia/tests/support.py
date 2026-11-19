def score_for(rows, names=('Soprano', 'Contralto', 'Tenore', 'Basso'), time='4/4', tonalita='C'):
    from music21 import key, meter, note, stream
    score = stream.Score()
    for name, row in zip(names, rows):
        part = stream.Part()
        part.partName = name
        part.append(meter.TimeSignature(time))
        part.append(key.Key(tonalita))
        for item in row:
            pitch, duration = item if isinstance(item, tuple) else (item, 1)
            part.append(note.Rest(quarterLength=duration) if pitch is None
                        else note.Note(pitch, quarterLength=duration))
        part.makeMeasures(inPlace=True)
        part.makeTies(inPlace=True)
        score.append(part)
    return score


def xml_file(directory, rows, **kwargs):
    path = directory / 'corale à voci.musicxml'
    score_for(rows, **kwargs).write('musicxml', fp=path)
    return path
