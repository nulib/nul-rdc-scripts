#!/usr/bin/env python3

import os
from pathlib import Path
import posixpath
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
parser.add_argument('--load_inventory', '-l', required=False, action='store', dest='source_inventory', help='Use to specify an inventory csv file.')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output csv file')
parser.add_argument('--auxiliary', '-x', required=False, nargs=1, action='store', dest='aux_parse', help='Sets how to parse auxiliary files. Options include: extension (by extension), parse (by word), none (no aux files). Default is none.')
parser.add_argument('--skip', '-s', required=False, nargs='*', action='store', dest='skip', help='Use to specify patterns to skip. Can take multiple inputs. For example, "_ac." "_am." could be used to skip legacy ac and am files.')
parser.add_argument('--prepend_accession', '-p', action='store', dest='prepend', type=str, help='set a string to be added to the beginning of the file accession number when generated')

args = parser.parse_args()

def interpret_aux_command():
    '''checks if argument passed to aux_parse is valid'''
    aux_parse_list = ['extension', 'parse', '2pass']
    for i in args.aux_parse:
        if not i in aux_parse_list:
            print('\n---ERROR: ' + i + ' is not a valid input to the auxiliary command ---\n')
            quit()

def input_check(indir):
    """
    Checks if input was provided and if it is a directory that exists
    """
    if not indir:
        print ("No input provided")
        quit()
    if not os.path.isdir(indir):
        print('input is not a directory')
        quit()

def select_number(max_limit):
    """
    Prompts user to enter a number
    Number must be 1 or greater
    and less than or equal to max_limit
    """
    choice_confirm = False
    while choice_confirm is False:
        choice = int(input())
        if choice<=max_limit and choice>=1:
            choice_confirm = True
            return choice
        else:
            print("please select a number that is equal to or less than " + str(max_limit));

def yes_no(question):
    """
    Poses yes/no question to user
    Returns True/False
    """
    print(question)
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    while True:
        choice = input().lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           print("Please respond with 'yes' or 'no'");

def import_csv(csv_file):
    """
    Imports csv file and maps data to dictionary
    """
    filter_text = ['_am_', '_am', '-am', '_ac_', '_ac', '-ac', '_access', '_streaming'] #'-a' removed to avoid some collisions
    csv_dict = {}
    with open(csv_file, encoding='utf-8')as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            base_filename = row["Fileset Original Filename"]
            for i in filter_text:
                if i in base_filename:
                    base_filename = base_filename.split(i)
            base_filename = clean_filename(base_filename)
            data_dict = {
            "Collection Title" : row["Collection Title"],
            "Meadow URL" : row["Meadow URL"],
            "Work ID" : row["Work ID"],
            "Work Accession" : row["Work Accession"],
            "Work Title" : row["Work Title"],
            "Fileset ID" : row["Fileset ID"],
            "Fileset Accession" : row["Fileset Accession"],
            "Fileset Role" : row["Fileset Role"],
            "Fileset Original Filename" : row["Fileset Original Filename"],
            "Fileset Label" : row["Fileset Label"],
            "Fileset Description" : row["Fileset Description"],
            "File Path" : None
            }
            csv_dict.update({base_filename : data_dict})
    return csv_dict

def clean_filename(base_filename):
    """
    Takes list or string as input
    Attempts to reconcile filename to searchable term
    List would be filename that was split at a pattern
    Removes remaining extensions
    """
    global global_element_selection
    if type(base_filename) is list:
        for a in base_filename:
            if a.startswith("."):
                base_filename.remove(a)
        for a, item in enumerate(base_filename):
            if item.startswith("."):
                base_filename.remove(item)
            base_filename[a] = Path(item).stem
        number_of_elements = len(base_filename)
        if number_of_elements == 1:
            base_filename = "".join(base_filename)
        else:
            if not global_element_selection:
                print("\nMultiple possible base filenames found")
                print("Please select the list element you would like to search for")
                print(base_filename)
                print("Enter a number from 1-" + str(number_of_elements))
                number_selection = select_number(number_of_elements)
                #subtract 1 so that number corresponds to list index
                number_selection = (number_selection - 1)
                base_filename = base_filename[number_selection]
                make_global = yes_no("\nDo you want to apply this globally for similar filenames in this inventory?")
                if make_global:
                    global_element_selection = number_selection
            else:
                base_filename = base_filename[global_element_selection]
    else:
        base_filename = Path(base_filename).stem
    return base_filename

