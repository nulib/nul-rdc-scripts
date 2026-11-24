#!/usr/bin/env python3
"""
XML MediaAsset to XLSX/TSV Converter
Converts vendor MediaAsset XML files (MediaPreserve, Preserve South) into a flat
table (.xlsx by default, or TSV) for Excel / OpenRefine processing.
One row per barcode (per-side XMLs are merged), with preservation and access master columns grouped per side.
Vendor face designations (A, B, ...) are output as sides (1, 2, ...).

Vendor differences handled:
- Preserve South uses <ChecksumValue> instead of <Checksum> on master elements.
- Preserve South adds carrier fields (TapeWidth, ReelSize, TapeType, PackOrientation,
  CassetteType, StudioXferMethod, VideoCorrectionDevice*), extra A/D and DIO device
  fields, and repeated <Photograph>/<Checksum>/<FileSizeInKB> groups under <Original>.
"""

import xml.etree.ElementTree as ET
import csv
import sys
import os
import argparse
from pathlib import Path


# Technical fields kept from PreservationMaster / AccessMaster elements, in the
# order they appear in the consolidated "side N preservation/access" cell.
# Encoding-chain fields (host computer, OS, A/D, DIO, encode software) are
# intentionally omitted; add them back here if needed.
FILE_FIELDS = [
    'filename',
    'running time',
    'sample rate',
    'bit per sample',
    'bit rate',
    'sound field from jhove',
    'file size bytes',
    'checksum type',
    'checksum',
    'checksum date created',
    'date created',
    'track designation',
    'region designation',
]
PRES_FIELDS = ACCESS_FIELDS = FILE_FIELDS

# Separator between "label: value" pairs inside a consolidated cell
CELL_SEP = '; '

# XML tag -> field name mapping for PreservationMaster / AccessMaster elements.
# Multiple tags may map to one field (vendor aliases); the first non-empty wins.
FILE_TAG_MAP = {
    'Filename':                 'filename',
    'DateCreated':              'date created',
    'Checksum':                 'checksum',        # MediaPreserve
    'ChecksumValue':            'checksum',        # Preserve South
    'ChecksumType':             'checksum type',
    'ChecksumDateCreated':      'checksum date created',
    'RunningTime':              'running time',
    'BitPerSample':             'bit per sample',
    'SampleRate':               'sample rate',
    'BitRate':                  'bit rate',
    'SoundFieldFromJhove':      'sound field from jhove',
    'FileSizeInBytes':          'file size bytes',
    'FileSizeInKB':             'file size kb',
    'FileSizeInMB':             'file size mb',
    'FileSizeInGB':             'file size gb',
    'TrackDesignation':         'track designation',
    'RegionDesignation':        'region designation',
    'HostComputerManufacturer': 'host computer manufacturer',
    'HostComputerName':         'host computer name',
    'HostComputerVersion':      'host computer version',
    'OperatingSystem':          'operating system',
    'OperatingSystemVersion':   'operating system version',
    'A2D_DeviceType':           'a2d device type',
    'A2D_DeviceManufacturer':   'a2d device manufacturer',
    'A2D_DeviceModelName':      'a2d device model name',
    'A2D_DeviceModelVersion':   'a2d device model version',
    'A2D_DeviceModelSerialNumber': 'a2d device model serial number',
    'A2D_DeviceDriver':         'a2d device driver',
    'A2D_DeviceDriverVersion':  'a2d device driver version',
    'DIO_DeviceManufacturer':   'dio device manufacturer',
    'DIO_DeviceModelName':      'dio device model name',
    'DIO_DeviceModelVersion':   'dio device model version',
    'DIO_DeviceDriver':         'dio device driver',
    'DIO_DeviceDriverVersion':  'dio device driver version',
    'EncodeSoftwareManufacturer': 'encode software manufacturer',
    'EncodeSoftware':           'encode software',
    'EncodeSoftwareVersion':    'encode software version',
}

