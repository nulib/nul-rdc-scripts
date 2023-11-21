import os
from Arguments import args


def input_check():
    if args.input_path:
        indir = args.input_path
    else:
        print("No input provided")
        quit()
    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    return indir
