import tempfile
import importlib.util
import unittest
from pathlib import Path

from armonia.analisi import analizza
from armonia.lettura import leggi
from armonia.regole import controlla
from tests.support import xml_file


def chords(*cc):
    """accordi come tuple (S, A, T, B) di una semiminima -> righe per voce"""
    return [list(v) for v in zip(*cc)]


@unittest.skipUnless(importlib.util.find_spec('music21'), 'music21 non installato: regole musicali non eseguibili')
class SintassiTests(unittest.TestCase):
    def findings(self, rows, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            return controlla(analizza(leggi(xml_file(Path(tmp), rows, **kwargs)))).segnalazioni

    def hits(self, rows, rule, **kwargs):
        return [f for f in self.findings(rows, **kwargs) if f.regola == rule]

    def tipo(self, rows, **kwargs):
        return [f.evidenza.split(':')[0].split(' (')[0] for f in self.hits(rows, 'CA-TIPO', **kwargs)]

    # --- cadenze
    def test_cadenza_perfetta_e_imperfetta(self):
        self.assertEqual(self.tipo(chords(('D5','B4','G3','G2'), ('C5','E4','G3','C3'))), ['cadenza perfetta'])
        self.assertEqual(self.tipo(chords(('D5','G4','D4','B2'), ('C5','E4','G3','C3'))), ['cadenza imperfetta'])
        self.assertEqual(self.tipo(chords(('D5','G4','B3','G2'), ('E5','G4','C4','C3'))), ['cadenza imperfetta'])

    def test_cadenze_plagale_sospesa_inganno(self):
        self.assertEqual(self.tipo(chords(('F5','A4','C4','F3'), ('E5','G4','C4','C3'))), ['cadenza plagale'])
        self.assertEqual(self.tipo(chords(('C5','E4','G3','C3'), ('B4','D4','G3','G2'))), ['cadenza sospesa'])
        self.assertEqual(self.tipo(chords(('D5','G4','B3','G2'), ('C5','E4','A3','A2'))), ["cadenza d'inganno"])

    def test_cadenza_e_manuale_o_automatica(self):
        f = self.hits(chords(('D5','B4','G3','G2'), ('C5','E4','G3','C3')), 'CA-TIPO')[0]
        self.assertEqual(f.gravita, 'osservazione')
        self.assertIn(f.affidabilita, ('condizionata all’analisi', 'da verificare'))

    def test_fine_frase_senza_cadenza(self):
        self.assertEqual(len(self.hits(chords(('C5','E4','G3','C3'), ('D5','F4','A3','D3')), 'CA-FINALE')), 1)

    # --- risoluzioni
    NAPOLETANA = [('E5','A4','C4','A2'), ('D5','F4','Bb3','D3')]

    def test_napoletana_su_V_ok_su_altro_errore(self):
        ok = chords(*self.NAPOLETANA, ('B4','E4','G#3','E3'), ('A4','E4','A3','A2'))
        self.assertFalse(self.hits(ok, 'RS-NAPOLETANA', tonalita='a'))
        bad = chords(*self.NAPOLETANA, ('C5','E4','A3','A2'))
        hit = self.hits(bad, 'RS-NAPOLETANA', tonalita='a')
        self.assertTrue(hit and hit[0].gravita == 'errore')

    def test_sesta_italiana_risolve_su_V(self):
        it6 = ('D#5','A4','A3','F3')
        ok = chords(('E5','A4','C4','A3'), it6, ('E5','G#4','B3','E3'), ('E5','A4','C4','A3'))
        res = self.findings(ok, tonalita='a')
        self.assertFalse([f for f in res if f.regola in ('RS-ECCEDENTE', 'HA-INCOMPLETE')])
        bad = chords(('E5','A4','C4','A3'), it6, ('D5','F4','A3','D3'))
        hit = [f for f in self.findings(bad, tonalita='a') if f.regola == 'RS-ECCEDENTE']
        self.assertTrue(hit and hit[0].gravita == 'errore')

    def test_64_cadenziale(self):
        ok = chords(('C5','E4','G3','G2'), ('B4','D4','G3','G2'))
        self.assertFalse(self.hits(ok, 'RS-64'))
        bad = chords(('C5','E4','G3','G2'), ('B4','G4','D4','G2'))
        self.assertEqual(len(self.hits(bad, 'RS-64')), 1)

    def test_ritardo_non_risolto(self):
        base = [[('C5',6),('B4',2)], [('G4',4),('B3',4)], [('E4',4),('D4',4)], [('C3',4),('G2',4)]]
        self.assertFalse(self.hits(base, 'RS-RITARDO'))
        bad = [[('C5',6),('E5',2)]] + base[1:]
        hit = self.hits(bad, 'RS-RITARDO')
        self.assertTrue(hit and hit[0].gravita == 'errore')

    # --- progressioni
    def test_progressione_per_terze_discendenti(self):
        rows = chords(('E5','G4','C4','C3'), ('E5','A4','C4','A2'), ('F5','A4','C4','F3'), ('F5','A4','D4','D3'))
        hit = self.hits(rows, 'PR-RILEVATA')
        self.assertEqual(len(hit), 1)
        self.assertIn('terze discendenti', hit[0].evidenza)

    def test_due_accordi_non_sono_progressione(self):
        self.assertFalse(self.hits(chords(('C5','E4','G3','C3'), ('B4','D4','G3','G2'), ('C5','E4','G3','C3')), 'PR-RILEVATA'))

    # --- modulazioni
    def test_modulazione_alla_dominante_con_pivot(self):
        rows = chords(('E5','G4','C4','C3'), ('E5','A4','C4','A2'), ('F#5','A4','D4','D3'), ('G5','B4','D4','G3'))
        hit = self.hits(rows, 'MO-RILEVATA')
        self.assertEqual(len(hit), 1)
        self.assertIn('Sol maggiore (tono vicino: dominante)', hit[0].evidenza)
        self.assertIn('pivot vi = ii', hit[0].evidenza)

    def test_tonicizzazione_senza_modulazione(self):
        rows = chords(('E5','G4','C4','C3'), ('F#5','A4','D4','D3'), ('G5','B4','D4','G3'), ('E5','G4','C4','C3'))
        self.assertFalse(self.hits(rows, 'MO-RILEVATA'))
        self.assertTrue(self.hits(rows, 'MO-TONICIZZAZIONE'))

    def test_diatonico_non_modula(self):
        rows = chords(('E5','G4','C4','C3'), ('F5','A4','C4','F3'), ('F5','G4','D4','G2'), ('E5','G4','C4','C3'))
        self.assertFalse([f for f in self.findings(rows) if f.regola.startswith('MO-')])


if __name__ == '__main__':
    unittest.main()
