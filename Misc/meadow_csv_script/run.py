#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    from meadow_csv_script import meadow_csv_mainfunc
    meadow_csv_mainfunc.csv_main()

if __name__ == "__main__":
	main()
