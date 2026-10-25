# PDF di armonia (settime, sesta napoletana, seste eccedenti)

Requisiti: Python 3, `pip install reportlab fonttools`
Font usati (percorsi Linux, da adattare in engrave.py e glyphs.py se necessario):
- DejaVu Sans  -> /usr/share/fonts/truetype/dejavu/
- FreeSerif    -> /usr/share/fonts/truetype/freefont/FreeSerif.ttf (chiavi e alterazioni, disegnate come contorni)

Esecuzione:
    python3 build_all.py   # out/orizzontale/ e out/verticale/
    python3 build1.py      # solo orizzontale (default)
    PDF_ORIENT=verticale python3 build1.py

File:
- music.py    altezze, spelling, controllo parallele/incroci/estensioni
- solver.py   ricerca delle disposizioni a 4 voci (programmazione dinamica)
- glyphs.py   chiavi e alterazioni da contorni del font
- engrave.py  motore di notazione (grand staff, frecce, etichette)
- doc.py      impaginazione (pagine, testo, tabelle)
- scales.py   accordi di settima sui gradi delle scale
- data1.py / data23.py   gli esempi a 4 voci (S, A, T, B per ogni accordo)
- build1/2/3.py  contenuto testuale e pagine dei tre PDF
