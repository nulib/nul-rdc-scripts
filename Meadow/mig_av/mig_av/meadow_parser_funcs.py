#!/usr/bin/env python3

import re

def get_label(role_dict, filename, inventory_label):
    #run through each key in role_dict
    #if it matches on extension, it should be removed and passed to the next check
    label = None
    for i in role_dict:
        if not label:
            if role_dict[i]['type'] == 'extension':
                if filename.endswith(tuple(role_dict[i]['identifiers'])):
                    role = role_dict[i]['role']
                    if not role == 'X' and not inventory_label:
                        label = role_dict[i]['label']
                    elif inventory_label:
                        label = inventory_label + ' ' + role_dict[i]['label']
                    else:
                        label = 'Asset ' + role_dict[i]['label']
                    file_builder = role_dict[i]['file_builder']
            elif role_dict[i]['type'] == 'pattern':
                if any(ext in filename for ext in role_dict[i]['identifiers']):
                    label = label_creator(filename, inventory_label)
                    role = role_dict[i]['role']
                    file_builder = role_dict[i]['file_builder']
            elif role_dict[i]['type'] == 'xparse':
                if any(ext in filename for ext in role_dict[i]['identifiers']):
                    label = xparser(filename, role_dict[i]['identifiers'], inventory_label)
                    role = role_dict[i]['role']
                    file_builder = role_dict[i]['file_builder']
            else:
                label = filename
                role = 'S'
                file_builder = '_supplementary_'
    return label,role,file_builder

def xparser(filename, pattern_list, inventory_label):
    #TODO use regex instead so numbers could be extracted
    parser_dict = {
    'can' : ['_Can', '-Can'],
    'asset' : ['_Asset', '-Asset'],
    'back' : ['Back.'],
    'front' : ['Front.']
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
    else:
        label = label.capitalize()
    return label

def label_creator(filename, inventory_label):
    '''
    parses item side information from filenames and updates the label accordingly

    >>> label_creator("P001-TEST-f01i01_v01s02.wav", "Reel 1")
    'Reel 1 Side 2'
    '''
    pattern_dict = {
    'Side' : 's(\d{2})',
    'Part' : 'p(\d{2})',
    'Region' : 'r(\d{2})',
    'Capture' : 'c(\d{2})'
    }
    label_list = [inventory_label]
    #print(pattern_dict['Side']['abbreviation'])
    #regex for anything between pattern (- or _)v## and (- or _ or .)
    filename_regex = re.findall(r'[-_]v\d{2}(.*?)[-_.]', filename)
    #count pattern to check if it appears multiple times
    filename_count = len(filename_regex)
    if filename_count > 1:
        #do not attempt to make sense of pattern collisions
        print("WARNING: " + filename + " Filename label information was not parsed!")
        filename_labels = None
    elif filename_count < 1:
        filename_labels = None
    else:
        #convert findall results to string
        filename_regex_string = "".join(filename_regex)
        filename_labels = parse_filename_label(filename_regex_string, pattern_dict)
    #Append side string to Label string (add comma + space if Label already exists)
    label_list.extend(filename_labels)
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label

def parse_filename_label(filename_regex_string, pattern_dict):
    filename_labels = []
    for key in pattern_dict.keys():
        component_number_full = re.search(pattern_dict[key], filename_regex_string)
        #strip leading zero from the (\d{2}) of the matched pattern
        if component_number_full:
            component_number_clean = component_number_full[1].lstrip("0")
            #construct the "Side String"
            component_string = key + " " + component_number_clean
        else:
            component_string = None
        filename_labels.append(component_string)
    return filename_labels

if __name__ == "__main__":
    import doctest
    doctest.testmod()
