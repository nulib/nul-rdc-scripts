"""
Checks the result of ingest_test.
"""

import os
import platform
import subprocess

def main(current_dir):
    # setup directories
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    ingest_test_dir = os.path.join(current_dir, "ingest_test")

    # get paths to ingest sheets to compare
    ingest_path = os.path.join(ingest_test_dir, "ingest_test_ingest.csv")
    if not os.path.isfile(ingest_path):
        print("ERROR: ingest sheet not found.")
        quit()
    correct_ingest_path = os.path.join(correct_results_dir, "ingest_test_ingest.csv")

    # print error and quit if not windows
    if not platform.system() == "Windows":
        print("ERROR: this script must be run on Windows.")
        print("\nOtherwise, compare the following files manually:")
        print("Test results: " + ingest_path)
        print("Correct results: " + correct_ingest_path)
        quit()

    #run windows compare command
    compare_command = ["fc", ingest_path, correct_ingest_path]
    subprocess.run(compare_command)

    # prompt user to reset
    print("Reset? (y/n): ", end="")
    answer = input()
    if answer.lower() == "y":
        os.remove(ingest_path)

if __name__ == "__main__":
	main()