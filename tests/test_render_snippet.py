import os
import pytest
from tools.armonia.render_snippet import render_satb_snippet, render_block_snippet

def test_render_satb_snippet(tmp_path):
    out_pdf = tmp_path / "test_chord.pdf"
    chords = [
        {'v': ['C5', 'G4', 'E4', 'C3'], 'rn': 'I', 'fig': []},
        {'v': ['B4', 'G4', 'F4', 'D3'], 'rn': 'V7', 'fig': ['7']}
    ]
    render_satb_snippet(chords, str(out_pdf))
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0

def test_render_block_snippet(tmp_path):
    out_pdf = tmp_path / "test_blocks.pdf"
    chords = [
        {'p': ['C4', 'E4', 'G4'], 'rn': 'I', 'name': 'Do M'},
        {'p': ['C4', 'Eb4', 'G4'], 'rn': 'i', 'name': 'Do m'}
    ]
    render_block_snippet(chords, str(out_pdf), clef='treble')
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
