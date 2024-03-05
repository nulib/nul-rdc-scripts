import argparse

parser = argparse.ArgumentParser(
    description="Allows for input to generate the ffplay window with analysis tools"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter full path to the file you want to analyze",
)

parser.add_argument(
    "--ffplay",
    "-play",
    action="store",
    dest="ffplay_path",
    default="ffplay",
    type=str,
    help="Enter the path to ffplay if it is not on your path",
)

parser.add_argument(
    "--highlight",
    "-hi",
    action="store",
    dest="highlight_color",
    default="red",
    type=str,
)

args = parser.parse_args()
