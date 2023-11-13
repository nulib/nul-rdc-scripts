#!/usr/bin/env python3

import glob
import os
import csv
from iqc_parameters import args


def exiftool_check():
    '''checks that exiftool exists by running its -ver command'''
    try:
        subprocess.check_output([args.exiftool_path, '-ver']).decode("ascii").rstrip()
    except:
        print("Error locating exiftool")
        quit()


def find_inventories():
    '''
    '''
    if args.source_inventory:
        source_inventories = args.source_inventory
    else:
        print('\n*** Checking input directory for CSV files ***')
        source_inventories = glob.glob(os.path.join(args.input_path, "*.csv"))
        #source_inventories = [i for i in source_inventories if not '-meadow_ingest_inventory.csv' in i]
        if not source_inventories:
            print("\n+++ ERROR: Unable to find inventory +++")
            quit()
        else:
            print("Inventories found\n")
    return(source_inventories)


def import_inventories(source_inventories):
    '''
    '''
    required_inventory_fields = ['filename', 'role']
    source_inventory_dictlist = []
    for i in source_inventories:
        if os.path.isfile(i):
            csvDict = []
            with open(i, encoding='utf-8')as f:
                reader = csv.DictReader(f, delimiter=',')
                missing_fieldnames = [a for a in required_inventory_fields if not a in reader.fieldnames]
                if missing_fieldnames:
                    print('\n--- ERROR: Inventory is missing the following columns: ' + str(missing_fieldnames))
                for row in reader:
                    csvData = {
                    'filename' : row['filename'],
                    'role' : row ['role']
                    }
                    csvDict.append(csvData)
        else:
            print('\n--- ERROR: ' + i + ' is not a file ---\n')
            quit()
        source_inventory_dictlist.extend(csvDict)
    return source_inventory_dictlist


def generate_inventory_filename_list(source_inventory_dictlist):
    '''
    '''
    inventory_filename_list = []
    for i in source_inventory_dictlist:
        inventory_filename_list.append(i.get('filename'))
    return inventory_filename_list


def clean_file_list(files):
    '''
    skip file types we don't want
    '''
    files = [f for f in files if not f[0] == '.']
    files = [f for f in files if not f == 'Thumbs.db']
    files = [f for f in files if not f.endswith('.md5')]
    files = [f for f in files if not f.endswith('.csv')]
    return(files)


def get_directory_size(directory):
    '''
    Returns the `directory` size in bytes
    '''
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total


def get_size_format(b, factor=1024, suffix="B"):
    '''
    Scale bytes to its proper byte format
    e.g: 1253656678 = '1.17GB'
    '''
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def generate_checksums(filename, file, checksum_type):
    '''
    Uses hashlib to return an MD5 checksum of an input filename
    '''
    #TODO Remove passing 'file' variable to this?
    read_size = 0
    last_percent_done = 0
    method_to_call = getattr(hashlib, checksum_type)
    chksm = method_to_call()
    total_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        while True:
            #2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write(checksum_type + ' ' + file + ': ' + '[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
        print()
    checksum_output = chksm.hexdigest()
    return checksum_output

def interpret_checksum_command():
    '''
    checks if argument used with verify_checksums is valid
    '''
    #TODO update this to take a single value rather than a list?
    checksum_list = ['md5', 'sha1']
    for i in args.verify_checksums:
        if not i in checksum_list:
            print('\n---ERROR: ' + i + ' is not a valid checksum input ---\n')
            quit()
