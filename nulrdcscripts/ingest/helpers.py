#!/usr/bin/env python3

import re


def get_label(role_dict, filename, inventory_label):
    # run through each key in role_dict
    role_index = -1
    for i in role_dict:
        if any(ext in filename for ext in role_dict[i]["identifiers"]):
            role_index = i
            break

    # base case if role not found
    if role_index == -1:
        label = filename
        role = "S"
        file_builder = "_supplementary_"
    else:
        role = role_dict[role_index]["role"]
        file_builder = role_dict[i]["file_builder"]
        label = label_creator(filename, inventory_label)

        #append label if role has extra info
        if role_dict[role_index]["label"]:
            label += " " + role_dict[role_index]["label"]

    return label, role, file_builder

# no longer necessary
def xparser(filename, pattern_list, inventory_label):
    # TODO use regex instead so numbers could be extracted
    parser_dict = {
        "reel": ["_Reel", "-Reel"],
        "can": ["_Can", "-Can"],
        "asset": ["_Asset", "-Asset"],
        "back": ["Back."],
        "front": ["Front."],
        "side": ["Side."],
        "ephemera": ["_Ephemera", "-Ephemera"],
    }
    label_list = []
    if inventory_label:
        label_list.append(inventory_label)
    for i in parser_dict:
        for a in parser_dict.get(i):
            if a in filename:
                label_list.append(i)
        # label_list.append(parser_dict(i))
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label


def label_creator(filename, inventory_label):
    """
    parses item side information from filenames and updates the label accordingly

    >>> label_creator("P001-TEST-f01i01_v01s02.wav", "Reel 1")
    'Reel 1 Side 2'
    """
    pattern_dict = {
        "side": "s(\d{2})",
        "part": "p(\d{2})",
        "region": "r(\d{2})",
        "capture": "c(\d{2})",
    }
    label_list = [inventory_label]
    # print(pattern_dict['Side']['abbreviation'])
    # regex for anything between pattern (- or _)v## and (- or _ or .)
    filename_regex = re.findall(r"[-_]v\d{2}(.*?)[-_.]", filename)
    # count pattern to check if it appears multiple times
    filename_count = len(filename_regex)
    if filename_count > 1:
        # do not attempt to make sense of pattern collisions
        print("WARNING: " + filename + " Filename label information was not parsed!")
        filename_labels = None
    elif filename_count < 1:
        filename_labels = None
    else:
        # convert findall results to string
        filename_regex_string = "".join(filename_regex)
        filename_labels = parse_filename_label(filename_regex_string, pattern_dict)
    # Append side string to Label string
    if filename_labels:
        label_list.extend(filename_labels)
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label


def parse_filename_label(filename_regex_string, pattern_dict):
    filename_labels = []
    for key in pattern_dict.keys():
        component_number_full = re.search(pattern_dict[key], filename_regex_string)
        # strip leading zero from the (\d{2}) of the matched pattern
        if component_number_full:
            component_number_clean = component_number_full[1].lstrip("0")
            # construct the "Side String"
            component_string = key + " " + component_number_clean
        else:
            component_string = None
        filename_labels.append(component_string)
    return filename_labels


if __name__ == "__main__":
    import doctest

    doctest.testmod()