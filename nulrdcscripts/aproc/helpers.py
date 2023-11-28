#!/usr/bin/env python3

import os
import sys
import re
import subprocess
import platform
import json
import csv
import datetime
import time
from nulrdcscripts.aproc.params import args


def get_immediate_subdirectories(folder):
    """
    get list of immediate subdirectories of input
    """
    return [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]


def create_output_folder(folder):
    if not os.path.isdir(folder):
        try:
            os.mkdir(folder)
        except:
            print("unable to create output folder:", folder)
            quit()
    else:
        print("using existing folder", folder, "as output")


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


def load_reference_inventory(reference_inventory_file):
    reference_inventory_fieldnames = []
    with open(reference_inventory_file, "r") as f:
        reader = csv.DictReader(f, delimiter=",")
        reference_inventory_fieldnames.extend(reader.fieldnames)
    return reference_inventory_fieldnames


def load_item_metadata(file, source_inventory_dict):
    # TODO error out if multiple matches are found
    loaded_metadata = {}
    for item in source_inventory_dict:
        if item in file:
            loaded_metadata = {item: source_inventory_dict[item]}
    if not loaded_metadata:
        print("ERROR: Unable to find matching file for " + file)
        quit()
    return loaded_metadata


def ffprobe_report(filename, input_file_abspath):
    """
    returns nested dictionary with ffprobe metadata  
    """
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

    audio_codec_name_list = [
        stream.get("codec_long_name") for stream in (audio_output["streams"])
    ][0]
    audio_bitrate = [
        stream.get("bits_per_raw_sample") for stream in (audio_output["streams"])
    ][0]
    audio_sample_rate = [
        stream.get("sample_rate") for stream in (audio_output["streams"])
    ][0]
    audio_channels = [stream.get("channels") for stream in (audio_output["streams"])][0]

    file_metadata = {
        #'filename' : filename,
        "file size": format_output.get("format")["size"],
        "duration": format_output.get("format")["duration"],
        "streams": format_output.get("format")["nb_streams"],
        "channels": audio_channels,
        "audio streams": audio_codec_name_list,
        "audio sample rate": audio_sample_rate,
        "audio bitrate": audio_bitrate,
    }

    ffprobe_metadata = {"file metadata": file_metadata}

    return ffprobe_metadata


def generate_spectrogram(input, channel_layout, outputFolder, outputName):
    """
    Creates a spectrogram for each audio track in the input
    """
    spectrogram_resolution = "1928x1080"
    output = os.path.join(outputFolder, outputName + "_0a0" + "-spectrogram" + ".png")
    spectrogram_args = [args.ffmpeg_path]
    spectrogram_args += ["-loglevel", "error", "-y"]
    spectrogram_args += ["-i", input, "-lavfi"]
    if channel_layout > 1:
        spectrogram_args += [
            "[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s"
            % {"a": "0", "b": spectrogram_resolution}
        ]
    else:
        spectrogram_args += [
            "[0:a:%(a)s]showspectrumpic=s=%(b)s"
            % {"a": "0", "b": spectrogram_resolution}
        ]
    spectrogram_args += [output]
    subprocess.run(spectrogram_args)


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


