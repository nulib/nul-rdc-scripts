#!/usr/bin/env python3

"""
Contains argument parser for ingest.py
"""

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action = "store",
    dest = "input_path",
    type = str,
    help = "Full path to input folder. Uses current folder if none is provided.",
)
parser.add_argument(
    "--output",
    "-o",
    action = "store",
    dest = "output_path",
    type = str,
    help = "Full path to output csv file. Creates one in input folder if none is provided.",
)
parser.add_argument(
    "--load_inventory",
    "-l",
    required = False,
    type = str,
    action = "store",
    dest = "inventory_path",
    help = "Full path to inventory csv. If not specified the script will look in the base folder of the input for inventories. If no inventories are found the script will leave some fields blank.",
)
parser.add_argument(
    "--skip",
    "-s",
    required = False,
    nargs = "*",
    action = "store",
    dest = "skip",
    help = 'Use to specify patterns to skip. Can take multiple inputs. For example, "_ac." "_am." could be used to skip legacy ac and am files.',
)
parser.add_argument(
    "--description",
    "-d",
    required = False,
    nargs = "*",
    action = "store",
    dest = "desc",
    help = 'Use to specify column names to populate Meadow description field with. Can take multiple inputs. Information from each column will be separated by a ";" in the description. Example usage: -d "Date/Time" "Barcode". If not specified, script will default to looking for the column "inventory_title"',
)
parser.add_argument(
    "--auxiliary",
    "-x",
    required = False,
    default = "extension",
    type = str,
    action = "store",
    dest = "x_parse",
    choices = ["extension","parse", None],
    help = "Sets how to parse auxiliary files. Default is extension.",
)
parser.add_argument(
    "--prepend_accession",
    "-p",
    action = "store",
    dest = "prepend",
    type = str,
    help = "set a string to be added to the beginning of the file accession number when generated",
)

args = parser.parse_args()