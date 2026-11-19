import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from armonia.__main__ import main


@unittest.skipUnless(importlib.util.find_spec('music21'), 'music21 non installato: prova completa non eseguibile')
class IntegrazioneTests(unittest.TestCase):
    def test_example_generates_real_partial_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'corale.musicxml'
            shutil.copyfile(Path(__file__).resolve().parents[1]/'esempi/corale.musicxml',path)
            output = io.StringIO()
            with patch('builtins.input',side_effect=[str(path), '']), contextlib.redirect_stdout(output):
                code = main()
            self.assertEqual(code,2,output.getvalue())
            reports = list(Path(tmp).glob('corale_analisi_*.md'))
            self.assertEqual(len(reports),1)
            text = reports[0].read_text()
            self.assertIn('VL-P5',text)
            self.assertIn('HA-MODULATION',text)
            self.assertIn('tonicizzazione di G major',text)
            self.assertIn('Analisi armonica',text)
            self.assertIn('Analisi parziale',text)
