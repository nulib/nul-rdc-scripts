#!/usr/bin/env python3

"""
Helper functions related to ingest sheet fields.
"""

import re
import nulrdcscripts.ingest.ingest_data as data

def get_role_dict(aux_parse: str):
    """
    Builds role_dict
    See ingest_data.py for structure of role_dict.

    :param str aux_parse: sets how x files should be parsed, "extension", "parse", or None
    :returns: list of dicts containing rules for role assignment
    :rtype: list of dicts
    """
    role_dict: list[dict[str, str]] = data.role_dict

    # add aux dict to the beginning of the role_dict
    # this will catch X files that also have a/p identifiers in the filename
    if aux_parse:
        if "extension" in aux_parse:
            role_dict = {**data.x_extension_dict, **data.role_dict}
        elif "parse" in aux_parse:
            role_dict = {**data.x_parse_dict, **data.role_dict}
        else:
            print("\n---ERROR: i is not a valid aux_parse input ---\n")
            quit()
    return role_dict

def ingest_label_creator(filename: str, inventory_label: str):
    """
    Creates ingest label based on information in filename.

    :param str filename: name of file to create label for
    :param str inventory_label: item label from inventory
    :returns: label for file in ingest sheet
    :rtype: str
    """
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
        filename_labels = parse_filename_regex(filename_regex_string)
    # Append side string to Label string
    if filename_labels:
        label_list.extend(filename_labels)
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label

def parse_filename_regex(filename_regex: list[str]):
    """
    Parses regex info from filename to get label info

    :param str filename_regex:
    :returns: filename labels
    :rtype: list of str 
    """
    filename_labels: list[str] = []
    for key in data.pattern_dict.keys():
        component_number_full = re.search(data.pattern_dict[key], filename_regex)
        # strip leading zero from the (\d{2}) of the matched pattern
        if component_number_full:
            component_number_clean = component_number_full[1].lstrip("0")
            # construct the "Side String"
            component_string = key + " " + component_number_clean
        else:
            component_string = None
        filename_labels.append(component_string)
    return filename_labels

def get_ingest_description(item: dict[str, str], filename: str):
    """
    Get file description for ingest sheet

    :param dict item: inventory row for file
    :param str filename: input filename
    :returns: item description for ingest sheet
    :rtype: str
    """
    if not item["description"]:
        description = filename
    else:
        description = item["description"]
    return description

def get_fields():
    """
    Gets column names for ingest csv.

    :returns: fieldnames for ingest sheet csv
    :rtype: list of str
    """
    return data.header_names

"""
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
"""