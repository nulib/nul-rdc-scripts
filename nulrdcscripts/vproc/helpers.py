#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import csv
import datetime
import time
import nulrdcscripts.vproc.equipment_dict as equipment_dict
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


def checksum_streams(input, audioStreamCounter):
    """
    Gets the stream md5 of a file
    Uses both video and all audio streams if audio is present
    """
    stream_sum = []
    stream_sum_command = [
        args.ffmpeg_path,
        "-loglevel",
        "error",
        "-i",
        input,
        "-map",
        "0:v",
        "-an",
    ]

    stream_sum_command.extend(("-f", "md5", "-"))
    video_stream_sum = (
        subprocess.check_output(stream_sum_command).decode("ascii").rstrip()
    )
    stream_sum.append(video_stream_sum.replace("MD5=", ""))
    for i in range(audioStreamCounter):
        audio_sum_command = [args.ffmpeg_path]
        audio_sum_command += ["-loglevel", "error", "-y", "-i", input]
        audio_sum_command += ["-vn", "-map", "0:a:%(a)s" % {"a": i}]
        audio_sum_command += ["-c:a", "pcm_s24le", "-f", "md5", "-"]
        audio_stream_sum = (
            subprocess.check_output(audio_sum_command).decode("ascii").rstrip()
        )
        stream_sum.append(audio_stream_sum.replace("MD5=", ""))
    return stream_sum


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


def two_pass_h264_encoding(audioStreamCounter, preservationAbsPath, accessAbsPath):
    if os.name == "nt":
        nullOut = "NUL"
    else:
        nullOut = "/dev/null"
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

    # sometimes these files are created I'm not sure why
    current_dir = os.getcwd()
    if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log")):
        os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log"))
    if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree")):
        os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree"))


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


def mediaconch_policy_check(input, policy):
    mediaconchResults = (
        subprocess.check_output([args.mediaconch_path, "--policy=" + policy, input])
        .decode("ascii")
        .rstrip()
        .split()[0]
    )
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults


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


def generate_coding_history(coding_history, hardware, append_list):
    """
    Formats hardware into BWF style coding history. Takes a piece of hardware (formatted: 'model; serial No.'), splits it at ';' and then searches the equipment dictionary for that piece of hardware. Then iterates through a list of other fields to append in the free text section. If the hardware is not found in the equipment dictionary this will just pull the info from the csv file and leave out some of the BWF formatting.
    """
    equipmentDict = equipment_dict.equipment_dict()
    if hardware.split(";")[0] in equipmentDict.keys():
        hardware_history = (
            equipmentDict[hardware.split(";")[0]]["coding algorithm"]
            + ","
            + "T="
            + hardware
        )
        for i in append_list:
            if i:
                hardware_history += "; "
                hardware_history += i
        if "hardware type" in equipmentDict.get(hardware.split(";")[0]):
            hardware_history += "; "
            hardware_history += equipmentDict[hardware.split(";")[0]]["hardware Type"]
        coding_history.append(hardware_history)
    # handle case where equipment is not in the equipmentDict using a more general format
    elif hardware and not hardware.split(";")[0] in equipmentDict.keys():
        hardware_history = hardware
        for i in append_list:
            if i:
                hardware_history += "; "
                hardware_history += i
        coding_history.append(hardware_history)
    else:
        pass
    return coding_history