# New columns are appended after the original MediaPreserve set so existing
# OpenRefine column positions are unchanged.
BASE_FIELDNAMES = [
    'source file',
    'accession number',
    'barcode',
    'container markings',
    'running time mins',
    'record date',
    'format',
    'stock brand',
    'tape model',
    'track configuration',
    'speed IPS',
    'sound',
    'noise reduction',
    'language',
    'equalization',
    'transfer comments',
    'digitizer',
    'originator address',
    'deck equipment barcode',
    'deck description',
    'deck brand',
    'deck model',
    'deck serial number',
    'picture count',
    # Preserve South additions
    'tape width',
    'reel size',
    'tape type',
    'pack orientation',
    'cassette type',
    'studio transfer method',
    'photographs',
    'photograph checksums',
    'photograph file sizes kb',
    'capture date',
    'discrepancies',
]


def time_to_minutes(time_str):
    """Convert HH:MM:SS to minutes, rounding up any seconds."""
    if not time_str:
        return ''
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            total_minutes = hours * 60 + minutes
            if seconds > 0:
                total_minutes += 1
            return str(total_minutes)
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            if seconds > 0:
                minutes += 1
            return str(minutes)
        else:
            return time_str
    except (ValueError, AttributeError):
        return time_str


def extract_date_only(datetime_str):
    """Extract only the date portion from a datetime string."""
    if not datetime_str:
        return ''
    try:
        if 'T' in datetime_str:
            return datetime_str.split('T')[0]
        elif ' ' in datetime_str:
            return datetime_str.split(' ')[0]
        else:
            return datetime_str
    except (ValueError, AttributeError):
        return datetime_str


# Vendor placeholder values treated as empty so they don't get transferred as data
NULL_VALUES = {'n/a', 'na', 'none', 'null'}


def clean(text):
    """Strip whitespace and blank out vendor placeholder values like 'N/A'."""
    text = text.strip() if text else ''
    return '' if text.lower() in NULL_VALUES else text


def get_text(element, tag):
    """Safely extract text from an XML element."""
    child = element.find(tag)
    return clean(child.text) if child is not None else ''


def parse_file_element(element, field_list):
    """
    Extract fields from a PreservationMaster or AccessMaster element.
    Returns a dict keyed by field name (from FILE_TAG_MAP), with date/time
    conversions applied. Missing fields default to empty string.
    """
    data = {field: '' for field in field_list}

    for xml_tag, field_name in FILE_TAG_MAP.items():
        if field_name not in data or data[field_name]:
            continue  # not wanted, or already filled by an alias
        raw = get_text(element, xml_tag)
        if not raw:
            continue
        if field_name in ('date created', 'checksum date created'):
            data[field_name] = extract_date_only(raw)
        else:
            data[field_name] = raw

    return data


def parse_photographs(original):
    """
    Preserve South lists photos as repeated sibling groups under <Original>:
    <Photograph>, <Checksum>, <FileSizeInKB>. Walk children in order and attach
    each Checksum/FileSizeInKB to the most recent Photograph.
    Returns semicolon-joined strings (filenames, checksums, sizes), aligned by position.
    """
    photos = []
    for child in original:
        text = clean(child.text)
        if child.tag == 'Photograph':
            photos.append({'file': text, 'checksum': '', 'size': ''})
        elif photos and child.tag == 'Checksum':
            photos[-1]['checksum'] = text
        elif photos and child.tag == 'FileSizeInKB':
            photos[-1]['size'] = text
    return (
        '; '.join(p['file'] for p in photos),
        '; '.join(p['checksum'] for p in photos),
        '; '.join(p['size'] for p in photos),
    )


def time_to_seconds(time_str):
    """Convert HH:MM:SS (or MM:SS) to integer seconds; None if unparseable."""
    try:
        total = 0
        for part in time_str.split(':'):
            total = total * 60 + int(part)
        return total
    except (ValueError, AttributeError):
        return None


