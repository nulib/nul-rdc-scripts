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

    :var str indir: fullpath to input directory
    :var str outfile: fullpath to output csv file
    :var list[dict] role_dict: contains rules for role assignment
    :var dict[str, int] num_roles: counts number of each role type
    :var list[dict] inventory_dictlist: contains inventory data
    :var list[dict] ingest_dictlist: contains ingest sheet data
    :var str work_type: type of work ingest sheet is for
    """
    def __init__(
            self, 
            indir: str, 
            outfile: str, 
            x_parse: str
        ):
        """
        Initializes Ingest_Sheet_Maker input, output, role assignment rules,
        and starts counter for number of roles.

        :param str indir: fullpath to input folder
        :param str outfile: fullpath to output csv file
        :param str x_parse: sets how x files are parsed
        .. note: x_parse can be "extension", "parse", or None
        """
        self.indir: str
        """fullpath to input directory"""
        self.outfile: str
        """fullpath to output csv file"""
        self.indir, self.outfile = helpers.init_io(
            indir,
            outfile
        )
        self.inventory_dictlist: list[dict[str, str]] = None
        """contains inventory data"""

        self.role_dict = ing_helpers.get_role_dict(x_parse)
        """contains rules for role assignment"""

        self.num_roles = {
            "A": 0,
            "P": 0,
            "S": 0,
            "X": 0,
        }
        """counts number of each role type"""

    def load_inventory(self, inventory_path: str, description_fields: list[str]):
        """
        Loads data from csv to be used during ingest.

        .. note: will search for inventory in indir if none is given

        :param str inventory_path: fullpath to inventory or None
        :param list[str] description_fields: contains inventory fields to use in ingest label
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
        Walks through input directory and analyzes valid files before creating ingest csv.

        :param list[str] skip: contains file types to skip
        :param str prepend: added to beginning of file_accession_number
        """

        self.ingest_dictlist: list[dict[str, str]] = {}
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

        :param str file name of file to be analyzed
        :param str parent_dir: fullpath to parent directory of file
        :param str prepend: added to beginning of file_accession_number
        """
        # TODO add safety check to make sure there aren't multiple matches for a filename in the accession numbers
        # TODO handle cases where there is no inventory
        for item in self.inventory_dictlist:
            if not item["filename"] in filename:
                continue

            # if corresponding item is found
            u_file: str = helpers.get_unix_fullpath(filename, parent_dir)
            work_accession_number: str = item["work_accession_number"]
            description: str = ing_helpers.get_ingest_description(item, filename)
            
            #options for image or AV
            if self.work_type == "IMAGE":
                role = item["role"]
                label = item["label"]
                file_accession_number = item["file_accession_number"]
            else:
                label, role, file_builder = self.get_ingest_LRF(
                    filename, item["label"]
                )
                file_accession_number = work_accession_number + file_builder + f'{self.num_roles[role]:03d}'
            # prepend to file_accession_number
            if prepend:
                file_accession_number = prepend + file_accession_number
            # create meadow dict for file
            meadow_file_dict: dict[str, str]= {
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
            return
        # TODO build out how to handle cases where a file is not found in the inventory
        # allow user to add the file anyway
        # only gets here if file isnt found
        print(
            "+++ WARNING: No entry matching " + filename + 
            " was found in your inventory +++"
        )

    def get_ingest_LRF(self, filename: str, inventory_label: str):
        """
        Gets label, role, and file builder for ingest sheet.

        :param str filename: name of input file
        :param str inventory_label: label created from inventory
        :returns: label, role, and file_builder for ingest sheet
        :rtype: tuple of str
        """
        # run through each key in role_dict
        role_index = -1
        for i in self.role_dict:
            if any(ext in filename for ext in self.role_dict[i]["identifiers"]):
                role_index = i
                break

        role: str
        label: str
        file_builder: str
        # base case if role not found
        if role_index == -1:
            label = filename
            role = "S"
            file_builder = "_supplementary_"
        else:
            role  = self.role_dict[role_index]["role"]
            file_builder  = self.role_dict[role_index]["file_builder"]
            label = ing_helpers.ingest_label_creator(filename, inventory_label)

            #append label if role has extra info
            if self.role_dict[role_index]["label"]:
                label += " " + self.role_dict[role_index]["label"]
        # track number of files with this role and return
        self.num_roles[role] = self.num_roles[role] + 1
        return label, role, file_builder