def generate_system_log():
    # gather system info for json output
    osinfo = platform.platform()
    systemInfo = {
        "operating system": osinfo,
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


def verify_csv_exists(csv_file):
    """
    TODO add doctest
    """
    if csv_file.endswith(".csv"):
        if not os.path.isfile(csv_file):
            print("ERROR: Unable to locate " + csv_file)
            quit()
    else:
        print("ERROR: " + csv_file + " is not a CSV file")
        quit()


def group_lists(original_list):
    """
    groups list items by the number found in them
    """
    grouped_lists = []
    for value in original_list:
        numeric_string = "".join(filter(str.isdigit, value))
        if (
            grouped_lists
            and "".join(filter(str.isdigit, grouped_lists[-1][0])) == numeric_string
        ):
            grouped_lists[-1].append(value)
        else:
            grouped_lists.append([value])
    return grouped_lists


def create_coding_history(row, encoding_chain_fields, append_list):
    # separates out just the number from the encoding chain field
    # then compares that to the previous entry in the list so that same numbers are grouped
    grouped_field_list = group_lists(encoding_chain_fields)
    coding_history_dict = {}
    coding_history = []

    # when the inventory has columns for encoding chain but nothing is entered
    # like for vendor projects
    # this functions throws a bunch of errors
    # I just wrapped it in a try/except and return None if anything goes wrong
    # this way it will just give up if it doesn't find the info
    try:
        for encoding_chain in grouped_field_list:
            coding_history_dict = {
                "primary fields": {
                    "coding algorithm": None,
                    "sample rate": None,
                    "word length": None,
                    "sound mode": None,
                },
                "freetext": {
                    "device": None,
                    "id": None,
                    "append fields": None,
                    "ad type": None,
                },
            }
            for i in encoding_chain:
                if i.lower().endswith("hardware"):
                    hardware_parser = row[i].split(";")
                    hardware_parser = [i.lstrip() for i in hardware_parser]
                    if len(hardware_parser) != 3:
                        print(
                            "ERROR: Encoding chain hardware does not follow expected formatting"
                        )
                    coding_history_dict["primary fields"]["coding algorithm"] = (
                        "A=" + hardware_parser[0]
                    )
                    # TODO change how T= is added so it is instead just placed before the first entry of the freetext section
                    coding_history_dict["freetext"]["device"] = "T=" + hardware_parser[1]
                    coding_history_dict["freetext"]["id"] = hardware_parser[2]
                if i.lower().endswith("mode"):
                    coding_history_dict["primary fields"]["sound mode"] = "M=" + row[i]
                if i.lower().endswith("digital characteristics"):
                    hardware_parser = row[i].split(";")
                    hardware_parser = [i.lstrip() for i in hardware_parser]
                    if len(hardware_parser) != 2:
                        print(
                            "ERROR: Encoding chain digital characteristics does not follow expected formatting"
                        )
                    coding_history_dict["primary fields"]["sample rate"] = (
                        "F=" + hardware_parser[0]
                    )
                    coding_history_dict["primary fields"]["word length"] = (
                        "W=" + hardware_parser[1]
                    )
                if (
                    i.lower().endswith("hardware type")
                    and row[i].lower() == "playback deck"
                ):
                    clean_list = []
                    for field in append_list:
                        if field:
                            clean_list.append(field)
                    if clean_list:
                        append_fields = "; ".join(clean_list)
                    # convert append list to string
                    coding_history_dict["freetext"]["append fields"] = append_fields
                elif i.lower().endswith("hardware type"):
                    coding_history_dict["freetext"]["ad type"] = row[i]
            primary_fields = []
            freetext = []
            for key in coding_history_dict["primary fields"]:
                if coding_history_dict["primary fields"][key]:
                    primary_fields.append(coding_history_dict["primary fields"][key])
            for key in coding_history_dict["freetext"]:
                if coding_history_dict["freetext"][key]:
                    freetext.append(coding_history_dict["freetext"][key])
            if primary_fields and freetext:
                coding_history_p = ",".join(primary_fields)
                coding_history_t = "; ".join(freetext)
                coding_history_component = coding_history_p + "," + coding_history_t
                coding_history.append(coding_history_component)
        coding_history = "\r\n".join(coding_history)
        return coding_history
    except:
        return None


def import_inventories(source_inventories, skip_coding_history):
    csvDict = {}
    for i in source_inventories:
        verify_csv_exists(i)
        with open(i, encoding="utf-8") as f:
            while True:
                # save spot
                stream_index = f.tell()
                # skip advancing line by line
                line = f.readline()
                if not ("Name of Person Inventorying" in line or "MEADOW Ingest fields" in line):
                    # go back one line and break out of loop once fieldnames are found
                    f.seek(stream_index, os.SEEK_SET)
                    break
            reader = csv.DictReader(f, delimiter=",")
            # fieldnames to check for
            # some items have multiple options
            # leftmost item (0 index) is our current standard
            video_fieldnames_list = [
                ["work_accession_number"],
                ["filename"],
                ["label"],
                ["inventory_title"],
                ["record date/time"],
                ["housing/container markings"],
                ["condition notes"],
                ["barcode"],
                ["call number"],
                ["box/folder alma number", "Box/Folder\nAlma number"],
                ["format"],
                ["running time (mins)"],
                ["tape brand"],
                ["speed IPS"],
                ["tape thickness"],
                ["base (acetate/polyester)"],
                ["track configuration"],
                ["length/reel size"],
                ["sound"],
                ["tape type (cassette)"],
                ["noise reduction"],
                ["capture date"],
                ["digitizer", "staff initials"],
                ["digitizer notes", "capture notes"],
            ]
            # dictionary of fieldnames found in the inventory file,
            # keyed by our current standard fieldnames
            # ex. for up to date inventory
            # "digitizer notes": "digitizer notes"
            # ex. if old inventory was used
            # "digitizer notes": "capture notes"
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
            if missing_fieldnames:
                print("ERROR: inventory  missing the following columns")
                print(missing_fieldnames)
                quit()

            encoding_chain_fields = sorted(
                [a for a in reader.fieldnames if "encoding chain" in a.lower()]
            )
            if not encoding_chain_fields:
                print("WARNING: Unable to find encoding chain fields in inventory")
                print("Continue without building Coding History? (y/n)")
                yes = {"yes", "y", "ye", ""}
                no = {"no", "n"}
                choice = input().lower()
                if choice in yes:
                    skip_coding_history = True
                elif choice in no:
                    quit()
                else:
                    sys.stdout.write("Please respond with 'yes' or 'no'")
                    quit()
            for row in reader:
                # index row based on fieldnames found in file
                name = row[fieldnames["filename"]]
                record_date = row[fieldnames["record date/time"]]
                container_markings = row[fieldnames["housing/container markings"]]
                container_markings = container_markings.split("\n")
                format = row[fieldnames["format"]].lower()
                captureDate = row[fieldnames["capture date"]]
                # try to format date as yyyy-mm-dd if not formatted correctly
                if captureDate:
                    captureDate = str(guess_date(captureDate))
                tapeBrand = row[fieldnames["tape brand"]]
                sound = row[fieldnames["sound"]]
                type = row[fieldnames["tape type (cassette)"]]
                nr = row[fieldnames["noise reduction"]]
                speed = row[fieldnames["speed IPS"]]
                if not skip_coding_history:
                    coding_history = create_coding_history(
                        row, encoding_chain_fields, [tapeBrand, type, speed, nr]
                    )
                    if not coding_history:
                        print("WARNING: coding history was unable to be created")
                else:
                    coding_history = None
                # TODO make a more generic expandable coding history builder
                # TODO separate out metadata that is specifically needed for embedding vs json file metadata
                csvData = {
                    "Inventory Metadata": {
                        "work_accession_number": row[fieldnames["work_accession_number"]],
                        "box/folder alma number": row[fieldnames["box/folder alma number"]],
                        "barcode": row[fieldnames["barcode"]],
                        "inventory title": row[fieldnames["inventory_title"]],
                        "record date": record_date,
                        "container markings": container_markings,
                        "condition notes": row[fieldnames["condition notes"]],
                        "digitization operator": row[fieldnames["digitizer"]],
                        "capture date": captureDate,
                        "sound note": sound,
                        "capture notes": row[fieldnames["digitizer notes"]],
                    },
                    "BWF Metadata": {
                        "format": format,
                        "coding history": coding_history,
                    },
                }
                csvDict.update({name: csvData})
    return csvDict


def get_bwf_metadata(pm_file_abspath):
    # TODO use bwfmetaedit to get metadata instead
    ffprobe_tags = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-show_entries",
                "format_tags",
                pm_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    ffprobe_tags = ffprobe_tags["format"]["tags"]
    # core_bwf_command = [args.metaedit_path, '--out-core', pm_file_abspath]
    tech_bwf_command = [args.metaedit_path, "--out-tech", pm_file_abspath]
    # TODO fix - splitlines returns different results here depending on OS
    tech_bwf_csv = (
        subprocess.check_output(tech_bwf_command)
        .decode("ascii")
        .rstrip()
        .splitlines()[-1]
    )
    embedded_md5 = {"MD5Stored": tech_bwf_csv.split(",")[16]}
    ffprobe_tags.update(embedded_md5)
    # core_bwf_csv = subprocess.check_output(core_bwf_command).decode("ascii").rstrip()
    return ffprobe_tags


def parse_mediaconchResults(mediaconchResults_dict):
    if "FAIL" in mediaconchResults_dict.values():
        mediaconchResults = "FAIL"
        failed_policies = []
        for key in mediaconchResults_dict.keys():
            if "FAIL" in mediaconchResults_dict.get(key):
                failed_policies.append(key)
        mediaconchResults = mediaconchResults + ": " + str(failed_policies).strip("[]")
    else:
        mediaconchResults = "PASS"
    return mediaconchResults


def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime


def write_output_csv(csv_file, csvHeaderList, csvWriteList, qcResults):
    csvOutFileExists = os.path.isfile(csv_file)
    with open(csv_file, "a") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        if not csvOutFileExists:
            writer.writerow(csvHeaderList)
        writer.writerow(csvWriteList)
