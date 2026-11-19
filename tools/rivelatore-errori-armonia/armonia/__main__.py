"""Interazione ordinaria: soltanto il percorso del MusicXML."""

from datetime import datetime
import sys

from .analisi import analizza
from .lettura import ErroreIngresso, NOMI, leggi, percorso
from .regole import controlla
from .report import markdown, salva


def _mappatura(lines):
    print('Identità SATB ambigue. Linee disponibili:')
    for i,label in enumerate(lines,1):
        print(f'  {i}. {label}')
    while True:
        raw = input('Indici in ordine S A T B (esempio: 1 2 3 4; vuoto per uscire): ').strip()
        if not raw:
            raise EOFError
        try:
            indices = [int(n) for n in raw.replace(',', ' ').split()]
            if sorted(indices) != [1,2,3,4]:
                raise ValueError
            return {v: lines[i-1] for v,i in zip(NOMI,indices)}
        except ValueError:
            print('Inserire i quattro indici, ciascuno una volta.')


def _esegui():
    print('Analisi di armonia complementare\nProfilo: complementare_it\n')
    failed = False
    while True:
        try:
            value = input('File MusicXML (vuoto per uscire): ').strip()
        except EOFError:
            return 1 if failed else 0
        if not value:
            return 1 if failed else 0
        path = percorso(value)
        try:
            print('Lettura della partitura...')
            score = leggi(path, _mappatura)
            print('Voci riconosciute: ' + ', '.join(NOMI.values()))
            print('Analisi degli accordi e del ritmo armonico...')
            analysis = analizza(score)
            print('Analisi della condotta delle parti e delle risoluzioni...')
            result = controlla(analysis)
        except ErroreIngresso as exc:
            print(f'{exc}\n')
            failed = True
            continue
        except (ImportError, OSError, ValueError) as exc:
            print(f'Analisi non completata: {exc}')
            return 1
        except EOFError:
            print('Analisi annullata.')
            return 1
        print('Scrittura del report...')
        timestamp = datetime.now().astimezone()
        text = markdown(result, timestamp)
        directory = None
        while True:
            try:
                output = salva(text, path, directory, timestamp)
                break
            except OSError as exc:
                print(f'Report non salvato: {exc}. L’analisi è ancora in memoria.')
                try:
                    alternative = input('Cartella alternativa (vuoto per annullare): ').strip()
                except EOFError:
                    return 1
                if not alternative:
                    return 1
                directory = percorso(alternative)
        counts = result.conteggi
        print('\nAnalisi completata' + (' con copertura parziale.' if result.parziale else '.'))
        print(f'Errori confermati: {counts["errori"]} | Avvertimenti certi: {counts["avvertimenti"]} | Casi da verificare: {counts["verificare"]}')
        print(f'Report: {output.resolve()}')
        return 2 if result.parziale else 0


def main():
    try:
        return _esegui()
    except KeyboardInterrupt:
        print('\nAnalisi interrotta. Nessun successo di salvataggio annunciato.')
        return 130
    except Exception as exc:
        print(f'Fallimento operativo ({type(exc).__name__}): {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
