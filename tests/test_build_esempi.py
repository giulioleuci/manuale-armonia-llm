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

def test_tutti_gli_esempi_entrano_nel_box_alla_stessa_scala(tmp_path):
    """\\musica include ogni PDF a scala fissa: nessun esempio deve superare la larghezza del box (va a capo)"""
    from tools.armonia.render_snippet import LARGHEZZA_MAX
    import re
    larghi = []
    for path in build_all_esempi(out_dir=str(tmp_path)):
        w = float(re.search(rb'/MediaBox \[\s*0 0 ([\d.]+)', open(path, 'rb').read()).group(1))
        if w > LARGHEZZA_MAX + 0.5: larghi.append((os.path.basename(path), w))
    assert not larghi, larghi
