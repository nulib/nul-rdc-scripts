import os
import subprocess
from nulrdcscripts.tools.generateaccess.params import args


def main():
    input_path = os.path.abspath(args.input_path)
    if os.path.isfile(input_path):
        if input_path.endswith(".mkv"):
            transcode(input_path)
        else:
            raise Exception(
                "This file type or folder currently is not accepted by this script. A .mkv file is required"
            )
    else:
        raise Exception(
            "This file type or folder currently is not accepted by this script. A .mkv file is required"
        )


def transcode(file_path):
    transcode_pass = [1, 2]
    outfile = file_path.replace("_p.mkv", "_a.mp4")
    for item in transcode_pass:
        standard_input = f"-c:v libx264 -preset medium -b:v 8000k -pass {item} -filter_complex '[0:a:0]aformat=channel_layouts=stereo[a0];[0:a:1]aformat=channel_layouts=stereo[a1]; amerge=inputs=2[a]' -map 0:v -map '[a]' -map -0:t -f mp4"
        if item == 1:
            print("Running first pass")
            command = f"ffmpeg -y -i {file_path} {standard_input} nul"
            print("Finished first pass")
        else:
            print("Running second pass")
            command = f"ffmpeg -y -i {file_path} {standard_input} {outfile}"
            print("Finished second pass")
        subprocess(command)


if __name__ == "__main__":
    main()
