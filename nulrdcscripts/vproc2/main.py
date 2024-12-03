import os
import subprocess
from nulrdcscripts.tools.checksoftware import main as checksoftwaremain
from nulrdcscripts.tools.spectrogramgeneration import main as spectrogramgenerationmain
from nulrdcscripts.tools.md5generation import main as md5generationmain
from nulrdcscripts.vproc2.params import args

software_check = [args.ffmpeg_path, args.ffprobe_path]
filetypes = ["mkv", "mp4"]
for i in software_check:
    checksoftwaremain(i)


def checkfolder(input_dir):
    folderTF = os.path.isdir(input_dir)
    if folderTF:
        pass
    else:
        raise Exception(
            "The given input path is not a folder. Please provide a folder location."
        )


def transcodeaccess(audioStreamCounter, filename, accfile):
    prefix = (
        "-y",
        "-i",
        filename,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        "8000k",
        "-pix_fmt",
        "yuv420p",
    )
    mix4to3 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-map",
        "0:a:2",
        "-map",
        "0:a:3",
    )
    mix4to2 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-map",
        "[b]",
    )
    mix2to1 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
    )
    if os.name == "nt":
        nullOut = "NUL"
    else:
        nullOut = "/dev/null"
    pass1 = [args.ffmpeg_path]
    if not args.verbose:
        pass1 += ["-loglevel", "error"]
    pass1 += [
        prefix,
        "-pass",
        "1",
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass1 += ["-c:a", "aac", "-b:a", "256k"]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass1 += [mix4to3]
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass1 += [mix4to2]
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass1 += [mix2to1]
    pass1 += ["-f", "mp4", nullOut]
    pass2 = [args.ffmpeg_path]
    if not args.verbose:
        pass2 += ["-loglevel", "error"]
    pass2 += [
        prefix,
        "-pass",
        "2",
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass2 += ["-c:a", "aac", "-b:a", "256k"]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass2 += [mix4to3]
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass2 += [mix4to2]
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass2 += [mix2to1]
    pass2 += [accfile]
    subprocess.run(pass1)
    subprocess.run(pass2)


def output_dir():
    if args.output_path:
        if os.path.isdir(args.output_path):
            pass
        else:
            print(
                "The output location provided is not a directory. Using the input directory"
            )
            output_path = args.input_path
    else:
        print("Using input directory as the output location")
        output_path = args.input_path
    return output_path


def runBatch(input_path, output_path):
    for dirname in os.listdir(input_path):
        if os.path.isdir(dirname):
            runSingle(dirname, output_path)
        else:
            pass


def runSingle(input_path, output_path):
    for filename in input_path:
        if filename.endswith(filetypes):
            if not args.transcodeaccess:
                pass
            else:
                if not filename.endswith(".mkv"):
                    raise Exception(
                        "This is not a preservation file, will not transcode."
                    )
                else:
                    accessfile = transcodeaccess(
                        audioStreamCounter, filename, accessfile
                    )
                    md5generationmain.md5generationCall(accessfile)
            md5generationmain.md5generationCall(filename)
            spectrogramgenerationmain.generatespectrogramsCall(
                filename, output_path, args.ffprobe_path
            )
        else:
            pass


def main():
    input_path = args.input_dir
    checkfolder(input_path)
    output_path = output_dir()

    if args.batch:
        runBatch(input_path, output_path)
    else:
        runSingle(input_path, output_path)
