#!/usr/bin/env python3

import os
import sys
import subprocess
import csv
import progressbar
import nulrdcscripts.vproc.equipment_dict as equipment_dict
from nulrdcscripts.vproc.params import args
from nulrdcscripts.vproc.assists import guess_date,delete_files



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



def ffv1_checksum(transcode_nameDict):
    pass

def two_pass_h264_encoding(transcode_nameDict, audioStreamCounter):
    with progressbar.ProgressBar(max_value=100) as h264prog:
        
        for t in range(100):
            # get relevant names from nameDict
            inputAbsPath = transcode_nameDict.get("inputAbsPath")
            tempMasterFile = transcode_nameDict.get("tempMasterFile")
            framemd5AbsPath = transcode_nameDict.get("framemd5AbsPath")
            acAbsPath = transcode_nameDict.get("acAbsPath")
            framemd5File = transcode_nameDict.get("framemd5File")
            copyMixCommand = ["-c:a","aac","-b:a","256k"]
            fourto3Mixcommand = ["-filter_complex","[0:a:0][0:a:1]amerge=inputs=2[a]", "-map", "0:v", "-map", "[a]","-map","0:a:2","-map","0:a:3",]
            fourto2Mixcommand = ["-filter-complex","[0:a:0][:0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]","-map","0:v", "-map","[a]", "-map", "[b]",]
            twoto1Mixcommand = ["-filter-complex","[0:a:0][0:a:1]amerge=inputs=2[a]","-map","0:v","-map","[a]",]
            inputvideocommand = ["-y","-i",inputAbsPath,"-c:v","libx264","-preset","medium",'-b:v","8000k',"-pix_fmt","yuv420p"]
            h264prog.update(t)
            # create ffmpeg command
            if os.name == "nt":
                nullOut = "NUL"
            else:
                nullOut="/dev/null"
            pass1 = [args.ffmpeg.path]
            if not args.verbose:
                pass1 += ["-loglevel", "error"]
            pass1 += [inputvideocommand,
                "-pass",
                "1",
            ]
            
            h264prog.update(t)
            if audioStreamCounter > 0:
                if args.mixdown == "copy":
                    pass1 += copyMixCommand
                if args.mixdown == "4to3" and audioStreamCounter == 4:
                    pass1 += fourto3Mixcommand
                if args.mixdown == "4to2" and audioStreamCounter == 4:
                    pass1 += fourto2Mixcommand
                if args.mixdown == "2to1" and audioStreamCounter == 2:
                    pass1 += twoto1Mixcommand
            h264prog.update(t)
            pass1 += ["-f", "mp4", nullOut]
            pass2 = [args.ffmpeg_path]
            if not args.verbose:
                pass2 += ["-loglevel", "error"]
            pass2 += [inputvideocommand,
                "-pass",
                "2",
            ]
            if audioStreamCounter > 0:
                if args.mixdown == "copy":
                    pass2 += copyMixCommand
                if args.mixdown == "4to3" and audioStreamCounter == 4:
                    pass2 += fourto3Mixcommand
                if args.mixdown == "4to2" and audioStreamCounter == 4:
                    pass2 += fourto2Mixcommand
                if args.mixdown == "2to1" and audioStreamCounter == 2:
                    pass2 += twoto1Mixcommand
            pass2 += [acAbsPath]
            h264prog.update(t)
            subprocess.run(pass1)
            h264prog.update(t)
            subprocess.run(pass2)

            # sometimes these files are created I'm not sure why
            current_dir = os.getcwd()
            if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log")):
                os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log"))
            if os.path.isfile(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree")):
                os.remove(os.path.join(current_dir, "ffmpeg2pass-0.log.mbtree"))

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
                    inputAbsPath,
                ]
                if os.path.isfile(tempMasterFile):
                    subprocess.call(add_attachment)
                    filesToDelete = [tempMasterFile, framemd5AbsPath]
                    delete_files(filesToDelete)
                else:
                    print("There was an issue finding the file", tempMasterFile)



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




def qc_results(inventoryCheck, mediaconchResults):
    QC_results = {}
    QC_results["QC"] = {
        "inventory check": inventoryCheck,
        "mediaconch results": mediaconchResults,
    }
    return QC_results




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
                ["inventory_title"],
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
                    title = row[fieldnames["inventory_title"]]
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
                        "inventory_title": title,
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

