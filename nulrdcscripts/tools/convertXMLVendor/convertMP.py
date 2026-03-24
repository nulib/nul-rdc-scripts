#!/usr/bin/env python3
"""
XML MediaAsset to TSV Converter
Converts XML files from MediaPreserve into a flat TSV structure for OpenRefine processing.
One row per barcode, with preservation and access master columns side-by-side per face.
Handles any number of face designations dynamically.
"""

import xml.etree.ElementTree as ET
import csv
import sys
import os
import argparse
from pathlib import Path


# Fields present on PreservationMaster elements
PRES_FIELDS = [
    'filename',
    'date created',
    'checksum',
    'checksum type',
    'checksum date created',
    'running time minutes',
    'bit per sample',
    'sample rate',
    'bit rate',
    'sound field from jhove',
    'file size bytes',
    'file size kb',
    'file size mb',
    'file size gb',
    'track designation',
    'region designation',
    'host computer manufacturer',
    'host computer name',
    'host computer version',
    'operating system',
    'operating system version',
    'a2d device type',
    'a2d device manufacturer',
    'a2d device model name',
    'a2d device model version',
    'a2d device driver',
    'encode software manufacturer',
    'encode software',
    'encode software version',
]

# Fields present on AccessMaster elements (subset of PRES_FIELDS — no host/a2d fields)
ACCESS_FIELDS = [
    'filename',
    'date created',
    'checksum',
    'checksum type',
    'checksum date created',
    'running time minutes',
    'bit per sample',
    'sample rate',
    'bit rate',
    'sound field from jhove',
    'file size bytes',
    'file size kb',
    'file size mb',
    'file size gb',
    'track designation',
    'region designation',
    'encode software manufacturer',
    'encode software',
    'encode software version',
]

# XML tag -> field name mapping for PreservationMaster / AccessMaster elements
FILE_TAG_MAP = {
    'Filename':                 'filename',
    'DateCreated':              'date created',
    'Checksum':                 'checksum',
    'ChecksumType':             'checksum type',
    'ChecksumDateCreated':      'checksum date created',
    'RunningTime':              'running time minutes',
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
    'A2D_DeviceDriver':         'a2d device driver',
    'EncodeSoftwareManufacturer': 'encode software manufacturer',
    'EncodeSoftware':           'encode software',
    'EncodeSoftwareVersion':    'encode software version',
}

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


def get_text(element, tag):
    """Safely extract text from an XML element."""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ''


def parse_file_element(element, field_list):
    """
    Extract fields from a PreservationMaster or AccessMaster element.
    Returns a dict keyed by field name (from FILE_TAG_MAP), with date/time
    conversions applied. Missing fields default to empty string.
    """
    data = {field: '' for field in field_list}

    for xml_tag, field_name in FILE_TAG_MAP.items():
        if field_name not in data:
            continue
        raw = get_text(element, xml_tag)
        if field_name == 'running time minutes':
            data[field_name] = time_to_minutes(raw)
        elif field_name in ('date created', 'checksum date created'):
            data[field_name] = extract_date_only(raw)
        else:
            data[field_name] = raw

    return data


def face_columns(face_label, master_type, field_list):
    """Return the ordered list of column names for a given face + master type."""
    label = face_label.lower()
    return [f'face {label} {master_type} {field}' for field in field_list]


def empty_face_record(face_label, master_type, field_list):
    """Return a dict of empty strings for all columns of a face + master type."""
    return {col: '' for col in face_columns(face_label, master_type, field_list)}


def filled_face_record(face_label, master_type, field_list, data):
    """Map parsed field data to prefixed column names."""
    label = face_label.lower()
    return {f'face {label} {master_type} {field}': data.get(field, '') for field in field_list}


def parse_xml_file(xml_file):
    """Parse a single MediaPreserve XML file. Returns a list of record dicts."""
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
        }

        # Collect all faces dynamically — normalize to uppercase
        files_by_face = {}

        for pm in root.findall('PreservationMaster'):
            face = get_text(pm, 'FaceDesignation').upper() or 'UNKNOWN'
            files_by_face.setdefault(face, {'preservation': None, 'access': None})
            files_by_face[face]['preservation'] = parse_file_element(pm, PRES_FIELDS)

        for am in root.findall('AccessMaster'):
            face = get_text(am, 'FaceDesignation').upper() or 'UNKNOWN'
            files_by_face.setdefault(face, {'preservation': None, 'access': None})
            files_by_face[face]['access'] = parse_file_element(am, ACCESS_FIELDS)

        if not files_by_face:
            print(f"Warning: No PreservationMaster or AccessMaster elements found in {xml_file}")
            return [base_data]

        # Build record — one column set per face, sorted for deterministic output
        record = base_data.copy()
        for face in sorted(files_by_face):
            pres_data = files_by_face[face]['preservation']
            access_data = files_by_face[face]['access']

            if pres_data:
                record.update(filled_face_record(face, 'pres', PRES_FIELDS, pres_data))
            else:
                record.update(empty_face_record(face, 'pres', PRES_FIELDS))

            if access_data:
                record.update(filled_face_record(face, 'access', ACCESS_FIELDS, access_data))
            else:
                record.update(empty_face_record(face, 'access', ACCESS_FIELDS))

        return [record]

    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {xml_file}: {e}")
        return []


def collect_xml_files(base_dir):
    """
    Recursively collect XML files, case-insensitively, deduplicated.
    Excludes the output TSV (not an issue since we glob only .xml, but
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
    Base fields come first in defined order; face columns follow, sorted
    so faces are grouped (face a pres ..., face a access ..., face b ...).
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
        # col format: "face X pres/access fieldname"
        parts = col.split(' ', 3)  # ['face', 'X', 'pres/access', 'fieldname']
        face = parts[1] if len(parts) > 1 else ''
        master = 0 if (len(parts) > 2 and parts[2] == 'pres') else 1
        field = parts[3] if len(parts) > 3 else ''
        return (face, master, field)

    face_cols.sort(key=face_sort_key)
    return BASE_FIELDNAMES + face_cols


def process_xml_files(xml_files, output_tsv):
    """Process all XML files and write combined output to TSV."""
    all_records = []

    for xml_file in xml_files:
        print(f"  Processing: {xml_file}")
        records = parse_xml_file(xml_file)
        all_records.extend(records)

    if not all_records:
        print("No records found to write.")
        return

    fieldnames = build_fieldnames(all_records)

    with open(output_tsv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_records)

    print(f"\nWrote {len(all_records)} record(s) to {output_tsv}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert MediaPreserve XML files to TSV for OpenRefine processing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i /path/to/xml/folder/
  %(prog)s -i ~/Desktop/Batch_01/ -o custom_name.tsv
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
        help='Output TSV filename (default: <foldername>_xml_converted.tsv)'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0')

    args = parser.parse_args()
    base_dir = Path(args.folder)

    if not base_dir.exists():
        print(f"Error: '{args.folder}' does not exist.")
        sys.exit(1)
    if not base_dir.is_dir():
        print(f"Error: '{args.folder}' is not a directory.")
        sys.exit(1)

    output_filename = args.output_name or f"{base_dir.name}_xml_converted.tsv"
    output_tsv = base_dir / output_filename

    xml_files = collect_xml_files(base_dir)

    if not xml_files:
        print(f"Error: No XML files found in '{args.folder}' or its subdirectories.")
        sys.exit(1)

    print(f"Input:  {base_dir}")
    print(f"Output: {output_tsv}")
    print(f"Found {len(xml_files)} XML file(s)\n")

    process_xml_files(xml_files, output_tsv)


if __name__ == '__main__':
    main()