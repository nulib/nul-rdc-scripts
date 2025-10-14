#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import csv
import datetime
import time
from nulrdcscripts.vproc.params import args


def create_transcode_output_folders(baseOutput, outputFolderList):
    if not os.path.isdir(baseOutput):
        try:
            os.mkdir(baseOutput)
        except:
            print("unable to create output folder:", baseOutput)
            quit()
    else:
        print(baseOutput, "already exists")
        print("Proceeding")

    for folder in outputFolderList:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except:
                print("unable to create output folder:", folder)
                quit()
        else:
            print("using existing folder", folder, "as output")


def check_mixdown_arg():
    mixdown_list = ["copy", "4to3", "4to2", "2to1"]
    # TO DO add swap as an option to allow switching tracks 3&4 with tracks 1&2
    if not args.mixdown in mixdown_list:
        print("The selected audio mixdown is not a valid value")
        print("please use one of: copy, 4to3, 4to2, 2to1")
        quit()


def ffprobe_report(filename, input_file_abspath):
    """
    returns nested dictionary with ffprobe metadata
    """
    video_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "v",
                "-show_entries",
                "stream=codec_name,avg_frame_rate,codec_time_base,width,height,pix_fmt,sample_aspect_ratio,display_aspect_ratio,color_range,color_space,color_transfer,color_primaries,chroma_location,field_order,codec_tag_string",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    audio_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=codec_long_name,bits_per_raw_sample,sample_rate,channels",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    format_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-show_entries",
                "format=duration,size,nb_streams",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    data_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "d",
                "-show_entries",
                "stream=codec_tag_string",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    attachment_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "t",
                "-show_entries",
                "stream_tags=filename",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )

    # cleaning up attachment output
    tags = [streams.get("tags") for streams in (attachment_output["streams"])]
    attachment_list = []
    for i in tags:
        attachmentFilename = [i.get("filename")]
        attachment_list.extend(attachmentFilename)

    # parse ffprobe metadata lists
    video_codec_name_list = [
        stream.get("codec_name") for stream in (video_output["streams"])
    ]
    audio_codec_name_list = [
        stream.get("codec_long_name") for stream in (audio_output["streams"])
    ]
    data_streams = [
        stream.get("codec_tag_string") for stream in (data_output["streams"])
    ]
    width = [stream.get("width") for stream in (video_output["streams"])][0]
    height = [stream.get("height") for stream in (video_output["streams"])][0]
    pixel_format = [stream.get("pix_fmt") for stream in (video_output["streams"])][0]
    sar = [stream.get("sample_aspect_ratio") for stream in (video_output["streams"])][0]
    dar = [stream.get("display_aspect_ratio") for stream in (video_output["streams"])][
        0
    ]
    framerate = [stream.get("avg_frame_rate") for stream in (video_output["streams"])][
        0
    ]
    color_space = [stream.get("color_space") for stream in (video_output["streams"])][0]
    color_range = [stream.get("color_range") for stream in (video_output["streams"])][0]
    color_transfer = [
        stream.get("color_transfer") for stream in (video_output["streams"])
    ][0]
    color_primaries = [
        stream.get("color_primaries") for stream in (video_output["streams"])
    ][0]
    audio_bitrate = [
        stream.get("bits_per_raw_sample") for stream in (audio_output["streams"])
    ]
    audio_sample_rate = [
        stream.get("sample_rate") for stream in (audio_output["streams"])
    ]
    audio_channels = [stream.get("channels") for stream in (audio_output["streams"])]
    audio_stream_count = len(audio_codec_name_list)

    file_metadata = {
        "filename": filename,
        "file size": format_output.get("format")["size"],
        "duration": format_output.get("format")["duration"],
        "streams": format_output.get("format")["nb_streams"],
        "video streams": video_codec_name_list,
        "audio streams": audio_codec_name_list,
        "data streams": data_streams,
        "attachments": attachment_list,
    }

    techMetaV = {
        "width": width,
        "height": height,
        "sample aspect ratio": sar,
        "display aspect ratio": dar,
        "pixel format": pixel_format,
        "framerate": framerate,
        "color space": color_space,
        "color range": color_range,
        "color primaries": color_primaries,
        "color transfer": color_transfer,
    }

    techMetaA = {
        "audio stream count": audio_stream_count,
        "audio bitrate": audio_bitrate,
        "audio sample rate": audio_sample_rate,
        "channels": audio_channels,
    }

    ffprobe_metadata = {
        "file metadata": file_metadata,
        "techMetaV": techMetaV,
        "techMetaA": techMetaA,
    }

    return ffprobe_metadata


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


fourtoThree = [
    "-filter_complex",
    "[0:a:0][0:a:1]amerge=inputs2[a]",
    "-map",
    "0:v",
    "-map",
    "[a]",
    "-map",
    "0:a:2",
    "-map",
    "0:a:3",
]

fourtoTwo = [
    "-filter_complex",
    "[0:a:0][0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]",
    "-map",
    "0:v",
    "-map",
    "[a]",
    "-map",
    "[b]",
]

twotoOne = [
    "-filter_complex",
    "[0:a:0][0:a:1]amerge=inputs=2[a]",
    "-map",
    "0:v",
    "-map",
    "[a]",
]


