#!/usr/bin/env python3

import sys
import os
import csv
import glob
import posixpath
import nulrdcscripts.ingest.helpers as helpers
from nulrdcscripts.ingest.params import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    # sorted[]
    """setting up inputs and outputs"""
    
    indir = input_check(args.input_path)
    if args.output_path:
        meadow_csv_file = args.output_path
    else:
        base_folder_name = os.path.basename(indir)
        meadow_csv_file = os.path.join(
            indir, 
            base_folder_name + '_ingest.csv'
        )
    output_check(meadow_csv_file)

    if args.aux_parse:
        interpret_aux_command()

    """importing inventories"""
    if args.source_inventory:
        source_inventories = args.source_inventory
        source_inventory_dictlist = import_inventories(source_inventories)
    else:
        print("\n*** Checking input directory for CSV files ***")
        source_inventories = glob.glob(os.path.join(indir, "*.csv"))
        # skip auto-generated meadow ingest csv if it already exists
        source_inventories = [
            i for i in source_inventories if not ("_ingest.csv" in i or "qc_log.csv" in i)
        ]
        if not source_inventories:
            print("\n+++ WARNING: Unable to find CSV inventory file +++")
            print("CONTINUE? (y/n)")
            yes = {"yes", "y", "ye", ""}
            no = {"no", "n"}
            choice = input().lower()
            if choice in yes:
                source_inventory_dictlist = [{}]
            elif choice in no:
                quit()
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'")
                quit()
            # rather than quitting - prompt user to choose whether or not to continue
        else:
            print("Inventories found\n")
            source_inventory_dictlist = import_inventories(source_inventories)

    # check that each csv file actually exists [approach later will be to iterate through loaded dictionaries of CSV files to check if a file corresponds to a key, which is derived from the filename column]
    # fallback 1: if source inventory exists in indir, iterate through loading csv files all csv files
    # fallback 2: if no inventory is specified and no csv files are found in indir, warn and proceed with no inventory

    """
    setting up parameters for meadow inventory
    """
    # TODO may want to convert everything to lowercase so you don't risk running into errors
    # TODO move generating this dict to a function in a separate module
    role_dict = {
        "framemd5": {
            "identifiers": [".framemd5"],
            "type": "extension",
            "role": "S",
            "label": "framemd5 file",
            "file_builder": "_supplementary_",
        },
        "metadata": {
            "identifiers": [".xml", ".json", ".pdf"],
            "type": "extension",
            "role": "S",
            "label": "technical metadata file",
            "file_builder": "_supplementary_",
        },
        "qctools": {
            "identifiers": [".xml.gz", ".qctools.mkv"],
            "type": "extension",
            "role": "S",
            "label": "QCTools report",
            "file_builder": "_supplementary_",
        },
        "logfile": {
            "identifiers": [".log"],
            "type": "extension",
            "role": "S",
            "label": "log file",
            "file_builder": "_supplementary_",
        },
        "spectrogram": {
            "identifiers": ["spectrogram"],
            "type": "pattern",
            "role": "S",
            "label": "spectrogram file",
            "file_builder": "_supplementary_",
        },
        "dpx_checksum": {
            "identifiers": ["dpx.txt"],
            "type": "extension",
            "role": "S",
            "label": "original DPX checksums",
            "file_builder": "_supplementary_",
        },
        "access": {
            "identifiers": [
                "-a.",
                "_a.",
                "-am.",
                "_am.",
                "_am_",
                "-am-",
                "-am_",
                "_access",
            ],
            "type": "pattern",
            "role": "A",
            "label": None,
            "file_builder": "_access_",
        },
        "preservation": {
            "identifiers": [
                "-p.",
                "_p.",
                "-pm.",
                "_pm",
                "_pm_",
                "-pm-",
                "-pm_",
                "_preservation",
            ],
            "type": "pattern",
            "role": "P",
            "label": None,
            "file_builder": "_preservation_",
        },
    }
    if args.aux_parse:
        if "extension" in args.aux_parse:
            aux_dict = {
                "auxiliary": {
                    "identifiers": [".jpg", ".JPG"],
                    "type": "extension",
                    "role": "X",
                    "label": "image",
                    "file_builder": "_auxiliary_",
                }
            }
        elif "parse" in args.aux_parse:
            aux_dict = {
                "front": {
                    "identifiers": ["front"],
                    "type": "pattern",
                    "role": "X",
                    "label": "asset front",
                    "file_builder": "_auxiliary_",
                },
                "back": {
                    "identifiers": ["back"],
                    "type": "pattern",
                    "role": "X",
                    "label": "asset back",
                    "file_builder": "_auxiliary_",
                },
                "asset": {
                    "identifiers": ["_asset", "-asset"],
                    "type": "pattern",
                    "role": "X",
                    "label": "asset",
                    "file_builder": "_auxiliary_",
                },
                "can": {
                    "identifiers": ["_can", "-can"],
                    "type": "pattern",
                    "role": "X",
                    "label": "can",
                    "file_builder": "_auxiliary_",
                },
                "ephemera": {
                    "identifiers": ["_ephemera", "-ephemera"],
                    "type": "pattern",
                    "role": "X",
                    "label": "ephemera",
                    "file_builder": "_auxiliary_",
                },
                "auxiliary": {
                    "identifiers": ["_x","-x"],
                    "type": "pattern",
                    "role": "X",
                    "label": "auxiliary file",
                    "file_builder": "_auxiliary_",
                },
            }
        # add the aux_dict to the beginning of the role_dict
        # this will catch X files that also have a/p identifiers in the filename
        role_dict = {**aux_dict, **role_dict}

    header_names = [
        "work_type",
        "work_accession_number",
        "file_accession_number",
        "filename",
        "description",
        "label",
        "role",
        "work_image",
        "structure",
    ]
    """
    extract the filenames from the inventories as a list
    """
    filename_list = []
    for i in source_inventory_dictlist:
        name = i.get("filename")
        filename_list.append(name)
    # error out if duplicate filenames are found
    if len(filename_list) != len(set(filename_list)):
        print("\n--- ERROR: There are duplicate filenames in your inventories ---\n")
        quit()
    # convert list to dict so it becomes easier to parse from here on
    source_inventory_dict = {}
    for item in source_inventory_dictlist:
        name = item["filename"]
        source_inventory_dict[name] = item
    # TODO add a check for existing file with filename before overwriting
    """
    attempt to create output csv before continuing
    """
    try:
        with open(meadow_csv_file, "w", newline="\n") as outfile:
            outfile.close
    except OSError:
        print("\n--- ERROR: Unable to create output file", meadow_csv_file + " ---\n")
        quit()

    meadow_full_dict = {}
    for subdir, dirs, files in os.walk(indir):
        dirs.sort()
        clean_subdir = subdir.replace(indir, "")
        clean_subdir = clean_subdir.strip("/")
        # skip file types we don't want
        # TODO put this in an external function to make this a little cleaner
        files = [f for f in files if not f[0] == "."]
        files = [f for f in files if not f == "Thumbs.db"]
        files = [f for f in files if not f.endswith(".md5")]
        files = [f for f in files if not f.endswith(".csv")]
        if args.skip:
            skip_list = args.skip
            for i in skip_list:
                files = [f for f in files if not i in f]
        dirs[:] = [d for d in dirs if not d[0] == "."]
        for file in sorted(files):
            # set filename, use unix style path without leading slash
            filename = os.path.join(clean_subdir, file)
            filename = filename.replace(os.sep, posixpath.sep)
            filename = filename.strip("/")
            meadow_file_dict = {
                "work_type": None,
                "work_accession_number": None,
                "file_accession_number": None,
                "filename": filename,
                "description": None,
                "label": None,
                "role": None,
                "work_image": None,
                "structure": None,
            }

            # TODO add safety check to make sure there aren't multiple matches for a filename in the accession numbers
            # check for corresponding item in loaded inventory
            # TODO handle cases where there is no inventory
            for item in filename_list:
                if item in file:
                    meadow_file_dict.update(
                        {
                            "work_accession_number": source_inventory_dict[item][
                                "work_accession_number"
                            ]
                        }
                    )
                    # load the work type
                    work_type = source_inventory_dict[item]["work_type"]
                    meadow_file_dict.update({"work_type": work_type})
                    # load the description or auto-fill if description is empty
                    if not source_inventory_dict[item]["description"]:
                        meadow_file_dict.update({"description": file})
                    else:
                        meadow_file_dict.update(
                            {"description": source_inventory_dict[item]["description"]}
                        )
                    # if dictionary does not already have a key corresponding to the item add it
                    if item not in meadow_full_dict:
                        meadow_full_dict[item] = [meadow_file_dict]
                    # otherwise append it to the existing key
                    else:
                        meadow_full_dict[item].append(meadow_file_dict)
                    # setting a generic label
                    inventory_label = source_inventory_dict[item]["label"]
                    if work_type == "VIDEO" or work_type == "AUDIO":
                        label, role, file_builder = helpers.get_label(
                            role_dict, 
                            file, 
                            inventory_label)
                        meadow_file_dict.update({"role": role})
                        role_count = sum(
                            x.get("role") == role for x in meadow_full_dict.get(item)
                        )
                        meadow_file_dict.update({"label": label})
                        if args.prepend:
                            meadow_file_dict.update(
                                {
                                    "file_accession_number": args.prepend
                                    + item
                                    + file_builder
                                    + f"{role_count:03d}"
                                }
                            )
                        else:
                            meadow_file_dict.update(
                                {
                                    "file_accession_number": item
                                    + file_builder
                                    + f"{role_count:03d}"
                                }
                            )
                    else:
                        meadow_file_dict.update(
                            {"role": source_inventory_dict[item]["role"]}
                        )
                        meadow_file_dict.update({"label": inventory_label})
                        if args.prepend:
                            meadow_file_dict.update(
                                {
                                    "file_accession_number": args.prepend
                                    + source_inventory_dict[item][
                                        "file_accession_number"
                                    ]
                                }
                            )
                        else:
                            meadow_file_dict.update(
                                {
                                    "file_accession_number": source_inventory_dict[
                                        item
                                    ]["file_accession_number"]
                                }
                            )
            # TODO build out how to handle cases where a file is not found in the inventory
            # allow user to add the file anyway
            if not any(item in file for item in filename_list):
                print(
                    "+++ WARNING: No entry matching " + file + 
                    " was found in your inventory +++"
                )

    # TODO final check that all ihidden files and folderstems from filename list are accounted for in the final inventory

    with open(meadow_csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header_names)
        writer.writeheader()
        for item in meadow_full_dict:
            for file_info in meadow_full_dict[item]:
                writer.writerow(file_info)
    print("Process complete!")
    print("Meadow inventory located at: " + meadow_csv_file)