def generate_input_dict(indir):
    """
    Finds all files in input
    Removes hidden files and unwanted filetypes
    Returns a dictionary of files with their paths relative to input
    """
    indir_dictionary = {}
    for subdir, dirs, files in os.walk(indir):
        clean_subdir = (subdir.replace(indir, ''))
        clean_subdir = clean_subdir.strip('/')
        files = [f for f in files if not f[0] == '.']
        files = [f for f in files if not f == 'Thumbs.db']
        files = [f for f in files if not f.endswith('.md5')]
        files = [f for f in files if not f.endswith('.csv')]
        if args.skip:
            skip_list = args.skip
            for i in skip_list:
                files = [f for f in files if not i in f]
        for file in files:
            file_path = os.path.join(clean_subdir, file)
            file_path = file_path.replace(os.sep, posixpath.sep)
            file_path = file_path.strip('/')
            indir_dictionary.update({file : file_path})
    return indir_dictionary

def get_role(filename, inventory_label):
    """
    Assigns role to file
    Based on extension or pattern
    """
    role_dict = {
    'framemd5' : {'identifiers' : ['.framemd5'], 'type' : 'extension', 'role' : 'S', 'label' : 'framemd5 file', 'file_builder' : '_supplementary_'},
    'metadata' : {'identifiers' : ['.xml', 'json'], 'type' : 'extension', 'role' : 'S', 'label' : 'technical metadata file', 'file_builder' : '_supplementary_'},
    'logfile' : {'identifiers' : ['.log'], 'type' : 'extension', 'role' : 'S', 'label' : 'log file', 'file_builder' : '_supplementary_'},
    'qctools' : {'identifiers' : ['.xml.gz', '.qctools.mkv'], 'type' : 'extension', 'role' : 'S', 'label' : 'QCTools report', 'file_builder' : '_supplementary_'},
    'spectrogram' : {'identifiers' : ['.png', '.PNG'], 'type' : 'extension', 'role' : 'S', 'label' : 'spectrogram file', 'file_builder' : '_supplementary_'},
    'dpx_checksum' : {'identifiers' : ['dpx.txt'], 'type' : 'extension', 'role' : 'S', 'label' : 'original DPX checksums', 'file_builder' : '_supplementary_'},
    'access' : {'identifiers' : ['-a.', '_a.', '-am.', '_am.', '_am_', '-am-', '-ac.', '.mp4', '_access.', '_amcc_'], 'type' : 'pattern', 'role' : 'A', 'label' : None, 'file_builder' : '_access_'},
    'preservation' : {'identifiers' : ['-p.', '_p.', '-pm.', '_pm.', '_pm_', '-pm-', '_preservation.', '.mkv'], 'type' : 'pattern', 'role' : 'P', 'label' : None, 'file_builder' : '_preservation_'},
    }
    if not args.aux_parse:
        aux_dict = {'auxiliary' : {'identifiers' : None, 'type' : None, 'role' : None, 'label' : None, 'file_builder' : None}}
    elif 'extension' in args.aux_parse:
        aux_dict = {
        'auxiliay' : {'identifiers' : ['.jpg', '.JPG'], 'type' : 'extension', 'role' : 'X', 'label' : 'image', 'file_builder' : '_auxiliary_'}
        }
    elif 'parse' in args.aux_parse or '2pass' in args.aux_parse:
        aux_dict = {'auxiliary' : {'identifiers' : ['_Asset', '-Asset', '_Can', '-Can', 'Front.', 'Back.', 'Side.', '_Ephemera.'], 'type' : 'xparse', 'role' : 'X', 'label' : None, 'file_builder' : '_auxiliary_'}}
    role_dict.update(aux_dict)
    role = None
    #TODO: make these separate functions
    #if 'extension' in args.aux_parse: label = None
    for i in role_dict:
        if role_dict[i]['type'] == 'extension' and not role:
            if filename.endswith(tuple(role_dict[i]['identifiers'])):
                role = role_dict[i]['role']
                file_accession_builder = role_dict[i]['file_builder']
                if not role == 'X' and not inventory_label:
                    label = role_dict[i]['label']
                elif inventory_label:
                    label = inventory_label + ' ' + role_dict[i]['label']
    for i in role_dict:
        if role_dict[i]['type'] == 'pattern' and not role:
            if any(ext in filename for ext in role_dict[i]['identifiers']):
                role = role_dict[i]['role']
                file_accession_builder = role_dict[i]['file_builder']
                label = inventory_label
    for i in role_dict:
        if role_dict[i]['type'] == 'xparse' and not role:
            if any(ext in filename for ext in role_dict[i]['identifiers']):
                label = xparser(filename, role_dict[i]['identifiers'], inventory_label)
                role = role_dict[i]['role']
                file_accession_builder = role_dict[i]['file_builder']
    if not role:
        label = inventory_label
        role = 'S'
        file_accession_builder = '_supplementary_'
    return role,file_accession_builder,label

