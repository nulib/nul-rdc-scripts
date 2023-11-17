"""
Helper functions related to inventories.
"""

import glob
import os
import csv
import nulrdcscripts.ingest.helpers as helpers

def load_inventory(inventory_path: str, desc_arg: list[str]):
    """
    finds work type to call image_load_inventory() or av_load_inventory()

    Args:
        inventory_path (str): fullpath to inventory csv
        desc_arg: (list of str): inventory fields to use for making description

    Returns:
        inventory_dictlist (list of dicts of str: str): inventory data
        work_type (str): IMAGE, AUDIO, or VIDEO
    """
    work_type = get_work_type(inventory_path)
    if work_type == "IMAGE":
        inventory_dictlist = image_load_inventory(inventory_path)
    else:
        inventory_dictlist = av_load_inventory(inventory_path, desc_arg)
    return inventory_dictlist, work_type

def image_load_inventory(inventory_path: str):
    """
    Loads image inventory

    Args:
        inventory_path (str):  fullpath to inventory csv
    
    Returns:
        inventory_dictlist (list of dicts of str: str)

    Note:
        Structure of inventory_dictlist is as follows

        image_inventory_dictlist = [
            {
                "filename": "filename",
                "label": "label",
                "work_accession_number": "work_accession_number",
                "file_accession_number": "file_accession_number",
                "role": "role",
                "description": "description",
            },
            {
                "filename": "filename",
                "label": "label",
                "work_accession_number": "work_accession_number",
                "file_accession_number": "file_accession_number",
                "role": "role",
                "description": "description",
            }
        ]
    """
    inventory_dictlist = []
    with open(inventory_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            row_data = {
                "filename": row["filename"],
                "label": row["label"],
                "work_accession_number": row["work_accession_number"],
                "file_accession_number": row["file_accession_number"],
                "role": row["role"],
                "description": row["description"],
            }
            inventory_dictlist.append(row_data)
    return inventory_dictlist
    
def av_load_inventory(inventory_path: str, desc_arg: list[str]):
    """
    Loads av inventory

    Args:
        inventory_path (str):  fullpath to inventory csv
    
    Returns:
        inventory_dictlist (list of dicts of str: str)

    Note:
        Structure of inventory_dictlist is as follows
        
        av_inventory_dictlist = [
            {
                "filename": "filename",
                "work_accession_number": "work_accession_number",
                "description": "description",
                "label": "label",
            },
            {
                "filename": "filename",
                "work_accession_number": "work_accession_number",
                "description": "description",
                "label": "label",
            },
        ]
    """
    inventory_dictlist = []
    with open(inventory_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        description_fields = get_description_fields(desc_arg, reader.fieldnames)
        for row in reader:         
            row_data = {
                "filename": row["filename"],
                "work_accession_number": row["work_accession_number"],
                "description": get_inventory_description(row, description_fields),
                "label": row["label"],
            }
            inventory_dictlist.append(row_data)
    return inventory_dictlist

def check_inventory(inventory_path: str):
    """
    Checks given inventory is a csv and exists. 
    Prints an error and quits if not.

    Args:
        inventory_path (str):  fullpath to inventory csv
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
    Quits if no inventory is found.

    Note:
        Will choose the first valid file it finds.
        Valid file: csv that is not ingest sheet or qc log

    Args:
        dir (str): fullpath to search directory
    """
    csv_files = glob.glob(os.path.join(dir, "*.csv"))
    for f in csv_files:
        if not ("_ingest.csv" in f or "qc_log.csv" in f):
            return f
    # will only reach here if no valid file is found
    return None

def get_inventory_description(row: dict[str: str], description_fields: list[str]):
    """
    Generates inventory description based on description fields

    Args:
        row (dict of str: str): inventory dict for item
        description_fields: (list of str): inventory fields to use for making description

    Returns:
        description (str): inventory description for file
    """
    description_list = []
    for header in description_fields:
        description_list.append(row[header])
    description = "; ".join(i for i in description_list if i)
    return description

def get_work_type(inventory_path: str):
    """
    Determines work type based on inventory fieldnames

    Args:
        inventory_path (str): fullpath to inventory csv

    Returns:
        (str): IMAGE, AUDIO, or VIDEO
    """
    with open(inventory_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        inventory_fields = reader.fieldnames
    if "Width (cm.)" in inventory_fields:
        return "IMAGE"
    elif "speed IPS" in inventory_fields:
        return "AUDIO"
    elif "region" or "stock" in inventory_fields:
        return "VIDEO"
    else:
        print("\n---ERROR: Unable to determine work_type. ---\n")
        print("make sure that your inventory has the necessary format-specific columns")
        print('IMAGE: "Width (cm.)"')
        print('AUDIO: "Speed IPS"')
        print('VIDEO: "Region" or "Stock"')
        quit() 

def get_description_fields(desc_arg: list[str], inventory_fields: list[str]):
    """
    Checks the inventory contains necessary fields for description creation.
    Prompts user to continue if there are missing fields.
    If the user continues, removes missing fields from description fields

    Args:
        desc_arg: (list of str): description fields to check
        inventory_fields (list of str): fields in inventory

    Returns:
        description_fields (list of str): valid description fields
    """
    if not desc_arg:
        return ["inventory_title"]

    #find missing description fields
    missing_fields = [
        fields for fields in desc_arg if not fields in inventory_fields
    ]
    if missing_fields:
        print("+++ WARNING: Your inventory is missing the following columns +++")
        print(missing_fields)
        if not helpers.yn_check("SKIP COLUMNS AND CONTINUE?"):
            quit()
    # remove missing fields
    description_fields = [
        header
        for header in description_fields
        if header not in missing_fields
    ]
    return description_fields