def input_check(indir):
    """Checks if input was provided and if it is a directory that exists"""
    if not indir:
        print("No input provided, using current directory")
        return os.getcwd()
    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    else:
        return indir


def output_check(output):
    """Checks that output is valid"""
    if not output.endswith(".csv"):
        print("\n--- ERROR: Output must be a CSV file ---\n")
        quit()


def interpret_aux_command():
    """checks if argument passed to aux_parse is valid"""
    aux_parse_list = ["extension", "parse"]
    for i in args.aux_parse:
        if not i in aux_parse_list:
            print(
                "\n---ERROR: "
                + i
                + " is not a valid input to the auxiliary command ---\n"
            )
            quit()


def update_fieldname_list(original_fieldname_list, missing_fieldname_list):
    fieldname_list = [
        header
        for header in original_fieldname_list
        if header not in missing_fieldname_list
    ]
    return fieldname_list


def missing_description_field_handler(missing_descriptive_fieldnames):
    print("+++ WARNING: Your inventory is missing the following columns +++")
    print(missing_descriptive_fieldnames)
    print("SKIP COLUMNS AND CONTINUE? (y/n)")
    yes = {"yes", "y", "ye", ""}
    no = {"no", "n"}
    choice = input().lower()
    if choice in yes:
        pass
    elif choice in no:
        quit()


