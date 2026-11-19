from fractions import Fraction
import unittest

from armonia.lettura import Evento
from armonia.regole import _prossimo_movimento


class RisoluzioniTests(unittest.TestCase):
    def events(self, pitches, fermata=None):
        return [Evento('S',p,Fraction(i),Fraction(i+1),fermata=i==fermata) for i,p in enumerate(pitches)]

    def test_rearticulations_do_not_resolve_tendency_note(self):
        events = self.events(['F4','F4','F4','E4'])
        self.assertIs(_prossimo_movimento(events,events[0]),events[3])

    def test_rest_and_fermata_stop_connection(self):
        for events in (self.events(['F4',None,'E4']), self.events(['F4','F4','E4'],fermata=1)):
            with self.subTest(events=events):
                self.assertIsNone(_prossimo_movimento(events,events[0]))

    def test_gap_and_end_do_not_invent_resolution(self):
        events = self.events(['F4','E4'])
        events[1].inizio = Fraction(2)
        self.assertIsNone(_prossimo_movimento(events,events[0]))
        self.assertIsNone(_prossimo_movimento(events,events[-1]))
