"""Progressioni fondamentali (Parti IV, VII, VIII): quinte e terze discendenti, sequenza modulante, cromatiche."""
from .base import add, A, catena

def genera():
    # quinte discendenti in Do maggiore: I IV VII6 III VI6 II V I
    add('es_cap17_01', catena([
        A('C', 'M', 0, 'I'), A('F', 'M', 0, 'IV'), A('B', 'd', 1, 'vii°', lt='B'), A('E', 'm', 0, 'iii', lt='B'),
        A('A', 'm', 1, 'vi'), A('D', 'm', 0, 'ii'), A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sop='C')]), dx=75)
    # terze discendenti in Do maggiore: I VI IV II VII V I
    add('es_cap17_02', catena([
        A('C', 'M', 0, 'I'), A('A', 'm', 0, 'vi'), A('F', 'M', 0, 'IV'), A('D', 'm', 0, 'ii'),
        A('B', 'd', 1, 'vii°', lt='B'), A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sop='C')]), dx=75)
    # quinte discendenti in Sol maggiore (stati fondamentali, con il VII in primo rivolto)
    add('es_cap17_11', catena([
        A('G', 'M', 0, 'I'), A('C', 'M', 0, 'IV'), A('F#', 'd', 1, 'vii°', lt='F#'), A('B', 'm', 0, 'iii', lt='F#'),
        A('E', 'm', 0, 'vi'), A('A', 'm', 0, 'ii'), A('D', 'M', 0, 'V', lt='F#'), A('G', 'M', 0, 'I', sop='G')]), nacc=1, dx=75)
    # sequenza modulante Do -> Sol: VI-II-V-I in Do, poi una quinta sopra in Sol (il Do finale e' il pivot)
    add('es_cap36_01', catena([
        A('A', 'm', 0, 'vi'), A('D', 'm', 0, 'ii'), A('G', 'M', 0, 'V', lt='B'), A('C', 'M', 0, 'I', sub='pivot: I = IV'),
        A('E', 'm', 0, 'vi', lt='F#'), A('A', 'm', 0, 'ii'), A('D', 'M', 0, 'V', lt='F#'), A('G', 'M', 0, 'I', sop='G')]), dx=75,
        caps=[(0, 3, 'Do maggiore'), (4, 7, 'Sol maggiore')])
    # cromatica ascendente (5, 6/5) in Do minore: VI - V6/5 di VII - VII - V6/5 - i
    add('es_cap17_13', catena([
        A('Ab', 'M', 0, 'VI'), A('F', '7', 1, 'V/VII', lt='A', mv={'Eb': 'down'}), A('Bb', 'M', 0, 'VII'),
        A('G', '7', 1, 'V', lt='B', mv={'F': 'down'}), A('C', 'm', 0, 'i', sop='C')]), nacc=-3, dx=80)
