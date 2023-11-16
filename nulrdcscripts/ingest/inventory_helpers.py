import glob
import os
import csv
import nulrdcscripts.ingest.helpers as helpers

def load_inventory(inventory_path: str, desc_arg: list[str]):
    work_type = get_work_type(inventory_path)
    if work_type == "IMAGE":
        inventory_dictlist = image_load_inventory(inventory_path)
    else:
        inventory_dictlist = av_load_inventory(inventory_path, desc_arg)
    return inventory_dictlist, work_type

def image_load_inventory(source_inventory):
    """
    reads directly from inventory data to create inventory dictlist
    """
    inventory_dictlist = []
    with open(source_inventory, encoding="utf-8") as f:
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
    
def av_load_inventory(source_inventory, desc_arg):
    """
    creates inventory dictlist
    """
    inventory_dictlist = []
    with open(source_inventory, encoding="utf-8") as f:
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

def check_inventory(filepath):
    """
    checks given inventory is a csv and exists
    """
    if not filepath.endswith(".csv"):
        print("\n--- ERROR: " + filepath + " is not a csv file ---\n")
        quit()
    if not os.path.isfile(filepath):
        print("\n--- ERROR: " + filepath + " is not a file ---\n")
        quit()

def find_inventory(indir):
    """
    searches for inventory csv in input directory
    will choose the first valid file it finds
        valid file: not ingest sheet or qc log
    """
    csv_files = glob.glob(os.path.join(indir, "*.csv"))
    for f in csv_files:
        if not ("_ingest.csv" in f or "qc_log.csv" in f):
            return f
    # will only reach here if no valid file is found
    print("\n--- ERROR: Unable to find inventory in input directory")
    quit()

def get_inventory_description(row, description_fields):
    """
    Generates inventory description based on description fields
    """
    description_list = []
    for header in description_fields:
        description_list.append(row[header])
    description = "; ".join(i for i in description_list if i)
    return description

def get_work_type(source_inventory):
    """
    Returns work type
    """
    with open(source_inventory, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        inventory_fields = reader.fieldnames
    if "Width (cm.)" in inventory_fields:
        return "IMAGE"
    elif "Speed IPS" in inventory_fields:
        return "AUDIO"
    elif "Region" or "Stock" in inventory_fields:
        return "VIDEO"
    else:
        print("\n---ERROR: Unable to determine work_type. ---\n")
        print("make sure that your inventory has the necessary format-specific columns")
        print('IMAGE: "Width (cm.)"')
        print('AUDIO: "Speed IPS"')
        print('VIDEO: "Region" or "Stock"')
        quit() 

def get_description_fields(desc_arg, inventory_fields):
    """
    Returns valid description fields and inventories with missing info
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