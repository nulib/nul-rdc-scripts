import os
import subprocess
from nulrdcscripts.tools.generateaccess.params import args


def single_run(input):
    if input.endswith("_p.mkv"):
        outputfile = input.replace("_p.mkv", "_a.mp4")
    else:
        if input.endswith(".mkv"):
            base, ext = os.path.splitext(input)
            inputnew = base + "_p.mkv"
            os.rename(input, inputnew)
            input = inputnew
            outputfile = input.replace("_p.mkv", "_a.mp4")
        else:
            raise Exception(
                "This file type is not supported by the script. File must be an .mkv with an end of .mkv or _p.mkv to work."
            )

    basecommand = [
        "ffmpeg",
        "-y",
        "-i",
        input,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        "8000k",
    ]
    filtercommand = [
        "-filter_complex",
        "[0:a:0]aformat=channel_layouts=stereo[a0];[0:a:1]aformat=channel_layouts=stereo[a1];[a0][a1]amerge=inputs=2[a]",
    ]
    mapcommand = ["-map", "0:v", "-map", "[a]", "-map", "-0:t", "-f", "mp4"]

    pass1command = basecommand + ["-pass", "1"] + filtercommand + mapcommand + ["nul"]
    subprocess.run(pass1command)
    pass2command = (
        basecommand + ["-pass", "1"] + filtercommand + mapcommand + outputfile
    )
    subprocess.run(pass2command)


def main():
    input_path = os.path.abspath(args.input_path)
    mkvs = []
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path, topdown=True):
            for file in files:
                if file.endswith(".mkv"):
                    mkvs.append(os.path.join(root, file))
        for mkv in mkvs:
            single_run(mkv)
    else:
        if input_path.endswith(".mkv"):
            single_run(input_path)
        else:
            raise Exception(
                "This file type is not accepted for transcoding. Try again."
            )


if __name__ == "__main__":
    main()
