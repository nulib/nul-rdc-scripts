import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    required = True,
    help="full path to input folder",
)

parser.add_argument(
    "-s",
    "--start",
    dest="start_time",
    required = True,
    action = "store",
    type=str,

)

parser.add_argument(
    "-e",
    "--end_time",
    action = "store",
    required = True,
    dest="end_time",
    type = str,
)

parser.add_argument(
    "-ffmpeg",
    "--ffmpeg_path",
    default = "ffmpeg",
    action ="store",
    type=str,
    dest="ffmpeg_path"
)

args = parser.parse_args()