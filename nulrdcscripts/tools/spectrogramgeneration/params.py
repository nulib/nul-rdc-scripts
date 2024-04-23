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
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="full path to output folder",
)
parser.add_argument(
    "--ffmpeg",
    action="store",
    dest="ffmpeg_path",
    default="ffmpeg",
    type=str,
    help="For setting a custom ffmpeg path",
)
args = parser.parse_args