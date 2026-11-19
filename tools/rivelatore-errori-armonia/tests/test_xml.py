from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from armonia.lettura import ErroreIngresso, percorso, xml_sicuro


class XmlTests(unittest.TestCase):
    def read(self, text, suffix='.xml'):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ('file' + suffix)
            path.write_bytes(text if isinstance(text, bytes) else text.encode())
            return xml_sicuro(path)

    def test_normal_doctype_is_not_fetched(self):
        root = self.read('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd"><score-partwise/>')
        self.assertEqual(root.tag, 'score-partwise')

    def test_entity_expansion_and_external_entities_rejected(self):
        for entity in ['"espansione"', 'SYSTEM "file:///etc/passwd"', 'SYSTEM "https://example.com/x"']:
            with self.subTest(entity=entity), self.assertRaises(ErroreIngresso):
                self.read(f'<!DOCTYPE score-partwise [<!ENTITY x {entity}>]><score-partwise>&x;</score-partwise>')

    def test_utf16_hostile_xml_also_rejected(self):
        with self.assertRaises(ErroreIngresso):
            self.read('<!DOCTYPE score-partwise [<!ENTITY x "x">]><score-partwise>&x;</score-partwise>'.encode('utf-16'))

    def test_wrong_root_empty_and_malformed_rejected(self):
        for text in ('', '<html/>', '<score-timewise/>', '<score-partwise>'):
            with self.subTest(text=text), self.assertRaises(ErroreIngresso):
                self.read(text)

    def test_transposition_microtones_and_grace_rejected(self):
        for text in ('<transpose/>', '<note><pitch><alter>0.5</alter></pitch></note>', '<grace/>', '<unpitched/>', '<senza-misura/>'):
            with self.subTest(text=text), self.assertRaises(ErroreIngresso):
                self.read(f'<score-partwise>{text}</score-partwise>')

    def test_size_and_note_count_limits(self):
        with patch('armonia.lettura.MAX_BYTES', 10), self.assertRaises(ErroreIngresso):
            self.read('<score-partwise/>')
        with patch('armonia.lettura.MAX_NOTE', 1), self.assertRaises(ErroreIngresso):
            self.read('<score-partwise><note/><note/></score-partwise>')

    def test_mxl_rejected_even_with_valid_xml(self):
        with self.assertRaises(ErroreIngresso):
            self.read('<score-partwise/>', '.mxl')

    def test_missing_file_becomes_concrete_input_error(self):
        with self.assertRaisesRegex(ErroreIngresso, 'non leggibile'):
            xml_sicuro(Path('/inesistente/file.musicxml'))

    def test_path_quotes_spaces_tilde(self):
        self.assertEqual(percorso('  "cartella à/file con spazi.xml"  '), Path('cartella à/file con spazi.xml'))
        self.assertEqual(percorso("'~/file.xml'"), Path.home() / 'file.xml')

    def test_meter_rejected_before_music21_if_irregular(self):
        with self.assertRaisesRegex(ErroreIngresso,'Metro|metro'):
            self.read('<score-partwise><part><measure><attributes><time><beats>5</beats><beat-type>4</beat-type></time></attributes></measure></part></score-partwise>')

    def test_inconsistent_written_key_or_missing_octave_is_rejected(self):
        with self.assertRaises(ErroreIngresso):
            self.read('<score-partwise><note><pitch><step>C</step></pitch></note></score-partwise>')
