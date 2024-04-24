import argparse

parser = argparse.ArgumentParser(
    description="Allows for input to generate the ffprobe video data"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter full path to the file you want to generate metadata for",
)

parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="Enter the path to where you want your output",
)

parser.add_argument(
    "--ffprobe",
    action="store",
    dest="ffprobe_path",
    default="ffprobe",
    type=str,
    help="Enter the path to ffprobe if it is not on your path",
)

args = parser.parse_args()
