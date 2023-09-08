import os
from Arguments import args


def output_check():
    if args.input_path:
        outdir = args.output_path
    else:
        print("No output given. Using input as directory")
        outdir = args.input_path
    if not os.path.isdir(outdir):
        print("Output is not a directory")
        quit()
    return outdir
