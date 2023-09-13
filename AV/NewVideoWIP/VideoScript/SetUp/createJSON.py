import json


def create_json(
    jsonAbsPath,
    systemInfo,
    input_metadata,
    mkvHash,
    mkv_stream_sum,
    baseFilename,
    output_metadata,
    item_csvDict,
    qcResults,
):
    input_techMetaV = input_metadata.get("techMetaV")
    input_techMetaA = input_metadata.get("techMetaA")
    output_techMetaV = output_metadata.get("techMetaV")
    output_techMetaA = output_metadata.get("techMetaA")
    output_file_metadata = output_metadata.get("file metadata")

    # create dictionary for json output
    data = {}
    data[baseFilename] = []

    # gather pre and post transcode file metadata for json output
    ffv1_file_meta = {}
    # add stream checksums to metadata
    ffv1_md5_dict = {"md5 checksum": mkvHash, "a/v streamMD5s": mkv_stream_sum}
    output_file_metadata = {**output_file_metadata, **ffv1_md5_dict}
    ffv1_file_meta = {"post-transcode metadata": output_file_metadata}

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
    data[baseFilename].append(techdata)
    data[baseFilename].append(qcResults)
    with open(jsonAbsPath, "w", newline="\n") as outfile:
        json.dump(data, outfile, indent=4)
