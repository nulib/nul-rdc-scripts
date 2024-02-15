import os
import subprocess
from nulrdcscripts.tools.oyez.setupparser import args


def main():
    ext = [".wav", ".mp3"]
    input_path = os.path.normpath(args.input_path)
    isDIRTF = os.path.isdir(args.input_path)

    if isDIRTF:
        for files in os.walk(input_path):
            for file in files:
                if file.endswith(".wav") or file.endswith(".mp3"):
                    command = (
                        args.mediainfo_path,
                        " -i ",
                        file,
                        " --LogFile=",
                        file,
                        ".json",
                    )
                    fullfilename = filename + ".json"
                    with open(fullfilename, "w") as f:
                        subprocess.run(command, stdout=f)
                else:
                    pass
    else:
        filename, file_ext = os.path.splitext(input_path)
        if file_ext == ".wav" or file_ext == ".mp3":
            command = (
                args.mediainfo_path,
                "-i",
                input_path,
                "--LogFile=",
                filename,
                ".json",
            )
            fullfilename = filename + ".json"
            with open(fullfilename, "w") as f:
                subprocess.run(command, stdout=f)

        else:
            raise ValueError("This file is not a .wav or .mp3 file.")

    filecheck = filename + ".json"
    with open(fullfilename, "r") as file:
        file.read()


if __name__ == "__main__":
    main()
