import os
import pytest
from tools.armonia.engrave import VOICE_DIRECTIONS, get_stem_direction, get_tie_direction
from tools.armonia.render_snippet import render_satb_snippet, render_block_snippet

def test_voice_directions():
    # Soprano (0): stem UP (+1), tie UP (+1)
    assert get_stem_direction(0) == 1
    assert get_tie_direction(0) == 1
    # Contralto (1): stem DOWN (-1), tie DOWN (-1)
    assert get_stem_direction(1) == -1
    assert get_tie_direction(1) == -1
    # Tenore (2): stem UP (+1), tie UP (+1)
    assert get_stem_direction(2) == 1
    assert get_tie_direction(2) == 1
    # Basso (3): stem DOWN (-1), tie DOWN (-1)
    assert get_stem_direction(3) == -1
    assert get_tie_direction(3) == -1

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

def test_tied_semiminime_rendering(tmp_path):
    out_pdf = tmp_path / "test_tied.pdf"
    # Chord 1 has G4 in Alto, Chord 2 holds G4 in Alto: should be two tied quarter notes
    chords = [
        {'v': ['C5', 'G4', 'E4', 'C3'], 'rn': 'I'},
        {'v': ['B4', 'G4', 'F4', 'D3'], 'rn': 'V7'}
    ]
    render_satb_snippet(chords, str(out_pdf))
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
