import io

import pytest
from reportlab.pdfgen.canvas import Canvas

from tools.armonia import engrave, render_snippet


def test_note_lunghe_lasciano_liberi_i_movimenti():
    # Minima: due posti; semibreve: quattro posti, anche prima di una nuova battuta.
    bars = [[{'p': 'D3', 'dur': 2}, {'p': 'A3', 'dur': 2}],
            [{'p': 'D3', 'dur': 4}]]
    layout, ends = engrave.layout_bass(bars, 100, 34)
    assert [n[1] for n in layout] == [110, 178, 256]
    assert ends == [246, 392]


def test_ritmi_gambi_e_legature_sul_canvas_reale():
    c = Canvas(io.BytesIO(), pageCompression=0)
    bars = [[{'p': 'D3', 'dur': .5}, {'p': 'F#3', 'dur': .5},
             {'p': 'A3', 'dur': 1, 'tie': True}, {'p': 'A3', 'dur': 2}],
            [{'p': 'D3', 'dur': 4, 'fermata': True}]]
    engrave.draw_bass_system(c, 34, 750, bars, nacc=2, beat_width=34)
    code = '\n'.join(c._code)
    # Quattro gambi in giù; nessun gambo sulla semibreve e nessuna nota in violino.
    import re
    stems = re.findall(r'n ([\d.]+) ([\d.]+) m \1 ([\d.]+) l S', code)
    stems = [(float(y1), float(y2)) for _, y1, y2 in stems if abs(float(y1)-float(y2)) > 15]
    # Le stanghette attraversano entrambi i righi; i gambi rimangono nel rigo basso.
    stems = [(a, b) for a, b in stems if abs(a-b) < 50]
    assert len(stems) == 4
    assert all(a > b and a < 700 for a, b in stems)
    c.save()


@pytest.mark.parametrize('bars', [
    [[{'p': 'D3', 'dur': 3}]],
    [[{'p': 'D3', 'dur': 2}]],
    [[{'p': 'D3', 'dur': 4, 'tie': True}]],
    [[{'p': 'D3', 'dur': 2, 'tie': True}, {'p': 'E3', 'dur': 2}]],
])
def test_rifiuta_durate_e_legature_non_valide(bars):
    with pytest.raises(ValueError):
        engrave.layout_bass(bars, 100, 34)


def test_pdf_a4_con_paginazione(tmp_path):
    path = tmp_path / 'bassi.pdf'
    exercises = [{'title': 'Basso 38', 'nacc': 2,
                  'bars': [[{'p': 'D3', 'dur': 4}]] * 24},
                 {'title': 'Basso 39', 'nacc': -2,
                  'bars': [[{'p': 'Bb2', 'dur': 4}]] * 24}]
    render_snippet.render_bass_exercises(exercises, str(path))
    data = path.read_bytes()
    assert data.count(b'/Type /Page\n') == 4
    assert b'/MediaBox [ 0 0 595.2756 841.8898 ]' in data
    # Seconda versione incisa da LilyPond dal MusicXML, generata di default.
    assert (tmp_path / 'bassi_lilypond.pdf').read_bytes().startswith(b'%PDF')


def test_legatura_interrotta_al_cambio_sistema():
    # Le estremità al margine rimangono alte: non simulano una nota inesistente.
    c = Canvas(io.BytesIO())
    engrave.draw_tie(c, 100, 200, 150, 200, open_end=True)
    path = next(command for command in reversed(c._code) if ' c ' in command).split()
    # Inizio sulla nota (200 + 3.5), fine aperta al margine e più alta.
    assert path[2] == '203.5' and path[8] == '150' and float(path[9]) > 208
    engrave.draw_tie(c, 100, 200, 150, 200, open_start=True)
    path = next(command for command in reversed(c._code) if ' c ' in command).split()
    assert path[1] == '100' and float(path[2]) > 208 and path[9] == '203.5'


def test_trascrizioni_complete_e_legature_valide():
    from tools.armonia.bassi_38_39 import BASSO_38, BASSO_39
    for bars in (BASSO_38, BASSO_39):
        assert len(bars) == 24
        engrave.layout_bass(bars, 0, 34)
