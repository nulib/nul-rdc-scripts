import csv
import json
import os
import platform
import progressbar
import subprocess
from nulrdcscripts.vproc.params import args
"""Functions that generate the output files. i.e. spectrogram generation, QCTools report generation"""

def ffprobe_report(filename):
    """
    returns nested dictionary with ffprobe metadata
    """
    input_file_abspath = args.input_file_abspath
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

def generate_spectrogram(input, channel_layout_list, outputFolder, outputName):
    """
    Creates a spectrogram for each audio track in the input
    """
    with progressbar.ProgressBar(max_value=100) as spectroprog:
        for t in range(100):
            spectrogram_resolution = "1920x1080"
            for index, item in enumerate(channel_layout_list):
                output = os.path.join(
                    outputFolder, outputName + "_spectrogram0" + str(index) + "_s.png"
                )
                spectroprog.update(t)
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
                spectroprog.update(t)
                subprocess.run(spectrogram_args)

def generate_qctools(input):
    """
    uses qcli to generate a QCTools report
    """
    with progressbar.ProgressBar(max_value=100) as qctoolprog:
        for t in range(100):
            qctools_args = [args.qcli_path, "-i", input]
            qctoolprog.update(t)
            subprocess.run(qctools_args)


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