def two_pass_h264_encoding(audioStreamCounter, preservationAbsPath, accessAbsPath, logfile=None):
    if os.name == "nt":
        nullOut = "NUL"
    else:
        nullOut = "/dev/null"
    if logfile is None:
        logfile = "ffmpeg2pass-0.log"  # fallback, but should always pass a unique one!

    pass1 = [args.ffmpeg_path]
    if not args.verbose:
        pass1 += ["-loglevel", "error"]
    pass1 += [
        "-y",
        "-i",
        preservationAbsPath,
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
        "-passlogfile",
        logfile,
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass1 += ["-c:a", "aac", "-b:a", "256k"]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass1 += fourtoThree
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass1 += fourtoTwo
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass1 += twotoOne
    pass1 += ["-f", "mp4", nullOut]

    pass2 = [args.ffmpeg_path]
    if not args.verbose:
        pass2 += ["-loglevel", "error"]
    pass2 += [
        "-y",
        "-i",
        preservationAbsPath,
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
        "-passlogfile",
        logfile,
    ]
    if audioStreamCounter > 0:
        if args.mixdown == "copy":
            pass2 += ["-c:a", "aac", "-b:a", "256k"]
        if args.mixdown == "4to3" and audioStreamCounter == 4:
            pass2 += fourtoThree
        if args.mixdown == "4to2" and audioStreamCounter == 4:
            pass2 += fourtoTwo
        if args.mixdown == "2to1" and audioStreamCounter == 2:
            pass2 += twotoOne
    pass2 += [accessAbsPath]
    subprocess.run(pass1)
    subprocess.run(pass2)

    # Clean up unique log files
    for ext in ["", ".mbtree"]:
        log_path = logfile + ext
        if os.path.isfile(log_path):
            os.remove(log_path)


def generate_spectrogram(input, channel_layout_list, outputFolder, outputName):
    """
    Creates a spectrogram for each audio track in the input
    """
    spectrogram_resolution = "1920x1080"
    for index, item in enumerate(channel_layout_list):
        output = os.path.join(
            outputFolder, outputName + "_spectrogram0" + str(index) + "_s.png"
        )
        spectrogram_args = [args.ffmpeg_path]
        spectrogram_args += ["-loglevel", "error", "-y"]
        spectrogram_args += ["-i", input, "-lavfi"]
        if item > 1:
            spectrogram_args += [
                "[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        else:
            spectrogram_args += [
                "[0:a:%(a)s]showspectrumpic=s=%(b)s"
                % {"a": index, "b": spectrogram_resolution}
            ]
        spectrogram_args += [output]
        subprocess.run(spectrogram_args)


def generate_qctools(input):
    """
    uses qcli to generate a QCTools report
    """
    qctools_args = [args.qcli_path, "-i", input]
    subprocess.run(qctools_args)


def mediaconch_policy_check(input, policy, debug=False):
    result = subprocess.check_output([args.mediaconch_path, "--policy=" + policy, input]).decode("ascii").rstrip()
    if debug:
        return result  # Return the full output for debugging
    # Default: just PASS/FAIL
    first_word = result.split()[0] if result else ""
    if first_word == "pass!":
        return "PASS"
    else:
        return f"FAIL: {result}"


def mediaconch_implementation_check(input):
    mediaconchResults = (
        subprocess.check_output([args.mediaconch_path, input])
        .decode("ascii")
        .rstrip()
        .split()[0]
    )
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults


def generate_system_log(ffvers, tstime, tftime):
    # gather system info for json output
    osinfo = platform.platform()
    systemInfo = {
        "operating system": osinfo,
        "ffmpeg version": ffvers,
        "transcode start time": tstime,
        "transcode end time": tftime,
        # TO DO: add capture software/version maybe -- would have to pull from csv
    }
    return systemInfo


def qc_results(inventoryCheck, mediaconchResults):
    QC_results = {}
    QC_results["QC"] = {
        "inventory check": inventoryCheck,
        "mediaconch results": mediaconchResults,
    }
    return QC_results


def guess_date(string):
    for fmt in ["%m/%d/%Y", "%d-%m-%Y", "%m/%d/%y", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)


def generate_coding_history(csvDict, baseFilename):
    encoding_chain = {}
    file_path = os.path.join(os.path.dirname(__file__), "deckconfig.json")
    try:
        # Read JSON data from the file
        with open(file_path, "r") as file:
            data = json.load(file)
        encoding_chain = csvDict.get(baseFilename)
        vTR = encoding_chain.get("vtr")
        # Access nested elements
        # VTR Data
        vtr_name = data[vTR]["VTR"]["vtr_name"]
        vtr_nutag = data[vTR]["VTR"]["vtr_nuTag"]
        vtr_out = data[vTR]["VTR"]["vtr_out"]

        # TBC Data
        tbc_name = data[vTR]["TBC"]["tbc_name"]
        tbc_nutag = data[vTR]["TBC"]["tbc_nuTag"]
        tbc_out = data[vTR]["TBC"]["tbc_out"]

        # A/D Converter Data
        ad_name = data[vTR]["A/D Converter"]["ad_name"]
        ad_nutag = data[vTR]["A/D Converter"]["ad_nuTag"]
        ad_out = data[vTR]["A/D Converter"]["ad_out"]

        # Capture Card Data
        capturecard_name = data[vTR]["Capture Card"]["capturecard_name"]
        capturecard_nutag = data[vTR]["Capture Card"]["capturecard_nuTag"]
        capturecard_out = data[vTR]["Capture Card"]["capturecard_out"]

        encoding_chain = {
            "vtr": {
                "vtr name": vtr_name,
                "vtr nu tag": vtr_nutag,
                "vtr output": vtr_out,
            },
            "tbc": {
                "tbc name": tbc_name,
                "tbc nu tag": tbc_nutag,
                "tbc output": tbc_out,
            },
            "ad": {
                "ad name": ad_name,
                "ad nu tag": ad_nutag,
                "ad output": ad_out,
            },
            "capturecard": {
                "cc name": capturecard_name,
                "cc nu tag": capturecard_nutag,
                "cc output": capturecard_out,
            },
        }
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return encoding_chain


def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime
