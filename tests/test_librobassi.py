from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from tools.armonia import librobassi


def test_libro_conserva_tutte_le_parti_e_le_note_riconosciute(tmp_path):
    for number, pitch in [(2, 'D'), (1, 'C')]:
        source = f'''<score-partwise version="4.0"><part-list>
          <score-part id="P1"><part-name>Basso</part-name></score-part>
          <score-part id="P2"><part-name>Basso</part-name></score-part>
        </part-list><part id="P1"><measure number="1"><attributes><divisions>2</divisions></attributes>
          <note><pitch><step>{pitch}</step><octave>3</octave></pitch><duration>8</duration><type>whole</type></note>
        </measure><measure number="1"><note><pitch><step>{pitch}</step><octave>4</octave></pitch>
          <duration>8</duration><type>whole</type></note></measure></part><part id="P2"><measure number="1">
          <note><pitch><step>G</step><octave>3</octave></pitch><duration>8</duration><type>whole</type></note>
        </measure></part></score-partwise>'''
        with ZipFile(tmp_path / f'libro.mvt{number}.mxl', 'w') as z:
            z.writestr('META-INF/container.xml', '<container><rootfiles><rootfile full-path="score.xml"/></rootfiles></container>')
            z.writestr('score.xml', source)
    report = librobassi.export_recognized_book(tmp_path, tmp_path / 'libro.musicxml')
    root = ET.parse(tmp_path / 'libro.musicxml').getroot()
    assert [p.findtext('pitch/step') for p in root.findall("part[@id='P1']/measure/note")] == ['C', 'C', 'D', 'D']
    assert len(root.findall('part/measure/note/pitch')) == 6
    assert len(root.findall('part')) == 2
    assert len(report) == 2
    assert root.find("part/measure[@number='S2-1']/print").get('new-page') == 'yes'
    assert 'bozza' in root.findtext('work/work-title').lower()
    assert len(list((tmp_path / 'musicxml').glob('*.musicxml'))) == 2