def import_csv(csvInventory):
    csvDict = {}
    try:
        with open(csvInventory, encoding="utf-8") as f:
            # skip through annoying lines at beginning
            while True:
                # save spot
                stream_index = f.tell()
                # skip advancing line by line
                line = f.readline()
                if not (
                    "Name of Person Inventorying" in line
                    or "MEADOW Ingest fields" in line
                ):
                    # go back one line and break out of loop once fieldnames are found
                    f.seek(stream_index, os.SEEK_SET)
                    break
            reader = csv.DictReader(f, delimiter=",")
            # fieldnames to check for
            # some items have multiple options
            # 0 index is our current standard
            video_fieldnames_list = [
                ["filename"],
                ["work_accession_number"],
                ["box/folder alma number", "Box/Folder\nAlma number"],
                ["barcode"],
                ["description", "inventory_title"],
                ["record date/time"],
                ["housing/container markings"],
                ["condition notes"],
                ["call number"],
                ["format"],
                ["capture date"],
                ["staff initials", "Digitizer"],
                ["VTR used"],
                ["VTR output used"],
                ["tape brand"],
                ["tape record mode"],
                ["TBC used"],
                ["TBC output used"],
                ["ADC"],
                ["capture card"],
                ["sound"],
                ["video standard", "Region"],
                ["capture notes"],
            ]
            # dictionary of fieldnames found in the inventory file,
            # keyed by our current standard fieldnames
            # ex. for up to date inventory
            # "video standard": "video standard"
            # ex. if old inventory was used
            # "video standard": "Region"
            # this way old inventories work
            fieldnames = {}
            missing_fieldnames = []

            # loops through each field and checks for each option
            for field in video_fieldnames_list:
                for field_option in field:
                    for reader_field in reader.fieldnames:
                        if field_option.lower() in reader_field.lower():
                            # adds the fieldname used in the file
                            # to a dictionary for us to use
                            # the key is our current standard
                            fieldnames.update({field[0]: reader_field})
                            break
                # keep track of any missing
                # uses field[0] so when it tells user which ones are missin
                # they will use our current standard
                if not field[0] in fieldnames:
                    missing_fieldnames.append(field[0])

            if not missing_fieldnames:
                for row in reader:
                    # index field using dictionary of found fieldnames
                    name = row[fieldnames["filename"]]
                    id1 = row[fieldnames["work_accession_number"]]
                    id2 = row[fieldnames["box/folder alma number"]]
                    id3 = row[fieldnames["barcode"]]
                    description = row[fieldnames["description"]]
                    record_date = row[fieldnames["record date/time"]]
                    container_markings = row[fieldnames["housing/container markings"]]
                    if container_markings:
                        container_markings = container_markings.split("\n")
                    condition_notes = row[fieldnames["condition notes"]]
                    format = row[fieldnames["format"]]
                    captureDate = row[fieldnames["capture date"]]
                    # try to format date as yyyy-mm-dd if not formatted correctly
                    try:
                        captureDate = str(guess_date(captureDate))
                    except:
                        captureDate = None
                    staff_initials = row[fieldnames["staff initials"]]
                    vtr = row[fieldnames["VTR used"]]
                    vtrOut = row[fieldnames["VTR output used"]]
                    tapeBrand = row[fieldnames["tape brand"]]
                    recordMode = row[fieldnames["tape record mode"]]
                    tbc = row[fieldnames["TBC used"]]
                    tbcOut = row[fieldnames["TBC output used"]]
                    adc = row[fieldnames["ADC"]]
                    dio = row[fieldnames["capture card"]]
                    sound = row[fieldnames["sound"]]
                    sound = sound.split("\n")
                    videoStandard = row[fieldnames["video standard"]]
                    capture_notes = row[fieldnames["capture notes"]]
                    coding_history = []
                    coding_history = generate_coding_history(
                        coding_history,
                        vtr,
                        [tapeBrand, recordMode, videoStandard, vtrOut],
                    )
                    coding_history = generate_coding_history(
                        coding_history, tbc, [tbcOut]
                    )
                    coding_history = generate_coding_history(
                        coding_history, adc, [None]
                    )
                    coding_history = generate_coding_history(
                        coding_history, dio, [None]
                    )
                    csvData = {
                        "accession number/call number": id1,
                        "box/folder alma number": id2,
                        "barcode": id3,
                        "description": description,
                        "record date": record_date,
                        "housing/container markings": container_markings,
                        "condition notes": condition_notes,
                        "format": format,
                        "staff initials": staff_initials,
                        "capture date": captureDate,
                        "coding history": coding_history,
                        "sound note": sound,
                        "capture notes": capture_notes,
                    }
                    csvDict.update({name: csvData})
            elif not "File name" in missing_fieldnames:
                print("WARNING: Unable to find all column names in csv file")
                print("File name column found. Interpreting csv file as file list")
                print("CONTINUE? (y/n)")
                yes = {"yes", "y", "ye", ""}
                no = {"no", "n"}
                choice = input().lower()
                if choice in yes:
                    for row in reader:
                        name = row["File name"]
                        csvData = {}
                        csvDict.update({name: csvData})
                elif choice in no:
                    quit()
                else:
                    sys.stdout.write("Please respond with 'yes' or 'no'")
                    quit()
            else:
                print("No matching column names found in csv file")
            # print(csvDict)
    except FileNotFoundError:
        print("Issue importing csv file")
    return csvDict


