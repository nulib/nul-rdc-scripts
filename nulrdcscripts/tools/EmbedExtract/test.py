import os
import subprocess
from setupparser import args


def main():
    ext = [".wav", ".mp3"]
    input_path = os.path.normpath(args.input_path)
    isDIRTF = os.path.isdir(args.input_path)

    if isDIRTF:
        outputFolder = os.path.join(input_path, "JSON")
        os.mkdir(outputFolder)
        for root, dirs, files in os.walk(input_path):
            for filename in files:
                file = os.path.join(root, filename)
                if filename.endswith(".wav") or filename.endswith(".mp3"):
                    name = os.path.basename(file)
                    outname1 = name.replace(".wav", "")
                    outname2 = outname1.replace(".mp3", "")
                    outname = outname2 + ".json"
                    output = os.path.join(outputFolder, outname)
                    command = (
                        args.mediainfo_path,
                        "-i",
                        file,
                        "--LogFile=",
                        output,
                    )
                    with open(output, "w") as f:
                        subprocess.run(command, stdout=f)
                else:
                    pass
            else:
                pass
    else:
        if input_path.endswith(".wav") or input_path.endswith(".mp3"):
            name = os.path.basename(input_path)
            outname1 = name.replace(".wav", "")
            outname2 = outname1.replace(".mp3", "")
            outname = outname2 + ".json"
            output = os.path.join(outputFolder, outname)
            command = (
                args.mediainfo_path,
                "-i",
                file,
                "--LogFile=",
                output,
            )
            with open(output, "w") as f:
                subprocess.run(command, stdout=f)
        else:
            pass
