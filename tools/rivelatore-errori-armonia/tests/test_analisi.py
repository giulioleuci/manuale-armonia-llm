import tempfile
import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path

from armonia.analisi import analizza
from armonia.lettura import leggi
from tests.support import xml_file


@unittest.skipUnless(importlib.util.find_spec('music21'), 'music21 non installato: analisi musicale non eseguibile')
class AnalisiTests(unittest.TestCase):
    def run_score(self, rows, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            return analizza(leggi(xml_file(Path(tmp), rows, **kwargs)))

    def test_metric_boundary_exists_without_attacks(self):
        result = self.run_score([[('G4', 8)], [('E4', 8)], [('C4', 8)], [('C3', 8)]])
        self.assertIn(Fraction(4), [s.inizio for s in result.segmenti])
        self.assertTrue(all(s.accordo.root().name == 'C' for s in result.segmenti))

    def test_compound_meter_positions_are_explicit(self):
        result = self.run_score([[('G4', 3)], [('E4', 3)], [('C4', 3)], [('C3', 3)]], time='6/8')
        self.assertIn('pulsazione 2', result.posizione(Fraction(3, 2)))
        self.assertIn('suddivisione 2', result.posizione(Fraction(2)))

    def test_recognizes_triad_and_inversion(self):
        result = self.run_score([['G4'], ['C4'], ['G3'], ['E3']])
        self.assertEqual(result.segmenti[0].accordo.inversion(), 1)
        self.assertIn('6', result.segmenti[0].grado)

    def test_rest_does_not_invent_note(self):
        result = self.run_score([['G4', None], ['E4','F4'], ['C4','D4'], ['C3','D3']])
        self.assertIsNone(result.segmenti[1].eventi['S'].pitch)

    def test_passing_note_is_conditional_reduction(self):
        result = self.run_score([['E4','F4',('G4',2)], [('C4',4)], [('G3',4)], [('C3',4)]])
        passing = next(s for s in result.segmenti if s.inizio == 1)
        self.assertIn('S', passing.figurazioni)
        self.assertIn('passaggio', passing.figurazioni['S'])
        self.assertEqual(passing.affidabilita, 'condizionata all’analisi')

    def test_seventh_without_fifth_keeps_essential_notes(self):
        result = self.run_score([['F4'], ['B3'], ['G3'], ['G2']])
        s = result.segmenti[0]
        self.assertIsNotNone(s.accordo)
        self.assertEqual(s.accordo.root().name, 'G')
        self.assertTrue(any('quinta' in a for a in s.alternative))

    def test_unison_score_does_not_block_surface_analysis(self):
        result = self.run_score([['C4'], ['C4'], ['C4'], ['C4']])
        self.assertTrue(result.segmenti)
        self.assertIsNone(result.segmenti[0].accordo)

    def test_pickup_uses_original_number_and_beat(self):
        from music21 import key, meter, note, stream
        score = stream.Score()
        for name,p in zip(('Soprano','Contralto','Tenore','Basso'),('G4','E4','C4','C3')):
            part = stream.Part()
            part.partName = name
            m = stream.Measure(number=0)
            m.insert(0,meter.TimeSignature('4/4'))
            m.insert(0,key.Key('C'))
            m.append(note.Note(p))
            m.padAsAnacrusis()
            part.append(m)
            full = stream.Measure(number=1)
            full.append(note.Note(p,quarterLength=4))
            part.append(full)
            score.append(part)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(score.write('musicxml',fp=Path(tmp)/'pickup.xml'))
            result = analizza(leggi(path))
        self.assertIn('battuta 0',result.posizione(Fraction(0)))
        self.assertIn('tempo 4',result.posizione(Fraction(0)))

    def test_key_change_is_not_silently_lost(self):
        from music21 import key
        from tests.support import score_for
        score = score_for([[('G4',4),('F#4',4)], [('E4',4),('D4',4)], [('C4',4),('A3',4)], [('C3',4),('D3',4)]])
        for part in score.parts:
            part.measure(2).insert(0,key.Key('G'))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(score.write('musicxml',fp=Path(tmp)/'change.xml'))
            result = analizza(leggi(path))
        self.assertEqual(next(s for s in result.segmenti if s.inizio == 4).tonalita.tonic.name,'G')
