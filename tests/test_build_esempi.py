import os
import pytest
from tools.build_esempi import build_all_esempi

def test_build_all_esempi(tmp_path):
    out_dir = str(tmp_path / "esempi_gen")
    generated = build_all_esempi(out_dir=out_dir, limit=3)
    assert len(generated) == 3
    for path in generated:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
