"""Fogli di lavoro fedeli alla scansione e bozza MusicXML esterna di Audiveris."""

from copy import deepcopy
import json
from pathlib import Path
from statistics import median
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .engrave import S, Staff, draw_clef, draw_staff_lines
from .render_snippet import BASS_SYSTEM_STEP


def export_recognized_book(omr_dir, out_path):
    """Conserva tutte le parti riconosciute, comprese le battute incomplete."""
    omr_dir, out_path = Path(omr_dir), Path(out_path)
    files = sorted(omr_dir.glob('*.mxl'), key=lambda p: int(p.stem.rsplit('.mvt', 1)[-1]))
    if not files:
        raise ValueError('Nessun MusicXML Audiveris disponibile')
    scores = []
    folder = out_path.parent / 'musicxml'
    folder.mkdir(parents=True, exist_ok=True)
    for path in files:
        with ZipFile(path) as z:
            container = ET.fromstring(z.read('META-INF/container.xml'))
            name = next(e.get('full-path') for e in container.iter() if e.tag.endswith('rootfile'))
            score = ET.fromstring(z.read(name))
        ET.ElementTree(score).write(folder / (path.stem+'.musicxml'), encoding='utf-8', xml_declaration=True)
        scores.append(score)
    root = ET.Element('score-partwise', version='4.0')
    ET.SubElement(ET.SubElement(root, 'work'), 'work-title').text = 'Jacopo Napoli · Bassi · BOZZA OMR DA CORREGGERE'
    parts = ET.SubElement(root, 'part-list')
    destinations = []
    for i in range(max(len(s.findall('part')) for s in scores)):
        ident = f'P{i+1}'
        ET.SubElement(ET.SubElement(parts, 'score-part', id=ident), 'part-name').text = f'Parte riconosciuta {i+1}'
        destinations.append(ET.SubElement(root, 'part', id=ident))
    report = []
    for si, (source, file) in enumerate(zip(scores, files), 1):
        source_parts = source.findall('part')
        part_maps = []
        for source_part in source_parts:
            occurrences, indexed = {}, {}
            for measure in source_part.findall('measure'):
                number = measure.get('number')
                ordinal = occurrences.get(number, 0)
                indexed[number, ordinal] = measure
                occurrences[number] = ordinal+1
            part_maps.append(indexed)
        numbers = list(dict.fromkeys(key for indexed in part_maps for key in indexed))
        if all(n.isdigit() for n, _ in numbers):
            numbers.sort(key=lambda key: (int(key[0]), key[1]))
        for pi, destination in enumerate(destinations):
            available = part_maps[pi] if pi < len(part_maps) else {}
            for bi, key in enumerate(numbers):
                number, ordinal = key
                measure = deepcopy(available[key]) if key in available else ET.Element('measure')
                measure.set('number', f'S{si}-{number}'+(f'-{ordinal+1}' if ordinal else ''))
                if bi == 0:
                    print_info = measure.find('print')
                    if print_info is None:
                        print_info = ET.Element('print')
                        measure.insert(0, print_info)
                    if si > 1:
                        print_info.set('new-page', 'yes')
                    direction = ET.Element('direction', placement='above')
                    ET.SubElement(ET.SubElement(direction, 'direction-type'), 'words').text = f'Sezione OMR {si} · da correggere'
                    measure.insert(1, direction)
                destination.append(measure)
        report.append({'sezione_omr': si, 'fonte': file.name,
                       'battute': len(numbers), 'parti': len(source_parts),
                       'note': len(source.findall('.//note/pitch')),
                       'battute_senza_note': [m.get('number') for m in source_parts[0].findall('measure')
                                             if not m.findall('note')]})
    if len(root.findall('.//note/pitch')) != sum(item['note'] for item in report):
        raise ValueError('Il libro non conserva tutte le note riconosciute')
    ET.indent(root)
    ET.ElementTree(root).write(out_path, encoding='utf-8', xml_declaration=True)
    out_path.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


