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
    default = "NA",
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
),
parser.add_argument(
    "--ffprobe",
    action="store",
    dest="ffprobe_path",
    default="ffprobe",
    type=str,
    help="For setting a custom ffprobe path",
)
parser.add_argument(
    "--sox",
    action="store",
    dest="sox_path",
    default="sox",
    type=str,
    help="For setting a custom sox path",
)
args = parser.parse_args()