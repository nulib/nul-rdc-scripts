import argparse


parser = argparse.ArgumentParser(
    description="Allows for input of files to be run through ffmpeg to generate data reports"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter the full path to the input file",
)

parser.add_argument(
    "--ffprobe",
    action="store",
    dest="ffprobe_path",
    default="ffprobe",
    type=str,
    help="Enter file path for ffprobe - optional if it is in path",
)

args = parser.parse_args()