def xparser(filename, pattern_list, inventory_label):
    #TODO use regex instead so numbers could be extracted?
    parser_dict = {
    'reel' : ['_Reel', '-Reel'],
    'can' : ['_Can', '-Can'],
    'asset' : ['_Asset', '-Asset'],
    'box' : ['_Box', '-Box'],
    'back' : ['Back.'],
    'front' : ['Front.'],
    'side' : ['Side.'],
    'ephemera' : ['_Ephemera.']
    }
    label_list = []
    if inventory_label:
        label_list.append(inventory_label)
    for i in parser_dict:
        for a in parser_dict.get(i):
            if a in filename:
                label_list.append(i)
        #label_list.append(parser_dict(i))
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label

def write_output(full_dict):
    """
    Writes output CSV file
    Takes dict with keys containing
    lists of dicts as input
    """
    header_names = [
        "Collection Title",
        "Meadow URL",
        "Work ID",
        "Work Accession",
        "Work Title",
        "Fileset ID",
        "Fileset Accession",
        "Fileset Role",
        "Fileset Original Filename",
        "Fileset Label",
        "Fileset Description",
        "File Path"
        ]
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames = header_names)
        writer.writeheader()
        for item in full_dict:
            for file_info in full_dict[item]:
                writer.writerow(file_info)

indir = args.input_path
input_check(indir)
output_file = args.output_path

global_element_selection = None
csv_file = args.source_inventory
csv_dict = import_csv(csv_file)
indir_dictionary = generate_input_dict(indir)
print("\n")

if args.aux_parse:
    interpret_aux_command()
    if "2pass" in args.aux_parse:
        filtered_dict = {k:v for (k,v) in indir_dictionary.items() if '.JPG' in k or '.jpg' in k or '.xml' in k}
        indir_dictionary = {k: v for k, v in indir_dictionary.items() if k not in filtered_dict}
        #TODO: 2pass will require a filter option to create a list
        # of strings to remove from the end of filenames set by user
        #TODO: set fileset accession as base_filename + image + 3 digit #
        reduced_csv_dict = {}
        for i in csv_dict:
            #TODO: make a new simplified dictionary that excludes repeats
            imported_data = csv_dict[i]
            filter_list = ['s01', 's02']
            for el in filter_list:
                #if i.endswith(el):
                i = i.removesuffix(el)
            if not i in reduced_csv_dict:
                reduced_csv_dict[i] = imported_data
        #print(reduced_csv_dict)
        #print(filtered_dict)
        #quit()

