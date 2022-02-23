#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    from image_ingest_sheet import image_ingest_sheet
    image_ingest_sheet.csv_main()

if __name__ == "__main__":
	main()
