import csv
import json
import os
import platform
import subprocess
from nulrdcscripts.vproc.params import args
from nulrdcscripts.vproc.equipment_dict import equipment_dict


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
    input_metadata,
    mov_stream_sum,
    mkvHash,
    mkv_stream_sum,
    baseFilename,
    output_metadata,
    item_csvDict,
    qcResults,
):
    input_techMetaV = input_metadata.get("techMetaV")
    input_techMetaA = input_metadata.get("techMetaA")
    input_file_metadata = input_metadata.get("file metadata")
    output_techMetaV = output_metadata.get("techMetaV")
    output_techMetaA = output_metadata.get("techMetaA")
    output_file_metadata = output_metadata.get("file metadata")

    # create dictionary for json output
    data = {}
    data[baseFilename] = []

    # gather pre and post transcode file metadata for json output
    mov_file_meta = {}
    ffv1_file_meta = {}
    # add stream checksums to metadata
    mov_md5_dict = {"a/v streamMD5s": mov_stream_sum}
    ffv1_md5_dict = {"md5 checksum": mkvHash, "a/v streamMD5s": mkv_stream_sum}
    input_file_metadata = {**input_file_metadata, **mov_md5_dict}
    output_file_metadata = {**output_file_metadata, **ffv1_md5_dict}
    ffv1_file_meta = {"post-transcode metadata": output_file_metadata}
    mov_file_meta = {"pre-transcode metadata": input_file_metadata}

    # gather technical metadata for json output
    techdata = {}
    video_techdata = {}
    audio_techdata = {}
    techdata["technical metadata"] = []
    video_techdata = {"video": input_techMetaV}
    audio_techdata = {"audio": input_techMetaA}
    techdata["technical metadata"].append(video_techdata)
    techdata["technical metadata"].append(audio_techdata)

    # gather metadata from csv dictionary as capture metadata
    csv_metadata = {"inventory metadata": item_csvDict}

    system_info = {"system information": systemInfo}

    data[baseFilename].append(csv_metadata)
    data[baseFilename].append(system_info)
    data[baseFilename].append(ffv1_file_meta)
    data[baseFilename].append(mov_file_meta)
    data[baseFilename].append(techdata)
    data[baseFilename].append(qcResults)
    with open(jsonAbsPath, "w", newline="\n") as outfile:
        json.dump(data, outfile, indent=4)
