import xml.etree.ElementTree as ET

import pytest

from tools.armonia import render_snippet


def test_musicxml_conserva_note_e_legature_tra_sistemi(tmp_path):
    bars = [[{'p': 'D3', 'dur': 4}]] * 2 + [
        [{'p': 'F#3', 'dur': 4, 'tie': True}],
        [{'p': 'F#3', 'dur': 1}, {'p': 'Fn3', 'dur': .5, 'acc': True},
         {'p': 'E3', 'dur': .5}, {'p': 'D3', 'dur': 2, 'fermata': True}],
    ]
    path = tmp_path / 'spartiti' / 'bassi.musicxml'
    render_snippet.export_bass_musicxml([
        {'title': 'Basso <prova>', 'nacc': 2, 'bars': bars},
        {'title': 'Basso successivo', 'nacc': -2,
         'bars': [[{'p': 'Bb2', 'dur': 4}]]},
    ], path)
    root = ET.parse(path).getroot()
    assert root.tag == 'score-partwise'
    measures = root.findall('./part/measure')
    assert len(measures) == 5
    assert measures[0].findtext('./attributes/key/fifths') == '2'
    assert measures[4].findtext('./attributes/key/fifths') == '-2'
    assert measures[0].findtext('./direction/direction-type/words') == 'Basso <prova>'
    credits = {c.findtext('credit-type'): c.findtext('credit-words') for c in root.findall('credit')}
    assert credits == {'title': 'Basso <prova> – Basso successivo',
                       'subtitle': 'Basso da armonizzare a quattro voci'}
    assert measures[3].find('print').get('new-system') == 'yes'
    assert measures[4].find('print').get('new-page') == 'yes'
    bass = [n for m in measures for n in m.findall('note') if n.findtext('staff') == '2']
    assert [n.findtext('duration') for n in bass] == ['8', '8', '8', '2', '1', '1', '4', '8']
    assert [n.findtext('./pitch/step') for n in bass] == ['D', 'D', 'F', 'F', 'F', 'E', 'D', 'B']
    assert bass[2].find('tie').get('type') == 'start'
    assert bass[3].find('tie').get('type') == 'stop'
    assert bass[4].findtext('accidental') == 'natural'
    assert bass[4].find('accidental').get('cautionary') is None   # Fa naturale necessario in Re maggiore
    assert [n.findtext('beam') for n in bass[4:6]] == ['begin', 'end']
    assert bass[6].find('./notations/fermata') is not None
    assert bass[-1].findtext('./pitch/alter') == '-1'
    for m in measures:
        blank = m.find("note[staff='1']")
        assert blank.get('print-object') == 'no'
        assert blank.find('rest') is not None
        assert m.findtext('backup/duration') == '8'
    assert all(n.findtext('stem') == 'down' for n in bass if n.findtext('type') != 'whole')


@pytest.mark.parametrize('exercises', [[], [
    {'title': 'Non valido', 'bars': [[{'p': 'C3', 'dur': 2}]]}], [
    {'title': 'Non valido', 'nacc': 8, 'bars': [[{'p': 'C3', 'dur': 4}]]}],
])
def test_musicxml_valida_prima_di_scrivere(tmp_path, exercises):
    path = tmp_path / 'bassi.musicxml'
    path.write_text('originale')
    with pytest.raises(ValueError):
        render_snippet.export_bass_musicxml(exercises, path)
    assert path.read_text() == 'originale'
