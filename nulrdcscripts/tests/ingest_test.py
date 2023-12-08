"""
Checks the result of ingest_test.
"""

import os
import platform
import subprocess
import difflib
import nulrdcscripts.tests.colors as colors

def main(current_dir):
    # setup directories
    correct_results_dir: str = os.path.join(current_dir, "CORRECT")
    ingest_test_dir: str = os.path.join(current_dir, "ingest_test")

    # get paths to ingest sheets to compare
    ingest_path: str = os.path.join(ingest_test_dir, "ingest_test_ingest.csv")
    if not os.path.isfile(ingest_path):
        print("ERROR: ingest sheet not found.")
        quit()
    correct_ingest_path: str = os.path.join(correct_results_dir, "ingest_test_ingest.csv")

    # read in both ingest sheets
    with open(ingest_path) as f:
        ingest: list[str] = f.read().splitlines()
    with open(correct_ingest_path) as f:
        correct_ingest: list[str] = f.read().splitlines()
    
    # use unified diff to get pretty printout of differences
    dif: list[str] = list(difflib.unified_diff(correct_ingest, ingest, "", "", "", "", 0))

    print("ingest_test_ingest.csv...", end="")

    # if no differences, pass
    if len(dif) == 0:
        print(colors.PASS + "pass!" + colors.DEFAULT)
    # otherwise print fail and color coded differences
    # green is whats in the correct csv
    # red is whats in the test version
    else:
        print(colors.FAIL + "fail!")
        print(colors.DEFAULT)
        print("Comparing " + colors.PASS + correct_ingest_path + 
            colors.DEFAULT + " to " + colors.FAIL + ingest_path)
        print(colors.DEFAULT)
        for line in dif:
            if line[0] == "-":
                print(colors.PASS + line + colors.DEFAULT)
            elif line[0] == "+":
                print(colors.FAIL + line + colors.DEFAULT)
            else:
                print(line)

    # prompt user to reset
    print("\nreset? (y/n): ", end="")
    answer = input()
    if answer.lower() == "y":
        print(colors.DELETE)
        print("deleting " + ingest_path)
        os.remove(ingest_path)
        print(colors.DEFAULT, end="")

if __name__ == "__main__":
	main()