def render_scanned_book(folder, out_path):
    """Ricopia ogni rigo originale; il riconoscimento non cambia le note del PDF."""
    folder = Path(folder)
    mapping = json.loads((folder / 'pagine.json').read_text())
    omr_path, = (folder / 'omr').glob('*.omr')
    c = Canvas(str(out_path), pagesize=A4)
    c.setTitle('Jacopo Napoli — Bassi: fogli di lavoro dalla scansione')
    count = page = 0
    report = []
    with ZipFile(omr_path) as z:
        for item in mapping:
            sheet = ET.fromstring(z.read(f'sheet#{item["pagina"]}/sheet#{item["pagina"]}.xml'))
            image = Image.open(folder / 'fonti' / item['immagine']).convert('RGB')
            sx = image.width / int(sheet.find('picture').get('width'))
            sy = image.height / int(sheet.find('picture').get('height'))
            staffs = sorted(sheet.findall('./page/system/part/staff'),
                            key=lambda staff: float(staff.find('lines/line/point').get('y')))
            margin_left = min(float(staff.get('left'))*sx for staff in staffs)
            bounds = []
            for staff in staffs:
                lines = staff.findall('lines/line')
                top = median(float(p.get('y')) for p in lines[0].findall('point'))*sy
                bottom = median(float(p.get('y')) for p in lines[-1].findall('point'))*sy
                bounds.append((top, bottom))
            for ri, (staff, (top, bottom)) in enumerate(zip(staffs, bounds)):
                row = ri % 4
                if row == 0:
                    page += 1
                    c.setFont('DVB', 13)
                    c.drawString(12*mm, A4[1]-15*mm, f'Jacopo Napoli · Bassi — PDF originale, pag. {item["pagina_pdf"]}')
                    c.setFont('DV', 7)
                    c.drawString(12*mm, A4[1]-21*mm, 'Rigo superiore libero: riporta anche l’armatura indicata nel basso.')
                    c.drawRightString(A4[0]-12*mm, 6*mm, str(page))
                gap = (bottom-top)/4
                ymin = max(0, top-6*gap, (bounds[ri-1][1]+top)/2 if ri else 0)
                ymax = min(image.height, bottom+3*gap,
                           (bottom+bounds[ri+1][0])/2 if ri+1 < len(bounds) else image.height)
                left = float(staff.get('left'))*sx
                right = float(staff.get('right'))*sx
                padding = 6*gap if left > margin_left+gap else gap
                xmin, xmax = max(0, int(left-padding)), min(image.width, int(right+gap))
                ymin, ymax = int(ymin), int(ymax+1)
                strip = image.crop((xmin, ymin, xmax, ymax))
                xscale = (A4[0]-24*mm)/strip.width
                yscale = S/gap
                ytop = A4[1]-30*mm-row*BASS_SYSTEM_STEP
                bass_top = ytop-4*S-66
                ybottom = bass_top-(ymax-top)*yscale
                c.drawImage(ImageReader(strip), 12*mm, ybottom,
                            width=strip.width*xscale, height=strip.height*yscale)
                x0, x1 = 12*mm+(left-xmin)*xscale, 12*mm+(right-xmin)*xscale
                treble = Staff('treble', ytop-4*S)
                draw_staff_lines(c, treble, x0, x1)
                draw_clef(c, 'treble', x0+4, treble)
                c.setLineWidth(.5)
                c.line(x0, ytop, x0, bass_top-4*S)
                count += 1
                report.append({'pagina_output': page, 'rigo_output': row+1,
                               'pagina_pdf': item['pagina_pdf'], 'lato': item['lato'],
                               'rigo_originale': ri+1})
                if row == 3 or ri == len(staffs)-1:
                    c.showPage()
    c.save()
    Path(out_path).with_suffix('.righi.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return count


if __name__ == '__main__':
    folder = Path(__file__).resolve().parents[2] / 'out' / 'librobassi'
    report = export_recognized_book(folder / 'omr', folder / 'librobassi.musicxml')
    count = render_scanned_book(folder, folder / 'librobassi.pdf')
    print(f'{count} righi originali nel PDF; {len(report)} sezioni nella bozza MusicXML.')