def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime


def write_output_csv(outdir, csvHeaderList, csvWriteList, output_metadata, qcResults):
    csv_file = os.path.join(outdir, "qc_log.csv")
    csvOutFileExists = os.path.isfile(csv_file)

    with open(csv_file, "a") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        if not csvOutFileExists:
            writer.writerow(csvHeaderList)
        writer.writerow(csvWriteList)


def create_json(
    jsonAbsPath,
    systemInfo,
    preservation_metadata,
    preservation_stream_sum,
    mkvHash,
    access_stream_sum,
    baseFilename,
    access_metadata,
    item_csvDict,
    qcResults,
):
    preservation_techMetaV = preservation_metadata.get("techMetaV")
    preservation_techMetaA = preservation_metadata.get("techMetaA")
    preservation_file_metadata = preservation_metadata.get("file metadata")
    access_techMetaV = access_metadata.get("techMetaV")
    access_techMetaA = access_metadata.get("techMetaA")
    access_file_metadata = access_metadata.get("file metadata")

    # create dictionary for json output
    data = {}
    data[baseFilename] = []

    # gather pre and post transcode file metadata for json output
    preservation_file_meta = {}
    access_file_meta = {}
    # add stream checksums to metadata
    preservation_md5_dict = {
        "md5 checksum": mkvHash,
        "a/v streamMD5s": preservation_stream_sum,
    }
    access_md5_dict = {"md5 checksum": mkvHash, "a/v streamMD5s": access_stream_sum}
    preservation_file_metadata = {**preservation_file_metadata, **preservation_md5_dict}
    access_file_metadata = {**access_file_metadata, **access_md5_dict}
    access_file_meta = {"access metadata": access_file_metadata}
    preservation_file_meta = {"preservation metadata": preservation_file_metadata}

    # gather technical metadata for json output
    techdata = {}
    preservation_video_techdata = {}
    preservation_audio_techdata = {}
    access_video_techdata = {}
    access_audio_techdata = {}
    techdata["technical metadata"] = []
    preservation_video_techdata = {"video": preservation_techMetaV}
    preservation_audio_techdata = {"audio": preservation_techMetaA}
    access_video_techdata = {"video": access_techMetaV}
    access_audio_techdata = {"audio": access_techMetaA}
    techdata["technical metadata"].append(preservation_video_techdata)
    techdata["technical metadata"].append(preservation_audio_techdata)
    techdata["technical metadata"].append(access_video_techdata)
    techdata["technical metadata"].append(access_audio_techdata)

    # gather metadata from csv dictionary as capture metadata
    csv_metadata = {"inventory metadata": item_csvDict}

    system_info = {"system information": systemInfo}

    data[baseFilename].append(csv_metadata)
    data[baseFilename].append(system_info)
    data[baseFilename].append(access_file_meta)
    data[baseFilename].append(preservation_file_meta)
    data[baseFilename].append(techdata)
    data[baseFilename].append(qcResults)
    with open(jsonAbsPath, "w", newline="\n") as outfile:
        json.dump(data, outfile, indent=4)
