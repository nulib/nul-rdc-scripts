import json


def create_json(
    jsonAbsPath,
    systemInfo,
    preservation_metadata,
    baseFilename,
    access_metadata,
    item_csvDict,
    qcResults,
    encoding_chain,
):
    preservation_techMetaV = preservation_metadata.get("techMetaV")
    preservation_techMetaA = preservation_metadata.get("techMetaA")
    preservation_file_metadata = preservation_metadata.get("file metadata")
    access_techMetaV = access_metadata.get("techMetaV")
    access_techMetaA = access_metadata.get("techMetaA")
    access_file_metadata = access_metadata.get("file metadata")
    vtr_inform = encoding_chain.get("vtr")
    tbc_inform = encoding_chain.get("tbc")
    ad_inform = encoding_chain.get("ad")
    cc_inform = encoding_chain.get("capturecard")

    # create dictionary for json output
    data = {}
    data[baseFilename] = []

    # gather access and preservation file metadata for json output
    preservation_file_meta = {}
    access_file_meta = {}
    preservation_file_metadata = {**preservation_file_metadata}
    access_file_metadata = {**access_file_metadata}
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

    # gather encoding information
    encoding_history = {}
    vtr_info = {}
    tbc_info = {}
    ad_info = {}
    cc_info = {}
    encoding_history["encoding chain"] = []
    vtr_info = {"vtr": vtr_inform}
    tbc_info = {"tbc": tbc_inform}
    ad_info = {"a/d": ad_inform}
    cc_info = {"capture card": cc_inform}
    encoding_history["encoding chain"].append(vtr_info)
    encoding_history["encoding chain"].append(tbc_info)
    encoding_history["encoding chain"].append(ad_info)
    encoding_history["encoding chain"].append(cc_info)

    # gather metadata from csv dictionary as capture metadata
    csv_metadata = {"inventory metadata": item_csvDict}

    system_info = {"system information": systemInfo}

    data[baseFilename].append(csv_metadata)
    data[baseFilename].append(encoding_history)
    data[baseFilename].append(system_info)
    data[baseFilename].append(access_file_meta)
    data[baseFilename].append(preservation_file_meta)
    data[baseFilename].append(techdata)
    data[baseFilename].append(qcResults)
    with open(jsonAbsPath, "w", newline="\n") as outfile:
        json.dump(data, outfile, indent=4)
