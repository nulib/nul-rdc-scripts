#!/usr/bin/env python3

import sys
from nulrdcscripts.ingest.Ingest_Sheet_Maker import Ingest_Sheet_Maker

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():

    ingester = Ingest_Sheet_Maker()
    ingester.run()

    # TODO error out if duplicate filenames are found
    # TODO add a check for existing file with filename before overwriting
    # TODO final check that all ihidden files and folderstems from filename list are accounted for in the final inventory
    # TODO add early warning if spreadsheet is missing important columns like work_accession_number

if __name__ == "__main__":
    main()
