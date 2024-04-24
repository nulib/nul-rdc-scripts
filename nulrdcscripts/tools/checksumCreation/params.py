import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    acition="store",
    dest="input_path",
    type=str,
    help="full path to input folder",
)

args = parser.parse_args()
