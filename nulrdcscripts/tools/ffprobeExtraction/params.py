import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    help="full path to input file",
)

parser.add_argument(
    "-of",
    "--outputformat",
    action="store",
    dest="output_format",  # <-- change here
    default="xml",
    type=str,
    help="format that you want the ffprobe report to be in. JSON is the default and the other accepted value is XML",
)
args = parser.parse_args()
