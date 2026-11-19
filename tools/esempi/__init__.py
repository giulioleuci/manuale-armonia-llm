"""Generatore degli esempi musicali risolti dal solver (vedi tests/test_esempi_codice.py)."""
from .base import ES
from . import fondamenti, sintassi, ottava, fondamentali, settime, ritardi, progressioni, napoletana, eccedenti, scelta_numerica

def genera():
    ES.clear()
    for m in (fondamenti, sintassi, ottava, fondamentali, settime, ritardi, progressioni, napoletana, eccedenti, scelta_numerica): m.genera()
    return ES
