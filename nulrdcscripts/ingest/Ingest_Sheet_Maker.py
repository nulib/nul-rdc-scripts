#!/usr/bin/env python3

"""
Contains class for creating an ingest sheet csv file
"""

import os
from nulrdcscripts.ingest.params import args
import nulrdcscripts.ingest.helpers as helpers
import nulrdcscripts.ingest.inventory_helpers as inv_helpers
import nulrdcscripts.ingest.ingest_helpers as ing_helpers

class Ingest_Sheet_Maker:
    """
    a class for creating ingest sheet csv files

    Attributes:
        indir (str): fullpath to input directory
        outfile (str): fullpath to output csv file
        role_dict (dict of str: str): contains rules for role assignment
        num_roles (dict of str: int): counter for number of each role
        inventory_dictlist (list of dict of str: str): contains inventory data
        ingest_sheet_dict (list of dict of str: str): contains ingest sheet data
        work_type (str): type of work ingest sheet is for
    """
    def __init__(self):
        """
        sets up ingest sheet maker
        """
        self.indir, self.outfile = helpers.init_io(
            args.input_path,
            args.output_path
        )
        self.role_dict = ing_helpers.get_role_dict(args.aux_parse)
        self.init_inventory(args.source_inventory)
        # track # of each role for file_accession_number creation
        self.num_roles = {
            "A": 0,
            "P": 0,
            "S": 0,
            "X": 0,
        }

    def run(self):
        """
        Walks through input directory and analyzes valid files before creating ingest csv
        """
        self.ingest_sheet_dict = {}
        for subdir, dirs, files in os.walk(self.indir):
            # files and subdirs are "cleaned" in separate functions before analyzing
            for file in helpers.clean_files(files, args.skip):
                self.analyze_file(
                    file, 
                    helpers.clean_subdir(subdir, self.indir), 
                    args.prepend
                )
        helpers.write_csv(
            self.outfile, 
            ing_helpers.get_fields(), 
            self.ingest_sheet_dict
        )
        print("Process complete!")
        print("Meadow inventory located at: " + self.outfile)

    def init_inventory(self, source_inventory):
        """
        Creates inventory_dictlist used to create ingest sheet

        Note:
            Will search for inventory in indir if none is given

        Args:
            source_inventory (str): fullpath to inventory
        """
        self.inventory_dictlist = []
        if not source_inventory:
            inventory_path = inv_helpers.find_inventory(self.indir)
            print("Inventory found in input directory")
        else:
            # index source_inventory at 0 because of argparse formatting
            inv_helpers.check_inventory(source_inventory[0])
            inventory_path = source_inventory
            print("Inventory found")

        self.inventory_dictlist, self.work_type = inv_helpers.load_inventory(
            inventory_path, args.desc
        )

    def analyze_file(self, file, subdir, prepend):
        """
        Analyzes file and appends data to ingest sheet dictionary
        """
        # TODO add safety check to make sure there aren't multiple matches for a filename in the accession numbers
        # TODO handle cases where there is no inventory
        for item in self.inventory_dictlist:
            if not item["filename"] in file:
                return
            
            # if corresponding item is found
            filename = helpers.get_unix_fullpath(file, subdir)
            work_accession_number = item["work_accession_number"]
            description = self.get_ingest_description(item, file)
            
            #options for image or AV
            if self.work_type == "IMAGE":
                role = item["role"]
                label = item["label"]
                file_accession_number = item["file_accession_number"]
            else:
                label, role, file_builder = self.get_ingest_LRF(
                    file, item["label"]
                )
                file_accession_number = filename + file_builder + f'{self.num_roles[role]:03d}'
            # prepend to file_accession_number
            if prepend:
                file_accession_number = prepend + file_accession_number
            # create meadow dict for file
            meadow_file_dict = {
                "work_type": self.work_type,
                "work_accession_number": work_accession_number,
                "file_accession_number": file_accession_number,
                "filename": filename,
                "description": description,
                "label": label,
                "role": role,
                "work_image": None,
                "structure": None,
            }
            # Add file to ingest_sheet_dict
            # Either creating a new key or using an existing one
            if item["filename"] not in self.ingest_sheet_dict:
                self.ingest_sheet_dict[item["filename"]] = [meadow_file_dict]
            else:
                self.ingest_sheet_dict[item["filename"]].append(meadow_file_dict)
        # TODO build out how to handle cases where a file is not found in the inventory
        # allow user to add the file anyway
        if not any(item["filename"] in file for item in self.inventory_dictlist):
            print(
                "+++ WARNING: No entry matching " + file + 
                " was found in your inventory +++"
            )

    def get_ingest_description(self, item, file):
        """
        return the item description or auto-fill if description is empty
        """
        if not item["description"]:
            return file
        else:
            return item["description"]

    def get_ingest_LRF(self, filename, inventory_label):
        """
        Returns meadow role, label, and file_builder
        """
        # run through each key in role_dict
        role_index = -1
        for i in self.role_dict:
            if any(ext in filename for ext in self.role_dict[i]["identifiers"]):
                role_index = i
                break
        # base case if role not found
        if role_index == -1:
            label = filename
            role = "S"
            file_builder = "_supplementary_"
        else:
            role = self.role_dict[role_index]["role"]
            file_builder = self.role_dict[role_index]["file_builder"]
            label = ing_helpers.ingest_label_creator(filename, inventory_label)

            #append label if role has extra info
            if self.role_dict[role_index]["label"]:
                label += " " + self.role_dict[role_index]["label"]
        # track number of files with this role and return
        self.num_roles[role] = self.num_roles[role] + 1
        return label, role, file_builder

# os.walk management