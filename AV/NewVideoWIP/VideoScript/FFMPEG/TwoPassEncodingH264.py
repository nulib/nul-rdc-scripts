import os
import subprocess
from VideoScript.Arguments.Arguments import args
import VideoScript.FFProbe.parse_ffprobe_metadata_lists as ffprobemeta


mixDown4to3 = [
    "-filter_complex",
    "[0:a:0][0:a:1]amerge=inputs=2[a]" "-map",
    "0:v",
    "-map",
    "[a]",
    "-map",
    "0:a:2",
    "-map",
    "0:a:3",
]
mixdown2to1 = [
    "-filter_complex",
    "[0:a:0][0:a:1]amerge=inputs=2[a]",
    "-map",
    "0:v",
    "-map",
    "[a]",
]
mixDown4to2 = [
    "-filter_complex",
    """[0:a:0][0:a:1]amerge=inputs=2[a]; [0:a:2]
             [0:a:3]amerge=inputs=2[b]""",
    "-map",
    "0:v",
    "-map",
    "[a]",
    "-map",
    "[b]",
]


def two_pass_h264_encoding(audiostreamCounter, outputAbsPath, acAbsPath):
    if os.name == "nt":
        nullOut = "NUL"
    else:
        nullOut = "/dev/null"

    # Pass One

    pass1 = [args.ffmpeg_path]

    if not args.verbose:
        pass1 += ["-loglevel", "error"]

    pass1 += [
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
        "-pass",
        "1",
    ]

    if audiostreamCounter > 0:
        if args.mixdown == "copy":
            pass1 += ["-c:a", "aac", "-b:a", "128k"]
        if args.mixdown == "4to3" and audiostreamCounter == 4:
            pass1 += mixDown4to3
        if args.mixdown == "4to2" and audiostreamCounter == 4:
            pass1 += mixDown4to2

        if args.mixdown == "2to1" and audiostreamCounter == 2:
            pass1 += mixdown2to1

        pass1 += ["-f", "mp4", nullOut]

        # Pass Two

    pass2 = [args.ffmpeg_path]
    if not args.verbose:
        pass2 += ["-loglevel", "error"]
    pass2 += [
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
        "-pass",
        "2",
    ]

    if audiostreamCounter > 0:
        if args.mixdown == "copy":
            pass2 += ["-c:a", "aac", "-b:a", "128k"]
        if args.mixdown == "4to3" and audiostreamCounter == 4:
            pass2 += mixDown4to3
        if args.mixdown == "4to2" and audiostreamCounter == 4:
            pass2 += mixDown4to2
        if args.mixdown == "2to1" and audiostreamCounter == 2:
            pass2 += mixdown2to1
    pass2 += [acAbsPath]
    subprocess.run(pass1)
    subprocess.run(pass2)
