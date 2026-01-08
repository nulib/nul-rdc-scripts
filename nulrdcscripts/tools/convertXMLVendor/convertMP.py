#!/usr/bin/env python3
"""
XML MediaAsset to CSV Converter
Converts XML files from MediaPreserve into a flat CSV structure for OpenRefine processing.
One row per face (side), with preservation and access master columns side-by-side.
"""

import xml.etree.ElementTree as ET
import csv
import sys
import os
import argparse
from pathlib import Path


def time_to_minutes(time_str):
    """Convert HH:MM:SS to minutes, rounding up any seconds."""
    if not time_str:
        return ''
    
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            total_minutes = hours * 60 + minutes
            # Round up if there are any seconds
            if seconds > 0:
                total_minutes += 1
            return str(total_minutes)
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            # Round up if there are any seconds
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
        # Handle formats like "2025-11-04T09:47:02" or "2025-11-04"
        if 'T' in datetime_str:
            return datetime_str.split('T')[0]
        elif ' ' in datetime_str:
            return datetime_str.split(' ')[0]
        else:
            return datetime_str
    except (ValueError, AttributeError):
        return datetime_str


def parse_xml_file(xml_file):
    """Parse a single XML file and extract relevant fields."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extract Original section data (common to all preservation/access masters)
        original = root.find('Original')
        if original is None:
            print(f"Warning: No Original section found in {xml_file}")
            return []
        
        # Build transfer comments with baked/cleaned status
        transfer_comments = get_text(original, 'TransferComments')
        baked = get_text(original, 'Baked')
        cleaned = get_text(original, 'Cleaned')
        
        # Append baked and cleaned info to transfer comments
        if transfer_comments:
            transfer_comments = f"{transfer_comments} Baked: {baked}, Cleaned: {cleaned}"
        else:
            transfer_comments = f"Baked: {baked}, Cleaned: {cleaned}"
        
        # Merge originator and transfer operator into digitizer field
        originator = get_text(original, 'Originator')
        transfer_operator = get_text(original, 'TransferOperator')
        
        if originator and transfer_operator:
            digitizer = f"{originator}; {transfer_operator}"
        elif originator:
            digitizer = originator
        elif transfer_operator:
            digitizer = transfer_operator
        else:
            digitizer = ''
        
        # Base data from Original section
        base_data = {
            'source file': os.path.basename(xml_file),
            'accession number': get_text(original, 'AssetIdentifier'),
            'barcode': get_text(original, 'ArchiveID'),
            'container markings': get_text(original, 'Markings'),
            'running time mins': time_to_minutes(get_text(original, 'RunningTime')),
            'record date': get_text(original, 'RecordDate'),
            'format': get_text(original, 'FormatType'),
            'stock brand': get_text(original, 'StockBrand'),
            'track configuration': get_text(original, 'TrackConfiguration'),
            'speed IPS': get_text(original, 'RecordingSpeed'),
            'tape model': get_text(original, 'TapeModel'),
            'sound': get_text(original, 'SoundField'),
            'noise reduction': get_text(original, 'NoiseReduction'),
            'language': get_text(original, 'Language'),
            'equalization': get_text(original, 'Equalization'),
            'transfer comments': transfer_comments,
            'digitizer': digitizer,
            'originator address': get_text(original, 'OriginatorAddress'),
            'deck equipment barcode': get_text(original, 'Deck_EquipmentBarcode'),
            'deck description': get_text(original, 'Deck_Description'),
            'deck brand': get_text(original, 'Deck_Brand'),
            'deck model': get_text(original, 'Deck_Model'),
            'deck serial number': get_text(original, 'Deck_SerialNumber'),
            'picture count': get_text(original, 'PictureCount'),
        }
        
        # Group files by face designation - collect all faces for this barcode
        files_by_face = {}
        
        # Collect PreservationMaster files
        for pm in root.findall('PreservationMaster'):
            face = get_text(pm, 'FaceDesignation')
            if face not in files_by_face:
                files_by_face[face] = {'preservation': None, 'access': None}
            
            files_by_face[face]['preservation'] = {
                'filename': get_text(pm, 'Filename'),
                'date created': extract_date_only(get_text(pm, 'DateCreated')),
                'checksum': get_text(pm, 'Checksum'),
                'checksum type': get_text(pm, 'ChecksumType'),
                'checksum date created': extract_date_only(get_text(pm, 'ChecksumDateCreated')),
                'running time minutes': time_to_minutes(get_text(pm, 'RunningTime')),
                'bit per sample': get_text(pm, 'BitPerSample'),
                'sample rate': get_text(pm, 'SampleRate'),
                'bit rate': get_text(pm, 'BitRate'),
                'sound field from jhove': get_text(pm, 'SoundFieldFromJhove'),
                'file size bytes': get_text(pm, 'FileSizeInBytes'),
                'file size kb': get_text(pm, 'FileSizeInKB'),
                'file size mb': get_text(pm, 'FileSizeInMB'),
                'file size gb': get_text(pm, 'FileSizeInGB'),
                'track designation': get_text(pm, 'TrackDesignation'),
                'region designation': get_text(pm, 'RegionDesignation'),
                'host computer manufacturer': get_text(pm, 'HostComputerManufacturer'),
                'host computer name': get_text(pm, 'HostComputerName'),
                'host computer version': get_text(pm, 'HostComputerVersion'),
                'operating system': get_text(pm, 'OperatingSystem'),
                'operating system version': get_text(pm, 'OperatingSystemVersion'),
                'a2d device type': get_text(pm, 'A2D_DeviceType'),
                'a2d device manufacturer': get_text(pm, 'A2D_DeviceManufacturer'),
                'a2d device model name': get_text(pm, 'A2D_DeviceModelName'),
                'a2d device model version': get_text(pm, 'A2D_DeviceModelVersion'),
                'a2d device driver': get_text(pm, 'A2D_DeviceDriver'),
                'encode software manufacturer': get_text(pm, 'EncodeSoftwareManufacturer'),
                'encode software': get_text(pm, 'EncodeSoftware'),
                'encode software version': get_text(pm, 'EncodeSoftwareVersion'),
            }
        
        # Collect AccessMaster files
        for am in root.findall('AccessMaster'):
            face = get_text(am, 'FaceDesignation')
            if face not in files_by_face:
                files_by_face[face] = {'preservation': None, 'access': None}
            
            files_by_face[face]['access'] = {
                'filename': get_text(am, 'Filename'),
                'date created': extract_date_only(get_text(am, 'DateCreated')),
                'checksum': get_text(am, 'Checksum'),
                'checksum type': get_text(am, 'ChecksumType'),
                'checksum date created': extract_date_only(get_text(am, 'ChecksumDateCreated')),
                'running time minutes': time_to_minutes(get_text(am, 'RunningTime')),
                'bit per sample': get_text(am, 'BitPerSample'),
                'sample rate': get_text(am, 'SampleRate'),
                'bit rate': get_text(am, 'BitRate'),
                'sound field from jhove': get_text(am, 'SoundFieldFromJhove'),
                'file size bytes': get_text(am, 'FileSizeInBytes'),
                'file size kb': get_text(am, 'FileSizeInKB'),
                'file size mb': get_text(am, 'FileSizeInMB'),
                'file size gb': get_text(am, 'FileSizeInGB'),
                'track designation': get_text(am, 'TrackDesignation'),
                'region designation': get_text(am, 'RegionDesignation'),
                'encode software manufacturer': get_text(am, 'EncodeSoftwareManufacturer'),
                'encode software': get_text(am, 'EncodeSoftware'),
                'encode software version': get_text(am, 'EncodeSoftwareVersion'),
            }
        
        # Build single record with all faces consolidated
        record = base_data.copy()
        
        # Add fields for face A (if exists)
        if 'A' in files_by_face:
            if files_by_face['A']['preservation']:
                for key, value in files_by_face['A']['preservation'].items():
                    record[f'face a pres {key}'] = value
            else:
                for key in ['filename', 'date created', 'checksum', 'checksum type', 
                           'checksum date created', 'running time minutes', 'bit per sample',
                           'sample rate', 'bit rate', 'sound field from jhove',
                           'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                           'track designation', 'region designation',
                           'host computer manufacturer', 'host computer name', 
                           'host computer version', 'operating system', 
                           'operating system version', 'a2d device type',
                           'a2d device manufacturer', 'a2d device model name',
                           'a2d device model version', 'a2d device driver',
                           'encode software manufacturer', 'encode software',
                           'encode software version']:
                    record[f'face a pres {key}'] = ''
                    
            if files_by_face['A']['access']:
                for key, value in files_by_face['A']['access'].items():
                    record[f'face a access {key}'] = value
            else:
                for key in ['filename', 'date created', 'checksum', 'checksum type',
                           'checksum date created', 'running time minutes', 'bit per sample',
                           'sample rate', 'bit rate', 'sound field from jhove',
                           'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                           'track designation', 'region designation',
                           'encode software manufacturer', 'encode software',
                           'encode software version']:
                    record[f'face a access {key}'] = ''
        else:
            # No face A - set all to empty
            for key in ['filename', 'date created', 'checksum', 'checksum type', 
                       'checksum date created', 'running time minutes', 'bit per sample',
                       'sample rate', 'bit rate', 'sound field from jhove',
                       'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                       'track designation', 'region designation',
                       'host computer manufacturer', 'host computer name', 
                       'host computer version', 'operating system', 
                       'operating system version', 'a2d device type',
                       'a2d device manufacturer', 'a2d device model name',
                       'a2d device model version', 'a2d device driver',
                       'encode software manufacturer', 'encode software',
                       'encode software version']:
                record[f'face a pres {key}'] = ''
            for key in ['filename', 'date created', 'checksum', 'checksum type',
                       'checksum date created', 'running time minutes', 'bit per sample',
                       'sample rate', 'bit rate', 'sound field from jhove',
                       'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                       'track designation', 'region designation',
                       'encode software manufacturer', 'encode software',
                       'encode software version']:
                record[f'face a access {key}'] = ''
        
        # Add fields for face B (if exists)
        if 'B' in files_by_face:
            if files_by_face['B']['preservation']:
                for key, value in files_by_face['B']['preservation'].items():
                    record[f'face b pres {key}'] = value
            else:
                for key in ['filename', 'date created', 'checksum', 'checksum type', 
                           'checksum date created', 'running time minutes', 'bit per sample',
                           'sample rate', 'bit rate', 'sound field from jhove',
                           'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                           'track designation', 'region designation',
                           'host computer manufacturer', 'host computer name', 
                           'host computer version', 'operating system', 
                           'operating system version', 'a2d device type',
                           'a2d device manufacturer', 'a2d device model name',
                           'a2d device model version', 'a2d device driver',
                           'encode software manufacturer', 'encode software',
                           'encode software version']:
                    record[f'face b pres {key}'] = ''
                    
            if files_by_face['B']['access']:
                for key, value in files_by_face['B']['access'].items():
                    record[f'face b access {key}'] = value
            else:
                for key in ['filename', 'date created', 'checksum', 'checksum type',
                           'checksum date created', 'running time minutes', 'bit per sample',
                           'sample rate', 'bit rate', 'sound field from jhove',
                           'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                           'track designation', 'region designation',
                           'encode software manufacturer', 'encode software',
                           'encode software version']:
                    record[f'face b access {key}'] = ''
        else:
            # No face B - set all to empty
            for key in ['filename', 'date created', 'checksum', 'checksum type', 
                       'checksum date created', 'running time minutes', 'bit per sample',
                       'sample rate', 'bit rate', 'sound field from jhove',
                       'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                       'track designation', 'region designation',
                       'host computer manufacturer', 'host computer name', 
                       'host computer version', 'operating system', 
                       'operating system version', 'a2d device type',
                       'a2d device manufacturer', 'a2d device model name',
                       'a2d device model version', 'a2d device driver',
                       'encode software manufacturer', 'encode software',
                       'encode software version']:
                record[f'face b pres {key}'] = ''
            for key in ['filename', 'date created', 'checksum', 'checksum type',
                       'checksum date created', 'running time minutes', 'bit per sample',
                       'sample rate', 'bit rate', 'sound field from jhove',
                       'file size bytes', 'file size kb', 'file size mb', 'file size gb',
                       'track designation', 'region designation',
                       'encode software manufacturer', 'encode software',
                       'encode software version']:
                record[f'face b access {key}'] = ''
        
        return [record]
        
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {xml_file}: {e}")
        return []


def get_text(element, tag):
    """Safely extract text from an XML element."""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ''


def process_xml_files(xml_files, output_csv):
    """Process multiple XML files and write to CSV."""
    all_records = []
    
    for xml_file in xml_files:
        print(f"Processing: {xml_file}")
        records = parse_xml_file(xml_file)
        all_records.extend(records)
    
    if not all_records:
        print("No records found to write!")
        return
    
    # Define CSV column order
    fieldnames = [
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
        'face a pres filename',
        'face a pres date created',
        'face a pres checksum',
        'face a pres checksum type',
        'face a pres checksum date created',
        'face a pres running time minutes',
        'face a pres bit per sample',
        'face a pres sample rate',
        'face a pres bit rate',
        'face a pres sound field from jhove',
        'face a pres file size bytes',
        'face a pres file size kb',
        'face a pres file size mb',
        'face a pres file size gb',
        'face a pres track designation',
        'face a pres region designation',
        'face a pres host computer manufacturer',
        'face a pres host computer name',
        'face a pres host computer version',
        'face a pres operating system',
        'face a pres operating system version',
        'face a pres a2d device type',
        'face a pres a2d device manufacturer',
        'face a pres a2d device model name',
        'face a pres a2d device model version',
        'face a pres a2d device driver',
        'face a pres encode software manufacturer',
        'face a pres encode software',
        'face a pres encode software version',
        'face a access filename',
        'face a access date created',
        'face a access checksum',
        'face a access checksum type',
        'face a access checksum date created',
        'face a access running time minutes',
        'face a access bit per sample',
        'face a access sample rate',
        'face a access bit rate',
        'face a access sound field from jhove',
        'face a access file size bytes',
        'face a access file size kb',
        'face a access file size mb',
        'face a access file size gb',
        'face a access track designation',
        'face a access region designation',
        'face a access encode software manufacturer',
        'face a access encode software',
        'face a access encode software version',
        'face b pres filename',
        'face b pres date created',
        'face b pres checksum',
        'face b pres checksum type',
        'face b pres checksum date created',
        'face b pres running time minutes',
        'face b pres bit per sample',
        'face b pres sample rate',
        'face b pres bit rate',
        'face b pres sound field from jhove',
        'face b pres file size bytes',
        'face b pres file size kb',
        'face b pres file size mb',
        'face b pres file size gb',
        'face b pres track designation',
        'face b pres region designation',
        'face b pres host computer manufacturer',
        'face b pres host computer name',
        'face b pres host computer version',
        'face b pres operating system',
        'face b pres operating system version',
        'face b pres a2d device type',
        'face b pres a2d device manufacturer',
        'face b pres a2d device model name',
        'face b pres a2d device model version',
        'face b pres a2d device driver',
        'face b pres encode software manufacturer',
        'face b pres encode software',
        'face b pres encode software version',
        'face b access filename',
        'face b access date created',
        'face b access checksum',
        'face b access checksum type',
        'face b access checksum date created',
        'face b access running time minutes',
        'face b access bit per sample',
        'face b access sample rate',
        'face b access bit rate',
        'face b access sound field from jhove',
        'face b access file size bytes',
        'face b access file size kb',
        'face b access file size mb',
        'face b access file size gb',
        'face b access track designation',
        'face b access region designation',
        'face b access encode software manufacturer',
        'face b access encode software',
        'face b access encode software version',
    ]
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(all_records)
    
    print(f"\nSuccess! Wrote {len(all_records)} records to {output_csv}")
    print(f"Processed {len(xml_files)} XML files")


def main():
    parser = argparse.ArgumentParser(
        description='Convert MediaPreserve XML files to TSV format for OpenRefine processing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i /path/to/xml/folder/
  %(prog)s --input ~/Desktop/MediaPreserve_XMLs/
  %(prog)s -i ~/Desktop/Batch_01/ -o custom_name.tsv

The script will:
  1. Recursively search the folder and all subfolders for .xml files
  2. Process all XML files found
  3. Create TSV file in the specified folder (default: <foldername>_xml_converted.tsv)
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
        help='Name for output TSV file (default: <foldername>_xml_converted.tsv)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    input_path = args.folder
    base_dir = Path(input_path)
    
    if not base_dir.exists():
        print(f"Error: '{input_path}' does not exist!")
        sys.exit(1)
    
    if not base_dir.is_dir():
        print(f"Error: '{input_path}' is not a directory!")
        sys.exit(1)
    
    # Generate output filename from folder name if not provided
    if args.output_name is None:
        folder_name = base_dir.name
        output_filename = f"{folder_name}_xml_converted.tsv"
    else:
        output_filename = args.output_name
    
    # Output file will be in the same directory
    output_csv = base_dir / output_filename
    
    # Recursively collect all XML files from directory and subdirectories
    xml_files = []
    xml_files.extend(base_dir.rglob('*.xml'))
    xml_files.extend(base_dir.rglob('*.XML'))
    
    if not xml_files:
        print(f"Error: No XML files found in '{input_path}' or its subdirectories!")
        sys.exit(1)
    
    print(f"Searching in: {base_dir}")
    print(f"Found {len(xml_files)} XML files in directory and subdirectories\n")
    print("Processing files:")
    for xml_file in xml_files:
        # Show relative path from base directory
        rel_path = xml_file.relative_to(base_dir)
        print(f"  - {rel_path}")
    print()
    
    process_xml_files(xml_files, output_csv)
    
    print(f"\nOutput saved to: {output_csv}")


if __name__ == '__main__':
    main()