# TODO add early warning if spreadsheet is missing important columns like work_accession_number
def import_inventories(source_inventories):
    """
    import CSV inventories and parse each row into a dictionary that is added to a list
    We use lists of dicts initially to catch duplicate filenames later on
    TODO Cell wrangling stems from here (description and label)
    """
    missing_fieldnames = False
    source_inventory_dictlist = []
    for i in source_inventories:
        if i.endswith(".csv"):
            if os.path.isfile(i):
                csvDict = []
                with open(i, encoding="utf-8") as f:
                    reader = csv.DictReader(f, delimiter=",")
                    for row in reader:
                        # work type is assumed by the presence of format-specific column headers
                        if "Width (cm.)" in reader.fieldnames:
                            work_type = "IMAGE"
                        elif "Speed IPS" in reader.fieldnames:
                            work_type = "AUDIO"
                        elif "Region" or "Stock" in reader.fieldnames:
                            work_type = "VIDEO"
                        else:
                            print(
                                """\n---ERROR: Unable to determine 
                                  work_type. ---\n"""
                            )
                            print(
                                """make sure that your inventory has the 
                                  necessary format-specific columns"""
                            )
                            print(
                                '''IMAGE: "Width (cm.)" \n AUDIO: "Speed 
                                  IPS" \n VIDEO: "Region" or "Stock"'''
                            )
                            quit()
                        name = row["filename"]
                        if work_type == "AUDIO" or work_type == "VIDEO":
                            if not args.desc:
                                description_fields = ["inventory_title"]
                            else:
                                description_fields = args.desc
                            missing_descriptive_fieldnames = [
                                a
                                for a in description_fields
                                if not a in reader.fieldnames
                            ]
                            if missing_descriptive_fieldnames:
                                missing_fieldnames = True
                                description_fields = update_fieldname_list
                                (description_fields, missing_descriptive_fieldnames)
                            description_list = []
                            for header in description_fields:
                                # TODO make this its own function since it's probably going to get repeated
                                description_list.append(row[header])
                            description = "; ".join(i for i in description_list if i)
                            # description.update({'descriptive': row[header]})
                            if not "label" in reader.fieldnames:
                                inventory_label = None
                            else:
                                inventory_label = row["label"]
                            # if work_type == "VIDEO" and 'Region' in reader.fieldnames:
                            csvData = {
                                "filename": row["filename"],
                                "work_type": work_type,
                                "work_accession_number": row["work_accession_number"],
                                "description": description,
                                "label": inventory_label,
                            }
                        elif work_type == "IMAGE":
                            csvData = {
                                "filename": row["filename"],
                                "label": row["label"],
                                "work_type": work_type,
                                "work_accession_number": row["work_accession_number"],
                                "file_accession_number": row["file_accession_number"],
                                "role": row["role"],
                                "description": row["description"],
                            }
                        else:
                            print(
                                "--- ERROR: Problem identifying work type in "
                                + i
                                + " ---"
                            )
                            quit()
                        csvDict.append(csvData)
                        # print(csvDict)
                    if missing_fieldnames == True:
                        missing_description_field_handler(
                            missing_descriptive_fieldnames
                        )
            else:
                print("\n--- ERROR: " + i + " is not a file ---\n")
                quit()
        else:
            print("\n--- ERROR: Inventory path is not valid ---\n")
        source_inventory_dictlist.extend(csvDict)
    # print(source_inventory_dictlist)
    # quit()
    return source_inventory_dictlist

if __name__ == "__main__":
    main()