def find_discrepancies(original, root):
    """
    Flag places where the vendor's carrier notes disagree with the delivered files,
    or where the delivered files disagree with each other. Returns a '; '-joined string.
    """
    issues = []

    # Running time: carrier vs. sum of preservation faces, and pres vs. access per face
    orig_rt = get_text(original, 'RunningTime')
    pres_rt, access_rt = {}, {}
    for tag, store in (('PreservationMaster', pres_rt), ('AccessMaster', access_rt)):
        for el in root.findall(tag):
            face = get_side(el)
            store[face] = get_text(el, 'RunningTime')

    pres_secs = [time_to_seconds(t) for t in pres_rt.values()]
    if orig_rt and pres_secs and None not in pres_secs:
        if time_to_seconds(orig_rt) != sum(pres_secs):
            faces = ', '.join(f'{f} {t}' for f, t in sorted(pres_rt.items()))
            issues.append(f'running time: carrier {orig_rt} vs pres side {faces}')

    for face in sorted(set(pres_rt) | set(access_rt)):
        if face not in pres_rt:
            issues.append(f'side {face}: access master with no preservation master')
        elif face not in access_rt:
            issues.append(f'side {face}: preservation master with no access master')
        elif pres_rt[face] != access_rt[face]:
            issues.append(f'side {face} running time: pres {pres_rt[face]} vs access {access_rt[face]}')

    # Sound field: carrier description vs. channel count JHOVE reports on the files
    sound = get_text(original, 'SoundField').lower()
    expected = {'mono': '1', 'stereo': '2'}.get(sound)
    if expected:
        for tag in ('PreservationMaster', 'AccessMaster'):
            for el in root.findall(tag):
                ch = get_text(el, 'SoundFieldFromJhove')
                if ch and ch != expected:
                    face = get_side(el)
                    kind = 'pres' if tag == 'PreservationMaster' else 'access'
                    note = ' (verify: dual/mixed mono?)' if sound == 'mono' and ch == '2' else ''
                    issues.append(f'sound field: carrier {sound} vs side {face} {kind} {ch} ch{note}')

    # Picture count vs. photographs actually listed
    count = get_text(original, 'PictureCount')
    listed = len(original.findall('Photograph'))
    if count and listed and count != str(listed):
        issues.append(f'picture count: {count} stated vs {listed} listed')

    return '; '.join(issues)


def get_side(element):
    """Convert vendor FaceDesignation (A, B, ...) to a side number (1, 2, ...)."""
    face = get_text(element, 'FaceDesignation').upper()
    if len(face) == 1 and face.isalpha():
        return str(ord(face) - ord('A') + 1)
    return face or 'UNKNOWN'


def consolidate(data):
    """Collapse parsed file fields into one 'label: value; ...' string, skipping empties."""
    if not data:
        return ''
    return CELL_SEP.join(f'{f}: {data[f]}' for f in FILE_FIELDS if data.get(f))


