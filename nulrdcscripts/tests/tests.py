import os
import subprocess
import nulrdcscripts.tests.colors as colors
import nulrdcscripts.tests.aproc_test as aproc_test
import nulrdcscripts.tests.vproc_test as vproc_test
import nulrdcscripts.tests.ingest_test as ingest_test
from nulrdcscripts.tests.params import args

def main():
    """
    Runs the test of users choosing.
    """
    tests_path = get_tests_path()
    if args.ingest:
        input_path = os.path.join(tests_path, "ingest_test")
        ingest_command = ["poetry", "run", "ingest", "-i", input_path]
        print("*running ingest on ingest_tests*")
        print(colors.CONSOLE)
        subprocess.run(ingest_command)
        print(colors.DEFAULT)
        print("*testing ingest output*")
        ingest_test.main(tests_path)
    elif args.vproc:
        input_path = os.path.join(tests_path, "vproc_test")
        vproc_command = ["poetry", "run", "vproc", "-b", "-i", input_path]
        print("*running vproc on vproc_tests*")
        print(colors.CONSOLE)
        subprocess.run(vproc_command)
        print(colors.DEFAULT)
        print("*testing vproc output*")
        vproc_test.main(tests_path)
    elif args.aproc:
        input_path = os.path.join(tests_path, "aproc_test")
        aproc_command = ["poetry", "run", "aproc", "-a", "-i", input_path]
        print("*running aproc on aproc_tests*")
        print(colors.CONSOLE)
        subprocess.run(aproc_command)
        print(colors.DEFAULT)
        print("*testing aproc output*")
        aproc_test.main(tests_path)

def get_tests_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_txt = os.path.join(current_dir, "tests_path.txt")

    if not os.path.isfile(path_txt):
        f = open(path_txt, "x")
        f.close()

    with open(path_txt) as f:
        tests_path = f.read()
    if not os.path.isdir(tests_path):
        while True:
            print("Please enter path to tests folder: ")
            tests_path = input()
            if not os.path.isdir(tests_path):
                print("ERROR: not a valid path")
            else:
                break
        with open(path_txt, "w") as f:
            f.write(tests_path)
    return tests_path

if __name__ == "__main__":
    main()
