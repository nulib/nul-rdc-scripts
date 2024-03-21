#!/usr/bin/env python3

"""
Helper functions related to inventories.
"""

import glob
import os
import csv
import nulrdcscripts.aqc.helpers as helpers

def load_inventory(inventory_path: str):
    """
    Finds work type to call image_load_inventory() or av_load_inventory().

    .. note:: worktype can be IMAGE, AUDIO, or VIDEO

    :param str inventory_path: fullpath to inventory csv
    :param list[str] desc_arg: inventory fields to use for making description
    :returns: inventory data and worktype
    :rtype: tuple of list[dict] and str
    """
    inventory_dictlist: list[dict[str, str]] = []
    with open(inventory_path, encoding="utf-8") as f:
        f = skip_non_fieldnames(f)
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:         
            row_data: dict[str, str] = {
                "filename": row["filename"],
                "work_accession_number": row["work_accession_number"],
                "found": False,
                "file_check": False
            }
            inventory_dictlist.append(row_data)
    return inventory_dictlist

def check_inventory(inventory_path: str):
    """
    Checks given inventory is a csv and exists. 
    Prints an error and quits if not.

    :param str inventory_path:  fullpath to inventory csv
    """
    if not inventory_path.endswith(".csv"):
        print("\n--- ERROR: " + inventory_path + " is not a csv file ---\n")
        quit()
    if not os.path.isfile(inventory_path):
        print("\n--- ERROR: " + inventory_path + " is not a file ---\n")
        quit()

def find_inventory(dir: str):
    """
    Searches for inventory csv in given directory.
    Returns None if no inventory is found.

    .. note::
        Will choose the first valid file it finds.
        Valid file: csv that is not ingest sheet or qc log

    :param str dir: fullpath to search directory
    """
    csv_files = glob.glob(os.path.join(dir, "*.csv"))
    for f in csv_files:
        if not ("_ingest.csv" in f or "qc_log.csv" in f):
            return f
    # will only reach here if no valid file is found
    return None

def get_work_type(inventory_path: str):
    """
    Determines work type based on inventory fieldnames.

    :param str inventory_path: fullpath to inventory csv
    :returns: worktype as 'IMAGE', 'AUDIO', or 'VIDEO'
    :rtype: str
    """
    with open(inventory_path, encoding="utf-8") as f:
        f = skip_non_fieldnames(f)
        reader = csv.DictReader(f, delimiter=",")
        inventory_fields = reader.fieldnames
    if "Width (cm.)" in inventory_fields:
        return "IMAGE"
    elif any(x in ["speed IPS", "Speed IPS"] for x in inventory_fields):
        return "AUDIO"
    elif any(x in ["video standard", "Region", "stock", "Stock"] for x in inventory_fields):
        return "VIDEO"
    else:
        print("\n---ERROR: Unable to determine work_type. ---\n")
        print("make sure that your inventory has the necessary format-specific columns")
        print('IMAGE: "Width (cm.)"')
        print('AUDIO: "speed IPS"')
        print('VIDEO: "video standard", "Region" or "Stock"')
        quit()

def skip_non_fieldnames(f):
    """
    Takes in TextIOWrapper result from open() and returns new TextIOWrapper indexed after 
    non-fieldname lines in inventory.

    :param f: inventory file
    :type f: TextIOWrapper
    :return: new file TextIOWrapper indexed after extraneous lines
    :rtype: TextIOWrapper
    """
    while True:
        # save spot
        stream_index = f.tell()
        # skip advancing line by line
        line = f.readline()
        if not ("Name of Person Inventorying" in line or "MEADOW Ingest fields" in line):
            # go back one line and break out of loop once fieldnames are found
            f.seek(stream_index, os.SEEK_SET)
            break
    return f