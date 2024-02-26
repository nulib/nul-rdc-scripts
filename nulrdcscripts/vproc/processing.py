import os
import subprocess
from nulrdcscripts.vproc.params import args


def ffv1_lossless_transcode(input_metadata, transcode_nameDict, audioStreamCounter):
    # get relevant names from nameDict
    inputAbsPath = transcode_nameDict.get("inputAbsPath")
    tempMasterFile = transcode_nameDict.get("tempMasterFile")
    framemd5AbsPath = transcode_nameDict.get("framemd5AbsPath")
    outputAbsPath = transcode_nameDict.get("outputAbsPath")
    framemd5File = transcode_nameDict.get("framemd5File")

    # create ffmpeg command
    ffmpeg_command = [args.ffmpeg_path]
    if not args.verbose:
        ffmpeg_command.extend(("-loglevel", "error"))
    ffmpeg_command.extend(
        [
            "-i",
            inputAbsPath,
            "-map",
            "0",
            "-dn",
            "-c:v",
            "ffv1",
            "-level",
            "3",
            "-g",
            "1",
            "-slices",
            str(args.ffv1_slice_count),
            "-slicecrc",
            "1",
        ]
    )
    # TO DO: consider putting color data in a list or dict to replace the following if statements with a single if statement in a for loop
    if input_metadata["techMetaV"]["color primaries"]:
        ffmpeg_command.extend(
            ("-color_primaries", input_metadata["techMetaV"]["color primaries"])
        )
    if input_metadata["techMetaV"]["color transfer"]:
        ffmpeg_command.extend(
            ("-color_trc", input_metadata["techMetaV"]["color transfer"])
        )
    if input_metadata["techMetaV"]["color space"]:
        ffmpeg_command.extend(
            ("-colorspace", input_metadata["techMetaV"]["color space"])
        )
    if audioStreamCounter > 0:
        ffmpeg_command.extend(("-c:a", "copy"))
    ffmpeg_command.extend(
        (
            tempMasterFile if args.embed_framemd5 else outputAbsPath,
            "-f",
            "framemd5",
            "-an",
            framemd5AbsPath,
        )
    )

    # execute ffmpeg command
    subprocess.run(ffmpeg_command)

    # remux to attach framemd5
    if args.embed_framemd5:
        add_attachment = [
            args.ffmpeg_path,
            "-loglevel",
            "error",
            "-i",
            tempMasterFile,
            "-c",
            "copy",
            "-map",
            "0",
            "-attach",
            framemd5AbsPath,
            "-metadata:s:t:0",
            "mimetype=application/octet-stream",
            "-metadata:s:t:0",
            "filename=" + framemd5File,
            outputAbsPath,
        ]
        if os.path.isfile(tempMasterFile):
            subprocess.call(add_attachment)
            filesToDelete = [tempMasterFile, framemd5AbsPath]
            delete_files(filesToDelete)
        else:
            print("There was an issue finding the file", tempMasterFile)


def two_pass_h264_encoding(audioStreamCounter, outputAbsPath, acAbsPath):
    command = (
        "-y",
        "-i",
        outputAbsPath,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        "8000k",
        "-pix_fmt",
        "yuv420p",
    )
    mixdowncopy = "-c:a", "aac", "-b:a", "256k"
    mixdown4to3 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-map",
        "[0:a:2]",
        "-map",
        "[0:a:3]",
    )
    mixdown4to2 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-map",
        "[b]",
    )
    mixdown2to1 = (
        "-filter_complex",
        "[0:a:0][0:a:1]amerge=inputs=2[a]",
        "-map",
        "[0:v]",
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
        command,
        "-pass",
        "1",
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass1 += [mixdowncopy]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass1 += [mixdown4to3]
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass1 += [mixdown4to2]
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass1 += [mixdown2to1]
    pass1 += ["-f", "mp4", nullOut]
    pass2 = [args.ffmpeg_path]
    if not args.verbose:
        pass2 += ["-loglevel", "error"]
    pass2 += [
        command,
        "-pass",
        "2",
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass2 += [mixdowncopy]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass2 += [mixdown4to3]
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass2 += [mixdown4to2]
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass2 += [mixdown2to1]
    pass2 += [acAbsPath]
    subprocess.run(pass1)
    subprocess.run(pass2)

    # sometimes these files are created I'm not sure why
    current_dir = os.getcwd()
    if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log")):
        os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log"))
    if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree")):
        os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree"))


def delete_files(list):
    """
    Loops through a list of files and tries to delete them
    """
    for i in list:
        try:
            os.remove(i)
        except FileNotFoundError:
            print("unable to delete " + i)
            print("File not found")
