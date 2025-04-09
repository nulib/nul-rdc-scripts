import os
import progressbar
import subprocess
import time
from nulrdcscripts.tools.ffprobeExtraction.params import args


def main():
    # Check if the input file exists
    if not os.path.isfile(args.input_path):
        print(f"Error: The input file '{args.input_path}' does not exist.")
        return

    if args.output_format == "JSON" or args.output_format == "json":
        output_format = "json"
    elif args.output_format == "XML" or args.output_format == "xml":
        output_format = "xml"
    else:
        raise ValueError(
            "This file format is not supported by this script for ffprobe data extraction."
        )

    output_path = os.path.splitext(args.input_path)[0] + {output_format}

    input_path = os.path.abspath(args.input_path)
    output_path = os.path.abspath(output_path)

    command = f'ffprobe -f lavfi -i "movie={input_path},signalstats" -show_frames -show_streams -of {output_format} > {output_path}'
    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    for i in range(100):
        time.sleep(0.1)
        bar.update(i)

    subprocess.run(command)


if __name__ == "__main__":
    main()
