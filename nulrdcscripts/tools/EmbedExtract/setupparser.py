import argparse

parser = argparse.ArgumentParser(
    description="Allows for the input of a batch of files or a singular file to have metadata extracted into a JSON file"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter the full path to the input file or folder",
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

parser.add_argument(
    "--mediainfo",
    "-mediainfo",
    action="store",
    dest="mediainfo_path",
    default="mediainfo",
    type=str,
    help="Enter path to mediainfo if it is not in your path",
)

args = parser.parse_args()
