#!/usr/bin/env python3

"""
Contains class for creating an ingest sheet csv file.
"""

import os
import nulrdcscripts.ingest.helpers as helpers
import nulrdcscripts.ingest.inventory_helpers as inv_helpers
import nulrdcscripts.ingest.ingest_helpers as ing_helpers

class Ingest_Sheet_Maker:
    """
    a class for creating ingest sheet csv files

    Note:
        Uses args from params.py

    Attributes:
        indir (str): fullpath to input directory
        outfile (str): fullpath to output csv file
        role_dict (list of dict): contains rules for role assignment
        num_roles (dict of str: int): counter for number of each role
        inventory_dictlist (list of dict of str: str): contains inventory data
        ingest_dictlist (list of dict of str: str): contains ingest sheet data
        work_type (str): type of work ingest sheet is for

    Methods:
        load_inventory(inventory_path, description_fields): loads inventory data from csv
        run(skip, prepend): creates ingest csv from files in input directory
    """
    def __init__(
            self, 
            indir: str, 
            outfile: str, 
            x_parse: str,
        ):
        """
        Initializes Ingest_Sheet_Maker input, output, role assignment rules,
        and starts counter for number of roles.

        Args:
            indir (str): fullpath to input folder
            outfile (str): fullpath to output csv file
            x_parse (str): sets how x files are parsed
                "extension" or "parse"
        """
        self.indir, self.outfile = helpers.init_io(
            indir,
            outfile
        )
        self.inventory_dictlist = None
        self.role_dict = ing_helpers.get_role_dict(x_parse)
        # track # of each role for file_accession_number creation
        self.num_roles = {
            "A": 0,
            "P": 0,
            "S": 0,
            "X": 0,
        }

    def load_inventory(self, inventory_path: str, description_fields: list[str]):
        """
        Creates inventory_dictlist used to create ingest sheet

        Note:
            Will search for inventory in indir if none is given

        Args:
            inventory_path (str): fullpath to inventory or None
            description_fields (list of str): contains inventory fields to use in ingest label
        """
        self.inventory_dictlist = []
        if not inventory_path:
            inventory_path = inv_helpers.find_inventory(self.indir)
            if not inventory_path:
                print("\n--- ERROR: Unable to find inventory in input directory ---")
                quit()
                # commmented out until this feature is added
                # print("\n--- WARNING: Unable to find inventory in input directory ---")
                # if not helpers.yn_check("Continue?"):
                #     quit()
            else:
                print("Inventory found in input directory")
        else:
            inv_helpers.check_inventory(inventory_path)
            inventory_path = inventory_path
            print("Inventory found")

        self.inventory_dictlist, self.work_type = inv_helpers.load_inventory(
            inventory_path, description_fields
        )

    def run(self, skip: list[str], prepend: str):
        """
        Walks through input directory and analyzes valid files before creating ingest csv

        Args:
            skip (list of str): contains file types to skip
            prepend (str): added to beginning of file_accession_number
        """

        self.ingest_dictlist = {}
        for subdir, dirs, files in os.walk(self.indir):
            # files and subdirs are "cleaned" in separate functions before analyzing
            for file in helpers.clean_files(files, skip):
                self.analyze_file(
                    file, 
                    helpers.clean_subdir(subdir, self.indir), 
                    prepend
                )
        helpers.write_csv(
            self.outfile, 
            ing_helpers.get_fields(), 
            self.ingest_dictlist
        )
        print("Process complete!")
        print("Meadow inventory located at: " + self.outfile)

    def analyze_file(self, filename: str, parent_dir: str, prepend: str = ""):
        """
        Analyzes file and appends data to ingest sheet dictionary

        Args:
            file (str): name of file to be analyzed
            parent_dir (str): fullpath to parent directory of file
            prepend (str): added to beginning of file_accession_number
        """
        # TODO add safety check to make sure there aren't multiple matches for a filename in the accession numbers
        # TODO handle cases where there is no inventory
        for item in self.inventory_dictlist:
            if not item["filename"] in filename:
                return
            
            # if corresponding item is found
            u_file = helpers.get_unix_fullpath(filename, parent_dir)
            work_accession_number = item["work_accession_number"]
            description = ing_helpers.get_ingest_description(item, filename)
            
            #options for image or AV
            if self.work_type == "IMAGE":
                role = item["role"]
                label = item["label"]
                file_accession_number = item["file_accession_number"]
            else:
                label, role, file_builder = self.get_ingest_LRF(
                    filename, item["label"]
                )
                file_accession_number = u_file + file_builder + f'{self.num_roles[role]:03d}'
            # prepend to file_accession_number
            if prepend:
                file_accession_number = prepend + file_accession_number
            # create meadow dict for file
            meadow_file_dict = {
                "work_type": self.work_type,
                "work_accession_number": work_accession_number,
                "file_accession_number": file_accession_number,
                "filename": u_file,
                "description": description,
                "label": label,
                "role": role,
                "work_image": None,
                "structure": None,
            }
            # Add file to ingest_dictlist
            # Either creating a new key or using an existing one
            if item["filename"] not in self.ingest_dictlist:
                self.ingest_dictlist[item["filename"]] = [meadow_file_dict]
            else:
                self.ingest_dictlist[item["filename"]].append(meadow_file_dict)
        # TODO build out how to handle cases where a file is not found in the inventory
        # allow user to add the file anyway
        if not any(item["filename"] in filename for item in self.inventory_dictlist):
            print(
                "+++ WARNING: No entry matching " + filename + 
                " was found in your inventory +++"
            )

    def get_ingest_LRF(self, filename: str, inventory_label: str):
        """
        Gets label, role, and file builder for ingest sheet

        Args:
            filename (str): name of input file
            inventory_label (str): label created from inventory

        Returns:
            label (str): label for ingest sheet
            role (str): role for ingest sheet
            file_builder (str): used for file_access_number creation
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