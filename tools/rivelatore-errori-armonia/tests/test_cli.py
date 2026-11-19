import contextlib
import io
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from armonia.__main__ import main


class CliTests(unittest.TestCase):
    def run_main(self, responses):
        output = io.StringIO()
        with patch('builtins.input', side_effect=responses), contextlib.redirect_stdout(output):
            code = main()
        return code, output.getvalue()

    def test_empty_path_exits_without_report(self):
        self.assertEqual(self.run_main([''])[0], 0)

    def test_interrupt_returns_130(self):
        self.assertEqual(self.run_main(KeyboardInterrupt())[0], 130)

    def test_bad_input_can_be_corrected_or_cancelled(self):
        code, text = self.run_main(['inesistente.musicxml', ''])
        self.assertEqual(code, 1)
        self.assertIn('non leggibile', text)

    def test_eof_is_clean(self):
        self.assertEqual(self.run_main(EOFError())[0], 0)

    def test_save_retry_preserves_computed_analysis(self):
        from armonia.report import salva
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            result = SimpleNamespace(parziale=True,conteggi={'errori':0,'avvertimenti':0,'verificare':1})
            def save_once_available(text, path, directory, timestamp):
                if directory is None:
                    raise PermissionError('cartella originale non scrivibile')
                return salva(text,path,directory,timestamp)
            with patch('armonia.__main__.leggi',return_value=object()), \
                 patch('armonia.__main__.analizza',return_value=object()) as analysis, \
                 patch('armonia.__main__.controlla',return_value=result), \
                 patch('armonia.__main__.markdown',return_value='# Analisi già calcolata'), \
                 patch('armonia.__main__.salva',side_effect=save_once_available):
                code, text = self.run_main(['/origine/corale.xml',str(target)])
            self.assertEqual(code,2)
            self.assertEqual(analysis.call_count,1)
            outputs = list(target.glob('corale_analisi_*.md'))
            self.assertEqual(len(outputs),1)
            self.assertEqual(outputs[0].read_text(),'# Analisi già calcolata')
            self.assertIn('ancora in memoria',text)
