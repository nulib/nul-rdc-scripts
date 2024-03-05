#!/usr/bin/env python3

"""
Runner file for Ingest_Sheet_Maker class.

.. note::
    Uses command line arguments from params.py
"""

import sys
from nulrdcscripts.ingest.params import args
from nulrdcscripts.ingest.Ingest_Sheet_Maker import Ingest_Sheet_Maker

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    """
    Creates an Ingest_Sheet_Maker, loads an inventory, and creates the ingest sheet.
    """
    ingester = Ingest_Sheet_Maker(
        args.input_path,
        args.output_path,
        args.x_parse,
    )
    ingester.load_inventory(args.inventory_path, args.desc)
    ingester.run(args.skip, args.prepend)

    # TODO error out if duplicate filenames are found
    # TODO add a check for existing file with filename before overwriting
    # TODO final check that all ihidden files and folderstems from filename list are accounted for in the final inventory
    # TODO add early warning if spreadsheet is missing important columns like work_accession_number

if __name__ == "__main__":
    main()
