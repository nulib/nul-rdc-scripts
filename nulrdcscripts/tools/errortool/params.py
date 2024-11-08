import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    default = "Z:\\RDC\\ACTIVE_AV\\errorReports",
    type=str,
    help="full path to output folder",
)
args = parser.parse_args()