import tempfile
import importlib.util
import unittest
from pathlib import Path

from armonia.lettura import ErroreIngresso, leggi, percorso
from tests.support import xml_file


@unittest.skipUnless(importlib.util.find_spec('music21'), 'music21 non installato: integrazione MusicXML non eseguibile')
class LetturaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_quoted_path_and_accents(self):
        p = xml_file(self.dir, [['G4'], ['E4'], ['C4'], ['C3']])
        self.assertEqual(percorso(f'"{p}"'), p)
        data = leggi(p)
        self.assertEqual(list(data.linee), ['S', 'A', 'T', 'B'])
        self.assertEqual(data.linee['B'][0].pitch.nameWithOctave, 'C3')

    def test_crossing_keeps_voice_identity(self):
        p = xml_file(self.dir, [['G4', 'C4'], ['E4', 'E4'], ['C4', 'G3'], ['C3', 'C3']])
        self.assertEqual(leggi(p).linee['S'][1].pitch.nameWithOctave, 'C4')

    def test_rejects_hostile_or_non_musicxml(self):
        for text in ['<html/>', '<score-partwise>',
                     '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><score-partwise>&a;</score-partwise>']:
            with self.subTest(text=text):
                p = self.dir / 'bad.xml'
                p.write_text(text)
                with self.assertRaises(ErroreIngresso):
                    leggi(p)

    def test_ambiguous_names_request_one_mapping(self):
        p = xml_file(self.dir, [['G4'], ['E4'], ['C4'], ['C3']], names=('Uno','Due','Tre','Quattro'))
        calls = []
        def choose(lines):
            calls.append(lines)
            return dict(zip('SATB', lines))
        data = leggi(p, choose)
        self.assertEqual(len(calls), 1)
        self.assertEqual(data.linee['S'][0].pitch.nameWithOctave, 'G4')

    def test_rejects_lost_voice_chords(self):
        from music21 import chord
        from tests.support import score_for
        s = score_for([['G4'], ['E4'], ['C4'], ['C3']])
        m = s.parts[0].measure(1)
        m.replace(m.notes[0], chord.Chord(['G4','B4']))
        p = s.write('musicxml', fp=self.dir / 'chords.xml')
        with self.assertRaisesRegex(ErroreIngresso, 'monodich|separate'):
            leggi(Path(p))

    def test_rejects_mxl(self):
        with self.assertRaisesRegex(ErroreIngresso, 'mxl|MusicXML'):
            leggi(self.dir / 'file.mxl')

    def test_chord_symbol_is_annotation_not_vocal_note(self):
        from music21 import harmony
        from tests.support import score_for
        s = score_for([['G4'], ['E4'], ['C4'], ['C3']])
        s.parts[0].measure(1).insert(0, harmony.ChordSymbol('C'))
        path = Path(s.write('musicxml', fp=self.dir / 'symbol.xml'))
        data = leggi(path)
        self.assertEqual(sum(e.pitch is not None for e in data.linee['S']), 1)
        self.assertEqual(data.annotazioni[0].tipo, 'simbolo')

    def test_ties_merge_into_single_attack(self):
        path = xml_file(self.dir, [[('G4',8)], [('E4',8)], [('C4',8)], [('C3',8)]])
        data = leggi(path)
        self.assertEqual(len(data.linee['S']), 1)
        self.assertEqual(data.linee['S'][0].fine, 8)
        self.assertIn('start', data.linee['S'][0].legature)

    def test_two_staff_export_matches_four_parts(self):
        from music21 import clef, layout, note, stream, meter, key
        score = stream.Score()
        for staff_no, rows in enumerate((('G4 E4','F4 D4'), ('C4 B3','C3 G2')),1):
            staff = stream.PartStaff(id=f'P{staff_no}')
            m = stream.Measure(number=1)
            m.insert(0,meter.TimeSignature('4/4'))
            m.insert(0,key.Key('C'))
            m.insert(0,clef.TrebleClef() if staff_no == 1 else clef.BassClef())
            for voice_no, row in enumerate(rows,1):
                v = stream.Voice(id=str(voice_no))
                for name in row.split():
                    v.append(note.Note(name,quarterLength=2))
                m.insert(0,v)
            staff.append(m)
            score.append(staff)
        score.insert(0,layout.StaffGroup(list(score.parts),symbol='brace'))
        path = Path(score.write('musicxml',fp=self.dir / 'two.xml'))
        two = leggi(path,lambda lines: dict(zip('SATB',lines)))
        four = leggi(xml_file(self.dir,[[('G4',2),('E4',2)],[('F4',2),('D4',2)],
                                       [('C4',2),('B3',2)],[('C3',2),('G2',2)]]))
        for voice in 'SATB':
            self.assertEqual([(e.pitch.nameWithOctave,e.inizio,e.fine) for e in two.linee[voice]],
                             [(e.pitch.nameWithOctave,e.inizio,e.fine) for e in four.linee[voice]])
