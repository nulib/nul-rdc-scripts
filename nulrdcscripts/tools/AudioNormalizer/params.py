import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    dest="input_path",
    action = "store",
    type = str,
    required=True, 
    help = "Enter your input_path to the file or folder of files that you want to normalize"
)

parser.add_argument(
    "-ffmpeg-norm",
    dest="ffmpeg_norm_path",
    default="ffmpeg-normalize",
    action="store",
    type=str,

) 

args = parser.parse_args()
