import re
import nulrdcscripts.ingest.ingest_data as data

"""
Helpers related to ingest sheet fields
"""

def get_role_dict(aux_parse):
    """
    Builds role_dict

    Note:
        Uses dictionaries found in ingest_data.py

    Args:
        aux_parse (str): sets how x files should be parsed
            "extension", "parse", or None
    """
    role_dict = data.role_dict

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
    parses item side information from filenames and updates the label accordingly
    label_creator("P001-TEST-f01i01_v01s02.wav", "Reel 1")
    'Reel 1 Side 2'
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
        filename_labels = parse_ingest_label(filename_regex_string)
    # Append side string to Label string
    if filename_labels:
        label_list.extend(filename_labels)
    label = " ".join(i for i in label_list if i)
    if not label:
        label = filename
    return label

def parse_ingest_label(filename_regex: str):
    """
    Parses info to create addition to ingest label
    """
    filename_labels = []
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

def get_ingest_description(item, filename: str):
    """
    Get file description for ingest sheet

    Args:
        item (dict of str: str): inventory row for file
        filename (str): input filename

    Returns:
        (str): label for ingest sheet
    """
    if not item["description"]:
        return filename
    else:
        return item["description"]

def get_fields():
    """
    Gets column names for ingest sheet

    Returns:
        (list of str): fieldnames for ingest sheet
    """
    return data.header_names

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