def parse_xml_file(xml_file):
    """Parse a single vendor MediaAsset XML file. Returns a list of record dicts."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        original = root.find('Original')
        if original is None:
            print(f"Warning: No <Original> section found in {xml_file}")
            return []

        # Build transfer comments with baked/cleaned status
        transfer_comments = get_text(original, 'TransferComments')
        baked = get_text(original, 'Baked')
        cleaned = get_text(original, 'Cleaned')
        transfer_comments = (
            f"{transfer_comments} Baked: {baked}, Cleaned: {cleaned}"
            if transfer_comments
            else f"Baked: {baked}, Cleaned: {cleaned}"
        )

        # Merge originator + transfer operator into digitizer
        originator = get_text(original, 'Originator')
        transfer_operator = get_text(original, 'TransferOperator')
        if originator and transfer_operator:
            digitizer = f"{originator}; {transfer_operator}"
        else:
            digitizer = originator or transfer_operator

        photo_files, photo_checksums, photo_sizes = parse_photographs(original)

        base_data = {
            'source file':            os.path.basename(xml_file),
            'accession number':       get_text(original, 'AssetIdentifier'),
            'barcode':                get_text(original, 'ArchiveID'),
            'container markings':     get_text(original, 'Markings'),
            'running time mins':      time_to_minutes(get_text(original, 'RunningTime')),
            'record date':            get_text(original, 'RecordDate'),
            'format':                 get_text(original, 'FormatType'),
            'stock brand':            get_text(original, 'StockBrand'),
            'track configuration':    get_text(original, 'TrackConfiguration'),
            'speed IPS':              get_text(original, 'RecordingSpeed'),
            'tape model':             get_text(original, 'TapeModel'),
            'sound':                  get_text(original, 'SoundField'),
            'noise reduction':        get_text(original, 'NoiseReduction'),
            'language':               get_text(original, 'Language'),
            'equalization':           get_text(original, 'Equalization'),
            'transfer comments':      transfer_comments,
            'digitizer':              digitizer,
            'originator address':     get_text(original, 'OriginatorAddress'),
            'deck equipment barcode': get_text(original, 'Deck_EquipmentBarcode'),
            'deck description':       get_text(original, 'Deck_Description'),
            'deck brand':             get_text(original, 'Deck_Brand'),
            'deck model':             get_text(original, 'Deck_Model'),
            'deck serial number':     get_text(original, 'Deck_SerialNumber'),
            'picture count':          get_text(original, 'PictureCount'),
            # Preserve South additions
            'tape width':             get_text(original, 'TapeWidth'),
            'reel size':              get_text(original, 'ReelSize'),
            'tape type':              get_text(original, 'TapeType'),
            'pack orientation':       get_text(original, 'PackOrientation'),
            'cassette type':          get_text(original, 'CassetteType'),
            'studio transfer method': get_text(original, 'StudioXferMethod'),
            'photographs':              photo_files,
            'photograph checksums':     photo_checksums,
            'photograph file sizes kb': photo_sizes,
            'discrepancies':            find_discrepancies(original, root),
        }

        # Collect all faces dynamically — normalize to uppercase
        files_by_face = {}

        for pm in root.findall('PreservationMaster'):
            face = get_side(pm)
            files_by_face.setdefault(face, {'preservation': None, 'access': None})
            files_by_face[face]['preservation'] = parse_file_element(pm, PRES_FIELDS)

        for am in root.findall('AccessMaster'):
            face = get_side(am)
            files_by_face.setdefault(face, {'preservation': None, 'access': None})
            files_by_face[face]['access'] = parse_file_element(am, ACCESS_FIELDS)

        if not files_by_face:
            print(f"Warning: No PreservationMaster or AccessMaster elements found in {xml_file}")
            return [base_data]

        # Build record — one preservation and one access column per side
        record = base_data.copy()

        # Capture date from the first side's preservation master. Preserve South
        # has no DateCreated, so fall back to the checksum date.
        first_pres = next((files_by_face[f]['preservation'] for f in sorted(files_by_face)
                           if files_by_face[f]['preservation']), {})
        record['capture date'] = (first_pres.get('date created')
                                  or first_pres.get('checksum date created', ''))
        for face in sorted(files_by_face):
            record[f'side {face} preservation'] = consolidate(files_by_face[face]['preservation'])
            record[f'side {face} access'] = consolidate(files_by_face[face]['access'])

        # Hidden keys used by merge_by_barcode (not written to output)
        record['_sides'] = sorted(files_by_face, key=lambda f: f.zfill(4))
        record['_rt_secs'] = time_to_seconds(get_text(original, 'RunningTime'))

        return [record]

    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {xml_file}: {e}")
        return []


# Fields expected to differ between per-side XMLs: labeled by side, not flagged
PER_SIDE_FIELDS = {'transfer comments'}


def side_label(record):
    """'side 1', 'sides 1, 2', or the source file if no sides were found."""
    sides = record.get('_sides') or []
    if not sides:
        return record.get('source file', '?')
    return ('side ' if len(sides) == 1 else 'sides ') + ', '.join(sides)


def merge_photos(group):
    """Union photographs across XMLs (deduped by filename), keeping columns aligned."""
    seen = {}
    for r in group:
        files = [x for x in r.get('photographs', '').split('; ') if x]
        sums = r.get('photograph checksums', '').split('; ')
        sizes = r.get('photograph file sizes kb', '').split('; ')
        for i, f in enumerate(files):
            if f not in seen:
                seen[f] = (sums[i] if i < len(sums) else '', sizes[i] if i < len(sizes) else '')
    return (
        '; '.join(seen),
        '; '.join(v[0] for v in seen.values()),
        '; '.join(v[1] for v in seen.values()),
        str(len(seen)) if seen else '',
    )


def merge_by_barcode(records):
    """
    Combine records that share a barcode into one row. Some vendors (Preserve
    South) deliver one XML per side; MediaPreserve delivers one XML per barcode,
    which passes through unchanged.

    - side columns: taken from whichever XML has them
    - running time mins: carrier running times summed across XMLs
    - photographs: unioned; picture count = number of unique photos
    - capture date: earliest
    - other fields: one value if all XMLs agree; otherwise "side 1: X | side 2: Y",
      and (except transfer comments) flagged in discrepancies
    """
    groups = {}
    for r in records:
        key = r.get('barcode') or f"__nobarcode__{r.get('source file')}"
        groups.setdefault(key, []).append(r)

    merged = []
    for group in groups.values():
        group.sort(key=lambda r: [s.zfill(4) for s in r.get('_sides') or []])
        if len(group) == 1:
            merged.append({k: v for k, v in group[0].items() if not k.startswith('_')})
            continue

        out, issues = {}, []
        for r in group:
            issues.extend(i for i in r.get('discrepancies', '').split('; ') if i)

        keys = []
        for r in group:
            keys.extend(k for k in r if k not in keys and not k.startswith('_'))

        for k in keys:
            vals = [(side_label(r), r.get(k, '')) for r in group]
            filled = [(lbl, v) for lbl, v in vals if v]
            unique = list(dict.fromkeys(v for _, v in filled))

            if k.startswith('side '):
                out[k] = unique[0] if unique else ''
                if len(unique) > 1:
                    out[k] = ' || '.join(unique)
                    issues.append(f'{k} delivered in more than one XML')
            elif k == 'source file':
                out[k] = '; '.join(v for _, v in vals)
            elif k == 'running time mins':
                secs = [r.get('_rt_secs') for r in group]
                if all(isinstance(x, int) for x in secs):
                    total = sum(secs)
                    out[k] = time_to_minutes(f'{total // 3600}:{total % 3600 // 60:02d}:{total % 60:02d}')
                else:
                    out[k] = ' | '.join(f'{lbl}: {v}' for lbl, v in filled)
            elif k == 'capture date':
                out[k] = min(unique) if unique else ''
            elif k in ('photographs', 'photograph checksums', 'photograph file sizes kb', 'picture count', 'discrepancies'):
                continue  # handled below
            elif len(unique) <= 1:
                out[k] = unique[0] if unique else ''
            else:
                out[k] = ' | '.join(f'{lbl}: {v}' for lbl, v in filled)
                if k not in PER_SIDE_FIELDS:
                    issues.append(f'{k} differs between side XMLs')

        (out['photographs'], out['photograph checksums'],
         out['photograph file sizes kb'], out['picture count']) = merge_photos(group)
        out['discrepancies'] = '; '.join(dict.fromkeys(issues))
        merged.append(out)

    return merged


def collect_xml_files(base_dir):
    """
    Recursively collect XML files, case-insensitively, deduplicated.
    Excludes the output file (not an issue since we glob only .xml, but
    also guards against re-processing a previous run's output if renamed).
    """
    seen = set()
    result = []
    for p in base_dir.rglob('*'):
        if p.suffix.lower() == '.xml' and p.resolve() not in seen:
            seen.add(p.resolve())
            result.append(p)
    return sorted(result)


def build_fieldnames(all_records):
    """
    Derive the full ordered fieldname list from all collected records.
    Base fields come first in defined order; side columns follow
    (side 1 preservation, side 1 access, side 2 preservation, ...).
    """
    face_cols = []
    seen = set(BASE_FIELDNAMES)
    for record in all_records:
        for key in record:
            if key not in seen:
                face_cols.append(key)
                seen.add(key)

    # Sort face columns: group by face label, then pres before access
    def face_sort_key(col):
        # col format: "side N preservation/access"
        parts = col.split(' ')
        side = parts[1] if len(parts) > 1 else ''
        master = 0 if (len(parts) > 2 and parts[2] == 'preservation') else 1
        return (side.zfill(4), master)

    face_cols.sort(key=face_sort_key)
    return BASE_FIELDNAMES + face_cols


def write_xlsx(records, fieldnames, path):
    """
    Write an .xlsx with every cell stored and formatted as Text, so Excel never
    converts barcodes to scientific notation or drops leading zeros.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = 'xml_converted'
    ws.append(fieldnames)
    for r in records:
        ws.append([r.get(f, '') for f in fieldnames])
    for row in ws.iter_rows():
        for cell in row:
            cell.number_format = '@'
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions
    for i, f in enumerate(fieldnames, 1):
        width = max([len(f)] + [len(str(r.get(f, ''))) for r in records])
        ws.column_dimensions[get_column_letter(i)].width = min(max(width, 8) + 2, 60)
    wb.save(path)


def process_xml_files(xml_files, output_path, excel=False):
    """Process all XML files, merge by barcode, and write an .xlsx (or a TSV with --tsv)."""
    all_records = []

    for xml_file in xml_files:
        print(f"  Processing: {xml_file}")
        all_records.extend(parse_xml_file(xml_file))

    if not all_records:
        print("No records found to write.")
        return

    xml_count = len(all_records)
    all_records = merge_by_barcode(all_records)
    fieldnames = build_fieldnames(all_records)

    if excel:
        write_xlsx(all_records, fieldnames, output_path)
    else:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_records)

    print(f"\nWrote {len(all_records)} barcode(s) from {xml_count} XML file(s) to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert vendor MediaAsset XML files (MediaPreserve, Preserve South) to .xlsx (or TSV) for Excel / OpenRefine.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i /path/to/xml/folder/
  %(prog)s -i ~/Desktop/Batch_01/ -o custom_name.xlsx
  %(prog)s -i ~/Desktop/Batch_01/ --tsv
        """
    )
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        dest='folder',
        help='Path to folder containing XML files (searches recursively)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        dest='output_name',
        help='Output filename (default: <foldername>_xml_converted.xlsx; a .tsv name writes a TSV)'
    )
    parser.add_argument(
        '--tsv',
        action='store_true',
        help='Write a tab-separated file instead of .xlsx'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 2.1.0')

    args = parser.parse_args()
    base_dir = Path(args.folder)

    if not base_dir.exists():
        print(f"Error: '{args.folder}' does not exist.")
        sys.exit(1)
    if not base_dir.is_dir():
        print(f"Error: '{args.folder}' is not a directory.")
        sys.exit(1)

    as_tsv = args.tsv or (args.output_name or '').lower().endswith('.tsv')
    ext = 'tsv' if as_tsv else 'xlsx'
    output_filename = args.output_name or f"{base_dir.name}_xml_converted.{ext}"
    output_path = base_dir / output_filename

    xml_files = collect_xml_files(base_dir)

    if not xml_files:
        print(f"Error: No XML files found in '{args.folder}' or its subdirectories.")
        sys.exit(1)

    print(f"Input:  {base_dir}")
    print(f"Output: {output_path}")
    print(f"Found {len(xml_files)} XML file(s)\n")

    process_xml_files(xml_files, output_path, excel=not as_tsv)


if __name__ == '__main__':
    main()