partial_matches = None
full_dict = {}
for item in csv_dict:
    partial_matches = [x for x in indir_dictionary.keys() if item in x]
    if partial_matches:
        print(item + " was found")
        if csv_dict[item]["Fileset Original Filename"] in partial_matches:
            partial_matches.remove(csv_dict[item]["Fileset Original Filename"])
        for match in partial_matches:
            inventory_label = csv_dict[item]["Fileset Label"]
            if inventory_label == csv_dict[item]["Fileset Original Filename"]:
                inventory_label = None
            role,file_accession_builder,label = get_role(match, inventory_label)
            if not label:
                label = match
            file_dict = {
            "Collection Title" : csv_dict[item]["Collection Title"],
            "Meadow URL" : csv_dict[item]["Meadow URL"],
            "Work ID" : csv_dict[item]["Work ID"],
            "Work Accession" : csv_dict[item]["Work Accession"],
            "Work Title" : csv_dict[item]["Work Title"],
            "Fileset ID" : None,
            "Fileset Accession" : None,
            "Fileset Role" : role,
            "Fileset Original Filename" : match,
            "Fileset Label" : label,
            "Fileset Description" : csv_dict[item]["Fileset Description"],
            "File Path" : indir_dictionary[match]
            }
            #add item to full dict or append if item exists
            if item not in full_dict:
                full_dict[item] = [file_dict]
            else:
                full_dict[item].append(file_dict)
            #update the Fileset ID and file accession
            if role == "A":
                file_dict.update({"Fileset ID" : csv_dict[item]["Fileset ID"]})
                file_dict.update({"Fileset Accession" : csv_dict[item]["Fileset Accession"]})
            else:
                role_count = sum(x.get("Fileset Role") == role for x in full_dict.get(item))
                if not args.prepend:
                    file_dict.update({"Fileset Accession" : item + file_accession_builder + f'{role_count:03d}'})
                else:
                    file_dict.update({"Fileset Accession" : args.prepend + item + file_accession_builder + f'{role_count:03d}'})
    else:
        print("nothing matching " + item + " found")

if args.aux_parse:
    if "2pass" in args.aux_parse:
        for item in reduced_csv_dict:
            partial_matches = [x for x in filtered_dict.keys() if item in x]
            if partial_matches:
                print("images for " + item + " found")
                for match in partial_matches:
                    inventory_label = reduced_csv_dict[item]["Fileset Label"]
                    if inventory_label == reduced_csv_dict[item]["Fileset Original Filename"]:
                        inventory_label = None
                    role,file_accession_builder,label = get_role(match, inventory_label)
                    if not label:
                        label = match
                    file_dict = {
                    "Collection Title" : reduced_csv_dict[item]["Collection Title"],
                    "Meadow URL" : reduced_csv_dict[item]["Meadow URL"],
                    "Work ID" : reduced_csv_dict[item]["Work ID"],
                    "Work Accession" : reduced_csv_dict[item]["Work Accession"],
                    "Work Title" : reduced_csv_dict[item]["Work Title"],
                    "Fileset ID" : None,
                    "Fileset Accession" : None,
                    "Fileset Role" : role,
                    "Fileset Original Filename" : match,
                    "Fileset Label" : label,
                    "Fileset Description" : reduced_csv_dict[item]["Fileset Description"],
                    "File Path" : filtered_dict[match]
                    }
                    #add item to full dict or append if item exists
                    if item not in full_dict:
                        full_dict[item] = [file_dict]
                    else:
                        full_dict[item].append(file_dict)
                    #update the Fileset ID and file accession
                    if role == "A":
                        file_dict.update({"Fileset ID" : reduced_csv_dict[item]["Fileset ID"]})
                        file_dict.update({"Fileset Accession" : reduced_csv_dict[item]["Fileset Accession"]})
                    else:
                        role_count = sum(x.get("Fileset Role") == role for x in full_dict.get(item))
                        if not args.prepend:
                            file_dict.update({"Fileset Accession" : item + file_accession_builder + f'{role_count:03d}'})
                        else:
                            file_dict.update({"Fileset Accession" : args.prepend + item + file_accession_builder + f'{role_count:03d}'})
            else:
                print("nothing matching " + item + " found")

write_output(full_dict)
print("Process complete!")
