import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter the full path to the access file",
)
parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    required=False,
    type=str,
    help="Enter the full output path for where you want your JSON file to be located",
)


args = parser.parse_args()
