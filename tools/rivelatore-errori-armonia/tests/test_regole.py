import tempfile
import importlib.util
import unittest
from pathlib import Path

from armonia.analisi import analizza
from armonia.lettura import leggi
from armonia.regole import controlla
from tests.support import xml_file


@unittest.skipUnless(importlib.util.find_spec('music21'), 'music21 non installato: regole musicali non eseguibili')
class RegoleTests(unittest.TestCase):
    def findings(self, rows, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            return controlla(analizza(leggi(xml_file(Path(tmp), rows, **kwargs))))

    def ids(self, rows):
        return [f.regola for f in self.findings(rows).segnalazioni]

    def test_compound_parallel_fifths(self):
        result = self.findings([['G4','A4'], ['E4','F4'], ['C4','D4'], ['C3','D3']])
        hits = [f for f in result.segnalazioni if f.regola == 'VL-P5' and f.voci == ('S','B')]
        self.assertEqual(len(hits), 1)
        self.assertIn('P12', hits[0].evidenza)

    def test_diminished_is_not_perfect_fifth(self):
        result = self.findings([['F4','G4'], ['D4','E4'], ['A3','C4'], ['B2','C3']])
        self.assertFalse(any(f.regola == 'VL-P5' and f.voci == ('S','B') for f in result.segnalazioni))

    def test_contrary_fifths_separate_category(self):
        result = self.findings([['G4','A4'], ['E4','F4'], ['C4','D4'], ['C3','D2']])
        self.assertTrue(any(f.regola == 'VL-CONTRARY' and f.voci == ('S','B') for f in result.segnalazioni))
        self.assertFalse(any(f.regola == 'VL-P5' and f.voci == ('S','B') for f in result.segnalazioni))

    def test_no_parallel_across_rest(self):
        result = self.findings([['G4',None,'A4'], ['E4','F4','F4'], ['C4','D4','D4'], ['C3','D3','D3']])
        self.assertFalse(any(f.regola == 'VL-P5' and f.voci == ('S','B') for f in result.segnalazioni))

    def test_third_voice_does_not_duplicate_stationary_pair(self):
        result = self.findings([[('G4',4)], ['E4','F4','E4','F4'], [('C4',4)], [('C3',4)]])
        self.assertFalse(any(f.regola in ('VL-P5','VL-P8') and f.voci == ('S','B') for f in result.segnalazioni))

    def test_direct_fifth_requires_soprano_leap(self):
        leap = self.findings([['E4','A4'], ['C4','F4'], ['G3','D4'], ['C3','D3']])
        step = self.findings([['G4','A4'], ['E4','F4'], ['C4','D4'], ['E3','D3']])
        self.assertTrue(any(f.regola == 'VL-DIRECT' and f.voci == ('S','B') for f in leap.segnalazioni))
        self.assertFalse(any(f.regola == 'VL-DIRECT' and f.voci == ('S','B') for f in step.segnalazioni))

    def test_crossing_and_spacing(self):
        ids = self.ids([['C4'], ['E4'], ['C3'], ['C2']])
        self.assertIn('VL-CROSS', ids)
        self.assertIn('VL-SPACE', ids)

    def test_unison_is_not_crossing(self):
        self.assertNotIn('VL-CROSS', self.ids([['E4'], ['E4'], ['C4'], ['C3']]))

    def test_leading_tone_double_is_conditional(self):
        result = self.findings([['B4','C5'], ['F4','E4'], ['B3','C4'], ['G2','C3']])
        hit = next(f for f in result.segnalazioni if f.regola == 'HA-LEADING-DOUBLE')
        self.assertNotEqual(hit.affidabilita, 'certa sui dati e sul profilo')

    def test_seventh_resolves_down(self):
        good = self.findings([['F4','E4'], ['B3','C4'], ['D3','G3'], ['G2','C3']])
        bad = self.findings([['F4','G4'], ['B3','C4'], ['D3','E3'], ['G2','C3']])
        self.assertFalse(any(f.regola == 'HA-SEVENTH' and f.voci == ('S',) for f in good.segnalazioni))
        self.assertTrue(any(f.regola == 'HA-SEVENTH' and f.voci == ('S',) for f in bad.segnalazioni))

    def test_harmonic_syncopation_survives_rearticulation(self):
        result = self.findings([['G4',('A4',2),('A4',2)], ['E4',('F4',2),('F4',2)],
                                ['C4',('D4',2),('D4',2)], ['C3',('D3',2),('D3',2)]])
        self.assertTrue(any(f.regola == 'HR-SYNC' for f in result.segnalazioni))

    def test_coverage_marks_undefined_rules_unavailable(self):
        result = self.findings([['G4'], ['E4'], ['C4'], ['C3']])
        self.assertTrue(result.parziale)
        self.assertIn('non supportata', result.copertura['HA-TRITONE'])

    def test_octaves_and_unisons_are_named(self):
        result = self.findings([['C4','D4'], ['G3','A3'], ['E3','F3'], ['C3','D3']])
        self.assertTrue(any(f.regola == 'VL-P8' and f.voci == ('S','B') for f in result.segnalazioni))
        self.assertNotIn('VL-P8', self.ids([['C4','C4'], ['G3','G3'], ['E3','E3'], ['C3','C3']]))

    def test_voice_overlap_without_simultaneous_crossing(self):
        result = self.findings([['G4','B4'], ['E4','A4'], ['C4','C4'], ['C3','C3']])
        self.assertTrue(any(f.regola == 'VL-OVERLAP' and f.voci == ('S','A') for f in result.segnalazioni))
        self.assertFalse(any(f.regola == 'VL-CROSS' for f in result.segnalazioni))

    def test_range_leap_and_recovery(self):
        self.assertIn('ME-RANGE', self.ids([['B5'], ['E4'], ['C4'], ['C3']]))
        self.assertNotIn('ME-RANGE', self.ids([['A5'], ['E4'], ['C4'], ['C3']]))
        self.assertIn('ME-LEAP', self.ids([['C4','D5'], ['E4','E4'], ['C4','C4'], ['C3','C3']]))
        self.assertIn('ME-RECOVERY', self.ids([['C4','G4','A4'], ['E4','E4','E4'], ['C4','C4','C4'], ['C3','C3','C3']]))
        self.assertNotIn('ME-RECOVERY', self.ids([['C4','G4','F4'], ['E4','E4','E4'], ['C4','C4','C4'], ['C3','C3','C3']]))

    def test_unequal_fifth_is_caution_not_parallel(self):
        result = self.findings([['F4','G4'], ['D4','E4'], ['B3','C4'], ['B2','C3']])
        self.assertTrue(any(f.regola == 'VL-UNEQUAL' and f.voci == ('S','B') for f in result.segnalazioni))
        self.assertFalse(any(f.regola == 'VL-P5' and f.voci == ('S','B') for f in result.segnalazioni))

    def test_minor_third_doubling_has_no_universal_ban(self):
        result = self.findings([['E4'], ['C4'], ['G3'], ['E3']])
        self.assertFalse(any(f.regola == 'HA-DOUBLING' for f in result.segnalazioni))

    def test_chromatic_relation_not_same_voice_chromatic_step(self):
        simultaneous = self.findings([['F#4'], ['F4'], ['D4'], ['D3']])
        self.assertTrue(any(f.regola == 'HA-CHROMATIC' for f in simultaneous.segnalazioni))
        same_voice = self.findings([['F4','F#4'], ['D4','D4'], ['A3','A3'], ['D3','D3']])
        self.assertFalse(any(f.regola == 'HA-CHROMATIC' for f in same_voice.segnalazioni))

    def test_leading_tone_resolution_exception_inner_voice(self):
        good = self.findings([['B4','C5'], ['F4','E4'], ['D4','G3'], ['G2','C3']])
        bad = self.findings([['B4','E5'], ['F4','E4'], ['D4','G3'], ['G2','C3']])
        self.assertFalse(any(f.regola == 'HA-LEADING' and f.voci == ('S',) for f in good.segnalazioni))
        self.assertTrue(any(f.regola == 'HA-LEADING' and f.voci == ('S',) for f in bad.segnalazioni))
        inner = self.findings([['F4','E4'], ['D4','C4'], ['B3','G3'], ['G2','C3']])
        self.assertTrue(any(f.regola == 'HA-LEADING' and f.voci == ('T',) and f.affidabilita == 'da verificare'
                            and f.gravita == 'osservazione' for f in inner.segnalazioni))

    def test_dominant_seventh_needs_no_preparation(self):
        result = self.findings([['F4','E4'], ['B3','C4'], ['D3','G3'], ['G2','C3']])
        self.assertFalse(any(f.regola == 'HA-PREPARATION' for f in result.segnalazioni))

    def test_second_inversion_identified_cadentially(self):
        result = self.findings([['E4','D4'], ['C4','B3'], ['G3','G3'], ['G2','G2']])
        self.assertTrue(any(f.regola == 'HA-64' and 'cadenza' in f.evidenza for f in result.segnalazioni))

    def test_figures_require_the_sixth(self):
        from fractions import Fraction
        from armonia.lettura import Annotazione
        with tempfile.TemporaryDirectory() as tmp:
            score = leggi(xml_file(Path(tmp), [['G4'], ['E4'], ['C4'], ['C3']]))
            score.annotazioni.append(Annotazione(Fraction(0),'cifre',('6',)))
            result = controlla(analizza(score))
        self.assertTrue(any(f.regola == 'HA-FIGURES' for f in result.segnalazioni))

    def test_secondary_dominant_requires_observed_resolution(self):
        result = self.findings([['F#4','G4'], ['C4','B3'], ['A3','D4'], ['D3','G2']])
        self.assertTrue(any(f.regola == 'HA-MODULATION' for f in result.segnalazioni))

    def test_fermata_breaks_parallel_connection(self):
        from music21 import expressions
        from tests.support import score_for
        with tempfile.TemporaryDirectory() as tmp:
            score = score_for([['G4','A4'], ['E4','F4'], ['C4','D4'], ['C3','D3']])
            score.parts[0].recurse().notes[0].expressions.append(expressions.Fermata())
            path = Path(score.write('musicxml',fp=Path(tmp)/'fermata.xml'))
            result = controlla(analizza(leggi(path)))
        self.assertFalse(any(f.regola == 'VL-P5' and f.voci == ('S','B') for f in result.segnalazioni))

    def test_repeated_dominant_tendency_notes_resolve_later(self):
        result = self.findings([['F4','F4','E4'], ['B3','B3','C4'], ['D3','D3','G3'], ['G2','G2','C3']])
        self.assertFalse(any(f.regola in ('HA-SEVENTH','HA-LEADING') for f in result.segnalazioni))

    def test_new_inversion_of_same_chord_is_checked(self):
        result = self.findings([['E4','E4','D4'], ['C4','C4','B3'], ['G3','G3','G3'], ['C3','G2','G2']])
        self.assertTrue(any(f.regola == 'HA-64' and f.inizio == 1 for f in result.segnalazioni))

    def test_changed_doubling_of_same_chord_is_checked(self):
        result = self.findings([['G4','B4'], ['D4','D4'], ['B3','B3'], ['G2','G2']])
        self.assertTrue(any(f.regola == 'HA-LEADING-DOUBLE' and f.inizio == 1 for f in result.segnalazioni))

    def test_plain_figures_respect_signature_accidentals(self):
        from fractions import Fraction
        from armonia.lettura import Annotazione
        with tempfile.TemporaryDirectory() as tmp:
            score = leggi(xml_file(Path(tmp), [['A-4'], ['G4'], ['E4'], ['C3']]))
            score.annotazioni.append(Annotazione(Fraction(0),'cifre',('6',)))
            result = controlla(analizza(score))
        self.assertTrue(any(f.regola == 'HA-FIGURES' for f in result.segnalazioni))
