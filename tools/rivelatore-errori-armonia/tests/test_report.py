from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from armonia.report import markdown, salva
from armonia.regole import Risultato, Segnalazione, carica_profilo
from armonia.analisi import CERTA, CONDIZIONATA


class ReportTests(unittest.TestCase):
    def test_collision_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'corale.esame.xml'
            time = datetime(2026,10,18,15,30,12,123456,tzinfo=timezone.utc)
            first = salva('primo', source, data=time)
            second = salva('secondo', source, data=time)
            self.assertEqual(first.name, 'corale.esame_analisi_20261018_153012_123456.md')
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_text(), 'primo')
            self.assertEqual(second.read_text(), 'secondo')
            self.assertEqual(len(list(Path(tmp).iterdir())), 2)

    def test_save_failure_leaves_no_final_or_temp_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('armonia.report.os.link', side_effect=PermissionError('negato')):
                with self.assertRaises(PermissionError):
                    salva('analisi', Path(tmp) / 'corale.xml')
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_partial_markdown_explains_coverage_and_conditional_errors(self):
        data = SimpleNamespace(file=Path('corale|prova.xml'), mappatura={'S':'Soprano'}, misure=[])
        analysis = SimpleNamespace(partitura=data, tonalita=['C major'], limiti=[], segmenti=[], posizione=lambda t: f'tempo {t}')
        profile = carica_profilo()
        findings = [Segnalazione('VL-P5', Fraction(0), Fraction(1), ('S','B'), 'C/G→D/A', 'P12→P12', 'superficie', 'errore', CERTA, 'Rivedere il collegamento'),
                    Segnalazione('HA-LEADING', Fraction(0), Fraction(1), ('S',), 'B→A', 'sensibile', 'V–I', 'errore', CONDIZIONATA, 'Verificare la tonalità')]
        result = Risultato(analysis, profile, findings, {'HA-TRITONE':'non supportata: norma indefinita'})
        text = markdown(result)
        self.assertEqual(result.conteggi['errori'], 1)
        self.assertEqual(result.conteggi['verificare'], 1)
        self.assertIn('Analisi parziale', text)
        self.assertIn('id="e001"', text)
        self.assertIn('norma indefinita', text)
        self.assertIn('corale\\|prova.xml', text)

    def test_no_absolute_certificate(self):
        data = SimpleNamespace(file=Path('x.xml'), mappatura={}, misure=[])
        analysis = SimpleNamespace(partitura=data, tonalita=[], limiti=[], segmenti=[], posizione=str)
        result = Risultato(analysis,carica_profilo(),[],{})
        self.assertIn('Nessuna violazione rilevata dalle regole applicate', markdown(result))
